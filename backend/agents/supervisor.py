import os
import logging
from typing import Dict, Any, List
from backend.state import AgentState

logger = logging.getLogger("nova_agent.supervisor")

def supervisor_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    SUPERVISOR AGENT (Dynamic Planning, Orchestration, Loop Detection & Fallback Recovery)
    
    Responsibilities:
    - Analyzes user objective and long-term memory context to create dynamic execution plan.
    - Decides whether to dispatch parallel execution or specific specialized agents.
    - Detects loops/deadlocks if identical actions are repeated.
    - Manages failure recovery and fallback strategies when tools fail.
    - Monitors iteration budget and triggers self-evaluation before synthesis.
    """
    objective = state["objective"]
    history = state.get("agent_history", [])
    iteration_count = state.get("iteration_count", 0) + 1
    max_iterations = state.get("max_iterations", 8)
    
    research_results = state.get("research_results", [])
    market_results = state.get("market_results", []) or state.get("web_results", [])
    crossref_results = state.get("crossref_results", [])
    
    failed_tools = state.get("failed_tools", [])
    test_mode = state.get("test_mode", "normal")
    replan_count = state.get("replan_count", 0)
    self_eval_passed = state.get("self_eval_passed", False)
    
    new_trace_events = []

    # 1. Dynamic Planning on First Iteration
    if iteration_count == 1:
        new_trace_events.append({"event": "[PLANNING]", "detail": f"Analyzing objective: '{objective}'"})
        
        # Check long-term memory context
        memory_ctx = state.get("memory_context")
        if memory_ctx:
            new_trace_events.append({
                "event": "[MEMORY_FOUND]",
                "detail": f"Loaded relevant past investigation '{memory_ctx.get('objective', '')[:40]}...'"
            })
            
        obj_lower = objective.lower()
        plan_steps = []
        if "research" in obj_lower or "paper" in obj_lower:
            plan_steps = ["Gather scientific papers via arXiv & CrossRef", "Evaluate evidence", "Synthesize report"]
        elif "market" in obj_lower or "competitor" in obj_lower:
            plan_steps = ["Gather market intelligence via Tavily", "Evaluate evidence", "Synthesize report"]
        else:
            plan_steps = ["Parallel Research & Market Gathering", "Evaluate evidence & hypothesis", "Synthesize report"]
            
        new_trace_events.append({
            "event": "[PLAN_CREATED]",
            "detail": f"Plan: {', '.join(plan_steps)}"
        })

    # 2. Resource-Aware Budget Monitoring
    remaining_iterations = max_iterations - iteration_count
    new_trace_events.append({
        "event": "[RESOURCE_STATUS]",
        "detail": f"Iteration {iteration_count}/{max_iterations} | Remaining budget: {remaining_iterations} steps"
    })
    
    if test_mode == "resource_constraint" and iteration_count >= 2:
        new_trace_events.append({
            "event": "[RESOURCE_DECISION]",
            "detail": "Resource budget constraint reached. Prioritizing synthesis with available evidence."
        })
        return {
            "next_action": "strategic_synthesis_agent",
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> strategic_synthesis_agent (resource_constraint)"],
            "trace_events": new_trace_events
        }

    # 3. Loop & Deadlock Detection
    recent_actions = history[-3:] if len(history) >= 3 else history
    if len(recent_actions) >= 2 and len(set(recent_actions)) == 1:
        new_trace_events.append({
            "event": "[LOOP_DETECTED]",
            "detail": f"Repeated execution loop detected on {recent_actions[0]}. Recovering strategy."
        })
        return {
            "next_action": "evaluator_agent",
            "loop_detected": True,
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> evaluator_agent (loop_recovery)"],
            "trace_events": new_trace_events
        }

    # 4. Failure Recovery & Fallback Handling
    if ("Tavily" in failed_tools or test_mode == "tool_failure") and "ResearchAgent" not in history:
        new_trace_events.append({"event": "[TOOL_FAILURE]", "detail": "Tavily Web Search API unavailable."})
        new_trace_events.append({"event": "[FALLBACK]", "detail": "Fallback: Redirecting to Research Agent for academic paper evidence."})
        return {
            "next_action": "research_agent",
            "failed_tools": ["Tavily"],
            "fallback_attempts": ["ResearchAgentFallback"],
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> research_agent (fallback)"],
            "trace_events": new_trace_events
        }

    # 5. Parallel Execution Strategy for collaborative queries
    obj_lower = objective.lower()
    is_collaborative = not ("pure research" in obj_lower or "pure market" in obj_lower)
    
    if is_collaborative and "parallel_execution" not in [t.get("event") for t in state.get("trace_events", [])] and "ResearchAgent" not in history and "MarketIntelligenceAgent" not in history:
        new_trace_events.append({
            "event": "[PARALLEL_EXECUTION]",
            "detail": "Dispatching Research Agent & Market Intelligence Agent concurrently."
        })
        return {
            "next_action": "parallel_research_market",
            "active_agents": ["ResearchAgent", "MarketIntelligenceAgent"],
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> parallel_research_market"],
            "trace_events": new_trace_events
        }

    # 6. Sequential Routing
    if "ResearchAgent" not in history and "research" in obj_lower:
        return {
            "next_action": "research_agent",
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> research_agent"],
            "trace_events": new_trace_events
        }

    if "MarketIntelligenceAgent" not in history and "market" in obj_lower and "Tavily" not in failed_tools:
        return {
            "next_action": "market_intelligence_agent",
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> market_intelligence_agent"],
            "trace_events": new_trace_events
        }

    # 7. Self-Evaluation Node before Synthesis
    if "EvaluatorAgent" not in history:
        return {
            "next_action": "evaluator_agent",
            "iteration_count": iteration_count,
            "actions_taken": ["supervisor -> evaluator_agent"],
            "trace_events": new_trace_events
        }

    # 8. Final Strategic Synthesis Node
    new_trace_events.append({"event": "[DECISION]", "detail": "Evidence sufficient. Directing Strategic Synthesis Agent."})
    return {
        "next_action": "strategic_synthesis_agent",
        "iteration_count": iteration_count,
        "actions_taken": ["supervisor -> strategic_synthesis_agent"],
        "trace_events": new_trace_events
    }
