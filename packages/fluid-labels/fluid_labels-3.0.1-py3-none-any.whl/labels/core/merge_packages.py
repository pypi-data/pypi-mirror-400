import itertools
import logging
import os
from collections import defaultdict
from os.path import split
from pathlib import Path

from fluidattacks_core.semver.match_versions import match_version_ranges

from labels.advisories.utils import DatabasesToDownload
from labels.enrichers.dispatcher import IMAGES_TYPES
from labels.model.file import DependencyType, Location
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType

LOGGER = logging.getLogger(__name__)

POSSIBLE_LOCK_FILES = {
    "Pipfile": ["Pipfile.lock"],
    "composer.json": ["composer.lock"],
    "packages.config": ["packages.lock.json"],
    "package.json": [
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        # For angular libraries
        "ng-package.json",
    ],
    "Gemfile": ["Gemfile.lock", "gems.locked"],
    "pyproject.toml": ["poetry.lock", "uv.lock"],
    "package.swift": ["Package.resolved"],
    "Package.swift": ["Package.resolved"],
}

LOCK_FILE_NAMES = set(itertools.chain(*POSSIBLE_LOCK_FILES.values()))


def extract_file_info(path: str) -> str:
    _, file_info = split(path)
    return file_info


def _find_lock_and_non_lock_files(
    locations: list[Location],
) -> tuple[list[Location], list[Location]]:
    non_lock_files = []
    lock_files = []

    for location in locations:
        file_info = extract_file_info(location.path())
        if file_info in POSSIBLE_LOCK_FILES:
            non_lock_files.append(location)
        elif any(file_info == lock for locks in POSSIBLE_LOCK_FILES.values() for lock in locks):
            lock_files.append(location)

    return lock_files, non_lock_files


def _get_corresponding_manifest_path(lock_file: Location) -> str | None:
    lock_path = lock_file.access_path or (
        lock_file.coordinates.real_path if lock_file.coordinates else None
    )
    if not lock_path:
        return None

    lock_file_name = extract_file_info(lock_path)
    for manifest_name, lock_names in POSSIBLE_LOCK_FILES.items():
        if lock_file_name in lock_names:
            lock_dir = parent_dir(lock_path)
            manifest_path = Path(lock_dir) / manifest_name

            if lock_file.coordinates and lock_file.coordinates.real_path:
                real_lock_dir = parent_dir(lock_file.coordinates.real_path)
                manifest_real_path = Path(real_lock_dir) / manifest_name
                if manifest_real_path.exists():
                    return str(manifest_real_path)

            if manifest_path.exists():
                return str(manifest_path)

    return None


def update_package_locations(packages: list[Package]) -> None:
    for package in packages:
        lock_files, non_lock_files = _find_lock_and_non_lock_files(package.locations)

        for lock_file in lock_files:
            lock_file_path = lock_file.access_path or (
                lock_file.coordinates.real_path if lock_file.coordinates else None
            )
            if not lock_file_path:
                continue

            found_package_in_manifest = False
            for non_lock_file in non_lock_files:
                if same_directory(lock_file_path, non_lock_file.path()):
                    if lock_file.dependency_type != DependencyType.ROOT:
                        lock_file.dependency_type = non_lock_file.dependency_type
                    lock_file.scope = non_lock_file.scope
                    found_package_in_manifest = True
                    break

            if found_package_in_manifest:
                continue

            corresponding_manifest_path = _get_corresponding_manifest_path(lock_file)
            if (
                corresponding_manifest_path
                and lock_file.dependency_type == DependencyType.UNDETERMINABLE
            ):
                lock_file.dependency_type = DependencyType.TRANSITIVE


def parent_dir(path: str) -> str:
    p = path.rstrip(os.sep)
    if os.sep not in p:
        return ""
    return p.rsplit(os.sep, 1)[0]


def same_directory(lock_path: str, non_lock_path: str) -> bool:
    if lock_path.rsplit(os.sep, 1)[-1] in POSSIBLE_LOCK_FILES.get(
        non_lock_path.rsplit(os.sep, 1)[-1],
        [],
    ):
        return parent_dir(non_lock_path) == parent_dir(lock_path)

    return False


