"""Ingest IJAIKE website JSON content into MongoDB + ChromaDB."""

import asyncio
import json
from pathlib import Path
from uuid import uuid4

import aiofiles

from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.models.document import Document
from app.models.enums import DocumentCategory, DocumentStatus
from app.models.user import User
from app.services.ingest_service import IngestService
from app.utils.website_content import page_to_text

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_JSON = _PROJECT_ROOT / "data" / "website" / "ijaike_knowledge.json"
UPLOAD_ROOT = Path("./uploads")

PAGE_CATEGORIES: dict[str, DocumentCategory] = {
    "Home": DocumentCategory.OTHER,
    "About JAIKE": DocumentCategory.OTHER,
    "Journal Focus": DocumentCategory.OTHER,
    "Journal Scope": DocumentCategory.OTHER,
    "What is Knowledge Engineering (KE)": DocumentCategory.OTHER,
    "Journal Readership": DocumentCategory.OTHER,
    "Subscription Information": DocumentCategory.OTHER,
    "About the Editor-in-Chief": DocumentCategory.EDITORIAL_POLICIES,
    "About the Associate Editor": DocumentCategory.EDITORIAL_POLICIES,
    "Editorial Charter": DocumentCategory.EDITORIAL_POLICIES,
    "Call for Papers - Inaugural Issues": DocumentCategory.CALL_FOR_PAPERS,
    "CFP Special Issues": DocumentCategory.CALL_FOR_PAPERS,
    "Submission Requirements": DocumentCategory.AUTHOR_GUIDELINES,
    "Submission Procedure": DocumentCategory.AUTHOR_GUIDELINES,
    "Special Issue Process": DocumentCategory.SPECIAL_ISSUE,
    "Reviewing Process": DocumentCategory.EDITORIAL_POLICIES,
    "Reviewer Anonymity Policy": DocumentCategory.EDITORIAL_POLICIES,
    "Resubmission Policy": DocumentCategory.EDITORIAL_POLICIES,
    "Formatting for Publication": DocumentCategory.AUTHOR_GUIDELINES,
    "Article Processing Charges (APC)": DocumentCategory.APC_POLICY,
    "Contact Us": DocumentCategory.OTHER,
    "Association for the Advancement of Knowledge Solutions (AAKS)": DocumentCategory.OTHER,
    "St. Joseph Institute of Technology": DocumentCategory.OTHER,
    "Journal Article Types and Style Guide": DocumentCategory.AUTHOR_GUIDELINES,
}


import sys

async def ingest_website() -> None:
    force_reindex = "--force" in sys.argv
    if not WEBSITE_JSON.exists():
        raise FileNotFoundError(f"Missing knowledge file: {WEBSITE_JSON}")

    await connect_to_mongo()
    admin = await User.find_one(User.email == "admin@ijaike.org")
    admin_id = admin.id if admin else None

    with WEBSITE_JSON.open(encoding="utf-8") as f:
        payload = json.load(f)

    ingest = IngestService()
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    for page in payload.get("pages", []):
        title = f"IJAIKE — {page['page_title']}"
        category = PAGE_CATEGORIES.get(page["page_title"], DocumentCategory.OTHER)
        text = page_to_text(page)
        filename = f"{page['page_title'].lower().replace(' ', '_')}.txt"

        existing = await Document.find_one(Document.title == title)
        if existing and existing.status == DocumentStatus.INDEXED and not force_reindex:
            print(f"SKIP (already indexed): {title}")
            continue

        doc_id = uuid4()
        dest_dir = UPLOAD_ROOT / category.value / str(doc_id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / filename
        async with aiofiles.open(dest_file, "w", encoding="utf-8") as out:
            await out.write(text)

        storage_path = f"{category.value}/{doc_id}/{filename}"

        if existing:
            document = existing
            document.file_path = storage_path
            document.status = DocumentStatus.PENDING
            document.error_message = None
            await document.save()
            doc_id = document.id
        else:
            document = Document(
                id=doc_id,
                title=title,
                filename=filename,
                file_path=storage_path,
                file_type="txt",
                file_size_bytes=len(text.encode("utf-8")),
                category=category,
                status=DocumentStatus.PENDING,
                uploaded_by=admin_id,
            )
            await document.insert()

        print(f"Processing: {title}...")
        await ingest.process_document(doc_id)
        print(f"  [OK] Indexed: {title}")

    await close_mongo_connection()
    print("\nAll website pages ingested into MongoDB + ChromaDB.")


if __name__ == "__main__":
    asyncio.run(ingest_website())
