"""
This file displays one training example to understand the dataset fields.

What this script shows:
    - The original user question
    - The AI genereated statement
    - The human-assigned support label
    - The human-selected evidence, if available
    - A preview of the cited source
    
only the training split is used. Dataset files are not modified.

Run from the repository root:
    python -m src.data.view_example
    
"""

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
    """
       Display the first no-support example from training data.
    """
    
    example = None
    
    with gzip.open(TRAIN_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            record = json.loads(line)
            
            if record["source_supports_statement"] == "no_support":
                example = record
                break
        
        if example is None:
            print("No no-support example was found.")
            return
        
        print("AVAILABLE FIELDS")
        print(", ".join(example.keys()))
        
        print("\nORIGINAL QUESTION")
        print(example["query"])
        
        # Show the full AI response to understand words such as "Others".
        # Their meaning may depend on the sentences before the claim.
        print("\nFULL AI-GENERATED RESPONSE")
        print(example["response"])
        
        print("\nAI-GENERATED STATEMENT")
        print(example["statement"])
        
        print("\nHUMAN SUPPORT LABEL")
        print(example["source_supports_statement"])
        
        # Some records do not contain human-selected evidence.
        print("\nHUMAN-SELECTED EVIDENCE")
        print(example.get("source_localized_evidence") or "Not provided.")

        source_text = example.get("source_text") or ""
        
        # Show the full source so relevant evidence is not hidden by truncation.
        print("\nFULL SOURCE TEXT")
        print(source_text)
        print(f"\nTotal source length: {len(source_text):,} characters")

        print("\nSOURCE URL")
        print(example.get("source_url") or "Not provided.")


if __name__ == "__main__":
    main()