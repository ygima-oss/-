"""移動平均とクロス判定。

外部ライブラリに依存しない純 Python 実装にしているため、
ネットワークや pandas/yfinance が無い環境でも単体テストできる。
"""

from __future__ import annotations

from typing import List, Optional, Sequence


def sma(values: Sequence[float], period: int) -> List[Optional[float]]:
    """単純移動平均(SMA)の系列を返す。

    period 本に満たない先頭部分は ``None`` で埋める。返り値は
    入力 ``values`` と同じ長さになる。
    """
    if period <= 0:
        raise ValueError("period は 1 以上である必要があります")

    out: List[Optional[float]] = [None] * len(values)
    running = 0.0
    for i, v in enumerate(values):
        running += v
        if i >= period:
            running -= values[i - period]
        if i >= period - 1:
            out[i] = running / period
    return out


def detect_cross(
    closes: Sequence[float], short_period: int, long_period: int
) -> Optional[str]:
    """直近 2 営業日でのクロスを判定する。

    返り値:
        "golden" … 短期線が長期線を下から上に抜けた（ゴールデンクロス）
        "dead"   … 短期線が長期線を上から下に抜けた（デッドクロス）
        None     … クロスなし、またはデータ不足
    """
    if short_period >= long_period:
        raise ValueError("short_period は long_period より小さい必要があります")

    # 直近 2 日分の SMA を比較できるだけのデータが必要。
    if len(closes) < long_period + 1:
        return None

    short = sma(closes, short_period)
    long = sma(closes, long_period)

    s_prev, s_now = short[-2], short[-1]
    l_prev, l_now = long[-2], long[-1]
    if None in (s_prev, s_now, l_prev, l_now):
        return None

    # 前日は短期 <= 長期、当日は短期 > 長期 → ゴールデンクロス
    if s_prev <= l_prev and s_now > l_now:
        return "golden"
    # 前日は短期 >= 長期、当日は短期 < 長期 → デッドクロス
    if s_prev >= l_prev and s_now < l_now:
        return "dead"
    return None
