import logging

import pytest

from pyckagist.api.interface import PackageInterface
from pyckagist.api.operator import PackageOperator


class TestablePackageOperator(PackageOperator):
    @classmethod
    def instantiate(cls, interface: PackageInterface):
        return super().instantiate(interface)


class TestPackageOperator:
    def test_logger(self, mocker):
        operator = TestablePackageOperator()

        mocker.patch("logging.getLogger", return_value=logging.Logger("TestLogger"))

        logger_instance = operator.logger()

        assert isinstance(logger_instance, logging.Logger)
        assert logger_instance.name == "TestLogger"

    def test_instantiate(self, mocker):
        with pytest.raises(NotImplementedError):
            TestablePackageOperator.instantiate(mocker.Mock())
