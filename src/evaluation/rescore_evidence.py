"""Rejudge saved dev components with validated evidence quotations."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.evidence_check import judge_with_evidence
from src.evaluation.overall import evaluate

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT / "outputs/annotation_pilot/evaluation"
    / "components_dev_20261121T211932_882760Z.json"
)


def main():
    """Preserve prior splits and fallbacks while revising component judgments."""
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    if report["split"] != "dev":
        raise ValueError("This experiment requires a dev report.")

    report.pop("metrics", None)
    report["method"] = "components_evidence_validated"
    report["parent_report"] = SOURCE.name

    for index, row in enumerate(report["predictions"], start=1):
        details = row.get("details") or {}
        components = details.get("components")

        # Preserve fallback and failed-split cases for a controlled comparison.
        if not components:
            continue

        labels = []
        for component in components:
            component["previous_label"] = component["label"]
            result = judge_with_evidence(
                report["model"],
                component["component"],
                component["passages"],
            )
            component["evidence_check"] = result
            judgment = result["judgment"]
            component["label"] = judgment["label"] if judgment else None
            labels.append(component["label"])

        row["previous_prediction"] = row["prediction"]

        # A failed evidence check leaves this example without a prediction.
        if None in labels:
            row["prediction"] = None
            row["error"] = "Evidence validation failed."
        else:
            supported = labels.count("supported")
            if supported == len(labels):
                row["prediction"] = "complete_support"
            elif supported:
                row["prediction"] = "partial_support"
            else:
                row["prediction"] = "no_support"

        print(
            f"[{index}/{len(report['predictions'])}] "
            f"{row['example_id']}: {row['prediction']}",
            flush=True,
        )

    report["metrics"] = evaluate(report)
    now = datetime.now(timezone.utc)
    report["created_at_utc"] = now.isoformat()
    stamp = now.strftime("%Y%m%dT%H%M%S_%fZ")
    output = SOURCE.parent / f"components_evidence_dev_{stamp}.json"

    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()