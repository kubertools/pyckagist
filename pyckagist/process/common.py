import shlex
import subprocess

from typing import Optional


class Process:
    def __init__(
        self,
        command: str,
        stdin: Optional[str] = None,
        environment: Optional[dict[str, str]] = None,
    ):
        self._command: str = command
        self._environment: Optional[dict[str, str]] = environment

        self._stdin: Optional[str] = stdin
        self._stdout: Optional[str] = None
        self._stderr: Optional[str] = None

        self._pd: Optional[subprocess.Popen] = None

    def command(self) -> str:
        return self._command

    def environment(self) -> dict[str, str]:
        if self._environment is None:
            return {}

        return self._environment

    def stdin(self) -> Optional[str]:
        if self._stdin is None:
            return None

        return self._stdin.strip()

    def stdout(self) -> Optional[str]:
        if self._stdout is None:
            return None

        return self._stdout.strip()

    def stderr(self) -> Optional[str]:
        if self._stderr is None:
            return None

        return self._stderr.strip()

    def exit_code(self) -> Optional[int]:
        if self._pd is None:
            return None

        return self._pd.poll()

    def is_finished(self) -> bool:
        return self.exit_code() is not None

    def run(self) -> None:
        try:
            split_cmd = shlex.split(self.command())

            self._pd = subprocess.Popen(
                split_cmd,
                env=self.environment(),
                encoding="utf-8",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self._stdout, self._stderr = self._pd.communicate(self.stdin())
        except Exception as e:
            self._stdout = ""
            self._stderr = str(e)

            raise ProcessError(self)


class ProcessError(RuntimeError):
    def __init__(self, process: Process):
        self._process = process

    def process(self) -> Process:
        return self._process

    def stderr(self) -> str:
        log = self._process.stderr()

        if log is None:
            return ""

        return log

    def exit_code(self) -> int:
        code = self._process.exit_code()

        if code is None:
            return -1

        return code

    def __str__(self):
        command = self.process().command()
        exit_node = self.process().exit_code()

        return f"{command} call has failed with the exit code {exit_node}"
