"""yfinance を使った株価・指数データの取得。

yfinance は import が重く、ネットワークも必要なので、関数内で遅延
import している。これにより indicators など他モジュールの単体テストを
yfinance 無しで実行できる。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Quote:
    """指標 1 件分の最新値とそのスナップショット。"""

    symbol: str
    name: str
    price: Optional[float]
    change_pct: Optional[float]  # 前日終値比(%)


def fetch_closes(symbol: str, lookback_days: int = 200) -> List[float]:
    """指定銘柄の終値リスト（古い→新しい順）を返す。

    取得に失敗した場合は空リストを返す。
    """
    import yfinance as yf

    # SMA 計算に十分な営業日を確保するため、余裕を持って取得する。
    period = f"{max(lookback_days, 120) + 60}d"
    try:
        hist = yf.Ticker(symbol).history(period=period, auto_adjust=False)
    except Exception as exc:  # noqa: BLE001 - ネットワーク等の失敗は握りつぶす
        print(f"[warn] {symbol} の取得に失敗: {exc}")
        return []

    if hist is None or hist.empty or "Close" not in hist:
        return []
    return [float(v) for v in hist["Close"].dropna().tolist()]


def fetch_quote(symbol: str, name: str) -> Quote:
    """市場環境指標の最新値と前日比(%)を取得する。"""
    closes = fetch_closes(symbol, lookback_days=10)
    if len(closes) >= 2:
        price = closes[-1]
        prev = closes[-2]
        change = ((price - prev) / prev * 100.0) if prev else None
        return Quote(symbol=symbol, name=name, price=price, change_pct=change)
    if len(closes) == 1:
        return Quote(symbol=symbol, name=name, price=closes[-1], change_pct=None)
    return Quote(symbol=symbol, name=name, price=None, change_pct=None)
