"""
majority_baseline.py

Purpose:
    Establish a simple starting score for later models to beat.

Steps:
    1. Find the most common label in the training data.
    2. Predict that label for every development example.
    3. Calculate accuracy and per-class precision, recall, and F1.
    4. Calculate macro-F1, which gives each class equal weight.

This baseline does not read claims or evidence.
It does not use the test set or change dataset files.

Run:
    python -m src.baselines.majority_baseline
"""

import gzip
import json
from collections import Counter
from pathlib import Path


# Locate the original dataset files.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

LABELS = ("complete_support", "partial_support", "no_support")


def load_labels(split):
    """Read the human-assigned labels from one dataset split."""

    file_path = DATA_DIR / f"verifiability_judgments_{split}.jsonl.gz"
    labels = []

    with gzip.open(file_path, "rt", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)
            label = record["source_supports_statement"]

            # Stop if the data contains an unexpected label.
            if label not in LABELS:
                raise ValueError(f"Unexpected label: {label}")

            labels.append(label)

    if not labels:
        raise ValueError(f"The {split} split contains no records.")

    return labels


def safe_divide(numerator, denominator):
    """Return zero when a metric's denominator is zero."""
    return numerator / denominator if denominator else 0.0


def main():
    """Choose a label using training data and evaluate on development data."""

    train_labels = load_labels("train")
    dev_labels = load_labels("dev")

    # Choose the prediction using training labels only.
    majority_label = Counter(train_labels).most_common(1)[0][0]

    # Every development example receives the same prediction.
    predictions = [majority_label] * len(dev_labels)

    correct = sum(
        actual == predicted
        for actual, predicted in zip(dev_labels, predictions)
    )
    accuracy = correct / len(dev_labels)

    print(f"Predicted label: {majority_label}")
    print(f"Development examples: {len(dev_labels):,}")
    print(f"Accuracy: {accuracy:.4f} ({accuracy:.1%})")

    print("\nPER-CLASS RESULTS")
    print(f"{'Label':<20} {'Precision':>10} {'Recall':>10} {'F1':>10}")

    f1_scores = []

    for label in LABELS:
        # True positive: this label was predicted and is correct.
        true_positive = sum(
            actual == label and predicted == label
            for actual, predicted in zip(dev_labels, predictions)
        )

        # False positive: this label was predicted but is incorrect.
        false_positive = sum(
            actual != label and predicted == label
            for actual, predicted in zip(dev_labels, predictions)
        )

        # False negative: this was the correct label but was not predicted.
        false_negative = sum(
            actual == label and predicted != label
            for actual, predicted in zip(dev_labels, predictions)
        )

        precision = safe_divide(
            true_positive, true_positive + false_positive
        )
        recall = safe_divide(
            true_positive, true_positive + false_negative
        )
        f1 = safe_divide(2 * precision * recall, precision + recall)

        f1_scores.append(f1)
        print(f"{label:<20} {precision:>10.4f} {recall:>10.4f} {f1:>10.4f}")

    # Macro-F1 averages the three class F1 scores equally.
    macro_f1 = sum(f1_scores) / len(LABELS)
    print(f"\nMacro-F1: {macro_f1:.4f}")


if __name__ == "__main__":
    main()