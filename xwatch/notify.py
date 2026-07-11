"""LINE への通知。

LINE 送信ロジックは goldencross 側と同一なので、そのまま再利用する。
環境変数 LINE_CHANNEL_ACCESS_TOKEN / LINE_TO を参照する。
"""

from __future__ import annotations

from goldencross.notify import send_line  # noqa: F401

__all__ = ["send_line"]
