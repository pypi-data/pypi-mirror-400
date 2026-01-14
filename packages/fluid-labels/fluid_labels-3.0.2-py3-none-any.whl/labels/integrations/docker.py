import base64
import json
import logging
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from labels.model.sources import ImageContext, ImageMetadata, LayerData
from labels.model.syft_sbom import (
    SyftAnnotation,
    SyftArtifact,
    SyftLocation,
    SyftMetadata,
    SyftRelationship,
    SyftSBOM,
    SyftSource,
)
from labels.utils.exceptions import (
    DockerImageNotFoundError,
    InvalidImageReferenceError,
    SkopeoNotFoundError,
    SyftNotFoundError,
)
from labels.utils.file import extract_tar_file

LOGGER = logging.getLogger(__name__)

ADDITIONAL_CATALOGERS = [
    "dart-pubspec-lock-cataloger",
    "dart-pubspec-cataloger",
    "swift-package-manager-cataloger",
    "cocoapods-cataloger",
]


def _format_image_ref(image_ref: str, *, daemon: bool = False) -> str:
    image_ref_pattern = (
        r"^(?:(?P<host>[\w\.\-]+(?:\:\d+)?)/)?"
        r"(?P<namespace>(?:[\w\.\-]+(?:/[\w\.\-]+)*)?/)?"
        r"(?P<image>[\w\.\-]+)(?::(?P<tag>[\w\.\-]+))?(?:@"
        r"(?P<digest>sha256:[A-Fa-f0-9]{64}))?$"
    )
    prefix_to_use = "docker-daemon:" if daemon else "docker://"
    prefix_used: str | None = None
    prefixes = ["docker://", "docker-daemon:"]
    for prefix in prefixes:
        if image_ref.startswith(prefix):
            image_ref = image_ref.replace(prefix, "", 1)
            prefix_used = prefix
            break

    prefix_to_use = prefix_used or prefix_to_use

    if re.match(image_ref_pattern, image_ref):
        return f"{prefix_to_use}{image_ref}"

    raise InvalidImageReferenceError(image_ref)


def _get_skopeo_path() -> str:
    skopeo_path = shutil.which("skopeo")
    if not skopeo_path:
        raise SkopeoNotFoundError
    return skopeo_path


def _execute_command(command_args: list[str]) -> bool:
    with subprocess.Popen(  # noqa: S603
        command_args,
        shell=False,
        stdout=subprocess.PIPE,
    ) as proc:
        exit_code = proc.wait()
        return exit_code == 0


def _load_manifest(layers_dir: str) -> dict[str, Any]:
    path = Path(layers_dir, "manifest.json")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_config(config_digest: str, layers_dir: str) -> dict[str, Any]:
    path = Path(layers_dir, config_digest.replace("sha256:", ""))
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _extract_layer(layer: dict[str, Any], layers_dir: str, output_dir: str) -> None:
    layer_digest = layer["digest"].replace("sha256:", "")
    tar_path = Path(layers_dir, layer_digest)
    if tar_path.exists():
        dest = Path(output_dir, layer["digest"])
        dest.mkdir(parents=True, exist_ok=True)
        extract_tar_file(str(tar_path), str(dest))


def _build_copy_auth_args(
    *,
    unauthenticated_args: list[str],
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
) -> list[str]:
    if username and password:
        unauthenticated_args.extend(
            ["--src-username", username, "--src-password", password],
        )

    elif token:
        unauthenticated_args.extend(["--src-registry-token", token])

    elif aws_creds:
        unauthenticated_args.append(f"--src-creds={aws_creds}")

    return unauthenticated_args


def _build_inspect_auth_args(
    *,
    unauthenticated_args: list[str],
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
) -> list[str]:
    if username and password:
        unauthenticated_args.extend(["--username", username, "--password", password])

    elif token:
        unauthenticated_args.append(f"--registry-token={token}")

    elif aws_creds:
        unauthenticated_args.append(f"--creds={aws_creds}")

    return unauthenticated_args


