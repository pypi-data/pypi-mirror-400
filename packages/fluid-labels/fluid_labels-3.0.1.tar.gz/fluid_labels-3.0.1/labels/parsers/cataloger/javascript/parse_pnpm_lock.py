import re
from typing import NamedTuple

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.common import (
    DependencyMap,
    add_dependency_to_root_relationship,
    build_relationships,
    create_root_package_from_package_json,
    find_root_location,
    get_direct_dependencies_from_package_json,
    group_packages_by_name,
)
from labels.parsers.cataloger.javascript.package_builder import new_simple_npm_package
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter

VERSION_PATTERN = re.compile(r"(\d+\.\d+\.\d+(-[0-9A-Za-z\.]+)?)")


class PnpmPackageCreationDetails(NamedTuple):
    package_key: str
    package_spec: IndexedDict[str, ParsedValue]
    packages_object: IndexedDict[str, ParsedValue]
    direct_dependencies: set[str]
    base_location: Location


class PnpmPackageInfo(NamedTuple):
    name: str
    key: str
    is_dev: bool
    dependencies: set[str]


def parse_pnpm_lock(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = reader.read_closer.read()
    file_content = parse_yaml_with_tree_sitter(content)
    if not isinstance(file_content, IndexedDict):
        return [], []

    direct_dependencies = get_direct_dependencies_from_package_json(reader.location)
    root_package = create_root_package_from_package_json(reader.location)

    packages = _collect_packages(reader, file_content, direct_dependencies)

    if root_package:
        packages.append(root_package)

    dependency_map = _build_dependency_map_pnpm(file_content)
    key_map = _build_key_map_pnpm(file_content)

    relationships = build_relationships(packages, dependency_map, reader.location, key_map)

    if root_package:
        root_relationships = _create_root_relationships(
            root_package, packages, direct_dependencies, reader.location
        )
        relationships.extend(root_relationships)

    return packages, relationships


def _create_root_relationships(
    root_package: Package,
    packages: list[Package],
    direct_dependencies: set[str],
    location: Location,
) -> list[Relationship]:
    """Create relationships from direct dependencies to root package."""
    relationships: list[Relationship] = []

    if not (location.coordinates and location.coordinates.real_path):
        return relationships

    lockfile_path = location.coordinates.real_path
    root_location = find_root_location(root_package, lockfile_path)

    if not root_location:
        return relationships

    packages_by_name = group_packages_by_name(packages, root_package.id_)

    for dep_name in direct_dependencies:
        for dep_pkg in packages_by_name.get(dep_name, []):
            add_dependency_to_root_relationship(
                dep_pkg, root_package, root_location, lockfile_path, relationships
            )

    return relationships


def _collect_packages(
    reader: LocationReadCloser,
    file_content: IndexedDict[str, ParsedValue],
    direct_dependencies: set[str],
) -> list[Package]:
    packages: list[Package] = []

    packages_object = file_content.get("packages")
    if not isinstance(packages_object, IndexedDict):
        return packages

    for package_key, pkg_spec in packages_object.items():
        if not isinstance(pkg_spec, IndexedDict):
            continue

        package_creation_details = PnpmPackageCreationDetails(
            package_key=package_key,
            package_spec=pkg_spec,
            packages_object=packages_object,
            direct_dependencies=direct_dependencies,
            base_location=reader.location,
        )

        package = _process_package(package_creation_details)
        if package:
            packages.append(package)

    return packages


def _process_package(creation_details: PnpmPackageCreationDetails) -> Package | None:
    name_and_version = _parse_package_key(
        creation_details.package_key, creation_details.package_spec
    )
    if name_and_version is None:
        return None

    package_name, package_version = name_and_version

    is_dev = creation_details.package_spec.get("dev") is True

    package_info = PnpmPackageInfo(
        name=package_name,
        key=creation_details.package_key,
        dependencies=creation_details.direct_dependencies,
        is_dev=is_dev,
    )

    position = creation_details.packages_object.get_key_position(package_info.key)
    is_transitive = package_info.name not in package_info.dependencies

    new_location = get_enriched_location(
        creation_details.base_location,
        line=position.start.line,
        is_transitive=is_transitive,
        is_dev=package_info.is_dev,
    )

    return new_simple_npm_package(new_location, package_name, package_version)


def _parse_package_key(package: str, spec: IndexedDict[str, ParsedValue]) -> tuple[str, str] | None:
    if package.startswith("github"):
        package_name = spec.get("name")
        package_version = spec.get("version")
    else:
        package_info: list[str] = VERSION_PATTERN.split(package.strip("\"'"))
        if len(package_info) < 2:
            return None
        package_name = package_info[0].lstrip("/")[0:-1]
        package_version = package_info[1]

    if not isinstance(package_name, str) or not isinstance(package_version, str):
        return None

    return package_name, package_version


def _process_package_for_dependency_map(
    package_key: str,
    package_value: IndexedDict[str, ParsedValue],
    package_name_regex: re.Pattern[str],
    dependency_map: DependencyMap,
) -> None:
    cleaned_key = package_name_regex.sub(r"\1", package_key)
    name_and_version = _parse_package_key(cleaned_key, package_value)
    if not name_and_version:
        return

    package_name, package_version = name_and_version
    map_key = f"{package_name}@{package_version}"

    if map_key in dependency_map:
        return

    deps = package_value.get("dependencies")
    peer_deps = package_value.get("peerDependencies")
    opt_deps = package_value.get("optionalDependencies")

    dependencies_dict: dict[str, ParsedValue] = {}
    if isinstance(deps, IndexedDict):
        dependencies_dict.update(deps)
    if isinstance(peer_deps, IndexedDict):
        dependencies_dict.update(peer_deps)
    if isinstance(opt_deps, IndexedDict):
        dependencies_dict.update(opt_deps)

    if not dependencies_dict:
        return

    deps_dict = _extract_dependency_requirements(dependencies_dict)
    if deps_dict:
        dependency_map[map_key] = deps_dict


def _build_key_map_pnpm(
    package_yaml: IndexedDict[str, ParsedValue],
) -> dict[tuple[str, int], str]:
    """Build a map from (package_name, line) to package_key (name@version)."""
    key_map: dict[tuple[str, int], str] = {}

    snapshots = package_yaml.get("snapshots")
    packages_items = package_yaml.get("packages")

    sources_to_check = []
    if isinstance(snapshots, IndexedDict):
        sources_to_check.append(snapshots)
    if isinstance(packages_items, IndexedDict):
        sources_to_check.append(packages_items)

    package_name_regex = re.compile(r"^/?([^(]*)(?:\(.*\))*$")

    for source_items in sources_to_check:
        for package_key, package_value in source_items.items():
            if not isinstance(package_value, IndexedDict):
                continue

            cleaned_key = package_name_regex.sub(r"\1", package_key)
            name_and_version = _parse_package_key(cleaned_key, package_value)
            if not name_and_version:
                continue

            package_name, package_version = name_and_version
            map_key = f"{package_name}@{package_version}"

            position = source_items.get_key_position(package_key)
            key_map[(package_name, position.start.line)] = map_key

    return key_map


def _build_dependency_map_pnpm(
    package_yaml: IndexedDict[str, ParsedValue],
) -> DependencyMap:
    dependency_map: DependencyMap = {}

    snapshots = package_yaml.get("snapshots")
    packages_items = package_yaml.get("packages")

    sources_to_check = []
    if isinstance(snapshots, IndexedDict):
        sources_to_check.append(snapshots)
    if isinstance(packages_items, IndexedDict):
        sources_to_check.append(packages_items)

    package_name_regex = re.compile(r"^/?([^(]*)(?:\(.*\))*$")

    for source_items in sources_to_check:
        for package_key, package_value in source_items.items():
            if isinstance(package_value, IndexedDict):
                _process_package_for_dependency_map(
                    package_key, package_value, package_name_regex, dependency_map
                )

    return dependency_map


def _extract_dependency_requirements(
    dependencies: dict[str, ParsedValue],
) -> dict[str, str]:
    deps_dict: dict[str, str] = {}

    for raw_dep_name, raw_dep_version in dependencies.items():
        if not isinstance(raw_dep_version, str):
            continue

        # Extract package name (handles scoped packages like @babel/core)
        dep_name = _extract_package_name_from_key_dependency(raw_dep_name)
        if not dep_name:
            # If extraction fails, use the raw name (for simple packages)
            dep_name = raw_dep_name
        dep_version = _extract_version_from_value_dependency(raw_dep_version)

        # Store the version requirement
        deps_dict[dep_name] = dep_version

    return deps_dict


def _extract_package_name_from_key_dependency(item: str) -> str | None:
    # Regex pattern to extract the package name
    pattern = r"^@?[\w-]+/[\w-]+$"
    match = re.match(pattern, item)
    if match:
        return match.group(0)
    return None


def _extract_version_from_value_dependency(item: str) -> str:
    # Regex pattern to extract the version number before any parentheses
    # Includes pre-release identifiers like -beta.2, -alpha.1, -rc.3, etc.
    pattern = r"^(\d+\.\d+\.\d+(?:-[\w.]+)?)"
    match = re.match(pattern, item)
    if match:
        return match.group(1)
    return item
