"""Compare NLI outputs with component labels in the small review pilot."""

import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS_FILE = (
    PROJECT_ROOT
    / "outputs/annotation_pilot/dev_component_annotations.json"
)
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
NLI_LABELS = ["contradiction", "entailment", "neutral"]


def main():
    """Score components that have a recorded evidence passage."""
    examples = json.loads(ANNOTATIONS_FILE.read_text(encoding="utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    print("Component-level comparison for the six-example review pilot.")
    print("NLI outputs and human component labels are reported side by side.")
    print("No accuracy score is calculated.")

    scored_count = 0
    skipped_count = 0

    for example in examples:
        for component in example["components"]:
            evidence = component["evidence"].strip()

            if not evidence:
                skipped_count += 1
                print(
                    f"\ndev line {example['line_number']}: "
                    f"{component['label']} "
                    "(skipped: no specific evidence passage recorded)"
                )
                continue

            inputs = tokenizer(
                evidence,
                component["text"],
                truncation="only_first",
                max_length=512,
                return_tensors="pt",
            )

            with torch.inference_mode():
                scores = model(**inputs).logits[0].softmax(dim=-1)

            predicted_index = scores.argmax().item()
            nli_prediction = model.config.id2label[predicted_index]
            score_by_label = {
                model.config.id2label[index]: round(score, 4)
                for index, score in enumerate(scores.tolist())
            }

            scored_count += 1
            print(
                f"\ndev line {example['line_number']}"
                f"\n  Component: {component['text']}"
                f"\n  Human component label: {component['label']}"
                f"\n  NLI output: {nli_prediction}"
                f"\n  NLI scores: {score_by_label}"
            )

    print(f"\nComponents scored: {scored_count}")
    print(f"Components skipped: {skipped_count}")
    print("Review differences manually. These pilot results are descriptive.")


if __name__ == "__main__":
    main()