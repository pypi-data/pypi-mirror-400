from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.ecosystem_data.debian import DpkgDBEntry
from labels.model.file import Location
from labels.model.package import Language, Package, PackageType
from labels.model.release import Release
from labels.parsers.cataloger.utils import (
    get_enriched_location,
    log_malformed_package_warning,
    purl_qualifiers,
)


def new_dpkg_package(
    entry: DpkgDBEntry,
    db_location: Location,
    release: Release | None = None,
) -> Package | None:
    name = entry.package
    version = entry.version

    if not name or not version:
        return None

    new_location = get_enriched_location(db_location)
    p_url = get_debian_package_url(entry, release)

    try:
        package = Package(
            name=name,
            version=version,
            p_url=p_url,
            locations=[new_location],
            type=PackageType.DebPkg,
            ecosystem_data=entry,
            found_by=None,
            language=Language.UNKNOWN_LANGUAGE,
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None

    return package


def get_debian_package_url(pkg: DpkgDBEntry, distro: Release | None = None) -> str:
    qualifiers = {"arch": pkg.architecture}
    if distro and (distro.id_ == "debian" or "debian" in (distro.id_like or [])):
        if distro.version_id:
            qualifiers["distro_version_id"] = distro.version_id
        qualifiers["distro_id"] = distro.id_
    if pkg.source:
        qualifiers["upstream"] = (
            f"{pkg.source}@{pkg.source_version}" if pkg.source_version else pkg.source
        )

    return PackageURL(  # type: ignore[misc]
        type="deb",
        namespace=distro.id_ if distro and distro.id_ else "",
        name=pkg.package,
        version=pkg.version,
        qualifiers=purl_qualifiers(qualifiers, distro),
    ).to_string()
