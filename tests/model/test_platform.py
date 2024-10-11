import os
import platform

from pyckagist import PackagePlatform


class TestPackagePlatform:
    def test_current_platform_correct_system_architecture(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "linux"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "x86_64"

        pkg_platform = PackagePlatform.current_platform()

        assert pkg_platform.system() == "linux"
        assert pkg_platform.architecture() == "x86_64"

    def test_current_platform_missing_system_env_var(self):
        if "PYCKAGIST_PLATFORM_SYSTEM" in os.environ:
            del os.environ["PYCKAGIST_PLATFORM_SYSTEM"]
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "x86_64"

        pkg_platform = PackagePlatform.current_platform()

        assert pkg_platform.system() == platform.uname().system.lower()
        assert pkg_platform.architecture() == "x86_64"

    def test_system_method_correct_system_and_architecture(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "windows"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "x86"

        pkg_platform = PackagePlatform.current_platform()

        assert pkg_platform.system() == "windows"
        assert pkg_platform.architecture() == "x86"

    def test_eq_method_correctly_compares_instances(self):
        pkg_platform1 = PackagePlatform("linux", "x86_64")
        pkg_platform2 = PackagePlatform("linux", "x86_64")
        pkg_platform3 = PackagePlatform("linux", "arm64")
        pkg_platform4 = PackagePlatform("windows", "x86_64")

        assert pkg_platform1 == pkg_platform2
        assert pkg_platform1 != pkg_platform3
        assert pkg_platform1 != pkg_platform4

    def test_str_method_returns_correct_string_representation(self):
        pkg_platform = PackagePlatform("linux", "x86_64")

        assert str(pkg_platform) == "linux/x86_64"

    def test_current_platform_missing_architecture_variable(self):
        if "PYCKAGIST_PLATFORM_SYSTEM" in os.environ:
            del os.environ["PYCKAGIST_PLATFORM_SYSTEM"]
        if "PYCKAGIST_PLATFORM_ARCHITECTURE" in os.environ:
            del os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"]

        pkg_platform = PackagePlatform.current_platform()

        assert pkg_platform.system() == platform.uname().system.lower()
        assert pkg_platform.architecture() == platform.uname().machine.lower()

    def test_eq_handles_non_package_platform_objects(self):
        pkg_platform = PackagePlatform.current_platform()

        assert pkg_platform != "linux/x86_64"

    def test_current_platform_handles_unusual_values(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "unknown_system"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "unknown_architecture"

        pkg_platform = PackagePlatform.current_platform()

        assert pkg_platform.system() == "unknown_system"
        assert pkg_platform.architecture() == "unknown_architecture"

    def test_str_handles_unusual_system_and_architecture_strings(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "custom_system"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "custom_architecture"

        pkg_platform = PackagePlatform.current_platform()

        assert str(pkg_platform) == "custom_system/custom_architecture"
