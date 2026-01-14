import re
import unicodedata
from pathlib import Path
from typing import NamedTuple
from zipfile import ZipInfo

from bs4 import BeautifulSoup, Tag

from labels.model.ecosystem_data.java import (
    JavaArchive,
    JavaManifest,
    JavaPomParent,
    JavaPomProject,
    JavaPomProperties,
)
from labels.model.file import Location
from labels.model.package import Package
from labels.parsers.cataloger.java.parse_archive.archive_file_info import ArchiveFileInfo
from labels.parsers.cataloger.java.utils.package_builder import new_java_package_from_maven_data
from labels.parsers.cataloger.java.utils.parsing_utils import get_direct_child_text, safe_get_text
from labels.parsers.cataloger.utils import get_enriched_location
from labels.utils.zip import contents_from_zip, new_zip_glob_match


class JavaPackageIdentity(NamedTuple):
    artifact_id: str | None
    version: str | None
    group_id: str | None


class MavenHandler:
    def __init__(
        self,
        *,
        file_manifest: list[ZipInfo],
        archive_path: str,
        location: Location,
        file_info: ArchiveFileInfo,
    ) -> None:
        self.file_manifest = file_manifest
        self.archive_path = archive_path
        self.location = location
        self.file_info = file_info
        self._properties_cache: dict[str, JavaPomProperties] | None = None
        self._projects_cache: dict[str, JavaPomProject] | None = None

    def discover_auxiliary_packages(self, parent_package: Package) -> list[Package]:
        properties = self._load_properties()
        projects = self._load_projects()

        packages = []
        for parent_path, properties_obj in properties.items():
            pom_project = projects.get(parent_path)

            new_location = get_enriched_location(self.location)

            package = new_java_package_from_maven_data(properties_obj, pom_project, new_location)
            if package and not self._same_as_parent_package(parent_package, package):
                packages.append(package)

        return packages

    def extract_identity(self, manifest: JavaManifest) -> JavaPackageIdentity:
        properties = self._load_properties()
        projects = self._load_projects()
        properties_obj, project_obj = self._find_matching_objects(properties, projects)

        artifact_id = None
        version = None
        group_id = None

        if properties_obj:
            artifact_id = properties_obj.artifact_id
            version = properties_obj.version
            group_id = properties_obj.group_id

        if project_obj and not version:
            version = project_obj.version
        if project_obj and not group_id:
            group_id = project_obj.group_id

        artifact_id = artifact_id or self._select_name_from_manifest_or_file(manifest)
        version = version or self._select_version_from_manifest_or_file(manifest)
        group_id = group_id or self._select_name_from_manifest_or_file(manifest)

        return JavaPackageIdentity(artifact_id=artifact_id, version=version, group_id=group_id)

    def build_ecosystem_data(self, manifest: JavaManifest) -> JavaArchive:
        properties = self._load_properties()
        projects = self._load_projects()
        props_obj, proj_obj = self._find_matching_objects(properties, projects)

        return JavaArchive(
            manifest=manifest,
            pom_properties=props_obj,
            pom_project=proj_obj if proj_obj else None,
        )

    def _same_as_parent_package(self, parent_package: Package, package: Package) -> bool:
        return package.name == parent_package.name and package.version == parent_package.version

    def _find_matching_objects(
        self, properties: dict[str, JavaPomProperties], projects: dict[str, JavaPomProject]
    ) -> tuple[JavaPomProperties | None, JavaPomProject | None]:
        artifacts_map = {props.artifact_id for props in properties.values() if props.artifact_id}

        for parent_path, properties_obj in properties.items():
            if properties_obj.artifact_id:
                artifact_matches_filename = self._artifact_id_matches_filename(
                    properties_obj.artifact_id, self.file_info.name, artifacts_map
                )
                project_object = projects.get(parent_path)
                if artifact_matches_filename and project_object:
                    return properties_obj, project_object

        return None, None

    def _artifact_id_matches_filename(
        self, artifact_id: str, filename: str, artifacts_map: set[str]
    ) -> bool:
        if filename in artifacts_map:
            return artifact_id == filename

        return artifact_id.startswith(filename) or filename.endswith(artifact_id)

    def _select_name_from_manifest_or_file(self, manifest: JavaManifest) -> str:
        name = self._extract_name_from_apache_maven_bundle_plugin(manifest)
        if name:
            return name

        # the filename tends to be the next-best reference for the package name
        name = self._extract_name_from_file_info()
        if name:
            return name

        # remaining fields in the manifest is a bit of a free-for-all depending on
        # the build tooling used and package maintainer preferences
        main_attrs = manifest.main
        field_names = [
            "Name",
            "Bundle-Name",
            "Short-Name",
            "Extension-Name",
            "Implementation-Title",
        ]
        for key in field_names:
            if main_attrs.get(key):
                return main_attrs[key]

        return ""

    def _extract_name_from_apache_maven_bundle_plugin(self, manifest: JavaManifest) -> str:
        created_by = manifest.main.get("Created-By", "")
        if "Apache Maven Bundle Plugin" in created_by:
            symbolic_name = manifest.main.get("Bundle-SymbolicName", "")
            if symbolic_name:
                vendor_id = manifest.main.get("Implementation-Vendor-Id", "")
                if vendor_id and vendor_id == symbolic_name:
                    return ""

                # Assuming symbolicName convention "${groupId}.${artifactId}".
                fields = symbolic_name.split(".")
                # Potential issue with determining the actual artifactId based
                # on BND behavior.
                return fields[-1] if fields else ""

        return ""

    def _extract_name_from_file_info(self) -> str:
        if "." in self.file_info.name:
            # Handle the special case for 'org.eclipse.*' group IDs
            if self.file_info.name.startswith("org.eclipse."):
                return self.file_info.name

            # Split the name on dots and check if it looks like a
            # 'groupId.artifactId'
            fields = self.file_info.name.split(".")
            if all(self._is_valid_java_identifier(f) for f in fields):
                # If all parts are valid Java identifiers, assume the last part
                # is the artifact ID
                return fields[-1]

        return self.file_info.name

    @staticmethod
    def _is_valid_java_identifier(field: str) -> bool:
        if not field:
            return False

        first_char = field[0]
        if first_char.isalpha() or unicodedata.category(first_char) in [
            "Sc",
            "Pc",
        ]:
            # If the first character is valid, check the remaining characters.
            # Note: Python's str.isidentifier() checks if the entire string is a
            # valid identifier.
            return field.isidentifier()

        return False

    def _select_version_from_manifest_or_file(self, manifest: JavaManifest) -> str:
        if version := self.file_info.version:
            return version

        field_names = [
            "Implementation-Version",
            "Specification-Version",
            "Plugin-Version",
            "Bundle-Version",
        ]
        for field in field_names:
            if value := self._field_value_from_manifest(manifest, field):
                return value

        return ""

    def _field_value_from_manifest(self, manifest: JavaManifest, field: str) -> str:
        if (value := manifest.main.get(field, None)) and value:
            return value

        for section in manifest.sections or []:
            if (value := section.get(field, None)) and value:
                return value
        return ""

    def _load_properties(self) -> dict[str, JavaPomProperties]:
        if self._properties_cache is None:
            matches = new_zip_glob_match(
                self.file_manifest, ("*pom.properties",), case_sensitive=False
            )
            self._properties_cache = self._pom_properties_by_parent(self.archive_path, matches)
        return self._properties_cache or {}

    def _pom_properties_by_parent(
        self, archive_path: str, extract_paths: list[str]
    ) -> dict[str, JavaPomProperties]:
        properties_by_parent_path = {}
        contents_of_maven_properties = contents_from_zip(archive_path, *extract_paths)

        for file_path, file_contents in contents_of_maven_properties.items():
            if not file_contents:
                continue

            pom_properties = self._parse_pom_properties(file_contents)

            properties_by_parent_path[str(Path(file_path).parent)] = pom_properties

        return properties_by_parent_path

    def _parse_pom_properties(self, file_content: str) -> JavaPomProperties:
        properties_map = {}

        for raw_line in file_content.splitlines():
            line = raw_line.strip()

            if line == "" or line.lstrip().startswith("#"):
                continue

            idx = next((i for i in range(len(line)) if line[i] in ":="), -1)
            if idx == -1:
                continue

            key = line[:idx].strip()
            value = line[idx + 1 :].strip()
            properties_map[key] = value

        converted_props = {}
        for raw_key, value in properties_map.items():
            key = re.sub(r"(?<!^)(?=[A-Z])", "_", raw_key).lower()
            if key in set(JavaPomProperties.__annotations__.keys()):
                converted_props[key] = value

        return JavaPomProperties(**converted_props)

    def _load_projects(self) -> dict[str, JavaPomProject]:
        if self._projects_cache is None:
            matches = new_zip_glob_match(self.file_manifest, ("*pom.xml",), case_sensitive=False)
            self._projects_cache = self._pom_project_by_parent(self.archive_path, matches)
        return self._projects_cache or {}

    def _pom_project_by_parent(
        self, archive_path: str, extract_paths: list[str]
    ) -> dict[str, JavaPomProject]:
        contents_of_maven_project = contents_from_zip(archive_path, *extract_paths)

        project_by_parent = {}

        for file_path, file_contents in contents_of_maven_project.items():
            pom_project = self._parse_pom_xml_project(file_contents)
            if not pom_project:
                continue

            project_by_parent[str(Path(file_path).parent)] = pom_project

        return project_by_parent

    def _parse_pom_xml_project(self, reader: str) -> JavaPomProject | None:
        project = BeautifulSoup(reader, features="xml").project
        if not project:
            return None

        return self._build_pom_project(project)

    def _build_pom_project(self, project: Tag) -> JavaPomProject:
        artifact_id = safe_get_text(self._find_direct_child(project, "artifactId"))
        name = safe_get_text(self._find_direct_child(project, "name"))

        return JavaPomProject(
            parent=self._build_pom_parent(self._find_direct_child(project, "parent")),
            group_id=safe_get_text(self._find_direct_child(project, "groupId")),
            artifact_id=artifact_id,
            version=safe_get_text(self._find_direct_child(project, "version")),
            name=name,
        )

    def _build_pom_parent(self, parent: Tag | None) -> JavaPomParent | None:
        if not parent:
            return None

        group_id = get_direct_child_text(parent, "groupId")
        artifact_id = get_direct_child_text(parent, "artifactId")
        version = get_direct_child_text(parent, "version")

        if (
            not group_id
            or not artifact_id
            or not version
            or not group_id.strip()
            or not artifact_id.strip()
            or not version.strip()
        ):
            return None

        return JavaPomParent(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
        )

    def _find_direct_child(self, parent: Tag, tag: str) -> Tag | None:
        return next(
            (child for child in parent.find_all(tag, recursive=False) if child.parent == parent),
            None,
        )
