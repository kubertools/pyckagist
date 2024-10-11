from pyckagist.model.platform import PackagePlatform


class RemotePackageDefinition:
    def __init__(self, name: str, source: str):
        self._name = name
        self._source = source

    def name(self) -> str:
        return self._name

    def source(self) -> str:
        return self._source

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return f"{self.source()}/{self.name()}"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.name() != other.name():
            return False
        if self.source() != other.source():
            return False

        return True


class RemotePackage:
    def __init__(
        self,
        definition: RemotePackageDefinition,
        version: str,
        platforms: list[PackagePlatform],
    ):
        self._definition = definition
        self._version = version
        self._platforms = platforms

    def definition(self) -> RemotePackageDefinition:
        return self._definition

    def name(self) -> str:
        return self._definition.name()

    def version(self) -> str:
        return self._version

    def supported_platforms(self) -> list[PackagePlatform]:
        return self._platforms

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.definition() != other.definition():
            return False
        if self.version() != other.version():
            return False
        if self.supported_platforms() != other.supported_platforms():
            return False

        return True

    def __str__(self):
        return f"{self.definition()} ({self.version()})"
