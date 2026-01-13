"""
Type definitions for Google SERP scraper.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# Time range options for search results
TimeRangeLiteral = Literal["hour", "day", "week", "month", "year"]


class TimeRange(str, Enum):
    """Time range filter for search results."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


# Google country codes (gl parameter) - ISO 3166-1 alpha-2
# Source: https://serpapi.com/google-countries
CountryCode = Literal[
    "af", "al", "dz", "as", "ad", "ao", "ai", "aq", "ag", "ar", "am", "aw", "au", "at", "az",
    "bs", "bh", "bd", "bb", "by", "be", "bz", "bj", "bm", "bt", "bo", "ba", "bw", "bv", "br",
    "io", "bn", "bg", "bf", "bi", "kh", "cm", "ca", "cv", "ky", "cf", "td", "cl", "cn", "cx",
    "cc", "co", "km", "cg", "cd", "ck", "cr", "ci", "hr", "cu", "cy", "cz", "dk", "dj", "dm",
    "do", "ec", "eg", "sv", "gq", "er", "ee", "et", "fk", "fo", "fj", "fi", "fr", "gf", "pf",
    "tf", "ga", "gm", "ge", "de", "gh", "gi", "gr", "gl", "gd", "gp", "gu", "gt", "gn", "gw",
    "gy", "ht", "hm", "va", "hn", "hk", "hu", "is", "in", "id", "ir", "iq", "ie", "il", "it",
    "jm", "jp", "jo", "kz", "ke", "ki", "kp", "kr", "kw", "kg", "la", "lv", "lb", "ls", "lr",
    "ly", "li", "lt", "lu", "mo", "mk", "mg", "mw", "my", "mv", "ml", "mt", "mh", "mq", "mr",
    "mu", "yt", "mx", "fm", "md", "mc", "mn", "ms", "ma", "mz", "mm", "na", "nr", "np", "nl",
    "nc", "nz", "ni", "ne", "ng", "nu", "nf", "mp", "no", "om", "pk", "pw", "ps", "pa", "pg",
    "py", "pe", "ph", "pn", "pl", "pt", "pr", "qa", "re", "ro", "ru", "rw", "sh", "kn", "lc",
    "pm", "vc", "ws", "sm", "st", "sa", "sn", "rs", "sc", "sl", "sg", "sk", "si", "sb", "so",
    "za", "gs", "es", "lk", "sd", "sr", "sj", "sz", "se", "ch", "sy", "tw", "tj", "tz", "th",
    "tl", "tg", "tk", "to", "tt", "tn", "tr", "tm", "tc", "tv", "ug", "ua", "ae", "uk", "gb",
    "us", "um", "uy", "uz", "vu", "ve", "vn", "vg", "vi", "wf", "eh", "ye", "zm", "zw", "gg",
    "je", "im", "me",
]

# Google language codes (hl parameter)
# Source: https://serpapi.com/google-languages
LanguageCode = Literal[
    "af", "ak", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bg", "ca", "zh-cn", "zh-tw",
    "hr", "cs", "da", "nl", "en", "et", "tl", "fi", "fr", "de", "el", "gu", "ha", "he", "hi",
    "hu", "is", "id", "ga", "it", "ja", "kn", "ko", "ku", "ky", "lo", "la", "lv", "ln", "lt",
    "loz", "lg", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "pl", "pt",
    "pt-br", "pt-pt", "ro", "ru", "sr", "es", "es-419", "sw", "sv", "ta", "te", "th", "tr",
    "uk", "ur", "vi", "cy", "yo", "zu",
]


class ResultType(str, Enum):
    """Type of search result."""

    WEB = "web"
    NEWS = "news"
    NAVIGATIONAL = "navigational"
    VIDEO = "video"
    KG_ENTITY = "kg_entity"


class SearchOptions(BaseModel):
    """Search request options."""

    query: str
    country: CountryCode = "us"
    language: LanguageCode = "en"
    location: str | None = None
    time_range: TimeRange | None = None
    autocorrect: bool = True
    page: int = 1
    lite: bool = True


# =============================================================================
# Lite Mode Models (minimal, web-only results)
# =============================================================================


class LiteResult(BaseModel):
    """Lite mode search result - web results only."""

    title: str
    link: str
    snippet: str
    source: str | None = None  # Site/publisher name (e.g., "Wikipedia", "YouTube")


class LiteSearchResult(BaseModel):
    """Lite mode search response - organic results only."""

    results: list[LiteResult] = Field(default_factory=list)


# =============================================================================
# Full Mode Models (all result types, sitelinks, PAA, related, KG)
# =============================================================================


class Sitelink(BaseModel):
    """Sitelink for organic result (includes forum sub-results)."""

    title: str
    link: str
    snippet: str | None = None  # Description text
    date: str | None = None  # For forum-style sitelinks (e.g., "Apr 20, 2023")
    answers: str | None = None  # For forum-style sitelinks (e.g., "160 answers")


class OrganicResult(BaseModel):
    """Full mode organic search result."""

    title: str
    link: str
    snippet: str
    source: str | None = None  # Site/publisher name (e.g., "Wikipedia", "YouTube")
    sitelinks: list[Sitelink] | None = None
    result_type: ResultType | None = None
    channel: str | None = None  # For video results


class PeopleAlsoAsk(BaseModel):
    """People Also Ask question."""

    question: str
    snippet: str | None = None
    link: str | None = None
    title: str | None = None


class RelatedSearch(BaseModel):
    """Related search query."""

    query: str


class KnowledgeGraph(BaseModel):
    """Knowledge Graph panel data."""

    title: str | None = None
    type: str | None = None
    description: str | None = None
    description_source: str | None = None
    description_link: str | None = None
    website: str | None = None
    image_url: str | None = None
    attributes: dict[str, str | list[str]] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Complete search result response."""

    organic: list[OrganicResult] = Field(default_factory=list)
    people_also_ask: list[PeopleAlsoAsk] = Field(default_factory=list)
    related_searches: list[RelatedSearch] = Field(default_factory=list)
    knowledge_graph: KnowledgeGraph | None = None
