import logging
from typing import Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from backend.state import AgentState
from backend.agents import (
    supervisor_agent_node,
    research_agent_node,
    market_agent_node,
    synthesis_agent_node
)

# Load environment variables
load_dotenv()

logger = logging.getLogger("nova_agent.agent")

MAX_ITERATIONS = 8

def finish_node(state: AgentState) -> Dict[str, Any]:
    """
    FINISH NODE
    Responsibility: Finalizes structured report output and emits completion trace events.
    """
    objective = state["objective"]
    web_results = state.get("web_results", []) or state.get("market_results", [])
    research_results = state.get("research_results", [])
    crossref_results = state.get("crossref_results", [])
    analysis = state.get("analysis_results") or {}

    # Compile Sources Used
    sources_used = []
    for item in web_results:
        if item.get("url"):
            sources_used.append(f"Web (Tavily): {item.get('title')} ({item.get('url')})")
    for item in research_results:
        if item.get("url"):
            sources_used.append(f"arXiv: {item.get('title')} ({item.get('url')})")
    for item in crossref_results:
        if item.get("url"):
            sources_used.append(f"CrossRef: {item.get('title')} ({item.get('url')})")

    # Important evidence summary
    important_evidence = []
    for item in web_results[:2]:
        important_evidence.append(f"Web Evidence (Tavily): {item.get('title')} - {item.get('content')[:150]}...")
    for item in research_results[:2]:
        important_evidence.append(f"Research Paper (arXiv): {item.get('title')} - {item.get('summary')[:150]}...")
    for item in crossref_results[:2]:
        important_evidence.append(f"Research Paper (CrossRef): {item.get('title')} - {item.get('summary')[:150]}...")

    final_report = {
        "EXECUTIVE SUMMARY": f"Competitive intelligence assessment regarding '{objective}'. Analyzed {len(web_results)} web sources via Tavily API, {len(research_results)} arXiv research papers, and {len(crossref_results)} CrossRef research papers.",
        "KEY DEVELOPMENTS": analysis.get("key_developments", ["Active developments observed in market and research data."]),
        "IMPORTANT EVIDENCE": important_evidence if important_evidence else ["Collected empirical data from Tavily web search, arXiv, and CrossRef."],
        "EMERGING TRENDS": analysis.get("emerging_trends", ["Accelerated momentum in key technological capabilities."]),
        "OPPORTUNITIES": analysis.get("opportunities", ["Strategic expansion into identified high-impact sectors."]),
        "THREATS AND RISKS": analysis.get("threats_and_risks", ["Potential market displacement and technological disruption."]),
        "STRATEGIC IMPLICATIONS": analysis.get("strategic_implications", ["Organisations should maintain proactive monitoring and agile response capability."]),
        "RECOMMENDED ACTIONS": analysis.get("recommended_actions", ["Implement regular intelligence updates and evaluate strategic pilot initiatives."]),
        "CONFIDENCE LEVEL": analysis.get("confidence_level", "HIGH"),
        "SOURCES USED": sources_used if sources_used else ["Tavily Web, arXiv, and CrossRef research feeds"]
    }

    new_trace_events = [
        {
            "event": "[DECISION]",
            "detail": "Task complete."
        },
        {
            "event": "[TASK_COMPLETE]",
            "detail": "Multi-agent task execution finished successfully."
        },
        {
            "event": "[FINAL INTELLIGENCE REPORT]",
            "detail": final_report
        }
    ]

    return {
        "task_complete": True,
        "final_report": final_report,
        "actions_taken": ["finish"],
        "trace_events": new_trace_events
    }


def route_next_agent(state: AgentState) -> str:
    """
    Conditional router mapping Supervisor decisions to agent graph edges.
    """
    return state.get("next_action", "finish")


# ============================================================================
# LANGGRAPH MULTI-AGENT ORCHESTRATION GRAPH
# ============================================================================
graph_builder = StateGraph(AgentState)

# Add Agent Nodes
graph_builder.add_node("supervisor", supervisor_agent_node)
graph_builder.add_node("research_agent", research_agent_node)
graph_builder.add_node("market_intelligence_agent", market_agent_node)
graph_builder.add_node("strategic_synthesis_agent", synthesis_agent_node)
graph_builder.add_node("finish", finish_node)

# Set Entry Point to Supervisor
graph_builder.set_entry_point("supervisor")

# Supervisor Dynamic Routing Edges
graph_builder.add_conditional_edges(
    "supervisor",
    route_next_agent,
    {
        "research_agent": "research_agent",
        "market_intelligence_agent": "market_intelligence_agent",
        "strategic_synthesis_agent": "strategic_synthesis_agent",
        "finish": "finish"
    }
)

# Return Edges from Specialized Agents back to Supervisor
graph_builder.add_edge("research_agent", "supervisor")
graph_builder.add_edge("market_intelligence_agent", "supervisor")
graph_builder.add_edge("strategic_synthesis_agent", "supervisor")

# End Edge
graph_builder.add_edge("finish", END)

# Compile Multi-Agent Graph
agent_graph = graph_builder.compile()
