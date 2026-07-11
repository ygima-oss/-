"""X（旧Twitter）投稿の新着を検知して LINE に通知するシステム。

X API を使わず、RSS 化した投稿フィード（RSSHub / Nitter などの無料
インスタンス）を GitHub Actions で定期取得し、前回までに見た投稿と
差分を取って新着だけを LINE に push する。RSS の URL は環境変数
``X_RSS_URL`` で差し替え可能なので、インスタンスが停止しても設定を
変えるだけで復旧できる。
"""

__all__ = [
    "config",
    "feed",
    "state",
    "message",
    "notify",
]
