"""Recover saved component judgments from before verification; no model calls."""

import argparse
import copy
import json
from pathlib import Path

from src.evaluation.overall import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    original = json.loads(args.report.read_text(encoding="utf-8"))
    if original["method"] != "components_verified":
        raise ValueError("Expected a verified pipeline report.")
    evaluate(original)

    report = copy.deepcopy(original)
    report["method"] = "components_before_verification"
    report["parent_report"] = args.report.name
    report["reconstruction_note"] = (
        "Original judgments recovered from the verified run. "
        "Same decomposition and model calls, not an independent rerun. "
        "Fallbacks and failures before verification are retained."
    )

    for row in report["predictions"]:
        details = row.get("details") or {}

        if "previous_prediction" in details:
            row["prediction"] = details["previous_prediction"]
            for part in details.get("components", []):
                if "previous_label" not in part:
                    raise ValueError("Missing original component label.")
                part["label"] = part.pop("previous_label")
                for field in (
                    "sentence_evidence_check",
                    "evidence_verification",
                    "verification_error",
                ):
                    part.pop(field, None)

            details.pop("previous_prediction")
            details.pop("verification_version", None)
            row.pop("error", None)

        elif details.get("fallback") and not details.get("components"):
            details.pop("verification_version", None)

        elif (
            row["prediction"] is None
            and not details
            and row.get("error") == "Invalid number of components"
        ):
            pass

        else:
            raise ValueError(
                f"Cannot reconstruct example: {row['example_id']}"
            )

    report["metrics"] = evaluate(report)
    output = args.report.with_name(
        args.report.stem + "_before_verification.json"
    )
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    scores = report["metrics"]
    print("Examples:", scores["count"])
    print(f"Accuracy: {scores['accuracy']:.2%}")
    print(f"Macro-F1: {scores['macro_f1']:.4f}")
    print("Failures:", scores["failed"])
    print("Saved:", output.resolve())


if __name__ == "__main__":
    main()