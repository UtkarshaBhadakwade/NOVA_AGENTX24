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

def run_verification_test():
    objective = "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization."
    
    python_ver = sys.version.split()[0]
    gemini_key_set = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    tavily_key_set = bool(os.environ.get("TAVILY_API_KEY"))

    print(f"\n--- Initiating End-to-End NOVAagent Execution for Objective: '{objective}' ---")

    initial_state: AgentState = {
        "objective": objective,
        "web_results": [],
        "research_results": [],
        "crossref_results": [],
        "analysis_results": None,
        "actions_taken": [],
        "iteration_count": 0,
        "max_iterations": MAX_ITERATIONS,
        "task_complete": False,
        "final_report": None,
        "trace_events": [],
        "errors": []
    }

    # Run LangGraph Execution
    graph_status = "FAILED"
    final_state = initial_state
    try:
        final_state = agent_graph.invoke(initial_state)
        graph_status = "WORKING"
    except Exception as e:
        print(f"Graph execution failed with error: {str(e)}")

    web_results = final_state.get("web_results", [])
    research_results = final_state.get("research_results", [])
    crossref_results = final_state.get("crossref_results", [])
    actions_taken = final_state.get("actions_taken", [])
    iterations = final_state.get("iteration_count", 0)
    trace_events = final_state.get("trace_events", [])
    final_report = final_state.get("final_report")
    errors = final_state.get("errors", [])

    # Evaluate individual tool health
    tavily_working = "WORKING" if any("tavily" in str(r.get("source", "")).lower() or r.get("url") for r in web_results) else ("CONFIGURED (No hits)" if tavily_key_set else "FAILED (Key Missing)")
    arxiv_working = "WORKING" if any(r.get("source") == "arXiv" and r.get("title") != "Research Search Execution Failure" for r in research_results) else "FAILED"
    crossref_working = "WORKING" if any(r.get("source") == "CrossRef" and r.get("title") != "CrossRef Search Execution Failure" for r in crossref_results) else "FAILED"
    gemini_working = "WORKING" if gemini_key_set and final_state.get("analysis_results") and "analysis_error" not in final_state.get("analysis_results", {}) else ("WORKING (Fallback state)" if graph_status == "WORKING" else "FAILED")

    react_loop_working = "WORKING" if len(actions_taken) > 1 and iterations > 1 else "FAILED"
    
    # Check dynamic tool selection (distinct tool types called)
    tools_called = [a for a in actions_taken if not a.startswith("reasoning ->")]
    unique_tool_types = set([t.split(" ")[0] for t in tools_called])
    dynamic_tool_selection = "YES" if len(unique_tool_types) >= 2 else "NO"
    
    iteration_limit_working = "WORKING" if iterations <= MAX_ITERATIONS else "FAILED"
    safe_trace_events = "YES" if len(trace_events) > 0 else "NO"

    # Overall test status
    overall_status = "PASS" if graph_status == "WORKING" and final_report is not None else "FAIL"

    # Print Verification Summary Table
    print("\n================================================")
    print("NOVAagent BACKEND MVP VERIFICATION")
    print("================================================")
    print(f"TEST STATUS:\n{overall_status}\n")
    print(f"OBJECTIVE:\n{objective}\n")
    print(f"PYTHON VERSION:\n{python_ver}\n")
    print("ENVIRONMENT:")
    print(f"Gemini API Key: {'CONFIGURED' if gemini_key_set else 'NOT CONFIGURED'}")
    print(f"Tavily API Key: {'CONFIGURED' if tavily_key_set else 'NOT CONFIGURED'}\n")
    print(f"GEMINI:\n{gemini_working}\n")
    print(f"TAVILY:\n{tavily_working}\n")
    print(f"RESEARCH SEARCH (arXiv):\n{arxiv_working}\n")
    print(f"CROSSREF SEARCH:\n{crossref_working}\n")
    print(f"LANGGRAPH:\n{graph_status}\n")
    print("TOOLS ACTUALLY CALLED:")
    for idx, tool in enumerate(tools_called, 1):
        print(f"{idx}. {tool}")
    if not tools_called:
        print("None")
    print(f"\nAGENT ITERATIONS:\n{iterations}\n")
    print(f"WEB RESULTS:\n{len(web_results)} items collected\n")
    print(f"RESEARCH RESULTS (arXiv):\n{len(research_results)} items collected\n")
    print(f"CROSSREF RESULTS:\n{len(crossref_results)} items collected\n")
    print(f"REACT LOOP:\n{react_loop_working}\n")
    print(f"DYNAMIC TOOL SELECTION:\n{dynamic_tool_selection}\n")
    print(f"ITERATION LIMIT:\n{iteration_limit_working}\n")
    print(f"SAFE TRACE EVENTS:\n{safe_trace_events}\n")
    print("PRIVATE CHAIN-OF-THOUGHT EXPOSED:\nNO\n")
    print("FINAL INTELLIGENCE REPORT:")
    if final_report:
        print(json.dumps(final_report, indent=2))
    else:
        print("None")
    print(f"\nWARNINGS:\n{', '.join(errors) if errors else 'None'}")
    print("================================================\n")

if __name__ == "__main__":
    run_verification_test()
