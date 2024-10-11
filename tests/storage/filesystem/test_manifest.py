from pyckagist.storage.entity.package import PackageEntity, PackagePlatformEntity
from pyckagist.storage.entity.reference import ReferenceEntity
from pyckagist.storage.filesystem.manifest import FilePackageManifest


class TestFilePackageManifest:
    def test_load_packages_from_valid_json(self, mocker):
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data='{"packages": {"pkg1": {"name": "pkg1", "version": "1.0", "platform": {"system": "linux", "architecture": "x86_64"}, "executable_path": "/path/to/exe", "executable_hash": "hash"}}}'
            ),
        )

        manifest = FilePackageManifest("dummy_path.json")

        packages = manifest.packages()

        assert len(packages) == 1
        assert packages["pkg1"].name == "pkg1"
        assert packages["pkg1"].version == "1.0"

    def test_save_packages_to_json_file(self, mocker):
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("builtins.open", mocker.mock_open())
        mocker.patch("json.load", return_value={})
        mocker.patch("json.dump")

        manifest = FilePackageManifest("dummy_path.json")

        package_entity = PackageEntity(
            name="test_package",
            version="1.0",
            platform=PackagePlatformEntity(system="linux", architecture="x86_64"),
            executable_path="/path/to/exe",
            executable_hash="hash",
        )
        manifest._save_packages({"test_package": package_entity})

        saved_packages = manifest._json_load("packages")

        assert len(saved_packages) == 1
        assert saved_packages["test_package"]["name"] == "test_package"
        assert saved_packages["test_package"]["version"] == "1.0"
        assert saved_packages["test_package"]["platform"]["system"] == "linux"
        assert saved_packages["test_package"]["platform"]["architecture"] == "x86_64"
        assert saved_packages["test_package"]["executable_path"] == "/path/to/exe"
        assert saved_packages["test_package"]["executable_hash"] == "hash"

    def test_load_references_from_valid_json(self, mocker):
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data='{"references": [{"namespace": "ns1", "package": "pkg1"}]}'
            ),
        )

        manifest = FilePackageManifest("dummy_path.json")

        references = manifest.references()

        assert len(references) == 1
        assert references[0].namespace == "ns1"
        assert references[0].package == "pkg1"

    def test_save_references_to_json_file(self, mocker):
        # Arrange
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch(
            "builtins.open",
            mocker.mock_open(
                read_data='{"references": [{"namespace": "ns1", "package": "pkg1"}]}'
            ),
        )

        manifest = FilePackageManifest("dummy_path.json")
        references = [ReferenceEntity(namespace="ns1", package="pkg1")]

        manifest._save_references(references)
        saved_references = manifest._json_load("references")

        assert len(saved_references) == 1
        assert saved_references[0]["namespace"] == "ns1"
        assert saved_references[0]["package"] == "pkg1"

    def test_json_file_not_present(self, mocker):
        mocker.patch("os.path.exists", return_value=False)

        manifest = FilePackageManifest("dummy_path.json")

        packages = manifest.packages()
        references = manifest.references()

        assert len(packages) == 0
        assert len(references) == 0

    def test_load_packages_with_non_existent_file(self, mocker):
        mocker.patch("os.path.exists", return_value=False)

        manifest = FilePackageManifest("non_existent.json")

        packages = manifest.packages()
        references = manifest.references()

        assert packages == {}
        assert references == []
