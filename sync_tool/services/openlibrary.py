"""OpenLibrary Search API client (FR-007, FR-010, FR-011)."""
import urllib.parse
from typing import Optional

import requests

from sync_tool.models import DatabaseMatch


def build_search_url(endpoint: str, title: str, author: Optional[str] = None) -> str:
    params = {
        "title": title,
        "fields": "title,author_name,cover_i,key",
    }
    if author:
        params["author"] = author
    return f"{endpoint}?{urllib.parse.urlencode(params)}"


def cover_url(cover_i: int) -> str:
    return f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"


def parse_search_response(data: dict, endpoint: str) -> Optional[DatabaseMatch]:
    docs = data.get("docs")
    if not docs:
        return None
    top = docs[0]
    matched_title = top.get("title", "")
    authors = top.get("author_name")
    matched_author = authors[0] if authors else None
    cover = cover_url(top["cover_i"]) if top.get("cover_i") else None
    # Simple confidence based on presence of expected fields
    score = 0.0
    if matched_title:
        score += 0.4
    if matched_author:
        score += 0.3
    if cover:
        score += 0.3
    return DatabaseMatch(
        confidence=score,
        matched_title=matched_title,
        matched_author=matched_author,
        cover_url=cover,
    )


class OpenLibraryClient:
    def __init__(self, endpoint: str, timeout: int = 10, session: Optional[requests.Session] = None):
        self.endpoint = endpoint
        self.timeout = timeout
        self._session = session or requests.Session()

    def search(self, title: str, author: Optional[str] = None) -> Optional[DatabaseMatch]:
        url = build_search_url(self.endpoint, title, author)
        resp = self._session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return parse_search_response(data, self.endpoint)
