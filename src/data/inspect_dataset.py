"""
This file inspect the citation-support dataset before building any models.

What this script does:
    1. Opens the compressed train, development, and test files.
    2. Counts the examples in each file.
    3. Counts the examples belonging to each support label.

The dataset files are read only; this script does not change them.

Run from the repository's main folder:
    python -m src.data.inspect_dataset
"""

import gzip  
import json  
from collections import Counter  
from pathlib import Path


# Locate the repository root using this script's location:
# repository / src / data / inspect_dataset.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "raw"

def main():
    """Print the record count and support-label distribution for each split."""
    
    for split in ("train", "dev", "test"):
        file_path = DATA_DIR / f"verifiability_judgments_{split}.jsonl.gz"
        
        # "rt" = read in text mode.
        # Each nonempty line contains one example in JSON format.
        with gzip.open(file_path, "rt", encoding="utf-8") as file:
            records = [
                json.loads(line)
                for line in file
                if line.strip()
            ]
         
         # Count the human-assigned support labels   
        label_counts = Counter(
            record["source_supports_statement"]
            for record in records
        )
        
        print(f"\n{split.upper()}: {len(records):,} records")

        for label, count in sorted(label_counts.items()):
            print(f"  {label}: {count:,}")

if __name__ == "__main__":
    main()