def _custom_object_hook(json_object: dict[str, Any]) -> ImageMetadata | dict:
    if "Name" in json_object and "Digest" in json_object and "RepoTags" in json_object:
        layersdata = [
            LayerData(
                mimetype=layer_data["MIMEType"],
                digest=layer_data["Digest"],
                size=layer_data["Size"],
                annotations=layer_data.get("Annotations"),
            )
            for layer_data in json_object["LayersData"]
        ]
        return ImageMetadata(
            name=json_object["Name"],
            digest=json_object["Digest"],
            repotags=json_object["RepoTags"],
            created=json_object["Created"],
            dockerversion=json_object["DockerVersion"],
            labels=json_object["Labels"],
            architecture=json_object["Architecture"],
            os=json_object["Os"],
            layers=json_object["Layers"],
            layersdata=layersdata,
            env=json_object["Env"],
        )
    return json_object


def copy_image(  # noqa: PLR0913
    image_ref: str,
    dest_path: str,
    *,
    username: str | None = None,
    password: str | None = None,
    aws_creds: str | None = None,
    token: str | None = None,
    os_override: str | None = None,
    arch_override: str | None = None,
) -> bool:
    skopeo_path = _get_skopeo_path()

    formated_image_ref = _format_image_ref(image_ref)

    command_args = [
        skopeo_path,
        "copy",
        "--dest-decompress",
        "--insecure-policy",
        *build_override_args(os_override=os_override, arch_override=arch_override),
        formated_image_ref,
        f"dir:{dest_path}",
    ]

    authenticated_args = _build_copy_auth_args(
        unauthenticated_args=command_args,
        username=username,
        password=password,
        aws_creds=aws_creds,
        token=token,
    )

    return _execute_command(authenticated_args)


