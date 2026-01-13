"""
Core functionality for building search options.
"""

from serp_mcp.types import CountryCode, LanguageCode, SearchOptions, TimeRange


def parse_time_range(time_range: str | None) -> TimeRange | None:
    """Parse time range string to TimeRange enum."""
    if not time_range:
        return None
    try:
        return TimeRange(time_range.lower())
    except ValueError:
        raise ValueError(
            f"Invalid time range: {time_range}. Valid options: hour, day, week, month, year"
        )


def build_search_options(
    query: str,
    country: CountryCode = "us",
    language: LanguageCode = "en",
    location: str | None = None,
    time_range: str | None = None,
    autocorrect: bool = True,
    page: int = 1,
    lite: bool = False,
) -> SearchOptions:
    """Build SearchOptions with validation."""
    parsed_time_range = parse_time_range(time_range)

    return SearchOptions(
        query=query,
        country=country,
        language=language,
        location=location,
        time_range=parsed_time_range,
        autocorrect=autocorrect,
        page=page,
        lite=lite,
    )
