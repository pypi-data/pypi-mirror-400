from typing import NamedTuple

from labels.model.file import DependencyType, Location
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.javascript.common import is_version_compatible
from labels.parsers.cataloger.javascript.package_builder import new_npm_package_from_lock
from labels.parsers.cataloger.utils import get_enriched_location


class PackageV2Info(NamedTuple):
    path: str
    dependencies: dict[str, str]
    dev_dependencies: dict[str, str]
    peer_dependencies: dict[str, str]
    optional_dependencies: dict[str, str]


class _RelationshipContext(NamedTuple):
    package: Package
    package_location: Location
    pkg_info: PackageV2Info
    packages_by_name: dict[str, list[Package]]
    lockfile_path: str
    package_map: dict[tuple[str, int], PackageV2Info]


def parse_package_lock_v2(
    location: Location,
    file_content: IndexedDict[str, ParsedValue],
) -> tuple[list[Package], list[Relationship]]:
    packages_dict = file_content.get("packages")
    if not isinstance(packages_dict, IndexedDict):
        return [], []

    packages = []
    root_package = _create_root_package(location, packages_dict)
    if root_package:
        packages.append(root_package)

    direct_dependencies = _get_direct_dependencies_from_root(packages_dict)
    packages.extend(_collect_packages(location, packages_dict, direct_dependencies))
    package_map_v2 = _build_package_map_v2(packages_dict)
    relationships = _build_relationships_v2(packages, package_map_v2, location.path())

    return packages, relationships


def _collect_packages(
    location: Location,
    packages_dict: IndexedDict[str, ParsedValue],
    direct_dependencies: list[str],
) -> list[Package]:
    packages: list[Package] = []

    for dependency_key, package_value in packages_dict.items():
        if dependency_key == "":
            continue

        if not isinstance(package_value, IndexedDict):
            continue

        name = _get_name(dependency_key, package_value) or _get_name_from_path(dependency_key)

        is_transitive = name not in direct_dependencies
        is_dev = package_value.get("dev") is True
        new_location = get_enriched_location(
            location,
            line=package_value.position.start.line,
            is_dev=is_dev,
            is_transitive=is_transitive,
        )

        package = new_npm_package_from_lock(
            location=new_location, name=name, value=package_value, lockfile_version=2
        )
        if package:
            packages.append(package)

    return packages


def _build_package_map_v2(
    packages_dict: IndexedDict[str, ParsedValue],
) -> dict[tuple[str, int], PackageV2Info]:
    package_map: dict[tuple[str, int], PackageV2Info] = {}

    for package_path, package_value in packages_dict.items():
        if not isinstance(package_value, IndexedDict):
            continue

        name = _get_name(package_path, package_value)
        if not name:
            continue

        dependencies_dict = package_value.get("dependencies")
        dev_dependencies_dict = package_value.get("devDependencies")
        peer_dependencies_dict = package_value.get("peerDependencies")
        optional_dependencies_dict = package_value.get("optionalDependencies")

        if isinstance(dependencies_dict, IndexedDict):
            dependencies = {k: str(v) for k, v in dependencies_dict.data.items()}
        else:
            dependencies = {}

        if isinstance(dev_dependencies_dict, IndexedDict):
            dev_dependencies = {k: str(v) for k, v in dev_dependencies_dict.data.items()}
        else:
            dev_dependencies = {}

        if isinstance(peer_dependencies_dict, IndexedDict):
            peer_dependencies = {k: str(v) for k, v in peer_dependencies_dict.data.items()}
        else:
            peer_dependencies = {}

        if isinstance(optional_dependencies_dict, IndexedDict):
            optional_dependencies = {k: str(v) for k, v in optional_dependencies_dict.data.items()}
        else:
            optional_dependencies = {}

        line = package_value.position.start.line
        package_map[(name, line)] = PackageV2Info(
            path=package_path,
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            peer_dependencies=peer_dependencies,
            optional_dependencies=optional_dependencies,
        )
    return package_map


def _create_root_package(
    location: Location,
    packages_dict: IndexedDict[str, ParsedValue],
) -> Package | None:
    root_entry = packages_dict.get("")
    if not isinstance(root_entry, IndexedDict):
        return None

    root_name = root_entry.get("name")
    if not isinstance(root_name, str):
        return None

    root_location = get_enriched_location(
        base=location,
        line=root_entry.position.start.line,
        is_transitive=False,
        is_dev=False,
    )
    update_root: dict[str, DependencyType] = {"dependency_type": DependencyType.ROOT}
    root_location = root_location.model_copy(deep=True, update=update_root)
    return new_npm_package_from_lock(
        location=root_location,
        name=root_name,
        value=root_entry,
        lockfile_version=2,
    )


