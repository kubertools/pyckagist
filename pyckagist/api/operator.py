import logging
from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional

from typing_extensions import Self

from pyckagist.api.interface import PackageInterface


class PackageOperator(ABC):
    _logger: Optional[Logger] = None

    @classmethod
    @abstractmethod
    def instantiate(cls, interface: PackageInterface) -> Self:
        raise NotImplementedError

    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)

        return self._logger
