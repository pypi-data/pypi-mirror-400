import json
from unittest.mock import patch

import pytest
import responses

from recent_state_summarizer.__main__ import main


@pytest.fixture
def blog_server(httpserver):
    httpserver.expect_request("/archive/2025").respond_with_data(
        f"""\
<!DOCTYPE html>
<html>
  <body>
    <div class="archive-entries">
      <section class="archive-entry">
        <a class="entry-title-link" href="{httpserver.url_for('/post1')}">Pythonのテストについて学ぶ</a>
      </section>
      <section class="archive-entry">
        <a class="entry-title-link" href="{httpserver.url_for('/post2')}">pytest入門</a>
      </section>
      <section class="archive-entry">
        <a class="entry-title-link" href="{httpserver.url_for('/post3')}">モックとフィクスチャの使い方</a>
      </section>
    </div>
  </body>
</html>"""
    )
    return httpserver


@responses.activate
def test_main_success_path(monkeypatch, blog_server, capsys):
    monkeypatch.setattr("openai.api_key", "sk-test-dummy-key-for-testing")

    monkeypatch.setattr(
        "sys.argv", ["omae-douyo", blog_server.url_for("/archive/2025")]
    )

    expected_summary = """\
このユーザーは最近、Pythonのテストについて学習しています。
具体的には、pytestの入門やモック・フィクスチャの使い方について記事を書いています。
テストコードを書くスキルを向上させようとしていることが伺えます。"""

    responses.add(
        responses.POST,
        "https://api.openai.com/v1/chat/completions",
        json={
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": expected_summary,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        },
        status=200,
        headers={"Content-Type": "application/json"},
    )

    main()

    captured = capsys.readouterr()
    assert expected_summary in captured.out

    assert len(responses.calls) == 1
    api_call = responses.calls[0]
    assert api_call.request.url == "https://api.openai.com/v1/chat/completions"
    assert api_call.request.method == "POST"
    request_body = json.loads(api_call.request.body)
    assert (
        "- Pythonのテストについて学ぶ\n- pytest入門\n- モックとフィクスチャの使い方"
        in request_body["messages"][0]["content"]
    )


@patch("recent_state_summarizer.__main__.fetch_main")
def test_fetch_subcommand(fetch_main, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["omae-douyo", "fetch", "https://example.com", "articles.jsonl"],
    )

    main()

    fetch_main.assert_called_once_with(
        "https://example.com", "articles.jsonl", save_as_title_list=False
    )
