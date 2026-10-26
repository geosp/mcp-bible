"""
Tests for the command-line entry point
"""

import os
import subprocess
import sys


def test_help_lists_transport_modes():
    result = subprocess.run(
        [sys.executable, "-m", "mcp_bible.server", "--help"],
        capture_output=True, text=True, timeout=30,
    )

    assert result.returncode == 0
    assert "{stdio,http}" in result.stdout


def test_mcp_transport_env_selects_http(tmp_path):
    # Without --mode, MCP_TRANSPORT picks the transport. HTTP without an auth
    # provider or --no-auth refuses to start, which proves HTTP was selected.
    env = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
    env["MCP_TRANSPORT"] = "http"

    result = subprocess.run(
        [sys.executable, "-m", "mcp_bible.server"],
        capture_output=True, text=True, timeout=30, env=env, cwd=tmp_path,
    )

    assert result.returncode == 1
    assert "HTTP transport has auth enabled" in result.stderr
