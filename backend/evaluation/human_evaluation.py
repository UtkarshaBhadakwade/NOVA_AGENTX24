import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("nova_agent.evaluation.human")

HUMAN_EVAL_RUBRIC = {
    "scale": "1-5 Likert Scale (1 = Poor, 2 = Weak, 3 = Acceptable, 4 = Good, 5 = Excellent)",
    "dimensions": {
        "accuracy": "Factual correctness and factual consistency of key intelligence claims.",
        "evidence_grounding": "Direct linking of report statements to verifiable citations (arXiv, CrossRef, Web).",
        "evidence_quality": "Source reliability, peer-reviewed journal quality, and recency.",
        "strategic_usefulness": "Actionability, clear opportunity/threat decomposition, and practical recommendations.",
        "uncertainty_handling": "Honest qualification of missing data, non-speculative tone, and appropriate confidence badges.",
        "robustness": "System stability under ambiguous prompts, tool outages, and adversarial claims.",
        "overall_quality": "Overall synthesis clarity, formatting, and report value."
    }
}

DEFAULT_HUMAN_EVAL_STORE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "reports", "human_evaluation.json")
)

def init_human_evaluation_store(file_path: str = DEFAULT_HUMAN_EVAL_STORE_PATH) -> Dict[str, Any]:
    """Initializes human evaluation store marked PENDING until real scores are entered."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading human eval store: {str(e)}")

    default_data = {
        "status": "PENDING",
        "rubric": HUMAN_EVAL_RUBRIC,
        "evaluator_name": None,
        "last_updated": None,
        "evaluations": [],
        "aggregated_scores": {
            "accuracy_avg": None,
            "evidence_grounding_avg": None,
            "evidence_quality_avg": None,
            "strategic_usefulness_avg": None,
            "uncertainty_handling_avg": None,
            "robustness_avg": None,
            "overall_quality_avg": None,
            "total_evaluations_completed": 0
        }
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(default_data, f, indent=2)
        
    return default_data

def record_human_evaluation(
    eval_record: Dict[str, Any],
    file_path: str = DEFAULT_HUMAN_EVAL_STORE_PATH
) -> Dict[str, Any]:
    """
    Saves a completed human evaluation score entry (1-5 scale) and updates aggregated metrics.
    """
    store = init_human_evaluation_store(file_path)
    
    eval_entry = {
        "test_case_id": eval_record.get("test_case_id"),
        "objective": eval_record.get("objective"),
        "evaluator_name": eval_record.get("evaluator_name", "Human Evaluator"),
        "timestamp": eval_record.get("timestamp"),
        "scores": {
            "accuracy": min(5, max(1, int(eval_record.get("accuracy", 3)))),
            "evidence_grounding": min(5, max(1, int(eval_record.get("evidence_grounding", 3)))),
            "evidence_quality": min(5, max(1, int(eval_record.get("evidence_quality", 3)))),
            "strategic_usefulness": min(5, max(1, int(eval_record.get("strategic_usefulness", 3)))),
            "uncertainty_handling": min(5, max(1, int(eval_record.get("uncertainty_handling", 3)))),
            "robustness": min(5, max(1, int(eval_record.get("robustness", 3)))),
            "overall_quality": min(5, max(1, int(eval_record.get("overall_quality", 3))))
        },
        "comments": eval_record.get("comments", "")
    }
    
    store["evaluations"].append(eval_entry)
    store["status"] = "COMPLETED"
    store["evaluator_name"] = eval_entry["evaluator_name"]
    store["last_updated"] = eval_entry["timestamp"]
    
    # Recalculate aggregated averages
    store["aggregated_scores"] = aggregate_human_scores(store["evaluations"])
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)
        
    return store

def aggregate_human_scores(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregates human evaluation scores across completed evaluations."""
    if not evaluations:
        return {
            "accuracy_avg": None,
            "evidence_grounding_avg": None,
            "evidence_quality_avg": None,
            "strategic_usefulness_avg": None,
            "uncertainty_handling_avg": None,
            "robustness_avg": None,
            "overall_quality_avg": None,
            "total_evaluations_completed": 0
        }
        
    count = len(evaluations)
    return {
        "accuracy_avg": round(sum(e["scores"]["accuracy"] for e in evaluations) / count, 2),
        "evidence_grounding_avg": round(sum(e["scores"]["evidence_grounding"] for e in evaluations) / count, 2),
        "evidence_quality_avg": round(sum(e["scores"]["evidence_quality"] for e in evaluations) / count, 2),
        "strategic_usefulness_avg": round(sum(e["scores"]["strategic_usefulness"] for e in evaluations) / count, 2),
        "uncertainty_handling_avg": round(sum(e["scores"]["uncertainty_handling"] for e in evaluations) / count, 2),
        "robustness_avg": round(sum(e["scores"]["robustness"] for e in evaluations) / count, 2),
        "overall_quality_avg": round(sum(e["scores"]["overall_quality"] for e in evaluations) / count, 2),
        "total_evaluations_completed": count
    }
