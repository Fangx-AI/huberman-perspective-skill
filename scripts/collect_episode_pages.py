#!/usr/bin/env python3
"""Fetch public Huberman Lab Episode metadata, show notes, and timestamps.

The collector deliberately excludes the Transcript tab. It stores metadata and
public notes only, so it can be rerun safely without copying full copyrighted
transcripts into the Skill.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import Request, urlopen

try:
    from lxml import html as lxml_html
except ImportError:  # pragma: no cover - the bundled runtime normally provides lxml
    lxml_html = None

CANONICAL_YOUTUBE_RE = re.compile(r"youtubeID\s*=\s*['\"]([\w-]+)['\"]")
YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def canonical_youtube_url(href: str) -> str | None:
    """Return a canonical YouTube URL, including the Huberman-site edge case.

    Some current Episode pages emit ``https://<11-char-video-id>`` for the
    YouTube platform link. Treat that exact shape as a malformed-but-recoverable
    YouTube URL, while requiring the surrounding platform marker in the parser.
    """
    raw = html.unescape(href or "").strip()
    if not raw:
        return None
    parsed = urlsplit(raw)
    original_host = parsed.netloc.rstrip(".")
    host = original_host.lower()
    candidate = ""
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/embed/"):
            candidate = parsed.path.split("/", 2)[2]
    elif YOUTUBE_ID_RE.fullmatch(original_host) and parsed.path in {"", "/"}:
        # Current Huberman Lab HTML occasionally emits https://<video-id>.
        candidate = original_host
    if YOUTUBE_ID_RE.fullmatch(candidate):
        return f"https://www.youtube.com/watch?v={candidate}"
    return None


class EpisodeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capture: str | None = None
        self.capture_depth = 0
        self.buffers = {"notes": [], "timestamps": []}
        self.h1 = []
        self.topics: list[str] = []
        self.youtube: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        classes = attrs_d.get("class", "") or ""
        if tag == "div" and self.capture is None:
            if "rich-text-episode-notes" in classes:
                self.capture, self.capture_depth = "notes", 1
            elif "rich-text-episode-timestamps" in classes:
                self.capture, self.capture_depth = "timestamps", 1
        elif tag == "div" and self.capture is not None:
            self.capture_depth += 1
        if tag == "h1":
            self.h1.append("")
        href = attrs_d.get("href") or ""
        if href.startswith("/topics/"):
            self.topics.append(href)
        youtube_url = canonical_youtube_url(href)
        if youtube_url:
            self.youtube.append(youtube_url)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.capture is not None:
            self.capture_depth -= 1
            if self.capture_depth == 0:
                self.capture = None
        if tag == "h1" and self.h1 and self.h1[-1] == "":
            pass

    def handle_data(self, data: str) -> None:
        value = re.sub(r"\s+", " ", data).strip()
        if not value:
            return
        if self.capture:
            self.buffers[self.capture].append(value)
        if self.h1:
            self.h1[-1] += (" " if self.h1[-1] else "") + value


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "huberman-perspective-notes/1.0"})
    with urlopen(req, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")


def jsonld(html_text: str) -> dict:
    scripts = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html_text, re.I | re.S)
    for script in scripts:
        try:
            obj = json.loads(html.unescape(script))
        except (ValueError, TypeError):
            continue
        if isinstance(obj, list):
            candidates = obj
        elif isinstance(obj, dict) and isinstance(obj.get("@graph"), list):
            candidates = obj["@graph"]
        else:
            candidates = [obj]
        for item in candidates:
            if isinstance(item, dict) and ("PodcastEpisode" in str(item.get("@type")) or "episodeNumber" in item):
                return item
    return {}


def clean_join(values: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(values)).strip()


def dom_text(tree, xpath: str) -> str:
    nodes = tree.xpath(xpath) if tree is not None else []
    return clean_join([node.text_content() for node in nodes])


def collect(row: dict[str, str]) -> dict:
    url = row["url"]
    now = datetime.now(timezone.utc).isoformat()
    try:
        raw = fetch(url)
        tree = lxml_html.fromstring(raw) if lxml_html is not None else None
        parser = EpisodeParser()
        parser.feed(raw)
        data = jsonld(raw)
        topics = sorted({urljoin(url, topic) for topic in (tree.xpath("//div[contains(@class,'share-topics-row')]//a[starts-with(@href,'/topics/')]/@href") if tree is not None else parser.topics)})
        canonical_ids = [ident for ident in CANONICAL_YOUTUBE_RE.findall(raw) if YOUTUBE_ID_RE.fullmatch(ident)]
        if canonical_ids:
            youtube = [f"https://www.youtube.com/watch?v={canonical_ids[-1]}"]
        else:
            youtube = sorted(set(parser.youtube))
        title = data.get("name") or dom_text(tree, "//h1[1]") or clean_join(parser.h1)
        note_nodes = tree.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' rich-text-episode-notes ')]") if tree is not None else []
        notes = dom_text(tree, "//*[contains(concat(' ', normalize-space(@class), ' '), ' rich-text-episode-notes ')]") or clean_join(parser.buffers["notes"])
        resource_urls = sorted({urljoin(url, href) for node in note_nodes for href in node.xpath(".//a/@href")})
        timestamps = dom_text(tree, "//*[contains(concat(' ', normalize-space(@class), ' '), ' rich-text-timestamps ')]") or clean_join(parser.buffers["timestamps"])
        return {
            "episode_id": row.get("id", ""),
            "url": url,
            "title": title,
            "date_published": data.get("datePublished", ""),
            "episode_number": data.get("episodeNumber", ""),
            "duration": data.get("duration", ""),
            "description": data.get("description", ""),
            "image": data.get("image", ""),
            "topics": topics,
            "youtube_urls": youtube,
            "resource_urls": resource_urls,
            "show_notes": notes,
            "timestamps": timestamps,
            "fetched_at": now,
            "fetch_ok": True,
            "error": "",
        }
    except Exception as exc:
        return {"episode_id": row.get("id", ""), "url": url, "fetched_at": now, "fetch_ok": False, "error": str(exc)}


def load_rows(catalog: Path) -> list[dict[str, str]]:
    with catalog.open("r", encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row.get("platform") == "official"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    rows = load_rows(args.catalog)
    existing: dict[str, dict] = {}
    if args.output.exists() and not args.refresh:
        with args.output.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    item = json.loads(line)
                    existing[item["url"]] = item
    pending = [row for row in rows if row["url"] not in existing]
    print(f"catalog={len(rows)} cached={len(existing)} pending={len(pending)}", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(collect, row) for row in pending]
        for future in as_completed(futures):
            item = future.result()
            existing[item["url"]] = item
            print(f"{'OK' if item.get('fetch_ok') else 'FAIL'} {item['url']}", file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for url in sorted(existing):
            handle.write(json.dumps(existing[url], ensure_ascii=False) + "\n")
    ok = sum(1 for item in existing.values() if item.get("fetch_ok"))
    print(f"wrote {len(existing)} records; ok={ok}; failed={len(existing)-ok} to {args.output}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
