import re
from typing import NamedTuple, NotRequired, TypedDict

from labels.model.file import Location, LocationReadCloser
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
    get_dev_dependencies_from_package_json,
    get_direct_dependencies_from_package_json,
    group_packages_by_name,
)
from labels.parsers.cataloger.javascript.package_builder import new_simple_npm_package
from labels.parsers.cataloger.utils import get_enriched_location


class YarnPackage(TypedDict):
    line: int
    version: str
    raw_key: NotRequired[str]  # Original key from yarn.lock header
    checksum: NotRequired[str]
    dependencies: NotRequired[list[tuple[str, str]]]
    integrity: NotRequired[str]
    resolution: NotRequired[str]
    resolved: NotRequired[str]


class PackageKey(NamedTuple):
    name: str
    version: str


class ParserState(NamedTuple):
    parsed_yarn_lock: dict[PackageKey, YarnPackage]
    current_package: str | None = None
    current_package_line: int | None = None
    current_package_version: str | None = None
    current_indentation: int | None = None
    current_key: str | None = None
    package_key: PackageKey | None = None
    current_raw_key: str | None = None  # Raw key from header line


def parse_yarn_lock(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    yarn_lock_content = reader.read_closer.read()
    parsed_yarn_lock = _parse_yarn_file(yarn_lock_content)

    resolution_map = _build_resolution_map_from_parsed(parsed_yarn_lock)

    root_package = create_root_package_from_package_json(reader.location)
    has_package_json = root_package is not None

    direct_dependencies = get_direct_dependencies_from_package_json(reader.location)
    dev_dependencies = get_dev_dependencies_from_package_json(reader.location)

    packages = _extract_packages(
        parsed_yarn_lock,
        reader.location,
        direct_dependencies,
        dev_dependencies,
        has_package_json=has_package_json,
    )

    if root_package:
        packages.append(root_package)

    dependency_map = _build_dependency_map_yarn(parsed_yarn_lock, resolution_map)
    key_map = _build_key_map_yarn(parsed_yarn_lock)
    relationships = build_relationships(packages, dependency_map, reader.location, key_map)

    if root_package:
        root_relationships = _create_root_relationships(
            root_package, packages, direct_dependencies, reader.location
        )
        relationships.extend(root_relationships)

    return packages, relationships


def _parse_yarn_file(yarn_lock_content: str) -> dict[PackageKey, YarnPackage]:
    yarn_lock_lines = yarn_lock_content.strip().split("\n")
    initial_state = ParserState(parsed_yarn_lock={})

    final_state = _process_lines(yarn_lock_lines, initial_state)
    return final_state.parsed_yarn_lock


def _process_lines(lines: list[str], state: ParserState) -> ParserState:
    for index, line in enumerate(lines, 1):
        state = _process_line(line, index, state)
    return state


def _process_line(line: str, index: int, state: ParserState) -> ParserState:
    if not line:
        return state._replace(current_indentation=None)

    if line.startswith("#"):
        return state

    if not line.startswith(" "):
        return _handle_package_header(line, index, state)

    return _process_indented_line(line, state)


def _process_indented_line(line: str, state: ParserState) -> ParserState:
    if state.current_package and state.current_package_line and line.strip().startswith("version"):
        return _handle_version_line(line, state)

    if _is_start_of_list_line(state, line):
        return _handle_list_start(line, state)

    if _is_list_item_line(state, line):
        return _handle_list_item(line, state)

    if state.package_key:
        return _handle_property(line, state)

    return state


def _handle_package_header(line: str, index: int, state: ParserState) -> ParserState:
    current_package, current_package_line = _parse_current_package(line, index)
    raw_key = line.strip().rstrip(":").strip('"')
    return state._replace(
        current_package=current_package,
        current_package_line=current_package_line,
        current_package_version=None,
        package_key=None,
        current_raw_key=raw_key,
    )


def _handle_version_line(line: str, state: ParserState) -> ParserState:
    if not state.current_package or not state.current_package_line:  # pragma: no cover
        return state

    _, raw_version = _resolve_pair(line)
    version = raw_version.strip('"')
    package_key = PackageKey(name=state.current_package, version=version)

    new_package: YarnPackage = {
        "line": state.current_package_line,
        "version": version,
    }
    if state.current_raw_key:
        new_package["raw_key"] = state.current_raw_key

    new_parsed_lock = {**state.parsed_yarn_lock, package_key: new_package}

    return state._replace(
        parsed_yarn_lock=new_parsed_lock,
        current_package_version=version,
        package_key=package_key,
    )


def _handle_list_start(line: str, state: ParserState) -> ParserState:
    if not state.package_key:  # pragma: no cover
        return state

    indentation = _count_indentation(line)
    key = line.strip().split(":")[0]

    if key not in ("dependencies", "optionalDependencies"):
        return state._replace(current_indentation=None, current_key=None)

    existing_deps = state.parsed_yarn_lock[state.package_key].get("dependencies", [])

    updated_package: YarnPackage = {
        **state.parsed_yarn_lock[state.package_key],
        "dependencies": existing_deps if key == "optionalDependencies" else [],
    }
    new_parsed_lock = {**state.parsed_yarn_lock, state.package_key: updated_package}

    return state._replace(
        parsed_yarn_lock=new_parsed_lock,
        current_indentation=indentation,
        current_key=key,
    )


def _handle_list_item(line: str, state: ParserState) -> ParserState:
    if not state.package_key:  # pragma: no cover
        return state

    current_deps = state.parsed_yarn_lock[state.package_key].get("dependencies", [])
    new_dep = _resolve_pair(line)
    new_deps = [*current_deps, new_dep]

    updated_package: YarnPackage = {
        **state.parsed_yarn_lock[state.package_key],
        "dependencies": new_deps,
    }
    new_parsed_lock = {**state.parsed_yarn_lock, state.package_key: updated_package}

    return state._replace(parsed_yarn_lock=new_parsed_lock)


def _handle_property(line: str, state: ParserState) -> ParserState:
    if not state.package_key:  # pragma: no cover
        return state

    key, value = _resolve_pair(line)
    if key not in ("checksum", "integrity", "resolution", "resolved"):
        return state._replace(current_indentation=None)

    existing_package = state.parsed_yarn_lock[state.package_key]
    updated_package: YarnPackage = {**existing_package, key: value.strip('"')}  # type: ignore[misc]
    new_parsed_lock = {**state.parsed_yarn_lock, state.package_key: updated_package}

    return state._replace(parsed_yarn_lock=new_parsed_lock, current_indentation=None)


def _create_root_relationships(
    root_package: Package,
    packages: list[Package],
    direct_dependencies: set[str],
    location: Location,
) -> list[Relationship]:
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


def _extract_packages(
    parsed_yarn_lock: dict[PackageKey, YarnPackage],
    location: Location,
    direct_dependencies: set[str],
    dev_dependencies: set[str],
    *,
    has_package_json: bool,
) -> list[Package]:
    packages = []

    for pkg_info, item in parsed_yarn_lock.items():
        name = _get_name(pkg_info, item)
        version = item.get("version")

        if has_package_json:
            is_direct = name in direct_dependencies
            is_transitive: bool | None = not is_direct

            if is_direct:
                is_dev: bool | None = name in dev_dependencies
            else:
                is_dev = None
        else:
            is_transitive = None
            is_dev = None

        new_location = get_enriched_location(
            location,
            line=item["line"],
            is_transitive=is_transitive,
            is_dev=is_dev,
        )

        package = new_simple_npm_package(new_location, name, version)
        if package:
            packages.append(package)

    return packages


def _extract_patch_entry(entry: str) -> tuple[str, str] | None:
    if match := re.search(r"@patch:(.+?)@npm%3A([^#]+)", entry):
        pkg_name = match.group(1)
        version_range_encoded = match.group(2)
        return pkg_name, f"npm:{version_range_encoded}"
    return None


def _extract_npm_entry(entry: str) -> tuple[str, str] | None:
    parts = entry.split("@npm:")
    if len(parts) >= 2:
        return parts[0], f"npm:{parts[-1]}"
    return None


def _extract_scoped_entry(entry: str) -> tuple[str, str] | None:
    last_at = entry.rfind("@")
    pkg_name = entry[:last_at]
    version_range = entry[last_at + 1 :].rstrip(":")
    return pkg_name, version_range


def _extract_simple_entry(entry: str) -> tuple[str, str] | None:
    parts = entry.split("@", 1)
    if len(parts) == 2:
        return parts[0], parts[1].rstrip(":")
    return None


def _process_entry(entry: str, version: str, resolution_map: dict[tuple[str, str], str]) -> None:
    result = None

    if "@patch:" in entry:
        result = _extract_patch_entry(entry)
    elif "@npm:" in entry:
        result = _extract_npm_entry(entry)
    elif entry.startswith("@") and entry.count("@") >= 2:
        result = _extract_scoped_entry(entry)
    elif "@" in entry:
        result = _extract_simple_entry(entry)

    if result:
        pkg_name, version_range = result
        resolution_map[(pkg_name, version_range)] = version


def _build_resolution_map_from_parsed(
    parsed_yarn_lock: dict[PackageKey, YarnPackage],
) -> dict[tuple[str, str], str]:
    resolution_map: dict[tuple[str, str], str] = {}

    for item in parsed_yarn_lock.values():
        raw_key = item.get("raw_key")
        version = item.get("version")

        if not raw_key or not version:
            continue

        entries = raw_key.split(", ")
        for raw_entry in entries:
            entry = raw_entry.strip('"')
            _process_entry(entry, version, resolution_map)

    return resolution_map


def _build_dependency_map_yarn(
    parsed_yarn_lock: dict[PackageKey, YarnPackage],
    resolution_map: dict[tuple[str, str], str],
) -> DependencyMap:
    dependency_map: DependencyMap = {}

    for pkg_key, item in parsed_yarn_lock.items():
        pkg_name = _get_name(pkg_key, item)
        version = item.get("version")

        if "dependencies" in item and version is not None:
            deps_dict: dict[str, str] = {}

            for dep_name, dep_version in item["dependencies"]:
                clean_name = dep_name.strip('"')
                version_range = dep_version.strip('"')

                resolved_version = resolution_map.get((clean_name, version_range))

                deps_dict[clean_name] = resolved_version or version_range

            package_key = f"{pkg_name}@{version}"
            dependency_map[package_key] = deps_dict

    return dependency_map


def _build_key_map_yarn(
    parsed_yarn_lock: dict[PackageKey, YarnPackage],
) -> dict[tuple[str, int], str]:
    key_map: dict[tuple[str, int], str] = {}

    for pkg_key, item in parsed_yarn_lock.items():
        pkg_name = _get_name(pkg_key, item)
        version = item.get("version")
        line = item.get("line")

        if line is not None and version is not None:
            key_map[(pkg_name, line)] = f"{pkg_name}@{version}"

    return key_map


def _get_name(pkg_info: PackageKey, item: YarnPackage) -> str:
    if resolution := item.get("resolution"):
        is_scoped_package = resolution.startswith("@")
        if is_scoped_package:
            return f"@{resolution.split('@')[1]}"
        return resolution.split("@")[0]

    return pkg_info.name


def _parse_current_package(line: str, index: int) -> tuple[str | None, int | None]:
    line = line.strip()
    if match_ := re.match(r'^"?((?:@\w[\w\-\.]*/)?\w[\w\-\.]*)@', line):
        current_package = match_.groups()[0]
        current_package_line = index
    else:
        current_package = None
        current_package_line = None

    return current_package, current_package_line


def _resolve_pair(line: str) -> tuple[str, str]:
    line = line.strip()
    if ": " in line:
        key, value = line.split(": ")
        return key.strip(), value.strip()

    key, value = line.split(" ", maxsplit=1)
    return key.strip(), value.strip()


def _count_indentation(line: str) -> int:
    # Stripping the leading spaces and comparing the length difference
    return len(line) - len(line.lstrip(" "))


def _is_start_of_list_line(state: ParserState, line: str) -> bool:
    return bool(
        state.current_package and state.current_package_version and line.strip().endswith(":"),
    )


def _is_list_item_line(state: ParserState, line: str) -> bool:
    return bool(
        state.current_package
        and state.current_package_version
        and state.current_key
        and state.current_indentation
        and _count_indentation(line) > state.current_indentation,
    )
