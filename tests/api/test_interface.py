import pytest

from pyckagist.api.interface import PackageInterface
from pyckagist.process.dispatcher import ProcessDispatcher
from pyckagist.process.handle import ProcessHandle


class TestPackageInterface:
    def test_initialize_with_valid_executable_and_dispatcher(self):
        executable_path = "/valid/path/to/executable"
        process_dispatcher = ProcessDispatcher("/cache/path")

        package_interface = PackageInterface(executable_path, process_dispatcher)

        assert package_interface._executable_path == executable_path
        assert package_interface._process_dispatcher == process_dispatcher

    def test_execute_with_invalid_executable_path(self, mocker):
        executable_path = "/invalid/path/to/executable"
        dispatcher = ProcessDispatcher("/cache/path")
        package_interface = PackageInterface(executable_path, dispatcher)

        mocker.patch("os.path.exists", return_value=False)

        with pytest.raises(FileNotFoundError):
            package_interface.execute("some_command")

    def test_execute_with_custom_environment(self, mocker):
        executable_path = "/path/to/executable"
        dispatcher = ProcessDispatcher("/cache/path")
        package_interface = PackageInterface(executable_path, dispatcher)

        custom_env = {"CUSTOM_VAR": "custom_value"}

        expected_process_handle = mocker.Mock(ProcessHandle)

        dispatch_mock = mocker.patch.object(ProcessDispatcher, "dispatch")
        dispatch_mock.return_value = expected_process_handle

        result = package_interface.execute("command", env=custom_env)

        dispatch_mock.assert_called_once_with(
            executable_path, "command", None, custom_env
        )
        assert result == expected_process_handle

    def test_set_and_get_env_var(self):
        executable_path = "/path/to/executable"
        dispatcher = ProcessDispatcher("/cache/path")
        package_interface = PackageInterface(executable_path, dispatcher)

        key = "TEST_KEY"
        value = "TEST_VALUE"

        result = package_interface.env_var(key, value)

        assert result == value
        assert package_interface.env_var(key) == value
        assert package_interface._environment[key] == value

    def test_set_and_get_env_vars(self):
        executable_path = "/path/to/executable"
        dispatcher = ProcessDispatcher("/cache/path")
        package_interface = PackageInterface(executable_path, dispatcher)

        assert package_interface.env_vars() == {}

        expected_environment = {"TEST": "test"}

        result = package_interface.env_vars(expected_environment)

        assert result == expected_environment
        assert package_interface.env_vars() == expected_environment
        assert package_interface._environment == expected_environment

        expected_environment = {"TEST1": "test1"}

        result = package_interface.env_vars(expected_environment)

        assert result == expected_environment
        assert package_interface.env_vars() == expected_environment
        assert package_interface._environment == expected_environment

    def test_update_and_get_env_vars(self):
        executable_path = "/path/to/executable"
        dispatcher = ProcessDispatcher("/cache/path")
        package_interface = PackageInterface(executable_path, dispatcher)

        assert package_interface.env_vars() == {}

        expected_environment = {"TEST": "test"}

        result = package_interface.env_vars(expected_environment, clear=False)

        assert result == expected_environment
        assert package_interface.env_vars() == expected_environment
        assert package_interface._environment == expected_environment

        expected_environment = {"TEST": "test", "TEST1": "test1"}

        result = package_interface.env_vars({"TEST1": "test1"}, clear=False)

        assert result == expected_environment
        assert package_interface.env_vars() == expected_environment
        assert package_interface._environment == expected_environment
