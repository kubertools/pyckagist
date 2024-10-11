from typing import Type

from kommonlib.registry import AbstractRegistry

from pyckagist.api.operator import PackageOperator


class PackageOperatorRegistry(AbstractRegistry[str, Type[PackageOperator]]):
    def _is_bidirectional(self) -> bool:
        return False

    def _is_unique(self) -> bool:
        return True
