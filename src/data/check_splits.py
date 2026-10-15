"""
check_splits.py

Purpose:
    Check whether the same question appears in more than one
    dataset split.

Why this matters:
    Questions used during development should stay separate
    from questions used for final testing.

This checks exact question text only. It does not detect
differently worded versions of the same question.

The dataset files are not changed.

Run:
    python -m src.data.check_splits
"""

import gzip
import json
from pathlib import Path


# Locate the folder containing the original dataset files.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_questions(split):
    """Collect the unique questions from one dataset split."""

    file_path = DATA_DIR / f"verifiability_judgments_{split}.jsonl.gz"

    # A set stores each question only once.
    questions = set()

    with gzip.open(file_path, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)
            question = record.get("query")

            # Stop if a question is missing instead of silently skipping it.
            if not isinstance(question, str) or not question.strip():
                raise ValueError(
                    f"{split}, line {line_number}: missing or blank question"
                )

            questions.add(question)

    return questions


def main():
    """Print unique question counts and overlap between splits."""

    questions = {
        split: load_questions(split)
        for split in ("train", "dev", "test")
    }

    print("UNIQUE QUESTIONS")
    for split, values in questions.items():
        print(f"  {split}: {len(values):,}")

    print("\nQUESTIONS SHARED BETWEEN SPLITS")

    # The & operator finds questions present in both sets.
    for first, second in (
        ("train", "dev"),
        ("train", "test"),
        ("dev", "test"),
    ):
        shared = questions[first] & questions[second]
        print(f"  {first} / {second}: {len(shared):,}")


# Run the checks when this module is executed.
if __name__ == "__main__":
    main()