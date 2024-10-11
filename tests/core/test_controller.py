import re

import pytest

from pyckagist import Package
from pyckagist.core.controller import PackageController
from pyckagist.core.resolver import PackageResolver
from pyckagist.process.dispatcher import ProcessDispatcher
from pyckagist.storage.manager import PackageLifecycleManager


class TestPackageController:
    def test_install_package_successfully(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package = Package("test_package", "1.0.0")
        namespace = "test_namespace"

        package_resolver.to_package_definition.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value = None
        package_resolver.resolve_package.return_value = mocker.Mock()

        package_controller.install(namespace, package)

        package_resolver.resolve_package.assert_called_once_with(package)
        package_lifecycle_manager.register.assert_called_once()

    def test_uninstall_package(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        executable_package = mocker.Mock()
        package_resolver.to_package_definition.return_value = mocker.Mock()

        package = Package("test_package", "1.0.0")
        namespace = "test_namespace"

        package_lifecycle_manager.find.return_value = executable_package

        package_controller.uninstall(namespace, package)

        package_lifecycle_manager.unregister.assert_called_once_with(
            namespace, executable_package
        )
        package_lifecycle_manager.cleanup.assert_called_once()

    def test_uninstall_package_not_installed(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package = Package("test_package", "1.0.0")
        namespace = "test_namespace"

        package_lifecycle_manager.find.return_value = None

        with pytest.raises(
            RuntimeError,
            match=re.escape(
                f"Package {package} is not installed in the namespace {namespace}"
            ),
        ):
            package_controller.uninstall(namespace, package)

    def test_identify_package_installed(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package = Package("test_package", "1.0.0")

        package_resolver.to_package_definition.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value = mocker.Mock()

        is_installed = package_controller.is_installed(package)

        assert is_installed

    def test_identify_package_installed_but_invalid(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package_resolver.to_package_definition.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value = mocker.Mock()

        package_lifecycle_manager.find.return_value.validate.return_value = False

        package = Package("test_package", "1.0.0")

        is_installed = package_controller.is_installed(package)

        assert not is_installed

    def test_operate_package_successfully(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package = Package("test_package", "1.0.0")
        namespace = "test_namespace"
        operator = mocker.Mock()

        package_resolver.to_package_definition.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value.validate.return_value = True
        package_lifecycle_manager.find.return_value.executable_path.return_value = (
            "test_executable_path"
        )
        process_dispatcher.dispatch.return_value = mocker.Mock()

        result = package_controller.operate(namespace, package, operator)

        assert result == operator.instantiate.return_value

    def test_sync_package_definitions(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        namespace = "test_namespace"
        packages = [
            Package("test_package1", "1.0.0"),
            Package("test_package2", "2.0.0"),
        ]

        definitions = [mocker.call(package) for package in packages]

        package_resolver.to_package_definition.side_effect = definitions
        package_controller.sync(namespace, packages)

        package_lifecycle_manager.sync.assert_called_once_with(namespace, definitions)

    def test_handle_invalid_package_definitions_gracefully(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package = Package("invalid_package", "1.0.0")
        namespace = "test_namespace"

        package_resolver.to_package_definition.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value = None
        package_resolver.resolve_package.side_effect = RuntimeError(
            "Invalid package definition"
        )

        with pytest.raises(RuntimeError):
            package_controller.install(namespace, package)

        package_resolver.resolve_package.assert_called_once_with(package)

    def test_validate_executable_package(self, mocker):
        package_resolver = mocker.Mock(spec=PackageResolver)
        process_dispatcher = mocker.Mock(spec=ProcessDispatcher)
        package_lifecycle_manager = mocker.Mock(spec=PackageLifecycleManager)
        package_controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        package_resolver.to_package_definition.return_value = mocker.Mock()

        executable_package = mocker.Mock()
        package_lifecycle_manager.find.return_value = executable_package
        executable_package.validate.return_value = True

        result = package_controller._find_locally(mocker.Mock)

        assert result == executable_package

    def test_package_is_broken(self, mocker):
        namespace = "test_namespace"
        package = Package("test_package", "1.0")

        operator = mocker.Mock()
        package_resolver = mocker.Mock()
        package_lifecycle_manager = mocker.Mock()
        process_dispatcher = mocker.Mock()

        package_resolver.to_package_definition.return_value = mocker.Mock()
        package_lifecycle_manager.find.return_value = None

        controller = PackageController(
            package_resolver=package_resolver,
            package_lifecycle_manager=package_lifecycle_manager,
            process_dispatcher=process_dispatcher,
        )

        with pytest.raises(
            RuntimeError,
            match=re.escape(
                "Package test_package (1.0) is broken and needs to be reinstalled."
            ),
        ):
            controller.operate(namespace, package, operator)
