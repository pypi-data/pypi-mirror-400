import logging
import multiprocessing
import traceback

import reactivex
from reactivex import Observable
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

from labels.model.package import Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.model.syft_sbom import SyftSBOM
from labels.parsers.builder.builder import build_package
from labels.parsers.builder.relationships_builder import get_relationships
from labels.parsers.operations.cataloger import execute_parsers
from labels.parsers.operations.generator import gen_location_tasks
from labels.parsers.operations.handler import handle_parser
from labels.parsers.operations.utils import handle_relationships, identify_release

LOGGER = logging.getLogger(__name__)


def log_and_continue(e: Exception, file_item: str) -> Observable[None]:
    LOGGER.error(
        "Error found while resolving packages of %s: %s: %s",
        file_item,
        str(e),
        traceback.format_exc(),
    )
    return reactivex.empty()


def process_file_item(
    file_item: str,
    resolver: Resolver,
    pool_scheduler: ThreadPoolScheduler,
) -> Observable[tuple[list[Package], list[Relationship]]]:
    return reactivex.just(file_item).pipe(
        handle_parser(scheduler=pool_scheduler),
        gen_location_tasks(resolver),
        execute_parsers(resolver, Environment(linux_release=identify_release(resolver))),
        ops.catch(lambda e, _: log_and_continue(e, file_item)),
    )


def _get_package_type(package_type: str) -> PackageType:
    try:
        return PackageType(package_type)
    except ValueError:
        return PackageType.UnknownPkg


def package_operations_factory_v2(
    docker_sbom: SyftSBOM,
) -> tuple[list[Package], list[Relationship]]:
    LOGGER.info("📦 Gathering packages and relationships (v2)")

    packages: list[Package] = []

    for artifact_pkg in docker_sbom.artifacts:
        pkg_type = _get_package_type(artifact_pkg.type)

        package = build_package(
            artifact=artifact_pkg,
            package_type=pkg_type,
        )

        if package:
            packages.append(package)

    relations: list[Relationship] = get_relationships(docker_sbom, packages)

    return packages, relations


def package_operations_factory(
    resolver: Resolver,
) -> tuple[list[Package], list[Relationship]]:
    observer: Observable[str] = reactivex.from_iterable(resolver.walk_file())
    result_packages: list[Package] = []
    result_relations: list[Relationship] = []
    completed_event = multiprocessing.Event()
    errors = []

    def on_completed() -> None:
        completed_event.set()

    def on_error(error: Exception) -> None:
        errors.append(error)
        on_completed()

    def on_next(value: tuple[list[Package], list[Relationship]]) -> None:
        packages, relations = value
        result_packages.extend(packages)
        result_relations.extend(relations)

    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    final_obs: Observable[tuple[list[Package], list[Relationship]]] = observer.pipe(
        ops.map(
            lambda file_item: process_file_item(file_item, resolver, pool_scheduler),  # type: ignore[arg-type]
        ),
        ops.merge(max_concurrent=optimal_thread_count),
    )
    final_obs.subscribe(on_next=on_next, on_error=on_error, on_completed=on_completed)

    completed_event.wait()
    result_relations.extend(handle_relationships(result_packages))

    return result_packages, result_relations
