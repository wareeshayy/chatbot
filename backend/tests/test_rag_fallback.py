"""Regression tests for selecting a fallback from the highest-ranked source."""

from app.services.rag_service import _fallback_text


def test_agentic_fallback_wins_when_agentic_source_is_first() -> None:
    context = """[Source 1: Agentic AI Solutions for Intelligent Chatbot Development, page 1]
RAG chatbots for universities.
[Source 2: Custom AI-Powered Web Applications & Full-Stack Software Development, page 2]
Enterprise portals."""

    assert _fallback_text(context).startswith("## JAIKE Agentic AI Chatbot Services")


def test_custom_web_fallback_wins_when_custom_source_is_first() -> None:
    context = """[Source 1: Custom AI-Powered Web Applications & Full-Stack Software Development, page 2]
Enterprise portals.
[Source 2: Agentic AI Solutions for Intelligent Chatbot Development, page 1]
RAG chatbots."""

    assert _fallback_text(context).startswith("## JAIKE Custom Web Application & Full-Stack Services")
