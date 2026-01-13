from unittest.mock import patch

from recent_state_summarizer.fetch import URLType, _detect_url_type, cli


@patch("recent_state_summarizer.fetch._main")
class TestCli:
    def test_default_as_json(self, fetch_main, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            [
                "recent_state_summarizer.fetch",
                "https://example.com",
                "output.jsonl",
            ],
        )

        cli()

        fetch_main.assert_called_once_with(
            "https://example.com", "output.jsonl", save_as_title_list=False
        )

    def test_as_title_list(self, fetch_main, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            [
                "recent_state_summarizer.fetch",
                "https://example.com",
                "output.txt",
                "--as-title-list",
            ],
        )

        cli()

        fetch_main.assert_called_once_with(
            "https://example.com", "output.txt", save_as_title_list=True
        )


class TestDetectUrlType:
    def test_hatena_bookmark_rss(self):
        url = "https://b.hatena.ne.jp/entrylist/it.rss"
        assert _detect_url_type(url) == URLType.HATENA_BOOKMARK_RSS

    def test_hatena_blog_hatenablog_com(self):
        url = "https://example.hatenablog.com/archive/2023"
        assert _detect_url_type(url) == URLType.HATENA_BLOG

    def test_hatena_blog_hateblo_jp(self):
        url = "https://example.hateblo.jp/archive/2023"
        assert _detect_url_type(url) == URLType.HATENA_BLOG

    def test_unknown_url(self):
        url = "https://example.com/blog"
        assert _detect_url_type(url) == URLType.UNKNOWN
