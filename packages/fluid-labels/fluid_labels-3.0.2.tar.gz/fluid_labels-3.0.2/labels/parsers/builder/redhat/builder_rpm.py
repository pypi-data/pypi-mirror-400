from pydantic import ValidationError

from labels.model.ecosystem_data.redhat import RpmDBEntry
from labels.model.package import Package, PackageType
from labels.model.syft_sbom import SyftArtifact, SyftMetadata
from labels.parsers.builder.utils import get_language, get_locations
from labels.parsers.cataloger.utils import log_malformed_package_warning


def _get_rpmpkg_entry(metadata: SyftMetadata) -> RpmDBEntry:
    return RpmDBEntry(
        name=metadata.name,
        version=metadata.version,
        epoch=metadata.epoch,
        arch=metadata.architecture,
        release=metadata.release,
        source_rpm=metadata.source_rpm,
    )


def builder(
    artifact: SyftArtifact,
    package_type: PackageType,
) -> Package | None:
    pkg_language = get_language(artifact.language)
    pkg_locations = get_locations(artifact.locations)

    metadata = artifact.metadata
    pkg_ecosystem_data = _get_rpmpkg_entry(metadata)

    try:
        package = Package(
            name=artifact.name,
            version=artifact.version,
            p_url=artifact.p_url,
            locations=pkg_locations,
            type=package_type,
            ecosystem_data=pkg_ecosystem_data,
            found_by=artifact.found_by,
            language=pkg_language,
            syft_id=artifact.id_,
        )
    except ValidationError as ex:  # pragma: no cover
        log_malformed_package_warning(pkg_locations[0], ex)
        return None

    return package
