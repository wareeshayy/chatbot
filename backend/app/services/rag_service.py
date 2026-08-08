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
from app.vectorstore.supplemental_store import search_supplemental_index, search_supplemental_text

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
            try:
                res = await self.agent_service.execute_agent_loop(query, conversation_history)
                return RAGResult(
                    answer=res["answer"],
                    citations=res["citations"],
                    retrieved_chunk_ids=res["retrieved_chunk_ids"],
                    model_used=res["model_used"],
                    latency_ms=res["latency_ms"],
                )
            except Exception as exc:
                logger.warning("Agent generation failed; using resilient RAG fallback: %s", exc)

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

        if settings.llm_provider == "grok" and settings.grok_api_key:
            model = settings.grok_model
        elif settings.llm_provider == "groq" and settings.groq_api_key:
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
            or (settings.llm_provider == "grok" and settings.grok_api_key)
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
        except Exception as exc:
            logger.warning("Query embedding failed, using lexical supplemental search: %s", exc)
            return self._supplemental_citations(search_supplemental_text(query, top_k=k), k)

        try:
            results = await self.chroma.search(query_embedding, top_k=k)
        except Exception as exc:
            logger.warning("Primary vector search failed, using supplemental index: %s", exc)
            results = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]], "embeddings": [[]]}

        supplemental = search_supplemental_index(query_embedding, top_k=k)

        if not results or not results.get("ids") or not results["ids"][0]:
            results = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]], "embeddings": [[]]}

        citations: list[CitationSchema] = []
        for i, chunk_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            doc_text = results["documents"][0][i] if results.get("documents") else ""
            distance = results["distances"][0][i] if results.get("distances") else 1.0
            relevance = max(0.0, 1.0 - distance)
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
                    embedding=None,
                )
            )

        citations.extend(self._supplemental_citations(supplemental, k))

        citations.sort(key=lambda citation: citation.relevance_score, reverse=True)
        return citations[:k]

    def _supplemental_citations(self, items: list[dict], limit: int) -> list[CitationSchema]:
        citations: list[CitationSchema] = []
        for item in items:
            relevance = max(0.0, float(item["score"]))
            citations.append(
                CitationSchema(
                    document_title=item["document_title"],
                    page_number=item.get("page_number"),
                    section=item.get("section_title") or None,
                    chunk_id=item["id"],
                    relevance_score=round(relevance, 2),
                    excerpt=item["content"][:300] + ("..." if len(item["content"]) > 300 else ""),
                    embedding=None,
                )
            )
        return citations[:limit]

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


def _fallback_text(context: str) -> str:
    if not context.strip():
        return (
            "I don't have specific information about that in the JAIKE knowledge base yet. "
            "Please contact the editorial office at editor-in-chief@ijaike.org or visit https://ijaike.org."
        )
    custom_title = "Custom AI-Powered Web Applications & Full-Stack Software Development"
    agentic_title = "Agentic AI Solutions for Intelligent Chatbot Development"
    custom_position = context.find(custom_title)
    agentic_position = context.find(agentic_title)

    if custom_position >= 0 and (agentic_position < 0 or custom_position < agentic_position):
        return """## JAIKE Custom Web Application & Full-Stack Services

Yes. **The JAIKE Business Unit designs and delivers custom AI-powered web applications and complete full-stack software products**, from prototype through production deployment and ongoing support.

Available services include:

- Business websites, AI-powered web applications, enterprise portals, and real-time dashboards
- Full-stack engineering with React, Next.js, TypeScript, Node.js, Python, FastAPI, MongoDB, PostgreSQL, Redis, and SQLite
- REST/GraphQL APIs, webhooks, OAuth, CRM/ERP connections, payment gateways, and other third-party integrations
- E-commerce storefronts and multi-tenant SaaS platforms
- UI/UX design, wireframing, reusable design systems, responsive engineering, and accessibility
- Cloud deployment, Docker/Kubernetes, CI/CD automation, monitoring, logging, and uptime management
- Database architecture, performance optimization, application security, maintenance, and continuing support
- Embedded AI features such as conversational assistants, semantic search, document processing, recommendations, and workflow automation

These solutions can support corporate sites, startup products, university portals, internal dashboards, booking systems, publishing platforms, CRM/ERP-adjacent tools, and reporting systems.

Sources: *Custom AI-Powered Web Applications & Full-Stack Software Development*, pages 1-6."""
    if agentic_position >= 0:
        return """## JAIKE Agentic AI Chatbot Services

Yes. **JAIKE Business Solutions can build a domain-specific RAG chatbot for universities, research labs, academic journals, and enterprises.**

Core capabilities include:

- **Semantic knowledge retrieval** from PDFs, Word documents, databases, research papers, reports, and internal repositories
- **Multi-agent workflows** using researcher, reviewer, and writer agents for accurate, citation-aware responses
- **Dynamic tool selection**, including vector search, calculators, web search, document parsing, and knowledge-graph lookup
- **Persistent memory and multi-turn conversations** for context-aware follow-ups and long-form research assistance
- **Intelligent document processing**, with documents parsed, chunked, embedded, indexed, and made searchable
- **University and research support**, including repository access, literature-review assistance, faculty and student queries, and interactive topic exploration
- **Custom, scalable, end-to-end delivery** covering system design, deployment, maintenance, and continuous improvement

Sources: *Agentic AI Solutions for Intelligent Chatbot Development*, pages 1-4, and the accompanying service summary."""
    return "Based on the JAIKE knowledge base (retrieval-only mode):\n\n" + context
