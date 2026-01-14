from typing import TypedDict

from labels.enrichers.api_interface import make_get


class OriginInfo(TypedDict):
    VCS: str
    URL: str
    Ref: str
    Hash: str


class VersionInfo(TypedDict):
    Version: str
    Time: str
    Origin: OriginInfo | None


def fetch_latest_version_info(module_path: str) -> VersionInfo | None:
    # https://go.dev/ref/mod#version-queries
    base_url = "https://proxy.golang.org"
    url = f"{base_url}/{module_path.lower()}/@latest"

    response: VersionInfo | None = make_get(url)
    return response
