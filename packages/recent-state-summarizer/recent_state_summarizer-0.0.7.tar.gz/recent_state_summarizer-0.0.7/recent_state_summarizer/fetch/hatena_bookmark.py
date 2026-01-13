from typing import Generator, TypedDict

import feedparser
import httpx


class BookmarkEntry(TypedDict):
    title: str
    url: str
    description: str


def fetch_hatena_bookmark_rss(
    url: str,
) -> Generator[BookmarkEntry, None, None]:
    """Fetch entries from Hatena Bookmark RSS feed.

    Args:
        url: URL of the Hatena Bookmark RSS feed

    Yields:
        Bookmark entries with title, url, and description
    """
    response = httpx.get(url)
    response.raise_for_status()

    feed = feedparser.parse(response.content)

    for entry in feed.entries:
        yield {
            "title": entry.title,
            "url": entry.link,
            "description": entry.description,
        }
