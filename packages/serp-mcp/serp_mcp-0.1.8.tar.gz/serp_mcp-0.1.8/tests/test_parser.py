"""Tests for SERP parser utilities."""

from serp_mcp.parser import clean_text


class TestCleanText:
    """Tests for clean_text utility."""

    def test_html_entities(self):
        assert clean_text("&amp;") == "&"
        assert clean_text("&quot;hello&quot;") == '"hello"'
        # Note: &lt;test&gt; becomes <test> which is then stripped as a tag

    def test_strip_tags(self):
        assert clean_text("<b>bold</b>") == "bold"
        assert clean_text("<a href='x'>link</a>") == "link"

    def test_normalize_whitespace(self):
        assert clean_text("  multiple   spaces  ") == "multiple spaces"
        assert clean_text("line\n\nbreak") == "line break"

    def test_empty_input(self):
        assert clean_text("") == ""
        assert clean_text(None) == ""
