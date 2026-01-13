"""Tests for core functionality."""

import pytest

from serp_mcp.core import build_search_options, parse_time_range
from serp_mcp.types import SearchOptions, TimeRange


class TestParseTimeRange:
    """Tests for time range parsing."""

    def test_valid_time_ranges(self):
        assert parse_time_range("hour") == TimeRange.HOUR
        assert parse_time_range("day") == TimeRange.DAY
        assert parse_time_range("week") == TimeRange.WEEK
        assert parse_time_range("month") == TimeRange.MONTH
        assert parse_time_range("year") == TimeRange.YEAR

    def test_case_insensitive(self):
        assert parse_time_range("HOUR") == TimeRange.HOUR
        assert parse_time_range("Day") == TimeRange.DAY
        assert parse_time_range("WEEK") == TimeRange.WEEK

    def test_none_input(self):
        assert parse_time_range(None) is None

    def test_empty_string(self):
        assert parse_time_range("") is None

    def test_invalid_time_range(self):
        with pytest.raises(ValueError) as exc_info:
            parse_time_range("invalid")
        assert "Invalid time range" in str(exc_info.value)
        assert "hour, day, week, month, year" in str(exc_info.value)


class TestBuildSearchOptions:
    """Tests for build_search_options function."""

    def test_basic_options(self):
        opts = build_search_options(query="test")
        assert opts.query == "test"
        assert opts.country == "us"
        assert opts.language == "en"

    def test_all_parameters(self):
        opts = build_search_options(
            query="restaurants",
            country="gb",
            language="en",
            location="London,England,United Kingdom",
            time_range="week",
            autocorrect=False,
            page=2,
            lite=True,
        )
        assert opts.query == "restaurants"
        assert opts.country == "gb"
        assert opts.language == "en"
        assert opts.location == "London,England,United Kingdom"
        assert opts.time_range == TimeRange.WEEK
        assert opts.autocorrect is False
        assert opts.page == 2
        assert opts.lite is True

    def test_time_range_string_conversion(self):
        opts = build_search_options(query="test", time_range="day")
        assert opts.time_range == TimeRange.DAY

    def test_time_range_none(self):
        opts = build_search_options(query="test")
        assert opts.time_range is None

    def test_invalid_country_raises(self):
        with pytest.raises(Exception):
            build_search_options(query="test", country="invalid")

    def test_invalid_language_raises(self):
        with pytest.raises(Exception):
            build_search_options(query="test", language="invalid")

    def test_invalid_time_range_raises(self):
        with pytest.raises(ValueError):
            build_search_options(query="test", time_range="invalid")

    def test_returns_search_options(self):
        opts = build_search_options(query="test")
        assert isinstance(opts, SearchOptions)



