import pytest

from pyckagist.model.package import PackageDefinition
from pyckagist.storage.common import PackageStorage, PackageManifest
from pyckagist.storage.entity.package import PackageEntity, PackagePlatformEntity
from pyckagist.storage.entity.reference import ReferenceEntity


class DummyPackageManifest(PackageManifest):
    _pkgs: dict[str, PackageEntity] = {}
    _refs: list[ReferenceEntity] = []

    def _load_references(self) -> list[ReferenceEntity]:
        return self._refs

    def _load_packages(self) -> dict[str, PackageEntity]:
        return self._pkgs

    def _save_references(self, references: list[ReferenceEntity]) -> None:
        self._refs = references.copy()

    def _save_packages(self, packages: dict[str, PackageEntity]) -> None:
        self._pkgs = packages.copy()


# noinspection PyMissingConstructor
class SuperPackageManifest(PackageManifest):
    def __init__(self):
        # this implementation is intentionally left empty
        pass

    def _load_references(self) -> list[ReferenceEntity]:
        return super()._load_references()  # type: ignore[safe-super]

    def _load_packages(self) -> dict[str, PackageEntity]:
        return super()._load_packages()  # type: ignore[safe-super]

    def _save_references(self, references: list[ReferenceEntity]) -> None:
        return super()._save_references(references)  # type: ignore[safe-super]

    def _save_packages(self, packages: dict[str, PackageEntity]) -> None:
        return super()._save_packages(packages)  # type: ignore[safe-super]


class SuperPackageStorage(PackageStorage):
    def resolve_package_path(self, package: PackageDefinition) -> str:
        return super().resolve_package_path(package)  # type: ignore[safe-super]

    def save_package(self, package: PackageDefinition, data: bytes) -> None:
        return super().save_package(package, data)  # type: ignore[safe-super]

    def delete_package(self, package: PackageDefinition) -> None:
        return super().delete_package(package)  # type: ignore[safe-super]

    def load_package(self, package: PackageDefinition) -> bytes:
        return super().load_package(package)  # type: ignore[safe-super]

    def package_exists(self, package: PackageDefinition) -> bool:
        return super().package_exists(package)  # type: ignore[safe-super]


class TestPackageManifest:
    def test_raise_not_implemented_error(self):
        manifest = SuperPackageManifest()

        with pytest.raises(NotImplementedError):
            manifest._load_references()
        with pytest.raises(NotImplementedError):
            manifest._load_packages()
        with pytest.raises(NotImplementedError):
            manifest._save_references([])
        with pytest.raises(NotImplementedError):
            manifest._save_packages({})

    def test_initialization_of_package_manifest(self):
        manifest = DummyPackageManifest()

        assert manifest.packages() == {}
        assert manifest.references() == []

    def test_save_and_load_with_empty_data(self):
        manifest = DummyPackageManifest()

        manifest.save()
        manifest.load()

        assert manifest.packages() == {}
        assert manifest.references() == []

    def test_save_and_load_with_data(self):
        manifest = DummyPackageManifest()

        test_package = PackageEntity(
            name="test",
            version="1.0.0",
            platform=PackagePlatformEntity(
                system="test",
                architecture="test",
            ),
            executable_path="test",
            executable_hash="test",
        )
        test_reference = ReferenceEntity(namespace="test", package="test_package")

        manifest.packages()["test"] = test_package
        manifest.references().append(test_reference)

        manifest.save()

        assert manifest.packages() == {"test": test_package}
        assert manifest.references() == [test_reference]

        manifest.packages().clear()
        manifest.references().clear()

        manifest.load()

        assert manifest.packages() == {"test": test_package}
        assert manifest.references() == [test_reference]


class TestPackageStorage:
    def test_raise_not_implemented_error(self, mocker):
        storage = SuperPackageStorage()

        package_definition = mocker.Mock()

        with pytest.raises(NotImplementedError):
            storage.resolve_package_path(package_definition)
        with pytest.raises(NotImplementedError):
            storage.save_package(package_definition, b"data")
        with pytest.raises(NotImplementedError):
            storage.delete_package(package_definition)
        with pytest.raises(NotImplementedError):
            storage.load_package(package_definition)
        with pytest.raises(NotImplementedError):
            storage.package_exists(package_definition)
