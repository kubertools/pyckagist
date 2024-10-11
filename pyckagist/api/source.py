from abc import ABC, abstractmethod

from pyckagist.model.platform import PackagePlatform


class PackageSource(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def package_list(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def stable_package_version(self, package_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def latest_package_version(self, package_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def has_package_version(self, package_name: str, package_version: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def package_platforms(
        self, package_name: str, package_version: str
    ) -> list[PackagePlatform]:
        raise NotImplementedError

    @abstractmethod
    def package_executable(
        self, package_name: str, version: str, platform: PackagePlatform
    ) -> bytes:
        raise NotImplementedError

    def __str__(self):
        return self.name()
