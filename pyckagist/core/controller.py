import logging
from typing import Type, TypeVar, Optional

from pyckagist import PackageOperator
from pyckagist.api.interface import PackageInterface
from pyckagist.core.resolver import PackageResolver
from pyckagist.model.package import Package, ExecutablePackage
from pyckagist.process.dispatcher import ProcessDispatcher
from pyckagist.storage.manager import PackageLifecycleManager

PACKAGE_OPERATOR = TypeVar("PACKAGE_OPERATOR", bound=PackageOperator)


class PackageController:
    def __init__(
        self,
        package_resolver: PackageResolver,
        process_dispatcher: ProcessDispatcher,
        package_lifecycle_manager: PackageLifecycleManager,
    ):
        self._logger = logging.getLogger("Pyckagist")

        self._package_resolver = package_resolver
        self._process_dispatcher = process_dispatcher
        self._package_lifecycle_manager = package_lifecycle_manager

    def _find_locally(self, package: Package) -> Optional[ExecutablePackage]:
        definition = self._package_resolver.to_package_definition(package)

        exec_package = self._package_lifecycle_manager.find(definition)
        if exec_package is None:
            return None
        if not exec_package.validate():
            return None

        return exec_package

    def is_installed(self, package: Package) -> bool:
        return self._find_locally(package) is not None

    def install(self, namespace: str, package: Package) -> None:
        executable_package = self._find_locally(package)
        if executable_package is not None:
            self._logger.info(f"Package {package} is already installed")
        else:
            executable_package = self._package_resolver.resolve_package(package)

            self._logger.info(f"Installed package {package}")

        self._package_lifecycle_manager.register(namespace, executable_package)

    def uninstall(self, namespace: str, package: Package) -> None:
        exec_package = self._find_locally(package)
        if exec_package is None:
            raise RuntimeError(
                f"Package {package} is not installed in the namespace {namespace}"
            )

        self._package_lifecycle_manager.unregister(namespace, exec_package)
        self._package_lifecycle_manager.cleanup()

        self._logger.info(f"Uninstalled package {package}")

    def operate(
        self, namespace: str, package: Package, operator: Type[PACKAGE_OPERATOR]
    ) -> PACKAGE_OPERATOR:
        self.install(namespace, package)

        exec_package = self._find_locally(package)
        if exec_package is None:
            raise RuntimeError(
                f"Package {package} is broken and needs to be reinstalled."
            )

        package_interface = PackageInterface(
            exec_package.executable_path(), self._process_dispatcher
        )

        return operator.instantiate(package_interface)

    def sync(self, namespace: str, packages: list[Package]) -> None:
        definitions = []
        for package in packages:
            definition = self._package_resolver.to_package_definition(package)

            definitions.append(definition)

        self._package_lifecycle_manager.sync(namespace, definitions)
