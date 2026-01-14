from typing import NamedTuple

from labels.model.file import DependencyType, Location
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.javascript.common import (
    DependencyMap,
    get_direct_dependencies_with_fallback,
    is_version_compatible,
    normalize_npm_alias,
)
from labels.parsers.cataloger.javascript.package_builder import new_npm_package_from_lock
from labels.parsers.cataloger.utils import get_enriched_location


class NpmContext(NamedTuple):
    lockfile_path: str
    parent_key: str
    key_map: dict[tuple[str, int], str]


class RelationshipContext(NamedTuple):
    packages: list[Package]
    dependency_map: DependencyMap
    location: Location
    key_map: dict[tuple[str, int], str]
    root_package: Package | None
    direct_dependencies: list[str]
    dependencies: IndexedDict[str, ParsedValue]


def _create_root_package(
    location: Location,
    file_content: IndexedDict[str, ParsedValue],
) -> Package | None:
    root_name = file_content.get("name")
    root_version = file_content.get("version")

    if not isinstance(root_name, str) or not isinstance(root_version, str):
        return None

    root_location = get_enriched_location(
        location,
        line=1,
        is_dev=False,
        is_transitive=False,
    )
    update_root: dict[str, DependencyType] = {"dependency_type": DependencyType.ROOT}
    root_location = root_location.model_copy(deep=True, update=update_root)

    return new_npm_package_from_lock(
        location=root_location,
        name=root_name,
        value=file_content,
        lockfile_version=1,
    )


def parse_package_lock_v1(
    location: Location,
    file_content: IndexedDict[str, ParsedValue],
) -> tuple[list[Package], list[Relationship]]:
    dependencies = file_content.get("dependencies")
    if not isinstance(dependencies, IndexedDict):
        return [], []

    packages = []
    root_package = _create_root_package(location, file_content)
    if root_package:
        packages.append(root_package)

    direct_dependencies = _get_direct_dependencies_v1(location, dependencies)
    packages.extend(_collect_packages(location, dependencies, direct_dependencies))

    consolidated_packages = _consolidate_packages_v1(packages)

    # Get consolidated root package
    consolidated_root = None
    if root_package:
        for pkg in consolidated_packages:
            if pkg.name == root_package.name and pkg.version == root_package.version:
                consolidated_root = pkg
                break

    dependency_map = _build_dependency_map_v1(dependencies)
    key_map = _build_key_map_v1(dependencies)

    rel_context = RelationshipContext(
        packages=consolidated_packages,
        dependency_map=dependency_map,
        location=location,
        key_map=key_map,
        root_package=consolidated_root,
        direct_dependencies=direct_dependencies,
        dependencies=dependencies,
    )
    relationships = _build_relationships_v1(rel_context)

    return consolidated_packages, relationships


def _consolidate_packages_v1(packages: list[Package]) -> list[Package]:
    consolidated: dict[tuple[str, str], Package] = {}

    for pkg in packages:
        key = (pkg.name, pkg.version)
        if key in consolidated:
            existing_pkg = consolidated[key]
            for loc in pkg.locations:
                if loc not in existing_pkg.locations:
                    existing_pkg.locations.append(loc)
        else:
            consolidated[key] = pkg

    return list(consolidated.values())


def _get_direct_dependencies_fallback(dependencies: IndexedDict[str, ParsedValue]) -> list[str]:
    """Fallback: infer direct dependencies from lockfile (less accurate)."""
    transitives: set[str] = set()
    for details in dependencies.values():
        if not isinstance(details, IndexedDict):
            continue

        requires = details.get("requires")
        if not isinstance(requires, IndexedDict):
            continue

        transitives.update(requires.keys())

    return [dependency for dependency in dependencies if dependency not in transitives]


def _get_direct_dependencies_v1(
    location: Location,
    dependencies: IndexedDict[str, ParsedValue],
) -> list[str]:
    fallback = _get_direct_dependencies_fallback(dependencies)
    return get_direct_dependencies_with_fallback(location, fallback)


