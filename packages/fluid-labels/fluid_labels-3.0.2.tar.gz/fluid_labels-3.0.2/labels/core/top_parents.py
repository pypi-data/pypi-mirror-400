from typing import NamedTuple

from labels.model.file import DependencyChain, DependencyType
from labels.model.package import Package, PackageType
from labels.model.relationship import Relationship


class _PathContext(NamedTuple):
    rel_map: dict[str, list[str]]
    package_names_cache: dict[str, str]
    packages_by_id: dict[str, Package]
    current_name: str
    current_version: str


def calculate_top_parents_for_packages(
    packages: list[Package],
    relationships: list[Relationship],
) -> list[Package]:
    rel_map = build_relationship_map(relationships)

    package_names_cache = {pkg.id_: f"{pkg.name}@{pkg.version}" for pkg in packages}
    packages_by_id = {pkg.id_: pkg for pkg in packages}

    for pkg in packages:
        if pkg.type != PackageType.NpmPkg:
            continue
        for location in pkg.locations:
            node_id = f"{pkg.id_}@{location.location_id()}"
            context = _PathContext(
                rel_map=rel_map,
                package_names_cache=package_names_cache,
                packages_by_id=packages_by_id,
                current_name=pkg.name,
                current_version=pkg.version,
            )
            top_parents_with_paths = find_top_parents(node_id, context)
            current_pkg_name_version = f"{pkg.name}@{pkg.version}"

            if (
                location.dependency_type in (DependencyType.DIRECT, DependencyType.ROOT)
                and current_pkg_name_version in top_parents_with_paths
            ):
                del top_parents_with_paths[current_pkg_name_version]

            if top_parents_with_paths:
                location.top_parents = sorted(top_parents_with_paths.keys())
                location.dependency_chains = [
                    DependencyChain(depth=len(path), chain=path)
                    for path in top_parents_with_paths.values()
                ]
                location.dependency_chains.sort(key=lambda x: (x.depth, x.chain[-1]))
            else:
                location.top_parents = None
                location.dependency_chains = None

    return packages


def build_relationship_map(relationships: list[Relationship]) -> dict[str, list[str]]:
    rel_map: dict[str, list[str]] = {}
    for rel in relationships:
        if rel.type.value == "dependency-of":
            if rel.from_ not in rel_map:
                rel_map[rel.from_] = []
            rel_map[rel.from_].append(rel.to_)
    return rel_map


MAX_TRAVERSAL_ITERATIONS = 100_000


def _extract_package_id(node_id: str) -> str:
    return node_id.split("@")[0]


def _extract_location_id(node_id: str) -> str:
    return node_id.split("@", 1)[1]


def _get_package_name_version(package_id: str, cache: dict[str, str]) -> str:
    return cache.get(package_id, package_id)


def _get_dependency_type(
    node_id: str,
    packages_by_id: dict[str, Package],
) -> DependencyType | None:
    pkg_id = _extract_package_id(node_id)
    pkg = packages_by_id.get(pkg_id)

    if not pkg:
        return None

    location_id = _extract_location_id(node_id)
    location = next(
        (loc for loc in pkg.locations if loc.location_id() == location_id),
        None,
    )

    return location.dependency_type if location else None


def _should_add_as_top_parent(
    node_id: str,
    packages_by_id: dict[str, Package],
) -> bool:
    dep_type = _get_dependency_type(node_id, packages_by_id)

    if dep_type is None:
        return True

    return dep_type == DependencyType.DIRECT


def _is_root_node(node_id: str, packages_by_id: dict[str, Package]) -> bool:
    dep_type = _get_dependency_type(node_id, packages_by_id)
    return dep_type == DependencyType.ROOT


def _add_node_to_results(
    node_id: str,
    path: list[str],
    results: dict[str, list[str]],
    context: _PathContext,
) -> None:
    pkg_id = _extract_package_id(node_id)
    pkg_name = _get_package_name_version(pkg_id, context.package_names_cache)

    if pkg_name not in results:
        results[pkg_name] = path


def _handle_circular_dependencies(
    parents: list[str],
    visited: set[str],
    current_path: list[str],
    results: dict[str, list[str]],
    context: _PathContext,
) -> None:
    if not parents or not all(p in visited for p in parents):
        return

    if not context.packages_by_id:
        return

    for parent_id in parents:
        if not _should_add_as_top_parent(parent_id, context.packages_by_id):
            continue

        pkg_id = _extract_package_id(parent_id)
        parent_name = _get_package_name_version(pkg_id, context.package_names_cache)
        extended_path = [*current_path, parent_name]

        if parent_name not in results:
            results[parent_name] = extended_path


def find_top_parents(
    node_id: str,
    context: _PathContext,
) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {}

    start_pkg_id = _extract_package_id(node_id)
    start_name = _get_package_name_version(start_pkg_id, context.package_names_cache)
    queue: list[tuple[str, list[str]]] = [(node_id, [start_name])]
    visited: set[str] = {node_id}
    iterations = 0

    while queue:
        iterations += 1
        if iterations > MAX_TRAVERSAL_ITERATIONS:
            break

        current_id, current_path = queue.pop(0)
        parents = context.rel_map.get(current_id, [])

        if not parents:
            if _should_add_as_top_parent(current_id, context.packages_by_id):
                _add_node_to_results(current_id, current_path, results, context)
            continue

        for parent_id in parents:
            if _is_root_node(parent_id, context.packages_by_id):
                _add_node_to_results(current_id, current_path, results, context)
                continue

            if parent_id in visited:
                continue

            parent_pkg_id = _extract_package_id(parent_id)
            parent_name = _get_package_name_version(parent_pkg_id, context.package_names_cache)
            new_path = [*current_path, parent_name]

            visited.add(parent_id)
            queue.append((parent_id, new_path))

        _handle_circular_dependencies(parents, visited, current_path, results, context)

    return results if results else {}
