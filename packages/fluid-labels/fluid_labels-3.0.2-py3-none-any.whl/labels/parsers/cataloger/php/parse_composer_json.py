from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.php.package_builder import new_package_from_composer
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter

EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def parse_composer_json(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    file_content = parse_json_with_tree_sitter(reader.read_closer.read())
    if not isinstance(file_content, IndexedDict):
        return [], []

    packages = _collect_packages(file_content, reader)

    return packages, []


def _collect_packages(
    file_content: IndexedDict[str, ParsedValue], reader: LocationReadCloser
) -> list[Package]:
    deps = file_content.get("require")
    dev_deps = file_content.get("require-dev")

    return [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]


def _get_packages(
    reader: LocationReadCloser,
    dependencies: ParsedValue,
    *,
    is_dev: bool,
) -> list[Package]:
    if not isinstance(dependencies, IndexedDict):
        return []

    items = dependencies.items()
    packages = []
    for name, version in items:
        if not isinstance(version, str) or not name:
            continue

        new_location = get_enriched_location(
            reader.location,
            line=dependencies.get_key_position(name).start.line,
            is_dev=is_dev,
            is_transitive=False,
        )

        package = new_package_from_composer(name=name, version=version, location=new_location)
        if package:  # pragma: no branch
            packages.append(package)

    return packages
