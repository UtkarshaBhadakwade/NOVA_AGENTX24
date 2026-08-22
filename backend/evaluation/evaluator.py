import os
import sys
import time
import uuid
import logging
from typing import Dict, Any, List

# Ensure parent directory is in path so we import the existing production NOVA agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.agent import agent_graph, MAX_ITERATIONS
from backend.state import AgentState
from backend.evaluation.baseline import run_baseline_llm
from backend.evaluation.metrics import compute_single_run_metrics, compute_repeated_runs_metrics
from backend.evaluation.human_evaluation import generate_human_eval_template

logger = logging.getLogger("nova_agent.evaluator")

def execute_nova_agent(objective: str, test_mode: str = "normal") -> tuple[Dict[str, Any], float]:
    """
    Calls the EXISTING production NOVA Agent without modifying any agent code.
    Passes objective and test_mode, measures latency, and returns output dict + latency.
    """
    thread_id = f"eval_{uuid.uuid4().hex[:8]}"
    
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
        "failed_tools": [],
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
        "test_mode": test_mode,
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

    start_time = time.time()
    try:
        final_state = agent_graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}}
        )
        latency = time.time() - start_time
        
        tools_called = [
            action for action in final_state.get("actions_taken", [])
            if not action.startswith("supervisor ->")
        ]

        output = {
            "objective": final_state.get("objective"),
            "status": "completed" if final_state.get("task_complete") else "incomplete",
            "iterations": final_state.get("iteration_count", 0),
            "tools_called": tools_called,
            "trace_events": final_state.get("trace_events", []),
            "final_report": final_state.get("final_report"),
            "errors": final_state.get("errors", [])
        }
        return output, latency
    except Exception as e:
        latency = time.time() - start_time
        logger.error(f"Evaluation agent run failed: {str(e)}")
        return {
            "objective": objective,
            "status": "error",
            "iterations": 0,
            "tools_called": [],
            "trace_events": [],
            "final_report": None,
            "errors": [str(e)]
        }, latency

def evaluate_test_case(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a single test case scenario.
    Runs 1 or repeated runs, measures metrics, baseline comparison, and generates human eval template.
    """
    test_id = test_case["id"]
    scenario = test_case["scenario"]
    objective = test_case["objective"]
    test_mode = test_case["test_mode"]
    repeat_count = test_case.get("repeat_count", 1)

    print(f"  [RUNNING {test_id}] Scenario: {scenario} | Mode: {test_mode} | Repeats: {repeat_count}")

    runs_data = []
    for run_idx in range(repeat_count):
        nova_output, latency = execute_nova_agent(objective, test_mode=test_mode)
        metrics = compute_single_run_metrics(nova_output, latency)
        runs_data.append({
            "run_index": run_idx + 1,
            "nova_output": nova_output,
            "metrics": metrics
        })

    # Statistical summary across runs
    single_metrics = runs_data[0]["metrics"]
    repeated_summary = compute_repeated_runs_metrics([r["metrics"] for r in runs_data]) if repeat_count > 1 else None

    # Baseline comparison (if requested or applicable)
    baseline_result = None
    if scenario == "BASELINE_COMPARISON" or repeat_count == 1:
        baseline_result = run_baseline_llm(objective)

    # Human evaluation template
    human_eval_template = generate_human_eval_template(
        test_id=test_id,
        scenario=scenario,
        objective=objective,
        report=runs_data[0]["nova_output"].get("final_report") or {}
    )

    return {
        "test_id": test_id,
        "scenario": scenario,
        "objective": objective,
        "test_mode": test_mode,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "primary_run_metrics": single_metrics,
        "repeated_runs_summary": repeated_summary,
        "baseline_comparison": baseline_result,
        "human_evaluation_template": human_eval_template,
        "raw_runs_count": len(runs_data)
    }
