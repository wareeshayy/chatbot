"""Run all knowledge-base ingestion: website JSON + PDFs."""

import asyncio

from scripts.ingest_pdfs import ingest_pdfs
from scripts.ingest_website import ingest_website


async def ingest_all() -> None:
    print("=== Ingesting IJAIKE website content ===\n")
    await ingest_website()
    print("\n=== Ingesting IJAIKE PDF documents ===\n")
    await ingest_pdfs()
    print("\n=== All ingestion complete ===")


if __name__ == "__main__":
    asyncio.run(ingest_all())
