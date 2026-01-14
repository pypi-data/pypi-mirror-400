import hashlib
from enum import StrEnum
from io import TextIOWrapper
from typing import TextIO

from pydantic import BaseModel, ConfigDict


class DependencyType(StrEnum):
    DIRECT = "DIRECT"
    TRANSITIVE = "TRANSITIVE"
    ROOT = "ROOT"
    UNDETERMINABLE = "UNDETERMINABLE"


class Scope(StrEnum):
    BUILD = "BUILD"
    RUN = "RUN"
    UNDETERMINABLE = "UNDETERMINABLE"


class Coordinates(BaseModel):
    real_path: str
    file_system_id: str | None = None
    line: int | None = None


class DependencyChain(BaseModel):
    depth: int
    chain: list[str]


class Location(BaseModel):
    scope: Scope = Scope.UNDETERMINABLE
    coordinates: Coordinates | None = None
    access_path: str | None = None
    dependency_type: DependencyType = DependencyType.UNDETERMINABLE
    reachable_cves: list[str] = []
    top_parents: list[str] | None = None
    dependency_chains: list[DependencyChain] | None = None

    def path(self) -> str:
        path = self.access_path or (self.coordinates.real_path if self.coordinates else None)
        if not path:
            error_msg = "Both access_path and coordinates.real_path are empty"
            raise ValueError(error_msg)
        return path

    def location_id(self) -> str:
        path = self.path()
        line = self.coordinates.line if self.coordinates else 0
        location_str = f"{path}:{line}"
        return hashlib.sha256(location_str.encode()).hexdigest()[:16]

    def output_dependency_type(self) -> DependencyType:
        """Return the appropriate dependency_type for public SBOM output.

        ROOT is an internal type used for calculations like top_parents.
        In the output it is represented as DIRECT to avoid exposing implementation details.
        """
        return (
            DependencyType.DIRECT
            if self.dependency_type == DependencyType.ROOT
            else self.dependency_type
        )


class LocationReadCloser(BaseModel):
    location: Location
    read_closer: TextIO | TextIOWrapper
    model_config = ConfigDict(arbitrary_types_allowed=True)