def _get_direct_dependencies_from_root(
    packages_dict: IndexedDict[str, ParsedValue],
) -> list[str]:
    root_entry = packages_dict.get("")
    if not isinstance(root_entry, IndexedDict):
        return []

    result: list[str] = []

    deps_candidate = root_entry.get("dependencies")
    if isinstance(deps_candidate, IndexedDict):
        result.extend(deps_candidate.keys())

    dev_deps_candidate = root_entry.get("devDependencies")
    if isinstance(dev_deps_candidate, IndexedDict):
        result.extend(dev_deps_candidate.keys())

    return result


def _get_name(dependency_key: str, package_value: IndexedDict[str, ParsedValue]) -> str:
    name = dependency_key
    if not name:
        if "name" not in package_value:
            return _get_name_from_path(dependency_key)
        name = str(package_value["name"])

    # Handle alias name
    if "name" in package_value and package_value["name"] != dependency_key:
        name = str(package_value["name"])

    return _get_name_from_path(name)


def _get_name_from_path(name: str) -> str:
    return name.split("node_modules/")[-1]


def _resolve_npm_location_v2(
    parent_path: str,
    dependency_name: str,
    dep_locations: list[Location],
    package_map: dict[tuple[str, int], PackageV2Info],
    alias_name: str | None = None,
) -> list[Location]:
    if len(dep_locations) == 0:
        return []

    candidate_paths: list[str] = []

    def _append_candidate_paths_for(name: str) -> None:
        candidate_paths.append(f"{parent_path}/node_modules/{name}")

        parts = parent_path.split("/node_modules/")
        for i in range(len(parts) - 1, 0, -1):
            ancestor_path = "/node_modules/".join(parts[:i])
            candidate_paths.append(f"{ancestor_path}/node_modules/{name}")

        candidate_paths.append(f"node_modules/{name}")

    _append_candidate_paths_for(dependency_name)
    if alias_name and alias_name != dependency_name:
        _append_candidate_paths_for(alias_name)

    for candidate_path in candidate_paths:
        for dep_location in dep_locations:
            line = dep_location.coordinates.line if dep_location.coordinates else None
            if line is None:
                continue

            pkg_info = package_map.get((dependency_name, line))
            if pkg_info and pkg_info.path == candidate_path:
                return [dep_location]

    return []


def _process_dependencies_for_relationships(
    dependencies_dict: dict[str, str],
    context: _RelationshipContext,
    relationships: list[Relationship],
) -> None:
    for original_dep_name, raw_required_version in dependencies_dict.items():
        real_name, normalized_required_version = _parse_alias_requirement(raw_required_version)
        lookup_name = real_name or original_dep_name

        for dep_pkg in context.packages_by_name.get(lookup_name, []):
            if not is_version_compatible(dep_pkg.version, normalized_required_version):
                continue
            all_locs = [loc for loc in dep_pkg.locations if loc.path() == context.lockfile_path]
            dep_locations = _resolve_npm_location_v2(
                context.pkg_info.path,
                lookup_name,
                all_locs,
                context.package_map,
                original_dep_name if real_name else None,
            )
            for dep_location in dep_locations:
                from_id = f"{dep_pkg.id_}@{dep_location.location_id()}"
                to_id = f"{context.package.id_}@{context.package_location.location_id()}"
                relationships.append(
                    Relationship(
                        from_=from_id,
                        to_=to_id,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    )
                )


def _build_relationships_v2(
    packages: list[Package],
    package_map: dict[tuple[str, int], PackageV2Info],
    lockfile_path: str,
) -> list[Relationship]:
    relationships: list[Relationship] = []

    packages_by_name: dict[str, list[Package]] = {}
    for pkg in packages:
        if any((loc.path() == lockfile_path) for loc in pkg.locations):
            packages_by_name.setdefault(pkg.name, []).append(pkg)

    for package in packages:
        for package_location in [loc for loc in package.locations if loc.path() == lockfile_path]:
            line = package_location.coordinates.line if package_location.coordinates else None
            if line is None:
                continue

            pkg_info = package_map.get((package.name, line))
            if not pkg_info:
                continue

            context = _RelationshipContext(
                package=package,
                package_location=package_location,
                pkg_info=pkg_info,
                packages_by_name=packages_by_name,
                lockfile_path=lockfile_path,
                package_map=package_map,
            )

            for dependencies_dict in [
                pkg_info.dependencies,
                pkg_info.dev_dependencies,
                pkg_info.peer_dependencies,
                pkg_info.optional_dependencies,
            ]:
                _process_dependencies_for_relationships(
                    dependencies_dict,
                    context,
                    relationships,
                )

    return relationships


def _parse_alias_requirement(required_version: str) -> tuple[str | None, str]:
    """Normalize npm alias requirements.

    For entries like "npm:strip-ansi@^6.0.1" return ("strip-ansi", "^6.0.1").
    For non-alias requirements, return (None, required_version).
    """
    version_str = required_version.strip()
    prefix = "npm:"
    if not version_str.startswith(prefix):
        return None, version_str

    tail = version_str[len(prefix) :]
    if "@" in tail:
        real_name, parsed_version = tail.split("@", 1)
        return real_name, parsed_version.strip()
    return tail, "*"
