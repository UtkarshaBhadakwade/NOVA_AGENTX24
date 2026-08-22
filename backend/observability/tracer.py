import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("nova_agent.observability")

class NOVAObservabilityTracer(BaseCallbackHandler):
    """
    End-to-End Tracing Handler for NOVA Agent.
    
    Captures lifecycle metrics:
    - Trace ID & Investigation ID
    - Agent execution timestamps & latency
    - High-level decision traces (sanitized, no chain-of-thought)
    - Tool execution start/end, latency, result count, and errors
    - Structured error categorization
    - Token usage metrics (Input/Output/Total or NOT_AVAILABLE)
    """
    
    def __init__(self, investigation_id: Optional[str] = None):
        super().__init__()
        self.trace_id = f"trc_{uuid.uuid4().hex[:12]}"
        self.investigation_id = investigation_id or f"inv_{uuid.uuid4().hex[:8]}"
        self.start_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        
        self.agent_spans: List[Dict[str, Any]] = []
        self.tool_spans: List[Dict[str, Any]] = []
        self.decision_spans: List[Dict[str, Any]] = []
        self.error_spans: List[Dict[str, Any]] = []
        self.token_usage: Dict[str, Any] = {
            "input_tokens": "NOT_AVAILABLE",
            "output_tokens": "NOT_AVAILABLE",
            "total_tokens": "NOT_AVAILABLE"
        }
        
        self.active_tools: Dict[str, float] = {}

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Traces LLM invocation start safely without storing secrets."""
        model_name = serialized.get("name") or "Gemini 3.6 Flash"
        self.agent_spans.append({
            "component": "LLM",
            "model_name": model_name,
            "start_time": time.time(),
            "status": "STARTED"
        })

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Captures LLM completion and extracts token usage if provided by model response."""
        end_time = time.time()
        if self.agent_spans:
            last_span = self.agent_spans[-1]
            last_span["end_time"] = end_time
            last_span["latency"] = round(end_time - last_span["start_time"], 3)
            last_span["status"] = "COMPLETED"
            
        # Extract actual token usage if available in LLM generation info
        if hasattr(response, "llm_output") and response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.token_usage = {
                "input_tokens": usage.get("prompt_tokens", "NOT_AVAILABLE"),
                "output_tokens": usage.get("completion_tokens", "NOT_AVAILABLE"),
                "total_tokens": usage.get("total_tokens", "NOT_AVAILABLE")
            }

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Captures LLM execution errors."""
        end_time = time.time()
        error_msg = str(error)
        err_cat = "API_ERROR" if "API" in error_msg else "AGENT_FAILURE"
        
        self.error_spans.append({
            "trace_id": self.trace_id,
            "component": "LLM",
            "error_category": err_cat,
            "error_message": error_msg,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "recovery_attempted": True
        })
        if self.agent_spans:
            last_span = self.agent_spans[-1]
            last_span["end_time"] = end_time
            last_span["latency"] = round(end_time - last_span["start_time"], 3)
            last_span["status"] = "FAILED"

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Traces tool call initiation safely."""
        tool_name = serialized.get("name") or "Tool"
        call_id = f"{tool_name}_{time.time()}"
        self.active_tools[call_id] = time.time()
        
        self.tool_spans.append({
            "tool_name": tool_name,
            "call_id": call_id,
            "start_time": time.time(),
            "sanitized_query": input_str[:100] if input_str else "",
            "status": "RUNNING"
        })

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Traces tool completion, latency, and result count."""
        end_time = time.time()
        if self.tool_spans:
            last_span = self.tool_spans[-1]
            last_span["end_time"] = end_time
            last_span["latency"] = round(end_time - last_span["start_time"], 3)
            last_span["status"] = "SUCCESS"
            
            # Count structured items if returned
            result_count = 1
            if isinstance(output, str):
                result_count = output.count("Title:") or output.count("http") or 1
            elif isinstance(output, list):
                result_count = len(output)
            last_span["result_count"] = result_count

    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """Traces tool execution failure and records error category."""
        end_time = time.time()
        error_msg = str(error)
        
        err_cat = "TOOL_FAILURE"
        if "timeout" in error_msg.lower():
            err_cat = "TIMEOUT"
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            err_cat = "NETWORK_ERROR"

        if self.tool_spans:
            last_span = self.tool_spans[-1]
            last_span["end_time"] = end_time
            last_span["latency"] = round(end_time - last_span["start_time"], 3)
            last_span["status"] = "FAILED"
            last_span["error_type"] = err_cat
            last_span["error_message"] = error_msg

        self.error_spans.append({
            "trace_id": self.trace_id,
            "component": last_span["tool_name"] if self.tool_spans else "Tool",
            "error_category": err_cat,
            "error_message": error_msg,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "recovery_attempted": True
        })

    def record_decision(self, event_tag: str, detail: str) -> None:
        """Records high-level decision trace without chain-of-thought."""
        self.decision_spans.append({
            "event": event_tag,
            "detail": detail,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    def export_trace_summary(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """Exports end-to-end trace metadata summary."""
        self.end_time = time.time()
        total_latency = round(self.end_time - self.start_time, 3)
        
        # Populate decisions from graph trace_events if any
        graph_events = final_state.get("trace_events", [])
        for ev in graph_events:
            if isinstance(ev, dict) and ev.get("event"):
                self.record_decision(ev["event"], str(ev.get("detail", "")))

        tools_called = final_state.get("actions_taken", [])
        
        return {
            "trace_id": self.trace_id,
            "investigation_id": self.investigation_id,
            "objective": final_state.get("objective", ""),
            "start_timestamp": self.start_timestamp,
            "end_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_latency_seconds": total_latency,
            "iteration_count": final_state.get("iteration_count", 0),
            "tool_call_count": len(tools_called),
            "status": "completed" if final_state.get("task_complete") else "incomplete",
            "token_usage": self.token_usage,
            "agent_spans_count": len(self.agent_spans),
            "tool_spans": self.tool_spans,
            "decision_spans": self.decision_spans,
            "error_spans": self.error_spans,
            "failed_tools": final_state.get("failed_tools", []),
            "fallback_attempts": final_state.get("fallback_attempts", [])
        }
