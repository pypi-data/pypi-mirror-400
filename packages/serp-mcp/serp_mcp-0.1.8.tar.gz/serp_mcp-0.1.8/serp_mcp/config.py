"""
Configuration and URL building for Google SERP scraper.
"""

import base64
from urllib.parse import urlencode

from serp_mcp.types import SearchOptions, TimeRange
from serp_mcp.uule_pb2 import Uule  # type: ignore

# Time range to tbs parameter mapping
TIME_RANGE_TBS: dict[TimeRange, str] = {
    TimeRange.HOUR: "qdr:h",
    TimeRange.DAY: "qdr:d",
    TimeRange.WEEK: "qdr:w",
    TimeRange.MONTH: "qdr:m",
    TimeRange.YEAR: "qdr:y",
}


def encode_uule(canonical_name: str) -> str:
    """
    Encode a location to UULE format using protobuf.

    Proto schema (see uule.proto):
        message Uule {
            optional int32 role = 1;           // always 2
            optional int32 producer = 2;       // always 32
            optional string canonicalName = 4;
        }

    Encoding steps:
        1. Encode protobuf with role=2, producer=32, canonicalName=canonical_name
        2. Base64 encode (URL-safe)
        3. Prepend "w " (space becomes + when URL encoded)
    """
    uule = Uule()
    uule.role = 2
    uule.producer = 32
    uule.canonicalName = canonical_name

    # URL-safe base64
    b64 = base64.urlsafe_b64encode(uule.SerializeToString()).decode()

    # Prepend "w " - space will become "+" when URL encoded by urlencode()
    return "w " + b64


def build_search_url(options: SearchOptions) -> str:
    """Build the Google search URL from options."""
    params: dict[str, str] = {
        "q": options.query,
        "gl": options.country,
        "hl": options.language,
        "pws": "0",  # No personalized search
    }

    # Lite mode: web results only (smaller response, no PAA/related/sitelinks)
    if options.lite:
        params["udm"] = "14"

    # Pagination
    if options.page > 1:
        params["start"] = str((options.page - 1) * 10)

    # Autocorrect (nfpr=1 disables autocorrect)
    if not options.autocorrect:
        params["nfpr"] = "1"

    # Time range filter
    if options.time_range:
        params["tbs"] = TIME_RANGE_TBS[options.time_range]

    # Location (uule) - protobuf encoded
    if options.location:
        params["uule"] = encode_uule(options.location)

    return f"https://www.google.com/search?{urlencode(params)}"

