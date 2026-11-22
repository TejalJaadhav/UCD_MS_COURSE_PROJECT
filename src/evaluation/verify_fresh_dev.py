"""Evaluate sentence selection and verification on the fixed fresh dev sample."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.overall import evaluate
from src.evaluation.rescore_sentence_evidence import judge_component
from src.evaluation.run_prompted import ask

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT / "outputs/annotation_pilot/evaluation"
    / "components_fresh_original_20261122T022113_279028Z.json"
)


def main():
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    if report["split"] != "dev":
        raise ValueError("Expected a dev report.")

    report.pop("metrics", None)
    report["method"] = "components_7b_fresh_verified"
    report["parent_report"] = SOURCE.name

    for index, row in enumerate(report["predictions"], start=1):
        parts = (row.get("details") or {}).get("components")
        if not parts:
            continue

        labels = []
        for part in parts:
            part["previous_label"] = part["label"]

            try:
                # Reuse the sentence-selection method tested earlier.
                selection = judge_component(report["model"], part)
                part["sentence_evidence_check"] = selection
                if selection["status"] != "valid":
                    raise ValueError("Invalid evidence selection.")

                label = selection["response"]["label"]
                if label != "unsupported":
                    judgment, usage = ask(
                        report["model"],
                        (
                            "Verify whether the supplied evidence establishes "
                            "the statement. Use only this evidence. Do not supply "
                            "missing facts from memory. Preserve numbers, "
                            "populations, dates, qualifiers and relationships. "
                            "A missing numerical value does not establish a "
                            "claimed number. Return supported only if every "
                            "detail is established, contradicted only for "
                            "direct conflict, otherwise unsupported."
                        ),
                        {
                            "statement": part["component"],
                            "evidence": selection["selected_evidence"],
                        },
                        {
                            "label": {
                                "type": "string",
                                "enum": [
                                    "supported", "unsupported", "contradicted"
                                ],
                            },
                            "reason": {"type": "string"},
                        },
                    )
                    part["evidence_verification"] = {
                        "response": judgment,
                        "usage": usage,
                    }
                    label = judgment["label"]

                part["label"] = label

            except ValueError as error:
                part["label"] = None
                part["verification_error"] = str(error)

            labels.append(part["label"])

        row["previous_prediction"] = row["prediction"]
        if None in labels:
            row["prediction"] = None
            row["error"] = "Evidence selection or verification failed."
        elif all(label == "supported" for label in labels):
            row["prediction"] = "complete_support"
        elif "supported" in labels:
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
    output = SOURCE.parent / f"components_fresh_verified_{stamp}.json"

    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()