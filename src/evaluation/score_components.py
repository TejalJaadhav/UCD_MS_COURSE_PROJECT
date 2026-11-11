"""Score pilot claim components and save predictions for later review."""

import json
from datetime import datetime, timezone
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS_FILE = (
    PROJECT_ROOT / "outputs/annotation_pilot/dev_component_annotations.json"
)
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
MAX_LENGTH = 512


def main():
    """Score recorded evidence and save all component results."""
    examples = json.loads(ANNOTATIONS_FILE.read_text(encoding="utf-8"))

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    print(f"Component-level comparison for {len(examples)} examples.")
    print("NLI outputs and human component labels are reported side by side.")
    print("No accuracy score is calculated.")

    scored_count = 0
    skipped_count = 0
    results = []

    for example in examples:
        for component_number, component in enumerate(
            example["components"], start=1
        ):
            evidence = component["evidence"].strip()

            # Preserve the inputs and original labels for later review.
            # Component numbers start at 1 within each example.
            result = {
                "split": example["split"],
                "line_number": example["line_number"],
                "component_number": component_number,
                "gold_label": example["gold_label"],
                "claim": example["claim"],
                "component": component["text"],
                "human_component_label": component["label"],
                "evidence": evidence,
                "status": "skipped",
                "skip_reason": "No recorded evidence passage",
                "nli_prediction": None,
                "nli_scores": None,
                "input_tokens": None,
            }
            results.append(result)

            # Keep skipped components in the saved results.
            if not evidence:
                skipped_count += 1
                print(
                    f"\ndev line {example['line_number']}: "
                    f"{component['label']} "
                    "(skipped: no specific evidence passage recorded)"
                )
                continue

            # Evidence comes first, followed by the claim component.
            # Only the evidence may be truncated.
            inputs = tokenizer(
                evidence,
                component["text"],
                truncation="only_first",
                max_length=MAX_LENGTH,
                return_tensors="pt",
            )

            with torch.inference_mode():
                scores = model(**inputs).logits[0].softmax(dim=-1)

            # Read label names from the model configuration.
            predicted_index = scores.argmax().item()
            nli_prediction = model.config.id2label[predicted_index]
            score_by_label = {
                model.config.id2label[index]: probability
                for index, probability in enumerate(scores.tolist())
            }

            # Save full precision; round only the terminal display.
            result.update({
                "status": "scored",
                "skip_reason": None,
                "nli_prediction": nli_prediction,
                "nli_scores": score_by_label,
                "input_tokens": inputs["input_ids"].shape[1],
            })
            scored_count += 1

            display_scores = {
                label: round(probability, 4)
                for label, probability in score_by_label.items()
            }
            print(
                f"\ndev line {example['line_number']}"
                f"\n  Component: {component['text']}"
                f"\n  Human component label: {component['label']}"
                f"\n  NLI output: {nli_prediction}"
                f"\n  NLI scores: {display_scores}"
            )

    # Save each run separately so earlier results are preserved.
    completed_at = datetime.now(timezone.utc)
    run_id = completed_at.strftime("%Y%m%dT%H%M%S_%fZ")
    output_path = ANNOTATIONS_FILE.parent / f"component_scores_{run_id}.json"

    report = {
        "completed_at_utc": completed_at.isoformat(),
        "model": MODEL_NAME,
        "model_revision": getattr(model.config, "_commit_hash", None),
        "label_mapping": model.config.id2label,
        "max_length": MAX_LENGTH,
        "truncation": "only_first",
        "annotations_file": str(ANNOTATIONS_FILE.relative_to(PROJECT_ROOT)),
        "example_count": len(examples),
        "scored_count": scored_count,
        "skipped_count": skipped_count,
        "results": results,
    }

    # Exclusive creation prevents accidentally overwriting a results file.
    with output_path.open("x", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")

    print(f"\nResults saved to: {output_path}")
    print(f"Components scored: {scored_count}")
    print(f"Components skipped: {skipped_count}")
    print("Review differences manually. These pilot results are descriptive.")


if __name__ == "__main__":
    main()