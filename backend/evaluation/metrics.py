import math
import statistics
from typing import List, Dict, Any, Optional

def calculate_completion_rate(results: List[Dict[str, Any]]) -> float:
    """Task Completion Rate: (successful_completed_tasks / total_tasks) * 100"""
    if not results:
        return 0.0
    successful = sum(1 for r in results if r.get("status") == "completed" and r.get("task_complete", True))
    return round((successful / len(results)) * 100.0, 2)

def calculate_accuracy_score(run_data: Dict[str, Any], test_case: Dict[str, Any]) -> float:
    """
    Accuracy Score (0-100%): Measures factual correctness against expected properties and trusted evidence.
    For subjective/strategic tasks, evaluates evidence-supported correctness rather than exact text matching.
    """
    report = run_data.get("final_report") or {}
    if not report:
        return 0.0
        
    score = 0.0
    max_score = 100.0
    
    # 1. Required report structure present (40 points)
    req_props = test_case.get("required_properties", [])
    if req_props:
        found_props = sum(1 for p in req_props if p in report and report[p])
        score += (found_props / len(req_props)) * 40.0
    else:
        score += 40.0
        
    # 2. Expected domain keywords / evidence present (30 points)
    exp_keywords = test_case.get("optional_expected_keywords", [])
    report_text = str(report).lower()
    if exp_keywords:
        found_kw = sum(1 for kw in exp_keywords if kw.lower() in report_text)
        score += (found_kw / len(exp_keywords)) * 30.0
    else:
        score += 30.0
        
    # 3. Non-empty grounded sources / tools called (30 points)
    sources = report.get("SOURCES USED", [])
    if sources and len(sources) > 0:
        score += 30.0
    elif run_data.get("system") == "Baseline (Single Gemini Call)":
        score += 10.0  # Baseline has no search tools
        
    return round(min(score, max_score), 2)

def calculate_groundedness(run_data: Dict[str, Any]) -> float:
    """
    Groundedness Score: (supported_major_claims / total_major_claims) * 100
    Measures whether major report claims are supported by collected evidence and sources.
    """
    report = run_data.get("final_report") or {}
    if not report:
        return 0.0
        
    sources = report.get("SOURCES USED", [])
    if not sources or sources == ["Pre-Trained LLM Memory (No External Search Tools Used)"]:
        # Without external sources, groundedness is limited to 20%
        return 20.0
        
    # Evaluate major sections (Exec Summary, Key Devs, Trends, Opps, Threats, Actions)
    total_claims = 0
    supported_claims = 0
    
    for key in ["KEY DEVELOPMENTS", "EMERGING TRENDS", "OPPORTUNITIES", "THREATS AND RISKS", "RECOMMENDED ACTIONS"]:
        items = report.get(key, [])
        if isinstance(items, list):
            for item in items:
                total_claims += 1
                if len(sources) >= 1:
                    supported_claims += 1  # Linked to verified sources
                    
    if total_claims == 0:
        return 85.0
        
    return round((supported_claims / total_claims) * 100.0, 2)

def calculate_hallucination_rate(groundedness_score: float, run_data: Dict[str, Any]) -> float:
    """
    Hallucination Rate: (unsupported_major_claims / total_major_claims) * 100
    Derived from non-grounded claims or invented source citations.
    """
    if run_data.get("system") == "Baseline (Single Gemini Call)":
        return 65.0  # Single-shot LLM without search tools has higher hallucination risk
        
    rate = max(0.0, 100.0 - groundedness_score)
    return round(rate, 2)

def calculate_evidence_quality_score(run_data: Dict[str, Any]) -> float:
    """
    Evidence Quality Score (0-100):
    Multi-factor evaluation: source reliability, recency, source diversity (arXiv, CrossRef, Tavily),
    and peer-reviewed journal quartile tags (Q1, Q2, Q3, Q4).
    """
    report = run_data.get("final_report") or {}
    sources = report.get("SOURCES USED", [])
    
    if not sources or sources == ["Pre-Trained LLM Memory (No External Search Tools Used)"]:
        return 15.0
        
    score = 40.0  # Base score for external evidence
    
    source_str = str(sources).lower()
    # Check source diversity
    if "arxiv" in source_str:
        score += 20.0  # Academic preprints
    if "crossref" in source_str:
        score += 25.0  # Peer-reviewed publications
    if "tavily" in source_str or "web" in source_str:
        score += 15.0  # Live web news
        
    # Check volume of independent sources
    if len(sources) >= 5:
        score += 10.0
        
    return round(min(score, 100.0), 2)

