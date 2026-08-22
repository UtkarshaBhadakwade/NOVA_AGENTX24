import os
import sys
import json
import csv
import time
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.agent import agent_graph, MAX_ITERATIONS
from backend.state import AgentState
from backend.observability.tracer import NOVAObservabilityTracer
from backend.observability.metrics import compute_observability_metrics
from backend.observability.diagnostics import diagnose_trace
from backend.observability.failure_tests import run_controlled_failure_experiment
from backend.observability.improvement import run_improved_execution_experiment, generate_before_vs_after_comparison

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_agent.run_observability")

def run_normal_trace_test(objective: str = "Find the latest developments in AI agents and determine opportunities or threats.") -> Dict[str, Any]:
    """Runs Test 1: Normal Trace capture."""
    tracer = NOVAObservabilityTracer(investigation_id="test_normal_01")
    
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
        "test_mode": "normal",
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

    final_state = agent_graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": "normal_trace_thread"}, "callbacks": [tracer]}
    )
    return tracer.export_trace_summary(final_state)

def main():
    print("\n========================================================")
    print("NOVA AGENT — TASK 7 ADVANCED TRACING & OBSERVABILITY SUITE")
    print("========================================================\n")

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "reports"))
    os.makedirs(reports_dir, exist_ok=True)

    # ----------------------------------------------------
    # TEST 1 — NORMAL TRACE
    # ----------------------------------------------------
    print("[TEST 1/3] Running Normal Investigation Trace...")
    normal_summary = run_normal_trace_test()
    normal_metrics = compute_observability_metrics(normal_summary)
    print(f"  -> Trace ID: {normal_summary['trace_id']}")
    print(f"  -> Total Latency: {normal_summary['total_latency_seconds']}s | Iterations: {normal_summary['iteration_count']} | Tools: {normal_summary['tool_call_count']}")
    print(f"  -> Token Usage Status: {normal_summary['token_usage']}\n")

    # ----------------------------------------------------
    # TEST 2 — CONTROLLED FAILURE & DIAGNOSIS
    # ----------------------------------------------------
    print("[TEST 2/3] Running Controlled Failure Experiment (Simulated Tavily Timeout)...")
    before_summary, failure_tracer = run_controlled_failure_experiment()
    diagnosis = diagnose_trace(before_summary)
    print(f"  -> Failure Trace ID: {before_summary['trace_id']}")
    print(f"  -> Diagnostic Root Cause: {diagnosis['root_cause']}")
    print(f"  -> Affected Component: {diagnosis['affected_component']}")
    print(f"  -> Evidence: {diagnosis['evidence']}")
    print(f"  -> Recommended Improvement: {diagnosis['recommended_improvement']}\n")

    # ----------------------------------------------------
    # TEST 3 — IMPROVEMENT & BEFORE vs AFTER
    # ----------------------------------------------------
    print("[TEST 3/3] Applying Controlled Improvement Strategy & Measuring Before vs After...")
    after_summary, improved_tracer = run_improved_execution_experiment()
    comparison = generate_before_vs_after_comparison(before_summary, after_summary)

    print("\n========================================================")
    print("TASK 7 BEFORE vs AFTER MEASUREMENT TABLE")
    print("========================================================")
    print(f"{'METRIC':<25} | {'BEFORE (Baseline Failure)':<25} | {'AFTER (Improved Strategy)':<25}")
    print("-" * 80)
    for metric_name, m_data in comparison["metric_comparison"].items():
        print(f"{metric_name:<25} | {str(m_data['before']):<25} | {str(m_data['after']):<25}")
    print("========================================================\n")

    # Save Trace Reports
    full_report = {
        "normal_trace_test": normal_summary,
        "controlled_failure_test": {
            "trace_summary": before_summary,
            "diagnosis": diagnosis
        },
        "improved_trace_test": {
            "trace_summary": after_summary,
            "before_vs_after_comparison": comparison
        }
    }

    json_path = os.path.join(reports_dir, "observability_full_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    # Save CSV Summary
    csv_path = os.path.join(reports_dir, "before_vs_after_metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Before (Controlled Failure)", "After (Improved Strategy)", "Improvement Outcome"])
        for metric_name, m_data in comparison["metric_comparison"].items():
            writer.writerow([metric_name, m_data["before"], m_data["after"], m_data["improvement"]])

    print(f"Observability Reports saved to: {reports_dir}\n")

if __name__ == "__main__":
    main()
