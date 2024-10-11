from typing import Optional

from pyckagist.api.source import PackageSource
from pyckagist.core.context import PackageContextBuilder
from pyckagist.core.controller import PackageController
from pyckagist.core.remote import RemoteManager
from pyckagist.core.resolver import PackageResolver
from pyckagist.model.platform import PackagePlatform
from pyckagist.process.dispatcher import ProcessDispatcher
from pyckagist.registry.source import PackageSourceRegistry
from pyckagist.storage.filesystem.manifest import FilePackageManifest
from pyckagist.storage.filesystem.storage import FilePackageStorage
from pyckagist.storage.manager import PackageLifecycleManager


class PackageManager:
    def __init__(self, controller: PackageController) -> None:
        self._controller = controller

    def wrap(self, namespace: str) -> PackageContextBuilder:
        return PackageContextBuilder(self._controller, namespace)

    def controller(self):
        return self._controller


class PackageManagerBuilder:
    def __init__(self) -> None:
        self._base_path: Optional[str] = None

        self._offline_mode: bool = False
        self._package_sources: list[PackageSource] = []
        self._package_platform: Optional[PackagePlatform] = None

    def base_path(self, base_path: str):
        self._base_path = base_path
        return self

    def offline_mode(self, offline_mode: bool):
        self._offline_mode = offline_mode
        return self

    def package_source(self, source: PackageSource):
        self._package_sources.append(source)
        return self

    def package_platform(self, platform: PackagePlatform):
        self._package_platform = platform
        return self

    def build(self) -> PackageManager:
        if not self._base_path:
            raise ValueError("Base path is not set")

        package_platform = self._package_platform or PackagePlatform.current_platform()

        process_dispatcher = ProcessDispatcher(f"{self._base_path}/cache")

        package_storage = FilePackageStorage(f"{self._base_path}/bin")
        package_manifest = FilePackageManifest(f"{self._base_path}/packages.json")

        package_lifecycle_manager = PackageLifecycleManager(
            package_manifest, package_storage
        )

        remote_manager = None
        if not self._offline_mode:
            source_registry = PackageSourceRegistry()
            for source in self._package_sources:
                source_registry.register(source.name(), source)

            remote_manager = RemoteManager(source_registry)

        package_resolver = PackageResolver(
            package_platform, package_lifecycle_manager, remote_manager
        )
        controller = PackageController(
            package_resolver, process_dispatcher, package_lifecycle_manager
        )

        return PackageManager(controller)
