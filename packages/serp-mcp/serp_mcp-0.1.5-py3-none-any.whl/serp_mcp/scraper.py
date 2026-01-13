"""
Google SERP scraper with automatic fingerprint rotation.

Optimized flow:
1. Block ALL requests except www.google.com/search
2. Navigate to search URL (initial request without "sei" param)
3. Google JS triggers second request WITH "sei" param - capture ONLY this response
4. Context manager handles cleanup automatically
5. Process captured HTML
"""

import re

from camoufox.async_api import AsyncCamoufox

from serp_mcp.config import build_search_url
from serp_mcp.parser import parse_lite_results, parse_search_results
from serp_mcp.types import LiteSearchResult, SearchOptions, SearchResult

# Block everything except Google search URLs
NOT_GOOGLE_SEARCH_REGEX = re.compile(r"^(?!https://www\.google\.com/search(?:\?.*|$)).*")

# Match Second Google search response
GOOGLE_SEARCH_RESULTS_REGEX = re.compile(r"https://www\.google\.com/search.*sei=.*")


async def search_lite(
    options: SearchOptions,
    headless: bool = True,
) -> LiteSearchResult:
    """Perform a lite Google search (web results only, minimal data)."""
    html = await _fetch_search_html(options, headless)
    return parse_lite_results(html)


async def search_full(
    options: SearchOptions,
    headless: bool = True,
) -> SearchResult:
    """Perform a full Google search (all result types, sitelinks, PAA, related, KG)."""
    html = await _fetch_search_html(options, headless)
    return parse_search_results(html, options.query)


async def _fetch_search_html(
    options: SearchOptions,
    headless: bool = True,
) -> str:
    """Fetch Google search HTML using Camoufox."""
    url = build_search_url(options)

    async with AsyncCamoufox(  # type: ignore
        headless=headless,
        geoip=False,
    ) as browser:
        context = await browser.new_context()  # type: ignore
        await context.route(NOT_GOOGLE_SEARCH_REGEX, lambda route: route.abort())

        page = await context.new_page()

        async with page.expect_response(
            GOOGLE_SEARCH_RESULTS_REGEX, timeout=30_000
        ) as response_info:
            await page.goto(url, wait_until="commit")

        response = await response_info.value
        html = await response.text()

        await context.close()

    if "recaptcha" in html or "unusual traffic" in html:
        raise RuntimeError("CAPTCHA detected - try again later or use different IP")

    return html
