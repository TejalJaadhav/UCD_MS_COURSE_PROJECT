"""
review_short_sources.py

Purpose:
    Display training records whose saved source text contains
    10 words or fewer.

Why this matters:
    We need to read these records before deciding whether their
    source text contains enough information to assess the claim.

Short text is a reason for review, not automatic removal.
This script does not change any data or labels.

Run:
    python -m src.data.review_short_sources
"""

import gzip
import json
from pathlib import Path


# Locate the original training dataset.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "verifiability_judgments_train.jsonl.gz"
)

# Review sources with this many words or fewer.
MAX_SOURCE_WORDS = 10


def main():
    """Display every training record that meets the review threshold."""

    reviewed_count = 0

    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            source_text = record["source_text"]
            word_count = len(source_text.split())

            # Skip sources that are longer than our review threshold.
            if word_count > MAX_SOURCE_WORDS:
                continue

            reviewed_count += 1

            # Keep the original line number so we can find this record again.
            print("\n" + "=" * 60)
            print(f"TRAINING FILE LINE: {line_number}")
            print(f"SOURCE WORD COUNT: {word_count}")

            print("\nQUESTION")
            print(record["query"])

            # Context helps explain claims that are fragments or list items.
            print("\nFULL AI RESPONSE")
            print(record["response"])

            print("\nCLAIM")
            print(record["statement"])

            print("\nDATASET LABEL")
            print(record["source_supports_statement"])

            print("\nSOURCE TEXT")
            print(source_text)

            # Compare the alternative text field for additional information.
            print("\nSOURCE RAW TEXT")
            print(record.get("source_raw_text") or "Not provided.")

            # This passage is a human annotation, not a substitute source.
            print("\nHUMAN-SELECTED EVIDENCE")
            print(record.get("source_localized_evidence") or "Not provided.")

            print("\nSOURCE URL")
            print(record.get("source_url") or "Not provided.")

    print(f"\nTotal records displayed: {reviewed_count}")


# Start the review when this module is executed.
if __name__ == "__main__":
    main()