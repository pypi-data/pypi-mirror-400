"""
Google SERP Parser - Generalized Extraction

Extracts 4 categories of data:
1. Results (organic, video, news, sitelinks, etc.) - unified extraction
2. People Also Ask (PAA) - from data-q attributes
3. Related Searches - from search URLs
4. Knowledge Graph - from data-attrid attributes

Design principles:
- Generalized: Each category has its own focused extraction
- Elegant: Clean, readable code without URL-based type detection
- Deterministic: Use element position in nested structures, not randomized strings
"""

import html
import json
import re
from typing import Any, cast
from urllib.parse import unquote, urlparse

from serp_mcp.types import (
    KnowledgeGraph,
    LiteResult,
    LiteSearchResult,
    OrganicResult,
    PeopleAlsoAsk,
    RelatedSearch,
    ResultType,
    SearchResult,
    Sitelink,
)


def parse_lite_results(html: str) -> LiteSearchResult:
    """Parse Google SERP HTML into lite result (web results only)."""
    json_data = extract_embedded_json(html)

    results: list[LiteResult] = []
    for data in json_data.values():
        if (
            not isinstance(data, list)
            or len(data) < 32
            or get_record_type(data) is not ResultType.WEB
        ):
            continue

        result = extract_lite_result(data)
        if result:
            results.append(result)

    return LiteSearchResult(results=results)


def parse_search_results(html: str, query: str) -> SearchResult:
    """Parse Google SERP HTML into full structured result."""
    json_data = extract_embedded_json(html)

    result = SearchResult(
        organic=[],
        people_also_ask=[],
        related_searches=[],
    )

    for data in json_data.values():
        if not isinstance(data, list) or len(data) < 32:
            continue

        record_type = get_record_type(data)

        if record_type is ResultType.WEB:
            organic = extract_organic_result(data, ResultType.WEB)
            if organic:
                result.organic.append(organic)

        elif record_type is ResultType.NEWS:
            organic = extract_organic_result(data, ResultType.NEWS)
            if organic:
                result.organic.append(organic)

        elif record_type is ResultType.NAVIGATIONAL:
            organic = extract_organic_result(data, ResultType.NAVIGATIONAL)
            if organic:
                result.organic.append(organic)

        elif record_type is ResultType.VIDEO:
            organic = extract_video_result(data)
            if organic:
                result.organic.append(organic)

        elif record_type is ResultType.KG_ENTITY:
            parse_kg_entity(data, result)

    # Extract sitelinks
    for i, organic in enumerate(result.organic):
        next_url = result.organic[i + 1].link if i + 1 < len(result.organic) else None
        extract_sitelinks(html, organic, next_url)

    # Remove organic results that appear as sitelinks of earlier results
    sitelink_urls: set[str] = set()
    for organic in result.organic:
        if organic.sitelinks:
            for sl in organic.sitelinks:
                sitelink_urls.add(sl.link)
    result.organic = [r for r in result.organic if r.link not in sitelink_urls]

    extract_people_also_ask(html, result)
    extract_related_searches(html, result, query)
    extract_knowledge_graph(html, result)

    return result


# =============================================================================
# Category 1: Results Extraction (Organic, Video, News, Sitelinks, etc.)
# =============================================================================


def extract_embedded_json(html: str) -> dict[str, list[Any]]:
    """
    Extract embedded JSON from Google SERP HTML.

    Google embeds search data in a JavaScript variable like:
        var m={"sessionId":["gws-wiz-serp",...], ...};

    Uses a regex that properly handles:
    - Quoted strings (including escaped quotes)
    - Braces inside strings (e.g., snippets containing "};")
    - Nested objects up to 3 levels deep
    - Skips empty {} objects via lookahead
    """
    # Pattern components:
    # - string: "..." with escape handling
    # - content: non-brace/quote chars OR strings
    # - nested_N: {...} at depth N
    string = r'"(?:[^"\\]|\\.)*"'
    content = rf"(?:[^{{}}\"]|{string})*"
    nested_3 = rf"\{{{content}\}}"
    nested_2 = rf"\{{(?:{content}|{nested_3})*\}}"
    # (?=") lookahead ensures at least one key exists (skips empty {})
    pattern = rf'var\s+m\s*=\s*(\{{(?=")(?:{content}|{nested_2})*\}})'

    matches = re.findall(pattern, html)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly 1 JSON match, found {len(matches)}")

    json_data = json.loads(matches[0])
    if not json_data:
        raise ValueError("No embedded JSON data found in HTML")

    return cast(dict[str, list[Any]], json_data)


