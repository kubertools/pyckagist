from kommonlib.registry import AbstractRegistry

from pyckagist.registry.operator import PackageOperatorRegistry


class TestPackageOperatorRegistry:
    def test_package_operator_registry(self):
        assert issubclass(PackageOperatorRegistry, AbstractRegistry)

        registry = PackageOperatorRegistry()

        assert registry._is_unique() is True
        assert registry._is_bidirectional() is False
