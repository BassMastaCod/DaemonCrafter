import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Any

from str_case_util import Case

from daemoncrafter.executables import Executable


TIMEOUT = 10


def wait_for(condition: callable, expected: Any = True):
    start_time = time.time()
    while condition() != expected:
        if time.time() - start_time > TIMEOUT:
            raise TimeoutError(f'Condition failed to meet expected result within time limit.')
        time.sleep(0.5)


class DaemonProvider(ABC):
    """Abstract interface for OS-specific service backends."""
    def __init__(self, name: str, executable: Path|Executable):
        self.display_name = name
        self.service_name = Case.SNAKE_CASE.format(name)
        self.executable = executable

    @property
    def working_directory(self) -> Path:
        """Returns the path to the working directory."""
        return self.executable.parent

    @property
    @abstractmethod
    def configuration(self) -> Path:
        """Returns the path to the service configuration file."""
        pass

    @abstractmethod
    def _command(self, action: str, *args: str) -> list[str]:
        """Returns the command to execute given the arguments."""
        pass

    def _exec(self, action: str, *args: str, raise_on_failure: bool = True) -> subprocess.CompletedProcess:
        """Runs a system command with optional arguments.

        :param action: The main action to take (e.g., start, stop, enable)
        :param args: The arguments to accompany the action
        :param raise_on_failure: Whether to raise a CalledProcessError on non-zero exit status (default: True)
        """
        return subprocess.run(self._command(action, *args), capture_output=True, text=True, check=raise_on_failure)

    def _check(self, action: str, *args: str, code: int = 0) -> bool:
        """Runs a systemctl with a bool result instead of an error.

        See :meth:`_exec`

        :param action: The systemctl action to take (e.g., is-active, is-enabled)
        :param args: The arguments to pass to systemctl
        :param code: The expected return code (default: 0)
        :returns: True if the command was successful (or matched the expected code), False otherwise
        """
        return self._exec(action, *args, raise_on_failure=False).returncode == code

    @abstractmethod
    def is_installed(self) -> bool:
        """See :meth:`DaemonCrafter.is_installed`."""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """See :meth:`DaemonCrafter.is_running`."""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """See :meth:`DaemonCrafter.is_enabled`."""
        pass

    def install(self, **command_args) -> None:
        """See :meth:`DaemonCrafter.install`."""
        self._create_service_files(**command_args)
        try:
            self._register_service()
        except:
            self._remove_service_files()
            raise

    @abstractmethod
    def _create_service_files(self, **command_args) -> None:
        """Creates/Configures the files supporting the daemon."""
        pass

    @abstractmethod
    def _register_service(self) -> None:
        """Registers the daemon with the OS's service manager."""
        pass

    def uninstall(self) -> None:
        """See :meth:`DaemonCrafter.uninstall`."""
        self.stop()
        self.disable()
        self._remove_service_files()
        self._unregister_service()

    def _remove_service_files(self) -> None:
        """Removes the service files created by :meth:`_create_service_files`."""
        self.configuration.unlink(missing_ok=True)

    @abstractmethod
    def _unregister_service(self) -> None:
        """Deconfigures the daemon from the OS's service manager."""
        pass

    def start(self) -> None:
        """See :meth:`DaemonCrafter.start`."""
        self._exec('start')

    def stop(self) -> None:
        """See :meth:`DaemonCrafter.stop`."""
        self._exec('stop')

    def enable(self) -> None:
        """See :meth:`DaemonCrafter.enable`."""
        self._exec('enable')

    def disable(self) -> None:
        """See :meth:`DaemonCrafter.disable`."""
        self._exec('disable')

    @abstractmethod
    def get_logs(self, lines: int = 50, since: Optional[str] = None, until: Optional[str] = None) -> list[str]:
        """See :meth:`DaemonCrafter.get_logs`."""
        pass
