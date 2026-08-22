import statistics
from typing import Dict, Any, List

def compute_single_run_metrics(nova_output: Dict[str, Any], latency: float) -> Dict[str, Any]:
    """
    Computes automated evaluation metrics directly from actual NOVA Agent output dictionary.
    Does NOT fabricate scores; marks subjective items as REQUIRES_HUMAN_REVIEW.
    """
    report = nova_output.get("final_report") or {}
    trace = nova_output.get("trace_events", [])
    events = [t.get("event") for t in trace if isinstance(t, dict) and t.get("event")]
    
    # 1. Task Completion
    task_complete = nova_output.get("status") == "completed" and bool(report)
    
    # 2. Resource & Execution Efficiency
    iterations = nova_output.get("iterations", 0)
    tools_called = nova_output.get("tools_called", [])
    tool_calls_count = len(tools_called)
    
    # 3. Groundedness & Source Citations
    sources = report.get("SOURCES USED") or []
    developments = report.get("KEY DEVELOPMENTS") or []
    groundedness_ratio = round(len(sources) / max(len(developments), 1), 2)
    
    # 4. Failure Recovery Indicator
    tool_failure_detected = "[TOOL_FAILURE]" in events
    fallback_triggered = "[FALLBACK]" in events
    failure_recovery_success = (tool_failure_detected or fallback_triggered) and task_complete
    
    # 5. Uncertainty Handling & Qualification
    conf_section = report.get("CONFIDENCE AND UNCERTAINTY") or ""
    has_confidence_rating = any(level in conf_section for level in ["HIGH", "MEDIUM", "LOW"])
    
    # 6. Refusal / Qualification for Ambiguous or Unanswerable Queries
    refusal_or_qualification = "REQUIRES_HUMAN_REVIEW"
    if "HIGH" not in conf_section or "uncertain" in conf_section.lower() or "warning" in conf_section.lower():
        refusal_or_qualification = "QUALIFIED_WITH_UNCERTAINTY_WARNING"

    return {
        "task_completion": task_complete,
        "latency_seconds": round(latency, 2),
        "iterations": iterations,
        "tool_calls_count": tool_calls_count,
        "tools_called_list": tools_called,
        "sources_count": len(sources),
        "groundedness_citation_ratio": groundedness_ratio,
        "tool_failure_detected": tool_failure_detected,
        "fallback_triggered": fallback_triggered,
        "failure_recovery_success": failure_recovery_success,
        "uncertainty_handling_present": has_confidence_rating,
        "confidence_level": conf_section.split()[0] if conf_section else "UNKNOWN",
        "unsupported_claim_check": "REQUIRES_HUMAN_REVIEW",
        "evidence_quality_score": "REQUIRES_HUMAN_REVIEW",
        "refusal_or_qualification_status": refusal_or_qualification
    }

def compute_repeated_runs_metrics(runs_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes statistical metrics across repeated runs (5 runs).
    """
    if not runs_metrics:
        return {}
        
    latencies = [r["latency_seconds"] for r in runs_metrics]
    iterations_list = [r["iterations"] for r in runs_metrics]
    tool_calls_list = [r["tool_calls_count"] for r in runs_metrics]
    completions = [1 if r["task_completion"] else 0 for r in runs_metrics]
    confidences = [r.get("confidence_level") for r in runs_metrics]

    return {
        "total_runs": len(runs_metrics),
        "completion_rate": f"{round(sum(completions) / len(completions) * 100, 1)}%",
        "avg_latency_seconds": round(statistics.mean(latencies), 2),
        "min_latency_seconds": round(min(latencies), 2),
        "max_latency_seconds": round(max(latencies), 2),
        "std_dev_latency": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0.0,
        "avg_iterations": round(statistics.mean(iterations_list), 2),
        "avg_tool_calls": round(statistics.mean(tool_calls_list), 2),
        "confidence_consistency": len(set(confidences)) == 1,
        "confidence_distribution": {c: confidences.count(c) for c in set(confidences)}
    }
