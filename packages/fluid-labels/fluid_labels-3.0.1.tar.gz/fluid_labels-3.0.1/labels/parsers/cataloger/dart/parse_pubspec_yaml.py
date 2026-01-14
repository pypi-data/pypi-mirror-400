from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.dart.package_builder import new_pubspec_package
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter


def parse_pubspec_yaml(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    file_content = parse_yaml_with_tree_sitter(reader.read_closer.read())
    if not isinstance(file_content, IndexedDict):
        return [], []

    packages = _collect_packages(file_content, reader)

    return packages, []


def _collect_packages(
    file_content: IndexedDict[str, ParsedValue], reader: LocationReadCloser
) -> list[Package]:
    deps = file_content.get("dependencies")
    dev_deps = file_content.get("dev_dependencies")

    return [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]


def _get_packages(
    reader: LocationReadCloser,
    dependencies: ParsedValue,
    *,
    is_dev: bool = False,
) -> list[Package]:
    packages: list[Package] = []
    if not isinstance(dependencies, IndexedDict):
        return packages

    for name, version in dependencies.items():
        if not name or not isinstance(version, str):
            continue

        new_location = get_enriched_location(
            reader.location,
            line=dependencies.get_key_position(name).start.line,
            is_dev=is_dev,
            is_transitive=False,
        )

        package = new_pubspec_package(name, version, new_location)
        if package:
            packages.append(package)

    return packages
