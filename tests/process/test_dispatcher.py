from unittest.mock import Mock

import pytest

from pyckagist.process.dispatcher import ProcessDispatcher
from pyckagist.process.handle import ProcessHandle


class TestProcessDispatcher:
    @staticmethod
    def _mock_popen(mocker) -> Mock:
        mock_popen = mocker.patch("subprocess.Popen")
        mock_popen_instance = mock_popen.return_value

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 0

        return mock_popen_instance

    def test_dispatch_valid_executable_and_command(self, mocker):
        popen_mock = self._mock_popen(mocker)

        mocker.patch("os.path.exists", return_value=True)

        dispatcher = ProcessDispatcher("/fake/cache/path")
        result = dispatcher.dispatch("/fake/executable", "fake_command")

        assert isinstance(result, ProcessHandle)

        popen_mock.communicate.assert_called_once()

        assert result.exit_code() == 0
        assert result.process().command() == "/fake/executable fake_command"

    def test_dispatch_non_existent_executable(self, mocker):
        mocker.patch("os.path.exists", return_value=False)

        from pyckagist.process.dispatcher import ProcessDispatcher

        dispatcher = ProcessDispatcher("/fake/cache/path")

        with pytest.raises(FileNotFoundError) as excinfo:
            dispatcher.dispatch("/non/existent/executable", "fake_command")

        assert str(excinfo.value) == "Executable not found: /non/existent/executable"

    def test_dispatch_valid_executable_command_and_stdin(self, mocker):
        self._mock_popen(mocker)

        mocker.patch("os.path.exists", return_value=True)

        dispatcher = ProcessDispatcher("/fake/cache/path")
        result = dispatcher.dispatch(
            "/fake/executable", "fake_command", stdin="fake_stdin"
        )

        assert result.exit_code() == 0
        assert result.process().stdin() == "fake_stdin"
        assert result.process().command() == "/fake/executable fake_command"

    def test_dispatch_cache_environment_variables(self, mocker):
        self._mock_popen(mocker)

        mocker.patch("os.path.exists", return_value=True)

        dispatcher = ProcessDispatcher("/fake/cache/path")
        result = dispatcher.dispatch("/fake/executable", "fake_command")

        assert result.exit_code() == 0
        assert result.process().environment() == {
            "HOME": "/fake/cache/path",
            "TEMP": "/fake/cache/path",
            "APPDATA": "/fake/cache/path",
            "XDG_CACHE_HOME": "/fake/cache/path",
        }
