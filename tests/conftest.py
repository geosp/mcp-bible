"""
Shared fixtures for Bible MCP Server tests

BibleGateway is stubbed with httpx.MockTransport, so the tests run offline.
"""

import httpx
import pytest

from mcp_bible.bible_service import BibleService
from mcp_bible.config import BibleAPIConfig

PASSAGE_HTML = """
<html><body>
<div class="passage-text">
  <h3>For God So Loved the World</h3>
  <p><span class="text">For God so loved the world<sup class="footnote">[a]</sup>,
  that he gave his only Son<a href="#cr">(A)</a></span></p>
  <div class="footnotes"><p>[a] footnote text</p></div>
  <div class="crossrefs"><p>(A) crossref text</p></div>
</div>
</body></html>
"""

POETRY_HTML = """
<html><body>
<div class="passage-text">
  <div class="poetry">
    <p class="line">The Lord is my shepherd;</p>
    <p class="line">I shall not want.</p>
  </div>
</div>
</body></html>
"""


@pytest.fixture
def requests() -> list[httpx.Request]:
    """Requests seen by the mock transport"""
    return []


@pytest.fixture
def make_service(requests):
    """Build a BibleService whose HTTP calls are answered by a handler"""
    def factory(handler=None, **config) -> BibleService:
        def record(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if handler:
                return handler(request)
            return httpx.Response(200, text=PASSAGE_HTML)

        client = httpx.AsyncClient(transport=httpx.MockTransport(record))
        return BibleService(BibleAPIConfig(**config), client=client)

    return factory
