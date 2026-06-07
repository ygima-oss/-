"""LINE Messaging API への通知。

LINE Notify は 2025/3 で終了したため、Messaging API の push / broadcast
を使う。環境変数:
    LINE_CHANNEL_ACCESS_TOKEN … 必須。チャネルアクセストークン(長期)
    LINE_TO                   … 任意。送信先 userId。未設定なら broadcast。
"""

from __future__ import annotations

import os
from typing import Optional

import requests

_PUSH_URL = "https://api.line.me/v2/bot/message/push"
_BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"

# LINE のテキストメッセージ上限は 5000 文字。
_MAX_LEN = 4900


def send_line(
    text: str,
    token: Optional[str] = None,
    to: Optional[str] = None,
    timeout: int = 15,
) -> None:
    """LINE にテキストを送信する。

    ``to`` が指定されていれば push、無ければ broadcast を使う。
    """
    token = token or os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    to = to if to is not None else os.environ.get("LINE_TO")
    if not token:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")

    if len(text) > _MAX_LEN:
        text = text[: _MAX_LEN - 1] + "…"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    message = {"messages": [{"type": "text", "text": text}]}

    if to:
        url = _PUSH_URL
        message["to"] = to
    else:
        url = _BROADCAST_URL

    resp = requests.post(url, headers=headers, json=message, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(
            f"LINE 送信に失敗しました: {resp.status_code} {resp.text}"
        )
