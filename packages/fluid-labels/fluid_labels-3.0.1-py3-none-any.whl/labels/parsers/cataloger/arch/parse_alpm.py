from typing import Any

from labels.model.ecosystem_data.arch import AlpmDBEntry
from labels.model.file import Location, LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment, Release
from labels.model.resolver import Resolver
from labels.parsers.cataloger.arch.package_builder import new_arch_package

ALLOWED_STRING_KEYS: set[str] = {"name", "base", "version", "arch"}


def parse_alpm_db(
    _resolver: Resolver,
    environment: Environment,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    alpm_db_entry = _collect_alpm_db_entry(reader.read_closer.read())
    if not alpm_db_entry:
        return [], []

    packages = _collect_packages(alpm_db_entry, environment.linux_release, reader.location)

    return packages, []


def _collect_packages(
    alpm_db_entry: AlpmDBEntry, linux_release: Release | None, location: Location
) -> list[Package]:
    packages: list[Package] = []

    package = new_arch_package(alpm_db_entry, linux_release, location)
    if package:
        packages.append(package)

    return packages


def _collect_alpm_db_entry(content: str) -> AlpmDBEntry | None:
    pkg_fields: dict[str, Any] = {}
    lines = content.split("\n\n")

    for line in lines:
        if not line.strip():
            break  # End of block or file
        pkg_fields.update(_parse_key_value_pair(line))

    if pkg_fields:
        return _parse_raw_entry(pkg_fields)

    return None


def _parse_raw_entry(pkg_fields: dict[str, Any]) -> AlpmDBEntry:
    return AlpmDBEntry(
        package=pkg_fields.get("name", ""),
        base_package=pkg_fields.get("base", ""),
        version=pkg_fields.get("version", ""),
        architecture=pkg_fields.get("arch", ""),
    )


def _parse_key_value_pair(line: str) -> dict[str, Any]:
    try:
        key, value = line.split("\n", 1)
    except ValueError:
        return {}

    key = key.replace("%", "").lower()
    value = value.strip()

    if key not in ALLOWED_STRING_KEYS:
        return {}

    return {key: value}