def _collect_packages(
    location: Location,
    dependencies: IndexedDict[str, ParsedValue],
    direct_dependencies: list[str],
) -> list[Package]:
    packages: list[Package] = []
    for dependency_key, dependency_value in dependencies.items():
        if not isinstance(dependency_value, IndexedDict):
            continue

        is_transitive = dependency_key not in direct_dependencies
        is_dev = dependency_value.get("dev") is True
        new_location = get_enriched_location(
            location,
            line=dependency_value.position.start.line,
            is_dev=is_dev,
            is_transitive=is_transitive,
        )

        package = new_npm_package_from_lock(
            location=new_location, name=dependency_key, value=dependency_value, lockfile_version=1
        )
        if package:
            packages.append(package)

        sub_dependencies = dependency_value.get("dependencies")
        if isinstance(sub_dependencies, IndexedDict):
            packages.extend(_collect_packages(location, sub_dependencies, direct_dependencies))

    return packages


def _build_dependency_map_v1(
    dependencies: IndexedDict[str, ParsedValue],
    result: DependencyMap | None = None,
    parent_context: str = "",
) -> DependencyMap:
    if result is None:
        result = {}

    for dependency_key, dependency_value in dependencies.items():
        if not isinstance(dependency_value, IndexedDict):
            continue

        requires_dict = dependency_value.get("requires")
        if isinstance(requires_dict, IndexedDict):
            full_key = f"{parent_context}>{dependency_key}" if parent_context else dependency_key
            result[full_key] = {k: str(v) for k, v in requires_dict.data.items()}

        sub_dependencies = dependency_value.get("dependencies")
        if isinstance(sub_dependencies, IndexedDict):
            full_key_for_recursion = (
                f"{parent_context}>{dependency_key}" if parent_context else dependency_key
            )
            _build_dependency_map_v1(sub_dependencies, result, full_key_for_recursion)

    return result


def _build_key_map_v1(
    dependencies: IndexedDict[str, ParsedValue],
    result: dict[tuple[str, int], str] | None = None,
    parent_context: str = "",
) -> dict[tuple[str, int], str]:
    if result is None:
        result = {}

    for dependency_key, dependency_value in dependencies.items():
        if not isinstance(dependency_value, IndexedDict):
            continue

        line = dependency_value.position.start.line
        full_key = f"{parent_context}>{dependency_key}" if parent_context else dependency_key
        result[(dependency_key, line)] = full_key

        version = dependency_value.get("version")
        if isinstance(version, str):
            normalized_name, _ = normalize_npm_alias(version)
            if normalized_name:
                result[(normalized_name, line)] = full_key

        sub_dependencies = dependency_value.get("dependencies")
        if isinstance(sub_dependencies, IndexedDict):
            _build_key_map_v1(sub_dependencies, result, full_key)

    return result


def _resolve_child_location_v1(
    parent_key: str,
    dependency_name: str,
    dep_locations: list[Location],
    key_map: dict[tuple[str, int], str],
) -> Location | None:
    """Resolve the correct child location for npm v1."""
    candidate_keys = [f"{parent_key}>{dependency_name}"]

    parts = parent_key.split(">")
    for i in range(len(parts) - 1, -1, -1):
        ancestor_key = ">".join(parts[:i])
        if ancestor_key:
            candidate_keys.append(f"{ancestor_key}>{dependency_name}")

    candidate_keys.append(dependency_name)

    for candidate_key in candidate_keys:
        for dep_location in dep_locations:
            line = dep_location.coordinates.line if dep_location.coordinates else None
            if line is None:
                continue

            actual_key = key_map.get((dependency_name, line))

            if actual_key == candidate_key:
                return dep_location

    return None


def _normalize_npm_alias_name(alias_name: str, dependencies: IndexedDict[str, ParsedValue]) -> str:
    """Normalize npm alias name to the actual package name."""
    dep_value = dependencies.get(alias_name)
    if isinstance(dep_value, IndexedDict):
        version = dep_value.get("version")
        if isinstance(version, str):
            normalized_name, _ = normalize_npm_alias(version)
            if normalized_name:
                return normalized_name
    return alias_name


