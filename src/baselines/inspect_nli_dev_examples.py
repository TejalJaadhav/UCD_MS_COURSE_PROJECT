"""
inspect_nli_dev_examples.py

Purpose:
    Try the NLI model on one real development example from each
    support label.

The examples are chosen so their source text fits the model.
This is only a small check; it does not measure overall performance.

The script does not use human-selected evidence or change the data.

Run:
    python -m src.baselines.inspect_nli_dev_examples
"""

import gzip
import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# Use the small NLI model we tested.
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"

# Find the development data file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEV_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "verifiability_judgments_dev.jsonl.gz"
)

# These are the labels used in the dataset.
DATASET_LABELS = (
    "complete_support",
    "partial_support",
    "no_support",
)

# This is the model's score order from its model card.
NLI_LABELS = ("contradiction", "entailment", "neutral")


def main():
    """Find and score one short development example per dataset label."""

    print(f"Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    # Store at most one suitable example for each dataset label.
    selected = {}

    # Read development examples only. Do not use the test split here.
    with gzip.open(DEV_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            dataset_label = record["source_supports_statement"]

            # Skip labels for which we already found an example.
            if dataset_label in selected:
                continue

            source_text = record.get("source_text") or ""
            source_title = (
                record.get("source_title")
                or record.get("source_content_title")
                or ""
            )

            # Skip very short source text for this small demonstration.
            # Short sources need a separate review.
            if len(source_text.split()) < 50:
                continue

            # Give the model the source title and full saved source text.
            evidence = f"Title: {source_title}\nText: {source_text}"
            claim = record["statement"]

            # Check the full text pair length before sending it to the model.
            inputs = tokenizer(
                evidence,
                claim,
                return_tensors="pt",
                truncation=False,
            )

            # Keep only examples that fit without cutting off text.
            if inputs["input_ids"].shape[1] > 512:
                continue

            selected[dataset_label] = {
                "line_number": line_number,
                "claim": claim,
                "evidence": evidence,
                "inputs": inputs,
            }

            # Stop once we have one example for each dataset label.
            if len(selected) == len(DATASET_LABELS):
                break

    # Score each selected example and print the result.
    for dataset_label in DATASET_LABELS:
        example = selected.get(dataset_label)

        if example is None:
            print(f"\nNo suitable short example found for {dataset_label}.")
            continue

        with torch.no_grad():
            logits = model(**example["inputs"]).logits[0]
            scores = torch.softmax(logits, dim=0)

        print("\n" + "=" * 50)
        print(f"Development file line: {example['line_number']}")
        print(f"Dataset label: {dataset_label}")
        print(f"Claim: {example['claim']}")
        print("NLI scores:")

        for label, score in zip(NLI_LABELS, scores):
            print(f"  {label}: {score.item():.4f}")


if __name__ == "__main__":
    main()