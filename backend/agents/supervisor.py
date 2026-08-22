import os
import json
import logging
from typing import Dict, Any
from backend.state import AgentState

logger = logging.getLogger("nova_agent.supervisor")

MAX_ITERATIONS = 8

def supervisor_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    SUPERVISOR AGENT (Orchestrator)
    
    Responsibilities:
    - Inspect shared state (objective, evidence collected, agent_history, errors).
    - Identify information gaps.
    - Dynamically decide which specialized agent to delegate next.
    - Emit safe, high-level trace events ([SUPERVISOR_AGENT], [DELEGATION]).
    - Enforce safety iteration limits (8).
    """
    objective = state["objective"]
    research_results = state.get("research_results", [])
    crossref_results = state.get("crossref_results", [])
    market_results = state.get("market_results", []) or state.get("web_results", [])
    analysis_results = state.get("analysis_results")
    agent_history = state.get("agent_history", [])
    iteration_count = state.get("iteration_count", 0) + 1

    new_trace_events = []
    new_errors = []

    # First execution trace event
    if not state.get("trace_events"):
        new_trace_events.append({
            "event": "[AGENT START]",
            "detail": f"Initializing Multi-Agent System for Objective: '{objective}'"
        })

    # Check Max Iterations Safety Guardrail (8)
    if iteration_count >= MAX_ITERATIONS:
        logger.info("Supervisor: Maximum iteration limit reached.")
        new_trace_events.append({
            "event": "[SUPERVISOR_AGENT]",
            "detail": "Maximum iteration limit reached. Directing Strategic Synthesis Agent to generate final report."
        })
        if not analysis_results:
            next_action = "strategic_synthesis_agent"
            delegated_name = "STRATEGIC_SYNTHESIS_AGENT"
        else:
            next_action = "finish"
            delegated_name = "FINISH"

        new_trace_events.append({
            "event": "[DELEGATION]",
            "detail": f"Assigned to: {delegated_name}"
        })
        return {
            "iteration_count": iteration_count,
            "actions_taken": [f"supervisor -> {next_action}"],
            "agent_history": [f"supervisor -> {next_action}"],
            "delegated_agent": next_action,
            "trace_events": new_trace_events,
            "next_action": next_action,
            "search_query": objective
        }

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    decision_json = None
    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import SystemMessage, HumanMessage

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.6-flash",
                google_api_key=api_key,
                temperature=0.1
            )

            prompt = f"""
You are the Supervisor Agent (Orchestrator) for NOVA Agent, a multi-agent competitive intelligence system.

USER OBJECTIVE:
"{objective}"

SHARED AGENT STATE:
- Iteration Count: {iteration_count}/{MAX_ITERATIONS}
- Agent History: {agent_history}
- Research Papers Collected (arXiv + CrossRef): {len(research_results) + len(crossref_results)}
- Market Evidence Collected (Tavily Web Search): {len(market_results)}
- Strategic Analysis Completed: {bool(analysis_results)}

AVAILABLE SPECIALIZED AGENTS:
1. "research_agent": Scientific & Technical Intelligence Specialist (searches arXiv & CrossRef papers).
2. "market_intelligence_agent": Competitor & Industry Intelligence Specialist (searches Tavily web news, product launches, company updates).
3. "strategic_synthesis_agent": Strategic Intelligence Analyst (synthesizes evidence into structured intelligence report using Gemini).
4. "finish": Concludes multi-agent workflow when final report is compiled.

DYNAMIC DELEGATION INSTRUCTIONS:
Analyze the objective and current state:
- If the objective is primarily about research/technical trends ("research", "papers", "academic") and research_agent has NOT run yet, delegate to "research_agent".
- If the objective is primarily about competitors/market trends ("competitor", "industry", "platform") and market_intelligence_agent has NOT run yet, delegate to "market_intelligence_agent".
- If the objective requires broad intelligence ("opportunity or threat", "developments in AI") and missing evidence, delegate to "research_agent" first, then "market_intelligence_agent".
- If evidence exists (or specialized agents have run) but strategic_synthesis_agent has NOT run yet, delegate to "strategic_synthesis_agent".
- If strategic_synthesis_agent has been completed, select "finish".

