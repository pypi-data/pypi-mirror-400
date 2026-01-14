from typing import Any

from pydantic import BaseModel

from labels.model.constraints import NonEmptyStr


class SyftAnnotation(BaseModel):  # pragma: no cover
    evidence: str


class SyftLocation(BaseModel):  # pragma: no cover
    path: NonEmptyStr
    access_path: NonEmptyStr
    layer_id: NonEmptyStr
    annotations: SyftAnnotation | None = None


class SyftProject(BaseModel):  # pragma: no cover
    group_id: NonEmptyStr | None = None
    artifact_id: NonEmptyStr | None = None
    version: NonEmptyStr | None = None
    name: NonEmptyStr | None = None
    parent: dict[NonEmptyStr, NonEmptyStr] | None = None


class SyftMetadata(BaseModel):  # type: ignore[explicit-any]  # pragma: no cover
    package: NonEmptyStr
    version: NonEmptyStr
    provides: list[NonEmptyStr] = []
    dependencies: list[NonEmptyStr] = []
    maintainer: str = ""
    origin_package: str = ""
    architecture: str = ""
    source: str = ""
    source_version: str = ""
    pre_dependencies: list[NonEmptyStr] = []
    name: str = ""
    epoch: int | None = None
    arch: str = ""
    release: str = ""
    source_rpm: str = ""
    base_package: str = ""
    packager: str = ""
    requires_dist: list[NonEmptyStr] = []
    provides_extra: list[NonEmptyStr] = []
    manifest: dict[NonEmptyStr, Any] = {}  # type: ignore[explicit-any]
    pom_properties: dict[NonEmptyStr, str] = {}
    pom_project: dict[NonEmptyStr, Any] = {}  # type: ignore[explicit-any]


class SyftArtifact(BaseModel):  # pragma: no cover
    id_: str
    name: str
    version: str
    type: str
    locations: list[SyftLocation]
    metadata: SyftMetadata
    p_url: str
    found_by: str
    language: str


class SyftSource(BaseModel):  # pragma: no cover
    namespace: NonEmptyStr
    version: str


class SyftRelationship(BaseModel):  # pragma: no cover
    parent: NonEmptyStr
    child: NonEmptyStr
    type: NonEmptyStr


class SyftSBOM(BaseModel):  # pragma: no cover
    source: SyftSource
    artifacts: list[SyftArtifact]
    relationships: list[SyftRelationship]
