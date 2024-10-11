from unittest.mock import Mock

import pytest

from pyckagist.process.common import Process, ProcessError


class TestProcess:
    @staticmethod
    def _mock_popen(mocker) -> Mock:
        mock_popen = mocker.patch("subprocess.Popen")
        mock_popen_instance = mock_popen.return_value

        return mock_popen_instance

    def test_process_before_running(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = None

        process = Process(command="echo 'Hello World'")

        assert process.stdin() is None
        assert process.stdout() is None
        assert process.stderr() is None
        assert process.exit_code() is None
        assert process.is_finished() is False

    def test_process_runs_command_successfully(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 0

        process = Process(command="echo 'Hello World'")
        process.run()

        assert process.stdin() is None
        assert process.stdout() == "output"
        assert process.stderr() == "error"
        assert process.exit_code() == 0
        assert process.is_finished() is True

    def test_process_handles_empty_command_string(self, mocker):
        mock_popen = mocker.patch("subprocess.Popen")
        mock_popen.side_effect = ValueError("Empty command string")

        process = Process(command="")

        with pytest.raises(ProcessError):
            process.run()

    def test_process_exit_code(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 1

        process = Process(command="ls -l")
        process.run()

        assert process.exit_code() == 1

    def test_process_identifies_command_finished(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 0

        process = Process(command="ls")
        process.run()

        assert process.is_finished() is True

    def test_process_handles_large_stdin_data(self, mocker):
        large_input = "A" * 1000000

        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 0

        process = Process(command="echo 'Hello World'", stdin=large_input)
        process.run()

        assert process.stdin() == large_input
        assert process.stdout() == "output"
        assert process.stderr() == "error"
        assert process.exit_code() == 0
        assert process.is_finished() is True

    def test_process_handles_large_output(self, mocker):
        large_output = "A" * 1000000

        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = (large_output, "error")
        mock_popen_instance.poll.return_value = 0

        process = Process(command="some_large_command")
        process.run()

        assert process.stdin() is None
        assert process.stdout() == large_output
        assert process.stderr() == "error"
        assert process.exit_code() == 0
        assert process.is_finished() is True

    def test_process_handles_large_error(self, mocker):
        large_error = "A" * 1000000

        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", large_error)
        mock_popen_instance.poll.return_value = 1

        process = Process(command="some_large_command")
        process.run()

        assert process.stdin() is None
        assert process.stdout() == "output"
        assert process.stderr() == large_error
        assert process.exit_code() == 1
        assert process.is_finished() is True

    def test_strips_whitespace_from_logs(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("  output  ", "  error  ")
        mock_popen_instance.poll.return_value = 0

        process = Process(command="echo 'Hello World'")
        process.run()

        assert process.stdin() is None
        assert process.stdout() == "output"
        assert process.stderr() == "error"

    def test_process_handles_none_values(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 0

        process = Process(command="ls -l", stdin=None, environment=None)
        process.run()

        assert process.stdin() is None
        assert process.stdout() == "output"
        assert process.stderr() == "error"
        assert process.exit_code() == 0
        assert process.environment() == {}
        assert process.is_finished() is True

    def test_process_initializes_with_command_only(self, mocker):
        mocker.patch("subprocess.Popen")

        process = Process(command="ls -l")

        assert process.command() == "ls -l"

    def test_process_handles_failed_execution(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.side_effect = OSError("Command failed")
        mock_popen_instance.poll.return_value = None

        process = Process(command="invalid_command")

        with pytest.raises(ProcessError):
            process.run()

    def test_process_handles_command_with_env_vars(self, mocker):
        mock_popen_instance = self._mock_popen(mocker)

        mock_popen_instance.communicate.return_value = ("output", "error")
        mock_popen_instance.poll.return_value = 0

        env_vars = {"KEY": "VALUE"}
        process = Process(command="echo 'Hello World'", environment=env_vars)
        process.run()

        assert process.stdout() == "output"
        assert process.stderr() == "error"
        assert process.exit_code() == 0
        assert process.environment() == env_vars
        assert process.is_finished() is True


class TestProcessError:
    def test_process_error(self, mocker):
        mock_process = mocker.Mock(spec=Process)
        mock_process.stderr.return_value = "Some error"
        mock_process.exit_code.return_value = 1

        error = ProcessError(mock_process)

        assert error.process() == mock_process
        assert error.stderr() == "Some error"
        assert error.exit_code() == 1

        assert (
            str(error)
            == f"{error.process().command()} call has failed with the exit code {error.exit_code()}"
        )

    def test_process_error_with_none_values(self, mocker):
        mock_process = mocker.Mock(spec=Process)
        mock_process.stderr.return_value = None
        mock_process.exit_code.return_value = None

        error = ProcessError(mock_process)

        assert error.process() == mock_process
        assert error.stderr() == ""
        assert error.exit_code() == -1
