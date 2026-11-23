"""Apply the draft overall-judgment rule to component annotations."""

import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS_FILE = (
    PROJECT_ROOT
    / "outputs/annotation_pilot/dev_component_annotations.json"
)
COMPONENT_LABELS = {"supported", "unsupported", "contradicted"}
OVERALL_LABELS = {
    "complete_support",
    "partial_support",
    "no_support",
    "uncertain",
}


def combine_component_labels(example):
    """Apply the pilot rule and preserve examples marked uncertain."""
    if (
        example["draft_overall_judgment"] == "uncertain"
        or example["uncertainty"]
    ):
        return "uncertain"

    labels = {component["label"] for component in example["components"]}

    if not labels.issubset(COMPONENT_LABELS):
        raise ValueError(
            f"Unexpected component label on dev line {example['line_number']}"
        )

    if labels == {"supported"}:
        return "complete_support"

    if "supported" in labels:
        return "partial_support"

    return "no_support"


def main():
    """Print draft judgments without changing the annotation file."""
    examples = json.loads(ANNOTATIONS_FILE.read_text(encoding="utf-8"))
    counts = Counter()

    print(f"Reviewed examples: {len(examples)}")
    print("Draft project judgments, separate from dataset gold labels:")

    for example in examples:
        judgment = combine_component_labels(example)

        if judgment not in OVERALL_LABELS:
            raise ValueError(f"Unexpected overall judgment: {judgment}")

        counts[judgment] += 1
        print(
            f"dev line {example['line_number']}: "
            f"gold={example['gold_label']}, draft={judgment}"
        )

    print("\nDraft judgment counts:")
    for label in sorted(OVERALL_LABELS):
        print(f"{label}: {counts[label]}")


if __name__ == "__main__":
    main()