"""環境変数からの設定読み込み。

無料 RSS ソースはインスタンスが停止しやすいため、フィードの URL を
シークレット（環境変数）で外から差し替えられるようにしている。

環境変数:
    X_RSS_URL     … 必須。監視対象アカウントの RSS フィード URL。
                    例) https://rsshub.app/twitter/user/fumino_official
                        https://<nitter-instance>/fumino_official/rss
    X_ACCOUNT     … 任意。通知本文に出す表示用のアカウント名。
                    既定 "fumino_official"。
    X_MAX_NOTIFY  … 任意。1 回の実行で送る新着の最大件数。既定 5。
                    まとめて大量に検知したときの連投を防ぐ上限。
"""

from __future__ import annotations

import os

DEFAULT_STATE_PATH = os.path.join(
    os.path.dirname(__file__), "state", "seen.json"
)


class Config:
    @property
    def rss_url(self) -> str:
        url = os.environ.get("X_RSS_URL", "").strip()
        if not url:
            raise RuntimeError(
                "X_RSS_URL が設定されていません。監視対象アカウントの "
                "RSS フィード URL を環境変数に設定してください。"
            )
        return url

    @property
    def account(self) -> str:
        return os.environ.get("X_ACCOUNT", "fumino_official").strip()

    @property
    def max_notify(self) -> int:
        try:
            return max(1, int(os.environ.get("X_MAX_NOTIFY", "5")))
        except ValueError:
            return 5

    @property
    def state_path(self) -> str:
        return os.environ.get("X_STATE_PATH", DEFAULT_STATE_PATH)


def load_config() -> Config:
    return Config()
