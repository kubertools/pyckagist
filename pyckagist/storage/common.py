from abc import ABC, abstractmethod

from pyckagist.model.package import PackageDefinition
from pyckagist.storage.entity.package import PackageEntity
from pyckagist.storage.entity.reference import ReferenceEntity


class PackageManifest(ABC):
    def __init__(self):
        self._packages = {}
        self._references = []

        self.load()

    def save(self):
        self._save_references(self._references)
        self._save_packages(self._packages)

    def load(self):
        self._packages = self._load_packages()
        self._references = self._load_references()

    def references(self) -> list[ReferenceEntity]:
        return self._references

    def packages(self) -> dict[str, PackageEntity]:
        return self._packages

    @abstractmethod
    def _load_references(self) -> list[ReferenceEntity]:
        raise NotImplementedError()

    @abstractmethod
    def _save_references(self, references: list[ReferenceEntity]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _save_packages(self, packages: dict[str, PackageEntity]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _load_packages(self) -> dict[str, PackageEntity]:
        raise NotImplementedError()


class PackageStorage(ABC):
    @abstractmethod
    def resolve_package_path(self, package: PackageDefinition) -> str:
        raise NotImplementedError()

    @abstractmethod
    def save_package(self, package: PackageDefinition, data: bytes) -> None:
        raise NotImplementedError()

    @abstractmethod
    def delete_package(self, package: PackageDefinition) -> None:
        raise NotImplementedError()

    @abstractmethod
    def load_package(self, package: PackageDefinition) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def package_exists(self, package: PackageDefinition) -> bool:
        raise NotImplementedError()
