"""Save reproducible majority-baseline predictions and overall metrics."""

import argparse
import json
from collections import Counter
from datetime import datetime, timezone

from src.evaluation.overall import ROOT, evaluate, load_split


def main():
    """Choose a label from train only, then predict the requested split."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--dataset-version", choices=["raw", "cleaned"], default="raw")
    args = parser.parse_args()
    train, train_hash = load_split("train", args.dataset_version)
    records, data_hash = load_split(args.split, args.dataset_version)
    label = Counter(r["gold_label"] for r in train).most_common(1)[0][0]
    report = {"method": "majority", "split": args.split,
              "dataset_version": args.dataset_version,
              "dataset_sha256": data_hash, "train_sha256": train_hash,
              "example_ids": [r["example_id"] for r in records],
              "prediction_label": label,
              "predictions": [{"example_id": r["example_id"],
                               "gold_label": r["gold_label"], "prediction": label}
                              for r in records]}
    report["metrics"] = evaluate(report)
    now = datetime.now(timezone.utc)
    report["created_at_utc"] = now.isoformat()
    folder = ROOT / "outputs/annotation_pilot/evaluation"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"majority_{args.split}_{now.strftime('%Y%m%dT%H%M%S_%fZ')}.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(f"Saved: {path}")
    print(f"Examples: {report['metrics']['count']}")
    print(f"Accuracy: {report['metrics']['accuracy']:.4f}")
    print(f"Macro-F1: {report['metrics']['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