Respond ONLY with valid JSON:
{{
  "action": "research_agent" | "market_intelligence_agent" | "strategic_synthesis_agent" | "finish",
  "reasoning_status": "<High-level 1-sentence safe status describing why this agent is selected>",
  "search_query": "<Focused search query for specialized agent, or empty string if synthesis/finish>"
}}
"""
            messages = [
                SystemMessage(content="You are a multi-agent supervisor orchestrator node."),
                HumanMessage(content=prompt)
            ]

            res = llm.invoke(messages)
            raw_content = res.content
            if isinstance(raw_content, list):
                content_str = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in raw_content]).strip()
            else:
                content_str = str(raw_content).strip()

            if content_str.startswith("```json"):
                content_str = content_str[7:]
            if content_str.startswith("```"):
                content_str = content_str[3:]
            if content_str.endswith("```"):
                content_str = content_str[:-3]
            content_str = content_str.strip()

            decision_json = json.loads(content_str)
        except Exception as e:
            logger.error(f"Supervisor LLM error: {str(e)}")
            new_errors.append(f"Supervisor LLM warning: {str(e)}")

    # Dynamic deterministic fallbacks if Gemini API is missing, rate-limited, or encounters issues
    if not decision_json:
        research_called = any("research_agent" in a for a in agent_history)
        market_called = any("market_intelligence_agent" in a for a in agent_history)
        synthesis_called = any("strategic_synthesis_agent" in a for a in agent_history)

        obj_lower = objective.lower()
        is_pure_research = any(k in obj_lower for k in ["research trends", "scientific", "papers", "technical publication"]) and not any(k in obj_lower for k in ["competitor", "market"])
        is_pure_market = any(k in obj_lower for k in ["competitor", "industry developments", "market"]) and not any(k in obj_lower for k in ["research trends", "papers"])

        if is_pure_research and not research_called:
            decision_json = {
                "action": "research_agent",
                "reasoning_status": "Supervisor evaluating research objective and delegating technical research gathering to Research Agent.",
                "search_query": objective
            }
        elif is_pure_market and not market_called:
            decision_json = {
                "action": "market_intelligence_agent",
                "reasoning_status": "Supervisor evaluating market objective and delegating market intelligence gathering to Market Intelligence Agent.",
                "search_query": objective
            }
        elif not research_called:
            decision_json = {
                "action": "research_agent",
                "reasoning_status": "Supervisor delegating technical research gathering to Research Agent.",
                "search_query": objective
            }
        elif not market_called:
            decision_json = {
                "action": "market_intelligence_agent",
                "reasoning_status": "Supervisor delegating market intelligence gathering to Market Intelligence Agent.",
                "search_query": objective
            }
        elif not synthesis_called:
            decision_json = {
                "action": "strategic_synthesis_agent",
                "reasoning_status": "Available evidence is sufficient for strategic analysis. Directing Strategic Synthesis Agent.",
                "search_query": ""
            }
        else:
            decision_json = {
                "action": "finish",
                "reasoning_status": "Multi-agent intelligence gathering completed.",
                "search_query": ""
            }

    action = decision_json.get("action", "finish")
    reasoning_status = decision_json.get("reasoning_status", "Supervisor evaluating shared state and delegating task.")
    search_query = decision_json.get("search_query", objective) or objective

    valid_actions = ["research_agent", "market_intelligence_agent", "strategic_synthesis_agent", "finish"]
    if action not in valid_actions:
        new_errors.append(f"Invalid action '{action}'. Defaulting to finish.")
        action = "finish"

    agent_names_map = {
        "research_agent": "RESEARCH_AGENT",
        "market_intelligence_agent": "MARKET_INTELLIGENCE_AGENT",
        "strategic_synthesis_agent": "STRATEGIC_SYNTHESIS_AGENT",
        "finish": "FINISH"
    }
    delegated_name = agent_names_map.get(action, "FINISH")

    new_trace_events.append({
        "event": "[SUPERVISOR_AGENT]",
        "detail": reasoning_status
    })
    
    if action != "finish":
        new_trace_events.append({
            "event": "[DELEGATION]",
            "detail": f"Assigned to: {delegated_name}"
        })

    return {
        "iteration_count": iteration_count,
        "actions_taken": [f"supervisor -> {action}"],
        "agent_history": [f"supervisor -> {action}"],
        "delegated_agent": action,
        "trace_events": new_trace_events,
        "errors": new_errors,
        "next_action": action,
        "search_query": search_query
    }
