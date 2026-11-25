"""Compare saved 7B judgments before and after the verification stage."""

import argparse
import json
from collections import Counter
from pathlib import Path

from src.evaluation.overall import evaluate, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    if report["method"] != "components_verified":
        raise ValueError("Expected a components_verified report.")

    after_metrics = evaluate(report)
    gold, before, after = [], [], []
    accounting = Counter()

    for row in report["predictions"]:
        details = row.get("details") or {}

        if "previous_prediction" in details:
            original = details["previous_prediction"]
            accounting["verification_applied"] += 1
        elif details.get("fallback") and not details.get("components"):
            original = row["prediction"]
            accounting["unchanged_fallback"] += 1
        elif (
            row["prediction"] is None
            and not details
            and row.get("error") == "Invalid number of components"
        ):
            original = None
            accounting["decomposition_failure"] += 1
        else:
            raise ValueError(
                f"Cannot reconstruct original judgment: {row['example_id']}"
            )

        gold.append(row["gold_label"])
        before.append(original)
        after.append(row["prediction"])

    before_metrics = metrics(gold, before)
    fixed = sum(
        a != g and b == g for g, a, b in zip(gold, before, after)
    )
    broken = sum(
        a == g and b != g for g, a, b in zip(gold, before, after)
    )

    print("Model:", report["model"])
    print("Examples:", len(gold))
    for name, count in accounting.items():
        print(f"{name}: {count}")

    for name, result in (
        ("Before verification", before_metrics),
        ("After verification", after_metrics),
    ):
        print(
            f"{name}: accuracy={result['accuracy']:.2%}, "
            f"macro-F1={result['macro_f1']:.4f}, "
            f"failed={result['failed']}"
        )

    print(f"Incorrect -> correct: {fixed}")
    print(f"Correct -> incorrect or failed: {broken}")
    print(
        "Compares the full evidence-selection and verification stage, "
        "using the same saved decomposition and original judgments. "
        "Not an independent rerun of the unverified method."
    )


if __name__ == "__main__":
    main()