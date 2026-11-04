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
    """Normalize examples while preserving their original file line numbers."""
    examples = []

    for raw_line_number, raw_example in enumerate(
        load_jsonl_gz(path), start=1
    ):
        normalized = normalize_example(raw_example, split)

        # Keep the original position so cleaned records remain traceable.
        normalized["raw_line_number"] = raw_line_number
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
    """Remove identical normalized records, ignoring their original positions."""
    seen = set()
    unique_examples = []

    for example in examples:
        # Line numbers identify locations, not differences in content.
        content = {
            key: value
            for key, value in example.items()
            if key != "raw_line_number"
        }
        key = json.dumps(content, sort_keys=True)

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
    """Assign stable IDs using each example's original split and line number."""
    for split, examples in all_splits.items():
        for example in examples:
            # For example, original dev line 749 becomes dev_00749.
            raw_line_number = example["raw_line_number"]
            example["example_id"] = f"{split}_{raw_line_number:05d}"

    return all_splits

def validate_processed_examples(all_splits):
    """Check IDs and labels against the original compressed records."""
    seen_ids = set()

    for split, examples in all_splits.items():
        # Read original records independently to verify their labels.
        raw_examples = list(load_jsonl_gz(FILES[split]))

        for example in examples:
            line_number = example["raw_line_number"]
            expected_id = f"{split}_{line_number:05d}"

            assert 1 <= line_number <= len(raw_examples), "Invalid raw line"
            assert example["example_id"] == expected_id, "ID mismatch"
            assert expected_id not in seen_ids, "Duplicate ID"
            seen_ids.add(expected_id)

            # Compare the retained label with its original dataset label.
            raw_example = raw_examples[line_number - 1]
            assert (
                example["support_label"]
                == raw_example["source_supports_statement"]
            ), f"Label changed for {expected_id}"

        print(f"Validated {len(examples)} {split} records: IDs and labels OK")

def save_cleaned_splits(all_splits):
    """Save experimental cleaned splits as compressed JSON Lines files."""
    output_dir = Path("outputs/preprocessing/cleaned")
    output_dir.mkdir(parents=True, exist_ok=True)

    for split, examples in all_splits.items():
        output_path = output_dir / f"{split}.jsonl.gz"

        # Write generated copies; original files in data/raw stay unchanged.
        with gzip.open(output_path, "wt", encoding="utf-8") as file:
            for example in examples:
                file.write(json.dumps(example, ensure_ascii=False) + "\n")

        print(f"Saved {len(examples)} records to {output_path}")

def main():
    """Inspect record counts before and after each cleaning step."""
    original = load_all_splits()
    deduplicated = clean_exact_duplicates(original)
    # Inspect overlaps before deciding whether to exclude them.
    inspect_cross_split_overlap(deduplicated)
    cleaned = remove_cross_split_overlap(deduplicated)
    
    cleaned = assign_example_ids(cleaned)
    
        # Validate all remaining records before adding any saving step.
    validate_processed_examples(cleaned)

    # Display one example per split to check its ID and original position.
    for split, examples in cleaned.items():
        if examples:
            example = examples[0]
            print(
                f"{split}: ID={example['example_id']}, "
                f"raw line={example['raw_line_number']}"
            )

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
        
    save_cleaned_splits(cleaned)
        
        
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

