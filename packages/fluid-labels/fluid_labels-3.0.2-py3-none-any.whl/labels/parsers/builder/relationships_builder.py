from labels.model.ecosystem_data.alpine import ApkDBEntry
from labels.model.ecosystem_data.debian import DpkgDBEntry
from labels.model.package import Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.syft_sbom import SyftSBOM

VERSION_SPECIFIERS = "[(<>="
CHOICE_SEPARATOR = "|"


def _strip_version_specifier(item: str) -> str:
    index = next((i for i, char in enumerate(item) if char in VERSION_SPECIFIERS), None)

    if not index:
        return item.strip()

    return item[:index].strip()


def _split_package_choices(value: str) -> list[str]:
    fields = value.split(CHOICE_SEPARATOR)
    return [_strip_version_specifier(field) for field in fields if field.strip()]


def _build_package_lookup(packages: list[Package]) -> dict[str, list[Package]]:
    lookup: dict[str, list[Package]] = {}

    for package in packages:
        if not isinstance(package.ecosystem_data, (DpkgDBEntry, ApkDBEntry)):
            continue

        if package.name:
            lookup.setdefault(package.name, []).append(package)

        ecosystem_data = package.ecosystem_data
        for provides in ecosystem_data.provides or []:
            key = _strip_version_specifier(provides)
            lookup.setdefault(key, []).append(package)

    return lookup


def _get_os_package_relationships(packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []
    lookup_table = _build_package_lookup(packages)

    for package_to in packages:
        if not isinstance(package_to.ecosystem_data, (DpkgDBEntry, ApkDBEntry)):
            continue

        ecosystem_data = package_to.ecosystem_data

        all_dependencies: list[str] = list(ecosystem_data.dependencies or [])

        if isinstance(ecosystem_data, DpkgDBEntry) and ecosystem_data.pre_dependencies:
            all_dependencies.extend(ecosystem_data.pre_dependencies)

        for dep_specifier in all_dependencies:
            dependency_names = _split_package_choices(dep_specifier)

            for dependency in dependency_names:
                relationships.extend(
                    [
                        Relationship(
                            from_=package_from.id_,
                            to_=package_to.id_,
                            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                        )
                        for package_from in lookup_table.get(dependency, [])
                        if package_from.id_ != package_to.id_
                    ]
                )
    return relationships


def get_relationships(docker_sbom: SyftSBOM, packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []
    grouped_packages: dict[str, list[Package]] = {}

    for package in packages:
        if package.type in [PackageType.ApkPkg, PackageType.DebPkg]:
            grouped_packages.setdefault("os", []).append(package)

        if package.type in [
            PackageType.DotnetPkg,
            PackageType.PhpComposerPkg,
            PackageType.SwiftPkg,
        ]:
            grouped_packages.setdefault("pkg_manager", []).append(package)

    if os_packages := grouped_packages.get("os"):
        relationships.extend(_get_os_package_relationships(os_packages))

    if pkg_manager_packages := grouped_packages.get("pkg_manager"):
        pkg_map = {pkg.syft_id: pkg for pkg in pkg_manager_packages}

        for relationship in docker_sbom.relationships:
            if relationship.type != RelationshipType.DEPENDENCY_OF_RELATIONSHIP.value:
                continue

            from_pkg = pkg_map.get(relationship.parent)
            to_pkg = pkg_map.get(relationship.child)

            if from_pkg and to_pkg and from_pkg.id_ != to_pkg.id_:
                relationships.append(
                    Relationship(
                        from_=from_pkg.id_,
                        to_=to_pkg.id_,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    )
                )

    return relationships