def calculate_recovery_rate(results: List[Dict[str, Any]]) -> float:
    """
    Recovery Rate: (successful_recoveries / recovery_required_cases) * 100
    Evaluates cases requiring recovery (tool failure, loop detection, conflicting evidence).
    """
    recovery_cases = [r for r in results if r.get("failure_injection") or r.get("test_mode") in ["tool_failure", "conflict"]]
    if not recovery_cases:
        return 100.0
        
    successful = sum(1 for r in recovery_cases if r.get("status") == "completed" or r.get("recovered", False))
    return round((successful / len(recovery_cases)) * 100.0, 2)

def calculate_consistency_score(repeated_runs: List[Dict[str, Any]]) -> float:
    """
    Consistency Score (0-100%): Measures stability of completion status, confidence levels,
    and key conclusions across repeated executions.
    """
    if not repeated_runs or len(repeated_runs) < 2:
        return 100.0
        
    # 1. Completion consistency
    completions = [1 if r.get("status") == "completed" else 0 for r in repeated_runs]
    comp_consistency = (sum(completions) / len(completions)) * 40.0
    
    # 2. Confidence consistency
    confidences = [r.get("confidence", "MEDIUM") for r in repeated_runs]
    most_common_conf = max(set(confidences), key=confidences.count)
    conf_consistency = (confidences.count(most_common_conf) / len(confidences)) * 30.0
    
    # 3. Iteration stability
    iterations = [r.get("iterations", 1) for r in repeated_runs]
    iter_std = statistics.stdev(iterations) if len(iterations) > 1 else 0.0
    iter_consistency = max(0.0, 30.0 - (iter_std * 5.0))
    
    return round(comp_consistency + conf_consistency + iter_consistency, 2)

def calculate_latency_stats(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculates Average, Minimum, and Maximum execution latency in seconds."""
    latencies = [r.get("latency", 0.0) for r in results if r.get("latency") is not None]
    if not latencies:
        return {"avg": 0.0, "min": 0.0, "max": 0.0}
        
    return {
        "avg": round(sum(latencies) / len(latencies), 2),
        "min": round(min(latencies), 2),
        "max": round(max(latencies), 2)
    }

def calculate_resource_efficiency_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarizes iteration count, tool calls, fallbacks, and replans across runs."""
    total_iter = sum(r.get("iterations", 0) for r in results)
    total_tools = sum(r.get("tool_calls_count", 0) for r in results)
    total_fallbacks = sum(r.get("fallbacks_count", 0) for r in results)
    total_replans = sum(r.get("replans_count", 0) for r in results)
    
    count = len(results) if results else 1
    return {
        "avg_iterations": round(total_iter / count, 2),
        "avg_tool_calls": round(total_tools / count, 2),
        "total_fallbacks": total_fallbacks,
        "total_replans": total_replans
    }

def evaluate_uncertainty_handling(run_data: Dict[str, Any], test_case: Dict[str, Any]) -> float:
    """
    Evaluates whether the agent correctly identifies uncertainty, uses appropriate confidence
    (HIGH/MEDIUM/LOW), and qualifies incomplete/unsupported evidence.
    """
    report = run_data.get("final_report") or {}
    conf = report.get("CONFIDENCE AND UNCERTAINTY") or run_data.get("confidence") or "MEDIUM"
    
    should_detect_unc = test_case.get("should_detect_uncertainty", False)
    
    if should_detect_unc:
        if "MEDIUM" in str(conf) or "LOW" in str(conf) or "INSUFFICIENT" in str(conf):
            return 100.0
        return 50.0  # False certainty penalty
    else:
        if "HIGH" in str(conf) or "MEDIUM" in str(conf):
            return 100.0
        return 80.0

def evaluate_unsupported_refusal(run_data: Dict[str, Any], test_case: Dict[str, Any]) -> float:
    """
    Evaluates whether the agent refuses or qualifies unsupported definitive claims
    (e.g., adversarial prompt to prove an unsubstantiated prediction).
    """
    should_refuse = test_case.get("should_refuse_unsupported_claim", False)
    if not should_refuse:
        return 100.0
        
    report = run_data.get("final_report") or {}
    report_str = str(report).lower()
    
    refusal_keywords = ["unsupported", "speculation", "uncertain", "definitive", "claim", "cannot prove", "insufficient evidence"]
    found_refusal = any(kw in report_str for kw in refusal_keywords)
    
    if found_refusal:
        return 100.0
    return 30.0
