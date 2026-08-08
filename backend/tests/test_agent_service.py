"""Regression tests for keeping planner output out of chatbot answers."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.agent_service import AgentService


class StubRAGService:
    _retrieve = AsyncMock(return_value=[])


def test_parse_json_with_surrounding_planner_prose() -> None:
    service = AgentService(StubRAGService())
    response = '''I should refine the search.
{"thought":"Need font details","tool":"vector_search","tool_input":{"query":"IJAIKE font margins"}}
Continuing now.'''

    action = service._parse_json_safely(response)

    assert action is not None
    assert action["tool"] == "vector_search"
    assert action["tool_input"]["query"] == "IJAIKE font margins"


@pytest.mark.asyncio
async def test_malformed_planner_output_is_not_returned_to_user() -> None:
    service = AgentService(StubRAGService())
    leaked_plan = 'analysis: {"thought":"search again","tool":"vector_search"'

    with patch(
        "app.services.agent_service.raw_llm_completion",
        side_effect=[leaked_plan, "A safe, final answer for the user."],
    ):
        result = await service.execute_agent_loop("What are the formatting requirements?")

    assert result["answer"] == "A safe, final answer for the user."
    assert leaked_plan not in result["answer"]


@pytest.mark.asyncio
async def test_empty_writer_response_uses_safe_fallback() -> None:
    service = AgentService(StubRAGService())

    with patch(
        "app.services.agent_service.raw_llm_completion",
        side_effect=["not valid planner JSON", ""],
    ):
        result = await service.execute_agent_loop("What are the formatting requirements?")

    assert "couldn't generate a response" in result["answer"]
    assert "planner" not in result["answer"].lower()
