"""
Bible MCP Server

This demonstrates how to create a complete MCP server by extending
BaseMCPServer from mcp-service-kit.

Run it with:
    mcp-bible --mode stdio
    mcp-bible --mode http --port 3000
"""

import logging

from mcp_service_kit import BaseMCPServer, create_main_with_modes

from mcp_bible import __version__
from mcp_bible.bible_service import BibleService
from mcp_bible.config import AppConfig
from mcp_bible.service import BibleMCPService

logger = logging.getLogger(__name__)


class BibleMCPServer(BaseMCPServer):
    """
    Bible MCP Server implementation

    Extends BaseMCPServer to provide Bible functionality via MCP protocol.
    Only the service metadata is required; override create_auth_provider()
    to protect the HTTP transport.
    """

    @property
    def service_title(self) -> str:
        """Human-readable server title"""
        return "Bible MCP Server"

    @property
    def service_description(self) -> str:
        """Server description"""
        return (
            "Provides Bible passage retrieval capabilities via Model Context Protocol (MCP). "
            "Supports multiple Bible translations with automatic parsing and cleaning. "
            "Built using mcp-service-kit."
        )

    @property
    def service_version(self) -> str:
        """Service version"""
        return __version__


def create_bible_service(config: AppConfig) -> BibleMCPService:
    """Factory function for creating the Bible service"""
    # Create bible service (business logic)
    bible_service = BibleService(api_config=config.bible_api)

    # Create MCP service wrapper
    return BibleMCPService(bible_service)


main = create_main_with_modes(
    BibleMCPServer,
    create_bible_service,
    AppConfig,
    "mcp-bible",
    "Bible MCP Server - Provides Bible passage retrieval via MCP protocol"
)


if __name__ == "__main__":
    main()
