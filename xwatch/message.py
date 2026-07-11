"""LINE 通知用のメッセージ本文を組み立てる。"""

from __future__ import annotations

from .feed import Post

# 本文が長すぎると読みにくいので、投稿テキストはこの長さで丸める。
_MAX_TEXT = 400


def build_message(post: Post, account: str) -> str:
    lines = [f"🐦 X に新しい投稿 @{account}", ""]

    text = post.text
    if len(text) > _MAX_TEXT:
        text = text[: _MAX_TEXT - 1] + "…"
    if text:
        lines.append(text)
        lines.append("")

    if post.url:
        lines.append(post.url)

    return "\n".join(lines).rstrip()
