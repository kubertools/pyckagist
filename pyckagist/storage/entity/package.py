from typing_extensions import Self

from pyckagist.model.platform import PackagePlatform
from pyckagist.model.package import ExecutablePackage, PackageDefinition
from pyckagist.storage.entity.base import BaseEntity


class PackagePlatformEntity(BaseEntity):
    system: str
    architecture: str


class PackageEntity(BaseEntity):

    name: str
    version: str
    platform: PackagePlatformEntity

    executable_path: str
    executable_hash: str

    def to_executable_package(self) -> ExecutablePackage:
        return ExecutablePackage(
            definition=PackageDefinition(
                name=self.name,
                version=self.version,
                platform=PackagePlatform(
                    system=self.platform.system, architecture=self.platform.architecture
                ),
            ),
            executable_path=self.executable_path,
            executable_hash=self.executable_hash,
        )

    @classmethod
    def from_executable_package(cls, exec_package: ExecutablePackage) -> Self:
        return cls(
            name=exec_package.definition().name(),
            version=exec_package.definition().version(),
            platform=PackagePlatformEntity(
                system=exec_package.definition().platform().system(),
                architecture=exec_package.definition().platform().architecture(),
            ),
            executable_path=exec_package.executable_path(),
            executable_hash=exec_package.executable_hash(),
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name != other.name:
            return False
        if self.version != other.version:
            return False
        if self.platform.system != other.platform.system:
            return False
        if self.platform.architecture != other.platform.architecture:
            return False
        if self.executable_path != other.executable_path:
            return False
        if self.executable_hash != other.executable_hash:
            return False

        return True
