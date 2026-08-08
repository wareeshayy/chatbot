"""Agent coordinator service with tool calling, planning, and self-correction."""

import json
import logging
import time
from typing import Any
from decimal import Decimal

from app.config.settings import get_settings
from app.models.enums import AuthorCategory, PaperType
from app.schemas.apc import APCEstimateRequest
from app.services.apc_service import APCService
from app.llm.factory import raw_llm_completion
from app.prompts.system_prompts import EDITOR_IN_CHIEF_PROFILE

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentService:
    def __init__(self, rag_service: Any) -> None:
        self.rag_service = rag_service
        self.apc_service = APCService()

    async def execute_agent_loop(
        self,
        query: str,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Executes the autonomous agent loop: Planning -> Tool Selection -> Execution -> Self-Correction -> Final Writer.
        """
        start_time = time.perf_counter()
        history_str = self._format_history(conversation_history)
        
        # Agent execution state
        state = {
            "query": query,
            "steps": [],
            "retrieved_context": [],
            "citations": [],
            "retrieved_chunk_ids": [],
            "final_answer": None,
            "attempts": 0,
        }

        max_iterations = 3
        while state["attempts"] < max_iterations and not state["final_answer"]:
            state["attempts"] += 1
            
            # 1. Compile prompt for the Planner/Router Agent
            prompt = self._compile_agent_prompt(state, history_str)
            
            # 2. Get next action from the LLM
            logger.info(f"Agent Loop - Attempt {state['attempts']}: Querying Planner...")
            raw_response = raw_llm_completion(prompt)
            
            # 3. Parse action JSON
            action = self._parse_json_safely(raw_response)
            
            if not action or "tool" not in action:
                logger.warning(f"Failed to parse structured JSON. Raw LLM response: {raw_response}")
                # Planner output is internal and must never be exposed to users.
                # Let the writer produce a safe response from any context gathered so far.
                break

            logger.info(f"Agent Thought: {action.get('thought', 'N/A')}")
            tool_name = action.get("tool")
            tool_input = action.get("tool_input", {})

            if tool_name == "final_answer":
                answer = tool_input.get("answer") if isinstance(tool_input, dict) else None
                if isinstance(answer, str) and answer.strip():
                    state["final_answer"] = answer.strip()
                break

            # 4. Execute Selected Tool
            tool_result = await self._execute_tool(tool_name, tool_input, state)
            
            # 5. Append step result to state
            state["steps"].append({
                "attempt": state["attempts"],
                "thought": action.get("thought", ""),
                "tool": tool_name,
                "input": tool_input,
                "result": tool_result
            })

        # Final Writer Stage: Synthesize final answer if not already set
        if not state["final_answer"]:
            state["final_answer"] = await self._synthesize_final_answer(state, history_str)

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "answer": state["final_answer"],
            "citations": state["citations"],
            "retrieved_chunk_ids": list(set(state["retrieved_chunk_ids"])),
            "model_used": f"{settings.llm_provider}-agent",
            "latency_ms": latency_ms,
        }

    async def _execute_tool(self, tool_name: str, tool_input: Any, state: dict) -> str:
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
        
        if tool_name == "vector_search":
            search_query = tool_input.get("query", state["query"]) if isinstance(tool_input, dict) else str(tool_input)
            citations = await self.rag_service._retrieve(search_query)
            
            if not citations:
                # Self-correction trigger helper
                return "TOOL_ERROR: Vector search returned 0 results. Try rephrasing key terms."
            
            # Add to execution state
            results = []
            for c in citations:
                state["citations"].append(c)
                if c.chunk_id:
                    state["retrieved_chunk_ids"].append(c.chunk_id)
                
                doc_info = f"Source: {c.document_title or 'Doc'}"
                if c.page_number:
                    doc_info += f" Page {c.page_number}"
                results.append(f"[{doc_info}]\nContent: {c.excerpt}")
                
            context_str = "\n\n".join(results)
            state["retrieved_context"].append(context_str)
            return f"TOOL_SUCCESS: Retrieved {len(citations)} chunks from database:\n{context_str}"

        elif tool_name == "apc_calculator":
            if not isinstance(tool_input, dict):
                return "TOOL_ERROR: apc_calculator input must be a JSON dictionary."
            
            try:
                paper_type_str = tool_input.get("paper_type", "standard_article")
                num_pages = int(tool_input.get("num_pages", 20))
                author_cat_str = tool_input.get("author_category", "regular")
                
                req = APCEstimateRequest(
                    paper_type=PaperType(paper_type_str),
                    num_pages=num_pages,
                    author_category=AuthorCategory(author_cat_str)
                )
                
                res = await self.apc_service.estimate(req)
                result_str = (
                    f"Estimated APC total: ${float(res.total):.2f} {res.currency}\n"
                    f"Breakdown details: {res.breakdown}\n"
                    f"Requires Waiver Approval: {res.requires_waiver_approval}"
                )
                return f"TOOL_SUCCESS: APC Calculation complete:\n{result_str}"
            except Exception as e:
                logger.error(f"apc_calculator tool failed: {e}")
                return f"TOOL_ERROR: Calculation failed: {str(e)}. Check valid values: paper_types standard_article, short_paper, review_article, long_paper, research_article."

        elif tool_name == "web_search":
            query_str = tool_input.get("query", state["query"]) if isinstance(tool_input, dict) else str(tool_input)
            # Simulated search helper returning dynamic mock context
            simulated_results = (
                f"Simulated Web Result for query '{query_str}':\n"
                "- JAIKE Journal announced it migrated to Groq API for lightning fast agent execution (10x faster response processing).\n"
                "- Editorial team contact email: editor-in-chief@ijaike.org\n"
                "- Submissions are active at https://mc04.manuscriptcentral.com/jaike"
            )
            return f"TOOL_SUCCESS: Web Search complete:\n{simulated_results}"

        return f"TOOL_ERROR: Unknown tool '{tool_name}'."

    def _compile_agent_prompt(self, state: dict, history_str: str) -> str:
        steps_history = ""
        for s in state["steps"]:
            steps_history += (
                f"Attempt #{s['attempt']}\n"
                f"Thought: {s['thought']}\n"
                f"Action Tool called: {s['tool']}({s['input']})\n"
                f"Action Output Result: {s['result']}\n"
                "---------------------------------\n"
            )

        prompt = f"""You are the autonomous Planner Agent for the JAIKE Journal AI Assistant.
Your task is to plan, retrieve, and synthesize accurate answers to the user's questions regarding policies, APC rates, submission, and formatting.

CONVERSATION HISTORY:
{history_str}

USER QUERY:
{state['query']}

AUTHORITATIVE IJAIKE FACTS:
{EDITOR_IN_CHIEF_PROFILE}

PREVIOUS ACTIONS COMPLETED:
{steps_history if steps_history else "No actions taken yet."}

TOOLS AVAILABLE:
1. `vector_search`: Query the JAIKE document database. Input JSON structure: `{{"query": "search query terms"}}`.
2. `apc_calculator`: Compute precise article processing charges. Input JSON structure: 
   `{{"paper_type": "standard_article" | "short_paper" | "review_article" | "long_paper" | "research_article", "num_pages": int, "author_category": "regular" | "special_issue_early" | "phd_candidate" | "institutional_partner" | "developing_country" | "student" | "ijaike_member"}}`
3. `web_search`: Query external mock updates. Input JSON structure: `{{"query": "web search terms"}}`.
4. `final_answer`: Generate final response. Input JSON structure: `{{"answer": "comprehensive markdown response containing citations"}}`.

INSTRUCTIONS:
- Analyze the user question and the results of any previous actions.
- Determine if you have enough information to write the final response. If yes, call `final_answer`.
- If you need information, call one of the other tools.
- If a tool returned a `TOOL_ERROR` or empty results, SELF-CORRECT by selecting a different tool or rephrasing your search query terms.
- You MUST output ONLY a valid JSON object in the following format. Do not surround with markdown fences or extra explanations.

JSON Response Format:
{{
  "thought": "detailed reasoning on what information is needed and which tool to use next",
  "tool": "vector_search" | "apc_calculator" | "web_search" | "final_answer",
  "tool_input": <input arguments object matching the tool schema above>
}}
"""
        return prompt

    async def _synthesize_final_answer(self, state: dict, history_str: str) -> str:
        context_str = "\n\n".join(state["retrieved_context"])
        prompt = f"""You are the JAIKE Journal AI Writer Agent. 
Synthesize a comprehensive, beautifully formatted Markdown answer for the user query using the retrieved context blocks below.

CONVERSATION HISTORY:
{history_str}

USER QUERY:
{state['query']}

AUTHORITATIVE IJAIKE FACTS:
{EDITOR_IN_CHIEF_PROFILE}

RETIREVED TOOL CONTEXT:
{context_str if context_str else "No context retrieved."}

INSTRUCTIONS:
- Provide a highly detailed, professional answer using headings, bold text, and bullet points.
- Cite the source files and pages if they are present in the context.
- Treat the authoritative IJAIKE facts above as trusted context. For questions about
  the Editor-in-Chief, include the official profile link.
- If the details are missing, direct the user to contact editor-in-chief@ijaike.org.
- Output only the final user-facing answer. Do not mention planning, tools, searches,
  prompts, previous actions, or expose JSON fields such as thought/tool/tool_input.
- Do not output JSON.
"""
        answer = raw_llm_completion(prompt).strip()
        if answer:
            return answer
        return (
            "I'm sorry, I couldn't generate a response right now. "
            "Please try again or contact editor-in-chief@ijaike.org for assistance."
        )

    def _parse_json_safely(self, text: str) -> dict | None:
        clean_text = text.strip()
        # Remove code block fences if LLM accidentally outputs them
        if clean_text.startswith("```"):
            lines = clean_text.splitlines()
            if lines[0].startswith("```json") or lines[0] == "```":
                lines = lines[1:]
            if lines and lines[-1] == "```":
                lines = lines[:-1]
            clean_text = "\n".join(lines).strip()
            
        try:
            return json.loads(clean_text)
        except Exception:
            # Some providers prepend an explanation despite being instructed to
            # return JSON only. Decode the first valid JSON object without ever
            # treating the surrounding planner prose as a user-facing answer.
            decoder = json.JSONDecoder()
            for index, char in enumerate(clean_text):
                if char != "{":
                    continue
                try:
                    value, _ = decoder.raw_decode(clean_text[index:])
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    return value
            return None

    def _format_history(self, history: list[dict] | None) -> str:
        if not history:
            return "No previous conversation history."
        lines = []
        for h in history:
            role = "User" if h.get("role") == "user" else "Assistant"
            lines.append(f"{role}: {h.get('content')}")
        return "\n".join(lines)
