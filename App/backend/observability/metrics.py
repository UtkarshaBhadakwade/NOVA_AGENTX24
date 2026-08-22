from typing import Dict, Any, List

def compute_observability_metrics(trace_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates execution and efficiency metrics from trace data.
    """
    total_latency = trace_summary.get("total_latency_seconds", 0.0)
    tool_spans = trace_summary.get("tool_spans", [])
    error_spans = trace_summary.get("error_spans", [])
    
    tool_latencies = [t["latency"] for t in tool_spans if "latency" in t]
    avg_tool_latency = round(sum(tool_latencies) / len(tool_latencies), 3) if tool_latencies else 0.0
    
    successful_tools = [t for t in tool_spans if t.get("status") == "SUCCESS"]
    failed_tools = [t for t in tool_spans if t.get("status") == "FAILED"]
    
    tool_success_rate = f"{round(len(successful_tools) / max(len(tool_spans), 1) * 100, 1)}%"
    
    return {
        "trace_id": trace_summary.get("trace_id"),
        "total_latency_seconds": total_latency,
        "iteration_count": trace_summary.get("iteration_count", 0),
        "total_tool_calls": len(tool_spans),
        "avg_tool_latency_seconds": avg_tool_latency,
        "tool_success_rate": tool_success_rate,
        "total_errors_recorded": len(error_spans),
        "recovery_attempts_count": len(trace_summary.get("fallback_attempts", [])),
        "token_usage_status": trace_summary.get("token_usage", {})
    }
