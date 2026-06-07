"""エントリポイント。

監視銘柄を走査してクロスを検知し、市場環境とあわせて LINE に通知する。

使い方:
    python -m goldencross.main                 # 実際に LINE 送信
    python -m goldencross.main --dry-run       # 送信せず本文を標準出力
    python -m goldencross.main --always        # クロス無しでも通知する
    python -m goldencross.main -c path.yaml    # 設定ファイルを指定
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from . import data, fear_greed as fg_mod, message, notify
from .config import load_config
from .indicators import detect_cross


def run(config_path: str | None, dry_run: bool, always: bool) -> int:
    cfg = load_config(config_path) if config_path else load_config()

    # ---- 銘柄ごとにクロス判定 ----
    signals: List[message.Signal] = []
    for stock in cfg.all_stocks:
        symbol = stock["symbol"]
        name = stock.get("name", symbol)
        closes = data.fetch_closes(symbol, lookback_days=cfg.long_period + 30)
        if not closes:
            continue
        kind = detect_cross(closes, cfg.short_period, cfg.long_period)
        if kind:
            signals.append(
                message.Signal(
                    symbol=symbol, name=name, kind=kind, price=closes[-1]
                )
            )
            print(f"[signal] {name}({symbol}): {kind}")

    # ---- 市場環境 ----
    quotes = [
        data.fetch_quote(ind["symbol"], ind.get("name", ind["symbol"]))
        for ind in cfg.market_indicators
    ]
    fear_greed = fg_mod.fetch_fear_greed()

    # ---- 通知本文 ----
    body = message.build_message(signals, quotes, fear_greed)

    if not signals and not always:
        # クロスが無い日は市場環境だけ通知すると煩いので既定では送らない。
        print("クロス無し。通知をスキップします（--always で常時通知）。")
        print("----- プレビュー -----")
        print(body)
        return 0

    if dry_run:
        print("----- DRY RUN (LINE 未送信) -----")
        print(body)
        return 0

    notify.send_line(body)
    print("LINE に送信しました。")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ゴールデンクロス通知")
    parser.add_argument("-c", "--config", default=None, help="設定ファイルのパス")
    parser.add_argument(
        "--dry-run", action="store_true", help="LINE 送信せず本文を表示"
    )
    parser.add_argument(
        "--always",
        action="store_true",
        help="クロスが無くても市場環境を通知する",
    )
    args = parser.parse_args(argv)
    return run(args.config, args.dry_run, args.always)


if __name__ == "__main__":
    sys.exit(main())
