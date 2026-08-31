#!/usr/bin/env python3
"""Build a small, deduplicated catalog of Huberman Lab episode/video URLs.

This records metadata and links only. It does not download copyrighted transcripts.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

OFFICIAL = "https://www.hubermanlab.com/all-episodes"
URL_RE = re.compile(r'href=["\'](https://www\.hubermanlab\.com/episode/[^"\']+|/episode/[^"\']+)["\']', re.I)
PAGE_RE = re.compile(r'href=["\']([^"\']*_page=\d+[^"\']*)["\']', re.I)
YOUTUBE_RE = re.compile(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+|www\.youtube\.com/@[\w-]+)', re.I)
BILIBILI_RE = re.compile(r'https?://(?:www\.)?bilibili\.com/video/(BV[\w]+)', re.I)


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "huberman-perspective-catalog/1.0"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def official_rows() -> list[dict[str, str]]:
    pages = [OFFICIAL]
    seen_pages = set(pages)
    rows: dict[str, dict[str, str]] = {}
    while pages:
        page_url = pages.pop(0)
        html = fetch(page_url)
        for page_href in PAGE_RE.findall(html):
            next_page = urljoin(page_url, page_href)
            if next_page not in seen_pages:
                seen_pages.add(next_page)
                pages.append(next_page)
        for match in URL_RE.finditer(html):
            href = match.group(1)
            if href.startswith("/"):
                href = "https://www.hubermanlab.com" + href
            slug = href.rsplit("/", 1)[-1]
            context = clean(html[max(0, match.start() - 500): min(len(html), match.end() + 800)])
            rows[href] = {
                "platform": "official",
                "id": slug,
                "title_or_context": context[:240],
                "url": href,
                "source_url": page_url,
            }
    print(f"scanned {len(seen_pages)} official catalog pages", file=sys.stderr)
    return list(rows.values())


def url_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    found = set(YOUTUBE_RE.findall(text)) | {match.group(0) for match in BILIBILI_RE.finditer(text)}
    rows = []
    for url in sorted(found):
        if "bilibili.com" in url:
            platform = "bilibili"
            ident = BILIBILI_RE.search(url).group(1)
        else:
            platform = "youtube"
            ident = url.split("v=")[-1] if "v=" in url else url.rsplit("/", 1)[-1]
        rows.append({"platform": platform, "id": ident, "title_or_context": "", "url": url, "source_url": str(path)})
    return rows


def write_rows(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["platform", "id", "title_or_context", "url", "source_url"]
    existing: dict[tuple[str, str], dict[str, str]] = {}
    if output.exists():
        with output.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                existing[(row.get("platform", ""), row.get("id", ""))] = row
    for row in rows:
        existing[(row["platform"], row["id"])] = row
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(existing.values(), key=lambda r: (r["platform"], r["id"])))
    print(f"wrote {len(existing)} rows to {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--urls", type=Path, help="Text/Markdown file containing YouTube or Bilibili URLs")
    parser.add_argument("--no-fetch", action="store_true", help="Only process --urls")
    args = parser.parse_args()
    rows: list[dict[str, str]] = []
    if not args.no_fetch:
        try:
            rows.extend(official_rows())
        except Exception as exc:  # cataloging should degrade gracefully
            print(f"warning: official catalog unavailable: {exc}", file=sys.stderr)
    if args.urls:
        rows.extend(url_rows(args.urls))
    if not rows:
        print("no URLs found", file=sys.stderr)
        return 2
    write_rows(rows, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
