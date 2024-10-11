import os

from pyckagist import PackagePlatform


class TestPackagePlatform:
    def test_current_platform_correct_system_architecture(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "linux"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "x86_64"

        platform = PackagePlatform.current_platform()

        assert platform.system() == "linux"
        assert platform.architecture() == "x86_64"

    def test_current_platform_missing_system_env_var(self):
        if "PYCKAGIST_PLATFORM_SYSTEM" in os.environ:
            del os.environ["PYCKAGIST_PLATFORM_SYSTEM"]
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "x86_64"

        platform = PackagePlatform.current_platform()

        assert platform.system() == os.uname().sysname.lower()
        assert platform.architecture() == "x86_64"

    def test_system_method_correct_system_and_architecture(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "windows"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "x86"

        platform = PackagePlatform.current_platform()

        assert platform.system() == "windows"
        assert platform.architecture() == "x86"

    def test_eq_method_correctly_compares_instances(self):
        platform1 = PackagePlatform("linux", "x86_64")
        platform2 = PackagePlatform("linux", "x86_64")
        platform3 = PackagePlatform("linux", "arm64")
        platform4 = PackagePlatform("windows", "x86_64")

        assert platform1 == platform2
        assert platform1 != platform3
        assert platform1 != platform4

    def test_str_method_returns_correct_string_representation(self):
        platform = PackagePlatform("linux", "x86_64")

        assert str(platform) == "linux/x86_64"

    def test_current_platform_missing_architecture_variable(self):
        if "PYCKAGIST_PLATFORM_SYSTEM" in os.environ:
            del os.environ["PYCKAGIST_PLATFORM_SYSTEM"]
        if "PYCKAGIST_PLATFORM_ARCHITECTURE" in os.environ:
            del os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"]

        platform = PackagePlatform.current_platform()

        assert platform.system() == os.uname().sysname.lower()
        assert platform.architecture() == os.uname().machine.lower()

    def test_eq_handles_non_package_platform_objects(self):
        platform = PackagePlatform.current_platform()

        assert platform != "linux/x86_64"

    def test_current_platform_handles_unusual_values(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "unknown_system"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "unknown_architecture"

        platform = PackagePlatform.current_platform()

        assert platform.system() == "unknown_system"
        assert platform.architecture() == "unknown_architecture"

    def test_str_handles_unusual_system_and_architecture_strings(self):
        os.environ["PYCKAGIST_PLATFORM_SYSTEM"] = "custom_system"
        os.environ["PYCKAGIST_PLATFORM_ARCHITECTURE"] = "custom_architecture"

        platform = PackagePlatform.current_platform()

        assert str(platform) == "custom_system/custom_architecture"
