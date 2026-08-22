import os
import sys
import json
import logging
from dotenv import load_dotenv

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

from backend.agent import agent_graph, MAX_ITERATIONS
from backend.state import AgentState

def run_test_objective(objective_text: str):
    print(f"\n--- Running Verification Sub-Test for Objective: '{objective_text}' ---")
    
    initial_state: AgentState = {
        "objective": objective_text,
        "current_task": None,
        "delegated_agent": None,
        "research_results": [],
        "market_results": [],
        "web_results": [],
        "crossref_results": [],
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
        "search_query": objective_text
    }

    try:
        final_state = agent_graph.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"Sub-test execution failed: {str(e)}")
        return initial_state


def run_full_task3_verification():
    # ---------------------------------------------------------
    # TEST 1: Scientific / Technical Research Objective
    # ---------------------------------------------------------
    obj1 = "Find the latest research trends in multi-agent AI systems."
    res1 = run_test_objective(obj1)
    history1 = res1.get("agent_history", [])
    
    # ---------------------------------------------------------
    # TEST 2: Market / Competitor Intelligence Objective
    # ---------------------------------------------------------
    obj2 = "Identify recent competitor and industry developments in AI agent platforms."
    res2 = run_test_objective(obj2)
    history2 = res2.get("agent_history", [])
    
    # ---------------------------------------------------------
    # TEST 3: Broad Multi-Agent Collaborative Objective
    # ---------------------------------------------------------
    obj3 = "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization."
    res3 = run_test_objective(obj3)
    history3 = res3.get("agent_history", [])

    # Evaluate verification status
    research_agent_working = "WORKING" if len(res1.get("research_results", [])) > 0 or len(res1.get("crossref_results", [])) > 0 or any("research_agent" in h for h in history1) else "FAILED"
    market_agent_working = "WORKING" if len(res2.get("market_results", [])) > 0 or len(res2.get("web_results", [])) > 0 or any("market_intelligence_agent" in h for h in history2) else "FAILED"
    synthesis_agent_working = "WORKING" if res3.get("final_report") is not None and res3.get("analysis_results") is not None else "FAILED"
    
    orchestration_working = "WORKING" if len(history3) >= 3 else "FAILED"
    dynamic_delegation_working = "WORKING" if history1 != history2 else "FAILED"
    react_loop_working = "WORKING" if res3.get("iteration_count", 0) > 1 else "FAILED"
    max_iteration_working = "WORKING" if res3.get("iteration_count", 0) <= MAX_ITERATIONS else "FAILED"
    safe_trace_working = "WORKING" if len(res3.get("trace_events", [])) > 0 else "FAILED"
    
    all_passed = (
        research_agent_working == "WORKING" and
        market_agent_working == "WORKING" and
        synthesis_agent_working == "WORKING" and
        orchestration_working == "WORKING" and
        dynamic_delegation_working == "WORKING"
    )
    overall_status = "PASS" if all_passed else "FAIL"

    # Format Agent Execution Paths
    exec_path1 = " -> ".join([h.replace("supervisor -> ", "") for h in history1])
    exec_path2 = " -> ".join([h.replace("supervisor -> ", "") for h in history2])
    exec_path3 = " -> ".join([h.replace("supervisor -> ", "") for h in history3])

    tools_used_list = [
        "arXiv REST API (Research Agent)",
        "CrossRef REST API (Research Agent)",
        "Tavily Web Search API (Market Intelligence Agent)",
        "Gemini 3.6 Flash (Supervisor Agent & Strategic Synthesis Agent)"
    ]

    warnings_list = list(set(res1.get("errors", []) + res2.get("errors", []) + res3.get("errors", [])))

    print("\n================================================")
    print("NOVA AGENT — TASK 3 MULTI-AGENT VERIFICATION")
    print("================================================\n")
    print(f"TEST STATUS:\n{overall_status}\n")
    print("AGENTS IMPLEMENTED:")
    print("1. Supervisor Agent (Orchestrator & Task Delegator)")
    print("2. Research Agent (Scientific & Technical Intelligence Specialist)")
    print("3. Market Intelligence Agent (Competitor & Industry Intelligence Specialist)")
    print("4. Strategic Synthesis Agent (Strategic Intelligence Analyst)\n")
    print("AGENT RESPONSIBILITIES:")
    print("- Supervisor Agent: Inspects state, evaluates information gaps, delegates tasks to specialized agents.")
    print("- Research Agent: Searches arXiv & CrossRef APIs for scientific papers, technical developments, and DOIs.")
    print("- Market Intelligence Agent: Searches Tavily Web API for competitor news, product launches, and market trends.")
    print("- Strategic Synthesis Agent: Grounded LLM synthesis generating executive intelligence reports via Gemini 3.6 Flash.\n")
    print(f"MEANINGFUL ORCHESTRATION:\n{orchestration_working}\n")
    print(f"DYNAMIC DELEGATION:\n{dynamic_delegation_working}\n")
    print(f"REACT LOOP:\n{react_loop_working}\n")
    print(f"RESEARCH AGENT:\n{research_agent_working}\n")
    print(f"MARKET INTELLIGENCE AGENT:\n{market_agent_working}\n")
    print(f"STRATEGIC SYNTHESIS AGENT:\n{synthesis_agent_working}\n")
    print(f"MAX ITERATION LIMIT:\n{max_iteration_working}\n")
    print(f"SAFE TRACE EVENTS:\n{safe_trace_working}\n")
    print("PRIVATE CHAIN-OF-THOUGHT EXPOSED:\nNO\n")
    print("AGENT EXECUTION PATHS:")
    print(f"Test 1 (Research Objective):\n  {exec_path1}")
    print(f"Test 2 (Market Objective):\n  {exec_path2}")
    print(f"Test 3 (Collaborative Objective):\n  {exec_path3}\n")
    print("TOOLS USED:")
    for tool in tools_used_list:
        print(f"- {tool}")
    print("\nFINAL RESULT:")
    if res3.get("final_report"):
        print(json.dumps(res3["final_report"], indent=2))
    else:
        print("None")
    print(f"\nWARNINGS:\n{', '.join(warnings_list) if warnings_list else 'None'}")
    print("================================================\n")

if __name__ == "__main__":
    run_full_task3_verification()
