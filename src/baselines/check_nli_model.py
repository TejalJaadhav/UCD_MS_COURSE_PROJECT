"""
check_nli_model.py

Purpose:
    Load the NLI model and try it on one claim and its evidence.

Run:
    python -m src.baselines.check_nli_model
"""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# This small model returns contradiction, entailment, and neutral scores.
MODEL_NAME = "cross-encoder/nli-deberta-v3-small"


def main():
    """Try the model on one example from each support label."""

    examples = [
        {
            "name": "Complete support",
            "evidence": (
                "Judge John Deed - Full Cast & Crew. "
                "The show ran from 2001 to 2005 and had 6 seasons."
            ),
            "claim": "Judge John Deed had 6 series.",
        },
        {
            "name": "Partial support",
            "evidence": (
                "New York City approved a limit on sugary-drink sizes to "
                "combat obesity. Some people argue the government should "
                "not limit people's choices."
            ),
            "claim": (
                "Some people support drink-size limits to reduce obesity "
                "and other health problems, while others support personal choice."
            ),
        },
        {
            "name": "No support",
            "evidence": (
                "The New York City sugary-drink size limit was repealed."
            ),
            "claim": (
                "Others believe that limiting drink sizes can reduce "
                "sugar consumption."
            ),
        },
    ]

    print(f"Loading {MODEL_NAME}...")

    # Download the model and tokenizer the first time the script runs.
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

    # The model card gives the score order as contradiction, entailment, neutral.
    labels = ["contradiction", "entailment", "neutral"]

    for example in examples:
        # Give the source passage and claim to the NLI model.
        inputs = tokenizer(
            example["evidence"],
            example["claim"],
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        # Get scores without changing the model.
        with torch.no_grad():
            logits = model(**inputs).logits[0]
            scores = torch.softmax(logits, dim=0)

        print(f"\n{example['name']}")
        print(f"Claim: {example['claim']}")
        print("Scores:")

        for label, score in zip(labels, scores):
            print(f"  {label}: {score.item():.4f}")


if __name__ == "__main__":
    main()