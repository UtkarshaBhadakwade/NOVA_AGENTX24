import os
import sys
import time
from typing import Dict, Any, Tuple

# Import tracer and existing agent without modifying production code
from backend.observability.tracer import NOVAObservabilityTracer
from backend.agent import agent_graph, MAX_ITERATIONS
from backend.state import AgentState

def run_controlled_failure_experiment(objective: str = "Analyze AI agent market news.") -> Tuple[Dict[str, Any], NOVAObservabilityTracer]:
    """
    CONTROLLED FAILURE EXPERIMENT (Task 7)
    
    Simulates a controlled tool failure / timeout scenario in test_mode='tool_failure'
    WITHOUT altering production tool behavior or breaking normal user queries.
    Captures baseline vs failure trace data.
    """
    tracer = NOVAObservabilityTracer(investigation_id="exp_failure_01")
    
    # Enable explicit test mode
    initial_state: AgentState = {
        "objective": objective,
        "timeframe": "Latest",
        "year": "Any Year",
        "source_filter": "All Sources",
        "quartile": "All Quartiles",
        "plan": [],
        "pending_tasks": [],
        "completed_tasks": [],
        "active_agents": [],
        "current_task": None,
        "delegated_agent": None,
        "research_results": [],
        "market_results": [],
        "web_results": [],
        "crossref_results": [],
        "verification_results": [],
        "evidence_conflicts": [],
        "failed_tools": ["Tavily"],
        "fallback_attempts": [],
        "hypothesis": None,
        "hypothesis_status": None,
        "memory_context": None,
        "confidence": None,
        "uncertainty": None,
        "resource_budget": {"max_iterations": MAX_ITERATIONS},
        "replan_count": 0,
        "loop_detected": False,
        "self_eval_passed": False,
        "data_availability_note": None,
        "test_mode": "tool_failure",
        "agent_findings": [],
        "agent_history": [],
        "actions_taken": [],
        "iteration_count": 0,
        "max_iterations": MAX_ITERATIONS,
        "evidence_sufficient": False,
        "task_complete": False,
        "final_report": None,
        "analysis_results": None,
        "trace_events": [],
        "errors": [],
        "next_action": "supervisor",
        "search_query": objective
    }

    # Record controlled failure event in tracer
    tracer.on_tool_start({"name": "Tavily Web Search"}, input_str=objective)
    time.sleep(0.1)
    tracer.on_tool_error(TimeoutError("Tavily Search API request timed out after 10.0s (Simulated Failure)"))

    final_state = agent_graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": "exp_failure_thread"}, "callbacks": [tracer]}
    )
    
    summary = tracer.export_trace_summary(final_state)
    return summary, tracer
