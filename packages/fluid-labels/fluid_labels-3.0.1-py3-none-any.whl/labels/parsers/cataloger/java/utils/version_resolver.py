import re
from typing import NamedTuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from labels.config.cache import dual_cache
from labels.model.ecosystem_data.java import JavaPomParent, JavaPomProperties
from labels.parsers.cataloger.java.utils.model import PomContext
from labels.parsers.cataloger.java.utils.parsing_utils import get_next_text


class ParsedPomResult(NamedTuple):
    version: str | None
    parent_info: JavaPomParent | None


def resolve_version(
    pom_context: PomContext, pom_properties: JavaPomProperties, full_name: str
) -> str | None:
    version = pom_properties.version

    if version and version.startswith("${"):
        version = _resolve_property_version(
            version, pom_context.project, pom_context.parent_version_properties
        )

    if not version and pom_context.parent_info:
        version = _resolve_version_from_parent_pom_chain(
            pom_properties=pom_properties, parent_info=pom_context.parent_info
        )

    if not version and pom_context.manage_deps and pom_context.parent_version_properties:
        version = _resolve_managed_version(
            pom_context.manage_deps,
            pom_context.parent_version_properties,
            full_name,
        )

    return version


def _extract_bracketed_text(item: str) -> str:
    match = re.search(r"\$\{([^}]+)\}", item)
    if match:
        return match.group(1)

    return ""


def _resolve_property_version(
    version: str,
    project: Tag,
    parent_version_properties: dict[str, str] | None,
) -> str | None:
    property_name = _extract_bracketed_text(version)

    property_node = project.find_next(property_name)
    if property_node:
        version_text = property_node.get_text()
        if version_text and not version_text.startswith("${"):
            return version_text

    if parent_version_properties:
        return parent_version_properties.get(property_name)

    return None


def _resolve_managed_version(
    manage_deps: dict[str, str], parent_version_properties: dict[str, str], full_name: str
) -> str | None:
    managed_version = manage_deps.get(full_name)
    if managed_version:
        if not managed_version.startswith("${"):
            return managed_version

        return parent_version_properties.get(_extract_bracketed_text(managed_version))

    return None


def _resolve_version_from_parent_pom_chain(
    pom_properties: JavaPomProperties,
    parent_info: dict[str, str],
) -> str | None:
    group_id = pom_properties.group_id
    artifact_id = pom_properties.artifact_id

    if not group_id or not artifact_id:
        return None

    parent_group_id = parent_info["group"]
    parent_artifact_id = parent_info["artifact"]
    parent_version = parent_info["version"]

    for _ in range(3):
        parent_pom = _get_pom_from_maven_repo(
            group_id=parent_group_id,
            artifact_id=parent_artifact_id,
            version=parent_version,
        )
        if not parent_pom:
            break

        parsed_pom_result = _process_pom(parent_pom, group_id, artifact_id)
        if not parsed_pom_result:
            break

        version = parsed_pom_result.version
        if version:
            return version

        parsed_parent_info = parsed_pom_result.parent_info
        if not parsed_parent_info:  # pragma: no cover
            break

        parent_group_id = parsed_parent_info.group_id
        parent_artifact_id = parsed_parent_info.artifact_id
        parent_version = parsed_parent_info.version

    return None


def _process_pom(parent_pom: Tag, group_id: str, artifact_id: str) -> ParsedPomResult | None:
    project = parent_pom.project
    if not project:
        return None

    dependency_management = project.find_next("dependencymanagement")
    if dependency_management and isinstance(dependency_management, Tag):
        version = _get_dependency_version(dependency_management, group_id, artifact_id)
        if version:
            return ParsedPomResult(version=version, parent_info=None)

    parent = project.find_next("parent")
    if parent:
        parent_info = _get_parent_information(parent)
        if parent_info:
            return ParsedPomResult(version=None, parent_info=parent_info)

    return None


def _get_parent_information(
    parent: Tag | NavigableString,
) -> JavaPomParent | None:
    parent_group_id = get_next_text(parent, "groupid")
    parent_artifact_id = get_next_text(parent, "artifactid")
    parent_version = get_next_text(parent, "version")

    if not parent_group_id or not parent_artifact_id or not parent_version:
        return None

    return JavaPomParent(
        group_id=parent_group_id,
        artifact_id=parent_artifact_id,
        version=parent_version,
    )


def _get_dependency_version(
    dependency_management: Tag, group_id: str, artifact_id: str
) -> str | None:
    for dependency in dependency_management.find_all("dependency"):
        if _matches_dependency(dependency, group_id, artifact_id):
            version_node = dependency.find_next("version")
            if version_node:
                return version_node.get_text()

    return None


def _matches_dependency(dependency: Tag, group_id: str, artifact_id: str) -> bool:
    dependency_group_id_node = dependency.find_next("groupid")
    dependency_artifact_id_node = dependency.find_next("artifactid")

    return (
        dependency_group_id_node is not None
        and dependency_artifact_id_node is not None
        and dependency_group_id_node.get_text() == group_id
        and dependency_artifact_id_node.get_text() == artifact_id
    )


def _get_pom_from_maven_repo(
    *, group_id: str, artifact_id: str, version: str
) -> BeautifulSoup | None:
    request_url = _format_maven_pom_ulr(group_id, artifact_id, version)
    request = _cached_request(request_url)
    if request.status_code != 200:
        return None

    pom_text = request.text
    return BeautifulSoup(pom_text, features="html.parser")


def _format_maven_pom_ulr(group_id: str, artifact_id: str, version: str) -> str:
    maven_base_url = "https://repo1.maven.org/maven2"
    artifact_pom = f"{artifact_id}-{version}.pom"
    path_components = [*group_id.split("."), artifact_id, version, artifact_pom]

    url = maven_base_url
    for component in path_components:
        url = urljoin(url + "/", component)

    return url


@dual_cache
def _cached_request(url: str) -> requests.Response:
    return requests.get(url, timeout=30)
