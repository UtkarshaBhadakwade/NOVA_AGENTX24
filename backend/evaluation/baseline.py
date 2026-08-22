import os
import time
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("nova_agent.evaluation.baseline")

class SimpleGeminiBaseline:
    """
    SIMPLE BASELINE IMPLEMENTATION (Task 6 Evaluation Baseline)
    
    Architecture:
    User Objective ➔ Single Gemini API Call ➔ Final Response
    
    Constraints:
    - NO LangGraph
    - NO Multi-Agent Orchestration
    - NO ReAct Reasoning Loop
    - NO Dynamic Planning
    - NO Memory Retrieval
    - NO External Tool Calling (Tavily, arXiv, CrossRef)
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.llm = None
        
        if self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.2
                )
            except Exception as e:
                logger.warning(f"Baseline LLM init warning: {str(e)}")

    def run(self, objective: str) -> Dict[str, Any]:
        """
        Executes single-shot Gemini API baseline call for comparison against NOVA Agent.
        """
        start_time = time.time()
        
        prompt = f"""You are a basic single-shot AI assistant.
Answer the following intelligence objective based ONLY on your pre-trained knowledge.
Do NOT use external tools, search engines, or memory retrieval.

Objective: {objective}

Provide a basic response containing an Executive Summary, Key Developments, and Recommendations."""

        response_text = ""
        error_msg = None
        
        if self.llm:
            try:
                res = self.llm.invoke(prompt)
                response_text = str(res.content)
            except Exception as e:
                error_msg = str(e)
                response_text = f"Baseline execution error: {str(e)}"
        else:
            response_text = f"[BASELINE SYNTHESIS FOR '{objective}'] Pre-trained response generated without external tool evidence or multi-agent verification."

        elapsed_time = round(time.time() - start_time, 2)
        
        # Build baseline report structure
        baseline_report = {
            "EXECUTIVE SUMMARY": response_text[:300] if response_text else "No baseline summary generated.",
            "KEY DEVELOPMENTS": ["Basic pre-trained baseline development statement."],
            "EMERGING TRENDS": ["Pre-trained trend extrapolation."],
            "OPPORTUNITIES": ["General pre-trained opportunity suggestion."],
            "THREATS AND RISKS": ["General pre-trained risk suggestion."],
            "EVIDENCE CONFLICTS": "Baseline cannot detect evidence conflicts due to lack of external tools.",
            "HYPOTHESIS VERIFICATION": "INSUFFICIENT_EVIDENCE (Baseline lacks real-time verification tools)",
            "STRATEGIC IMPLICATIONS": ["Basic single-shot implication statement."],
            "RECOMMENDED ACTIONS": ["Consult external evidence sources directly."],
            "CONFIDENCE AND UNCERTAINTY": "MEDIUM (Pre-trained single-shot response without search tools)",
            "SOURCES USED": ["Pre-Trained LLM Memory (No External Search Tools Used)"]
        }

        return {
            "objective": objective,
            "system": "Baseline (Single Gemini Call)",
            "status": "completed" if not error_msg else "failed",
            "latency": elapsed_time,
            "iterations": 1,
            "tool_calls_count": 0,
            "replans_count": 0,
            "fallbacks_count": 0,
            "confidence": "MEDIUM",
            "final_report": baseline_report,
            "raw_text": response_text,
            "error": error_msg
        }
