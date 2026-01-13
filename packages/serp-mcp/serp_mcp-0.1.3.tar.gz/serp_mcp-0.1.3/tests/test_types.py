"""Tests for type definitions and validation."""

import pytest
from pydantic import ValidationError

from serp_mcp.types import (
    LiteResult,
    LiteSearchResult,
    OrganicResult,
    ResultType,
    SearchOptions,
    TimeRange,
)


class TestSearchOptionsValidation:
    """Tests for SearchOptions validation."""

    def test_valid_defaults(self):
        opts = SearchOptions(query="test")
        assert opts.country == "us"
        assert opts.language == "en"
        assert opts.page == 1
        assert opts.autocorrect is True
        assert opts.lite is True

    def test_valid_country_codes(self):
        for country in ["us", "gb", "de", "jp", "fr", "ca", "au"]:
            opts = SearchOptions(query="test", country=country)
            assert opts.country == country

    def test_invalid_country_code(self):
        with pytest.raises(ValidationError) as exc_info:
            SearchOptions(query="test", country="xyz")
        assert "country" in str(exc_info.value)

    def test_valid_language_codes(self):
        for lang in ["en", "de", "ja", "fr", "es", "zh-cn", "pt-br"]:
            opts = SearchOptions(query="test", language=lang)
            assert opts.language == lang

    def test_invalid_language_code(self):
        with pytest.raises(ValidationError) as exc_info:
            SearchOptions(query="test", language="xyz")
        assert "language" in str(exc_info.value)

    def test_time_range_enum(self):
        for tr in TimeRange:
            opts = SearchOptions(query="test", time_range=tr)
            assert opts.time_range == tr

    def test_time_range_none_by_default(self):
        opts = SearchOptions(query="test")
        assert opts.time_range is None

    def test_location_optional(self):
        opts = SearchOptions(query="test")
        assert opts.location is None

        opts = SearchOptions(query="test", location="New York")
        assert opts.location == "New York"

    def test_page_positive(self):
        opts = SearchOptions(query="test", page=5)
        assert opts.page == 5


class TestTimeRange:
    """Tests for TimeRange enum."""

    def test_all_values(self):
        assert TimeRange.HOUR.value == "hour"
        assert TimeRange.DAY.value == "day"
        assert TimeRange.WEEK.value == "week"
        assert TimeRange.MONTH.value == "month"
        assert TimeRange.YEAR.value == "year"

    def test_from_string(self):
        assert TimeRange("hour") == TimeRange.HOUR
        assert TimeRange("day") == TimeRange.DAY


class TestResultType:
    """Tests for ResultType enum."""

    def test_all_values(self):
        assert ResultType.WEB.value == "web"
        assert ResultType.NEWS.value == "news"
        assert ResultType.VIDEO.value == "video"
        assert ResultType.NAVIGATIONAL.value == "navigational"
        assert ResultType.KG_ENTITY.value == "kg_entity"


class TestLiteResult:
    """Tests for LiteResult model."""

    def test_valid_result(self):
        result = LiteResult(
            title="Test Title",
            link="https://example.com",
            snippet="Test snippet",
        )
        assert result.title == "Test Title"
        assert result.link == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.source is None

    def test_with_source(self):
        result = LiteResult(
            title="Test",
            link="https://example.com",
            snippet="Snippet",
            source="Example",
        )
        assert result.source == "Example"

    def test_extra_fields_ignored(self):
        result = LiteResult(
            title="Test",
            link="https://example.com",
            snippet="Snippet",
            extra_field="ignored",
        )
        assert not hasattr(result, "extra_field")


class TestLiteSearchResult:
    """Tests for LiteSearchResult model."""

    def test_empty_results(self):
        result = LiteSearchResult()
        assert result.results == []

    def test_with_results(self):
        results = [
            LiteResult(title="A", link="https://a.com", snippet="A"),
            LiteResult(title="B", link="https://b.com", snippet="B"),
        ]
        search_result = LiteSearchResult(results=results)
        assert len(search_result.results) == 2

    def test_model_dump_excludes_none(self):
        result = LiteResult(
            title="Test",
            link="https://example.com",
            snippet="Snippet",
        )
        dumped = result.model_dump(exclude_none=True)
        assert "source" not in dumped


class TestOrganicResult:
    """Tests for OrganicResult model."""

    def test_valid_result(self):
        result = OrganicResult(
            title="Test",
            link="https://example.com",
            snippet="Snippet",
        )
        assert result.title == "Test"
        assert result.sitelinks is None
        assert result.result_type is None
        assert result.channel is None

    def test_with_result_type(self):
        result = OrganicResult(
            title="Test",
            link="https://example.com",
            snippet="Snippet",
            result_type=ResultType.VIDEO,
            channel="Test Channel",
        )
        assert result.result_type == ResultType.VIDEO
        assert result.channel == "Test Channel"
