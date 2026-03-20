import requests
import subprocess
import time
from typing import Any

import pytest

from daemoncrafter import DaemonCrafter


TIMEOUT = 10


def read_last_line_logged(crafter: DaemonCrafter) -> str:
    """Read the last line logged by the daemon."""
    return crafter.get_logs(1)[-1]


def wait_for(condition: callable, expected: Any = True):
    start_time = time.time()
    while condition() != expected:
        if time.time() - start_time > TIMEOUT:
            assert condition() == expected, f'Condition failed to meet expected result within time limit.'
        time.sleep(0.5)


def test_full_lifecycle(crafter: DaemonCrafter):
    """Test the full lifecycle of a DaemonCrafter instance.

    In case of test failure, the cleanup.bat script will automatically run to clean up resources.
    """
    try:
        # Initial State
        assert crafter.is_installed() is False
        assert crafter.is_running() is False
        assert crafter.is_enabled() is False
        with pytest.raises(FileNotFoundError):
            crafter.get_logs()

        # Installation
        crafter.install()
        wait_for(crafter.is_installed)
        assert crafter.is_running() is False
        assert crafter.is_enabled() is False
        # no script logs yet

        # Execution
        crafter.start()
        wait_for(crafter.is_running)
        assert crafter.is_installed() is True
        assert crafter.is_enabled() is False
        wait_for(lambda: read_last_line_logged(crafter), expected='[INFO] Service started on port 6814')

        crafter.stop()
        wait_for(crafter.is_running, expected=False)
        assert crafter.is_installed() is True
        assert crafter.is_enabled() is False
        wait_for(lambda: read_last_line_logged(crafter), expected='[INFO] Service is shutting down...')

        # Configuration
        crafter.enable()
        wait_for(crafter.is_enabled)
        assert crafter.is_installed() is True
        assert crafter.is_running() is False

        crafter.disable()
        wait_for(crafter.is_enabled, expected=False)
        assert crafter.is_installed() is True
        assert crafter.is_running() is False

        # Usage
        crafter.start()
        wait_for(crafter.is_running)
        response = requests.get("http://localhost:6814/hello")
        assert response.status_code == 200
        assert response.text == 'Hello World'
        assert 'GET /hello HTTP/1.1' in read_last_line_logged(crafter)

        # Uninstallation
        crafter.uninstall()
        wait_for(crafter.is_installed, expected=False)
        assert crafter.is_running() is False
        assert crafter.is_enabled() is False
        assert read_last_line_logged(crafter) == '[INFO] Service is shutting down...'
        assert not crafter.backend.configuration.exists(), 'Service configuration file was not deleted.'

        # Reading Logs
        logs = crafter.get_logs(3)
        assert len(logs) == 3
        assert logs[0] == '[INFO] Hello endpoint was called'
    finally:
        print('Running cleanup scripts.')
        subprocess.call(['remove_service.bat'], shell=True)
        time.sleep(5)
        subprocess.call(['cleanup_files.bat'], shell=True)
