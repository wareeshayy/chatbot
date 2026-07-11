"""Ingest IJAIKE PDF documents into MongoDB + ChromaDB."""

import asyncio
import shutil
from pathlib import Path
from uuid import uuid4

from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.models.document import Document
from app.models.enums import DocumentStatus
from app.models.user import User
from app.services.ingest_service import IngestService
from app.utils.pdf_catalog import discover_pdf_sources

UPLOAD_ROOT = Path("./uploads")


async def ingest_pdfs(*, force_reindex: bool = False) -> None:
    await connect_to_mongo()

    admin = await User.find_one(User.email == "admin@ijaike.org")
    admin_id = admin.id if admin else None

    ingest = IngestService()
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    sources = discover_pdf_sources()
    if not sources:
        print("No PDFs found in data/pdfs/")
        await close_mongo_connection()
        return

    print(f"Found {len(sources)} PDF(s) to ingest.\n")

    for item in sources:
        src = Path(item["path"])
        if not src.exists():
            print(f"SKIP (not found): {src}")
            continue

        existing = await Document.find_one(Document.title == item["title"])
        if existing and existing.status == DocumentStatus.INDEXED and not force_reindex:
            print(f"SKIP (already indexed): {item['title']}")
            continue

        doc_id = uuid4()
        dest_dir = UPLOAD_ROOT / item["category"].value / str(doc_id)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / src.name
        shutil.copy2(src, dest_file)
        storage_path = f"{item['category'].value}/{doc_id}/{src.name}"

        if existing:
            document = existing
            document.file_path = storage_path
            document.status = DocumentStatus.PENDING
            document.error_message = None
            document.category = item["category"]
            await document.save()
            doc_id = document.id
        else:
            document = Document(
                id=doc_id,
                title=item["title"],
                filename=src.name,
                file_path=storage_path,
                file_type="pdf",
                file_size_bytes=src.stat().st_size,
                category=item["category"],
                status=DocumentStatus.PENDING,
                uploaded_by=admin_id,
            )
            await document.insert()

        print(f"Processing: {item['title']}...")
        try:
            await ingest.process_document(doc_id)
            print(f"  [OK] Indexed: {item['title']}")
        except Exception as exc:
            print(f"  [ERROR] Failed: {item['title']} — {exc}")

    await close_mongo_connection()
    print("\nPDF ingestion complete.")


if __name__ == "__main__":
    asyncio.run(ingest_pdfs())
