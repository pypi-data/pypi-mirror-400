import re
from pathlib import Path
from typing import TypeAlias

from fluidattacks_core.semver.match_versions import match_version_ranges

from labels.model.file import DependencyType, Location
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.parsers.cataloger.javascript.package_builder import new_simple_npm_package
from labels.parsers.cataloger.utils import LOGGER, get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter

DependencyRequirements: TypeAlias = dict[str, str]

DependencyMap: TypeAlias = dict[str, DependencyRequirements]


def _normalize_version_or_list(version_str: str) -> str:
    parts = [p.strip() for p in version_str.split("||")]
    normalized: list[str] = []
    for p in parts:
        if re.fullmatch(r"\d+(?:\.\d+)?", p):
            normalized.append(f"{p}.*")
        else:
            normalized.append(p)
    return " || ".join(normalized)


def normalize_npm_alias(version_or_alias: str) -> tuple[str | None, str]:
    if version_or_alias.startswith("npm:"):
        parts = version_or_alias.removeprefix("npm:").rsplit("@", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
    return None, version_or_alias


def read_package_json(location: Location) -> IndexedDict[str, ParsedValue] | None:
    if not (location.coordinates and location.coordinates.real_path):
        return None

    lockfile_path = Path(location.coordinates.real_path)
    package_json_path = lockfile_path.parent / "package.json"

    if not package_json_path.exists():
        return None

    try:
        with package_json_path.open("r", encoding="utf-8") as f:
            content = parse_json_with_tree_sitter(f.read())
            if isinstance(content, IndexedDict):
                return content
            return None
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Error reading package.json", extra={"extra": {"error": exc}})
        return None


def get_direct_dependencies_from_package_json(location: Location) -> set[str]:
    pkg_json = read_package_json(location)
    if not pkg_json:
        return set()

    direct: set[str] = set()
    deps = pkg_json.get("dependencies")
    dev_deps = pkg_json.get("devDependencies")
    opt_deps = pkg_json.get("optionalDependencies")

    if isinstance(deps, IndexedDict):
        direct.update(deps.keys())
    if isinstance(dev_deps, IndexedDict):
        direct.update(dev_deps.keys())
    if isinstance(opt_deps, IndexedDict):
        direct.update(opt_deps.keys())

    return direct


def get_dev_dependencies_from_package_json(location: Location) -> set[str]:
    pkg_json = read_package_json(location)
    if not pkg_json:
        return set()

    dev_deps = pkg_json.get("devDependencies")
    if isinstance(dev_deps, IndexedDict):
        return set(dev_deps.keys())

    return set()


def get_direct_dependencies_with_fallback(location: Location, fallback: list[str]) -> list[str]:
    pkg_json = read_package_json(location)
    if not pkg_json:
        return fallback

    direct: set[str] = set()
    deps = pkg_json.get("dependencies")
    dev_deps = pkg_json.get("devDependencies")
    opt_deps = pkg_json.get("optionalDependencies")

    if isinstance(deps, IndexedDict):
        direct.update(deps.keys())
    if isinstance(dev_deps, IndexedDict):
        direct.update(dev_deps.keys())
    if isinstance(opt_deps, IndexedDict):
        direct.update(opt_deps.keys())

    return list(direct)


def create_root_package_from_package_json(location: Location) -> Package | None:
    pkg_json = read_package_json(location)
    if not pkg_json:
        return None

    root_name = pkg_json.get("name")
    root_version = pkg_json.get("version")

    if not isinstance(root_name, str) or not isinstance(root_version, str):
        return None

    root_location = get_enriched_location(
        location,
        line=1,
        is_transitive=False,
        is_dev=False,
    )
    update_root: dict[str, DependencyType] = {"dependency_type": DependencyType.ROOT}
    root_location = root_location.model_copy(deep=True, update=update_root)

    return new_simple_npm_package(root_location, root_name, root_version)


def find_root_location(root_package: Package, lockfile_path: str) -> Location | None:
    for loc in root_package.locations:
        if loc.coordinates and loc.coordinates.real_path == lockfile_path:
            return loc
    return None


def group_packages_by_name(
    packages: list[Package], root_package_id: str
) -> dict[str, list[Package]]:
    packages_by_name: dict[str, list[Package]] = {}
    for pkg in packages:
        if pkg.id_ != root_package_id:
            packages_by_name.setdefault(pkg.name, []).append(pkg)
    return packages_by_name


def add_dependency_to_root_relationship(
    dep_pkg: Package,
    root_package: Package,
    root_location: Location,
    lockfile_path: str,
    relationships: list[Relationship],
) -> None:
    for dep_loc in dep_pkg.locations:
        if dep_loc.coordinates and dep_loc.coordinates.real_path == lockfile_path:
            from_id = f"{dep_pkg.id_}@{dep_loc.location_id()}"
            to_id = f"{root_package.id_}@{root_location.location_id()}"
            relationships.append(
                Relationship(
                    from_=from_id,
                    to_=to_id,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
            )
            break


def is_version_compatible(package_version: str, required_version: str) -> bool:
    version_str = required_version.strip()
    if version_str in ("*", "*.*", "*.*.*"):
        return True

    version_str = _normalize_version_or_list(version_str)

    return match_version_ranges(package_version, version_str)


def _is_exact_version(version_str: str) -> bool:
    """Check if a version string is exact (no range operators)."""
    return not any(char in version_str for char in ("^", "~", "*", ">", "<", "=", " "))


def build_relationships(
    packages: list[Package],
    dependency_map: DependencyMap,
    location: Location,
    key_map: dict[tuple[str, int], str] | None = None,
) -> list[Relationship]:
    """Build relationships between packages.

    Args:
        packages: List of packages to create relationships for
        dependency_map: Map of package names to their dependencies
        location: Location of the lockfile
        key_map: Optional map for yarn lockfiles

    Returns:
        List of relationships

    """
    lockfile_path = location.path()
    relationships: list[Relationship] = []

    packages_by_name: dict[str, list[Package]] = {}
    for pkg in packages:
        packages_by_name.setdefault(pkg.name, []).append(pkg)

    for package in packages:
        package_lock_locations = [loc for loc in package.locations if loc.path() == lockfile_path]
        if not package_lock_locations:
            continue

        for package_location in package_lock_locations:
            if key_map is not None:
                # Use key_map to get dependencies (for yarn and pnpm)
                relationships.extend(
                    _create_relationships_with_key_map(
                        package,
                        package_location,
                        key_map,
                        dependency_map,
                        packages_by_name,
                        lockfile_path,
                    )
                )
            else:
                # Fallback for simple name lookup (package-lock v1/v2)
                dependencies = dependency_map.get(package.name)
                if not dependencies:
                    continue

                relationships.extend(
                    _create_simple_relationships(
                        package, package_location, dependencies, packages_by_name, lockfile_path
                    )
                )

    return relationships


def _create_relationships_with_key_map(  # noqa: PLR0913
    package: Package,
    package_location: Location,
    key_map: dict[tuple[str, int], str],
    dependency_map: DependencyMap,
    packages_by_name: dict[str, list[Package]],
    lockfile_path: str,
) -> list[Relationship]:
    line = package_location.coordinates.line if package_location.coordinates else None
    if line is None:
        return []

    dep_key = key_map.get((package.name, line))
    if not dep_key:
        return []

    dependencies = dependency_map.get(dep_key)
    if not dependencies:
        return []

    return _create_simple_relationships(
        package, package_location, dependencies, packages_by_name, lockfile_path
    )


def _create_simple_relationships(
    package: Package,
    package_location: Location,
    dependencies: DependencyRequirements,
    packages_by_name: dict[str, list[Package]],
    lockfile_path: str,
) -> list[Relationship]:
    relationships: list[Relationship] = []

    for dependency_name, required_version in dependencies.items():
        use_exact = _is_exact_version(required_version)

        for dep_pkg in packages_by_name.get(dependency_name, []):
            if use_exact:
                if dep_pkg.version != required_version:
                    continue
            elif not is_version_compatible(dep_pkg.version, required_version):
                continue

            dep_locations = [loc for loc in dep_pkg.locations if loc.path() == lockfile_path]

            for dep_location in dep_locations:
                from_id = f"{dep_pkg.id_}@{dep_location.location_id()}"
                to_id = f"{package.id_}@{package_location.location_id()}"
                relationships.append(
                    Relationship(
                        from_=from_id,
                        to_=to_id,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    )
                )

    return relationships
