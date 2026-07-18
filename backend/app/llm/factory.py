"""LLM factory — Gemini (dev), OpenAI/Azure, OpenRouter, Groq (production)."""

from app.config.settings import get_settings
from app.prompts.system_prompts import IJAIKE_SYSTEM_PROMPT

settings = get_settings()


def generate_answer(system_context: str, chat_history: str, user_query: str) -> str:
    prompt = f"""{IJAIKE_SYSTEM_PROMPT}

CONTEXT DOCUMENTS:
{system_context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION:
{user_query}

INSTRUCTIONS FOR ANSWERING:
1. First, check if the USER QUESTION is a general knowledge/generic query (unrelated to the IJAIKE journal, e.g., science explanation, general code writing, math, greetings, etc.).
   - If it is a generic query, act as a helpful AI assistant and provide a detailed, comprehensive, and beautifully formatted answer using your general knowledge. Avoid referring to the context documents or mentioning that you lack context.
2. If the USER QUESTION is about the IJAIKE journal (its policies, APC, submission, formatting, peer review, special issues, etc.):
   - Prioritize using the CONTEXT DOCUMENTS provided above to answer.
   - Provide a highly detailed, comprehensive, beautifully formatted, and optimized answer (using Markdown, headers, bullet points, and bold text). Do not write short or restricted answers.
   - If the answer is not in the context, state that you don't have this specific details in the IJAIKE knowledge base, and suggest contacting the editorial office at editor-in-chief@ijaike.org or submitting via Manuscript Central: https://mc04.manuscriptcentral.com/jaike. Include source document names and page numbers when available.
"""

    if settings.llm_provider == "gemini" and settings.gemini_api_key:
        return _generate_gemini(prompt)
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return _generate_openai(prompt)
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        return _generate_openrouter(prompt)
    if settings.llm_provider == "groq" and settings.groq_api_key:
        return _generate_groq(prompt)
    # Fallback: return context-based summary without LLM
    return _fallback_answer(system_context, user_query)


def _generate_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.2, max_output_tokens=4096),
    )
    return response.text.strip()


def _generate_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content.strip()


def _fallback_answer(context: str, query: str) -> str:
    if not context.strip():
        return (
            "I don't have specific information about that in the IJAIKE knowledge base yet. "
            "Please contact the editorial office or visit https://ijaike.org"
        )
    return (
        "Based on the IJAIKE knowledge base (retrieval-only mode — add GEMINI_API_KEY for full AI answers):\n\n"
        + context[:3000]
    )


def _generate_openrouter(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    response = client.chat.completions.create(
        model=settings.openrouter_model or "openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000,
        extra_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "IJAIKE Chatbot",
        },
    )
    return response.choices[0].message.content.strip()


def _generate_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model=settings.groq_model or "llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=4096,
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def raw_llm_completion(prompt: str) -> str:
    if settings.llm_provider == "gemini" and settings.gemini_api_key:
        return _generate_gemini(prompt)
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return _generate_openai(prompt)
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        return _generate_openrouter(prompt)
    if settings.llm_provider == "groq" and settings.groq_api_key:
        return _generate_groq(prompt)
    return ""
