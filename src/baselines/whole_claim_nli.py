"""Train a three-label linear classifier on whole-claim NLI scores."""

from collections import Counter

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.evaluation.overall import LABELS

MODEL = "cross-encoder/nli-deberta-v3-small"
FEATURES = ("contradiction", "entailment", "neutral")


class WholeClaimNLI:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL).eval()
        mapping = {label.lower(): index for index, label in self.model.config.id2label.items()}
        self.indices = [mapping[label] for label in FEATURES]
        self.classifier = torch.nn.Linear(len(FEATURES), len(LABELS))
        with torch.no_grad():
            self.classifier.weight.zero_()
            self.classifier.bias.zero_()

    def features(self, claim, source):
        """Use the source as premise and keep the claim within the token limit."""
        inputs = self.tokenizer(
            source, claim, truncation="only_first", max_length=512, return_tensors="pt"
        )
        with torch.no_grad():
            return self.model(**inputs).logits[0].softmax(dim=-1)[self.indices]

    def fit(self, records):
        """Learn a mapping from NLI scores to gold labels using train only."""
        scores = torch.stack([self.features(r["claim"], r["source"] or "") for r in records])
        targets = torch.tensor([LABELS.index(r["gold_label"]) for r in records])
        counts = Counter(targets.tolist())
        weights = torch.tensor([len(records) / (len(LABELS) * counts[i]) for i in range(len(LABELS))])
        optimizer = torch.optim.LBFGS(self.classifier.parameters(), max_iter=80)

        def closure():
            optimizer.zero_grad()
            # Weight labels equally so the majority class does not dominate fitting.
            loss = torch.nn.functional.cross_entropy(self.classifier(scores), targets, weight=weights)
            loss = loss + 0.001 * self.classifier.weight.square().sum()
            loss.backward()
            return loss

        optimizer.step(closure)

    def predict(self, claim, source):
        scores = self.features(claim, source)
        with torch.no_grad():
            probabilities = self.classifier(scores).softmax(dim=-1)
        return LABELS[probabilities.argmax().item()], {
            "nli_scores": dict(zip(FEATURES, scores.tolist())),
            "support_scores": dict(zip(LABELS, probabilities.tolist())),
        }
