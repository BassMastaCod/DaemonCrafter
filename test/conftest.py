from pathlib import Path
import pytest

from daemon_crafter import DaemonCrafter


daemon_name = 'DaemonCrafter Test'


@pytest.fixture
def script() -> Path:
    """Path to the test script."""
    return Path(__file__).parent / 'script.py'


@pytest.fixture
def crafter(script: Path) -> DaemonCrafter:
    """Create a fresh DaemonCrafter instance for each test."""
    return DaemonCrafter(daemon_name, script)
