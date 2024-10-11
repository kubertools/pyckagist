from kommonlib.registry import AbstractRegistry

from pyckagist.registry.package import PackageRegistry


class TestPackageRegistry:
    def test_package_registry(self):
        assert issubclass(PackageRegistry, AbstractRegistry)

        registry = PackageRegistry()

        assert registry._is_unique() is True
        assert registry._is_bidirectional() is False
