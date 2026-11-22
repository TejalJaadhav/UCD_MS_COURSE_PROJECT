"""Evaluate the original 7B component method on the fixed fresh dev sample."""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.overall import evaluate, load_split
from src.evaluation.run_prompted import open_checkpoint, predict

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "outputs/annotation_pilot/evaluation"
MANIFEST = FOLDER / "fresh_dev_sample.json"
CHECKPOINT = FOLDER / "fresh_dev_7b_original.sqlite"
MODEL = "ollama:qwen2.5:7b"


def main():
    """Save each prediction and resume completed examples when rerun."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records, fingerprint = load_split("dev", "raw")
    if fingerprint != manifest["dataset_sha256"]:
        raise ValueError("Dataset differs from the saved sample.")

    by_id = {row["example_id"]: row for row in records}
    ids = manifest["example_ids"]
    if len(set(ids)) != len(ids) or not set(ids).issubset(by_id):
        raise ValueError("Sample contains duplicate or unknown IDs.")

    settings = {
        "method": "components",
        "model": MODEL,
        "example_ids": ids,
        "dataset_sha256": fingerprint,
    }
    db = open_checkpoint(CHECKPOINT, settings)
    completed = dict(db.execute("SELECT example_id, result FROM rows"))
    print(f"Checkpoint: {len(completed)}/{len(ids)} saved", flush=True)

    predictions = []
    try:
        for index, example_id in enumerate(ids, start=1):
            if example_id in completed:
                predictions.append(json.loads(completed[example_id]))
                continue

            record = by_id[example_id]
            row = {
                "example_id": example_id,
                "gold_label": record["gold_label"],
            }

            try:
                row["prediction"], row["details"] = predict(
                    "components",
                    MODEL,
                    record["claim"],
                    record["source"] or "",
                )
            except ValueError as error:
                row.update(prediction=None, error=str(error))

            # Commit completed work before reporting progress.
            with db:
                db.execute(
                    "INSERT INTO rows VALUES (?, ?)",
                    (example_id, json.dumps(row)),
                )
            predictions.append(row)
            print(
                f"[{index}/{len(ids)}] {example_id}: {row['prediction']}",
                flush=True,
            )
    finally:
        db.close()

    report = {
        "method": "components_7b_fresh_original",
        "model": MODEL,
        "split": "dev",
        "dataset_version": "raw",
        "dataset_sha256": fingerprint,
        "example_ids": ids,
        "predictions": predictions,
    }
    report["metrics"] = evaluate(report)
    now = datetime.now(timezone.utc)
    report["created_at_utc"] = now.isoformat()
    stamp = now.strftime("%Y%m%dT%H%M%S_%fZ")
    output = FOLDER / f"components_fresh_original_{stamp}.json"

    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()