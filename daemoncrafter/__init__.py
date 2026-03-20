import platform
from pathlib import Path
from typing import Optional

from daemoncrafter.linux import SystemdProvider
from daemoncrafter.providers import DaemonProvider
from daemoncrafter.windows import SCMProvider


class DaemonCrafter:
    """Manages the lifecycle of a system service, agnostic of the underlying OS.

    Unless specified, the backend provider is automatically selected based on the current OS.
    """
    def __init__(self, name: str, executable: Path, backend: Optional[type[DaemonProvider]] = None):
        if not backend:
            match platform.system().lower():
                case 'linux':
                    backend = SystemdProvider
                case 'windows':
                    backend = SCMProvider
                case _:
                    raise RuntimeError('Unsupported OS')
        self.backend = backend(name, executable)
        self.name = name
        self.executable = executable

    def is_installed(self) -> bool:
        """Checks if the daemon is currently installed.

        See :meth:`install`

        :return: True if the daemon is installed, False otherwise
        """
        return self.backend.is_installed()

    def install(self) -> None:
        """Installs an artifact as a daemon.

        An independent, system-level service is created for the artifact.
        """
        return self.backend.install()

    def uninstall(self) -> None:
        """Removes the daemon for the artifact.

        The artifact directory and virtual environment remain untouched.
        """
        self.backend.uninstall()

    def is_running(self) -> bool:
        """Checks if the daemon is currently running.

        See :meth:`start` and :meth:`enable`

        :return: True if the daemon is running, False otherwise
        """
        return self.backend.is_running()

    def start(self) -> None:
        """Manually starts the installed daemon."""
        self.backend.start()

    def stop(self) -> None:
        """Manually stops the running daemon."""
        self.backend.stop()

    def restart(self) -> None:
        """Manually stops the running daemon and then starts it again."""
        self.stop()
        self.start()

    def is_enabled(self) -> bool:
        """Checks if the daemon is enabled to start automatically at boot.

        :return: True if the daemon will start at boot, False otherwise
        """
        return self.backend.is_enabled()

    def enable(self) -> None:
        """Configures the installed daemon to start automatically at boot."""
        self.backend.enable()

    def disable(self) -> None:
        """Configures the installed daemon to not start automatically at boot."""
        self.backend.disable()

    def get_logs(self, lines: int = 50, since: Optional[str] = None, until: Optional[str] = None) -> list[str]:
        """Retrieves the logs for the daemon execution.

        :param lines: The number of log lines to retrieve (default: 50)
        :param since: Only return logs after this time
        :param until: Only return logs before this time
        :return: A list of log lines
        """
        return self.backend.get_logs(lines, since, until)
