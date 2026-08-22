import logging
from typing import Dict, Any
from backend.state import AgentState
from backend.tools import analyze_information

logger = logging.getLogger("nova_agent.synthesis_agent")

def synthesis_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    STRATEGIC SYNTHESIS AGENT
    Role: Strategic Intelligence Analyst.
    
    Responsibilities:
    - Receives research evidence (arXiv + CrossRef) and market evidence (Tavily).
    - Uses Gemini 3.6 Flash to synthesize grounded evidence into a structured intelligence report.
    - Emits safe trace events ([STRATEGIC_SYNTHESIS_AGENT], [TOOL_RESULT]).
    """
    objective = state["objective"]
    web_results = state.get("web_results", []) or state.get("market_results", [])
    research_results = state.get("research_results", [])
    crossref_results = state.get("crossref_results", [])

    new_trace_events = [
        {
            "event": "[STRATEGIC_SYNTHESIS_AGENT]",
            "detail": "Generating evidence-based strategic intelligence from collected research and market data."
        }
    ]

    analysis = analyze_information(objective, web_results, research_results, crossref_results)

    new_trace_events.append({
        "event": "[TOOL_RESULT]",
        "detail": f"Strategic analysis complete with confidence level: {analysis.get('confidence_level', 'N/A')}."
    })

    return {
        "analysis_results": analysis,
        "evidence_sufficient": True,
        "actions_taken": ["StrategicSynthesisAgent:analyze_information"],
        "agent_history": ["StrategicSynthesisAgent"],
        "trace_events": new_trace_events
    }
