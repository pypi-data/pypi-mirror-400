from pydantic import ValidationError

from labels.model.ecosystem_data.java import (
    JavaArchive,
    JavaManifest,
    JavaPomParent,
    JavaPomProject,
    JavaPomProperties,
)
from labels.model.package import Package, PackageType
from labels.model.syft_sbom import SyftArtifact, SyftMetadata
from labels.parsers.builder.utils import get_language, get_locations
from labels.parsers.cataloger.utils import log_malformed_package_warning


def _get_java_manifest(metadata: SyftMetadata) -> JavaManifest | None:
    if not metadata.manifest:  # type: ignore[misc]
        return None

    main: dict[str, str] = {}
    sections: list[dict[str, str]] = []

    if metadata.manifest.get("main", []):  # type: ignore[misc]
        main_list: list[dict[str, str]] = metadata.manifest.get("main", [])  # type: ignore[misc]
        for item in main_list:
            if (key := item.get("key")) and (value := item.get("value")):
                main[key] = value

    if metadata.manifest.get("sections", []):  # type: ignore[misc]
        sections_list: list[list[dict[str, str]]] = metadata.manifest.get("sections", [])  # type: ignore[misc]
        for section in sections_list:
            section_dict: dict[str, str] = {}
            for item in section:
                if (key := item.get("key")) and (value := item.get("value")):
                    section_dict[key] = value
            if section_dict:
                sections.append(section_dict)

    return JavaManifest(
        main=main,
        sections=sections,
    )


def _get_java_pom_properties(metadata: SyftMetadata) -> JavaPomProperties | None:
    if not metadata.pom_properties:
        return None

    return JavaPomProperties(
        name=metadata.pom_properties.get("name"),
        group_id=metadata.pom_properties.get("groupId"),
        artifact_id=metadata.pom_properties.get("artifactId"),
        version=metadata.pom_properties.get("version"),
    )


def _get_java_pom_project(metadata: SyftMetadata) -> JavaPomProject | None:
    if not metadata.pom_project:  # type: ignore[misc]
        return None

    parent: JavaPomParent | None = None

    if metadata.pom_project.get("parent"):  # type: ignore[misc]
        parent_data: dict[str, str] = metadata.pom_project.get("parent", {})  # type: ignore[misc]
        if (
            (group_id := parent_data.get("group_id"))
            and (artifact_id := parent_data.get("artifact_id"))
            and (version := parent_data.get("version"))
        ):
            parent = JavaPomParent(
                group_id=group_id,
                artifact_id=artifact_id,
                version=version,
            )

    return JavaPomProject(
        group_id=metadata.pom_project.get("group_id"),  # type: ignore[misc]
        artifact_id=metadata.pom_project.get("artifact_id"),  # type: ignore[misc]
        version=metadata.pom_project.get("version"),  # type: ignore[misc]
        name=metadata.pom_project.get("name"),  # type: ignore[misc]
        parent=parent,
    )


def _get_dpkg_entry(metadata: SyftMetadata) -> JavaArchive | None:
    manifest = _get_java_manifest(metadata)
    pom_properties = _get_java_pom_properties(metadata)
    pom_project = _get_java_pom_project(metadata)

    return JavaArchive(
        manifest=manifest,
        pom_properties=pom_properties,
        pom_project=pom_project,
    )


def _get_pkg_name(artifact_name: str, p_url: str) -> str | None:
    if not artifact_name or not p_url:
        return None

    p_url_splits = p_url.split("/")

    if len(p_url_splits) >= 3:
        group_id = p_url_splits[1]
        return f"{group_id}:{artifact_name}"

    return None


def builder(
    artifact: SyftArtifact,
    package_type: PackageType,
) -> Package | None:
    pkg_language = get_language(artifact.language)
    pkg_locations = get_locations(artifact.locations)

    metadata = artifact.metadata
    pkg_ecosystem_data = _get_dpkg_entry(metadata)

    p_url = artifact.p_url

    pkg_name = _get_pkg_name(artifact.name, p_url) or artifact.name

    try:
        package = Package(
            name=pkg_name,
            version=artifact.version,
            p_url=p_url,
            locations=pkg_locations,
            type=package_type,
            ecosystem_data=pkg_ecosystem_data,
            found_by=artifact.found_by,
            language=pkg_language,
            syft_id=artifact.id_,
        )
    except ValidationError as ex:
        log_malformed_package_warning(pkg_locations[0], ex)
        return None

    return package
