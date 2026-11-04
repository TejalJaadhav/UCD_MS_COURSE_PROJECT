"""
This file Preprocess the Liu et al. (2023) dataset 
"""

import gzip
import json
from pathlib import Path

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

FILES = {
    "train": RAW_DIR / "verifiability_judgments_train.jsonl.gz",
    "dev": RAW_DIR / "verifiability_judgments_dev.jsonl.gz",
    "test": RAW_DIR / "verifiability_judgments_test.jsonl.gz",
}


def load_jsonl_gz(path):
    """Load examples from a compressed JSON Lines file."""
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line in file:
            yield json.loads(line)
            
def normalize_example(example, split):
    """Convert a raw example into the project's internal schema."""

    return {
        "query": example.get("query"),
        "statement": example.get("statement"),
        "evidence": example.get("source_localized_evidence") or None,
        "source_text": example.get("source_text"),
        "support_label": example.get("source_supports_statement"),
        "source_url": example.get("source_url"),
        "split": split,
    }
    
def load_and_normalize_split(split, path):
    """Load and normalize all examples from one dataset split."""

    examples = []

    for raw_example in load_jsonl_gz(path):
        normalized = normalize_example(raw_example, split)
        examples.append(normalized)

    return examples

def load_all_splits():
    """Load and normalize train, dev, and test splits."""

    all_splits = {}

    for split, path in FILES.items():
        all_splits[split] = load_and_normalize_split(split, path)

    return all_splits

def clean_exact_duplicates(all_splits):
    """Remove exact duplicate rows within each split."""

    cleaned_splits = {}

    for split, examples in all_splits.items():
        cleaned_splits[split] = remove_exact_duplicates(examples)

    return cleaned_splits
    
def remove_exact_duplicates(examples):
    """Remove rows that are completely identical."""

    seen = set()
    unique_examples = []

    for example in examples:
        key = json.dumps(example, sort_keys=True)

        if key not in seen:
            seen.add(key)
            unique_examples.append(example)

    return unique_examples
    

def remove_cross_split_overlap(all_splits):
    """Remove statement-source pairs already present in an earlier split."""

    seen_pairs = set()
    cleaned_splits = {}

    for split in ["train", "dev", "test"]:
        cleaned_examples = []
        current_split_pairs = set()

        for example in all_splits[split]:
            pair = (
                example["statement"],
                example["source_url"],
            )

            # Compare only with pairs from earlier splits.
            if pair not in seen_pairs:
                cleaned_examples.append(example)

            current_split_pairs.add(pair)

        cleaned_splits[split] = cleaned_examples

        # Update after the entire split to preserve repeats within this split.
        seen_pairs.update(current_split_pairs)

    return cleaned_splits

def assign_example_ids(all_splits):
    """Assign a unique ID to each processed example."""

    for split, examples in all_splits.items():
        for index, example in enumerate(examples, start=1):
            example["example_id"] = f"{split}_{index:05d}"

    return all_splits


def main():
    """Inspect record counts before and after each cleaning step."""
    original = load_all_splits()
    deduplicated = clean_exact_duplicates(original)
    # Inspect overlaps before deciding whether to exclude them.
    inspect_cross_split_overlap(deduplicated)
    cleaned = remove_cross_split_overlap(deduplicated)

    # Show the effect of each step separately for every split.
    for split in ["train", "dev", "test"]:
        original_count = len(original[split])
        deduplicated_count = len(deduplicated[split])
        cleaned_count = len(cleaned[split])

        print(f"\n{split.upper()}")
        print(f"  Original records: {original_count}")
        print(
            f"  Exact duplicates removed: "
            f"{original_count - deduplicated_count}"
        )
        print(
            f"  Earlier-split overlaps removed: "
            f"{deduplicated_count - cleaned_count}"
        )
        print(f"  Remaining records: {cleaned_count}")
        
        
def inspect_cross_split_overlap(all_splits):
    """Compare overlapping pairs with their first occurrence in an earlier split."""
    earlier_pairs = {}

    for split in ["train", "dev", "test"]:
        current_pairs = {}

        for example in all_splits[split]:
            pair = (example["statement"], example["source_url"])

            if pair in earlier_pairs:
                previous = earlier_pairs[pair]

                print(f"\nOverlap: {previous['split']} -> {split}")
                print(f"  Statement: {example['statement']}")
                print(f"  URL: {example['source_url']}")
                print(
                    f"  Labels: {previous['support_label']} "
                    f"-> {example['support_label']}"
                )
                print(
                    f"  Same source text: "
                    f"{previous['source_text'] == example['source_text']}"
                )
                print(
                    f"  Same evidence: "
                    f"{previous['evidence'] == example['evidence']}"
                )

            # Keep the first occurrence for comparison with later splits.
            current_pairs.setdefault(pair, example)

        # Update only after checking the entire split.
        for pair, example in current_pairs.items():
            earlier_pairs.setdefault(pair, example)


# Run the inspection only when this file is executed directly.
if __name__ == "__main__":
    main()

