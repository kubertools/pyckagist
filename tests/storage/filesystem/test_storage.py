import os.path
from unittest.mock import mock_open

from pyckagist import PackagePlatform
from pyckagist.model.package import PackageDefinition
from pyckagist.storage.filesystem.storage import FilePackageStorage


class TestFilePackageStorage:
    def test_resolve_package_path_for_different_platforms(self, mocker):
        mocker.patch("os.makedirs")

        mock_platform_windows = mocker.Mock(spec=PackagePlatform)
        mock_platform_windows.system.return_value = "windows"
        mock_platform_windows.architecture.return_value = "x86_64"

        mock_platform_linux = mocker.Mock(spec=PackagePlatform)
        mock_platform_linux.system.return_value = "linux"
        mock_platform_linux.architecture.return_value = "x86_64"

        package_windows = PackageDefinition("testpkg", "1.0.0", mock_platform_windows)
        package_linux = PackageDefinition("testpkg", "1.0.0", mock_platform_linux)

        storage = FilePackageStorage("/fake/path")

        expected_path_windows = os.path.abspath(
            "/fake/path/testpkg-1.0.0-windows-x86_64.exe"
        )
        expected_path_linux = os.path.abspath("/fake/path/testpkg-1.0.0-linux-x86_64")

        assert storage.resolve_package_path(package_windows) == expected_path_windows
        assert storage.resolve_package_path(package_linux) == expected_path_linux

    def test_delete_package(self, mocker):
        mocker.patch("os.makedirs")

        storage = FilePackageStorage("/fake/path")
        package = PackageDefinition(
            "testpkg", "1.0.0", PackagePlatform(system="system", architecture="arch")
        )

        exists_mock = mocker.patch("os.path.exists", return_value=True)
        remove_mock = mocker.patch("os.remove")

        storage.delete_package(package)

        exists_mock.assert_called_once_with(
            os.path.abspath("/fake/path/testpkg-1.0.0-system-arch")
        )
        remove_mock.assert_called_once_with(
            os.path.abspath("/fake/path/testpkg-1.0.0-system-arch")
        )

    def test_load_package_data_correctly(self, mocker):
        mocker.patch("os.makedirs")

        package = PackageDefinition(
            "testpkg", "1.0.0", PackagePlatform(system="system", architecture="arch")
        )

        mocker.patch("builtins.open", mock_open(read_data=b"test data"))
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.chmod")

        storage = FilePackageStorage("/fake/path")
        data = b"test data"

        storage.save_package(package, data)

        loaded_data = storage.load_package(package)

        assert loaded_data == data

    def test_handle_non_existent_package_paths(self, mocker):
        mocker.patch("os.makedirs")

        mock_platform = mocker.Mock(spec=PackagePlatform)
        mock_platform.system.return_value = "linux"
        mock_platform.architecture.return_value = "x86_64"

        package = PackageDefinition("nonexistentpkg", "1.0.0", mock_platform)

        storage = FilePackageStorage("/fake/path")

        assert not storage.package_exists(package)