def get_record_type(data: list[Any]) -> ResultType | None:
    """Determine the type of a JSON record. Returns None for unknown types."""
    d32 = safe_get(data, 32)
    if not isinstance(d32, list):
        # Check for KG entity: has /m/ prefix at [1]
        mid = safe_get(data, 1)
        if isinstance(mid, str) and mid.startswith("/m/"):
            return ResultType.KG_ENTITY
        return None

    # Check web result types at [32][9][13][20] - most common, check first
    d32_9 = safe_get(d32, 9)
    if isinstance(d32_9, list):
        d32_9_13 = safe_get(d32_9, 13)
        if isinstance(d32_9_13, list):
            type_marker = safe_get(d32_9_13, 20)
            if type_marker == "WEB_RESULT_INNER":
                return ResultType.WEB
            elif type_marker == "NEWS_ARTICLE_RESULT":
                return ResultType.NEWS
            elif type_marker == "NAVIGATIONAL_RESULT_INNER":
                return ResultType.NAVIGATIONAL

    # Check for video: SHOPPING_MERCHANT_VIDEO at [32][11][0]
    d32_11 = safe_get(d32, 11)
    if isinstance(d32_11, list) and safe_get(d32_11, 0) == "SHOPPING_MERCHANT_VIDEO":
        return ResultType.VIDEO

    return None


def extract_lite_result(data: list[Any]) -> LiteResult | None:
    """Extract lite result (web only) from [32][3]."""
    d32 = safe_get(data, 32)
    if not isinstance(d32, list):
        return None

    d32_3 = safe_get(d32, 3)
    if not isinstance(d32_3, list) or len(d32_3) < 3:
        return None

    url = safe_get(d32_3, 0)
    title = safe_get(d32_3, 1) or ""
    snippet = safe_get(d32_3, 2) or ""
    source = safe_get(d32_3, 9)

    return LiteResult(
        title=title,
        link=url,
        snippet=snippet,
        source=source,
    )


def extract_organic_result(data: list[Any], result_type: ResultType) -> OrganicResult | None:
    """Extract organic result (web/news/navigational) from [32][3]."""
    d32 = safe_get(data, 32)
    if not isinstance(d32, list):
        return None

    d32_3 = safe_get(d32, 3)
    if not isinstance(d32_3, list) or len(d32_3) < 3:
        return None

    url = safe_get(d32_3, 0)
    title = safe_get(d32_3, 1) or ""
    snippet = safe_get(d32_3, 2) or ""
    source = safe_get(d32_3, 9) or None

    return OrganicResult(
        title=title,
        link=url,
        snippet=snippet,
        source=source,
        result_type=result_type,
    )


def extract_video_result(data: list[Any]) -> OrganicResult | None:
    """Extract video result from [31] and [17]."""
    d31 = safe_get(data, 31)
    if not isinstance(d31, list) or len(d31) < 2:
        return None

    url = safe_get(data, 17)
    title = safe_get(d31, 0) or ""
    snippet = safe_get(d31, 1) or ""
    channel = safe_get(d31, 2) or None

    return OrganicResult(
        title=title,
        link=url,
        snippet=snippet,
        source=channel,
        result_type=ResultType.VIDEO,
        channel=channel,
    )


