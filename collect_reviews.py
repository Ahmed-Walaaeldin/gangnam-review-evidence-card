"""Collect the public English review summaries shown on Gangnam Beauty Guide.

One request, one listing page. No login, pagination, or underlying Korean-source access.
Run: python collect_reviews.py
Offline parser check: python collect_reviews.py --html sample_page.html
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


SOURCE_URL = "https://gangnambeautyguide.com/en/reviews/"
USER_AGENT = "GangnamReviewEvidencePrototype/1.0 (single public listing snapshot)"
META_RE = re.compile(r"★\s*(\d+(?:\.\d+)?)\s+(.+?)\s*·\s*(\d{4}-\d{2}-\d{2})")


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)

    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def text(self) -> str:
        def flatten(item: Node | str) -> str:
            if isinstance(item, str):
                return item
            if item.tag in {"script", "style"}:
                return ""
            return " ".join(flatten(child) for child in item.children)

        return re.sub(r"\s+", " ", flatten(self)).strip()

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()


class TreeParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, dict(attrs)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse_reviews(html: str) -> list[dict]:
    parser = TreeParser()
    parser.feed(html)
    grids = [node for node in parser.root.walk() if "gbg-card-grid" in node.classes()]
    if len(grids) != 1:
        raise ValueError(f"Expected one review grid; found {len(grids)}. The site layout may have changed.")

    records = []
    for position, card in enumerate((child for child in grids[0].children if isinstance(child, Node)), start=1):
        links = [node for node in card.walk() if node.tag == "a" and "/clinics/" in node.attrs.get("href", "")]
        if len(links) != 1:
            raise ValueError(f"Card {position}: expected one clinic link; found {len(links)}")
        clinic = links[0].text()
        clinic_url = urljoin(SOURCE_URL, links[0].attrs["href"])
        meta = META_RE.search(card.text())
        if not meta:
            raise ValueError(f"Card {position}: rating/source/date not found")
        visible_children = [child for child in card.children if isinstance(child, Node)]
        if len(visible_children) < 2:
            raise ValueError(f"Card {position}: summary block not found")
        summary = visible_children[1].text()
        if len(summary) < 30:
            raise ValueError(f"Card {position}: summary unexpectedly short")
        rating, source_platform, date = meta.groups()
        fingerprint = "\x1f".join([clinic_url, date, summary]).encode("utf-8")
        records.append({
            "id": hashlib.sha256(fingerprint).hexdigest()[:16],
            "listing_position": position,
            "clinic": clinic,
            "clinic_url": clinic_url,
            "rating": float(rating),
            "source_platform": source_platform.strip(),
            "review_date": date,
            "summary_en": summary,
            "listing_url": SOURCE_URL,
            "verification": "public English summary only; original post and patient not verified",
        })
    if not records:
        raise ValueError("No review cards found; output was not written")
    return records


def fetch_page() -> str:
    request = Request(SOURCE_URL, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read(5_000_000).decode(charset, errors="replace")


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--html", type=Path, help="Parse a saved HTML file instead of fetching the live page")
    cli.add_argument("--out", type=Path, default=Path(__file__).parent / "data" / "reviews.json")
    args = cli.parse_args()
    try:
        html = args.html.read_text(encoding="utf-8") if args.html else fetch_page()
        records = parse_reviews(html)
        payload = {
            "source_url": SOURCE_URL,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "count": len(records),
            "records": records,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.out.with_suffix(args.out.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(args.out)
        print(f"Collected {len(records)} public review summaries to {args.out}")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Collection failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
