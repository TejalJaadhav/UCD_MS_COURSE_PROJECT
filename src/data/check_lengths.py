"""
check_lengths.py

Purpose:
    Measure how long the training claims and source texts are.

Why this matters:
    Long sources may need special handling before a model can
    read them. We should understand their lengths first.

These are approximate word counts, not model token counts.

Run:
    python -m src.data.check_lengths
"""

import gzip
import json
from pathlib import Path
from statistics import mean, median


# Find the repository and the training dataset.
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


def show_summary(title, lengths):
    """Print the shortest, average, middle, and longest lengths."""

    print(f"\n{title}")
    print(f"  Shortest: {min(lengths):,} words")
    print(f"  Average: {mean(lengths):,.1f} words")

    # The median is the middle value after sorting the lengths.
    print(f"  Median: {median(lengths):,.1f} words")
    print(f"  Longest: {max(lengths):,} words")


def main():
    """Collect word counts from each training record."""

    claim_lengths = []
    source_lengths = []

    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            claim_lengths.append(count_words(record["statement"]))
            source_lengths.append(count_words(record["source_text"]))

    # Avoid calculating statistics if the dataset is empty.
    if not claim_lengths:
        print("No training records were found.")
        return

    print(f"Training records checked: {len(claim_lengths):,}")

    show_summary("CLAIM LENGTHS", claim_lengths)
    show_summary("SOURCE LENGTHS", source_lengths)

    # These thresholds describe the data.
    # They are not model limits or rules for cutting text.
    
        # Count very short sources to understand how common they are.
    # These thresholds are for inspection only, not automatic removal.
    print("\nRECORDS WITH SHORT SOURCES")

    for threshold in (5, 10, 20, 50):
        count = sum(length <= threshold for length in source_lengths)
        percentage = count / len(source_lengths) * 100

        print(
            f"  At most {threshold} words: "
            f"{count:,} records ({percentage:.1f}%)"
        )
        
    print("\nRECORDS WITH LONG SOURCES")
    for threshold in (500, 1000, 2000, 5000):
        count = sum(length > threshold for length in source_lengths)
        percentage = count / len(source_lengths) * 100

        print(
            f"  Over {threshold:,} words: "
            f"{count:,} records ({percentage:.1f}%)"
        )


# Run the analysis when this module is executed.
if __name__ == "__main__":
    main()