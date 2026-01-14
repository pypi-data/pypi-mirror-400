from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.package_builder import new_simple_npm_package
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter


def parse_package_json(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    file_content = parse_json_with_tree_sitter(reader.read_closer.read())
    if not isinstance(file_content, IndexedDict):
        return [], []

    packages = _collect_packages(file_content, reader)

    root_package = _create_root_package(file_content, reader)
    if root_package:
        packages.insert(0, root_package)

    return packages, []


def _create_root_package(
    file_content: IndexedDict[str, ParsedValue], reader: LocationReadCloser
) -> Package | None:
    root_name = file_content.get("name")
    root_version = file_content.get("version")

    if not isinstance(root_name, str) or not isinstance(root_version, str):
        return None

    root_location = get_enriched_location(
        reader.location,
        line=1,
        is_transitive=False,
        is_dev=False,
    )

    return new_simple_npm_package(root_location, root_name, root_version)


def _collect_packages(
    file_content: IndexedDict[str, ParsedValue], reader: LocationReadCloser
) -> list[Package]:
    return [
        *_create_packages(file_content, reader, is_dev=False),
        *_create_packages(file_content, reader, is_dev=True),
    ]


def _create_packages(
    content: IndexedDict[str, ParsedValue], reader: LocationReadCloser, *, is_dev: bool
) -> list[Package]:
    packages: list[Package] = []
    dependencies_key = "devDependencies" if is_dev else "dependencies"

    dependencies = content.get(dependencies_key)
    if not isinstance(dependencies, IndexedDict):
        return packages

    for package_name, specifier in dependencies.items():
        if not package_name:
            continue

        new_location = get_enriched_location(
            reader.location,
            line=dependencies.get_key_position(package_name).start.line,
            is_dev=is_dev,
            is_transitive=False,
        )

        package = new_simple_npm_package(new_location, package_name, str(specifier))
        if package:
            packages.append(package)

    return packages
