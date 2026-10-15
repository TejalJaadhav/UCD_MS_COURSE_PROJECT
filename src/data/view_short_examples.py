"""
view_short_examples.py

Purpose:
    Inspect unusually short claims and sources in the training data.

Why this matters:
    Short text may be valid, or it may indicate missing content.
    We need to read the examples before deciding what to do.

The script does not remove or change any records.

Run:
    python -m src.data.view_short_examples
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


def count_words(text):
    """Estimate word count by splitting text at whitespace."""
    return len(text.split())


def show_example(line_number, record):
    """Display the information needed to review one example."""

    print("\n" + "=" * 60)
    print(f"Training file line: {line_number}")
    print(f"Label: {record['source_supports_statement']}")

    print("\nQUESTION")
    print(record["query"])

    # The full response helps explain very short claims.
    print("\nFULL AI RESPONSE")
    print(record["response"])

    print("\nCLAIM")
    print(record["statement"])

    source = record["source_text"]
    print(f"\nSOURCE — {count_words(source):,} words")

    # Show short sources completely. Limit long sources for readability.
    print(source[:2000])
    if len(source) > 2000:
        print("[Preview only: remaining source text is not shown.]")

    print("\nHUMAN-SELECTED EVIDENCE")
    print(record.get("source_localized_evidence") or "Not provided.")

    print("\nSOURCE URL")
    print(record.get("source_url") or "Not provided.")


def main():
    """Find and display the shortest training examples."""

    records = []

    # Keep the original line number so each example can be found again.
    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip():
                records.append((line_number, json.loads(line)))

    # Sort independently by claim length and source length.
    shortest_claims = sorted(
        records,
        key=lambda item: count_words(item[1]["statement"]),
    )[:3]

    shortest_sources = sorted(
        records,
        key=lambda item: count_words(item[1]["source_text"]),
    )[:3]

    print("THREE SHORTEST CLAIMS")
    for line_number, record in shortest_claims:
        show_example(line_number, record)

    print("\nTHREE SHORTEST SOURCES")
    for line_number, record in shortest_sources:
        show_example(line_number, record)


# Run the review when this module is executed.
if __name__ == "__main__":
    main()