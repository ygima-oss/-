"""LINE 通知用のメッセージ本文を組み立てる。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from .data import Quote
from .fear_greed import FearGreed


@dataclass
class Signal:
    symbol: str
    name: str
    kind: str  # "golden" | "dead"
    price: Optional[float]
    theme: str = ""  # 例: "半導体" / "宇宙" / "量子"


def _fmt_price(v: Optional[float]) -> str:
    if v is None:
        return "—"
    if v >= 1000:
        return f"{v:,.0f}"
    return f"{v:,.2f}"


def _fmt_change(v: Optional[float]) -> str:
    if v is None:
        return ""
    sign = "+" if v >= 0 else ""
    return f"（{sign}{v:.2f}%）"


def build_message(
    signals: List[Signal],
    quotes: List[Quote],
    fear_greed: Optional[FearGreed],
    today: Optional[date] = None,
) -> str:
    today = today or date.today()
    lines: List[str] = []
    lines.append(f"📈 株式シグナル通知 {today:%Y-%m-%d}")
    lines.append("")

    golden = [s for s in signals if s.kind == "golden"]
    dead = [s for s in signals if s.kind == "dead"]

    def _line(s: Signal) -> str:
        tag = f"[{s.theme}]" if s.theme else ""
        return f"  ・{s.name}（{s.symbol}）{tag} {_fmt_price(s.price)}"

    if golden:
        lines.append("🟢 ゴールデンクロス（買いシグナル）")
        for s in golden:
            lines.append(_line(s))
        lines.append("")

    if dead:
        lines.append("🔴 デッドクロス（売りシグナル）")
        for s in dead:
            lines.append(_line(s))
        lines.append("")

    if not golden and not dead:
        lines.append("本日クロスした銘柄はありません。")
        lines.append("")

    # ---- 市場環境 ----
    lines.append("🌐 市場環境")
    for q in quotes:
        lines.append(
            f"  ・{q.name}: {_fmt_price(q.price)}{_fmt_change(q.change_pct)}"
        )
    if fear_greed is not None:
        lines.append(
            f"  ・Fear & Greed: {fear_greed.score:.0f} "
            f"（{fear_greed.rating_ja}）"
        )

    return "\n".join(lines).rstrip()
