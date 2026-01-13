"""
MCP server for Google SERP scraping.

This module provides an MCP (Model Context Protocol) server that exposes
a search tool for performing Google searches with various options.
"""

import json
from typing import cast

from fastmcp import FastMCP

from serp_mcp.core import build_search_options
from serp_mcp.scraper import search_full, search_lite
from serp_mcp.types import CountryCode, LanguageCode

mcp = FastMCP("serp-mcp")


@mcp.tool()
async def search(
    query: str,
    country: str = "us",
    language: str = "en",
    location: str | None = None,
    time_range: str | None = None,
    autocorrect: bool = True,
    page: int = 1,
    lite: bool = True,
) -> str:
    """
    Perform a Google search and return results.

    Args:
        query: Search query string
        country: Two-letter country code (default: "us")
        language: Two-letter language code (default: "en")
        location: Canonical location name for local results (e.g., "New York, NY, United States")
            Uses Google Ads API geo-targeting formatting for best results
        time_range: Optional time range filter (hour, day, week, month, year)
        autocorrect: Enable/disable Google's autocorrect (default: True)
        page: Page number for pagination (default: 1)
        lite: If True (default), returns only organic search results (~50% less traffic).
            If False, returns comprehensive results including knowledge graph, related
            searches, and "people also ask" data. Set to False when you need rich metadata
            beyond basic web results.

    Returns:
        JSON string of search results or error message
    """
    try:
        options = build_search_options(
            query=query,
            country=cast(CountryCode, country),
            language=cast(LanguageCode, language),
            location=location,
            time_range=time_range,
            autocorrect=autocorrect,
            page=page,
            lite=lite,
        )

        if lite:
            result = await search_lite(options, headless=True)
        else:
            result = await search_full(options, headless=True)  # type: ignore [assignment]

        return json.dumps(result.model_dump(exclude_none=True), indent=2, ensure_ascii=False)

    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Search error: {str(e)}"


def main() -> None:
    """Run MCP server with stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
