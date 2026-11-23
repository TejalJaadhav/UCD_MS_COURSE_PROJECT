"""Create a Markdown worksheet for reviewing saved component predictions."""

import argparse
import json
from pathlib import Path
from random import Random

from src.evaluation.overall import LABELS, evaluate, load_split


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    if report["method"] != "components" or report["split"] != "test":
        parser.error("Pass a component test report.")
    evaluate(report)

    records, _ = load_split("test", report["dataset_version"])
    by_id = {record["example_id"]: record for record in records}

    # Sample before looking at which predictions were correct.
    rng = Random(42)
    sample = []
    for label in LABELS:
        candidates = sorted(
            (row for row in report["predictions"] if row["gold_label"] == label),
            key=lambda row: row["example_id"],
        )
        sample.extend(rng.sample(candidates, 5))
    rng.shuffle(sample)

    print("# Held-out component review")
    print(f"\nRun file: `{args.report.name}`")
    print("\nSample: 15 claims, five per dataset label, seed 42.")

    for row in sample:
        example_id = row["example_id"]
        details = row.get("details") or {}
        print(f"\n## {example_id}")
        print(f"\n**Original claim:** {by_id[example_id]['claim']}")
        print(f"\n**Dataset label:** `{row['gold_label']}`")
        print(f"\n**Overall prediction:** `{row['prediction'] or 'failed'}`")

        for part in details.get("components", []):
            print(f"\n### {part['component']}")
            print(f"\n**Model judgment:** `{part['label']}`")
            for index, passage in enumerate(part["passages"], start=1):
                print(f"\n**Passage {index}:** {passage['text']}")
            print("\n- Is the evidence sufficient?")
            print("- Reviewer judgment and reason:")

        if not details.get("components"):
            reason = (
                row.get("error")
                or details.get("coverage_issue")
                or (details.get("split_review") or {}).get("reason")
                or "No component judgments recorded."
            )
            print(f"\n**No component judgments.** {reason}")
            for part in details.get("proposed_components", []):
                print(f"- Proposed part: {part}")

        print("\n- Did the split preserve the original claim?")
        print("- Were any details missing, changed, or added?")


if __name__ == "__main__":
    main()