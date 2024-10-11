from typing import Optional

from pyckagist.process.dispatcher import ProcessDispatcher
from pyckagist.process.handle import ProcessHandle


class PackageInterface:
    def __init__(
        self, executable_path: str, process_dispatcher: ProcessDispatcher
    ) -> None:
        self._executable_path: str = executable_path
        self._process_dispatcher: ProcessDispatcher = process_dispatcher

        self._environment: dict[str, str] = {}

    def execute(
        self,
        command: str,
        stdin: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
    ) -> ProcessHandle:
        environment = {}

        if self._environment is not None:
            environment.update(self._environment)
        if env is not None:
            environment.update(env)

        return self._process_dispatcher.dispatch(
            self._executable_path, command, stdin, environment
        )

    def env_var(self, key: str, value: Optional[str] = None) -> Optional[str]:
        if value is not None:
            self._environment[key] = value

        return self._environment.get(key)

    def env_vars(
        self, env: Optional[dict[str, str]] = None, clear: bool = True
    ) -> dict[str, str]:
        if env is None:
            return self._environment

        if clear:
            self._environment.clear()
        self._environment.update(env)

        return self._environment
