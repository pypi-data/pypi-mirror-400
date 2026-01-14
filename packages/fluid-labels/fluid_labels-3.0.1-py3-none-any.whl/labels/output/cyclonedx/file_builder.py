from collections import defaultdict

from cyclonedx.model.bom import Bom
from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.component import Component, ComponentType
from cyclonedx.model.tool import Tool
from packageurl import PackageURL

from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.output.cyclonedx.complete_file import (
    add_authors,
    add_component_properties,
    add_integrity,
    add_vulnerabilities,
)


def pkg_to_component(package: Package) -> Component:
    health_metadata = package.health_metadata
    authors = add_authors(health_metadata) if health_metadata else []
    integrity = add_integrity(health_metadata) if health_metadata else []
    properties = add_component_properties(package)

    return Component(
        type=ComponentType.LIBRARY,
        name=package.name,
        version=package.version,
        authors=authors,
        bom_ref=f"{package.name}@{package.version}",
        purl=PackageURL.from_string(package.p_url),
        properties=properties,
        hashes=integrity,
    )


def create_bom(namespace: str, version: str | None) -> Bom:
    bom = Bom()
    bom.metadata.component = Component(
        name=namespace,
        type=ComponentType.APPLICATION,
        bom_ref=BomRef(f"{namespace}@{version}" if version else namespace),
        version=version,
    )
    bom.metadata.tools.tools.add(Tool(vendor="Fluid Attacks", name="Fluid-Labels"))
    return bom


def add_components_to_bom(bom: Bom, component_cache: dict[str, Component]) -> None:
    for component in component_cache.values():
        bom.components.add(component)


def add_advisories_to_bom(
    bom: Bom,
    packages: list[Package],
) -> None:
    for package in packages:
        if package.advisories:
            vulnerabilities = add_vulnerabilities(package)
            for vulnerability in vulnerabilities:
                bom.vulnerabilities.add(vulnerability)


def add_relationships_to_bom(
    bom: Bom,
    relationships: list[Relationship],
    component_cache: dict[str, Component],
) -> None:
    dependency_map: dict[Component, list[Component]] = defaultdict(list)
    for relationship in relationships:
        if relationship.type.value == "dependency-of":
            # Extract base IDs (remove @location_id suffix if present)
            to_id = relationship.to_.split("@")[0] if "@" in relationship.to_ else relationship.to_
            from_id = (
                relationship.from_.split("@")[0]
                if "@" in relationship.from_
                else relationship.from_
            )

            to_pkg = component_cache.get(to_id)
            from_pkg = component_cache.get(from_id)
            if to_pkg and from_pkg:
                dependency_map[to_pkg].append(from_pkg)

    for ref, depends_on_list in dependency_map.items():
        bom.register_dependency(ref, depends_on_list)

    if bom.metadata.component:
        bom.register_dependency(bom.metadata.component, component_cache.values())
