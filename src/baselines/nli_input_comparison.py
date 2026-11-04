"""Compare NLI input methods on a balanced sample of dev examples."""

import gzip
import json
import random
from collections import Counter
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEV_FILE = PROJECT_ROOT / "data/raw/verifiability_judgments_dev.jsonl.gz"
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
LABELS = ["contradiction", "entailment", "neutral"]
GOLD_LABELS = ["complete_support", "partial_support", "no_support"]
SAMPLE_PER_LABEL = 5
RANDOM_SEED = 42


def load_balanced_sample():
    """Choose five dev records from each original gold label."""
    by_label = {label: [] for label in GOLD_LABELS}

    with gzip.open(DEV_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            example = json.loads(line)
            label = example["source_supports_statement"]
            by_label[label].append((line_number, example))

    random_generator = random.Random(RANDOM_SEED)
    sample = []

    for label in GOLD_LABELS:
        if len(by_label[label]) < SAMPLE_PER_LABEL:
            raise ValueError(f"Not enough dev examples for {label}")

        sample.extend(
            random_generator.sample(by_label[label], SAMPLE_PER_LABEL)
        )

    return sample


def score_pair(tokenizer, model, source, claim):
    """Return the NLI prediction, class scores, and input length."""
    inputs = tokenizer(
        source,
        claim,
        truncation="only_first",
        max_length=512,
        return_tensors="pt",
    )

    with torch.inference_mode():
        probabilities = model(**inputs).logits[0].softmax(dim=-1)

    prediction = LABELS[probabilities.argmax().item()]
    return prediction, probabilities.tolist(), inputs["input_ids"].shape[1]


def main():
    """Score the balanced sample using full sources and available evidence."""
    sample = load_balanced_sample()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    # Count model predictions separately for each gold label and input type.
    full_source_predictions = Counter()
    evidence_predictions = Counter()

    print(f"Sample size: {len(sample)}")
    print(f"Examples per gold label: {SAMPLE_PER_LABEL}")
    print(f"Random seed: {RANDOM_SEED}")

    for line_number, example in sample:
        claim = example["statement"]
        gold_label = example["source_supports_statement"]
        source_text = example["source_text"]

        source_prediction, source_scores, source_tokens = score_pair(
            tokenizer, model, source_text, claim
        )
        full_source_predictions[(gold_label, source_prediction)] += 1

        print(f"\nOriginal dev line: {line_number}")
        print(f"Gold label: {gold_label}")
        print(f"Statement: {claim}")
        print(f"Full-source prediction: {source_prediction}")
        print(f"Full-source input tokens: {source_tokens}")
        print(
            "Full-source scores:",
            dict(zip(LABELS, (round(score, 4) for score in source_scores))),
        )

        evidence = example.get("source_localized_evidence")
        if evidence:
            evidence_prediction, evidence_scores, evidence_tokens = score_pair(
                tokenizer, model, evidence, claim
            )
            evidence_predictions[(gold_label, evidence_prediction)] += 1

            print(f"Localized evidence: {evidence}")
            print(f"Evidence prediction: {evidence_prediction}")
            print(f"Evidence input tokens: {evidence_tokens}")
            print(
                "Evidence scores:",
                dict(
                    zip(
                        LABELS,
                        (round(score, 4) for score in evidence_scores),
                    )
                ),
            )
        else:
            print("Localized evidence: unavailable")

    print("\nFull-source NLI prediction counts by gold label:")
    for gold_label in GOLD_LABELS:
        counts = {
            prediction: full_source_predictions[(gold_label, prediction)]
            for prediction in LABELS
        }
        print(f"{gold_label}: {counts}")

    print("\nLocalized-evidence NLI prediction counts by gold label:")
    for gold_label in GOLD_LABELS:
        counts = {
            prediction: evidence_predictions[(gold_label, prediction)]
            for prediction in LABELS
        }
        print(f"{gold_label}: {counts}")


if __name__ == "__main__":
    main()