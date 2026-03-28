import requests
import subprocess
import time

import pytest

from daemoncrafter import DaemonCrafter
from daemoncrafter.errors import ServiceMissing, ServiceNotRunning, ServiceAlreadyRunning
from daemoncrafter.providers import wait_for


def read_last_line_logged(crafter: DaemonCrafter) -> str:
    """Read the last line logged by the daemon."""
    return crafter.get_logs(1)[-1]


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
        crafter.install(port=6814)
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
        wait_for(crafter.is_running, False)
        assert crafter.is_installed() is True
        assert crafter.is_enabled() is False
        wait_for(lambda: read_last_line_logged(crafter), expected='[INFO] Service is shutting down...')

        # Configuration
        crafter.enable()
        wait_for(crafter.is_enabled)
        assert crafter.is_installed() is True
        assert crafter.is_running() is False

        crafter.disable()
        wait_for(crafter.is_enabled, False)
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
        wait_for(crafter.is_installed, False)
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


def test_asgi_daemon(asgi_crafter: DaemonCrafter):
    """Test creating a daemon for a ASGI Application.

    In case of test failure, the cleanup.bat script will automatically run to clean up resources.
    """
    try:
        asgi_crafter.install(port=6814)
        wait_for(asgi_crafter.is_installed)

        asgi_crafter.start()
        wait_for(asgi_crafter.is_running)

        response = requests.get('http://localhost:6814/hello')
        assert response.status_code == 200
        assert response.text == 'Hello World from FastAPI'
    finally:
        print('Running cleanup scripts.')
        subprocess.call(['remove_service.bat'], shell=True)
        time.sleep(5)
        subprocess.call(['cleanup_files.bat'], shell=True)


def test_uninstall(crafter: DaemonCrafter):
    try:
        assert crafter.is_installed() is False
        crafter.install(port=6814)
        crafter.uninstall()
        wait_for(crafter.is_installed, False)
    finally:
        print('Running cleanup scripts.')
        subprocess.call(['remove_service.bat'], shell=True)
        time.sleep(5)
        subprocess.call(['cleanup_files.bat'], shell=True)


def test_errors(crafter: DaemonCrafter):
    try:
        assert crafter.is_installed() is False

        with pytest.raises(ServiceMissing):
            crafter.start()
        with pytest.raises(ServiceMissing):
            crafter.stop()
        with pytest.raises(ServiceMissing):
            crafter.enable()
        with pytest.raises(ServiceMissing):
            crafter.disable()
        with pytest.raises(ServiceMissing):
            crafter.uninstall()

        crafter.install(port=6814)
        wait_for(crafter.is_installed)

        with pytest.raises(ServiceNotRunning):
            crafter.stop()

        crafter.start()
        wait_for(crafter.is_running)

        with pytest.raises(ServiceAlreadyRunning):
            crafter.start()
    finally:
        print('Running cleanup scripts.')
        subprocess.call(['remove_service.bat'], shell=True)
        time.sleep(5)
        subprocess.call(['cleanup_files.bat'], shell=True)
