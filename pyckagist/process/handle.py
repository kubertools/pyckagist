import logging
from typing import Optional

from pyckagist.process.common import ProcessError, Process


class ProcessHandle:
    def __init__(self, process: Process):
        self._logger = logging.getLogger("process")

        self._process = process

    def process(self) -> Process:
        return self._process

    def assert_exit_code(
        self, expected_exit_code: int, print_stderr=True
    ) -> "ProcessHandle":
        if self.exit_code() == expected_exit_code:
            return self

        if print_stderr:
            self.print_stderr()

        raise ProcessError(self._process)

    def print_stderr(self) -> "ProcessHandle":
        for line in self.stderr().splitlines():
            self._logger.error(line.strip())

        return self

    def stderr(self) -> str:
        return self._wrap(self._process.stderr())

    def stdout(self) -> str:
        return self._wrap(self._process.stdout())

    def exit_code(self) -> int:
        code = self._process.exit_code()
        if code is None:
            raise RuntimeError("ProcessHandle cannot represent an unfinished process")

        return code

    @staticmethod
    def _wrap(str_in: Optional[str]):
        if str_in is None:
            return ""
        return str_in