def _add_root_dependency_relationship(  # noqa: PLR0913
    dep_name: str,
    ctx: RelationshipContext,
    packages_by_name: dict[str, list[Package]],
    root_location: Location,
    lockfile_path: str,
    relationships: list[Relationship],
) -> None:
    """Add relationship for a single direct dependency to root."""
    normalized_name = _normalize_npm_alias_name(dep_name, ctx.dependencies)

    for dep_pkg in packages_by_name.get(normalized_name, []):
        all_locs = [loc for loc in dep_pkg.locations if loc.path() == lockfile_path]
        for dep_loc in all_locs:
            line = dep_loc.coordinates.line if dep_loc.coordinates else None
            if line is None:
                continue

            dep_key = ctx.key_map.get((dep_name, line))
            if not dep_key:
                dep_key = ctx.key_map.get((normalized_name, line))

            if dep_key in (dep_name, normalized_name) and ctx.root_package:
                from_id = f"{dep_pkg.id_}@{dep_loc.location_id()}"
                to_id = f"{ctx.root_package.id_}@{root_location.location_id()}"
                relationships.append(
                    Relationship(
                        from_=from_id,
                        to_=to_id,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    )
                )
                break


def _create_root_relationships(
    ctx: RelationshipContext,
    packages_by_name: dict[str, list[Package]],
    lockfile_path: str,
) -> list[Relationship]:
    """Create relationships from direct dependencies to root package."""
    relationships: list[Relationship] = []

    if not ctx.root_package:
        return relationships

    root_location = None
    for loc in ctx.root_package.locations:
        if loc.path() == lockfile_path:
            root_location = loc
            break

    if not root_location:
        return relationships

    for dep_name in ctx.direct_dependencies:
        _add_root_dependency_relationship(
            dep_name, ctx, packages_by_name, root_location, lockfile_path, relationships
        )

    return relationships


def _build_relationships_v1(ctx: RelationshipContext) -> list[Relationship]:
    """Build relationships for npm v1 using location resolution."""
    lockfile_path = ctx.location.path()
    relationships: list[Relationship] = []

    packages_by_name: dict[str, list[Package]] = {}
    for pkg in ctx.packages:
        packages_by_name.setdefault(pkg.name, []).append(pkg)

    relationships.extend(_create_root_relationships(ctx, packages_by_name, lockfile_path))

    for package in ctx.packages:
        package_lock_locations = [loc for loc in package.locations if loc.path() == lockfile_path]
        if not package_lock_locations:
            continue

        for package_location in package_lock_locations:
            line = package_location.coordinates.line if package_location.coordinates else None
            if line is None:
                continue

            dep_key = ctx.key_map.get((package.name, line))
            if not dep_key:
                continue

            dependencies = ctx.dependency_map.get(dep_key)
            if not dependencies:
                continue

            npm_ctx = NpmContext(lockfile_path, dep_key, ctx.key_map)
            relationships.extend(
                _create_npm_relationships(
                    package, package_location, dependencies, packages_by_name, npm_ctx
                )
            )

    return relationships


def _create_npm_relationships(
    package: Package,
    package_location: Location,
    dependencies: dict[str, str],
    packages_by_name: dict[str, list[Package]],
    ctx: NpmContext,
) -> list[Relationship]:
    """Create npm relationships with location resolution."""
    relationships: list[Relationship] = []

    for dependency_name, required_version in dependencies.items():
        search_name = dependency_name
        actual_version = required_version

        if isinstance(required_version, str):
            normalized_name, normalized_version = normalize_npm_alias(required_version)
            if normalized_name:
                search_name = normalized_name
                actual_version = normalized_version

        for dep_pkg in packages_by_name.get(search_name, []):
            if not is_version_compatible(dep_pkg.version, actual_version):
                continue

            all_locs = [loc for loc in dep_pkg.locations if loc.path() == ctx.lockfile_path]
            resolved_location = _resolve_child_location_v1(
                ctx.parent_key, dependency_name, all_locs, ctx.key_map
            )

            if resolved_location:
                from_id = f"{dep_pkg.id_}@{resolved_location.location_id()}"
                to_id = f"{package.id_}@{package_location.location_id()}"
                relationships.append(
                    Relationship(
                        from_=from_id,
                        to_=to_id,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    )
                )

    return relationships
