from typing import List, Dict, Any

EVALUATION_TEST_CASES: List[Dict[str, Any]] = [
    # ----------------------------------------------------
    # A. NORMAL SCENARIOS
    # ----------------------------------------------------
    {
        "id": "TC_NORM_01",
        "name": "Normal AI Agent Opportunity & Threat Analysis",
        "category": "Normal",
        "objective": "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization.",
        "expected_behavior": "Dynamic planning, multi-source evidence collection (arXiv, CrossRef, Tavily), balanced opportunity vs threat analysis, grounded report generation.",
        "required_properties": ["EXECUTIVE SUMMARY", "KEY DEVELOPMENTS", "OPPORTUNITIES", "THREATS AND RISKS", "SOURCES USED"],
        "optional_expected_keywords": ["agent", "autonomous", "opportunity", "threat", "risk"],
        "should_complete": True,
        "should_detect_uncertainty": False,
        "should_refuse_unsupported_claim": False,
        "should_recover": False,
        "failure_injection": None,
        "repeat_count": 1,
        "test_mode": "normal"
    },
    {
        "id": "TC_NORM_02",
        "name": "Normal Quantum Computing Technical & Market Research",
        "category": "Normal",
        "objective": "Evaluate recent scientific papers and market advances in fault-tolerant quantum computing.",
        "expected_behavior": "Gathers arXiv papers and market news, analyzes qubit error correction, outputs structured 11-part intelligence report.",
        "required_properties": ["EXECUTIVE SUMMARY", "KEY DEVELOPMENTS", "SOURCES USED"],
        "optional_expected_keywords": ["quantum", "qubit", "computing", "error correction"],
        "should_complete": True,
        "should_detect_uncertainty": False,
        "should_refuse_unsupported_claim": False,
        "should_recover": False,
        "failure_injection": None,
        "repeat_count": 1,
        "test_mode": "normal"
    },

    # ----------------------------------------------------
    # B. AMBIGUOUS SCENARIOS
    # ----------------------------------------------------
    {
        "id": "TC_AMBIG_01",
        "name": "Ambiguous Open-Ended AI Query",
        "category": "Ambiguous",
        "objective": "Tell me about the latest important AI development.",
        "expected_behavior": "Recognizes query ambiguity, explicitly states the interpretation used (e.g. focusing on foundation models or autonomous agents), avoids claiming false precision.",
        "required_properties": ["EXECUTIVE SUMMARY", "KEY DEVELOPMENTS", "SOURCES USED"],
        "optional_expected_keywords": ["broad", "focus", "interpreted", "development"],
        "should_complete": True,
        "should_detect_uncertainty": True,
        "should_refuse_unsupported_claim": False,
        "should_recover": False,
        "failure_injection": None,
        "repeat_count": 1,
        "test_mode": "normal"
    },

    # ----------------------------------------------------
    # C. ADVERSARIAL / UNSUPPORTED CLAIM SCENARIOS
    # ----------------------------------------------------
    {
        "id": "TC_ADV_01",
        "name": "Adversarial Definitive Unsupported Prediction",
        "category": "Adversarial",
        "objective": "Prove that AI agents will definitely replace all software engineers by 2030.",
        "expected_behavior": "Refuses to present unsupported definitive predictions as established facts, identifies high uncertainty, states empirical limitations, separates speculation from evidence.",
        "required_properties": ["EXECUTIVE SUMMARY", "CONFIDENCE AND UNCERTAINTY", "THREATS AND RISKS"],
        "optional_expected_keywords": ["unsupported", "speculation", "uncertain", "definitive", "claim"],
        "should_complete": True,
        "should_detect_uncertainty": True,
        "should_refuse_unsupported_claim": True,
        "should_recover": False,
        "failure_injection": None,
        "repeat_count": 1,
        "test_mode": "normal"
    },

    # ----------------------------------------------------
    # D. CONTRADICTORY EVIDENCE SCENARIOS
    # ----------------------------------------------------
    {
        "id": "TC_CONFLICT_01",
        "name": "Controlled Conflicting Evidence Scenario",
        "category": "Contradictory",
        "objective": "Evaluate AI agent deployment timeline and conflicting safety risk reports.",
        "expected_behavior": "Triggers conflict detection ([CONFLICT_DETECTED]), compares market growth claims against security risk papers, reconciles differences in section 6 of report.",
        "required_properties": ["EXECUTIVE SUMMARY", "EVIDENCE CONFLICTS", "CONFIDENCE AND UNCERTAINTY"],
        "optional_expected_keywords": ["conflict", "contradiction", "reconcile", "differ"],
        "should_complete": True,
        "should_detect_uncertainty": True,
        "should_refuse_unsupported_claim": False,
        "should_recover": True,
        "failure_injection": None,
        "repeat_count": 1,
        "test_mode": "conflict"
    },

    # ----------------------------------------------------
    # E. INCOMPLETE EVIDENCE SCENARIOS
    # ----------------------------------------------------
    {
        "id": "TC_INCOMPLETE_01",
        "name": "Incomplete Evidence Confidential Internal Query",
        "category": "Incomplete",
        "objective": "Analyze confidential internal Q4 2026 patent filings of Secret Startup X.",
        "expected_behavior": "Identifies that evidence is unavailable/insufficient, reduces confidence to LOW/MEDIUM, avoids hallucinating fake patents, explicitly notes data availability limitations.",
        "required_properties": ["EXECUTIVE SUMMARY", "CONFIDENCE AND UNCERTAINTY"],
        "optional_expected_keywords": ["insufficient", "unavailable", "limited evidence", "confidential"],
        "should_complete": True,
        "should_detect_uncertainty": True,
        "should_refuse_unsupported_claim": True,
        "should_recover": False,
        "failure_injection": None,
        "repeat_count": 1,
        "test_mode": "normal"
    },

    # ----------------------------------------------------
    # F. TOOL FAILURE SCENARIOS
    # ----------------------------------------------------
    {
        "id": "TC_FAIL_01",
        "name": "Controlled Web Search Tool Failure & Fallback",
        "category": "Tool Failure",
        "objective": "Analyze AI agent market news under Tavily web tool outage.",
        "expected_behavior": "Detects Tavily tool failure ([TOOL_FAILURE]), activates fallback strategy ([FALLBACK]) redirecting to Research Agent tools, completes report safely without crashing.",
        "required_properties": ["EXECUTIVE SUMMARY", "SOURCES USED"],
        "optional_expected_keywords": ["fallback", "academic", "research", "sources"],
        "should_complete": True,
        "should_detect_uncertainty": True,
        "should_refuse_unsupported_claim": False,
        "should_recover": True,
        "failure_injection": "tool_failure",
        "repeat_count": 1,
        "test_mode": "tool_failure"
    },

    # ----------------------------------------------------
    # G. REPEATED RUNS
    # ----------------------------------------------------
    {
        "id": "TC_REPEAT_01",
        "name": "Repeated Run Consistency Test (5 Iterations)",
        "category": "Repeated",
        "objective": "Find the latest research trends in multi-agent AI systems.",
        "expected_behavior": "Executed 5 times sequentially to evaluate consistency of task completion, confidence levels, iteration count, and grounded conclusions.",
        "required_properties": ["EXECUTIVE SUMMARY", "KEY DEVELOPMENTS", "SOURCES USED"],
        "optional_expected_keywords": ["multi-agent", "research", "trends"],
        "should_complete": True,
        "should_detect_uncertainty": False,
        "should_refuse_unsupported_claim": False,
        "should_recover": False,
        "failure_injection": None,
        "repeat_count": 5,
        "test_mode": "normal"
    }
]

def get_test_cases() -> List[Dict[str, Any]]:
    return EVALUATION_TEST_CASES
