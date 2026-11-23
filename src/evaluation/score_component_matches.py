"""Score reviewed reference-to-prediction matches without running a model."""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "outputs/annotation_pilot/component_matching.json"
LABELS = {"supported", "unsupported", "contradicted"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    rows = json.loads(args.input.read_text(encoding="utf-8"))
    if not rows or len({r["example_id"] for r in rows}) != len(rows):
        raise ValueError("Expected nonempty examples with unique IDs.")

    totals = Counter()
    by_label = {label: Counter() for label in sorted(LABELS)}
    by_type = {}
    statuses = Counter()

    for row in rows:
        if row["matching_reviewed"] is not True:
            raise ValueError(f"Matching is unfinished: {row['example_id']}")

        statuses[row["output_status"]] += 1
        predictions = {
            part["prediction_number"]: part
            for part in row["predicted_parts"]
        }
        if len(predictions) != len(row["predicted_parts"]):
            raise ValueError("Duplicate prediction numbers.")

        for part in row["reference_parts"]:
            label = part["label"]
            status = part["match_status"]
            matches = part["matched_prediction_numbers"]

            if label not in LABELS:
                raise ValueError(f"Unexpected reference label: {label}")

            correct = False
            if status == "matched":
                if not matches or len(set(matches)) != len(matches):
                    raise ValueError("Matched details require unique prediction IDs.")
                if any(number not in predictions for number in matches):
                    raise ValueError("Unknown matched prediction number.")
                predicted_labels = [predictions[n]["label"] for n in matches]
                if any(value not in LABELS for value in predicted_labels):
                    raise ValueError("Unexpected predicted component label.")

                # A reference detail is correct only when all linked judgments agree.
                correct = all(value == label for value in predicted_labels)
            elif status in {"omitted", "no_component_output"}:
                if matches:
                    raise ValueError("An unmatched detail cannot have prediction IDs.")
            else:
                raise ValueError(f"Unfinished or unknown match status: {status}")

            counts = {
                "total": 1,
                "matched": int(status == "matched"),
                "correct": int(correct),
                "omitted": int(status == "omitted"),
                "no_component_output": int(status == "no_component_output"),
            }
            totals.update(counts)
            by_label[label].update(counts)

            # Categories describe reference mismatches, not dataset gold labels.
            for category in set(part.get("mismatch_types", [])):
                by_type.setdefault(category, Counter()).update(counts)

        totals["added_predictions"] += len(
            row.get("added_prediction_numbers", [])
        )
        totals["redundant_predictions"] += len(
            row.get("redundant_prediction_numbers", [])
        )

    print(f"Reviewed claims: {len(rows)}")
    print(f"Output statuses: {dict(statuses)}")
    print(f"Reference details: {totals['total']}")
    print(f"Matched: {totals['matched']}")
    print(f"Correct labels: {totals['correct']}")
    print(f"Omitted: {totals['omitted']}")
    print(f"No component output: {totals['no_component_output']}")
    print(f"Added predictions: {totals['added_predictions']}")
    print(f"Redundant predictions: {totals['redundant_predictions']}")

    if totals["matched"]:
        print(
            "Label agreement among matched reference details: "
            f"{totals['correct'] / totals['matched']:.2%}"
        )
    print(
        "Reference details covered with a correct label: "
        f"{totals['correct'] / totals['total']:.2%}"
    )

    print("\nReference-label breakdown:")
    for label, counts in by_label.items():
        print(
            f"{label}: {counts['correct']}/{counts['total']} correct; "
            f"{counts['matched']} matched"
        )

    print("\nMismatch categories represented in this sample:")
    for category, counts in sorted(by_type.items()):
        print(
            f"{category}: {counts['correct']}/{counts['total']} "
            "reference details correctly labeled"
        )

    print(
        "\nExploratory, AI-assisted, user-reviewed annotations. "
        "Reviewers previously saw model outputs. "
        "Categories absent from this sample cannot be assessed."
    )


if __name__ == "__main__":
    main()