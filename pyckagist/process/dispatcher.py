import logging
import os
from typing import Optional

from pyckagist.process.common import Process
from pyckagist.process.handle import ProcessHandle


class ProcessDispatcher:
    def __init__(self, cache_path: str):
        self._logger = logging.getLogger("process-dispatcher")

        self._cache_path = cache_path

    def dispatch(
        self,
        executable: str,
        command: str,
        stdin: Optional[str] = None,
        environment: Optional[dict[str, str]] = None,
    ) -> ProcessHandle:
        if os.path.exists(executable) is False:
            raise FileNotFoundError(f"Executable not found: {executable}")

        if environment is None:
            environment = {}

        environment["HOME"] = self._cache_path
        environment["TEMP"] = self._cache_path
        environment["APPDATA"] = self._cache_path
        environment["XDG_CACHE_HOME"] = self._cache_path

        self._logger.debug("Executing command: %s", command)

        process = Process(executable + " " + command, stdin, environment)
        process.run()

        return ProcessHandle(process)
