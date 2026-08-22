import os
import sys
import json
import csv
import time
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.evaluation.test_cases import EVALUATION_TEST_CASES
from backend.evaluation.evaluator import evaluate_test_case

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_agent.run_evaluation")

def main():
    print("\n========================================================")
    print("NOVA AGENT — TASK 6 ISOLATED EVALUATION FRAMEWORK")
    print("========================================================")

    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "reports"))
    os.makedirs(reports_dir, exist_ok=True)

    results = []
    summary_rows = []

    for test_case in EVALUATION_TEST_CASES:
        eval_res = evaluate_test_case(test_case)
        results.append(eval_res)

        m = eval_res["primary_run_metrics"]
        rep = eval_res.get("repeated_runs_summary")
        lat_text = f"{m['latency_seconds']}s"
        if rep:
            lat_text = f"{rep['avg_latency_seconds']}s (avg)"

        summary_rows.append({
            "test_id": eval_res["test_id"],
            "scenario": eval_res["scenario"],
            "status": "PASS" if m["task_completion"] else "FAIL",
            "latency": lat_text,
            "iterations": m["iterations"],
            "tool_calls": m["tool_calls_count"],
            "confidence": m["confidence_level"],
            "failure_recovery": "YES" if m["failure_recovery_success"] else "N/A"
        })

    # Save detailed JSON evaluation report
    json_path = os.path.join(reports_dir, "latest_evaluation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save CSV evaluation summary
    csv_path = os.path.join(reports_dir, "evaluation_summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["test_id", "scenario", "status", "latency", "iterations", "tool_calls", "confidence", "failure_recovery"])
        writer.writeheader()
        writer.writerows(summary_rows)

    # Save Human Evaluation Template
    human_evals = [r["human_evaluation_template"] for r in results]
    human_json_path = os.path.join(reports_dir, "human_evaluation.json")
    with open(human_json_path, "w", encoding="utf-8") as f:
        json.dump(human_evals, f, indent=2)

    print("\n========================================================")
    print("TASK 6 EVALUATION SUMMARY TABLE")
    print("========================================================")
    print(f"{'ID':<7} | {'SCENARIO':<22} | {'STATUS':<6} | {'LATENCY':<10} | {'ITERS':<5} | {'TOOLS':<5} | {'CONFIDENCE':<10}")
    print("-" * 80)
    for r in summary_rows:
        print(f"{r['test_id']:<7} | {r['scenario']:<22} | {r['status']:<6} | {r['latency']:<10} | {r['iterations']:<5} | {r['tool_calls']:<5} | {r['confidence']:<10}")
    print("========================================================")
    print(f"Reports saved to: {reports_dir}\n")

if __name__ == "__main__":
    main()
