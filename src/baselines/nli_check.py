"""Check the NLI model on simple supported, contradicted, and unknown claims."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "cross-encoder/nli-deberta-v3-small"

# Score order documented by the model's authors.
LABELS = ["contradiction", "entailment", "neutral"]


def main():
    """Load the model and print scores for three controlled examples."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    print("Model configuration label mapping:", model.config.id2label)
    print("Documented score order:", LABELS)

    source = "A man is eating pizza."
    examples = [
        ("A man is eating food.", "entailment"),
        ("No one is eating anything.", "contradiction"),
        ("The man has a sister.", "neutral"),
    ]

    for claim, expected in examples:
        # The source is the premise; the claim is the hypothesis.
        inputs = tokenizer(source, claim, return_tensors="pt")

        # Disable gradient calculations because we are not training.
        with torch.inference_mode():
            logits = model(**inputs).logits[0]
            scores = torch.softmax(logits, dim=-1)

        predicted = LABELS[scores.argmax().item()]

        print(f"\nSource: {source}")
        print(f"Claim: {claim}")
        print(f"Expected: {expected}")
        print(f"Predicted: {predicted}")

        for label, score in zip(LABELS, scores.tolist()):
            print(f"  {label}: {score:.4f}")


if __name__ == "__main__":
    main()