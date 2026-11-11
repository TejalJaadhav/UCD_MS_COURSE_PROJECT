"""Evaluate overall support predictions without dropping failed examples."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

LABELS = ("complete_support", "partial_support", "no_support")
ROOT = Path(__file__).resolve().parents[2]


def load_split(split, version="raw"):
    """Read compressed data and retain original IDs and gold labels."""
    if split not in {"train", "dev", "test"}:
        raise ValueError("Unknown split")
    if version not in {"raw", "cleaned"}:
        raise ValueError("Unknown dataset version")
    path = (ROOT / "data/raw" / f"verifiability_judgments_{split}.jsonl.gz"
            if version == "raw" else ROOT / "outputs/preprocessing/cleaned" / f"{split}.jsonl.gz")
    records = []
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            row = json.loads(line)
            raw_line = number if version == "raw" else row["raw_line_number"]
            label = row["source_supports_statement"] if version == "raw" else row["support_label"]
            if label not in LABELS:
                raise ValueError(f"Invalid gold label at {split}:{raw_line}")
            records.append({"example_id": f"{split}_{raw_line:05d}",
                            "gold_label": label, "claim": row["statement"],
                            "source": row["source_text"]})
    return records, hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(gold, predicted):
    """Count failures as misses and include all three classes in macro-F1."""
    if not gold or len(gold) != len(predicted):
        raise ValueError("Expected nonempty, equally sized labels")
    if any(x not in LABELS for x in gold):
        raise ValueError("Invalid gold label")
    if any(x not in LABELS and x is not None for x in predicted):
        raise ValueError("Invalid prediction; use null for an explicit failure")
    confusion = {label: {p: 0 for p in (*LABELS, "failed")} for label in LABELS}
    for actual, prediction in zip(gold, predicted):
        confusion[actual][prediction or "failed"] += 1
    per_class = {}
    for label in LABELS:
        tp = confusion[label][label]
        support = gold.count(label)
        predicted_count = predicted.count(label)
        precision = tp / predicted_count if predicted_count else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = dict(precision=precision, recall=recall, f1=f1, support=support)
    return {"count": len(gold), "failed": predicted.count(None),
            "coverage": sum(x is not None for x in predicted) / len(gold),
            "accuracy": sum(a == p for a, p in zip(gold, predicted)) / len(gold),
            "macro_f1": sum(x["f1"] for x in per_class.values()) / len(LABELS),
            "per_class": per_class, "confusion_matrix": confusion}


def evaluate(report):
    """Validate saved predictions against the exact dataset before scoring."""
    records, fingerprint = load_split(report["split"], report["dataset_version"])
    if fingerprint != report["dataset_sha256"]:
        raise ValueError("Dataset fingerprint differs from the prediction run")
    reference = {r["example_id"]: r for r in records}
    expected = report["example_ids"]
    if not expected or len(set(expected)) != len(expected):
        raise ValueError("Empty or duplicate evaluation IDs")
    rows = report["predictions"]
    by_id = {r["example_id"]: r for r in rows}
    if len(by_id) != len(rows) or set(by_id) != set(expected):
        raise ValueError("Missing, extra, or duplicate prediction rows")
    gold, predicted = [], []
    for key in expected:
        if key not in reference:
            raise ValueError(f"Unknown example: {key}")
        row = by_id[key]
        if row["gold_label"] != reference[key]["gold_label"]:
            raise ValueError(f"Gold label mismatch: {key}")
        gold.append(row["gold_label"])
        predicted.append(row["prediction"])
    return metrics(gold, predicted)


def main():
    """Print metrics for one saved run; never alter input data."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.run.read_text())), indent=2))


if __name__ == "__main__":
    main()
