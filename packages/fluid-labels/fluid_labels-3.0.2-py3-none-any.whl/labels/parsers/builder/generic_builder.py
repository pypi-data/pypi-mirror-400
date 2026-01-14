from pydantic import ValidationError

from labels.model.package import Package, PackageType
from labels.model.syft_sbom import SyftArtifact
from labels.parsers.builder.utils import get_language, get_locations
from labels.parsers.cataloger.utils import log_malformed_package_warning


def builder(
    artifact: SyftArtifact,
    package_type: PackageType,
) -> Package | None:
    pkg_language = get_language(artifact.language)
    pkg_locations = get_locations(artifact.locations)
    pkg_name = artifact.name.lower()

    try:
        package = Package(
            name=pkg_name,
            version=artifact.version,
            p_url=artifact.p_url,
            locations=pkg_locations,
            type=package_type,
            found_by=artifact.found_by,
            language=pkg_language,
            syft_id=artifact.id_,
        )
    except ValidationError as ex:  # pragma: no cover
        log_malformed_package_warning(pkg_locations[0], ex)
        return None

    return package
