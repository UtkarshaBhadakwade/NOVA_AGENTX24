import os
import time
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI

def run_baseline_llm(objective: str) -> Dict[str, Any]:
    """
    BASELINE MODEL (Isolated Single LLM Call)
    
    No LangGraph, no multi-agent network, no ReAct loop, no external search tools, no memory.
    Used purely for comparative evaluation metrics against NOVA Agent.
    """
    start_time = time.time()
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {
            "baseline_type": "Single Gemini Call (No Tools/Graph)",
            "output_text": "Error: GEMINI_API_KEY environment variable is missing.",
            "latency": round(time.time() - start_time, 2),
            "tool_calls": 0,
            "iterations": 1,
            "sources_count": 0
        }
        
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
        response = llm.invoke(f"Provide a brief competitive intelligence summary for: {objective}")
        text = response.content if hasattr(response, "content") else str(response)
        
        return {
            "baseline_type": "Single Gemini Call (No Tools/Graph)",
            "output_text": text,
            "latency": round(time.time() - start_time, 2),
            "tool_calls": 0,
            "iterations": 1,
            "sources_count": 0
        }
    except Exception as e:
        return {
            "baseline_type": "Single Gemini Call (No Tools/Graph)",
            "output_text": f"Baseline Error: {str(e)}",
            "latency": round(time.time() - start_time, 2),
            "tool_calls": 0,
            "iterations": 1,
            "sources_count": 0
        }
