from collections.abc import Callable

from labels.model.package import Package, PackageType
from labels.model.syft_sbom import SyftArtifact
from labels.parsers.builder.alpine.builder_apk import builder as builder_apk_pkg
from labels.parsers.builder.arch.builder_alpm import builder as builder_alpm_pkg
from labels.parsers.builder.debian.builder_deb import builder as builder_deb_pkg
from labels.parsers.builder.generic_builder import builder as generic_builder
from labels.parsers.builder.java.builder_java import builder as builder_java_pkg
from labels.parsers.builder.python.builder_python import builder as builder_python_pkg
from labels.parsers.builder.redhat.builder_rpm import builder as builder_rpmdb_pkg

BUILDERS: dict[PackageType, Callable[[SyftArtifact, PackageType], Package | None]] = {
    PackageType.DebPkg: builder_deb_pkg,
    PackageType.ApkPkg: builder_apk_pkg,
    PackageType.AlpmPkg: builder_alpm_pkg,
    PackageType.RpmPkg: builder_rpmdb_pkg,
    PackageType.PythonPkg: builder_python_pkg,
    PackageType.JavaPkg: builder_java_pkg,
    PackageType.NpmPkg: generic_builder,
    PackageType.DotnetPkg: generic_builder,
    PackageType.GemPkg: generic_builder,
    PackageType.PhpComposerPkg: generic_builder,
    PackageType.PhpPearPkg: generic_builder,
    PackageType.DartPubPkg: generic_builder,
    PackageType.SwiftPkg: generic_builder,
}


def build_package(
    artifact: SyftArtifact,
    package_type: PackageType,
) -> Package | None:
    if builder := BUILDERS.get(package_type):
        return builder(artifact, package_type)
    return None
