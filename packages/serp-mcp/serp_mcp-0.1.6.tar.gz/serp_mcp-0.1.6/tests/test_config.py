"""Tests for configuration and URL building."""

import base64

from serp_mcp.config import TIME_RANGE_TBS, build_search_url, encode_uule
from serp_mcp.types import SearchOptions, TimeRange
from serp_mcp.uule_pb2 import Uule


class TestEncodeUule:
    """Tests for UULE protobuf encoding."""

    def test_returns_string_starting_with_w_space(self):
        result = encode_uule("New York")
        assert result.startswith("w ")

    def test_encodes_simple_location(self):
        result = encode_uule("London")
        assert "w " in result
        # Should be base64 after "w "
        b64_part = result[2:]
        # Should be valid base64
        decoded = base64.urlsafe_b64decode(b64_part)
        assert len(decoded) > 0

    def test_protobuf_structure(self):
        """Verify the protobuf message has correct fields."""
        canonical_name = "New York,New York,United States"
        result = encode_uule(canonical_name)
        b64_part = result[2:]
        proto_bytes = base64.urlsafe_b64decode(b64_part)

        # Parse the protobuf
        uule = Uule()
        uule.ParseFromString(proto_bytes)

        assert uule.role == 2
        assert uule.producer == 32
        assert uule.canonicalName == canonical_name

    def test_handles_unicode(self):
        result = encode_uule("東京,日本")
        b64_part = result[2:]
        proto_bytes = base64.urlsafe_b64decode(b64_part)

        uule = Uule()
        uule.ParseFromString(proto_bytes)
        assert uule.canonicalName == "東京,日本"

    def test_handles_special_characters(self):
        result = encode_uule("São Paulo,Brazil")
        b64_part = result[2:]
        proto_bytes = base64.urlsafe_b64decode(b64_part)

        uule = Uule()
        uule.ParseFromString(proto_bytes)
        assert uule.canonicalName == "São Paulo,Brazil"


class TestBuildSearchUrl:
    """Tests for search URL building."""

    def test_basic_url(self):
        options = SearchOptions(query="test")
        url = build_search_url(options)

        assert url.startswith("https://www.google.com/search?")
        assert "q=test" in url
        assert "gl=us" in url
        assert "hl=en" in url
        assert "pws=0" in url

    def test_lite_mode_adds_udm(self):
        options = SearchOptions(query="test", lite=True)
        url = build_search_url(options)

        assert "udm=14" in url

    def test_no_udm_without_lite(self):
        options = SearchOptions(query="test", lite=False)
        url = build_search_url(options)

        assert "udm=" not in url

    def test_pagination(self):
        options = SearchOptions(query="test", page=2)
        url = build_search_url(options)

        assert "start=10" in url

    def test_pagination_page_3(self):
        options = SearchOptions(query="test", page=3)
        url = build_search_url(options)

        assert "start=20" in url

    def test_no_start_for_page_1(self):
        options = SearchOptions(query="test", page=1)
        url = build_search_url(options)

        assert "start=" not in url

    def test_autocorrect_disabled(self):
        options = SearchOptions(query="test", autocorrect=False)
        url = build_search_url(options)

        assert "nfpr=1" in url

    def test_autocorrect_enabled_by_default(self):
        options = SearchOptions(query="test")
        url = build_search_url(options)

        assert "nfpr=" not in url

    def test_time_range_day(self):
        options = SearchOptions(query="test", time_range=TimeRange.DAY)
        url = build_search_url(options)

        assert "tbs=qdr%3Ad" in url or "tbs=qdr:d" in url

    def test_time_range_week(self):
        options = SearchOptions(query="test", time_range=TimeRange.WEEK)
        url = build_search_url(options)

        assert "tbs=qdr%3Aw" in url or "tbs=qdr:w" in url

    def test_all_time_ranges(self):
        for time_range in TimeRange:
            options = SearchOptions(query="test", time_range=time_range)
            url = build_search_url(options)
            expected_tbs = TIME_RANGE_TBS[time_range]
            assert expected_tbs.replace(":", "%3A") in url or expected_tbs in url

    def test_location_adds_uule(self):
        options = SearchOptions(query="pizza", location="New York,New York,United States")
        url = build_search_url(options)

        assert "uule=w+" in url

    def test_country_code(self):
        options = SearchOptions(query="test", country="de")
        url = build_search_url(options)

        assert "gl=de" in url

    def test_language_code(self):
        options = SearchOptions(query="test", language="ja")
        url = build_search_url(options)

        assert "hl=ja" in url

    def test_query_encoding(self):
        options = SearchOptions(query="apple inc")
        url = build_search_url(options)

        assert "q=apple+inc" in url or "q=apple%20inc" in url

    def test_complex_query(self):
        options = SearchOptions(
            query="restaurants",
            country="gb",
            language="en",
            location="London,England,United Kingdom",
            time_range=TimeRange.MONTH,
            page=2,
            lite=True,
        )
        url = build_search_url(options)

        assert "q=restaurants" in url
        assert "gl=gb" in url
        assert "hl=en" in url
        assert "udm=14" in url
        assert "start=10" in url
        assert "uule=w+" in url
        assert "tbs=" in url
