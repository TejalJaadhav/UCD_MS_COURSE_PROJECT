"""
This The script displays the claim, full AI response, cited source,
and human annotation. It does not change the dataset.

Example command:
    python -m src.data.view_example --label partial_support
    
"""

import argparse # To read options supplied in the terminal command.
import gzip
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "verifiability_judgments_train.jsonl.gz"
)


def main():
    """Find and display the first example with the requested label."""

    # Allow the user to choose a label without changing the code.
    parser = argparse.ArgumentParser(
        description="View one training example by support label."
    )
    parser.add_argument(
        "--label",
        choices=["complete_support", "partial_support", "no_support"],
        default="partial_support",
        help="Label to inspect. Default: partial_support.",
    )
    args = parser.parse_args()

    # Read records one at a time until a matching example is found.
    example = None
    record_line = None

    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            record = json.loads(line)

            if record["source_supports_statement"] == args.label:
                example = record
                record_line = line_number
                break

    # Stop with a clear message if no matching record exists.
    if example is None:
        print(f"No example found with label: {args.label}")
        return

    # Record the location so we can find this example again.
    print(f"TRAINING FILE LINE: {record_line}")

    # Display the surrounding context before the individual claim.
    print("\nORIGINAL QUESTION")
    print(example["query"])

    print("\nFULL AI-GENERATED RESPONSE")
    print(example["response"])

    print("\nAI-GENERATED STATEMENT")
    print(example["statement"])

    print("\nHUMAN SUPPORT LABEL")
    print(example["source_supports_statement"])

    # Human-selected evidence is optional and may be missing.
    print("\nHUMAN-SELECTED EVIDENCE")
    print(example.get("source_localized_evidence") or "Not provided.")

    # Read the full source, since a short preview may hide evidence.
    source_text = example.get("source_text") or ""

    print("\nFULL SOURCE TEXT")
    print(source_text)
    print(f"\nTotal source length: {len(source_text):,} characters")

    print("\nSOURCE URL")
    print(example.get("source_url") or "Not provided.")

if __name__ == "__main__":
    main()