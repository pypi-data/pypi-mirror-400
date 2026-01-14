import re

from bs4 import BeautifulSoup

from labels.model.file import LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.package_builder import new_simple_npm_package
from labels.parsers.cataloger.utils import get_enriched_location

SCRIPT_DEP = re.compile(
    r"(?P<name>[^\s\/]*)(?P<separator>[-@\/])"
    r"(?P<version>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))",
)

NPM_CDNS = (
    "https://cdn.jsdelivr.net/npm/",
    "https://unpkg.com/",
    "https://cdn.skypack.dev/",
    "https://cdn.esm.sh/",
    "https://code.jquery.com/",
)


def parse_html_scripts(
    _resolver: Resolver | None, _env: Environment | None, reader: LocationReadCloser
) -> tuple[list[Package], list[Relationship]]:
    html = _safe_parse_html(reader)
    if not html:
        return [], []

    packages = _collect_packages(html, reader)

    return packages, []


def _collect_packages(html: BeautifulSoup, reader: LocationReadCloser) -> list[Package]:
    packages: list[Package] = []

    for script in html("script"):
        src_attribute = str(script.attrs.get("src"))
        if not (src_attribute and src_attribute.endswith(".js")):
            continue

        if not src_attribute.startswith(NPM_CDNS):
            continue

        name_version = _parse_name_version_from_src(src_attribute)
        if not name_version:
            continue

        name, version = name_version

        new_location = get_enriched_location(reader.location, line=script.sourceline)

        package = new_simple_npm_package(new_location, name, version)
        if package:
            packages.append(package)

    return packages


def _safe_parse_html(reader: LocationReadCloser) -> BeautifulSoup | None:
    try:
        return BeautifulSoup(reader.read_closer, features="html.parser")
    except (UnicodeError, AssertionError):
        return None


def _parse_name_version_from_src(src: str) -> tuple[str, str] | None:
    matched = SCRIPT_DEP.search(src)
    if not matched:
        return None

    return matched.group("name"), matched.group("version")
