"""CNN Fear & Greed Index の取得。

CNN の非公式 JSON エンドポイントを利用する。仕様変更や失敗時には
None を返し、通知全体は止めない（あくまで添付情報のため）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

# CNN の内部 API。User-Agent が無いと 418 を返すため付与する。
_URL = "https://production.cnn.com/index/fearandgreed/graphdata"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# スコア → 日本語ラベル
_RATING_JA = {
    "extreme fear": "極度の恐怖",
    "fear": "恐怖",
    "neutral": "中立",
    "greed": "貪欲",
    "extreme greed": "極度の貪欲",
}


@dataclass
class FearGreed:
    score: float
    rating: str  # 英語ラベル

    @property
    def rating_ja(self) -> str:
        return _RATING_JA.get(self.rating.lower(), self.rating)


def fetch_fear_greed(timeout: int = 10) -> Optional[FearGreed]:
    try:
        resp = requests.get(_URL, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        fg = data.get("fear_and_greed", {})
        score = fg.get("score")
        rating = fg.get("rating")
        if score is None:
            return None
        return FearGreed(score=float(score), rating=str(rating or ""))
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] Fear & Greed の取得に失敗: {exc}")
        return None
