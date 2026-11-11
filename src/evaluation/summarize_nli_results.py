"""Summarize saved NLI predictions alongside human component labels."""

import argparse
import json
from collections import Counter
from pathlib import Path

HUMAN_LABELS = ("supported", "unsupported", "contradicted")
NLI_LABELS = ("entailment", "neutral", "contradiction")


def main():
    """Read a saved run and print component prediction counts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_file", type=Path)
    args = parser.parse_args()

    report = json.loads(args.results_file.read_text(encoding="utf-8"))
    counts = Counter()
    skipped = Counter()

    for result in report["results"]:
        human_label = result["human_component_label"]
        if human_label not in HUMAN_LABELS:
            raise ValueError(f"Unexpected human label: {human_label}")

        # Count missing-evidence cases separately from model predictions.
        if result["status"] == "skipped":
            skipped[human_label] += 1
        elif result["status"] == "scored":
            prediction = result["nli_prediction"]
            if prediction not in NLI_LABELS:
                raise ValueError(f"Unexpected NLI label: {prediction}")
            counts[(human_label, prediction)] += 1
        else:
            raise ValueError(f"Unexpected status: {result['status']}")

    print(f"Results file: {args.results_file.name}")
    print(f"Examples: {report['example_count']}")
    print()
    print(
        f"{'Human label':<15}"
        f"{'Entailment':>12}"
        f"{'Neutral':>12}"
        f"{'Contradiction':>15}"
        f"{'Skipped':>10}"
    )

    for label in HUMAN_LABELS:
        print(
            f"{label:<15}"
            f"{counts[(label, 'entailment')]:>12}"
            f"{counts[(label, 'neutral')]:>12}"
            f"{counts[(label, 'contradiction')]:>15}"
            f"{skipped[label]:>10}"
        )

    print(f"\nScored: {sum(counts.values())}")
    print(f"Skipped: {sum(skipped.values())}")
    print("Descriptive pilot counts—not dataset classification accuracy.")


if __name__ == "__main__":
    main()