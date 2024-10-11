import re

import pytest

from pyckagist import PackagePlatform
from pyckagist.core.remote import RemoteManager
from pyckagist.core.resolver import PackageResolver
from pyckagist.model.package import ExecutablePackage, Package, PackageDefinition
from pyckagist.model.remote import RemotePackage
from pyckagist.storage.manager import PackageLifecycleManager


class TestPackageResolver:
    def test_resolve_package_version_locally(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        resolver = PackageResolver(package_platform, package_lifecycle_manager, None)

        local_package = mocker.Mock(spec=ExecutablePackage)
        local_package.definition().name.return_value = "test_package"
        local_package.definition().version.return_value = "1.0.0"
        package_lifecycle_manager.list.return_value = [local_package]

        resolved_version = resolver.resolve_package_version("test_package", "latest")

        assert resolved_version == "1.0.0"

    def test_resolve_package_version_remotely(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        package_name = "test_package"
        package_version = "latest"
        remote_package = mocker.Mock(spec=RemotePackage)
        remote_package.version.return_value = "2.0.0"
        remote_manager.find_compatible_packages.return_value = [remote_package]

        resolved_version = resolver.resolve_package_version(
            package_name, package_version
        )

        assert resolved_version == "2.0.0"

    def test_resolve_package_version_no_versions_found(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        resolver = PackageResolver(package_platform, package_lifecycle_manager)

        package_name = "non_existent_package"
        package_version = "latest"
        package_lifecycle_manager.list.return_value = []

        with pytest.raises(
            RuntimeError, match=f"No package versions found for {package_name}"
        ):
            resolver.resolve_package_version(package_name, package_version)

    def test_resolve_package_download(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)

        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_lifecycle_manager.save.return_value = ExecutablePackage(
            definition=PackageDefinition("test_package", "1.0.0", package_platform),
            executable_path="executable_path",
            executable_hash="executable_hash",
        )

        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        remote_package = mocker.Mock(spec=RemotePackage)
        remote_package.definition.return_value = mocker.Mock()
        remote_package.definition.return_value.name.return_value = "test_package"
        remote_package.version.return_value = "1.0.0"
        remote_manager.find_compatible_packages.return_value = [remote_package]
        remote_manager.package_executable.return_value = b"executable_data"

        package = Package("test_package", "latest")

        resolved_package = resolver.resolve_package(package)

        assert resolved_package.definition().name() == "test_package"
        assert resolved_package.definition().version() == "1.0.0"

    def test_resolve_when_remote_managed_is_not_provided(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        resolver = PackageResolver(package_platform, package_lifecycle_manager, None)

        package = Package("test_package", "latest")

        with pytest.raises(
            RuntimeError,
            match=re.escape(
                f"Package {package} is not present locally and remote manager is not available"
            ),
        ):
            resolver.resolve_package(package)

    def test_convert_package_to_definition(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        package_name = "test_package"
        package_version = "1.0.0"
        package = Package(package_name, package_version)

        package_definition = resolver.to_package_definition(package)

        assert package_definition.name() == package_name
        assert package_definition.version() == package_version
        assert package_definition.platform() == package_platform

    def test_resolve_package_no_package_versions_found(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)

        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_lifecycle_manager.list.return_value = []

        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        package = Package("test_package", "latest")
        remote_manager.find_compatible_packages.return_value = []

        with pytest.raises(
            RuntimeError,
            match=re.escape(f"No package versions found for {package.name()}"),
        ):
            resolver.resolve_package(package)

    def test_handle_network_failures(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        package = Package("test_package", "latest")
        remote_package = mocker.Mock(spec=RemotePackage)
        remote_package.version.return_value = "1.0.0"
        remote_manager.find_compatible_packages.return_value = [remote_package]

        remote_manager.package_executable.side_effect = IOError

        with pytest.raises(RuntimeError):
            resolver.resolve_package(package)

    def test_resolve_package_version_fallback_to_local(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        resolver = PackageResolver(package_platform, package_lifecycle_manager, None)

        package_name = "test_package"
        package_version = "latest"
        local_package = mocker.Mock(spec=ExecutablePackage)
        local_package.definition().name.return_value = package_name
        local_package.definition().version.return_value = "1.0.0"
        package_lifecycle_manager.list.return_value = [local_package]

        resolved_version = resolver.resolve_package_version(
            package_name, package_version
        )

        assert resolved_version == "1.0.0"

    def test_logging_package_download_failure(self, mocker):
        logger_mock = mocker.Mock()

        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        remote_manager = mocker.Mock(spec=RemoteManager)

        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )
        resolver._logger = logger_mock

        package = Package("test_package", "1.0.0")
        remote_package = mocker.Mock(spec=RemotePackage)
        remote_package.definition().name.return_value = "test_package"
        remote_package.version.return_value = "1.0.0"
        remote_manager.find_compatible_packages.return_value = [remote_package]
        remote_manager.package_executable.side_effect = IOError

        with pytest.raises(RuntimeError):
            resolver.resolve_package(package)

        logger_mock.error.assert_called_with(
            f"Failed to download package {remote_package}"
        )

    def test_no_compatible_packages_found(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)

        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_lifecycle_manager.list.return_value = []

        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        package = Package("test_package", "1.0.0")

        remote_manager.find_compatible_packages.return_value = []

        with pytest.raises(
            RuntimeError, match=re.escape(f"No compatible packages found for {package}")
        ):
            resolver.resolve_package(package)

    def test_save_package_correctly(self, mocker):
        package_platform = mocker.Mock(spec=PackagePlatform)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        remote_manager = mocker.Mock(spec=RemoteManager)
        resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )

        package = Package("test_package", "1.0.0")
        remote_package = mocker.Mock(spec=RemotePackage)
        remote_package.definition().name.return_value = "test_package"
        remote_package.version.return_value = "1.0.0"
        remote_package.supported_platforms.return_value = [package_platform]
        remote_manager.find_compatible_packages.return_value = [remote_package]
        remote_manager.package_executable.return_value = b"mock_executable_data"

        resolver.resolve_package(package)

        package_definition = PackageDefinition(
            name="test_package", version="1.0.0", platform=package_platform
        )
        package_lifecycle_manager.save.assert_called_once_with(
            package_definition, b"mock_executable_data"
        )
