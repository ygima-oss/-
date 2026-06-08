"""設定ファイル(watchlist.yaml)の読み込み。"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import yaml

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "watchlist.yaml"
)


class Config:
    def __init__(self, raw: Dict[str, Any]):
        self._raw = raw

    @property
    def short_period(self) -> int:
        return int(self._raw.get("sma", {}).get("short", 25))

    @property
    def long_period(self) -> int:
        return int(self._raw.get("sma", {}).get("long", 75))

    @property
    def jp_stocks(self) -> List[Dict[str, str]]:
        return list(self._raw.get("stocks", {}).get("jp", []) or [])

    @property
    def us_stocks(self) -> List[Dict[str, str]]:
        return list(self._raw.get("stocks", {}).get("us", []) or [])

    @property
    def all_stocks(self) -> List[Dict[str, str]]:
        return self.jp_stocks + self.us_stocks

    @property
    def market_indicators(self) -> List[Dict[str, str]]:
        return list(self._raw.get("market_indicators", []) or [])


def load_config(path: str = DEFAULT_CONFIG_PATH) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return Config(raw)
