"""Embed the collected review snapshot into the standalone static prototype.

Run after collect_reviews.py. Three source IDs have manually reviewed annotations;
all other source records remain visible as unreviewed English summaries.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent
DATA = ROOT / "data" / "reviews.json"
PAGE = ROOT / "index.html"
SOURCE_IDS = (
    "1ef27ec0af2620ef",  # AB PS: third rhinoplasty, cautious recommendation
    "f19d4051b235d7e0",  # View PS: eyelid surgery, cost/recovery absent
    "f453abf9b7827891",  # Hit PS: forehead lift, incision concern
    "0b8f796416279128",  # AB PS: similar third-rhinoplasty summary
    "9eda34702c2e0145",  # Hit PS: similar forehead-lift summary
)
START = "<!-- SOURCE_RECORDS_START -->"
END = "<!-- SOURCE_RECORDS_END -->"
DEDUPE_START = "<!-- DEDUPE_START -->"
DEDUPE_END = "<!-- DEDUPE_END -->"


def main() -> None:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    by_id = {record["id"]: record for record in snapshot["records"]}
    missing = [record_id for record_id in SOURCE_IDS if record_id not in by_id]
    if missing:
        raise ValueError(f"Reviewed source records missing from snapshot: {', '.join(missing)}")
    for record in snapshot["records"]:
        if not record["summary_en"] or not record["clinic"] or not record["review_date"]:
            raise ValueError(f"Incomplete source record: {record['id']}")
    source_data = json.dumps(snapshot["records"], ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    replacement = f'{START}\n  <script id="source-records" type="application/json">{source_data}</script>\n  {END}'
    page = PAGE.read_text(encoding="utf-8")
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError("Source-data markers missing or duplicated in index.html")
    before, rest = page.split(START, 1)
    _, after = rest.split(END, 1)
    updated = before + replacement + after
    if updated.count(DEDUPE_START) != 1 or updated.count(DEDUPE_END) != 1:
        raise ValueError("Dedupe-script markers missing or duplicated in index.html")
    dedupe_source = (ROOT / "dedupe.js").read_text(encoding="utf-8")
    if "</script" in dedupe_source.lower():
        raise ValueError("Dedupe source contains a script-closing tag")
    dedupe_block = f"{DEDUPE_START}\n  <script>\n{dedupe_source}\n  </script>\n  {DEDUPE_END}"
    before, rest = updated.split(DEDUPE_START, 1)
    _, after = rest.split(DEDUPE_END, 1)
    updated = before + dedupe_block + after
    PAGE.write_text(updated, encoding="utf-8")
    print(f"Embedded {len(snapshot['records'])} collected source records in {PAGE.name}")


if __name__ == "__main__":
    main()
