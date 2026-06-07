"""ゴールデンクロス通知システム。

日米株のゴールデン/デッドクロスを検知し、市場環境（VIX/SOX/ドル円/
Fear & Greed など）と合わせて LINE に通知する。
"""

__all__ = [
    "indicators",
    "data",
    "fear_greed",
    "message",
    "notify",
    "config",
]
