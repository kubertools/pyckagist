import re
from typing import Optional

from typing_extensions import Self


class PackageVersion:
    def __init__(self, major, minor, patch) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other) -> bool:
        other = self._type_check(other, soft=True)
        if other is None:
            return False

        if self.major != other.major:
            return False
        if self.minor != other.minor:
            return False
        if self.patch != other.patch:
            return False

        return True

    def __lt__(self, other) -> bool:
        other = self._type_check(other)

        return self._is_less(
            [self.major, self.minor, self.patch],
            [other.major, other.minor, other.patch],
        )

    def __gt__(self, other) -> bool:
        other = self._type_check(other)

        return self._is_greater(
            [self.major, self.minor, self.patch],
            [other.major, other.minor, other.patch],
        )

    def __le__(self, other) -> bool:
        other = self._type_check(other)

        return self == other or self < other

    def __ge__(self, other) -> bool:
        other = self._type_check(other)

        return self == other or self > other

    def _type_check(self, other, soft=False) -> Optional[Self]:
        if isinstance(other, self.__class__):
            return other
        if isinstance(other, str):
            return self.parse(other)

        if soft:
            return None

        raise ValueError(f"Cannot compare {self.__class__} with {type(other)}")

    @staticmethod
    def _is_greater(a: list[int], b: list[int]) -> bool:
        l = max(len(a), len(b))

        for i in range(l):
            a_val = a[i] if i < len(a) else 0
            b_val = b[i] if i < len(b) else 0

            if a_val > b_val:
                return True

        return False

    @staticmethod
    def _is_less(a: list[int], b: list[int]) -> bool:
        l = max(len(a), len(b))

        for i in range(l):
            a_val = a[i] if i < len(a) else 0
            b_val = b[i] if i < len(b) else 0

            if a_val < b_val:
                return True

        return False

    @classmethod
    def parse(cls, version_str: str) -> Self:
        version_str = re.sub(r"[^-\d.]", "", version_str)

        version_data = version_str.split(".")

        if len(version_data) == 1:
            return cls(int(version_data[0]), 0, 0)

        if len(version_data) == 2:
            return cls(int(version_data[0]), int(version_data[1]), 0)

        if len(version_data) == 3:
            return cls(int(version_data[0]), int(version_data[1]), int(version_data[2]))

        raise ValueError(f"Invalid version string: {version_str}")
