import os

from pyckagist.model.package import PackageDefinition
from pyckagist.storage.common import PackageStorage


class FilePackageStorage(PackageStorage):
    def __init__(self, storage_path) -> None:
        self._storage_path = os.path.abspath(storage_path)

        os.makedirs(self._storage_path, exist_ok=True)

    def resolve_package_path(self, package: PackageDefinition) -> str:
        name = package.name()
        version = package.version()
        platform = package.platform()

        if package.platform().system() == "windows":
            return os.path.abspath(
                f"{self._storage_path}/{name}-{version}-{platform.system()}-{platform.architecture()}.exe"
            )

        return os.path.abspath(
            f"{self._storage_path}/{name}-{version}-{platform.system()}-{platform.architecture()}"
        )

    def save_package(self, package: PackageDefinition, data: bytes) -> None:
        path = self.resolve_package_path(package)

        with open(path, "wb") as f:
            f.write(data)

        os.chmod(path, 0o755)

    def delete_package(self, package: PackageDefinition) -> None:
        path = self.resolve_package_path(package)

        if os.path.exists(path):
            os.remove(path)

    def load_package(self, package: PackageDefinition) -> bytes:
        path = self.resolve_package_path(package)

        with open(path, "rb") as f:
            return f.read()

    def package_exists(self, package: PackageDefinition) -> bool:
        path = self.resolve_package_path(package)

        return os.path.exists(path)
