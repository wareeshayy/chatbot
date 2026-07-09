"""RAG service — ChromaDB retrieval + Gemini LLM generation with citations."""

import time
from dataclasses import dataclass

from app.config.logging_config import get_logger
from app.config.settings import get_settings
from app.embeddings.factory import embed_query
from app.llm.factory import generate_answer
from app.prompts.faq_fallback import faq_fallback
from app.schemas.common import CitationSchema
from app.vectorstore.chroma_store import ChromaStore

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class RAGResult:
    answer: str
    citations: list[CitationSchema]
    retrieved_chunk_ids: list[str]
    model_used: str | None = None
    latency_ms: int = 0


class RAGService:
    def __init__(self) -> None:
        self.chroma = ChromaStore.get_instance()

    async def retrieve_and_generate(
        self,
        query: str,
        conversation_history: list[dict] | None = None,
    ) -> RAGResult:
        start = time.perf_counter()

        if self._is_index_empty() and not settings.gemini_api_key:
            faq = faq_fallback(query)
            if faq:
                answer, faq_citations = faq
                latency_ms = int((time.perf_counter() - start) * 1000)
                return RAGResult(
                    answer=answer,
                    citations=faq_citations,
                    retrieved_chunk_ids=[],
                    model_used="faq-fallback",
                    latency_ms=latency_ms,
                )

        citations = await self._retrieve(query)

        if not citations:
            if not settings.gemini_api_key and not settings.openai_api_key:
                faq = faq_fallback(query)
                if faq:
                    answer, faq_citations = faq
                    latency_ms = int((time.perf_counter() - start) * 1000)
                    return RAGResult(
                        answer=answer,
                        citations=faq_citations,
                        retrieved_chunk_ids=[],
                        model_used="faq-fallback",
                        latency_ms=latency_ms,
                    )

        history_text = ""
        if conversation_history:
            history_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in conversation_history[-6:]
            )

        context = self._format_context(citations)
        answer = generate_answer(context, history_text, query)

        model = settings.gemini_model if settings.gemini_api_key else "retrieval-only"
        latency_ms = int((time.perf_counter() - start) * 1000)

        return RAGResult(
            answer=answer,
            citations=citations,
            retrieved_chunk_ids=[c.chunk_id for c in citations if c.chunk_id],
            model_used=model,
            latency_ms=latency_ms,
        )

    def _is_index_empty(self) -> bool:
        try:
            return self.chroma.collection.count() == 0
        except Exception:
            return True

    async def _retrieve(self, query: str, top_k: int | None = None) -> list[CitationSchema]:
        k = top_k or settings.rag_top_k
        if not settings.gemini_api_key:
            try:
                count = self.chroma.collection.count()
                if count == 0:
                    return []
            except Exception:
                return []

        try:
            query_embedding = embed_query(query)
            results = self.chroma.search(query_embedding, top_k=k)
        except Exception as exc:
            logger.warning("Vector search failed, using empty context: %s", exc)
            return []

        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        citations: list[CitationSchema] = []
        for i, chunk_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            doc_text = results["documents"][0][i] if results.get("documents") else ""
            distance = results["distances"][0][i] if results.get("distances") else 1.0
            relevance = max(0.0, 1.0 - distance)
            embedding_vals = results["embeddings"][0][i] if results.get("embeddings") else None

            if relevance < settings.rag_score_threshold:
                continue

            page_num = meta.get("page_number")
            citations.append(
                CitationSchema(
                    document_title=meta.get("document_title", "Unknown"),
                    page_number=int(page_num) if page_num and int(page_num) > 0 else None,
                    section=meta.get("section_title") or None,
                    chunk_id=chunk_id,
                    relevance_score=round(relevance, 2),
                    excerpt=doc_text[:300] + ("..." if len(doc_text) > 300 else ""),
                    embedding=embedding_vals,
                )
            )
        return citations

    def _format_context(self, citations: list[CitationSchema]) -> str:
        if not citations:
            return ""
        parts = []
        for i, cite in enumerate(citations, 1):
            header = f"[Source {i}: {cite.document_title}"
            if cite.page_number:
                header += f", page {cite.page_number}"
            header += "]"
            parts.append(f"{header}\n{cite.excerpt}")
        return "\n\n".join(parts)
