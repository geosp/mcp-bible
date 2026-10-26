"""
Tests for the Bible MCP server and get_passage tool

Uses an in-memory FastMCP client against the server built by the kit.
"""

import httpx
from fastmcp import Client
from mcp_service_kit import BaseServerConfig

from mcp_bible.server import BibleMCPServer
from mcp_bible.service import BibleMCPService


def build_client(bible_service) -> Client:
    server = BibleMCPServer(BaseServerConfig(), BibleMCPService(bible_service))
    return Client(server.create_mcp_app())


async def test_lists_get_passage_tool(make_service):
    async with build_client(make_service()) as client:
        tools = await client.list_tools()

    assert [tool.name for tool in tools] == ["get_passage"]
    assert "Bible Passage Retrieval Tool" in tools[0].description


async def test_get_passage_uses_configured_default_version(make_service, requests):
    service = make_service(default_version="KJV")

    async with build_client(service) as client:
        result = await client.call_tool("get_passage", {"passage": "John 3:16"})

    assert result.data["success"] is True
    assert result.data["version"] == "KJV"
    assert "For God so loved the world" in result.data["text"]
    assert requests[0].url.params["version"] == "KJV"
    assert requests[0].url.params["search"] == "John 3:16"


async def test_get_passage_uses_configured_api_url(make_service, requests):
    service = make_service(api_url="https://example.test/passage/")

    async with build_client(service) as client:
        await client.call_tool("get_passage", {"passage": "John 3:16", "version": "NIV"})

    assert str(requests[0].url).startswith("https://example.test/passage/")
    assert requests[0].url.params["version"] == "NIV"


async def test_get_passage_multiple_references(make_service, requests):
    async with build_client(make_service()) as client:
        result = await client.call_tool(
            "get_passage", {"passage": "John 3:16; Romans 8:28", "version": "ESV"}
        )

    assert result.data["success"] is True
    assert [r.url.params["search"] for r in requests] == ["John 3:16", "Romans 8:28"]
    assert result.data["text"].startswith("John 3:16\n")
    assert "\n\nRomans 8:28\n" in result.data["text"]


async def test_get_passage_reports_http_errors(make_service):
    service = make_service(lambda request: httpx.Response(503))

    async with build_client(service) as client:
        result = await client.call_tool("get_passage", {"passage": "John 3:16"})

    assert result.data["success"] is False
    assert "503" in result.data["error"]


async def test_get_passage_reports_unparseable_page(make_service):
    service = make_service(lambda request: httpx.Response(200, text="<html></html>"))

    async with build_client(service) as client:
        result = await client.call_tool("get_passage", {"passage": "Nowhere 1:1"})

    assert result.data["success"] is False
    assert result.data["error"] == "Could not parse passage text"
