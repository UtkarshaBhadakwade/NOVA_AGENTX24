import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from backend.agent import agent_graph

async def main():
    print("=" * 60)
    print("Competitive Intelligence Agent - Local Loop Test")
    print("=" * 60)
    
    # Check keys
    gemini_key = os.environ.get("GEMINI_API_KEY")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    
    print(f"GEMINI_API_KEY: {'Configured' if gemini_key else 'Missing'}")
    print(f"TAVILY_API_KEY: {'Configured' if tavily_key else 'Missing'}")
    print(f"GEMINI_MODEL: {os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')}")
    print("-" * 60)
    
    if not gemini_key or not tavily_key:
        print("[WARNING] API Keys are missing! Running the agent will result in execution failure.")
        print("Please create a '.env' file in the workspace root with your API keys:")
        print("GEMINI_API_KEY=your_key")
        print("TAVILY_API_KEY=your_key")
        print("Terminating test script.")
        return
        
    # Read custom objective from command-line args if provided, else prompt for it
    if len(sys.argv) > 1:
        objective = " ".join(sys.argv[1:])
    else:
        print("\nPlease enter your competitive intelligence objective/prompt:")
        objective = input("> ").strip()
        if not objective:
            objective = "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization."
            print(f"No objective entered. Defaulting to: '{objective}'")
            
    print("\n[AGENT START]")
    print(f"Objective: {objective}")
    print("\nLaunching agent...")
    
    initial_state = {
        "objective": objective,
        "collected_evidence": [],
        "analysis_result": None,
        "steps": [],
        "iterations": 0,
        "max_iterations": 8,
        "next_action": None,
        "next_action_input": None,
        "final_report": None,
        "error": None
    }
    
    try:
        final_state = await agent_graph.ainvoke(initial_state)
        
        # Chronologically print out the trace events in the user's requested format
        for step in final_state.get("steps", []):
            step_type = step.get("type")
            content = step.get("content")
            print(f"\n[{step_type}]")
            if step_type == "ACTION":
                print(f"Tool: {content}")
            else:
                print(content)
            
        print("\n[FINAL INTELLIGENCE REPORT]")
        report = final_state.get("final_report")
        if report:
            print(report)
        else:
            print("No final report generated.")
            
        if final_state.get("error"):
            print(f"\n[ERROR] {final_state.get('error')}")
            
    except Exception as e:
        print(f"\n[FATAL ERROR] Agent invocation failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