def extract_docker_image(  # noqa: PLR0913
    image: ImageMetadata,
    output_dir: str,
    *,
    username: str | None = None,
    password: str | None = None,
    os_override: str | None = None,
    arch_override: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> tuple[str, dict[str, Any]]:
    layers_dir_temp = tempfile.mkdtemp()

    formated_image_ref = _format_image_ref(image.image_ref, daemon=daemon)

    copy_image(
        image_ref=formated_image_ref or image.image_ref,
        dest_path=layers_dir_temp,
        username=username,
        password=password,
        os_override=os_override,
        arch_override=arch_override,
        token=token,
        aws_creds=aws_creds,
    )

    manifest = _load_manifest(layers_dir_temp)
    manifest["config_full"] = _load_config(manifest["config"]["digest"], layers_dir_temp)

    for layer in manifest["layers"]:
        _extract_layer(layer, layers_dir_temp, output_dir)

    return layers_dir_temp, manifest


def build_override_args(
    *,
    os_override: str | None = None,
    arch_override: str | None = None,
) -> list[str]:
    os_value = os_override if os_override is not None else "linux"
    override_args = []
    if os_value:
        override_args.append(f"--override-os={os_value}")
    if arch_override:
        override_args.append(f"--override-arch={arch_override}")
    return override_args


def get_docker_image(  # noqa: PLR0913
    image_ref: str,
    *,
    username: str | None = None,
    password: str | None = None,
    os_override: str | None = None,
    arch_override: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> ImageMetadata:
    skopeo_path = _get_skopeo_path()

    formated_image_ref = _format_image_ref(image_ref, daemon=daemon)

    command_args = [
        skopeo_path,
        "inspect",
        *build_override_args(os_override=os_override, arch_override=arch_override),
        formated_image_ref,
    ]
    authenticated_args = _build_inspect_auth_args(
        unauthenticated_args=command_args,
        username=username,
        password=password,
        aws_creds=aws_creds,
        token=token,
    )

    try:
        result = subprocess.run(  # noqa: S603
            authenticated_args,
            check=True,
            capture_output=True,
            text=True,
        )
        image_metadata: ImageMetadata = json.loads(
            result.stdout,
            object_hook=_custom_object_hook,
        )
        image_metadata = (
            image_metadata.model_copy(
                update={"image_ref": image_ref},
            )
            if image_metadata
            else image_metadata
        )
    except subprocess.CalledProcessError as error:
        raise DockerImageNotFoundError(image_ref, error.stderr.strip()) from error
    else:
        return image_metadata


def get_image_context(  # noqa: PLR0913
    *,
    image: ImageMetadata,
    username: str | None = None,
    password: str | None = None,
    os_override: str | None = None,
    arch_override: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> ImageContext:
    temp_dir = tempfile.mkdtemp()

    layers_dir, manifest = extract_docker_image(
        image,
        temp_dir,
        username=username,
        password=password,
        os_override=os_override,
        arch_override=arch_override,
        token=token,
        aws_creds=aws_creds,
        daemon=daemon,
    )

    return ImageContext(
        id=image.digest,
        name=image.name,
        publisher="",
        arch=image.architecture,
        size=str(sum(x.size for x in image.layersdata)),
        full_extraction_dir=temp_dir,
        layers_dir=layers_dir,
        manifest=manifest,
        image_ref=image.image_ref,
    )


def _get_syft_path() -> str:
    syft_path = shutil.which("syft")
    if not syft_path:
        raise SyftNotFoundError
    return syft_path


def _build_platform_arg(
    *,
    os_override: str | None = None,
    arch_override: str | None = None,
) -> list[str]:
    os_value = os_override if os_override else "linux"
    arch_override_value = arch_override if arch_override else "arm64"
    return ["--platform", f"{os_value}/{arch_override_value}"]


def _get_formatted_image(*, image_ref: str, daemon: bool = False) -> str:
    image_ref_pattern = (
        r"^(?:(?P<host>[\w\.\-]+(?:\:\d+)?)/)?"
        r"(?P<namespace>(?:[\w\.\-]+(?:/[\w\.\-]+)*)?/)?"
        r"(?P<image>[\w\.\-]+)(?::(?P<tag>[\w\.\-]+))?(?:@"
        r"(?P<digest>sha256:[A-Fa-f0-9]{64}))?$"
    )

    syft_prefix = "docker" if daemon else "registry"
    prefixes = {"registry": "docker://", "docker": "docker-daemon:"}
    for prefix, prefix_value in prefixes.items():
        if image_ref.startswith(prefix_value):
            image_ref = image_ref.replace(prefix_value, "", 1)
            syft_prefix = prefix
            break

    if re.match(image_ref_pattern, image_ref):
        return f"{syft_prefix}:{image_ref}"

    raise InvalidImageReferenceError(image_ref)


@contextmanager
def _syft_auth_env(
    *,
    image_ref: str | None = None,
    username: str | None = None,
    password: str | None = None,
    aws_creds: str | None = None,
    token: str | None = None,
) -> Iterator[dict[str, str]]:
    if username and password:
        LOGGER.info("Setting DOCKER_USERNAME and DOCKER_PASSWORD environment variables for Syft")
        yield {
            "SYFT_REGISTRY_AUTH_USERNAME": username,
            "SYFT_REGISTRY_AUTH_PASSWORD": password,
        }
        return

    if image_ref and (auth := token or aws_creds):
        config_dir = tempfile.mkdtemp(prefix=".syft")
        LOGGER.debug("Creating temporary Docker config dir at %s", config_dir)

        try:
            docker_config_path = Path(config_dir, "config.json")
            registry_url = image_ref.split("/", 1)[0]

            encoded_auth = base64.b64encode(auth.encode("utf-8")).decode("utf-8")
            docker_config = {
                "auths": {
                    registry_url: {
                        "auth": encoded_auth,
                    },
                }
            }

            with docker_config_path.open("w", encoding="utf-8") as f:
                json.dump(docker_config, f)
            yield {
                "DOCKER_CONFIG": config_dir,
            }
        finally:
            LOGGER.debug("Cleaning up temporary DOCKER_CONFIG directory: %s", config_dir)
            shutil.rmtree(config_dir, ignore_errors=True)

        return

    yield {}


def _get_metadata(metadata: dict[str, Any]) -> SyftMetadata:
    dependencies = (
        metadata.get("depends", [])
        if metadata.get("depends")
        else metadata.get("pullDependencies", [])
    )
    release = metadata.get("release", "") if isinstance(metadata.get("release"), str) else ""
    package = str(metadata.get("package")) if metadata.get("package") else "UNKNOWN"
    version = str(metadata.get("version")) if metadata.get("version") else "UNKNOWN"
    source = metadata.get("source", "") if isinstance(metadata.get("source"), str) else ""

    return SyftMetadata(
        package=package,
        version=version,
        provides=metadata.get("provides", []),
        dependencies=dependencies,
        maintainer=metadata.get("maintainer", ""),
        origin_package=metadata.get("originPackage", ""),
        architecture=metadata.get("architecture", ""),
        source=source,
        source_version=metadata.get("sourceVersion", ""),
        pre_dependencies=metadata.get("preDepends", []),
        name=metadata.get("name", ""),
        epoch=metadata.get("epoch"),
        release=release,
        source_rpm=metadata.get("sourceRpm", ""),
        base_package=metadata.get("basepackage", ""),
        packager=metadata.get("packager", ""),
        requires_dist=metadata.get("requiresDist", []),
        provides_extra=metadata.get("providesExtra", []),
        manifest=metadata.get("manifest", {}),
        pom_properties=metadata.get("pomProperties", {}),
        pom_project=metadata.get("pomProject", {}),
    )


def _get_syft_source(source: dict[str, Any]) -> SyftSource:
    namespace = str(source.get("metadata", {}).get("userInput"))
    version = ""

    if (digests := source.get("metadata", {}).get("repoDigests")) and (first_digest := digests[0]):
        version = str(first_digest).split("@", 1)[1]

    return SyftSource(
        namespace=namespace,
        version=version,
    )


def _get_syft_relationships(relationships: list[dict[str, Any]]) -> list[SyftRelationship]:
    return [
        SyftRelationship(
            parent=parent,
            child=child,
            type=type_,
        )
        for relationship in relationships
        if (parent := relationship.get("parent"))
        and (child := relationship.get("child"))
        and (type_ := relationship.get("type"))
    ]


def _get_syft_artifacts(artifacts: list[dict[str, Any]]) -> list[SyftArtifact]:
    return [
        SyftArtifact(
            id_=str(artifact.get("id")),
            name=str(artifact.get("name")),
            version=str(artifact.get("version")),
            type=str(artifact.get("type")),
            locations=[
                SyftLocation(
                    path=location.get("path"),
                    access_path=location.get("path"),
                    layer_id=location.get("layerID"),
                    annotations=(
                        SyftAnnotation(
                            evidence=location.get("annotations", {}).get("evidence", ""),
                        )
                        if location.get("annotations")
                        else None
                    ),
                )
                for location in artifact.get("locations", [])
            ],
            p_url=str(artifact.get("purl")),
            metadata=_get_metadata(artifact.get("metadata", {})),
            found_by=str(artifact.get("foundBy")),
            language=str(artifact.get("language")),
        )
        for artifact in artifacts
        if artifact.get("id")
        and artifact.get("name")
        and artifact.get("version")
        and artifact.get("version") != "UNKNOWN"
    ]


def _get_syft_object_hook(json_object: dict[str, Any]) -> SyftSBOM | dict:
    if sbom_artifacts := json_object.get("artifacts"):
        sbom_source = json_object.get("source", {})
        sbom_relationships = json_object.get("artifactRelationships", [])
        return SyftSBOM(
            artifacts=_get_syft_artifacts(sbom_artifacts),
            source=_get_syft_source(sbom_source),
            relationships=_get_syft_relationships(sbom_relationships),
        )

    return json_object


def get_docker_sbom(  # noqa: PLR0913
    image_ref: str,
    *,
    username: str | None = None,
    password: str | None = None,
    os_override: str | None = None,
    arch_override: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> SyftSBOM:
    syft_path = _get_syft_path()
    formatted_img = _get_formatted_image(image_ref=image_ref, daemon=daemon)

    LOGGER.info("Retrieving SBOM for image: %s", image_ref)
    LOGGER.info("Retrieving SBOM for image: %s", formatted_img)

    command_args = [
        syft_path,
        "scan",
        formatted_img,
        *_build_platform_arg(os_override=os_override, arch_override=arch_override),
        "--select-catalogers",
        ",".join("+" + cataloger for cataloger in ADDITIONAL_CATALOGERS),
        "-o",
        "json",
    ]

    with _syft_auth_env(
        image_ref=image_ref,
        username=username,
        password=password,
        aws_creds=aws_creds,
        token=token,
    ) as syft_envs:
        try:
            result = subprocess.run(  # noqa: S603
                command_args,
                check=True,
                capture_output=True,
                text=True,
                env=syft_envs,
            )

            sbom_data: SyftSBOM = json.loads(
                result.stdout,
                object_hook=_get_syft_object_hook,
            )
        except subprocess.CalledProcessError as error:
            raise DockerImageNotFoundError(image_ref, error.stderr.strip()) from error

    return sbom_data
