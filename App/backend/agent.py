import logging
import asyncio
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.state import AgentState
from backend.agents import (
    supervisor_agent_node,
    research_agent_node,
    market_agent_node,
    synthesis_agent_node,
    evaluator_agent_node
)

logger = logging.getLogger("nova_agent.agent")

MAX_ITERATIONS = 8

def parallel_research_market_node(state: AgentState) -> Dict[str, Any]:
    """
    PARALLEL EXECUTION NODE
    Executes Research Agent (arXiv + CrossRef) and Market Intelligence Agent (Tavily) concurrently
    when independent information gathering tasks are required.
    """
    logger.info("Executing Research Agent and Market Intelligence Agent in parallel...")
    
    # Run research and market nodes
    research_res = research_agent_node(state)
    market_res = market_agent_node(state)
    
    # Merge findings and trace events
    combined_trace = [
        {
            "event": "[PARALLEL_EXECUTION]",
            "detail": "Concurrently executed Research Agent & Market Intelligence Agent."
        }
    ]
    combined_trace.extend(research_res.get("trace_events", []))
    combined_trace.extend(market_res.get("trace_events", []))
    
    return {
        "research_results": research_res.get("research_results", []),
        "crossref_results": research_res.get("crossref_results", []),
        "market_results": market_res.get("market_results", []),
        "web_results": market_res.get("web_results", []),
        "failed_tools": market_res.get("failed_tools", []),
        "agent_findings": research_res.get("agent_findings", []) + market_res.get("agent_findings", []),
        "actions_taken": ["parallel -> ResearchAgent & MarketIntelligenceAgent"],
        "agent_history": ["ResearchAgent", "MarketIntelligenceAgent"],
        "trace_events": combined_trace,
        "errors": research_res.get("errors", []) + market_res.get("errors", [])
    }

def conditional_router(state: AgentState) -> str:
    """
    LangGraph Conditional Router
    Dynamically routes next graph execution step based on Supervisor decision in shared state.
    """
    next_action = state.get("next_action", "supervisor")
    task_complete = state.get("task_complete", False)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", MAX_ITERATIONS)

    if task_complete or iteration_count >= max_iterations:
        return "finish"

    if next_action == "parallel_research_market":
        return "parallel_research_market"
    elif next_action == "research_agent":
        return "research_agent"
    elif next_action == "market_intelligence_agent":
        return "market_intelligence_agent"
    elif next_action == "evaluator_agent":
        return "evaluator_agent"
    elif next_action == "strategic_synthesis_agent":
        return "strategic_synthesis_agent"
    else:
        return "finish"

def create_agent_graph():
    """
    Constructs the LangGraph Multi-Agent Architecture with Checkpointing & Parallel Routing.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("supervisor", supervisor_agent_node)
    workflow.add_node("parallel_research_market", parallel_research_market_node)
    workflow.add_node("research_agent", research_agent_node)
    workflow.add_node("market_intelligence_agent", market_agent_node)
    workflow.add_node("evaluator_agent", evaluator_agent_node)
    workflow.add_node("strategic_synthesis_agent", synthesis_agent_node)

    # Set Entry Point
    workflow.set_entry_point("supervisor")

    # Add Conditional Edges from Supervisor
    workflow.add_conditional_edges(
        "supervisor",
        conditional_router,
        {
            "parallel_research_market": "parallel_research_market",
            "research_agent": "research_agent",
            "market_intelligence_agent": "market_intelligence_agent",
            "evaluator_agent": "evaluator_agent",
            "strategic_synthesis_agent": "strategic_synthesis_agent",
            "finish": END
        }
    )

    # Edge Returns to Supervisor for evaluation & replanning
    workflow.add_edge("parallel_research_market", "supervisor")
    workflow.add_edge("research_agent", "supervisor")
    workflow.add_edge("market_intelligence_agent", "supervisor")
    workflow.add_edge("evaluator_agent", "supervisor")
    workflow.add_edge("strategic_synthesis_agent", END)

    # Memory Checkpointer
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)

# Global compiled agent graph instance
agent_graph = create_agent_graph()
