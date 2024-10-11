import os.path

import pytest

from pyckagist.api.source import PackageSource
from pyckagist.core.controller import PackageController
from pyckagist.core.manager import PackageManager, PackageManagerBuilder
from pyckagist.model.platform import PackagePlatform
from pyckagist.storage.filesystem.manifest import FilePackageManifest
from pyckagist.storage.filesystem.storage import FilePackageStorage


class TestPackageManager:
    def test_initializes_with_valid_controller(self, mocker):
        controller_mock = mocker.Mock(spec=PackageController)
        package_manager = PackageManager(controller_mock)

        assert package_manager.controller() == controller_mock

    def test_wrap_returns_correct_namespace(self, mocker):
        controller_mock = mocker.Mock(spec=PackageController)
        package_manager = PackageManager(controller_mock)
        namespace = "test_namespace"

        package_context = package_manager.wrap(namespace)

        assert package_context._namespace == namespace

    def test_wrap_method_passes_controller_to_package_context(self, mocker):
        controller_mock = mocker.Mock(spec=PackageController)
        package_manager = PackageManager(controller_mock)

        namespace = "test_namespace"
        package_context = package_manager.wrap(namespace)

        assert package_context._controller == controller_mock


class TestPackageManagerBuilder:
    def test_build_package_manager(self, mocker):
        mocker.patch("pyckagist.core.manager.FilePackageStorage")
        mocker.patch("pyckagist.core.manager.FilePackageManifest")
        mocker.patch("pyckagist.core.manager.PackageResolver")

        builder = PackageManagerBuilder()

        builder.base_path("/test/path")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)

    def test_build_without_base_path_raises_value_error(self):
        builder = PackageManagerBuilder()

        with pytest.raises(ValueError, match="Base path is not set"):
            builder.build()

    def test_enable_offline_mode_sets_package_manager_without_remote_sources(
        self, mocker
    ):
        builder = PackageManagerBuilder()

        builder.base_path("/test/path")
        builder.offline_mode(True)

        mocker.patch("pyckagist.core.manager.FilePackageStorage")
        mocker.patch("pyckagist.core.manager.FilePackageManifest")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)

        assert package_manager.controller()._package_resolver._remote_manager is None

    def test_adding_package_sources(self, mocker):
        mock_package_source = mocker.MagicMock(spec=PackageSource)
        mock_package_source.name.return_value = "test_source"

        mocker.patch("pyckagist.core.manager.FilePackageStorage")
        mocker.patch("pyckagist.core.manager.FilePackageManifest")

        builder = PackageManagerBuilder()

        builder.base_path("/test/path")
        builder.package_source(mock_package_source)

        package_manager = builder.build()

        assert (
            package_manager.controller()._package_resolver._remote_manager is not None
        )

        source_registry = (
            package_manager.controller()._package_resolver._remote_manager._source_registry
        )

        assert source_registry.is_key_registered("test_source")
        assert source_registry.find_by_key("test_source") == mock_package_source

    def test_package_platform_initializes_package_manager(self, mocker):
        platform = PackagePlatform("linux", "x86_64")

        builder = PackageManagerBuilder()

        builder.base_path("/test/path")
        builder.package_platform(platform)

        mocker.patch("pyckagist.core.manager.FilePackageStorage")
        mocker.patch("pyckagist.core.manager.FilePackageManifest")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)

        assert (
            package_manager.controller()._package_resolver._package_platform == platform
        )

    def test_default_to_current_platform(self, mocker):
        builder = PackageManagerBuilder()

        builder.base_path("/test/path")

        mocker.patch("pyckagist.core.manager.FilePackageStorage")
        mocker.patch("pyckagist.core.manager.FilePackageManifest")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)

        assert (
            package_manager.controller()._package_resolver._package_platform
            == PackagePlatform.current_platform()
        )

    def test_create_file_package_storage_with_correct_binary_storage_path(self, mocker):
        builder = PackageManagerBuilder()

        builder.base_path("/test/path")

        mocker.patch("pyckagist.core.manager.FilePackageManifest")

        mocker.patch("os.makedirs")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)
        assert isinstance(
            package_manager.controller()._package_lifecycle_manager._storage,
            FilePackageStorage,
        )

    def test_create_process_dispatcher_with_correct_cache_path(self, mocker):
        builder = PackageManagerBuilder()

        builder.base_path("/test/path")

        mocker.patch("pyckagist.core.manager.FilePackageStorage")
        mocker.patch("pyckagist.core.manager.FilePackageManifest")

        mocker.patch("os.makedirs")
        mocker.patch("builtins.open")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)

        assert (
            package_manager.controller()._process_dispatcher._cache_path
            == "/test/path/cache"
        )

    def test_create_file_package_manifest_with_correct_json_file_path(self, mocker):
        builder = PackageManagerBuilder()

        builder.base_path("/test/path")

        mocker.patch("pyckagist.core.manager.FilePackageStorage")

        mocker.patch("os.makedirs")
        mocker.patch("builtins.open")

        package_manager = builder.build()

        assert isinstance(package_manager, PackageManager)
        assert isinstance(
            package_manager.controller()._package_lifecycle_manager._manifest,
            FilePackageManifest,
        )

        assert (
            package_manager.controller()._package_lifecycle_manager._manifest._data_file
            == os.path.abspath("/test/path/packages.json")
        )
