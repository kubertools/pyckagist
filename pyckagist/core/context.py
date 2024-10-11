from typing import Type, Optional

from typing_extensions import Self

from pyckagist.api.operator import PackageOperator
from pyckagist.core.controller import PackageController
from pyckagist.model.package import Package
from pyckagist.registry.operator import PackageOperatorRegistry
from pyckagist.registry.package import PackageRegistry


class PackageContext:
    def __init__(
        self,
        controller: PackageController,
        namespace: str,
        package_registry: PackageRegistry,
        operator_registry: PackageOperatorRegistry,
    ) -> None:
        self._namespace: str = namespace

        self._controller: PackageController = controller
        self._package_registry: PackageRegistry = package_registry
        self._operator_registry: PackageOperatorRegistry = operator_registry

        self._package_cache: dict[str, PackageOperator] = {}

        self._controller.sync(self.namespace(), self.list())

    def namespace(self) -> str:
        return self._namespace

    def use(self, package_name: str) -> PackageOperator:
        package: Optional[Package] = self.package(package_name)
        operator: Optional[Type[PackageOperator]] = self.operator(package_name)

        if package is None or operator is None:
            raise RuntimeError(f"Package {package_name} is not registered")

        if package_name not in self._package_cache:
            self._package_cache[package_name] = self._controller.operate(
                self.namespace(), package, operator
            )

        return self._package_cache[package_name]

    def has(self, package_name: str) -> bool:
        package: Optional[Package] = self.package(package_name)
        operator: Optional[Type[PackageOperator]] = self.operator(package_name)

        return package is not None and operator is not None

    def list(self) -> list[Package]:
        return list(
            map(lambda x: x[0], self._package_registry.get_all_by_key().values())
        )

    def package(self, package_name: str) -> Optional[Package]:
        return self._package_registry.find_by_key(package_name)

    def operator(self, package_name: str) -> Optional[Type[PackageOperator]]:
        return self._operator_registry.find_by_key(package_name)


class PackageContextBuilder:
    def __init__(self, controller: PackageController, namespace: str):
        self._controller: PackageController = controller
        self._namespace: str = namespace

        self._package_registry: PackageRegistry = PackageRegistry()
        self._operator_registry: PackageOperatorRegistry = PackageOperatorRegistry()

    def add(
        self,
        package_name: str,
        package_version: str,
        package_operator: Type[PackageOperator],
    ) -> Self:
        package = Package(package_name, package_version)

        if not self._package_registry.is_key_registered(package_name):
            self._package_registry.register(package_name, package)

        if not self._operator_registry.is_key_registered(package_name):
            self._operator_registry.register(package_name, package_operator)

        return self

    def remove(self, package_name: str) -> Self:
        package = self._package_registry.find_by_key(package_name)
        if package is not None:
            self._package_registry.unregister(package_name, package)

        operator = self._operator_registry.find_by_key(package_name)
        if operator is not None:
            self._operator_registry.unregister(package_name, operator)

        return self

    def build(self) -> PackageContext:
        return PackageContext(
            self._controller,
            self._namespace,
            self._package_registry,
            self._operator_registry,
        )
