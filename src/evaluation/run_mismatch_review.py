"""Prepare or run targeted mismatch diagnostics; no automatic reference matching."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.overall import load_split
from src.evaluation.run_prompted import open_checkpoint

ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS = ROOT / "annotation/mismatch_review.json"
FOLDER = ROOT / "outputs/annotation_pilot/evaluation"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--model", default="ollama:qwen2.5:7b")
    args = parser.parse_args()

    annotations = json.loads(ANNOTATIONS.read_text(encoding="utf-8"))
    records, fingerprint = load_split("dev", "cleaned")
    by_id = {row["example_id"]: row for row in records}
    ids = [row["example_id"] for row in annotations]

    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Expected nonempty, unique example IDs.")

    for row in annotations:
        key = row["example_id"]
        if key not in by_id or row.get("reviewed") is not True:
            raise ValueError(f"Unknown or unreviewed example: {key}")
        if row["claim"] != by_id[key]["claim"]:
            raise ValueError(f"Original claim differs: {key}")
        if row["evidence_quote"] not in by_id[key]["source"]:
            raise ValueError(f"Quote not found verbatim: {key}")
        if not row.get("reference_parts"):
            raise ValueError(f"No reference parts: {key}")
        for part in row["reference_parts"]:
            if part["label"] not in {
                "supported", "unsupported", "contradicted"
            }:
                raise ValueError(f"Invalid reference label: {key}")

    print(f"Validated {len(ids)} reviewed claim-source pairs.")
    print("Targeted diagnostic sample; not a representative benchmark.")

    if not args.run:
        print("Preparation only: no model calls made.")
        return

    from src.evaluation.verified_pipeline import predict_verified

    # Reject resuming after changes to annotations or pipeline code.
    code_files = [
        "run_mismatch_review.py",
        "run_prompted.py",
        "verified_pipeline.py",
        "rescore_sentence_evidence.py",
    ]
    settings = {
        "model": args.model,
        "example_ids": ids,
        "dataset_sha256": fingerprint,
        "annotations_sha256": hashlib.sha256(
            ANNOTATIONS.read_bytes()
        ).hexdigest(),
        "code_sha256": {
            name: hashlib.sha256(
                (ROOT / "src/evaluation" / name).read_bytes()
            ).hexdigest()
            for name in code_files
        },
    }

    FOLDER.mkdir(parents=True, exist_ok=True)
    checkpoint = FOLDER / "mismatch_review_verified.sqlite"
    db = open_checkpoint(checkpoint, settings)
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
                # References and mismatch tags are never passed to the model.
                result["prediction"], result["details"] = predict_verified(
                    args.model, record["claim"], record["source"] or ""
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
        "method": "components_verified",
        "sample_type": "targeted_dev_diagnostics",
        "settings": settings,
        "reference_annotations": annotations,
        "predictions": predictions,
        "note": "Component matching must be reviewed before category scoring.",
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output = FOLDER / f"mismatch_review_verified_{stamp}.json"
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()