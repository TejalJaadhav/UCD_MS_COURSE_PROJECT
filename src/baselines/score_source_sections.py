"""
score_source_sections.py

Purpose:
    Run the NLI model on each section of one source and save its scores.

This checks the section scoring and saving steps on one training
example. It does not measure model performance.

Run:
    python -m src.baselines.score_source_sections
"""

import gzip
import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.data.split_source import MODEL_NAME, split_into_sections


# Check the first record in the training file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_FILE = (
    PROJECT_ROOT / "data" / "raw"
    / "verifiability_judgments_train.jsonl.gz"
)
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# The score order for this model.
NLI_LABELS = ("contradiction", "entailment", "neutral")
RECORD_LINE = 1
INPUT_LIMIT = 512


def load_record():
    """Read the selected training record."""
    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line_number == RECORD_LINE and line.strip():
                return json.loads(line)

    raise ValueError(f"Training record line {RECORD_LINE} was not found.")


def main():
    """Score each source section and save all section results."""

    record = load_record()
    title = record.get("source_title") or record.get("source_content_title") or ""
    claim = record["statement"]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    # Split the source using the sectioning rule we agreed on.
    _, sections = split_into_sections(record["source_text"], tokenizer)
    section_results = []

    for section_number, section in enumerate(sections, start=1):
        evidence = f"Title: {title}\nText: {section}"

        # Keep the full claim and section. Do not silently cut either one.
        inputs = tokenizer(
            evidence,
            claim,
            return_tensors="pt",
            truncation=False,
        )

        token_count = inputs["input_ids"].shape[1]
        if token_count > INPUT_LIMIT:
            raise ValueError(
                f"Section {section_number} uses {token_count} tokens, "
                f"over the {INPUT_LIMIT}-token limit."
            )

        # Get the model's three scores for this section.
        with torch.no_grad():
            logits = model(**inputs).logits[0]
            scores = torch.softmax(logits, dim=0)

        score_values = {
            label: float(score)
            for label, score in zip(NLI_LABELS, scores)
        }
        section_prediction = max(score_values, key=score_values.get)

        section_results.append({
            "section_number": section_number,
            "input_tokens": token_count,
            "predicted_relation": section_prediction,
            "scores": score_values,
            "section_text": section,
        })

        print(
            f"Section {section_number}/{len(sections)}: "
            f"{section_prediction}; scores={score_values}"
        )

    # Apply our first rule: any entailing section means fully supported.
    overall_prediction = (
        "fully_supported"
        if any(
            result["predicted_relation"] == "entailment"
            for result in section_results
        )
        else "not_fully_supported"
    )

    # Save the example and every section's scores for later review.
    output = {
        "model": MODEL_NAME,
        "split": "train",
        "record_line": RECORD_LINE,
        "dataset_label": record["source_supports_statement"],
        "claim": claim,
        "source_title": title,
        "overall_prediction": overall_prediction,
        "sections": section_results,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"nli_train_line_{RECORD_LINE}.json"
    output_file.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print(f"\nOverall prediction: {overall_prediction}")
    print(f"Saved section scores to: {output_file}")


if __name__ == "__main__":
    main()