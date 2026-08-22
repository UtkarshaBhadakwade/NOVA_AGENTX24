import logging
from typing import Dict, Any
from backend.state import AgentState
from backend.tools import web_search

logger = logging.getLogger("nova_agent.market_agent")

def market_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    MARKET INTELLIGENCE AGENT
    Role: Competitor and Industry Intelligence Specialist.
    """
    query = state.get("search_query", state["objective"])
    year = state.get("year", "Any Year")
    timeframe = state.get("timeframe", "Latest")
    test_mode = state.get("test_mode", "normal")

    new_trace_events = [
        {
            "event": "[MARKET_INTELLIGENCE_AGENT]",
            "detail": f"Searching competitor & market developments via Tavily for: '{query}'"
        }
    ]
    
    # Adversarial Test Mode: Tool Failure Simulation
    if test_mode == "tool_failure":
        new_trace_events.append({
            "event": "[TOOL_FAILURE]",
            "detail": "Simulated Tavily Web Search API Failure (Adversarial Test)."
        })
        return {
            "market_results": [],
            "web_results": [],
            "failed_tools": ["Tavily"],
            "actions_taken": ["MarketIntelligenceAgent (Failed: Tavily)"],
            "agent_history": ["MarketIntelligenceAgent"],
            "trace_events": new_trace_events,
            "errors": ["Tavily API Simulated Failure"]
        }

    web_results = []
    errors = []
    
    try:
        web_results = web_search(query, year=year, timeframe=timeframe)
    except Exception as e:
        logger.error(f"MarketIntelligenceAgent Tavily error: {str(e)}")
        errors.append(f"Tavily Market Search Warning: {str(e)}")

    valid_web = [r for r in web_results if "Failure" not in r.get("title", "") and "Missing" not in r.get("title", "")]

    new_trace_events.append({
        "event": "[AGENT_COMPLETE]",
        "detail": f"Market Intelligence Agent completed: {len(valid_web)} live web results collected via Tavily."
    })

    findings_summary = {
        "agent": "MarketIntelligenceAgent",
        "query": query,
        "web_count": len(valid_web),
        "top_titles": [r.get("title") for r in valid_web[:4]]
    }

    return {
        "market_results": web_results,
        "web_results": web_results,
        "agent_findings": [findings_summary],
        "actions_taken": [f"MarketIntelligenceAgent (Tavily: {len(valid_web)})"],
        "agent_history": ["MarketIntelligenceAgent"],
        "trace_events": new_trace_events,
        "errors": errors
    }
