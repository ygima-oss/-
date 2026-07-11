"""既読投稿 ID の永続化。

GitHub Actions はステートレスなので、見た投稿の ID をリポジトリ内の
JSON に保存し、ワークフロー側でコミットして次回に引き継ぐ。
出会い頭の重複通知や順序ゆらぎに備えて、直近の ID を複数保持する。
"""

from __future__ import annotations

import json
import os
from typing import List

_MAX_KEEP = 200


def load_seen(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    seen = data.get("seen", []) if isinstance(data, dict) else []
    return [str(x) for x in seen]


def save_seen(path: str, ids: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    trimmed = ids[:_MAX_KEEP]
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"seen": trimmed}, f, ensure_ascii=False, indent=2)
        f.write("\n")
