import logging
from typing import Optional

from pyckagist.api.source import PackageSource
from pyckagist.model.platform import PackagePlatform
from pyckagist.model.remote import RemotePackageDefinition, RemotePackage
from pyckagist.model.version import PackageVersion
from pyckagist.registry.source import PackageSourceRegistry


class RemoteManager:
    def __init__(self, source_registry: PackageSourceRegistry):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._source_registry: PackageSourceRegistry = source_registry

    def _lookup_source(self, source_name: str) -> PackageSource:
        source: Optional[PackageSource] = self._source_registry.find_by_key(source_name)
        if source is None:
            raise RuntimeError(f"Source {source_name} not found")

        return source

    def lookup_package_definitions(
        self, package_name: str
    ) -> list[RemotePackageDefinition]:
        remote_packages = []

        for source_name in self._source_registry.get_keys():
            source = self._source_registry.find_by_key(source_name)
            if source is None:
                continue
            if package_name not in source.package_list():
                continue

            remote_packages.append(RemotePackageDefinition(package_name, source.name()))

            self._logger.debug(f"Found package {package_name} in source {source}")

        return remote_packages

    def lookup_package_version(
        self, package: RemotePackageDefinition, package_version: str
    ) -> str:
        if package_version == "latest":
            self._logger.debug(f"Searching for latest version of package {package}")

            source = self._lookup_source(package.source())
            return source.latest_package_version(package.name())

        if package_version == "stable":
            self._logger.debug(f"Searching for stable version of package {package}")

            source = self._lookup_source(package.source())
            return source.stable_package_version(package.name())

        return package_version

    def lookup_remote_package(
        self, package_definition: RemotePackageDefinition, package_version: str
    ) -> Optional[RemotePackage]:
        package_source = self._lookup_source(package_definition.source())
        package_version = self.lookup_package_version(
            package_definition, package_version
        )

        if not package_source.has_package_version(
            package_definition.name(), package_version
        ):
            self._logger.warning(f"Package {package_definition} not found")
            return None

        package_platforms = package_source.package_platforms(
            package_definition.name(), package_version
        )

        return RemotePackage(package_definition, package_version, package_platforms)

    def find_compatible_packages(
        self, package_name: str, package_version: str, platform: PackagePlatform
    ) -> list[RemotePackage]:
        compatible = []
        incompatible = []

        definitions = self.lookup_package_definitions(package_name)

        for package_definition in definitions:
            package = self.lookup_remote_package(package_definition, package_version)
            if package is None:
                continue

            if platform not in package.supported_platforms():
                self._logger.debug(
                    f"Package {package} was found but it is not compatible with the current platform {platform}"
                )
                incompatible.append(package)
                continue

            compatible.append(package)

        if len(compatible) == 0 and len(incompatible) > 0:
            version_names = list(map(lambda x: str(x), incompatible))
            self._logger.warning(
                f"No compatible package versions found for the current platform {platform}"
            )
            self._logger.warning(f"Incompatible package versions: {version_names}")

        comparable_versions = list(
            map(lambda x: PackageVersion.parse(x.version()), compatible)
        )
        return sorted(
            compatible, key=lambda x: comparable_versions[compatible.index(x)]
        )

    def package_executable(
        self, package: RemotePackage, platform: PackagePlatform
    ) -> bytes:
        source = self._lookup_source(package.definition().source())

        return source.package_executable(package.name(), package.version(), platform)
