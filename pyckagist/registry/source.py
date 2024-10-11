from kommonlib.registry import AbstractRegistry

from pyckagist.api.source import PackageSource


class PackageSourceRegistry(AbstractRegistry[str, PackageSource]):
    def _is_bidirectional(self) -> bool:
        return False

    def _is_unique(self) -> bool:
        return True
