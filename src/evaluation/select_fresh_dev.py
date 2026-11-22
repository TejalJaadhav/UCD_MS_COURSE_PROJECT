"""Select a fixed dev validation sample excluding previously tuned claims."""

import json
from pathlib import Path

from src.evaluation.overall import load_split
from src.evaluation.run_prompted import balanced_sample

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = (
    ROOT / "outputs/annotation_pilot/evaluation"
    / "components_dev_20261121T211932_882760Z.json"
)
OUTPUT = ROOT / "outputs/annotation_pilot/evaluation/fresh_dev_sample.json"


def claim_key(text):
    """Treat repeated claims with formatting differences as the same claim."""
    return " ".join(text.replace("*", "").casefold().split())


def main():
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    records, fingerprint = load_split("dev", "raw")
    tuned_ids = set(previous["example_ids"])

    # Also exclude the three diagnostic claims inspected during development.
    excluded_ids = tuned_ids | {"dev_00005", "dev_00020", "dev_00023"}
    excluded_claims = {
        claim_key(row["claim"])
        for row in records
        if row["example_id"] in excluded_ids
    }

    candidates = [
        row for row in records
        if claim_key(row["claim"]) not in excluded_claims
    ]
    selected = balanced_sample(candidates, per_label=10, seed=123)

    report = {
        "split": "dev",
        "dataset_version": "raw",
        "dataset_sha256": fingerprint,
        "seed": 123,
        "excluded_example_ids": sorted(excluded_ids),
        "example_ids": [row["example_id"] for row in selected],
    }

    with OUTPUT.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")

    print(f"Selected {len(selected)} examples, ten per label.")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()