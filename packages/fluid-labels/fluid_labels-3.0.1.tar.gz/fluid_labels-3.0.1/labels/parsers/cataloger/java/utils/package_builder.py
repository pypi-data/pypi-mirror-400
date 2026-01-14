import logging
from typing import NamedTuple

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.ecosystem_data.java import JavaArchive, JavaPomProject, JavaPomProperties
from labels.model.file import Location
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.java.utils.group_id_resolver import group_id_from_java_metadata
from labels.parsers.cataloger.utils import log_malformed_package_warning

LOGGER = logging.getLogger(__name__)

JENKINS_PLUGIN_POM_PROPERTIES_GROUP_IDS = [
    "io.jenkins.plugins",
    "org.jenkins.plugins",
    "org.jenkins-ci.plugins",
    "io.jenkins-ci.plugins",
    "com.cloudbees.jenkins.plugins",
]


class JavaPackageSpec(NamedTuple):
    simple_name: str | None
    version: str | None
    location: Location
    composed_name: str | None = None
    ecosystem_data: JavaArchive | None = None


def new_java_package(package_spec: JavaPackageSpec) -> Package | None:
    simple_name = package_spec.simple_name
    version = package_spec.version

    if not simple_name or not version:
        return None

    p_url = _get_package_url_for_java(simple_name, version, package_spec.ecosystem_data)

    name = package_spec.composed_name or simple_name

    try:
        return Package(
            name=name,
            version=version,
            locations=[package_spec.location],
            language=Language.JAVA,
            type=PackageType.JavaPkg,
            p_url=p_url,
            ecosystem_data=package_spec.ecosystem_data,
        )
    except ValidationError as ex:
        log_malformed_package_warning(package_spec.location, ex)
        return None


def new_java_package_from_maven_data(
    pom_properties: JavaPomProperties,
    parsed_pom_project: JavaPomProject | None,
    location: Location,
) -> Package | None:
    artifact_id = pom_properties.artifact_id
    version = pom_properties.version

    if not artifact_id or not version:
        return None

    ecosystem_data = JavaArchive(
        pom_properties=pom_properties,
        pom_project=parsed_pom_project if parsed_pom_project else None,
    )

    authoritative_group_id = (
        group_id_from_java_metadata(artifact_id, ecosystem_data) or pom_properties.group_id
    )

    if not authoritative_group_id:
        LOGGER.warning("No authoritative group ID found for %s in %s", artifact_id, location)
        return None

    package_type = _get_java_package_type_from_group_id(pom_properties.group_id)
    p_url = _get_package_url_for_java(artifact_id, version, ecosystem_data)

    try:
        return Package(
            name=f"{authoritative_group_id}:{artifact_id}",
            version=version,
            locations=[location],
            type=package_type,
            language=Language.JAVA,
            ecosystem_data=ecosystem_data,
            p_url=p_url,
        )
    except ValidationError as ex:
        log_malformed_package_warning(location, ex)
        return None


def _get_package_url_for_java(
    name: str, version: str, ecosystem_data: JavaArchive | None = None
) -> str:
    group_id = name

    group_id_from_metadata = group_id_from_java_metadata(name, ecosystem_data)
    if group_id_from_metadata:
        group_id = group_id_from_metadata

    return PackageURL(type="maven", namespace=group_id, name=name, version=version).to_string()


def _get_java_package_type_from_group_id(group_id: str | None) -> PackageType:
    if any(
        group_id and group_id.startswith(prefix)
        for prefix in JENKINS_PLUGIN_POM_PROPERTIES_GROUP_IDS
    ) or (group_id and ".jenkins.plugin" in group_id):
        return PackageType.JenkinsPluginPkg
    return PackageType.JavaPkg
