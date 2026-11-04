"""Evaluate a training-majority baseline on the original dev split."""

import gzip
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data/raw"
LABELS = ("complete_support", "partial_support", "no_support")


def load_labels(split):
    """Read gold labels without modifying the compressed dataset."""
    path = RAW_DIR / f"verifiability_judgments_{split}.jsonl.gz"

    with gzip.open(path, "rt", encoding="utf-8") as file:
        labels = [
            json.loads(line)["source_supports_statement"]
            for line in file
        ]

    if not labels or not set(labels).issubset(LABELS):
        raise ValueError(f"Empty split or unexpected labels in {split}")

    return labels


def main():
    """Select a label from train, then evaluate constant predictions on dev."""
    train_labels = load_labels("train")
    dev_labels = load_labels("dev")

    # Choose the prediction using training data only.
    train_counts = Counter(train_labels)
    majority_label = train_counts.most_common(1)[0][0]
    predictions = [majority_label] * len(dev_labels)

    accuracy = sum(
        gold == predicted
        for gold, predicted in zip(dev_labels, predictions)
    ) / len(dev_labels)

    print(f"Baseline prediction: {majority_label}")
    print(f"Dev records: {len(dev_labels)}")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nLabel                 Precision  Recall     F1       Count")

    f1_scores = []

    for label in LABELS:
        true_positive = sum(
            gold == label and predicted == label
            for gold, predicted in zip(dev_labels, predictions)
        )
        predicted_count = predictions.count(label)
        gold_count = dev_labels.count(label)

        # Use zero when a metric's denominator is zero.
        precision = (
            true_positive / predicted_count if predicted_count else 0.0
        )
        recall = true_positive / gold_count if gold_count else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )
        f1_scores.append(f1)

        print(
            f"{label:<22}{precision:<11.4f}{recall:<11.4f}"
            f"{f1:<9.4f}{gold_count}"
        )

    # Give each label equal weight, regardless of its frequency.
    macro_f1 = sum(f1_scores) / len(LABELS)
    print(f"\nMacro-F1: {macro_f1:.4f}")


if __name__ == "__main__":
    main()