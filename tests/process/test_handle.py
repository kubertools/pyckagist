import pytest

from pyckagist.process.common import Process, ProcessError
from pyckagist.process.handle import ProcessHandle


class TestProcessHandle:
    def test_process_handle(self, mocker):
        process_mock = mocker.Mock(spec=Process)
        process_handle = ProcessHandle(process_mock)

        assert process_handle.process() == process_mock
        assert process_handle.exit_code() == process_mock.exit_code()
        assert process_handle.stderr() == process_mock.stderr()
        assert process_handle.stdout() == process_mock.stdout()

    def test_process_handle_invalid_process_exit_code(self, mocker):
        process_mock = mocker.Mock(spec=Process)
        process_mock.exit_code.return_value = None

        process_handle = ProcessHandle(process_mock)

        with pytest.raises(RuntimeError):
            process_handle.exit_code()

    def test_process_handle_print_stderr(self, mocker):
        mock_process = mocker.Mock()
        mock_process.stderr.return_value = "error line 1\nerror line 2\n"
        process_handle = ProcessHandle(mock_process)

        logger_mock = mocker.patch.object(process_handle, "_logger")

        process_handle.print_stderr()

        logger_mock.error.assert_any_call("error line 1")
        logger_mock.error.assert_any_call("error line 2")

    def test_process_handle_assert_exit_code_print_stderr(self, mocker):
        process_mock = mocker.Mock(spec=Process)
        process_mock.stderr.return_value = "error"
        process_mock.exit_code.return_value = 1337

        process_handle = ProcessHandle(process_mock)

        logger_mock = mocker.patch.object(process_handle, "_logger")

        with pytest.raises(ProcessError):
            process_handle.assert_exit_code(0)

        logger_mock.error.assert_any_call("error")

    def test_process_handle_assert_exit_code_raises_error_on_mismatch(self, mocker):
        process_mock = mocker.Mock(spec=Process)
        process_mock.stderr.return_value = "error"
        process_mock.exit_code.return_value = 1337

        process_handle = ProcessHandle(process_mock)

        process_handle.assert_exit_code(1337, print_stderr=False)
        with pytest.raises(ProcessError):
            process_handle.assert_exit_code(0, print_stderr=False)

    def test_process_handle_log_wrap(self, mocker):
        process_mock = mocker.Mock(spec=Process)
        process_mock.stdout.return_value = None

        process_handle = ProcessHandle(process_mock)

        assert process_handle.stdout() == ""
