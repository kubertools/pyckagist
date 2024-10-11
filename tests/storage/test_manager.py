from pyckagist import PackagePlatform
from pyckagist.model.package import PackageDefinition, ExecutablePackage
from pyckagist.storage.common import PackageManifest, PackageStorage
from pyckagist.storage.entity.package import PackageEntity
from pyckagist.storage.entity.reference import ReferenceEntity
from pyckagist.storage.manager import PackageLifecycleManager


class TestPackageLifecycleManager:
    @staticmethod
    def _create_manifest(mocker):
        mock_manifest = mocker.Mock(spec=PackageManifest)

        mock_manifest.references.return_value = []
        mock_manifest.packages.return_value = {}

        return mock_manifest

    @staticmethod
    def _create_executable_package(suffix=""):
        return ExecutablePackage(
            definition=PackageDefinition(
                name="test_package" + suffix,
                version="1.0",
                platform=PackagePlatform(
                    system="test_system", architecture="test_arch"
                ),
            ),
            executable_path="/path/to/executable",
            executable_hash="hash123",
        )

    def test_register_adds_package_to_manifest(self, mocker):
        manifest = self._create_manifest(mocker)
        manager = PackageLifecycleManager(manifest, mocker.Mock(spec=PackageStorage))

        namespace = "test_namespace"
        executable_package = self._create_executable_package()

        manager.register(namespace, executable_package)

        assert (
            manager._to_package_key(executable_package.definition())
            in manifest.packages()
        )
        manifest.save.assert_called_once()

    def test_unregister_removes_package_from_manifest_and_cleans_up(self, mocker):
        manifest = self._create_manifest(mocker)
        manager = PackageLifecycleManager(manifest, mocker.Mock(spec=PackageStorage))

        namespace = "test_namespace"
        executable_package = self._create_executable_package()

        key = manager._to_package_key(executable_package.definition())

        reference = ReferenceEntity(namespace=namespace, package=key)
        manifest.references.return_value = [reference]

        manager.unregister(namespace, executable_package)

        assert reference not in manifest.references()
        assert key not in manifest.packages()

        manifest.save.assert_called_once()

    def test_save_stores_package_and_updates_manifest(self, mocker):
        manifest = self._create_manifest(mocker)

        storage = mocker.Mock(spec=PackageStorage)
        storage.resolve_package_path.return_value = "/path/to/executable"

        manager = PackageLifecycleManager(manifest, storage)

        executable_package = self._create_executable_package()

        key = manager._to_package_key(executable_package.definition())

        manager.save(executable_package.definition(), b"test data")

        assert key in manifest.packages()

        storage.save_package.assert_called_once_with(
            executable_package.definition(), b"test data"
        )
        manifest.save.assert_called_once()

    def test_delete_removes_package_from_storage_and_manifest(self, mocker):
        manifest = self._create_manifest(mocker)
        executable_package = self._create_executable_package()

        storage = mocker.Mock(spec=PackageStorage)
        storage.resolve_package_path.return_value = "/path/to/executable"

        manager = PackageLifecycleManager(manifest, storage)

        key = manager._to_package_key(executable_package.definition())
        manifest.packages()[key] = executable_package

        manager.delete(executable_package.definition())

        assert key not in manifest.packages()

        storage.delete_package.assert_called_once_with(executable_package.definition())
        manifest.save.assert_called_once()

    def test_sync_updates_manifest_references(self, mocker):
        manifest = self._create_manifest(mocker)

        manager = PackageLifecycleManager(manifest, mocker.Mock(spec=PackageStorage))

        namespace = "test_namespace"
        definitions = [
            PackageDefinition(
                name="test_package_1",
                version="1.0",
                platform=PackagePlatform(system="linux", architecture="x86_64"),
            ),
            PackageDefinition(
                name="test_package_2",
                version="1.0",
                platform=PackagePlatform(system="linux", architecture="x86_64"),
            ),
        ]

        reference_1 = ReferenceEntity(
            namespace=namespace, package=manager._to_package_key(definitions[0])
        )
        reference_2 = ReferenceEntity(
            namespace=namespace, package=manager._to_package_key(definitions[1])
        )
        reference_3 = ReferenceEntity(namespace=namespace, package="invalid_reference")
        reference_4 = ReferenceEntity(
            namespace="other_namespace", package=manager._to_package_key(definitions[1])
        )

        manifest.references().extend([reference_1, reference_3, reference_4])

        manager.sync(namespace, definitions)

        assert len(manifest.references()) == 2
        assert reference_1 in manifest.references()
        assert reference_4 in manifest.references()
        assert reference_2 not in manifest.references()
        assert reference_3 not in manifest.references()

        manifest.save.assert_called_once()

    def test_find_returns_correct_executable_package(self, mocker):
        manifest = self._create_manifest(mocker)
        executable_package = self._create_executable_package()

        storage = mocker.Mock(spec=PackageStorage)
        storage.resolve_package_path.return_value = "/path/to/executable"

        manager = PackageLifecycleManager(manifest, storage)

        mock_package_entity = mocker.Mock()
        mock_package_entity.to_executable_package.return_value = executable_package

        key = manager._to_package_key(executable_package.definition())

        manifest.packages()[key] = mock_package_entity

        result = manager.find(executable_package.definition())

        assert result == executable_package

    def test_find_returns_none_when_not_registered(self, mocker):
        manifest = self._create_manifest(mocker)
        executable_package = self._create_executable_package()

        storage = mocker.Mock(spec=PackageStorage)
        storage.resolve_package_path.return_value = "/path/to/executable"

        manager = PackageLifecycleManager(manifest, storage)

        assert manager.find(executable_package.definition()) is None

    def test_find_returns_none_when_platform_mismatch(self, mocker):
        manifest = self._create_manifest(mocker)
        executable_package = self._create_executable_package()

        storage = mocker.Mock(spec=PackageStorage)
        storage.resolve_package_path.return_value = "/path/to/executable"

        manager = PackageLifecycleManager(manifest, storage)

        key = manager._to_package_key(executable_package.definition())

        manifest.packages.return_value = {
            key: PackageEntity.from_executable_package(executable_package)
        }

        executable_package.definition()._platform = PackagePlatform(
            system="wrong", architecture="platform"
        )
        assert manager.find(executable_package.definition()) is None

    def test_reset_clears_references_and_cleans_manifest(self, mocker):
        manifest = self._create_manifest(mocker)

        manager = PackageLifecycleManager(manifest, mocker.Mock(spec=PackageStorage))

        mock_reference_1 = mocker.Mock(spec=ReferenceEntity)
        mock_reference_2 = mocker.Mock(spec=ReferenceEntity)

        exec_package_1 = self._create_executable_package("1")
        exec_package_2 = self._create_executable_package("2")
        mock_package_1 = PackageEntity.from_executable_package(exec_package_1)
        mock_package_2 = PackageEntity.from_executable_package(exec_package_2)

        manifest.references().extend([mock_reference_1, mock_reference_2])
        manifest.packages().update(
            {
                manager._to_package_key(exec_package_1.definition()): mock_package_1,
                manager._to_package_key(exec_package_2.definition()): mock_package_2,
            }
        )

        manager.reset()

        assert len(manifest.references()) == 0
        assert len(manifest.packages()) == 0

        manifest.save.assert_has_calls([mocker.call(), mocker.call(), mocker.call()])

    def test_list_returns_all_executable_packages(self, mocker):
        mock_manifest = mocker.Mock(spec=PackageManifest)
        mock_storage = mocker.Mock(spec=PackageStorage)
        manager = PackageLifecycleManager(mock_manifest, mock_storage)

        mock_reference_1 = mocker.Mock(spec=ReferenceEntity)
        mock_reference_1.namespace = "test_namespace"
        mock_reference_1.package = "package_key_1"

        mock_reference_2 = mocker.Mock(spec=ReferenceEntity)
        mock_reference_2.namespace = "test_namespace"
        mock_reference_2.package = "package_key_2"

        mock_manifest.references.return_value = [mock_reference_1, mock_reference_2]

        mock_package_1 = mocker.Mock(spec=PackageEntity)
        mock_package_1.to_executable_package.return_value = mocker.Mock(
            spec=ExecutablePackage
        )

        mock_package_2 = mocker.Mock(spec=PackageEntity)
        mock_package_2.to_executable_package.return_value = mocker.Mock(
            spec=ExecutablePackage
        )

        mock_manifest.packages.return_value = {
            "package_key_1": mock_package_1,
            "package_key_2": mock_package_2,
        }

        packages = manager.list()

        assert len(packages) == 2
        assert all(isinstance(pkg, ExecutablePackage) for pkg in packages)
