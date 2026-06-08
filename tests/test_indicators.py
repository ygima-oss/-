"""indicators / message のオフライン単体テスト。

外部ネットワーク・yfinance 無しで実行できる。
    python -m pytest tests/        （pytest があれば）
    python tests/test_indicators.py（無くてもそのまま実行可）
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from goldencross.indicators import detect_cross, sma  # noqa: E402
from goldencross.message import Signal, build_message  # noqa: E402


def test_sma_basic():
    values = [1, 2, 3, 4, 5]
    result = sma(values, 3)
    assert result[:2] == [None, None]
    assert result[2] == 2.0  # (1+2+3)/3
    assert result[3] == 3.0  # (2+3+4)/3
    assert result[4] == 4.0  # (3+4+5)/3


def test_golden_cross():
    # short=2, long=3 で末日にクロスするよう手計算した系列。
    #   SMA2[-2]=10, SMA3[-2]=10        → 前日は短期 == 長期
    #   SMA2[-1]=11, SMA3[-1]=10.667    → 当日は短期 > 長期（ゴールデン）
    closes = [10, 10, 10, 10, 12]
    assert detect_cross(closes, 2, 3) == "golden"


def test_dead_cross():
    #   SMA2[-2]=10, SMA3[-2]=10        → 前日は短期 == 長期
    #   SMA2[-1]=9,  SMA3[-1]=9.333     → 当日は短期 < 長期（デッド）
    closes = [10, 10, 10, 10, 8]
    assert detect_cross(closes, 2, 3) == "dead"


def test_cross_only_at_last_two_days():
    # クロスが直近 2 日より前に起きた場合は検知しない（重複通知防止）。
    closes = [10, 10, 10, 10, 12, 14, 16]  # クロスは index 4 で発生済み
    assert detect_cross(closes, 2, 3) is None


def test_no_cross_flat():
    closes = [100] * 120
    assert detect_cross(closes, 5, 25) is None


def test_insufficient_data():
    closes = [100, 101, 102]
    assert detect_cross(closes, 5, 25) is None


def test_build_message_with_signals():
    signals = [Signal("7203.T", "トヨタ自動車", "golden", 2800.0)]
    text = build_message(signals, [], None)
    assert "ゴールデンクロス" in text
    assert "トヨタ自動車" in text


def test_build_message_no_signals():
    text = build_message([], [], None)
    assert "クロスした銘柄はありません" in text


def _run_all():
    passed = 0
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS {name}")
                passed += 1
            except AssertionError as exc:
                print(f"  FAIL {name}: {exc}")
                failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
