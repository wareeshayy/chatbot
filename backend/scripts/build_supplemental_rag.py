"""Build the bundled supplemental RAG index from service documents."""

import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "backend" / "data" / "supplemental_rag.json"
SOURCES = (
    (
        PROJECT_ROOT / "data" / "pdfs" / "Agentic_AI_Solutions_for_Intelligent_Chatbot_Development.pdf",
        "Agentic AI Solutions for Intelligent Chatbot Development",
    ),
    (
        PROJECT_ROOT / "data" / "pdfs" / "Custom_AI_Powered_Web_Applications_and_Full_Stack_Software_Development.pdf",
        "Custom AI-Powered Web Applications & Full-Stack Software Development",
    ),
)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_local_env() -> None:
    for env_path in (PROJECT_ROOT / "backend" / ".env", PROJECT_ROOT / ".env.local"):
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def source_pages(path: Path) -> list[tuple[int, str]]:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return [(number, (page.extract_text() or "").strip()) for number, page in enumerate(reader.pages, 1)]
    return [(1, path.read_text(encoding="utf-8").strip())]


def chunks_for(path: Path, title: str) -> list[dict]:
    chunks = []
    for page_number, text in source_pages(path):
        start = 0
        chunk_index = 0
        while start < len(text):
            content = text[start : start + CHUNK_SIZE].strip()
            if content:
                digest = hashlib.sha256(f"{path.name}:{page_number}:{chunk_index}:{content}".encode()).hexdigest()[:24]
                chunks.append(
                    {
                        "id": f"service_{digest}",
                        "document_title": title,
                        "source_file": path.name,
                        "page_number": page_number,
                        "section_title": "JAIKE Business Unit AI Services",
                        "content": content,
                    }
                )
            if start + CHUNK_SIZE >= len(text):
                break
            start += CHUNK_SIZE - CHUNK_OVERLAP
            chunk_index += 1
    return chunks


def embed(text: str, api_key: str, model: str) -> list[float]:
    model_path = model if model.startswith("models/") else f"models/{model}"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:embedContent"
    endpoint += "?" + urllib.parse.urlencode({"key": api_key})
    body = json.dumps(
        {
            "model": model_path,
            "content": {"parts": [{"text": text}]},
            "taskType": "RETRIEVAL_DOCUMENT",
        }
    ).encode()
    request = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)["embedding"]["values"]


def main() -> None:
    load_local_env()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model = os.environ.get("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-2")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required to build the supplemental RAG index")

    chunks = [chunk for path, title in SOURCES for chunk in chunks_for(path, title)]
    for number, chunk in enumerate(chunks, 1):
        chunk["embedding"] = embed(chunk["content"], api_key, model)
        print(f"Embedded {number}/{len(chunks)}: {chunk['source_file']} page {chunk['page_number']}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"embedding_model": model, "chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP, "chunks": chunks}),
        encoding="utf-8",
    )
    print(f"Wrote {len(chunks)} chunks to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
