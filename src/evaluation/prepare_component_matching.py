"""Prepare reference and predicted claim parts for manual matching."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / "annotation/component_reference_annotations.json"
REPORT = (
    ROOT
    / "outputs/annotation_pilot/evaluation"
    / "components_test_20261112T201634_714712Z.json"
)
OUTPUT = ROOT / "outputs/annotation_pilot/component_matching.json"


def main():
    """Create a matching worksheet without overwriting earlier work."""
    references = json.loads(REFERENCES.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    predictions = {
        row["example_id"]: row for row in report["predictions"]
    }

    matches = []
    for reference in references:
        prediction = predictions[reference["example_id"]]
        details = prediction.get("details") or {}
        predicted_parts = details.get("components", [])

        # Fallbacks and failures have no scored component output.
        status = (
            "failed" if prediction["prediction"] is None
            else "fallback" if details.get("fallback")
            else "component_scored"
        )

        matches.append({
            "example_id": reference["example_id"],
            "output_status": status,
            "reference_parts": [
                {
                    "reference_number": number,
                    "text": part["text"],
                    "label": part["label"],
                    "mismatch_types": part.get("mismatch_types", []),
                    "matched_prediction_numbers": [],
                    "match_status": "pending",
                    "review_note": "",
                }
                for number, part in enumerate(
                    reference["components"], start=1
                )
            ],
            "predicted_parts": [
                {
                    "prediction_number": number,
                    "text": part["component"],
                    "label": part["label"],
                }
                for number, part in enumerate(predicted_parts, start=1)
            ],
            "added_prediction_numbers": [],
            "matching_reviewed": False,
        })

    # Exclusive creation protects a worksheet that has already been edited.
    with OUTPUT.open("x", encoding="utf-8") as stream:
        json.dump(matches, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print(f"Prepared {len(matches)} examples.")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()