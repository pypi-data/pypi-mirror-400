from collections.abc import Generator
from typing import TypedDict

import httpx
from bs4 import BeautifulSoup


class TitleTag(TypedDict):
    title: str
    url: str


def _fetch(url: str) -> str:
    response = httpx.get(url)
    response.raise_for_status()
    return response.text


def fetch_adventar_calendar(url: str) -> Generator[TitleTag, None, None]:
    """Fetch article titles and URLs from Adventar calendar.

    Args:
        url: Adventar calendar URL (e.g., https://adventar.org/calendars/11474)

    Yields:
        TitleTag dictionaries containing title and url
    """
    raw_html = _fetch(url)
    yield from _parse_titles(raw_html)


def _parse_titles(raw_html: str) -> Generator[TitleTag, None, None]:
    """Parse titles from Adventar calendar HTML."""
    soup = BeautifulSoup(raw_html, "html.parser")
    entry_list = soup.find("ul", class_="EntryList")
    if not entry_list:
        return

    items = entry_list.find_all("li", class_="item")
    for item in items:
        article = item.find("div", class_="article")
        if not article:
            continue

        link_div = article.find("div", class_="link")
        if not link_div:
            continue

        link = link_div.find("a")
        if not link or "href" not in link.attrs:
            continue

        title_div = link_div.find_next_sibling("div")
        if title_div and title_div.text.strip():
            title = title_div.text.strip()
        else:
            title = link.text.strip()

        yield {"title": title, "url": link["href"]}
