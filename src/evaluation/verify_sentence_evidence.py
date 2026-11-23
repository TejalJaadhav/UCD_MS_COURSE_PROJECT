"""Verify saved dev judgments against their selected evidence sentences."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.overall import evaluate
from src.evaluation.run_prompted import ask

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT / "outputs/annotation_pilot/evaluation"
    / "components_sentence_dev_20261122T014938_358991Z.json"
)


def main():
    """Verify cited judgments while retaining existing fallbacks."""
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    if report["split"] != "dev":
        raise ValueError("This experiment requires a dev report.")

    report.pop("metrics", None)
    report["method"] = "components_verified_sentence_evidence"
    report["parent_report"] = SOURCE.name

    for index, row in enumerate(report["predictions"], start=1):
        components = (row.get("details") or {}).get("components")
        if not components:
            continue

        labels = []
        for component in components:
            component["pre_verification_label"] = component["label"]
            check = component["sentence_evidence_check"]
            evidence = check.get("selected_evidence")

            # Unsupported judgments have no selected supporting evidence.
            if component["label"] == "unsupported":
                labels.append("unsupported")
                continue

            if not evidence:
                component["label"] = None
                component["verification_error"] = "No valid selected evidence."
                labels.append(None)
                continue

            result, usage = ask(
                report["model"],
                (
                    "Verify whether the supplied evidence establishes the "
                    "statement. Use only this evidence. Do not supply missing "
                    "facts from memory. Preserve numbers, populations, dates, "
                    "qualifiers and relationships. A missing numerical value "
                    "does not establish a claimed number. Return supported "
                    "only if every detail is established, contradicted only "
                    "for direct conflict, otherwise unsupported."
                ),
                {
                    "statement": component["component"],
                    "evidence": evidence,
                },
                {
                    "label": {
                        "type": "string",
                        "enum": ["supported", "unsupported", "contradicted"],
                    },
                    "reason": {"type": "string"},
                },
            )

            component["evidence_verification"] = {
                "response": result,
                "usage": usage,
            }
            component["label"] = result["label"]
            labels.append(result["label"])

        row["pre_verification_prediction"] = row["prediction"]
        if None in labels:
            row["prediction"] = None
            row["error"] = "Evidence unavailable for verification."
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
    output = SOURCE.parent / f"components_verified_dev_{stamp}.json"

    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()