from kommonlib.registry import AbstractRegistry

from pyckagist.registry.source import PackageSourceRegistry


class TestPackageSourceRegistry:
    def test_package_source_registry(self):
        assert issubclass(PackageSourceRegistry, AbstractRegistry)

        registry = PackageSourceRegistry()

        assert registry._is_unique() is True
        assert registry._is_bidirectional() is False
