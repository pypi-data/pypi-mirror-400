"""
Google SERP MCP server.
"""

from serp_mcp.core import build_search_options
from serp_mcp.mcp_server import main as mcp_main
from serp_mcp.scraper import search_full, search_lite
from serp_mcp.types import LiteResult, LiteSearchResult, SearchOptions, SearchResult

__version__ = "1.0.0"
__all__ = [
    "search_lite",
    "search_full",
    "SearchOptions",
    "LiteResult",
    "LiteSearchResult",
    "SearchResult",
    "build_search_options",
    "mcp_main",
]
