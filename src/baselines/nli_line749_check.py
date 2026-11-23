"""Compare NLI scores for one source sentence with and without context."""

import gzip
import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEV_FILE = PROJECT_ROOT / "data/raw/verifiability_judgments_dev.jsonl.gz"
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"
CLAIM = "Americans are among the most supportive of free speech."


def main():
    """Score the same claim against two versions of the source."""
    with gzip.open(DEV_FILE, "rt", encoding="utf-8") as file:
        example = next(
            json.loads(line)
            for line_number, line in enumerate(file, start=1)
            if line_number == 749
        )

    evidence_sentence = (
        "A 38-nation Pew Research Center survey conducted in 2015 "
        "found that Americans were among the most supportive of free speech, "
        "freedom of the press and the right to use the internet "
        "without government censorship."
    )

    context_before = (
        "Enshrined in the Bill of Rights, free expression is a bedrock "
        "American principle, and Americans tend to express stronger support "
        "for free expression than many others around the world. "
    )
    context_after = (
        " Moreover, Americans are much more tolerant of offensive speech "
        "than people in other nations."
    )

    if evidence_sentence not in example["source_text"]:
        raise ValueError("Evidence sentence was not found in the raw source.")

    checks = [
        ("Evidence sentence only", evidence_sentence),
        (
            "Evidence sentence with nearby context",
            context_before + evidence_sentence + context_after,
        ),
    ]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    print("Gold dataset label:", example["source_supports_statement"])
    print("Model label mapping:", model.config.id2label)

    for name, source in checks:
        # The source is the premise and the claim is the hypothesis.
        inputs = tokenizer(source, CLAIM, return_tensors="pt")

        with torch.inference_mode():
            scores = model(**inputs).logits[0].softmax(dim=-1)

        predicted_label = model.config.id2label[scores.argmax().item()]

        print(f"\n{name}")
        print(f"Input tokens: {inputs['input_ids'].shape[1]}")
        print(f"Prediction: {predicted_label}")

        for index, score in enumerate(scores.tolist()):
            label = model.config.id2label[index]
            print(f"  {label}: {score:.4f}")


if __name__ == "__main__":
    main()