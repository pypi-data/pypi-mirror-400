from bs4 import BeautifulSoup

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.dotnet.package_builder import new_dotnet_package
from labels.parsers.cataloger.utils import get_enriched_location

PACKAGE_TAG = "package"


def parse_dotnet_pkgs_config(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    file_content = BeautifulSoup(reader.read_closer.read(), features="html.parser")

    packages = _collect_packages(file_content, reader.location)

    return packages, []


def _collect_packages(file_content: BeautifulSoup, location: Location) -> list[Package]:
    packages: list[Package] = []

    for raw_package in file_content.find_all(PACKAGE_TAG, recursive=True):
        name = raw_package.get("id")
        version = raw_package.get("version")

        new_location = get_enriched_location(
            location, line=raw_package.sourceline, is_transitive=False
        )

        new_package = new_dotnet_package(name, version, new_location)
        if new_package:
            packages.append(new_package)

    return packages
