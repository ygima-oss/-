"""エントリポイント。

RSS フィードを取得して新着投稿を検知し、LINE に通知する。

使い方:
    python -m xwatch.main                 # 実際に LINE 送信
    python -m xwatch.main --dry-run       # 送信せず本文を標準出力
    python -m xwatch.main --notify-first  # 初回実行でも新着を通知する

初回実行（既読 ID が空）のときは、既存の投稿を大量に通知してしまうのを
避けるため、既定では通知せず「基準」として現在のフィードを記録するだけに
する（--notify-first で無効化）。
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from . import feed, message, notify, state
from .config import load_config


def run(dry_run: bool, notify_first: bool) -> int:
    cfg = load_config()

    posts = feed.fetch_posts(cfg.rss_url)
    if not posts:
        print("フィードから投稿を取得できませんでした（0 件）。")
        return 0

    seen = state.load_seen(cfg.state_path)
    seen_set = set(seen)
    first_run = len(seen) == 0

    # フィード掲載順（新しい順が一般的）から未読を抽出。
    new_posts = [p for p in posts if p.id not in seen_set]

    # 現在のフィード ID + 既存の既読 を新しい順で結合し重複除去。
    updated_seen = list(dict.fromkeys([p.id for p in posts] + seen))

    if first_run and not notify_first:
        state.save_seen(cfg.state_path, updated_seen)
        print(
            f"初回実行のため基準を記録しました（{len(posts)} 件）。"
            "次回以降の新着から通知します。"
        )
        return 0

    if not new_posts:
        # 既読を最新に更新して静かに終了。
        state.save_seen(cfg.state_path, updated_seen)
        print("新着はありません。")
        return 0

    # 古い順に送る。ただし連投を防ぐため最新 max_notify 件に制限。
    to_send = list(reversed(new_posts))[-cfg.max_notify :]
    skipped = len(new_posts) - len(to_send)

    print(f"新着 {len(new_posts)} 件を検知（送信 {len(to_send)} 件）。")
    for post in to_send:
        body = message.build_message(post, cfg.account)
        if dry_run:
            print("----- DRY RUN (LINE 未送信) -----")
            print(body)
            print()
        else:
            notify.send_line(body)
            print(f"[sent] {post.url or post.id}")

    if skipped > 0:
        print(f"（上限超過のため {skipped} 件は送信を省略しました）")

    # 送信の成否にかかわらず、検知した新着はすべて既読に記録する
    # （dry-run 時は記録しない）。
    if not dry_run:
        state.save_seen(cfg.state_path, updated_seen)

    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="X 投稿の LINE 通知")
    parser.add_argument(
        "--dry-run", action="store_true", help="LINE 送信せず本文を表示"
    )
    parser.add_argument(
        "--notify-first",
        action="store_true",
        help="初回実行でも新着を通知する（既定は基準記録のみ）",
    )
    args = parser.parse_args(argv)
    return run(args.dry_run, args.notify_first)


if __name__ == "__main__":
    sys.exit(main())
