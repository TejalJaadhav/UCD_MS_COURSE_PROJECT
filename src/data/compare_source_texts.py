"""
compare_source_texts.py

Purpose:
    Compare two source-text fields for three training records
    that appeared to contain too little information.

Fields:
    source_text: Extracted source text with formatting.
    source_raw_text: Extracted source text without formatting.
                     This is not the original webpage HTML.

We check both fields before deciding how to handle these records.
No data or labels are changed.

Run:
    python -m src.data.compare_source_texts
"""

import gzip
import json
from pathlib import Path


# Locate the original training file.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "verifiability_judgments_train.jsonl.gz"
)

# These line numbers came from our review of the shortest sources.
REVIEW_LINES = {4230, 4233, 6026}


def show_text(field_name, value):
    """Display the full text and its approximate word count."""

    print(f"\n{field_name.upper()}")

    # Handle missing, blank, or unexpected values clearly.
    if not isinstance(value, str) or not value.strip():
        print("Missing, blank, or not a text value.")
        return

    print(f"Word count: {len(value.split()):,}")
    print(value)


def main():
    """Compare both source fields for the selected records."""

    found_lines = set()

    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            # Read only the records selected for review.
            if line_number not in REVIEW_LINES:
                continue

            record = json.loads(line)
            found_lines.add(line_number)

            print("\n" + "=" * 60)
            print(f"TRAINING FILE LINE: {line_number}")

            print("\nCLAIM")
            print(record["statement"])

            print("\nDATASET LABEL")
            print(record["source_supports_statement"])

            # Display both fields without cutting off their contents.
            show_text("source_text", record.get("source_text"))
            show_text("source_raw_text", record.get("source_raw_text"))

            print("\nHUMAN-SELECTED EVIDENCE")
            print(record.get("source_localized_evidence") or "Not provided.")

            print("\nSOURCE URL")
            print(record.get("source_url") or "Not provided.")

            # Stop after finding all three selected records.
            if found_lines == REVIEW_LINES:
                break

    # Report if the file did not contain an expected line.
    missing_lines = REVIEW_LINES - found_lines
    if missing_lines:
        print(f"\nReview lines not found: {sorted(missing_lines)}")


# Run the comparison when this module is executed.
if __name__ == "__main__":
    main()