import os
import json
from typing import Dict, Any

HUMAN_EVAL_RUBRIC = {
    "1": "Very Poor / Completely Unacceptable",
    "2": "Poor / Partial or Flawed",
    "3": "Acceptable / Adequate Quality",
    "4": "Good / High Quality & Relevant",
    "5": "Excellent / State-of-the-Art Precision"
}

def generate_human_eval_template(test_id: str, scenario: str, objective: str, report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a structured human evaluation template with default PENDING status.
    Stores separate from automated metric results.
    """
    return {
        "test_id": test_id,
        "scenario": scenario,
        "objective": objective,
        "status": "PENDING",
        "human_evaluator_id": None,
        "timestamp": None,
        "scores": {
            "accuracy": {"score": None, "max": 5, "description": "Is the intelligence factually correct based on real sources?"},
            "groundedness": {"score": None, "max": 5, "description": "Are claims directly tied to citations without hallucinations?"},
            "evidence_quality": {"score": None, "max": 5, "description": "Are academic journals (Q1/Q2) and market news authoritative?"},
            "strategic_usefulness": {"score": None, "max": 5, "description": "Does the report provide actionable recommendations for decision-makers?"},
            "uncertainty_handling": {"score": None, "max": 5, "description": "Does the report properly qualify ambiguous or unverified claims?"},
            "overall_quality": {"score": None, "max": 5, "description": "Overall utility and presentation score."}
        },
        "notes": ""
    }
