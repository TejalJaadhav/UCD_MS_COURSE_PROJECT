"""
check_source_title.py

Purpose:
    Check whether the saved source titles identify the show
    mentioned in training record 2050.

The source text says "6 Seasons" but does not name the show.
We inspect the titles to see whether they provide that context.

This script does not change any data.

Run:
    python -m src.data.check_source_title
"""

import gzip
import json
from pathlib import Path


# Locate the training dataset.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "verifiability_judgments_train.jsonl.gz"
)

# The record selected during our short-source review.
REVIEW_LINE = 2050


def main():
    """Display the selected record's claim, titles, and source text."""

    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line_number != REVIEW_LINE:
                continue

            record = json.loads(line)

            # Show the claim we want to evaluate.
            print("CLAIM")
            print(record["statement"])

            # These titles come from the cited webpage.
            print("\nSOURCE TITLE")
            print(record.get("source_title") or "Not provided.")

            print("\nSOURCE CONTENT TITLE")
            print(record.get("source_content_title") or "Not provided.")

            print("\nSOURCE TEXT")
            print(record["source_text"])

            return

    print(f"Training line {REVIEW_LINE} was not found.")


if __name__ == "__main__":
    main()