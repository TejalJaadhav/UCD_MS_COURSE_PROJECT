"""Create a balanced dev worksheet for manual claim-component annotation."""

import gzip
import json
import random
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEV_FILE = PROJECT_ROOT / "data/raw/verifiability_judgments_dev.jsonl.gz"
OUTPUT_FILE = PROJECT_ROOT / "outputs/annotation_pilot/dev_annotation_pilot.csv"
GOLD_LABELS = ("complete_support", "partial_support", "no_support")
SAMPLE_PER_LABEL = 5
RANDOM_SEED = 42


def main():
    """Sample five original dev examples per label and write a CSV worksheet."""
    examples_by_label = {label: [] for label in GOLD_LABELS}

    with gzip.open(DEV_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            example = json.loads(line)
            label = example["source_supports_statement"]
            examples_by_label[label].append((line_number, example))

    random_generator = random.Random(RANDOM_SEED)
    selected = []

    for label in GOLD_LABELS:
        selected.extend(
            random_generator.sample(
                examples_by_label[label],
                SAMPLE_PER_LABEL,
            )
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "original_split",
        "original_line_number",
        "gold_dataset_label",
        "statement",
        "source_text",
        "source_localized_evidence",
        "claim_parts",
        "component_labels",
        "reasoning_notes",
        "uncertainty_or_disagreement",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for line_number, example in selected:
            writer.writerow(
                {
                    "original_split": "dev",
                    "original_line_number": line_number,
                    "gold_dataset_label": example[
                        "source_supports_statement"
                    ],
                    "statement": example["statement"],
                    "source_text": example["source_text"],
                    "source_localized_evidence": example.get(
                        "source_localized_evidence"
                    )
                    or "",
                    "claim_parts": "",
                    "component_labels": "",
                    "reasoning_notes": "",
                    "uncertainty_or_disagreement": "",
                }
            )

    print(f"Created worksheet with {len(selected)} examples:")
    print(OUTPUT_FILE)
    for label in GOLD_LABELS:
        print(f"{label}: {SAMPLE_PER_LABEL}")


if __name__ == "__main__":
    main()
