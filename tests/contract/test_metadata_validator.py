"""Contract tests for OpenLibrary client (T025)."""
import pytest

from sync_tool.services.openlibrary import build_search_url, parse_search_response


class TestBuildSearchUrl:
    def test_includes_title_and_author(self):
        url = build_search_url(
            "https://openlibrary.org/search.json",
            title="Le Petit Prince",
            author="Antoine de Saint-Exupéry",
        )
        assert "title=Le+Petit+Prince" in url or "title=Le%20Petit%20Prince" in url
        assert "author=Antoine+de+Saint-Exup%C3%A9ry" in url or "author=Antoine%20de%20Saint-Exup%C3%A9ry" in url

    def test_includes_fields_parameter(self):
        url = build_search_url(
            "https://openlibrary.org/search.json",
            title="Moby Dick",
            author="Herman Melville",
        )
        assert "fields=" in url
        assert "title" in url
        assert "author_name" in url
        assert "cover_i" in url
        assert "key" in url

    def test_omits_author_when_none(self):
        url = build_search_url("https://openlibrary.org/search.json", title="Test")
        assert "author=" not in url


class TestParseSearchResponse:
    def test_parses_top_match(self):
        data = {
            "numFound": 5,
            "docs": [
                {"title": "Le Petit Prince", "author_name": ["Antoine de Saint-Exupéry"], "cover_i": 123, "key": "/works/OL1W"},
                {"title": "Other", "author_name": ["Other Author"], "cover_i": 456, "key": "/works/OL2W"},
            ],
        }
        match = parse_search_response(data, "https://openlibrary.org/search.json")
        assert match is not None
        assert match.matched_title == "Le Petit Prince"
        assert match.matched_author == "Antoine de Saint-Exupéry"
        assert match.cover_url == "https://covers.openlibrary.org/b/id/123-L.jpg"
        assert match.confidence > 0

    def test_returns_none_on_empty_docs(self):
        assert parse_search_response({"numFound": 0, "docs": []}, "...") is None

    def test_returns_none_on_missing_docs_key(self):
        assert parse_search_response({"numFound": 0}, "...") is None

    def test_handles_missing_author_name(self):
        data = {
            "numFound": 1,
            "docs": [{"title": "Some Book", "cover_i": 789, "key": "/works/OL3W"}],
        }
        match = parse_search_response(data, "...")
        assert match is not None
        assert match.matched_author is None

    def test_handles_missing_cover_i(self):
        data = {
            "numFound": 1,
            "docs": [{"title": "Some Book", "author_name": ["Author"], "key": "/works/OL4W"}],
        }
        match = parse_search_response(data, "...")
        assert match is not None
        assert match.cover_url is None
