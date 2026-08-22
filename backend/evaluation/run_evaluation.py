import sys
import os
import json
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.evaluation.evaluator import Task6Evaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_agent.evaluation.runner")

def main():
    print("========================================================")
    print("NOVA AGENT — TASK 6 EVALUATION SUITE EXECUTION")
    print("========================================================")
    
    evaluator = Task6Evaluator()
    summary = evaluator.run_full_evaluation()
    
    print("\n========================================================")
    print("TASK 6 AUTOMATED METRICS SUMMARY")
    print("========================================================")
    metrics = summary["overall_metrics"]
    print(f"Task Completion Rate               : {metrics['task_completion_rate']}%")
    print(f"Accuracy Score                     : {metrics['accuracy_score']}%")
    print(f"Groundedness Score                 : {metrics['groundedness_score']}%")
    print(f"Hallucination Rate                 : {metrics['hallucination_rate']}%")
    print(f"Evidence Quality Score             : {metrics['evidence_quality_score']}%")
    print(f"Recovery Rate                      : {metrics['recovery_rate']}%")
    print(f"Consistency Score                  : {metrics['consistency_score']}%")
    print(f"Latency (Avg / Min / Max)          : {metrics['latency_seconds']['avg']}s / {metrics['latency_seconds']['min']}s / {metrics['latency_seconds']['max']}s")
    print(f"Uncertainty Handling Score         : {metrics['uncertainty_handling_score']}%")
    print(f"Unsupported Claim Refusal Score    : {metrics['unsupported_claim_refusal_score']}%")
    
    print("\n========================================================")
    print("BASELINE VS NOVA AGENT COMPARISON")
    print("========================================================")
    b_comp = summary["baseline_comparison"]
    print(f"{'METRIC':<25} | {'NOVA AGENT':<15} | {'SINGLE GEMINI BASELINE'}")
    print("-" * 65)
    print(f"{'Task Completion Rate':<25} | {b_comp['nova_agent']['completion_rate']}%{'':<10} | {b_comp['single_gemini_baseline']['completion_rate']}%")
    print(f"{'Accuracy Score':<25} | {b_comp['nova_agent']['accuracy']}%{'':<10} | {b_comp['single_gemini_baseline']['accuracy']}%")
    print(f"{'Groundedness Score':<25} | {b_comp['nova_agent']['groundedness']}%{'':<10} | {b_comp['single_gemini_baseline']['groundedness']}%")
    print(f"{'Hallucination Rate':<25} | {b_comp['nova_agent']['hallucination_rate']}%{'':<10} | {b_comp['single_gemini_baseline']['hallucination_rate']}%")
    print(f"{'Average Latency':<25} | {b_comp['nova_agent']['avg_latency']}s{'':<9} | {b_comp['single_gemini_baseline']['avg_latency']}s")
    print("========================================================\n")

if __name__ == "__main__":
    main()
