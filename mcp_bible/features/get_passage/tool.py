"""
MCP Tool: Get Bible Passage

Provides the get_passage tool for AI assistants.
"""

import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring, load_instruction

from mcp_bible.bible_service import BibleService
from mcp_bible.features.get_passage.models import GetPassageRequest, GetPassageResponse

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, bible_service: BibleService) -> None:
    """
    Register the get_passage tool with the MCP server

    Args:
        mcp: FastMCP server instance
        bible_service: BibleService instance for Bible operations
    """
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def get_passage(passage: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get a Bible passage with comprehensive documentation loaded from instructions.md"""
        try:
            logger.info(f"MCP tool called: get_passage(passage='{passage}', version='{version}')")

            # Create and validate request
            request = GetPassageRequest(
                passage=passage,
                version=version
            )

            # Call bible service
            result = await bible_service.fetch_passage(
                passage=request.passage,
                version=request.version
            )

            logger.info(f"Passage retrieval completed: {passage} ({version})")
            return result

        except ValueError as e:
            logger.warning(f"Passage validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Passage retrieval error: {e}")
            raise