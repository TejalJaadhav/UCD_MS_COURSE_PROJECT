"""
split_source.py

Purpose:
    Split one dataset source into overlapping sections and check
    that each section fits with its claim under the model's limit.

This is a small check of our section-splitting plan.
It does not run the NLI model or change the dataset.

Run from the repository folder:
    python -m src.data.split_source
"""

import argparse
import gzip
import json
from pathlib import Path

from transformers import AutoTokenizer


# Use the tokenizer for the NLI model we selected.
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"

# Set the section size and shared text between neighboring sections.
SECTION_SIZE = 200
OVERLAP_SIZE = 50
MODEL_INPUT_LIMIT = 512

# Locate the repository and its dataset files.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"


def split_into_sections(text, tokenizer):
    """Split text into token sections with some repeated text."""

    # Convert the full source into tokens without adding model markers.
    token_ids = tokenizer.encode(text, add_special_tokens=False)

    # Move forward by 150 tokens each time, repeating 50 tokens.
    step_size = SECTION_SIZE - OVERLAP_SIZE
    sections = []

    for start in range(0, len(token_ids), step_size):
        end = start + SECTION_SIZE
        section_ids = token_ids[start:end]

        # Turn each token section back into readable text.
        section_text = tokenizer.decode(
            section_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        sections.append(section_text)

        # Stop when we have included the end of the source.
        if end >= len(token_ids):
            break

    return token_ids, sections


def main():
    """Split one chosen dataset record and show section sizes."""

    parser = argparse.ArgumentParser(
        description="Check overlapping sections for one source."
    )
    parser.add_argument(
        "--split",
        choices=("train", "dev", "test"),
        default="train",
        help="Dataset split to inspect. Default: train.",
    )
    parser.add_argument(
        "--line",
        type=int,
        default=1,
        help="Record line to inspect. Default: 1.",
    )
    args = parser.parse_args()

    # Load the model's tokenizer so our sections use its token counting.
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Open only the selected dataset record.
    dataset_file = DATA_DIR / f"verifiability_judgments_{args.split}.jsonl.gz"

    with gzip.open(dataset_file, "rt", encoding="utf-8") as file:
        record = None

        for line_number, line in enumerate(file, start=1):
            if line_number == args.line and line.strip():
                record = json.loads(line)
                break

    if record is None:
        raise ValueError(
            f"Could not find a record on line {args.line} of {dataset_file}."
        )

    title = record.get("source_title") or record.get("source_content_title") or ""
    source_text = record.get("source_text") or ""
    claim = record["statement"]

    source_token_ids, sections = split_into_sections(source_text, tokenizer)

    print(f"Split: {args.split}")
    print(f"Record line: {args.line}")
    print(f"Claim: {claim}")
    print(f"Source title: {title or 'Not provided.'}")
    print(f"Source tokens: {len(source_token_ids):,}")
    print(f"Sections: {len(sections)}")

    # Count the full model input for each section and claim pair.
    for index, section in enumerate(sections, start=1):
        evidence = f"Title: {title}\nText: {section}"

        inputs = tokenizer(
            evidence,
            claim,
            add_special_tokens=True,
            truncation=False,
        )
        pair_token_count = len(inputs["input_ids"])

        print(f"\nSection {index}")
        print(f"  Section tokens: {len(tokenizer.encode(section)):,}")
        print(f"  Evidence and claim tokens: {pair_token_count:,}")
        print(f"  Fits within {MODEL_INPUT_LIMIT} tokens: "
              f"{pair_token_count <= MODEL_INPUT_LIMIT}")
        print(f"  Preview: {section[:180].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()