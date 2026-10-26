"""
Tests for configuration loading
"""

from mcp_bible.config import AppConfig, BibleAPIConfig


def test_defaults():
    config = BibleAPIConfig()

    assert config.api_url == "https://www.biblegateway.com/passage/"
    assert config.default_version == "ESV"
    assert "KJV" in config.supported_versions
    assert config.timeout == 30.0


def test_reads_bible_env_vars(monkeypatch):
    monkeypatch.setenv("BIBLE_API_URL", "https://example.test/passage/")
    monkeypatch.setenv("BIBLE_DEFAULT_VERSION", "KJV")
    monkeypatch.setenv("BIBLE_SUPPORTED_VERSIONS", "KJV, NIV ,ESV")
    monkeypatch.setenv("BIBLE_TIMEOUT", "5")

    config = BibleAPIConfig()

    assert config.api_url == "https://example.test/passage/"
    assert config.default_version == "KJV"
    assert config.supported_versions == ["KJV", "NIV", "ESV"]
    assert config.timeout == 5.0


def test_app_config_combines_sections(monkeypatch):
    monkeypatch.setenv("MCP_PORT", "4123")
    monkeypatch.setenv("BIBLE_DEFAULT_VERSION", "NIV")

    config = AppConfig()

    assert config.server.port == 4123
    assert config.bible_api.default_version == "NIV"
