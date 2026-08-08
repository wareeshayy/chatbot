"""Read-only supplemental vector index bundled with the application."""

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


INDEX_PATH = Path(__file__).resolve().parents[2] / "data" / "supplemental_rag.json"


@lru_cache(maxsize=1)
def _load_index() -> list[dict[str, Any]]:
    if not INDEX_PATH.exists():
        return []
    with INDEX_PATH.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    return payload.get("chunks", [])


def search_supplemental_index(query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
    """Return supplemental chunks ranked by cosine similarity."""
    query_norm = math.sqrt(sum(value * value for value in query_embedding))
    if not query_norm:
        return []

    ranked: list[tuple[float, dict[str, Any]]] = []
    for chunk in _load_index():
        embedding = chunk.get("embedding") or []
        if len(embedding) != len(query_embedding):
            continue
        embedding_norm = math.sqrt(sum(value * value for value in embedding))
        if not embedding_norm:
            continue
        score = sum(a * b for a, b in zip(query_embedding, embedding)) / (query_norm * embedding_norm)
        ranked.append((score, chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [{**chunk, "score": score} for score, chunk in ranked[:top_k]]


def search_supplemental_text(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Quota-safe lexical fallback over the same embedded document chunks."""
    terms = {term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 2}
    if not terms:
        return []

    ranked: list[tuple[float, dict[str, Any]]] = []
    for chunk in _load_index():
        searchable = f"{chunk.get('document_title', '')} {chunk.get('content', '')}".lower()
        matches = sum(1 for term in terms if term in searchable)
        if matches:
            ranked.append((matches / len(terms), chunk))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [{**chunk, "score": score} for score, chunk in ranked[:top_k]]
