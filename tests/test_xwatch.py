"""xwatch の feed 解析・message 組み立てのオフライン単体テスト。

外部ネットワーク無しで実行できる。
    python -m pytest tests/           （pytest があれば）
    python tests/test_xwatch.py       （無くてもそのまま実行可）
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xwatch.feed import Post, parse_feed  # noqa: E402
from xwatch.message import build_message  # noqa: E402

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Twitter @fumino_official</title>
<item>
  <title>新しい投稿 &amp; テスト</title>
  <description>&lt;p&gt;本文 &lt;b&gt;太字&lt;/b&gt;&lt;/p&gt;</description>
  <link>https://x.com/fumino_official/status/3</link>
  <guid>https://x.com/fumino_official/status/3</guid>
  <pubDate>Sat, 11 Jul 2026 10:00:00 GMT</pubDate>
</item>
<item>
  <title>ふたつめ</title>
  <link>https://x.com/fumino_official/status/2</link>
  <guid>https://x.com/fumino_official/status/2</guid>
</item>
</channel></rss>""".encode("utf-8")

ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry>
  <id>tag:x,1:9</id>
  <title>アトム投稿</title>
  <content type="html">&lt;p&gt;アトム本文&lt;/p&gt;</content>
  <link rel="alternate" href="https://x.com/fumino_official/status/9"/>
  <published>2026-07-11T10:00:00Z</published>
</entry>
</feed>""".encode("utf-8")


def test_parse_rss():
    posts = parse_feed(RSS)
    assert len(posts) == 2
    first = posts[0]
    assert first.id == "https://x.com/fumino_official/status/3"
    assert first.url == "https://x.com/fumino_official/status/3"
    # HTML タグ除去 & 実体参照デコード。
    assert first.text == "本文 太字"


def test_parse_atom():
    posts = parse_feed(ATOM)
    assert len(posts) == 1
    p = posts[0]
    assert p.id == "tag:x,1:9"
    assert p.url == "https://x.com/fumino_official/status/9"
    assert p.text == "アトム本文"


def test_build_message():
    post = Post(
        id="x1",
        text="投稿本文です",
        url="https://x.com/fumino_official/status/1",
        published="",
    )
    text = build_message(post, "fumino_official")
    assert "@fumino_official" in text
    assert "投稿本文です" in text
    assert "https://x.com/fumino_official/status/1" in text


def test_build_message_truncates_long_text():
    post = Post(id="x1", text="あ" * 1000, url="https://x.com/s/1", published="")
    text = build_message(post, "acct")
    assert "…" in text
    # 400 文字 + 見出し/URL 程度に収まる。
    assert len(text) < 500


def _run_all():
    passed = 0
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS {name}")
                passed += 1
            except AssertionError as exc:
                print(f"  FAIL {name}: {exc}")
                failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