def extract_sitelinks(html: str, organic: OrganicResult, next_url: str | None) -> None:
    """Extract sitelinks - same-domain links between this result and the next.

    Handles multiple patterns including forum sub-results with metadata:
    - Title, link, snippet, answer count, date
    """
    parsed = urlparse(organic.link)
    domain = parsed.hostname.replace("www.", "") if parsed.hostname else ""
    if not domain:
        return

    start = html.find(f'href="{organic.link}"')
    if start == -1:
        return

    # End at next result's URL, or end of HTML for last result
    end = html.find(f'href="{next_url}"', start + 1) if next_url else len(html)
    if end == -1:
        end = len(html)
    block = html[start:end]

    sitelinks: list[Sitelink] = []
    seen: dict[str, bool] = {}  # Use dict to preserve insertion order
    domain_escaped = re.escape(domain)

    # Pattern 1: Direct anchor text after href - href="URL"...>Title<
    pattern1 = rf'href="(https?://[^"]*{domain_escaped}[^"]*)"[^>]*>([^<]{{3,100}})<'

    for match in re.finditer(pattern1, block, re.I):
        link = match.group(1)
        title = clean_text(match.group(2))

        if not _is_valid_sitelink(link, title, organic.link, seen):
            continue
        seen[link] = True

        # Extract metadata from context after this link
        context_start = match.end()
        context = block[context_start : context_start + 300]
        answers, date = _extract_forum_metadata(context)

        sitelinks.append(Sitelink(title=title, link=link, answers=answers, date=date))
        if len(sitelinks) >= 6:
            break

    # Pattern 2: Span-wrapped titles (forum posts with <em> highlights)
    # Structure: <a href="URL"><span>Title with <em>highlights</em></span></a>
    if len(sitelinks) < 6:
        pattern2 = rf'<a[^>]*href="(https?://[^"]*{domain_escaped}[^"]*)"[^>]*><span>([^<]*(?:<em>[^<]*</em>[^<]*)*)</span>'
        for match in re.finditer(pattern2, block, re.I):
            link = match.group(1)
            raw_title = match.group(2)
            # Strip <em> tags from title
            title = clean_text(re.sub(r"</?em>", "", raw_title))

            if not _is_valid_sitelink(link, title, organic.link, seen):
                continue
            seen[link] = True

            # Extract metadata from context after this link
            context_start = match.end()
            context = block[context_start : context_start + 300]
            answers, date = _extract_forum_metadata(context)

            sitelinks.append(Sitelink(title=title, link=link, answers=answers, date=date))
            if len(sitelinks) >= 6:
                break

    # Pattern 3: H3 titles (common for structured sitelinks)
    if len(sitelinks) < 6:
        pattern3 = rf'href="(https?://[^"]*{domain_escaped}[^"]*)"[^>]*>[\s\S]{{0,50}}?<h3[^>]*>([^<]+)</h3>'
        for match in re.finditer(pattern3, block, re.I):
            link = match.group(1)
            title = clean_text(match.group(2))

            if not _is_valid_sitelink(link, title, organic.link, seen):
                continue
            seen[link] = True
            sitelinks.append(Sitelink(title=title, link=link))
            if len(sitelinks) >= 6:
                break

    if sitelinks:
        organic.sitelinks = sitelinks


def _extract_forum_metadata(context: str) -> tuple[str | None, str | None]:
    """Extract forum metadata (answers count, date) from HTML context."""
    answers = None
    date = None

    # Look for answer/comment/post count: "160 answers", "51 comments", "29 posts"
    answer_match = re.search(r">(\d+)\s*(answers?|comments?|replies?|posts?)<", context, re.I)
    if answer_match:
        answers = f"{answer_match.group(1)} {answer_match.group(2).lower()}"

    # Look for date patterns: "Apr 20, 2023", "Mar 15, 2025", "4 years ago"
    date_match = re.search(
        r">([A-Z][a-z]{2}\s+\d{1,2},?\s+\d{4}|\d+\s+(?:days?|weeks?|months?|years?)\s+ago)<",
        context,
        re.I,
    )
    if date_match:
        date = date_match.group(1)

    return answers, date


