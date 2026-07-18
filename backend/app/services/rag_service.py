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
        from app.services.agent_service import AgentService
        self.agent_service = AgentService(self)

    async def retrieve_and_generate(
        self,
        query: str,
        conversation_history: list[dict] | None = None,
    ) -> RAGResult:
        start = time.perf_counter()

        if self._has_llm():
            res = await self.agent_service.execute_agent_loop(query, conversation_history)
            return RAGResult(
                answer=res["answer"],
                citations=res["citations"],
                retrieved_chunk_ids=res["retrieved_chunk_ids"],
                model_used=res["model_used"],
                latency_ms=res["latency_ms"],
            )

        if await self._is_index_empty() and not self._has_llm():
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

        # If no LLM is configured at all, use FAQ fallback
        if not self._has_llm():
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
            # Retrieval-only mode — return raw context
            context = self._format_context(citations)
            latency_ms = int((time.perf_counter() - start) * 1000)
            return RAGResult(
                answer=_fallback_text(context),
                citations=citations,
                retrieved_chunk_ids=[c.chunk_id for c in citations if c.chunk_id],
                model_used="retrieval-only",
                latency_ms=latency_ms,
            )

        history_text = ""
        if conversation_history:
            history_text = "\n".join(
                f"{m['role']}: {m['content']}" for m in conversation_history[-6:]
            )

        context = self._format_context(citations)

        # Always call the LLM — even with empty context it can answer generic queries
        try:
            answer = generate_answer(context, history_text, query)
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            answer = ""

        # Last-resort fallback if LLM returned empty
        if not answer or not answer.strip():
            faq = faq_fallback(query)
            if faq:
                answer, citations = faq[0], faq[1]
            elif citations:
                answer = _fallback_text(context)
            else:
                answer = (
                    "I'm sorry, I couldn't generate a response right now. "
                    "Please try again or contact editor-in-chief@ijaike.org for assistance."
                )

        if settings.llm_provider == "groq" and settings.groq_api_key:
            model = settings.groq_model
        elif settings.llm_provider == "openrouter" and settings.openrouter_api_key:
            model = settings.openrouter_model
        elif settings.llm_provider == "openai" and settings.openai_api_key:
            model = settings.openai_model
        elif settings.llm_provider == "azure" and settings.azure_openai_api_key:
            model = settings.azure_openai_deployment
        else:
            model = settings.gemini_model if settings.gemini_api_key else "retrieval-only"
        latency_ms = int((time.perf_counter() - start) * 1000)

        return RAGResult(
            answer=answer,
            citations=citations,
            retrieved_chunk_ids=[c.chunk_id for c in citations if c.chunk_id],
            model_used=model,
            latency_ms=latency_ms,
        )

    def _has_llm(self) -> bool:
        """Returns True if any LLM provider is configured."""
        return bool(
            (settings.llm_provider == "groq" and settings.groq_api_key)
            or (settings.llm_provider == "gemini" and settings.gemini_api_key)
            or (settings.llm_provider == "openai" and settings.openai_api_key)
            or (settings.llm_provider == "openrouter" and settings.openrouter_api_key)
            or (settings.llm_provider == "azure" and settings.azure_openai_api_key)
        )

    async def _is_index_empty(self) -> bool:
        try:
            return await self.chroma.count() == 0
        except Exception:
            return True

    async def _retrieve(self, query: str, top_k: int | None = None) -> list[CitationSchema]:
        k = top_k or settings.rag_top_k
        if not self._has_llm() and not settings.gemini_api_key:
            try:
                count = await self.chroma.count()
                if count == 0:
                    return []
            except Exception:
                return []

        try:
            query_embedding = embed_query(query)
            results = await self.chroma.search(query_embedding, top_k=k)
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
