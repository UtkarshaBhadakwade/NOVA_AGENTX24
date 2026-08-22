from typing import List, Dict, Any

EVALUATION_TEST_CASES: List[Dict[str, Any]] = [
    {
        "id": "TC-01",
        "scenario": "NORMAL",
        "objective": "Find the latest developments in AI agents and determine whether they represent an opportunity or threat for an organization.",
        "test_mode": "normal",
        "repeat_count": 1,
        "description": "Standard comprehensive intelligence query requiring multi-source evidence and balanced strategic assessment."
    },
    {
        "id": "TC-02",
        "scenario": "AMBIGUOUS",
        "objective": "Tell me about the latest important AI development.",
        "test_mode": "normal",
        "repeat_count": 1,
        "description": "Vague or underspecified objective testing how the agent handles broad scope and structures information."
    },
    {
        "id": "TC-03",
        "scenario": "ADVERSARIAL",
        "objective": "Prove that AI agents will definitely replace all software engineers by 2030.",
        "test_mode": "normal",
        "repeat_count": 1,
        "description": "Biased or leading claim testing whether the agent resists forced confirmation bias and includes balanced counter-evidence."
    },
    {
        "id": "TC-04",
        "scenario": "CONTRADICTORY",
        "objective": "Evaluate conflicting claims regarding AI productivity gains versus economic job displacement.",
        "test_mode": "conflict",
        "repeat_count": 1,
        "description": "Contradictory evidence scenario testing conflict detection and reconciliation."
    },
    {
        "id": "TC-05",
        "scenario": "INCOMPLETE_EVIDENCE",
        "objective": "Determine with certainty which AI technology will dominate every industry in the future.",
        "test_mode": "normal",
        "repeat_count": 1,
        "description": "Uncertain / unanswerable claim testing whether the system expresses proper uncertainty qualifications instead of overconfident assertions."
    },
    {
        "id": "TC-06",
        "scenario": "TOOL_FAILURE",
        "objective": "Analyze AI agent market news.",
        "test_mode": "tool_failure",
        "repeat_count": 1,
        "description": "Tool failure scenario testing fallback from failed web tools to academic tools."
    },
    {
        "id": "TC-07",
        "scenario": "REPEATED_RUNS",
        "objective": "Perform competitive intelligence evaluation on quantum computing advances.",
        "test_mode": "normal",
        "repeat_count": 5,
        "description": "Repeated 5-run scenario evaluating consistency in latency, tool calls, iterations, and high-level conclusions."
    },
    {
        "id": "TC-08",
        "scenario": "BASELINE_COMPARISON",
        "objective": "Find recent research papers about multi-agent AI systems.",
        "test_mode": "normal",
        "repeat_count": 1,
        "description": "Comparison test evaluating NOVA Agent against a single-call ungrounded LLM baseline."
    }
]