def _is_valid_sitelink(link: str, title: str, main_link: str, seen: dict[str, bool]) -> bool:
    """Check if a sitelink is valid (not duplicate, not navigation, etc.)."""
    if not title or len(title) < 3 or link == main_link or link in seen:
        return False
    # Skip forum answer counts like "311 answers", "51 comments"
    if re.match(r"^\d+\s*(answers?|comments?|replies?|votes?|posts?)$", title, re.I):
        return False
    # Skip navigation terms
    skip_terms = ("more", "next", "previous", "menu", "search", "cached", "similar")
    if any(term in title.lower() for term in skip_terms):
        return False
    return True


def parse_kg_entity(data: list[Any], result: SearchResult) -> None:
    """Parse Knowledge Graph entity from JSON."""
    try:
        mid = data[1]
        if not isinstance(mid, str) or not mid.startswith("/m/"):
            return

        name = clean_text(str(data[2]))
        types = data[4] if isinstance(data[4], list) else []

        if not result.knowledge_graph:
            result.knowledge_graph = KnowledgeGraph(
                title=name,
                type=types[0] if types else None,
            )
        elif not result.knowledge_graph.type and types:
            result.knowledge_graph.type = types[0]
    except (IndexError, TypeError):
        pass


# =============================================================================
# Category 2: People Also Ask Extraction
# =============================================================================


def extract_people_also_ask(html: str, result: SearchResult) -> None:
    """Extract PAA questions with snippets and links from jsl.dh blocks.

    Structure:
    - Questions: data-q="..." attribute (stable marker)
    - Answer snippets: jsl.dh blocks with data-attrid="wa:/description"
    - Source links: jsl.dh blocks with external href + h3 title, ID = answer ID + 1
    """
    # Parse jsl.dh blocks - pattern handles escaped quotes inside content
    # Block IDs end with __N (e.g., 'base_id__69')
    answers: list[tuple[int, str]] = []  # (id, snippet)
    sources: list[tuple[int, str, str | None]] = []  # (id, link, title)

    # Regex handles escaped content: matches \" and other escapes properly
    jsl_pattern = r"window\.jsl\.dh\('([^']+)',\s*\"((?:[^\"\\]|\\.)*)\"\)"

    for match in re.finditer(jsl_pattern, html):
        block_id = match.group(1)
        content = _decode_jsl(match.group(2))

        # Extract numeric ID from end of block ID (e.g., '__69' -> 69)
        id_match = re.search(r"__(\d+)$", block_id)
        if not id_match:
            continue
        numeric_id = int(id_match.group(1))

        # Answer block: contains wa:/description
        if 'data-attrid="wa:/description"' in content:
            # Extract text from nested spans (may contain <b> tags)
            snippet_match = re.search(
                r'data-attrid="wa:/description"[^>]*>[\s\S]*?<span[^>]*>([\s\S]*?)</span>',
                content,
            )
            if snippet_match:
                # Strip HTML tags from snippet
                raw_text = re.sub(r"<[^>]+>", "", snippet_match.group(1))
                snippet = clean_text(raw_text)
                if len(snippet) > 15:
                    answers.append((numeric_id, snippet))

        # Source link block: contains external href (paired with answer by ID proximity)
        elif "href=" in content:
            link_match = re.search(r'href="(https?://[^"]+)"', content)
            if link_match and "google.com" not in link_match.group(1):
                link = link_match.group(1).split("#")[0]  # Remove fragment
                # Extract title from <h3> tag (stable marker for PAA source titles)
                title_match = re.search(r"<h3[^>]*>([^<]+)</h3>", content)
                title = clean_text(title_match.group(1)) if title_match else None
                sources.append((numeric_id, link, title))

    # Extract questions from data-q attributes (must end with ?)
    seen: dict[str, bool] = {}  # Use dict to preserve insertion order
    answer_idx = 0

    for match in re.finditer(r'data-q="([^"]+\?)"', html):
        question = clean_text(match.group(1))
        if not question or question.lower() in seen:
            continue
        seen[question.lower()] = True

        paa = PeopleAlsoAsk(question=question)

        # Assign answer snippet (matched by order)
        if answer_idx < len(answers):
            answer_id, snippet = answers[answer_idx]
            paa.snippet = snippet

            # Find source link that follows this answer (ID = answer ID + 1)
            for src_id, link, title in sources:
                if src_id == answer_id + 1:
                    paa.link = link
                    paa.title = title
                    break

        answer_idx += 1
        result.people_also_ask.append(paa)


