import os
import platform


class PackagePlatform:
    @staticmethod
    def current_platform() -> "PackagePlatform":
        system = (
            os.environ["PYCKAGIST_PLATFORM_SYSTEM"]
            if "PYCKAGIST_PLATFORM_SYSTEM" in os.environ
            else platform.uname().system.lower()
        )
        architecture = (
            os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"]
            if "PYCKAGIST_PLATFORM_ARCHITECTURE" in os.environ
            else platform.uname().machine.lower()
        )

        return PackagePlatform(system, architecture)

    def __init__(self, system: str, architecture: str) -> None:
        self._system = system
        self._architecture = architecture

    def system(self) -> str:
        return self._system

    def architecture(self) -> str:
        return self._architecture

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.system() != other.system():
            return False
        if self.architecture() != other.architecture():
            return False

        return True

    def __str__(self):
        return f"{self.system()}/{self.architecture()}"
