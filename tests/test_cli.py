"""
Tests for the command-line entry point
"""

import subprocess
import sys


def test_help_lists_transport_modes():
    result = subprocess.run(
        [sys.executable, "-m", "mcp_bible.server", "--help"],
        capture_output=True, text=True, timeout=30,
    )

    assert result.returncode == 0
    assert "{stdio,http}" in result.stdout
