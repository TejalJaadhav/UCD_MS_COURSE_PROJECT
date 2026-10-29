"""
evaluate_nli_dev_sample.py

Purpose:
    Try the NLI section-scoring rule on a small sample of development data.

It selects 10 examples from each dataset label, checks every source
section against the whole claim, and saves the scores.

This is an early check, not the final result for the project.

Run:
    python -m src.baselines.evaluate_nli_dev_sample
"""

import gzip
import json
import random
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.data.split_source import MODEL_NAME, split_into_sections


# Find the development dataset and output folder.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEV_FILE = PROJECT_ROOT / "data" / "raw" / "verifiability_judgments_dev.jsonl.gz"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Use the model's label order.
NLI_LABELS = ("contradiction", "entailment", "neutral")

# Pick the same number from each original dataset label.
DATASET_LABELS = ("complete_support", "partial_support", "no_support")
EXAMPLES_PER_LABEL = 10
RANDOM_SEED = 42
BATCH_SIZE = 8
INPUT_LIMIT = 512


def load_sample():
    """Choose a repeatable sample from the development split."""

    records_by_label = {label: [] for label in DATASET_LABELS}

    with gzip.open(DEV_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            label = record["source_supports_statement"]

            if label in records_by_label:
                records_by_label[label].append({
                    "line_number": line_number,
                    "record": record,
                })

    # Use a fixed seed so we get the same sample every time.
    randomizer = random.Random(RANDOM_SEED)
    sample = []

    for label in DATASET_LABELS:
        available = records_by_label[label]
        count = min(EXAMPLES_PER_LABEL, len(available))
        sample.extend(randomizer.sample(available, count))

    return sample


def main():
    """Score all sections and report a preliminary two-group result."""

    print(f"Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    sample = load_sample()
    section_pairs = []
    results = []

    # Split each selected source and prepare its sections for scoring.
    for item in sample:
        record = item["record"]
        title = record.get("source_title") or record.get("source_content_title") or ""
        claim = record["statement"]

        _, sections = split_into_sections(record["source_text"], tokenizer)
        result = {
            "dev_line": item["line_number"],
            "dataset_label": record["source_supports_statement"],
            "claim": claim,
            "source_title": title,
            "sections": [],
        }
        results.append(result)

        for section_number, section in enumerate(sections, start=1):
            evidence = f"Title: {title}\nText: {section}"

            # Count tokens before scoring; do not cut off the claim or evidence.
            encoded = tokenizer(
                evidence,
                claim,
                add_special_tokens=True,
                truncation=False,
            )
            token_count = len(encoded["input_ids"])

            if token_count > INPUT_LIMIT:
                raise ValueError(
                    f"Development line {item['line_number']}, section "
                    f"{section_number} has {token_count} tokens. "
                    f"The limit is {INPUT_LIMIT}."
                )

            section_pairs.append({
                "result": result,
                "section_number": section_number,
                "section_text": section,
                "evidence": evidence,
                "claim": claim,
                "token_count": token_count,
            })

    # Score section pairs in small batches.
    for start in range(0, len(section_pairs), BATCH_SIZE):
        batch = section_pairs[start:start + BATCH_SIZE]

        inputs = tokenizer(
            [pair["evidence"] for pair in batch],
            [pair["claim"] for pair in batch],
            padding=True,
            truncation=False,
            return_tensors="pt",
        )

        with torch.no_grad():
            logits = model(**inputs).logits
            batch_scores = torch.softmax(logits, dim=1)

        for pair, scores in zip(batch, batch_scores):
            score_values = {
                label: float(score)
                for label, score in zip(NLI_LABELS, scores)
            }
            predicted_relation = max(score_values, key=score_values.get)

            pair["result"]["sections"].append({
                "section_number": pair["section_number"],
                "input_tokens": pair["token_count"],
                "predicted_relation": predicted_relation,
                "scores": score_values,
                "section_text": pair["section_text"],
            })

    # Apply our first rule to each example.
    for result in results:
        result["gold_binary"] = (
            "fully_supported"
            if result["dataset_label"] == "complete_support"
            else "not_fully_supported"
        )
        result["predicted_binary"] = (
            "fully_supported"
            if any(
                section["predicted_relation"] == "entailment"
                for section in result["sections"]
            )
            else "not_fully_supported"
        )

    # Count correct predictions and calculate simple two-group metrics.
    binary_labels = ("fully_supported", "not_fully_supported")
    total = len(results)
    correct = sum(
        result["gold_binary"] == result["predicted_binary"]
        for result in results
    )

    f1_scores = []
    print(f"\nExamples checked: {total}")
    print(f"Accuracy: {correct / total:.4f}")

    print("\nPER-GROUP RESULTS")
    for label in binary_labels:
        true_positive = sum(
            r["gold_binary"] == label and r["predicted_binary"] == label
            for r in results
        )
        false_positive = sum(
            r["gold_binary"] != label and r["predicted_binary"] == label
            for r in results
        )
        false_negative = sum(
            r["gold_binary"] == label and r["predicted_binary"] != label
            for r in results
        )

        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )
        f1_scores.append(f1)

        print(
            f"  {label}: precision={precision:.4f}, "
            f"recall={recall:.4f}, F1={f1:.4f}"
        )

    print(f"Macro-F1: {sum(f1_scores) / len(f1_scores):.4f}")

    # Save the selected examples and every section score for review.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "nli_dev_sample.json"
    output_file.write_text(
        json.dumps(
            {
                "model": MODEL_NAME,
                "random_seed": RANDOM_SEED,
                "examples_per_dataset_label": EXAMPLES_PER_LABEL,
                "results": results,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"\nSaved detailed scores to: {output_file}")


if __name__ == "__main__":
    main()