from collections.abc import Generator
from typing import TypedDict
from urllib.request import urlopen

from bs4 import BeautifulSoup

PARSE_HATENABLOG_KWARGS = {"name": "a", "attrs": {"class": "entry-title-link"}}


class TitleTag(TypedDict):
    title: str
    url: str


def _fetch(url: str) -> str:
    with urlopen(url) as res:
        return res.read()


def _fetch_titles(url: str) -> Generator[TitleTag, None, None]:
    raw_html = _fetch(url)
    yield from _parse_titles(raw_html)

    soup = BeautifulSoup(raw_html, "html.parser")
    next_link = soup.find("a", class_="test-pager-next")
    if next_link and "href" in next_link.attrs:
        next_url = next_link["href"]
        print(f"Next page found, fetching... {next_url}")
        yield from _fetch_titles(next_url)


def _parse_titles(raw_html: str) -> Generator[TitleTag, None, None]:
    soup = BeautifulSoup(raw_html, "html.parser")
    body = soup.body
    title_tags = body.find_all(**PARSE_HATENABLOG_KWARGS)
    for title_tag in title_tags:
        yield {"title": title_tag.text, "url": title_tag["href"]}
