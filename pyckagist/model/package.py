import hashlib
import os

from pyckagist.model.platform import PackagePlatform


class Package:
    def __init__(self, name: str, version: str):
        self._name = name
        self._version = version

    def name(self) -> str:
        return self._name

    def version(self) -> str:
        return self._version

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name() != other.name():
            return False
        if self.version() != other.version():
            return False

        return True

    def __str__(self):
        return f"{self.name()} ({self.version()})"

    def __hash__(self):
        return hash(str(self))


class PackageDefinition:
    def __init__(self, name: str, version: str, platform: PackagePlatform):
        self._name = name
        self._version = version
        self._platform = platform

    def name(self) -> str:
        return self._name

    def version(self) -> str:
        return self._version

    def platform(self) -> PackagePlatform:
        return self._platform

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name() != other.name():
            return False
        if self.version() != other.version():
            return False
        if self.platform() != other.platform():
            return False

        return True

    def __str__(self):
        return f"{self.name()}@{self.platform()} ({self.version()})"


class ExecutablePackage:
    def __init__(
        self, definition: PackageDefinition, executable_path: str, executable_hash: str
    ):
        self._definition = definition
        self._executable_path = executable_path
        self._executable_hash = executable_hash

    def definition(self) -> PackageDefinition:
        return self._definition

    def executable_path(self) -> str:
        return self._executable_path

    def executable_hash(self) -> str:
        return self._executable_hash

    def validate(self) -> bool:
        if not os.path.exists(self._executable_path):
            return False

        with open(self._executable_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest() == self._executable_hash

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.definition() != other.definition():
            return False
        if self.executable_path() != other.executable_path():
            return False
        if self.executable_hash() != other.executable_hash():
            return False

        return True

    def __str__(self):
        return str(self.definition())

    @staticmethod
    def hash(data: bytes):
        return hashlib.sha256(data).hexdigest()
