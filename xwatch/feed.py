"""RSS / Atom フィードの取得と解析。

RSSHub / Nitter などが吐く RSS 2.0 と Atom のどちらにも対応する。
外部依存を増やさないよう、標準ライブラリの xml.etree で解析する。
無料インスタンスは既定 UA を弾くことがあるため UA を付けて取得する。
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional

import requests

_UA = "Mozilla/5.0 (compatible; x-line-notify/1.0)"
_TAG_RE = re.compile(r"<[^>]+>")
_ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass
class Post:
    id: str  # 投稿を一意に識別するキー（guid / id / link）
    text: str  # 本文（HTML を除去したプレーンテキスト）
    url: str  # 投稿への URL
    published: str  # 公開日時（フィードの文字列そのまま）


def _clean(raw: str) -> str:
    """HTML タグを除去し、実体参照をデコードして整形する。"""
    text = _TAG_RE.sub("", raw or "")
    text = html.unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _text(el: Optional[ET.Element]) -> str:
    return (el.text or "").strip() if el is not None else ""


def _parse_rss(root: ET.Element) -> List[Post]:
    posts: List[Post] = []
    for item in root.iter("item"):
        link = _text(item.find("link"))
        guid = _text(item.find("guid"))
        title = _text(item.find("title"))
        desc = _text(item.find("description"))
        pid = guid or link or title
        if not pid:
            continue
        posts.append(
            Post(
                id=pid,
                text=_clean(desc or title),
                url=link or guid,
                published=_text(item.find("pubDate")),
            )
        )
    return posts


def _atom_link(entry: ET.Element) -> str:
    # rel="alternate"（無ければ最初の）link の href を採用。
    fallback = ""
    for link in entry.findall(f"{_ATOM}link"):
        href = link.get("href", "")
        if not href:
            continue
        if link.get("rel", "alternate") == "alternate":
            return href
        fallback = fallback or href
    return fallback


def _parse_atom(root: ET.Element) -> List[Post]:
    posts: List[Post] = []
    for entry in root.iter(f"{_ATOM}entry"):
        link = _atom_link(entry)
        eid = _text(entry.find(f"{_ATOM}id"))
        title = _text(entry.find(f"{_ATOM}title"))
        content = _text(entry.find(f"{_ATOM}content")) or _text(
            entry.find(f"{_ATOM}summary")
        )
        pid = eid or link or title
        if not pid:
            continue
        published = _text(entry.find(f"{_ATOM}published")) or _text(
            entry.find(f"{_ATOM}updated")
        )
        posts.append(
            Post(
                id=pid,
                text=_clean(content or title),
                url=link or eid,
                published=published,
            )
        )
    return posts


def parse_feed(content: bytes) -> List[Post]:
    """RSS / Atom のバイト列を解析して Post のリストを返す。"""
    root = ET.fromstring(content)
    tag = root.tag.lower()
    if tag.endswith("feed"):  # Atom
        return _parse_atom(root)
    # RSS 2.0（<rss><channel><item>…）や RDF を含め item を走査。
    return _parse_rss(root)


def fetch_posts(url: str, timeout: int = 20) -> List[Post]:
    """RSS フィードを取得し、Post のリスト（フィード掲載順）を返す。

    多くのインスタンスは新しい投稿が先頭に来る。
    """
    resp = requests.get(url, headers={"User-Agent": _UA}, timeout=timeout)
    resp.raise_for_status()
    return parse_feed(resp.content)
