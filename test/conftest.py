from pathlib import Path
import pytest

from daemoncrafter import DaemonCrafter
from daemoncrafter.executables import ASGIApp

daemon_name = 'DaemonCrafter Test'


@pytest.fixture
def script() -> Path:
    """Path to the test script."""
    return Path(__file__).parent / 'script.py'


@pytest.fixture
def crafter(script: Path) -> DaemonCrafter:
    """Create a fresh DaemonCrafter instance for each test."""
    return DaemonCrafter(daemon_name, script)


@pytest.fixture
def asgi_crafter() -> DaemonCrafter:
    try:
        import fastapi
        import uvicorn
    except ImportError:
        raise RuntimeError('Using the "fast_api_crafter" fixture without "fastapi" and "uvicorn" installed will cause a failure.')

    app = ASGIApp(Path(__file__).parent, file='fastapi_app')
    return DaemonCrafter(daemon_name, app)
