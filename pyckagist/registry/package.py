from kommonlib.registry import AbstractRegistry

from pyckagist.model.package import Package


class PackageRegistry(AbstractRegistry[str, Package]):
    def _is_bidirectional(self) -> bool:
        return False

    def _is_unique(self) -> bool:
        return True
