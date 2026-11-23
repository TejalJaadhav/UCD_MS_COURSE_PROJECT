"""Paired bootstrap confidence intervals from two saved evaluation reports."""

import argparse
import json
import random
from pathlib import Path

from src.evaluation.overall import evaluate, metrics


def percentile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (
        ordered[upper] - ordered[lower]
    ) * (position - lower)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--samples", type=int, default=2000)
    args = parser.parse_args()
    if args.samples < 100:
        parser.error("Use at least 100 bootstrap samples.")

    reports = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (args.baseline, args.candidate)
    ]

    # Validate predictions against their original dataset.
    observed = [evaluate(report) for report in reports]
    for field in ("split", "dataset_version", "dataset_sha256"):
        if reports[0][field] != reports[1][field]:
            raise ValueError(f"Reports differ in {field}.")

    ids = reports[0]["example_ids"]
    if set(ids) != set(reports[1]["example_ids"]):
        raise ValueError("Reports must contain the same examples.")

    indexed = [
        {row["example_id"]: row for row in report["predictions"]}
        for report in reports
    ]
    gold = [indexed[0][key]["gold_label"] for key in ids]
    predictions = [
        [rows[key]["prediction"] for key in ids]
        for rows in indexed
    ]

    rng = random.Random(42)
    differences = {"accuracy": [], "macro_f1": []}

    for _ in range(args.samples):
        # Both methods receive exactly the same resampled examples.
        indices = rng.choices(range(len(ids)), k=len(ids))
        sampled_gold = [gold[i] for i in indices]
        scores = [
            metrics(sampled_gold, [values[i] for i in indices])
            for values in predictions
        ]
        for measure in differences:
            differences[measure].append(
                scores[1][measure] - scores[0][measure]
            )

    print("Baseline:", args.baseline.name)
    print("Candidate:", args.candidate.name)
    print(f"Examples: {len(ids)}; resamples: {args.samples}; seed: 42")
    print("Differences are candidate minus baseline, in percentage points.")

    for measure, values in differences.items():
        delta = observed[1][measure] - observed[0][measure]
        low = percentile(values, 0.025)
        high = percentile(values, 0.975)
        print(
            f"{measure}: {delta * 100:+.2f}; "
            f"95% interval [{low * 100:+.2f}, {high * 100:+.2f}]"
        )

    print(
        "Exploratory example-level bootstrap. Does not account for "
        "shared-question/source clusters, model-run variation, or "
        "development decisions informed by earlier test results."
    )


if __name__ == "__main__":
    main()