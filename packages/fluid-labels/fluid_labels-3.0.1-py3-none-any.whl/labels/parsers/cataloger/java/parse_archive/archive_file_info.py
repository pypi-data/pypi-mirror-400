import re
from pathlib import Path

from pydantic import BaseModel

name_and_version_pattern = re.compile(
    r"(?i)^(?P<name>[a-zA-Z][\w.]*?(?:-[a-zA-Z][\w.]*?)*?)"
    r"(?:-(?P<version>\d.*|build\d.*|rc?\d+(?:[^\w].*)?))?$",
)
secondary_version_pattern = re.compile(
    r"(?:[._-](?P<version>(\d.*|build\d+.*|rc?\d+(?:[a-zA-Z].*)?)))?$",
)


class ArchiveFileInfo(BaseModel):
    raw: str
    name: str
    version: str


def parse_file_info(raw: str) -> ArchiveFileInfo:
    cleaned_filename = Path(raw).stem

    matches = name_and_version_pattern.search(cleaned_filename)

    name = _get_subexp(matches, "name")
    version = _get_subexp(matches, "version")

    if not version:
        matches = secondary_version_pattern.search(name)
        secondary_version = _get_subexp(matches, "version")
        if secondary_version:
            name = name[: len(name) - len(secondary_version) - 1]
            version = secondary_version
    return ArchiveFileInfo(raw=raw, name=name, version=version)


def _get_subexp(matches: re.Match[str] | None, subexp_name: str) -> str:
    if matches:
        return matches.group(subexp_name) or ""

    return ""
