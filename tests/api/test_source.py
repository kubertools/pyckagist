import pytest

from pyckagist.api.source import PackageSource
from pyckagist.model.platform import PackagePlatform


class TestablePackageSource(PackageSource):
    def name(self) -> str:
        return "TestablePackageSource"

    def package_list(self) -> list[str]:
        return super().package_list()  # type: ignore[safe-super]

    def stable_package_version(self, package_name: str) -> str:
        return super().stable_package_version(package_name)  # type: ignore[safe-super]

    def latest_package_version(self, package_name: str) -> str:
        return super().latest_package_version(package_name)  # type: ignore[safe-super]

    def has_package_version(self, package_name: str, version: str) -> bool:
        return super().has_package_version(package_name, version)  # type: ignore[safe-super]

    def package_platforms(
        self, package_name: str, package_version: str
    ) -> list[PackagePlatform]:
        return super().package_platforms(package_name, package_version)  # type: ignore[safe-super]

    def package_executable(
        self, package_name: str, version: str, platform: PackagePlatform
    ) -> bytes:
        return super().package_executable(package_name, version, platform)  # type: ignore[safe-super]

    def proxy_name(self) -> str:
        return super().name()  # type: ignore[safe-super]


class TestPackageSource:
    def test_package_source_str(self):
        source = TestablePackageSource()

        assert str(source) == source.name()

    def test_raise_not_implemented_error(self):
        source = TestablePackageSource()

        with pytest.raises(NotImplementedError):
            source.proxy_name()
        with pytest.raises(NotImplementedError):
            source.package_list()
        with pytest.raises(NotImplementedError):
            source.stable_package_version("package_name")
        with pytest.raises(NotImplementedError):
            source.latest_package_version("package_name")
        with pytest.raises(NotImplementedError):
            source.has_package_version("package_name", "version")
        with pytest.raises(NotImplementedError):
            source.package_platforms("package_name", "version")
        with pytest.raises(NotImplementedError):
            platform = PackagePlatform("system", "architecture")

            source.package_executable("package_name", "version", platform)
