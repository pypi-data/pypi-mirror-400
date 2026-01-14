from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.swift.package_builder import new_swift_package_manager_package
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter


def parse_package_resolved(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_resolved = parse_json_with_tree_sitter(reader.read_closer.read())
    if not isinstance(package_resolved, IndexedDict):
        return [], []

    package_resolved_pins: ParsedValue = package_resolved.get("pins")
    if not isinstance(package_resolved_pins, IndexedList):
        return [], []

    packages = _collect_packages(package_resolved_pins, reader)

    return packages, []


def _collect_packages(
    package_resolved_pins: IndexedList[ParsedValue], reader: LocationReadCloser
) -> list[Package]:
    packages: list[Package] = []
    for pin in package_resolved_pins:
        if not isinstance(pin, IndexedDict):
            continue
        info = _get_name_and_version(pin)
        if not info:
            continue

        new_location = get_enriched_location(
            reader.location, line=pin.get_key_position("identity").start.line
        )
        if pkg := new_swift_package_manager_package(
            source_url=info[0], version=info[1], location=new_location
        ):
            packages.append(pkg)

    return packages


def _get_name_and_version(
    pin: IndexedDict[str, ParsedValue],
) -> tuple[str, str] | None:
    state: ParsedValue = pin.get("state")

    if not isinstance(state, IndexedDict):
        return None

    name = pin.get("location")
    version = state.get("version")

    if not isinstance(version, str) or not isinstance(name, str):
        return None

    return name, version
