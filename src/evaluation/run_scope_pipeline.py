"""Run the experimental pipeline on fixed scope-validation claims."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.overall import load_split
from src.evaluation.run_prompted import open_checkpoint

ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS = ROOT / "annotation/scope_validation.json"
FOLDER = ROOT / "outputs/annotation_pilot/evaluation"
MODEL = "ollama:qwen2.5:7b"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()

    references = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    records, fingerprint = load_split("dev", "cleaned")
    by_id = {row["example_id"]: row for row in records}
    ids = [row["example_id"] for row in references]

    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Expected nonempty, unique IDs.")

    for row in references:
        key = row["example_id"]
        if key not in by_id or row.get("reviewed") is not True:
            raise ValueError(f"Unknown or unreviewed example: {key}")
        if row["claim"] != by_id[key]["claim"]:
            raise ValueError(f"Claim differs: {key}")
        if not row["evidence_quote"].strip():
            raise ValueError(f"Empty reference quote: {key}")
        if row["evidence_quote"] not in by_id[key]["source"]:
            raise ValueError(f"Reference quote not found: {key}")

    print(f"Validated {len(ids)} claim-source pairs.")

    if not args.run:
        print("Preparation only. No model calls made.")
        return

    from src.evaluation.scope_context_pipeline import predict_scope_context

    files = [
        "run_scope_pipeline.py",
        "scope_context_pipeline.py",
        "check_context_evidence.py",
        "rescore_sentence_evidence.py",
        "run_prompted.py",
    ]
    settings = {
        "model": MODEL,
        "example_ids": ids,
        "dataset_sha256": fingerprint,
        "annotations_sha256": hashlib.sha256(
            ANNOTATIONS.read_bytes()
        ).hexdigest(),
        "code_sha256": {
            name: hashlib.sha256(
                (ROOT / "src/evaluation" / name).read_bytes()
            ).hexdigest()
            for name in files
        },
    }

    FOLDER.mkdir(parents=True, exist_ok=True)
    db = open_checkpoint(FOLDER / "scope_pipeline_v2.sqlite", settings)
    predictions = []

    try:
        completed = dict(db.execute("SELECT example_id, result FROM rows"))
        print(f"Checkpoint: {len(completed)}/{len(ids)} saved", flush=True)

        for index, key in enumerate(ids, 1):
            if key in completed:
                predictions.append(json.loads(completed[key]))
                continue

            record = by_id[key]
            result = {"example_id": key}

            try:
                # Only the original claim and full source are model inputs.
                result["prediction"], result["details"] = (
                    predict_scope_context(
                        MODEL, record["claim"], record["source"] or ""
                    )
                )
            except ValueError as error:
                result.update(prediction=None, error=str(error))

            with db:
                db.execute(
                    "INSERT INTO rows VALUES (?, ?)",
                    (key, json.dumps(result, ensure_ascii=False)),
                )

            predictions.append(result)
            print(
                f"[{index}/{len(ids)}] {key}: {result['prediction']}",
                flush=True,
            )
    finally:
        db.close()

    report = {
        "method": "scope_context_v1",
        "settings": settings,
        "reference_annotations": references,
        "predictions": predictions,
        "limitations": (
            "Small targeted development sample. Component matching requires "
            "review before scoring. dev_00217 has only one annotated target "
            "component; do not score its full claim against that component."
        ),
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = FOLDER / f"scope_pipeline_{stamp}.json"
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()