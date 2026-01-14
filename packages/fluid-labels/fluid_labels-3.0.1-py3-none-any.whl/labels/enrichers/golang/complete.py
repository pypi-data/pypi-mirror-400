from datetime import datetime

import pydantic

from labels.enrichers.golang.get import fetch_latest_version_info
from labels.model.metadata import HealthMetadata
from labels.model.package import Package


class GolangModuleEntry(pydantic.BaseModel):
    h1_digest: str


def complete_package(package: Package) -> Package:
    latest = fetch_latest_version_info(package.name)
    if not latest:
        return package
    package.health_metadata = HealthMetadata(
        latest_version=latest["Version"],
        latest_version_created_at=datetime.fromisoformat(latest["Time"]),
        artifact=None,
    )
    return package
