#!/usr/bin/env python3
"""kabutan(株探)からゴールデンクロス系シグナル銘柄をテーマ別に抽出し、
GitHub Issue 本文用の Markdown (issue_body.md) とタイトルを生成する。

各テーマは独立して取得し、失敗してもそのテーマだけエラー表示にして
全体は止めない(=Issueは必ず作られる)方針。
"""
import io
import os
import sys
import datetime

import requests
import pandas as pd

JST = datetime.timezone(datetime.timedelta(hours=9))
NOW = datetime.datetime.now(JST)
TODAY = NOW.strftime("%Y-%m-%d (%a)")
HHMM = NOW.strftime("%H:%M")

# (テーマ名, ベースURL, ページ番号のクエリキー)
THEMES = [
    ("5日×25日 ゴールデンクロス", "https://kabutan.jp/warning/?mode=6_1"),
    ("株価が25日移動平均線を上抜き", "https://kabutan.jp/warning/?mode=6_3"),
    ("MACD 買いシグナル", "https://kabutan.jp/tansaku/?mode=2_0440"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.8",
}

MAX_PAGES = 5      # 念のための上限
MAX_ROWS = 100     # Issueが巨大化しないよう1テーマあたりの表示上限


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        " ".join(str(x) for x in c) if isinstance(c, tuple) else str(c)
        for c in df.columns
    ]
    return df


def _pick_stock_table(html: str):
    """ページ内テーブルから「コード」と「銘柄」を含むものを選ぶ。"""
    tables = pd.read_html(io.StringIO(html))
    best = None
    for t in tables:
        t = _flatten_columns(t)
        joined = " ".join(t.columns)
        if "コード" in joined and "銘柄" in joined:
            if best is None or len(t) > len(best):
                best = t
    return best


def _col_like(df: pd.DataFrame, *keys):
    for c in df.columns:
        if all(k in c for k in keys):
            return c
    return None


def fetch_theme(url: str) -> pd.DataFrame:
    """ページネーションをたどって銘柄テーブルを集約。コードで重複排除。"""
    sep = "&" if "?" in url else "?"
    frames = []
    seen_codes = set()
    for page in range(1, MAX_PAGES + 1):
        page_url = url if page == 1 else f"{url}{sep}page={page}"
        r = requests.get(page_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        if not r.encoding or r.encoding.lower() == "iso-8859-1":
            r.encoding = r.apparent_encoding
        table = _pick_stock_table(r.text)
        if table is None or len(table) == 0:
            break
        code_c = _col_like(table, "コード")
        if code_c is None:
            break
        codes = set(str(v) for v in table[code_c].tolist())
        new_codes = codes - seen_codes
        if not new_codes:
            break  # 同じページが返ってきた=最終ページ
        seen_codes |= codes
        frames.append(table)
    if not frames:
        raise ValueError("銘柄テーブルが見つかりませんでした")
    df = pd.concat(frames, ignore_index=True)
    code_c = _col_like(df, "コード")
    df = df.drop_duplicates(subset=[code_c]).reset_index(drop=True)
    return df


def render_theme(label: str, df: pd.DataFrame) -> str:
    code_c = _col_like(df, "コード")
    name_c = _col_like(df, "銘柄")
    price_c = _col_like(df, "株価") or _col_like(df, "現在", "値") or _col_like(df, "終値")
    total = len(df)
    lines = [f"## 📊 {label}（{total} 銘柄）", ""]
    lines.append("| コード | 銘柄名 | 株価 |")
    lines.append("|---|---|---|")
    shown = df.head(MAX_ROWS)
    for _, row in shown.iterrows():
        code = str(row[code_c]) if code_c else ""
        name = str(row[name_c]) if name_c else ""
        price = str(row[price_c]) if price_c else ""
        lines.append(f"| {code} | {name} | {price} |")
    if total > MAX_ROWS:
        lines.append("")
        lines.append(f"_（上位 {MAX_ROWS} 件のみ表示。全 {total} 件）_")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    sections = []
    counts = []
    for label, url in THEMES:
        try:
            df = fetch_theme(url)
            sections.append(render_theme(label, df))
            counts.append(f"{label}: {len(df)}件")
        except Exception as e:  # テーマ単位で握りつぶす
            sections.append(f"## 📊 {label}\n\n⚠️ 取得失敗: `{e}`\n")
            counts.append(f"{label}: 取得失敗")

    title = f"📈 ゴールデンクロス銘柄まとめ {TODAY} {HHMM} JST"
    header = [
        f"# 📈 ゴールデンクロス銘柄まとめ",
        "",
        f"- 取得日時: **{TODAY} {HHMM} JST**",
        f"- データ元: [株探 (kabutan)](https://kabutan.jp/)",
        f"- サマリー: " + " / ".join(counts),
        "",
        "> ⚠️ 本情報はテクニカルシグナルの機械的な抽出であり、特定銘柄の売買を推奨するものではありません。",
        "",
        "---",
        "",
    ]
    body = "\n".join(header) + "\n".join(sections)

    with open("issue_body.md", "w", encoding="utf-8") as f:
        f.write(body)

    # ワークフローへタイトルを渡す
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"title={title}\n")

    print(title)
    print("\n".join(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
