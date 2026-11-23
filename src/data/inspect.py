"""
This file inspects the raw Liu et al. (2023) verifiability dataset.

"""

import gzip
import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path("data/raw")

FILES = {
    "train": DATA_DIR / "verifiability_judgments_train.jsonl.gz",
    "dev": DATA_DIR / "verifiability_judgments_dev.jsonl.gz",
    "test": DATA_DIR / "verifiability_judgments_test.jsonl.gz",
}

def load_jsonl_gz(path):
    """
    Function to load a gzip-compresses JSON Lines file.
    """
    
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line in file:
            yield json.loads(line)
            
def inspect_split(split_name, path):
    """
    Function to inspect one dataset split.
    """
    
    label_counts = Counter()
    missing_values = Counter()
    evidence_available = Counter()
    statements = Counter()
    
    total = 0
    fields = set()
    
    for example in load_jsonl_gz(path):
        total += 1
        
        fields.update(example.keys())
        label = example.get("source_supports_statement")
        label_counts[label] += 1
        
        evidence = example.get("source_localized_evidence")
        
        if evidence and evidence.strip():
            evidence_available[label] += 1
            
        statement = example.get("statement")
        
        if statement:
            statements[statement] += 1

        for field, value in example.items():
            if value is None or value == "":
                missing_values[field] += 1
    duplicate_statements = sum(
        count - 1 
        for count in statements.values()
        if count > 1
    )
    
    exact_rows = Counter()
    for example in load_jsonl_gz(path):
        row_key = json.dumps(example, sort_keys=True)
        exact_rows[row_key] += 1
    
    exact_duplicate_rows = sum(
        count - 1
        for count in exact_rows.values()
        if count > 1
    )
    
    statement_urls = {}
    
    for example in load_jsonl_gz(path):
        statement = example.get("statement")
        url = example.get("source_url")
        
        if statement not in statement_urls:
            statement_urls[statement] = set()
        
        statement_urls[statement].add(url)
        
    repeated_with_multiple_sources = sum(
        1
        for urls in statement_urls.values()
        if len(urls) > 1
    )
        
    
    
    print(f"\n{'=' * 60}")
    print(f"SPLIT: {split_name.upper()}")
    print(f"{'=' * 60}")
    
    print(f"\nTotal examples: {total}")    
    
    print("\nFields:")
    for field in sorted(fields):
        print(f"  - {field}")

    print("\nLabel distribution:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")

    print("\nLocalized evidence available:")
    for label, count in evidence_available.items():
        print(f"  {label}: {count}")

    print("\nMissing values:")
    for field, count in missing_values.items():
        print(f"  {field}: {count}")

    print(f"\nDuplicate statement occurrences: {duplicate_statements}")
    
    print(f"Exact duplicate rows: {exact_duplicate_rows}")
    
    print(
    f"Repeated statements with multiple sources: "
    f"{repeated_with_multiple_sources}"
    )
    

def check_split_overlap():
    """
    Function to check for statement-source pairs 
    shared across dataset splits.
    """
    
    split_pairs = {}

    for split_name, path in FILES.items():
        pairs = set()

        for example in load_jsonl_gz(path):
            pair = (
                example.get("statement"),
                example.get("source_url"),
            )
            pairs.add(pair)
            
        split_pairs[split_name] = pairs
            
    print("\n" + "=" * 60)
    print("CROSS-SPLIT OVERLAP")
    print("=" * 60)

    print(
        "Train vs Dev:",
        len(split_pairs["train"] & split_pairs["dev"]),
    )

    print(
        "Train vs Test:",
        len(split_pairs["train"] & split_pairs["test"]),
    )

    print(
        "Dev vs Test:",
        len(split_pairs["dev"] & split_pairs["test"]),
    )
    
    comparisons = [
        ("Train vs Dev", "train", "dev"),
        ("Train vs Test", "train", "test"),
        ("Dev vs Test", "dev", "test"),
    ]
    
    for name, split_a, split_b in comparisons:
        overlap = split_pairs[split_a] & split_pairs[split_b]

        print(f"\n{name} overlapping pairs:")

        for statement, url in overlap:
            print(f"  Statement: {statement}")
            print(f"  Source URL: {url}")
            print()
            
def main():
    for split_name, path in FILES.items():

        if not path.exists():
            print(f"File not found: {path}")
            continue

        inspect_split(split_name, path)
    
    check_split_overlap()


if __name__ == "__main__":
    main()
