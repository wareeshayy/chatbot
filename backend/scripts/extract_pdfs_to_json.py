"""Download IJAIKE PDFs (local + CFP links) and export extracted text to JSON."""

from __future__ import annotations

import asyncio
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

import fitz
import httpx

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = _PROJECT_ROOT / "data" / "pdfs"
WEBSITE_JSON = _PROJECT_ROOT / "data" / "website" / "ijaike_knowledge.json"
OUTPUT_JSON = PDF_DIR / "ijaike_pdfs_knowledge.json"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip())
    return slug.strip("-").lower() or "document"


def _filename_from_url(url: str) -> str:
    path = urlparse(url).path
    name = unquote(Path(path).name)
    if not name.lower().endswith(".pdf"):
        name = f"{_slugify(name)}.pdf"
    return name


def extract_pdf_text(pdf_path: Path) -> list[dict]:
    pages: list[dict] = []
    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page_number": page_num, "text": text})
    return pages


def collect_pdf_urls(knowledge: dict) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()

    for page in knowledge.get("pages", []):
        for issue in page.get("special_issues") or []:
            url = issue.get("download")
            if url and url not in seen:
                seen.add(url)
                found.append({
                    "title": issue.get("title", "IJAIKE PDF"),
                    "url": url,
                    "source_page": page.get("page_title"),
                })

    return found


async def download_pdf(client: httpx.AsyncClient, url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        response = await client.get(url, follow_redirects=True, timeout=60.0)
        response.raise_for_status()
        dest.write_bytes(response.content)
        return True
    except Exception as exc:
        print(f"  FAIL Download failed: {url} ({exc})")
        return False


async def ensure_remote_pdfs(knowledge: dict) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    remote = collect_pdf_urls(knowledge)
    if not remote:
        print("No remote PDF URLs found in website knowledge JSON.")
        return

    print(f"Found {len(remote)} PDF URL(s) in website JSON.\n")
    async with httpx.AsyncClient(headers={"User-Agent": "IJAIKE-Knowledge-Ingest/1.0"}) as client:
        for item in remote:
            filename = _filename_from_url(item["url"])
            dest = PDF_DIR / filename
            print(f"Downloading: {item['title']}")
            ok = await download_pdf(client, item["url"], dest)
            if ok:
                print(f"  OK Saved: {dest.name}")


def build_pdf_knowledge() -> dict:
    documents: list[dict] = []
    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        print(f"Extracting: {pdf_path.name}")
        try:
            pages = extract_pdf_text(pdf_path)
            full_text = "\n\n".join(
                f"[Page {p['page_number']}]\n{p['text']}" for p in pages
            )
            documents.append({
                "filename": pdf_path.name,
                "title": pdf_path.stem.replace("-", " ").replace("_", " "),
                "source_path": str(pdf_path.relative_to(_PROJECT_ROOT)).replace("\\", "/"),
                "page_count": len(pages),
                "pages": pages,
                "full_text": full_text,
            })
            print(f"  OK {len(pages)} page(s)")
        except Exception as exc:
            print(f"  FAIL Failed: {exc}")
            documents.append({
                "filename": pdf_path.name,
                "title": pdf_path.stem,
                "error": str(exc),
                "pages": [],
                "full_text": "",
            })

    return {
        "source": "IJAIKE PDF Knowledge Base",
        "extracted_date": date.today().isoformat(),
        "total_documents": len(documents),
        "documents": documents,
    }


async def main() -> None:
    knowledge: dict = {}
    if WEBSITE_JSON.exists():
        knowledge = json.loads(WEBSITE_JSON.read_text(encoding="utf-8"))
        await ensure_remote_pdfs(knowledge)
    else:
        print(f"Warning: {WEBSITE_JSON} not found — only local PDFs will be extracted.")

    payload = build_pdf_knowledge()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n=== Exported {payload['total_documents']} PDF(s) to {OUTPUT_JSON} ===")


if __name__ == "__main__":
    asyncio.run(main())
