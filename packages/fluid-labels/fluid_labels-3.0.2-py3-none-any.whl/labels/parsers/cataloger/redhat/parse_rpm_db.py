from labels.model.file import Location, LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.redhat.package_builder import new_redhat_package
from labels.parsers.cataloger.redhat.rpmdb.dispatcher import RpmDB, open_db


def parse_rpm_db(
    _resolver: Resolver,
    environment: Environment,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    if not reader.location.coordinates:
        return [], []

    database = open_db(reader.location.coordinates.real_path)
    if not database:
        return [], []

    packages = _collect_packages(database, reader.location, environment)

    return packages, []


def _collect_packages(
    database: RpmDB, location: Location, environment: Environment
) -> list[Package]:
    packages: list[Package] = []

    for entry in database.list_packages():
        package = new_redhat_package(entry=entry, env=environment, location=location)
        if package is not None:
            packages.append(package)

    return packages
