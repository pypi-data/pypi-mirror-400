from typing import NamedTuple

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.swift.package_builder import new_cocoa_pods_package
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter


class PodInfo(NamedTuple):
    name: str
    version: str
    dependencies: list[str]
    is_transitive: bool
    line: int


def parse_podfile_lock(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    file_content = _safe_parse_podfile(reader.read_closer.read())
    if not isinstance(file_content, IndexedDict):
        return [], []

    pods_info = _parse_pods_info(file_content)
    if not pods_info:
        return [], []

    packages = _collect_packages(pods_info, reader.location)
    relationships = _generate_relations(pods_info, packages)

    return packages, relationships


def _safe_parse_podfile(content: str) -> ParsedValue | None:
    try:
        parsed_podfile = parse_yaml_with_tree_sitter(content)
    except ValueError:
        return None

    return parsed_podfile


def _parse_pods_info(file_content: IndexedDict[str, ParsedValue]) -> list[PodInfo]:
    pods_info: list[PodInfo] = []

    direct_dependencies = file_content.get("DEPENDENCIES")
    pods = file_content.get("PODS")
    if not isinstance(direct_dependencies, IndexedList) or not isinstance(pods, IndexedList):
        return pods_info

    for index, pod in enumerate(pods):
        pod_name, pod_version = _extract_pod_info(pod)
        pod_dependencies = _extract_pod_dependencies(pod)
        is_transitive = pod_name not in direct_dependencies
        line = pods.get_position(index).start.line

        pods_info.append(
            PodInfo(
                name=pod_name,
                version=pod_version,
                dependencies=pod_dependencies,
                is_transitive=is_transitive,
                line=line,
            )
        )

    return pods_info


def _collect_packages(pods_info: list[PodInfo], location: Location) -> list[Package]:
    packages: list[Package] = []

    for pod_info in pods_info:
        new_location = get_enriched_location(
            location, is_transitive=pod_info.is_transitive, line=pod_info.line
        )

        package = new_cocoa_pods_package(
            name=pod_info.name, version=pod_info.version, location=new_location
        )
        if package:
            packages.append(package)

    return packages


def _generate_relations(pods_info: list[PodInfo], packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []

    packages_by_name = {package.name: package for package in packages}

    for pod_info in pods_info:
        package = packages_by_name.get(pod_info.name)
        if not package:
            continue

        relationships.extend(
            Relationship(
                from_=package_dependency.id_,
                to_=package.id_,
                type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
            )
            for dependency in pod_info.dependencies
            if (package_dependency := packages_by_name.get(dependency))
        )

    return relationships


def _extract_pod_info(pod: ParsedValue) -> tuple[str, str]:
    if isinstance(pod, str | IndexedDict):
        pod_blob = pod if isinstance(pod, str) else next(iter(pod))
        pod_name = pod_blob.split(" ")[0]
        pod_version = pod_blob.split(" ")[1].strip("()")
        return pod_name, pod_version
    return "", ""


def _extract_pod_dependencies(pod: ParsedValue) -> list[str]:
    dependencies = []
    if isinstance(pod, IndexedDict):
        for value in pod.values():
            if isinstance(value, IndexedList):
                for dep in value:
                    if isinstance(dep, str):
                        dep_name = dep.split(" ")[0]
                        dependencies.append(dep_name)
    return dependencies
