from __future__ import annotations

import argparse
import json
import logging
import textwrap
from collections.abc import Iterable
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse

from recent_state_summarizer.fetch.adventar import (
    TitleTag,
    fetch_adventar_calendar,
)
from recent_state_summarizer.fetch.hatena_blog import _fetch_titles
from recent_state_summarizer.fetch.hatena_bookmark import (
    fetch_hatena_bookmark_rss,
)

logger = logging.getLogger(__name__)


class URLType(Enum):
    """Type of URL for fetching."""

    HATENA_BLOG = "hatena_blog"
    HATENA_BOOKMARK_RSS = "hatena_bookmark_rss"
    ADVENTAR = "adventar"
    UNKNOWN = "unknown"


def _detect_url_type(url: str) -> URLType:
    """Detect the type of URL to determine fetch strategy.

    Args:
        url: URL to analyze

    Returns:
        URLType indicating the fetch strategy to use
    """
    parsed = urlparse(url)
    if (
        parsed.netloc == "b.hatena.ne.jp"
        and parsed.path.startswith("/entrylist/")
        and parsed.path.endswith(".rss")
    ):
        return URLType.HATENA_BOOKMARK_RSS

    if "/calendars/" in parsed.path or "adventar.org" in parsed.netloc:
        return URLType.ADVENTAR

    if "hatenablog.com" in url or "hateblo.jp" in url or "/archive/" in parsed.path:
        return URLType.HATENA_BLOG

    return URLType.UNKNOWN


def _select_fetcher(url_type):
    match url_type:
        case URLType.HATENA_BOOKMARK_RSS:
            return fetch_hatena_bookmark_rss
        case URLType.HATENA_BLOG:
            return _fetch_titles
        case URLType.ADVENTAR:
            return fetch_adventar_calendar
        case _:
            logger.warning("Unknown URL type: %s", url_type)
            return _fetch_titles  # To pass tests


def _main(
    url: str, save_path: str | Path, *, save_as_title_list: bool
) -> None:
    url_type = _detect_url_type(url)
    fetcher = _select_fetcher(url_type)
    title_tags = fetcher(url)
    if save_as_title_list:
        contents = _as_bullet_list(
            title_tag["title"] for title_tag in title_tags
        )
    else:
        contents = _as_json(title_tags)
    _save(save_path, contents)


def _as_bullet_list(titles: Iterable[str]) -> str:
    return "\n".join(f"- {title}" for title in titles)


def _as_json(title_tags: Iterable[TitleTag]) -> str:
    return "\n".join(
        json.dumps(title_tag, ensure_ascii=False) for title_tag in title_tags
    )


def _save(path: str | Path, contents: str) -> None:
    with open(path, "w", encoding="utf8", newline="") as f:
        f.write(contents)


def build_parser(add_help: bool = True) -> argparse.ArgumentParser:
    help_message = """
    Retrieve the titles and URLs of articles from a web page specified by URL
    and save them as JSON Lines format.

    Support:
        - はてなブログ（Hatena blog）
        - はてなブックマークRSS
        - Adventar

    Example:
        python -m recent_state_summarizer.fetch \\
          https://awesome.hatenablog.com/archive/2023 articles.jsonl
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(help_message),
        add_help=add_help,
    )
    parser.add_argument("url", help="URL of archive page")
    parser.add_argument("save_path", help="Local file path")
    parser.add_argument(
        "--as-title-list",
        action="store_true",
        default=False,
        help="Save as title-only bullet list instead of JSON Lines",
    )
    return parser


def cli():
    parser = build_parser()
    args = parser.parse_args()

    _main(args.url, args.save_path, save_as_title_list=args.as_title_list)


if __name__ == "__main__":
    cli()