def _decode_jsl(content: str) -> str:
    """Decode jsl.dh escaped content."""
    result = content
    # Decode hex escapes: \x3c -> <
    result = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), result)
    # Decode unicode escapes: \u003c -> <
    result = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), result)
    return result.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


# =============================================================================
# Category 3: Related Searches Extraction
# =============================================================================


def extract_related_searches(
    html: str, result: SearchResult, original_query: str
) -> None:
    """
    Extract related searches from search URL hrefs.
    Filters out navigation/filter URLs and the original query.
    """
    seen: dict[str, bool] = {}  # Use dict to preserve insertion order
    lower_original = original_query.lower().strip()

    for match in re.finditer(r'href="/search\?[^"]*q=([^"&]+)[^"]*"', html):
        query = unquote(match.group(1).replace("+", " "))
        query = clean_text(query)
        lower = query.lower()

        # Skip: original query, duplicates, too short, navigation terms
        if (
            lower == lower_original
            or lower in seen
            or len(query) < 5
            or query.startswith(("site:", "related:", "cache:"))
            or any(t in lower for t in ("images", "videos", "news", "maps", "shopping"))
        ):
            continue

        seen[lower] = True
        result.related_searches.append(RelatedSearch(query=query))


# =============================================================================
# Category 4: Knowledge Graph Extraction
# =============================================================================


def extract_knowledge_graph(html: str, result: SearchResult) -> None:
    """Extract Knowledge Graph data from data-attrid attributes."""
    if 'data-attrid="title"' not in html:
        return

    if not result.knowledge_graph:
        result.knowledge_graph = KnowledgeGraph()

    kg = result.knowledge_graph

    # Title
    if not kg.title:
        match = re.search(r'data-attrid="title"[^>]*>([^<]+)<', html)
        if match:
            kg.title = clean_text(match.group(1))

    # Website
    if not kg.website:
        website_pattern = r'data-attrid="[^"]*website[^"]*"[^>]*>[\s\S]*?href="([^"]+)"'
        match = re.search(website_pattern, html, re.I)
        if match:
            kg.website = match.group(1)

    # Attributes from kc:/ data-attrid - value after label colon
    attrid_pattern = r'data-attrid="(kc:/[^"]+)"'
    attrid_positions = [
        (m.start(), m.group(1)) for m in re.finditer(attrid_pattern, html)
    ]
    for i, (pos, attrid) in enumerate(attrid_positions):
        end = attrid_positions[i + 1][0] if i + 1 < len(attrid_positions) else len(html)
        block = html[pos:end]
        # Find colon, then get first text content (in link or plain)
        colon_match = re.search(r':\s*</span>\s*</span>', block)
        if not colon_match:
            continue
        after_colon = block[colon_match.end():]
        # Get first text: either in <a>text</a> or plain text after >
        value_match = re.search(r'>([^<]+)<', after_colon)
        if not value_match:
            continue
        value = clean_text(value_match.group(1))
        if not value or len(value) < 2:
            continue
        name = attrid.split(":")[-1].replace("_", " ").title()
        if name and name not in kg.attributes:
            kg.attributes[name] = value


# =============================================================================
# Utility Functions
# =============================================================================


def safe_get(data: list[Any], index: int) -> Any:
    """Safely get element from list by index."""
    try:
        return data[index]
    except (TypeError, IndexError):
        return None


def clean_text(text: str) -> str:
    """Clean text: decode HTML entities, strip tags, normalize whitespace."""
    if not text or not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]*>", "", text)
    return re.sub(r"\s+", " ", text).strip()