def _merge_locations(target: Package, source: Package) -> None:
    for loc in source.locations:
        if loc not in target.locations:
            target.locations.append(loc)


def obtain_locations_candidates(
    packages: dict[str, Package],
) -> tuple[
    dict[str, list[tuple[str, str, str, Location]]],
    dict[str, dict[str, list[tuple[str, str]]]],
]:
    non_lock_locations: dict[str, list[tuple[str, str, str, Location]]] = defaultdict(list)
    lock_locations: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for pkg_id, pkg in packages.items():
        for location in pkg.locations:
            if not location.access_path:
                continue
            file_name = location.access_path.rsplit(os.sep, 1)[-1]
            pkg_key = f"{pkg.name}_{pkg.language.value}_{pkg.type.value}"
            if file_name in POSSIBLE_LOCK_FILES:
                non_lock_locations[location.access_path].append(
                    (pkg_key, pkg.version, pkg_id, location)
                )
            elif file_name in LOCK_FILE_NAMES:
                lock_locations[location.access_path][pkg_key].append((pkg.version, pkg_id))

    return non_lock_locations, lock_locations


def merge_non_lock_locations(
    merged_packages: dict[str, Package],
) -> tuple[list[Package], list[Relationship]]:
    relationships: list[Relationship] = []
    non_lock_locations, lock_locations = obtain_locations_candidates(merged_packages)
    lock_files = list(lock_locations.keys())

    for location_path, pkgs_info in non_lock_locations.items():
        searched_lock_files = [
            lock_path
            for lock_path in lock_files
            if lock_path.rsplit(os.sep, 1)[-1]
            in POSSIBLE_LOCK_FILES.get(location_path.rsplit(os.sep, 1)[-1], [])
            and same_directory(lock_path, location_path)
        ]
        if not searched_lock_files:
            continue

        for pkg_info in pkgs_info:
            pkg_key, pkg_version, pkg_id, non_lock_location = pkg_info

            possible_equivalent_pkgs = [
                pkg_info[1]
                for searched_lock_file in searched_lock_files
                if (pkgs := lock_locations[searched_lock_file].get(pkg_key, []))
                for pkg_info in pkgs
                if match_version_ranges(pkg_info[0], pkg_version)
            ]

            if not possible_equivalent_pkgs:
                continue

            equivalent_lock_pkg_id = sorted(possible_equivalent_pkgs)[0]

            if not equivalent_lock_pkg_id:
                continue

            # Generate relationships DESCRIBED_BY: lock → non-lock
            lock_pkg = merged_packages[equivalent_lock_pkg_id]
            for lock_location in lock_pkg.locations:
                if lock_location.access_path in searched_lock_files:
                    from_id = f"{lock_pkg.id_}@{lock_location.location_id()}"
                    to_id = f"{lock_pkg.id_}@{non_lock_location.location_id()}"
                    relationships.append(
                        Relationship(
                            from_=from_id,
                            to_=to_id,
                            type=RelationshipType.DESCRIBED_BY_RELATIONSHIP,
                        )
                    )

            merged_packages[equivalent_lock_pkg_id].locations.append(non_lock_location)
            merged_packages[pkg_id].locations.remove(non_lock_location)

            if not merged_packages[pkg_id].locations:
                del merged_packages[pkg_id]

    return list(merged_packages.values()), relationships


def merge_packages(
    packages: list[Package],
) -> tuple[list[Package], list[Relationship], DatabasesToDownload]:
    # merge locations from equal packages based on id
    same_packages: dict[str, Package] = {}
    download_images_db = False
    for pkg in packages:
        if pkg.type in IMAGES_TYPES:
            download_images_db = True

        if pkg.id_ in same_packages:
            _merge_locations(same_packages[pkg.id_], pkg)
        else:
            same_packages[pkg.id_] = pkg

    # Merge locations from lock and non-lock files and generate DESCRIBED_BY relationships
    merged_packages, described_by_relationships = merge_non_lock_locations(same_packages)

    update_package_locations(merged_packages)
    return (
        merged_packages,
        described_by_relationships,
        DatabasesToDownload(roots_db=True, images_db=download_images_db),
    )
