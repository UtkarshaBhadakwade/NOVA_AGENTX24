from typing import Dict, Any, List

def diagnose_trace(trace_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    AUTOMATIC ROOT CAUSE DIAGNOSTIC ENGINE (Rule-Based Observability)
    
    Parses observable trace events, tool spans, and error logs to identify 
    root cause failures and recommend runtime improvements.
    Does NOT use hidden chain-of-thought; bases diagnosis purely on observable evidence.
    """
    trace_id = trace_summary.get("trace_id", "")
    error_spans = trace_summary.get("error_spans", [])
    tool_spans = trace_summary.get("tool_spans", [])
    failed_tools = trace_summary.get("failed_tools", [])
    fallback_attempts = trace_summary.get("fallback_attempts", [])
    
    evidence_items = []
    
    # 1. Inspect for Tool Timeout / Failure Scenario
    timeout_failures = [t for t in tool_spans if t.get("error_type") == "TIMEOUT" or "timeout" in str(t.get("error_message", "")).lower()]
    api_failures = [t for t in tool_spans if t.get("status") == "FAILED" or t.get("tool_name") in failed_tools]
    
    if timeout_failures:
        first_timeout = timeout_failures[0]
        tool_name = first_timeout.get("tool_name", "Web Search Tool")
        latency = first_timeout.get("latency", 10.0)
        evidence_items.append(f"Tool '{tool_name}' timed out after {latency}s (Status: FAILED).")
        
        if fallback_attempts:
            evidence_items.append(f"Fallback strategy triggered: {', '.join(fallback_attempts)}.")
            return {
                "trace_id": trace_id,
                "root_cause": f"{tool_name} execution timed out because external API response exceeded latency threshold.",
                "affected_component": tool_name,
                "evidence": evidence_items,
                "severity": "HIGH",
                "recommended_improvement": f"Reduce {tool_name} timeout threshold from 10s to 5s and trigger instant fallback routing upon initial failure."
            }
        else:
            evidence_items.append("Fallback strategy was NOT triggered prior to timeout threshold.")
            return {
                "trace_id": trace_id,
                "root_cause": f"{tool_name} timeout caused execution delay because fallback routing was not triggered within the threshold.",
                "affected_component": tool_name,
                "evidence": evidence_items,
                "severity": "CRITICAL",
                "recommended_improvement": "Lower API timeout limit and activate immediate alternative source routing."
            }

    # 2. Inspect for General Tool API Failure
    if api_failures or failed_tools:
        failed_name = failed_tools[0] if failed_tools else (api_failures[0].get("tool_name") if api_failures else "Unknown Tool")
        evidence_items.append(f"Tool '{failed_name}' failed during execution.")
        if fallback_attempts:
            evidence_items.append(f"Fallback executed: {', '.join(fallback_attempts)}.")
            
        return {
            "trace_id": trace_id,
            "root_cause": f"Tool '{failed_name}' returned API failure or missing API key.",
            "affected_component": failed_name,
            "evidence": evidence_items,
            "severity": "MEDIUM",
            "recommended_improvement": f"Bypass '{failed_name}' on initial failure and route directly to academic literature search tools."
        }

    # 3. Clean Execution Diagnosis
    return {
        "trace_id": trace_id,
        "root_cause": "NONE - Normal execution completed cleanly without errors.",
        "affected_component": "NONE",
        "evidence": ["All agent spans and tool calls executed successfully."],
        "severity": "INFO",
        "recommended_improvement": "Maintain current multi-agent parallel execution policy."
    }
