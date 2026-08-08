"""Tests for the bundled supplemental vector index."""

from app.vectorstore import supplemental_store


def test_supplemental_search_ranks_cosine_similarity(monkeypatch) -> None:
    chunks = [
        {"id": "matching", "embedding": [1.0, 0.0], "content": "RAG services"},
        {"id": "different", "embedding": [0.0, 1.0], "content": "Other content"},
    ]
    monkeypatch.setattr(supplemental_store, "_load_index", lambda: chunks)

    results = supplemental_store.search_supplemental_index([1.0, 0.0], top_k=2)

    assert [result["id"] for result in results] == ["matching", "different"]
    assert results[0]["score"] == 1.0


def test_supplemental_search_ignores_wrong_embedding_dimensions(monkeypatch) -> None:
    monkeypatch.setattr(
        supplemental_store,
        "_load_index",
        lambda: [{"id": "wrong-size", "embedding": [1.0], "content": "Ignored"}],
    )

    assert supplemental_store.search_supplemental_index([1.0, 0.0]) == []


def test_lexical_fallback_finds_service_capabilities(monkeypatch) -> None:
    chunks = [
        {"id": "rag", "document_title": "Agentic AI", "content": "RAG chatbot for universities"},
        {"id": "other", "document_title": "Unrelated", "content": "Publication formatting"},
    ]
    monkeypatch.setattr(supplemental_store, "_load_index", lambda: chunks)

    results = supplemental_store.search_supplemental_text("RAG chatbot university", top_k=2)

    assert results[0]["id"] == "rag"
