from typing import Type

import pytest

from pyckagist import PackageContext, PackageOperator, Package, PackageContextBuilder
from pyckagist.core.controller import PackageController
from pyckagist.registry.operator import PackageOperatorRegistry
from pyckagist.registry.package import PackageRegistry


class TestPackageContext:
    def test_initialize_package_context(self, mocker):
        mock_controller = mocker.Mock(spec=PackageController)

        namespace = "test_namespace"
        package_registry = PackageRegistry()
        operator_registry = PackageOperatorRegistry()

        context = PackageContext(
            controller=mock_controller,
            namespace=namespace,
            package_registry=package_registry,
            operator_registry=operator_registry,
        )

        assert context.namespace() == namespace
        mock_controller.sync.assert_called_once_with(namespace, [])

    def test_use_registered_package(self, mocker):
        mock_controller = mocker.Mock(spec=PackageController)

        package_registry = PackageRegistry()
        operator_registry = PackageOperatorRegistry()

        package_context = PackageContext(
            controller=mock_controller,
            namespace="test_namespace",
            package_registry=package_registry,
            operator_registry=operator_registry,
        )

        package_name = "test_package"
        mock_package = mocker.Mock(spec=Package)
        mock_operator = mocker.Mock(spec=Type[PackageOperator])

        package_registry.register(package_name, mock_package)
        operator_registry.register(package_name, mock_operator)

        mock_controller.operate.return_value = mocker.Mock(spec=PackageOperator)

        result = package_context.use(package_name)

        assert result is not None
        assert isinstance(result, PackageOperator)

    def test_use_unregistered_package(self, mocker):
        mock_controller = mocker.Mock(spec=PackageController)

        namespace = "test_namespace"
        package_registry = PackageRegistry()
        operator_registry = PackageOperatorRegistry()

        context = PackageContext(
            controller=mock_controller,
            namespace=namespace,
            package_registry=package_registry,
            operator_registry=operator_registry,
        )

        package_name = "unregistered_package"

        with pytest.raises(
            RuntimeError, match=f"Package {package_name} is not registered"
        ):
            context.use(package_name)

    def test_returns_true_when_package_is_valid(self, mocker):
        mock_controller = mocker.Mock(spec=PackageController)

        namespace = "test_namespace"
        package_registry = PackageRegistry()
        operator_registry = PackageOperatorRegistry()

        context = PackageContext(
            controller=mock_controller,
            namespace=namespace,
            package_registry=package_registry,
            operator_registry=operator_registry,
        )

        package_name = "test_package"
        package = mocker.Mock(spec=Package)
        operator = mocker.Mock(spec=PackageOperator)

        package_registry.register(package_name, package)
        operator_registry.register(package_name, operator)

        result = context.has(package_name)

        assert result is True

    def test_package_returns_registered_package(self, mocker):
        mock_package = mocker.Mock()

        package_registry = PackageRegistry()
        package_registry.register("registered_package", mock_package)

        package_context = PackageContext(
            controller=mocker.Mock(),
            namespace="test_namespace",
            package_registry=package_registry,
            operator_registry=mocker.Mock(),
        )

        result = package_context.package("registered_package")

        assert result == mock_package

    def test_operator_returns_package_operator_when_registered(self, mocker):
        mock_package_operator = mocker.Mock(spec=PackageOperator)

        operator_registry = PackageOperatorRegistry()
        operator_registry.register("registered_package", mock_package_operator)

        context = PackageContext(
            controller=mocker.Mock(),
            namespace="test_namespace",
            package_registry=PackageRegistry(),
            operator_registry=operator_registry,
        )
        result = context.operator("registered_package")

        assert result == mock_package_operator


class TestPackageContextBuilder:
    def test_add_package_and_operator(self, mocker):
        controller = mocker.Mock(spec=PackageController)
        builder = PackageContextBuilder(controller, "test_namespace")

        package_name = "test_package"
        package_version = "1.0.0"
        package_operator = mocker.Mock(spec=PackageOperator)

        builder.add(package_name, package_version, package_operator)

        assert builder._package_registry.is_key_registered(package_name)
        assert builder._operator_registry.is_key_registered(package_name)

    def test_remove_unregistered_package(self, mocker):
        controller = mocker.Mock(spec=PackageController)
        builder = PackageContextBuilder(controller, "test_namespace")

        package_name = "unregistered_package"

        builder.remove(package_name)

        assert not builder._package_registry.is_key_registered(package_name)
        assert not builder._operator_registry.is_key_registered(package_name)

    def test_remove_package_and_operator(self, mocker):
        controller = mocker.Mock(spec=PackageController)
        builder = PackageContextBuilder(controller, "test_namespace")

        package_name = "test_package"
        package_version = "1.0.0"
        package_operator = mocker.Mock(spec=PackageOperator)

        builder.add(package_name, package_version, package_operator)

        builder.remove(package_name)

        assert not builder._package_registry.is_key_registered(package_name)
        assert not builder._operator_registry.is_key_registered(package_name)

    def test_build_package_context(self, mocker):
        controller = mocker.Mock(spec=PackageController)
        namespace = "test_namespace"
        builder = PackageContextBuilder(controller, namespace)

        package_name = "test_package"
        package_version = "1.0.0"
        package_operator = mocker.Mock(spec=PackageOperator)

        builder.add(package_name, package_version, package_operator)

        package_context = builder.build()

        assert package_context._controller == controller
        assert package_context.namespace() == namespace
        assert package_context._package_registry.is_key_registered(package_name)
        assert package_context._operator_registry.is_key_registered(package_name)

    def test_add_existing_operator(self, mocker):
        controller = mocker.Mock(spec=PackageController)
        builder = PackageContextBuilder(controller, "test_namespace")

        package_name = "test_package"
        package_version = "1.0.0"
        package_operator = mocker.Mock(spec=PackageOperator)

        builder.add(package_name, package_version, package_operator)

        new_operator = mocker.Mock(spec=PackageOperator)
        builder.add(package_name, package_version, new_operator)

        assert builder._package_registry.is_key_registered(package_name)
        assert builder._operator_registry.is_key_registered(package_name)
        assert builder._operator_registry.find_by_key(package_name) == package_operator
