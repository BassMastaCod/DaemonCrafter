import subprocess
from pathlib import Path
from typing import Optional

from daemoncrafter.providers import DaemonProvider


SERVICE_DIR = Path('/etc/systemd/system')


class SystemdProvider(DaemonProvider):
    @property
    def configuration(self) -> Path:
        return SERVICE_DIR / f'{self.service_name}.xml'

    def _command(self, action: str, *args: str) -> list[str]:
        return ['systemctl', action, *args, self.service_name]

    def is_installed(self) -> bool:
        return not self._check('status', code=4)

    def is_running(self) -> bool:
        return self._check('is-active')

    def is_enabled(self) -> bool:
        return self._check('is-enabled')

    def _create_service_files(self) -> None:
        content = f'''[Unit]
Description={self.display_name}

[Service]
WorkingDirectory={self.working_directory}
ExecStart={self.executable}
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
'''
        self.configuration.write_text(content)

    def _register_service(self) -> None:
        self._exec('daemon-reexec')
        self._reload_systemd()

    def uninstall(self) -> None:
        self.stop()
        self.disable()

        if self.configuration.exists():
            self.configuration.unlink()
        self._reload_systemd()

    def get_logs(self, lines: int = 50, since: Optional[str] = None, until: Optional[str] = None) -> list[str]:
        cmd = ['journalctl', '-u', self.service_name, '-n', str(lines)]

        if since:
            cmd.extend(['--since', since])
        if until:
            cmd.extend(['--until', until])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.splitlines()

    def _reload_systemd(self) -> None:
        """Reloads systemd to pick up changes or new services."""
        self._exec('daemon-reload')
