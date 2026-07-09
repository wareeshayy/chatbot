"""Merge split page JSON parts into data/website/ijaike_knowledge.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEBSITE_DIR = ROOT / "data" / "website"
OUTPUT = WEBSITE_DIR / "ijaike_knowledge.json"


def main() -> None:
    pages: list[dict] = []
    for part_path in sorted(WEBSITE_DIR.glob("_pages_part*.json")):
        chunk = json.loads(part_path.read_text(encoding="utf-8"))
        if isinstance(chunk, list):
            pages.extend(chunk)
        else:
            raise ValueError(f"Expected list in {part_path}")

    payload = {
        "source": "IJAIKE - International Journal of Artificial Intelligence & Knowledge Engineering",
        "website": "https://ijaike.org",
        "extracted_date": "2026-07-05",
        "total_pages": len(pages),
        "pages": pages,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(pages)} pages to {OUTPUT}")


if __name__ == "__main__":
    main()
