import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree

from daemoncrafter.providers import DaemonProvider


class SCMProvider(DaemonProvider):
    @property
    def configuration(self) -> Path:
        return self.working_directory / f'{self.service_name}.xml'

    @property
    def winsw_executable(self) -> Path:
        return self.configuration.with_suffix('.exe')

    def _command(self, action: str, *args: str) -> list[str]:
        return ['sc', action, self.service_name, *args]

    def _exec(self, action: str, *args: str, raise_on_failure: bool = True) -> subprocess.CompletedProcess:
        """Override base _exec to provide better error messages for Windows-specific errors."""
        try:
            return super()._exec(action, *args, raise_on_failure=raise_on_failure)
        except subprocess.CalledProcessError as e:
            if e.returncode == 5:
                raise PermissionError(
                    f'Access denied when trying to {action} service "{self.service_name}". '
                    f'This operation requires administrator privileges. '
                    f'Please run this command as an administrator or from an elevated command prompt.'
                ) from e
            else:
                raise

    def is_installed(self) -> bool:
        return not self._check('query', code=1060)

    def is_running(self) -> bool:
        return 'RUNNING' in self._exec('query', raise_on_failure=False).stdout

    def is_enabled(self) -> bool:
        return 'AUTO_START' in self._exec('qc', raise_on_failure=False).stdout

    def _create_service_files(self, **command_args) -> None:
        self._copy_winsw_executable()

        root = ElementTree.Element('service')

        ElementTree.SubElement(root, 'id').text = self.service_name
        ElementTree.SubElement(root, 'name').text = self.display_name

        ElementTree.SubElement(root, 'workingdirectory').text = str(self.working_directory)

        ElementTree.SubElement(root, 'executable').text = sys.executable

        args = ['-u', str(self.executable)]
        for key, value in command_args.items():
            args.append(f'--{key}={value}')
        ElementTree.SubElement(root, 'arguments').text = ' '.join(args)

        ElementTree.SubElement(root, 'logpath').text = r'%BASE%\logs'

        log = ElementTree.SubElement(root, 'log')
        log.set('mode', 'roll-by-size')
        ElementTree.SubElement(log, 'sizeThreshold').text = '10240'
        ElementTree.SubElement(log, 'keepFiles').text = '10'

        tree = ElementTree.ElementTree(root)
        ElementTree.indent(tree, space='  ', level=0)
        tree.write(str(self.configuration), encoding='utf-8', xml_declaration=True)

    def _register_service(self) -> None:
        self._exec('create',
           'binPath=', f'"{self.winsw_executable}"',
           'DisplayName=', f'{self.display_name}'
        )

    def uninstall(self) -> None:
        self.stop()
        self.disable()

        self._exec('delete')
        if self.configuration.exists():
            self.configuration.unlink()

    def enable(self) -> None:
        self._exec('config', 'start=', 'auto')

    def disable(self) -> None:
        self._exec('config', 'start=', 'demand')

    def get_logs(self, lines: int = 50, since: Optional[str] = None, until: Optional[str] = None) -> list[str]:
        log_file = self.working_directory / 'logs' / 'daemoncrafter_test.err.log'
        if not log_file.exists():
            raise FileNotFoundError(f'Log file {log_file} does not exist.')

        with log_file.open('r', encoding='utf-8') as f:
            lines = f.readlines()[-lines:]

        return [line.strip() for line in lines]

    def _copy_winsw_executable(self) -> None:
        """Copy WinSW executable to the service directory."""
        package_dir = Path(__file__).parent
        bundled_winsw = package_dir / 'bin' / 'winsw.exe'
        shutil.copy2(bundled_winsw, self.winsw_executable)
