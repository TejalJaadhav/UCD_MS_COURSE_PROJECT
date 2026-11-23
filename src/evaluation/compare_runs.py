"""Compare saved evaluation reports on the same dataset records."""

import argparse
import json
from itertools import combinations
from pathlib import Path

from src.evaluation.overall import LABELS, evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path)
    args = parser.parse_args()

    # Validate every report before printing a comparison.
    reference = None
    results = []
    correctness = []
    for path in args.reports:
        report = json.loads(path.read_text(encoding="utf-8"))
        identity = (
            report["split"], report["dataset_version"], report["dataset_sha256"],
            set(report["example_ids"]),
        )
        if reference is None:
            reference = identity
        elif identity != reference:
            parser.error(f"{path.name} covers different dataset records")
        metrics = evaluate(report)
        fallback = sum(
            bool((row.get("details") or {}).get("fallback"))
            for row in report["predictions"]
        )
        results.append((report["method"], path.name, metrics, fallback))
        correctness.append((
            report["method"],
            {row["example_id"] for row in report["predictions"]
             if row["prediction"] == row["gold_label"]},
        ))


    print(f"Dataset: {reference[1]} {reference[0]} ({len(reference[3])} examples)")
    print("| Method | Accuracy | Macro-F1 | Failed | Fallbacks |")
    print("|---|---:|---:|---:|---:|")
    for method, _, metrics, fallback in results:
        print(f"| {method} | {metrics['accuracy']:.2%} | {metrics['macro_f1']:.4f} "
              f"| {metrics['failed']} | {fallback} |")

    print()
    print("| Method | Label | Precision | Recall | F1 | Correct / total |")
    print("|---|---|---:|---:|---:|---:|")
    for method, _, metrics, _ in results:
        for label in LABELS:
            scores = metrics["per_class"][label]
            correct = metrics["confusion_matrix"][label][label]
            print(f"| {method} | {label} | {scores['precision']:.4f} "
                  f"| {scores['recall']:.4f} | {scores['f1']:.4f} "
                  f"| {correct}/{scores['support']} |")

    if len(correctness) > 1:
        print("\n| Method A | Method B | Only A correct | Only B correct | Both correct | Neither correct |")
        print("|---|---|---:|---:|---:|---:|")
        for (name_a, correct_a), (name_b, correct_b) in combinations(correctness, 2):
            print(f"| {name_a} | {name_b} | {len(correct_a - correct_b)} "
                  f"| {len(correct_b - correct_a)} | {len(correct_a & correct_b)} "
                  f"| {len(reference[3] - (correct_a | correct_b))} |")

    print("\nReports:")
    for method, name, _, _ in results:
        print(f"- {method}: {name}")


if __name__ == "__main__":
    main()
