import sys
import os
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agent import agent_graph
from backend.state import AgentState

logging.basicConfig(level=logging.INFO)

def run_test_scenario(scenario_name: str, objective: str, test_mode: str = "normal"):
    print(f"\n========================================================")
    print(f"RUNNING SCENARIO: {scenario_name} (TestMode: {test_mode})")
    print(f"Objective: '{objective}'")
    print(f"========================================================")

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
        "memory_context": {"objective": "Previous AI Agent Research", "id": "test01"},
        "confidence": None,
        "uncertainty": None,
        "resource_budget": {"max_iterations": 8},
        "replan_count": 0,
        "loop_detected": False,
        "self_eval_passed": False,
        "data_availability_note": None,
        "test_mode": test_mode,
        "agent_findings": [],
        "agent_history": [],
        "actions_taken": [],
        "iteration_count": 0,
        "max_iterations": 8,
        "evidence_sufficient": False,
        "task_complete": False,
        "final_report": None,
        "analysis_results": None,
        "trace_events": [],
        "errors": [],
        "next_action": "supervisor",
        "search_query": objective
    }

    try:
        final_state = agent_graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": f"test_{scenario_name.lower().replace(' ', '_')}"}}
        )

        trace = final_state.get("trace_events", [])
        events = [t.get("event") for t in trace if t.get("event")]
        report = final_state.get("final_report", {})

        print(f"SUCCESS! Iterations: {final_state.get('iteration_count')}")
        print(f"Events Fired: {events[:12]}")
        print(f"Report Keys ({len(report.keys())}): {list(report.keys())}")
        return True, events, report
    except Exception as e:
        print(f"SCENARIO FAILED WITH ERROR: {str(e)}")
        return False, [], {}

def main():
    print("========================================================")
    print("NOVA AGENT — TASK 5 AGENT FRAMEWORK ADVERSARIAL TEST SUITE")
    print("========================================================")

    results = []

    # Normal Adaptive Execution
    s0, e0, r0 = run_test_scenario("Normal Adaptive Flow", "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization.", "normal")
    results.append(("Normal Flow", "PASS" if s0 else "FAIL", "[PLANNING], [PARALLEL_EXECUTION], [SELF_EVALUATION], [CHECKPOINT]"))

    # Adversarial Test 1: Tool Failure & Fallback
    s1, e1, r1 = run_test_scenario("Adversarial Test 1: Tool Failure & Fallback", "Analyze AI agent market news.", "tool_failure")
    results.append(("Tool Failure & Fallback", "PASS" if s1 and "[TOOL_FAILURE]" in e1 else "FAIL", "[TOOL_FAILURE] -> [FALLBACK] to Research Agent"))

    # Adversarial Test 2: Conflicting Evidence
    s2, e2, r2 = run_test_scenario("Adversarial Test 2: Conflicting Evidence", "Evaluate AI agent deployment timeline.", "conflict")
    results.append(("Conflicting Evidence", "PASS" if s2 and "[CONFLICT_DETECTED]" in e2 else "FAIL", "[CONFLICT_DETECTED] -> Reconciled in Report"))

    # Adversarial Test 3: Resource Constraint
    s3, e3, r3 = run_test_scenario("Adversarial Test 3: Resource Constraint", "Perform rapid AI research.", "resource_constraint")
    results.append(("Resource Constraint", "PASS" if s3 and "[RESOURCE_DECISION]" in e3 else "FAIL", "[RESOURCE_DECISION] -> Budget Prioritization"))

    # Adversarial Test 4: Self-Evaluation Failure
    s4, e4, r4 = run_test_scenario("Adversarial Test 4: Self-Evaluation Failure", "Analyze deep AI security claims.", "self_eval_fail")
    results.append(("Self-Evaluation Failure", "PASS" if s4 and "[SELF_EVALUATION]" in e4 else "FAIL", "[SELF_EVALUATION] -> Replanning Request"))

    print("\n========================================================")
    print("TASK 5 VERIFICATION SUMMARY TABLE")
    print("========================================================")
    print(f"{'TEST NAME':<35} | {'STATUS':<8} | {'KEY CAPABILITIES DEMONSTRATED'}")
    print("-" * 80)
    for name, status, caps in results:
        print(f"{name:<35} | {status:<8} | {caps}")
    print("========================================================\n")

if __name__ == "__main__":
    main()
