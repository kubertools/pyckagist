import pytest

from pyckagist.api.source import PackageSource
from pyckagist.core.remote import RemoteManager
from pyckagist.model.platform import PackagePlatform
from pyckagist.model.remote import RemotePackageDefinition, RemotePackage
from pyckagist.registry.source import PackageSourceRegistry


class TestRemoteManager:
    def test_initializing_remote_manager_with_valid_registry(self, mocker):
        registry_mock = mocker.Mock(spec=PackageSourceRegistry)

        remote_manager = RemoteManager(registry_mock)

        assert remote_manager._source_registry == registry_mock

    def test_lookup_non_existent_package_source(self, mocker):
        registry_mock = mocker.Mock(spec=PackageSourceRegistry)
        registry_mock.find_by_key.return_value = None

        remote_manager = RemoteManager(registry_mock)

        with pytest.raises(RuntimeError, match="Source non_existent_source not found"):
            remote_manager._lookup_source("non_existent_source")

    def test_retrieving_package_definitions(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        source_mock1 = mocker.Mock(spec=PackageSource)
        source_mock2 = mocker.Mock(spec=PackageSource)

        source_mock1.name.return_value = "source_name1"
        source_mock1.package_list.return_value = ["package_name"]

        source_mock2.name.return_value = "source_name2"
        source_mock2.package_list.return_value = ["other_package_name"]

        remote_manager._source_registry.register("source_name1", source_mock1)
        remote_manager._source_registry.register("source_name2", source_mock2)
        # noinspection PyTypeChecker
        remote_manager._source_registry.register("source_name3", None)  # type: ignore[arg-type]

        result = remote_manager.lookup_package_definitions("package_name")

        assert result == [RemotePackageDefinition("package_name", "source_name1")]

    def test_finding_latest_version_of_package(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]
        source_mock.latest_package_version.return_value = "1.1.1"

        remote_manager._source_registry.register("test_source", source_mock)

        result = remote_manager.lookup_package_version(
            RemotePackageDefinition("test_package", "test_source"), "latest"
        )

        assert result == "1.1.1"

    def test_finding_stable_version(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]
        source_mock.stable_package_version.return_value = "1.2.3"

        remote_manager._source_registry.register("test_source", source_mock)

        result = remote_manager.lookup_package_version(
            RemotePackageDefinition("test_package", "test_source"), "stable"
        )

        assert result == "1.2.3"

    def test_retrieving_package_metadata(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        remote_package_definition = RemotePackageDefinition(
            "test_package", "test_source"
        )
        remote_package = RemotePackage(
            remote_package_definition,
            "1.2.3",
            [PackagePlatform("test_system", "test_architecture")],
        )

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]
        source_mock.package_platforms.return_value = (
            remote_package.supported_platforms()
        )

        remote_manager._source_registry.register("test_source", source_mock)

        result = remote_manager.lookup_remote_package(
            RemotePackageDefinition("test_package", "test_source"), "1.2.3"
        )

        assert result == remote_package

    def test_find_compatible_packages_with_compatible_platform(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        compatible_platform = PackagePlatform("test_system1", "test_architecture1")
        incompatible_platform = PackagePlatform("test_system2", "test_architecture2")

        remote_package_definition1 = RemotePackageDefinition(
            "test_package", "test_source1"
        )
        remote_package_definition2 = RemotePackageDefinition(
            "test_package", "test_source2"
        )

        source_mock1 = mocker.Mock(spec=PackageSource)
        source_mock2 = mocker.Mock(spec=PackageSource)
        source_mock3 = mocker.Mock(spec=PackageSource)

        source_mock1.name.return_value = "test_source1"
        source_mock2.name.return_value = "test_source2"
        source_mock3.name.return_value = "test_source3"

        source_mock1.package_list.return_value = ["test_package"]
        source_mock2.package_list.return_value = ["test_package"]
        source_mock3.package_list.return_value = ["test_package"]

        package1 = RemotePackage(
            remote_package_definition1,
            "1.2.3",
            [compatible_platform, incompatible_platform],
        )
        package2 = RemotePackage(
            remote_package_definition2, "1.2.3", [incompatible_platform]
        )

        source_mock1.package_platforms.return_value = package1.supported_platforms()
        source_mock2.package_platforms.return_value = package2.supported_platforms()
        source_mock3.package_platforms.return_value = []

        remote_manager._source_registry.register("test_source1", source_mock1)
        remote_manager._source_registry.register("test_source2", source_mock2)
        remote_manager._source_registry.register("test_source3", source_mock3)

        result = remote_manager.find_compatible_packages(
            "test_package", "1.2.3", compatible_platform
        )

        assert result == [package1]

    def test_find_compatible_packages_with_missing_version(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]

        source_mock.has_package_version.return_value = False

        remote_manager._source_registry.register("test_source", source_mock)

        result = remote_manager.find_compatible_packages(
            "test_package", "1.2.3", mocker.Mock()
        )

        assert result == []

    def test_retrieving_package_executable(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]
        source_mock.package_executable.return_value = b"data"

        remote_manager._source_registry.register("test_source", source_mock)

        remote_package_definition = RemotePackageDefinition(
            "test_package", "test_source"
        )
        remote_package = RemotePackage(
            remote_package_definition,
            "1.2.3",
            [PackagePlatform("test_system", "test_architecture")],
        )
        platform = PackagePlatform("test_system", "test_architecture")
        executable = remote_manager.package_executable(remote_package, platform)

        assert executable == b"data"

    def test_handling_package_version_not_found(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        remote_package_definition = RemotePackageDefinition(
            "test_package", "test_source"
        )

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]
        source_mock.has_package_version.return_value = False

        remote_manager._source_registry.register("test_source", source_mock)

        assert (
            remote_manager.lookup_remote_package(remote_package_definition, "1.0.0")
            is None
        )

    def test_handling_package_not_found(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = []

        remote_manager._source_registry.register("test_source", source_mock)

        assert remote_manager.lookup_package_definitions("test_package") == []

    def test_no_compatible_packages_found(self, mocker):
        remote_manager = RemoteManager(PackageSourceRegistry())

        compatible_platform = PackagePlatform("test_system1", "test_architecture1")
        incompatible_platform = PackagePlatform("test_system2", "test_architecture2")

        remote_package_definition = RemotePackageDefinition(
            "test_package", "test_source"
        )

        source_mock = mocker.Mock(spec=PackageSource)

        source_mock.name.return_value = "test_source"
        source_mock.package_list.return_value = ["test_package"]

        package = RemotePackage(
            remote_package_definition, "1.2.3", [incompatible_platform]
        )

        source_mock.package_platforms.return_value = package.supported_platforms()

        remote_manager._source_registry.register("test_source", source_mock)

        result = remote_manager.find_compatible_packages(
            "test_package", "1.2.3", compatible_platform
        )

        assert result == []
