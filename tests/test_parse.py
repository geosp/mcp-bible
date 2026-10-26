"""
Tests for BibleGateway HTML parsing
"""

from mcp_bible.bible_service import BibleService
from mcp_bible.config import BibleAPIConfig

from .conftest import PASSAGE_HTML, POETRY_HTML


def parse(html: str) -> str | None:
    return BibleService(BibleAPIConfig())._parse_passage(html)


def test_parses_prose_and_strips_notes():
    text = parse(PASSAGE_HTML)

    assert "For God so loved the world" in text
    assert "he gave his only Son" in text
    assert "footnote text" not in text
    assert "crossref text" not in text
    assert "For God So Loved the World" not in text  # section header
    assert "[a]" not in text
    assert "(A)" not in text


def test_parses_poetry_lines():
    text = parse(POETRY_HTML)

    assert "The Lord is my shepherd;" in text
    assert "I shall not want." in text


def test_missing_passage_container_returns_none():
    assert parse("<html><body><p>No results</p></body></html>") is None


def test_empty_passage_returns_none():
    assert parse('<div class="passage-text"><p>  </p></div>') is None
