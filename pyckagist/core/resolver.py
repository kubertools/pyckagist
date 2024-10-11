import logging
from typing import Optional

from pyckagist.core.remote import RemoteManager
from pyckagist.model.package import PackageDefinition, Package, ExecutablePackage
from pyckagist.model.platform import PackagePlatform
from pyckagist.model.remote import RemotePackage
from pyckagist.model.version import PackageVersion
from pyckagist.storage.manager import PackageLifecycleManager


class PackageResolver:
    def __init__(
        self,
        package_platform: PackagePlatform,
        package_lifecycle_manager: PackageLifecycleManager,
        remote_manager: Optional[RemoteManager] = None,
    ):
        self._logger = logging.getLogger(self.__class__.__name__)

        self._package_platform = package_platform
        self._package_lifecycle_manager = package_lifecycle_manager

        self._remote_manager = remote_manager

        if remote_manager is None:
            self._logger.info(
                "Remote manager is not provided, only local packages will be available"
            )

    def _list_local_packages(self, package_name: str) -> list[ExecutablePackage]:
        packages = []

        for package in self._package_lifecycle_manager.list():
            if package.definition().name() == package_name:
                packages.append(package)

        return packages

    def resolve_package_version(self, package_name: str, package_version: str) -> str:
        if package_version != "latest" and package_version != "stable":
            return package_version

        if self._remote_manager is not None:
            remote_packages = self._remote_manager.find_compatible_packages(
                package_name, package_version, self._package_platform
            )
            if len(remote_packages) != 0:
                return remote_packages[0].version()

        packages = self._list_local_packages(package_name)
        if len(packages) == 0:
            raise RuntimeError(f"No package versions found for {package_name}")

        comparable_versions = list(
            map(lambda x: PackageVersion.parse(x.definition().version()), packages)
        )
        packages = sorted(
            packages, key=lambda x: comparable_versions[packages.index(x)]
        )
        return packages[-1].definition().version()

    def resolve_package(self, package: Package) -> ExecutablePackage:
        if self._remote_manager is None:
            raise RuntimeError(
                f"Package {package} is not present locally and remote manager is not available"
            )

        package_version: str = self.resolve_package_version(
            package.name(), package.version()
        )
        compatible_packages: list[RemotePackage] = (
            self._remote_manager.find_compatible_packages(
                package.name(), package_version, self._package_platform
            )
        )

        if len(compatible_packages) == 0:
            raise RuntimeError(f"No compatible packages found for {package}")

        for compatible_package in compatible_packages:
            try:
                self._logger.debug(f"Downloading package {compatible_package}")

                package_executable = self._remote_manager.package_executable(
                    compatible_package, self._package_platform
                )
            except IOError:
                self._logger.error(f"Failed to download package {compatible_package}")
                continue

            package_definition: PackageDefinition = PackageDefinition(
                name=compatible_package.definition().name(),
                version=compatible_package.version(),
                platform=self._package_platform,
            )

            return self._package_lifecycle_manager.save(
                package_definition, package_executable
            )

        raise RuntimeError(f"Failed to download package {package}")

    def to_package_definition(self, package: Package) -> PackageDefinition:
        name = package.name()
        version = self.resolve_package_version(package.name(), package.version())

        return PackageDefinition(
            name=name,
            version=version,
            platform=self._package_platform,
        )
