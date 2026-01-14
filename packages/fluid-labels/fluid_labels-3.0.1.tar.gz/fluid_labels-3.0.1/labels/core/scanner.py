import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

from labels.advisories.images import DATABASE as IMAGES_DATABASE
from labels.advisories.roots import DATABASE as ROOTS_DATABASE
from labels.advisories.utils import DatabasesToDownload
from labels.config.bugsnag import initialize_bugsnag
from labels.config.logger import configure_logger, modify_logger_level
from labels.config.utils import guess_environment
from labels.core.merge_packages import merge_packages
from labels.core.source_dispatcher import resolve_sbom_source, resolve_sbom_source_v2
from labels.core.top_parents import calculate_top_parents_for_packages
from labels.domain.cloudwatch import process_sbom_metrics
from labels.domain.tracks import send_event_to_tracks
from labels.enrichers.dispatcher import complete_package, complete_package_advisories_only
from labels.model.core import SbomConfig, SourceType
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.syft_sbom import SyftSBOM
from labels.output.dispatcher import dispatch_sbom_output
from labels.parsers.operations.package_operation import (
    package_operations_factory,
    package_operations_factory_v2,
)
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.utils.tracks import count_vulns_by_severity

LOGGER = logging.getLogger(__name__)


def configure_logging(sbom_config: SbomConfig) -> None:
    configure_logger(log_to_remote=True)
    initialize_bugsnag()

    if sbom_config.debug:
        modify_logger_level()


def initialize_advisories_databases(dbs_to_download: DatabasesToDownload) -> None:
    LOGGER.info("📦 Initializing advisories databases")
    if dbs_to_download.roots_db:
        ROOTS_DATABASE.initialize()
    if dbs_to_download.images_db:
        IMAGES_DATABASE.initialize()


def gather_packages_and_relationships(
    resolver: Directory | ContainerImage | SyftSBOM,
    max_workers: int = 32,
    *,
    include_package_metadata: bool = True,
) -> tuple[list[Package], list[Relationship]]:
    LOGGER.info("📦 Gathering packages and relationships")
    packages, relationships = (
        package_operations_factory(resolver)
        if isinstance(
            resolver,
            (Directory, ContainerImage),
        )
        else package_operations_factory_v2(resolver)
    )
    merged_packages, described_by_relationships, dbs_to_download = merge_packages(packages)
    LOGGER.info("PACKAGES: %d - MERGED: %d", len(packages), len(merged_packages))
    LOGGER.info(
        "RELATIONSHIPS: %d - DESCRIBED BY: %d",
        len(relationships),
        len(described_by_relationships),
    )

    all_relationships = relationships + described_by_relationships

    initialize_advisories_databases(dbs_to_download)

    worker_count = min(
        max_workers,
        (os.cpu_count() or 1) * 5 if os.cpu_count() is not None else max_workers,
    )
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        LOGGER.info("📦 Gathering additional package information")
        if include_package_metadata:
            packages = list(filter(None, executor.map(complete_package, merged_packages)))
        else:
            packages = list(executor.map(complete_package_advisories_only, merged_packages))

    LOGGER.info("📦 Calculating top parents")
    packages = calculate_top_parents_for_packages(packages, all_relationships)

    LOGGER.info("✅ Found %d packages", len(packages))

    return packages, all_relationships


def execute_labels_scan(sbom_config: SbomConfig) -> None:
    try:
        configure_logging(sbom_config)
        LOGGER.info("🚀 Starting Labels SBOM scan")

        if sbom_config.feature_preview:
            LOGGER.warning("🔬 Executing with feature preview enabled")

        main_sbom_resolver = (
            resolve_sbom_source(sbom_config)
            if (sbom_config.source_type == SourceType.DIRECTORY)
            or (not sbom_config.feature_preview)
            else resolve_sbom_source_v2(sbom_config)
        )

        LOGGER.info(
            "📦 Generating SBOM from %s: %s", sbom_config.source_type.value, sbom_config.source
        )
        start_time = time.perf_counter()
        packages, relationships = gather_packages_and_relationships(
            main_sbom_resolver,
            include_package_metadata=sbom_config.include_package_metadata,
        )
        end_time = time.perf_counter() - start_time
        process_sbom_metrics(sbom_config.execution_id, end_time, sbom_config.source_type)

        LOGGER.info("📦 Preparing %s report", sbom_config.output_format.value)
        dispatch_sbom_output(
            packages=packages,
            relationships=relationships,
            config=sbom_config,
            resolver=main_sbom_resolver,
        )
        send_event_to_tracks(
            sbom_config=sbom_config,
            packages_amount=len(packages),
            relationships_amount=len(relationships),
            vulns_summary=count_vulns_by_severity(packages),
        )
    except Exception:
        if guess_environment() == "production":
            LOGGER.exception(
                "Error executing labels scan. Output SBOM was not generated.",
                extra={"execution_id": sbom_config.execution_id},
            )
            return
        raise
