import json
import os

from pyckagist.storage.common import PackageManifest
from pyckagist.storage.entity.package import PackageEntity
from pyckagist.storage.entity.reference import ReferenceEntity


class FilePackageManifest(PackageManifest):
    def __init__(self, data_file: str) -> None:
        self._data_file = os.path.abspath(data_file)

        super().__init__()

    def _json_load(self, path, default=None):
        if not os.path.exists(self._data_file):
            return default

        with open(self._data_file, "r") as f:
            data = json.load(f)

            if path in data:
                return data[path]

            return default

    def _json_save(self, path, data):
        json_data = {}

        if os.path.exists(self._data_file):
            with open(self._data_file, "r") as f:
                json_data = json.load(f)

        with open(self._data_file, "w") as f:
            json_data[path] = data

            json.dump(json_data, f, indent=4)

    def _load_packages(self) -> dict[str, PackageEntity]:
        packages = {}

        for k, v in self._json_load("packages", {}).items():
            packages[k] = PackageEntity.deserialize(v)

        return packages

    def _save_packages(self, packages: dict[str, PackageEntity]) -> None:
        data = {}

        for k, v in packages.items():
            data[k] = v.serialize()

        self._json_save("packages", data)

    def _load_references(self) -> list[ReferenceEntity]:
        references = []

        for r in self._json_load("references", []):
            references.append(ReferenceEntity.deserialize(r))

        return references

    def _save_references(self, references: list[ReferenceEntity]) -> None:
        data = []

        for r in references:
            data.append(r.serialize())

        self._json_save("references", data)
