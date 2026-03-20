from pathlib import Path

import pytest

from daemoncrafter.windows import SCMProvider


def test_access_denied_msg(script: Path):
    """Test to reproduce status 5 error (Access Denied)"""
    provider = SCMProvider('Access Denied Test Service', script)
    try:
        provider.install()
        provider.uninstall()
        pytest.fail('Installation was successful, please execute this test again without administrator privileges.')
    except Exception as e:
        assert isinstance(e, PermissionError)
