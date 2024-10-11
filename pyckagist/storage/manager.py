import hashlib
from typing import Optional

from pyckagist.model.package import ExecutablePackage, PackageDefinition
from pyckagist.storage.common import PackageManifest, PackageStorage
from pyckagist.storage.entity.package import PackageEntity, PackagePlatformEntity
from pyckagist.storage.entity.reference import ReferenceEntity


class PackageLifecycleManager:
    def __init__(self, manifest: PackageManifest, storage: PackageStorage):
        self._manifest = manifest
        self._storage = storage

    def register(self, namespace: str, package: ExecutablePackage):
        key = self._to_package_key(package.definition())

        reference = ReferenceEntity(
            namespace=namespace,
            package=key,
        )
        if reference not in self._manifest.references():
            self._manifest.references().append(reference)

        self._manifest.packages()[key] = PackageEntity.from_executable_package(package)
        self._manifest.save()

    def unregister(self, namespace: str, package: ExecutablePackage):
        key = self._to_package_key(package.definition())

        reference = ReferenceEntity(
            namespace=namespace,
            package=key,
        )

        if reference in self._manifest.references():
            self._manifest.references().remove(reference)
            self._manifest.save()

        self.cleanup()

    def sync(self, namespace: str, definitions: list[PackageDefinition]) -> None:
        keys = list(map(self._to_package_key, definitions))

        for reference in self._manifest.references().copy():
            if reference.namespace != namespace:
                continue
            if reference.package not in keys:
                self._manifest.references().remove(reference)

        self.cleanup()
        self._manifest.save()

    def save(self, definition: PackageDefinition, data: bytes) -> ExecutablePackage:
        key = self._to_package_key(definition)

        self._storage.save_package(definition, data)

        self._manifest.packages()[key] = PackageEntity(
            name=definition.name(),
            version=definition.version(),
            platform=PackagePlatformEntity(
                system=definition.platform().system(),
                architecture=definition.platform().architecture(),
            ),
            executable_path=self._storage.resolve_package_path(definition),
            executable_hash=ExecutablePackage.hash(data),
        )
        self._manifest.save()

        return self._manifest.packages()[key].to_executable_package()

    def delete(self, definition: PackageDefinition) -> None:
        key = self._to_package_key(definition)

        if self._storage.package_exists(definition):
            self._storage.delete_package(definition)

        if key in self._manifest.packages():
            self._manifest.packages().pop(key)
            self._manifest.save()

    def list(self) -> list[ExecutablePackage]:
        packages = []

        references = list(map(lambda x: x.package, self._manifest.references()))
        for reference in references:
            if reference in self._manifest.packages():
                packages.append(
                    self._manifest.packages()[reference].to_executable_package()
                )

        return packages

    def find(self, definition: PackageDefinition) -> Optional[ExecutablePackage]:
        key = self._to_package_key(definition)

        if key not in self._manifest.packages():
            return None

        package = self._manifest.packages()[key].to_executable_package()
        if package.definition().platform() != definition.platform():
            self.delete(package.definition())
            return None

        return package

    def cleanup(self) -> None:
        references = list(map(lambda x: x.package, self._manifest.references()))

        for key, package in self._manifest.packages().copy().items():
            if key not in references:
                self.delete(package.to_executable_package().definition())

    def reset(self) -> None:
        self._manifest.references().clear()
        self.cleanup()

        self._manifest.save()

    @staticmethod
    def _to_package_key(definition: PackageDefinition) -> str:
        v = definition.name() + "/" + definition.version()

        return hashlib.sha1(v.encode()).hexdigest()
