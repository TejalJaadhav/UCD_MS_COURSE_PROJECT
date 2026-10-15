"""
check_dataset.py

Purpose:
    Check the dataset for missing claims, missing source text,
    and unexpected support labels.

    Also count missing human-selected evidence. This field is
    optional, so missing evidence is not automatically an error.

The script only reads the data. It does not change any files.

Run from the repository's main folder:
    python -m src.data.check_dataset
"""

import gzip
import json
from pathlib import Path


# Find the repository root and the folder holding the dataset.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

# These are the labels allowed in this dataset.
VALID_LABELS = {
    "complete_support",
    "partial_support",
    "no_support",
}


def has_text(value):
    """Check that a value contains text, rather than being empty."""
    return isinstance(value, str) and bool(value.strip())


def main():
    """Check each dataset split and print the results."""

    for split in ("train", "dev", "test"):
        file_path = DATA_DIR / f"verifiability_judgments_{split}.jsonl.gz"

        # Reset the counts before checking each split.
        total = 0
        missing_claims = 0
        missing_sources = 0
        invalid_labels = 0
        missing_evidence = 0

        # Read the compressed file one record at a time.
        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                record = json.loads(line)
                total += 1

                # Check the claim and source text needed by our models.
                if not has_text(record.get("statement")):
                    missing_claims += 1

                if not has_text(record.get("source_text")):
                    missing_sources += 1

                # Count missing labels and labels outside the allowed set.
                if record.get("source_supports_statement") not in VALID_LABELS:
                    invalid_labels += 1

                # Count optional evidence separately.
                if not has_text(record.get("source_localized_evidence")):
                    missing_evidence += 1

        # Display a summary without printing individual examples.
        print(f"\n{split.upper()}: {total:,} records")
        print(f"  Missing or blank claims: {missing_claims:,}")
        print(f"  Missing or blank source text: {missing_sources:,}")
        print(f"  Missing or invalid labels: {invalid_labels:,}")
        print(f"  Missing optional evidence: {missing_evidence:,}")


# Start the checks when this file is run.
if __name__ == "__main__":
    main()