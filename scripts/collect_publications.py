#!/usr/bin/env python3
"""Collect the public publication list from the Stanford Huberman Lab site."""
from __future__ import annotations

import argparse
import csv
import html as html_lib
import re
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from lxml import html


BASE = "https://hubermanlab.stanford.edu/publications"
DOI_RE = re.compile(r"https?://doi\.org/[^\s<]+", re.I)


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "huberman-perspective-publications/1.0"})
    with urlopen(req, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(value)).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows: list[dict[str, str]] = []
    page = 0
    while True:
        url = BASE if page == 0 else f"{BASE}?page={page}"
        tree = html.fromstring(fetch(url))
        entries = tree.xpath("//*[contains(concat(' ', normalize-space(@class), ' '), ' csl-entry ')]")
        for entry in entries:
            links = entry.xpath(".//a")
            internal = ""
            title = ""
            if links:
                internal = urljoin(url, links[0].get("href", ""))
                title = clean(" ".join(links[0].itertext()))
            citation = clean(entry.text_content())
            dois = sorted(set(DOI_RE.findall(citation)))
            rows.append({
                "index": str(len(rows) + 1),
                "title": title,
                "citation": citation,
                "internal_url": internal,
                "doi_urls": ";".join(dois),
                "source_url": url,
            })
        next_link = tree.xpath("//a[contains(@title, 'Load more')]/@href")
        if not next_link:
            break
        page += 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        fields = ["index", "title", "citation", "internal_url", "doi_urls", "source_url"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} publications to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
