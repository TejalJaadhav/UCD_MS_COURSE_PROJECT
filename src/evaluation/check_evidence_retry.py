"""Test correcting an evidence-ID format error on a saved dev response."""

import json
import re
from pathlib import Path

from src.evaluation.run_prompted import ask

ROOT = Path(__file__).resolve().parents[2]
REPORT = (
    ROOT / "outputs/annotation_pilot/evaluation"
    / "components_fresh_verified_20261122T025758_689936Z.json"
)


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    row = next(
        item for item in report["predictions"]
        if item["example_id"] == "dev_01090"
    )
    part = next(
        item for item in row["details"]["components"]
        if item["label"] is None
    )

    # Reconstruct the original sentence IDs in the same order.
    sentences = list(dict.fromkeys(
        sentence.strip()
        for passage in part["passages"]
        for sentence in re.split(r"(?<=[.!?])\s+", passage["text"])
        if sentence.strip()
    ))
    previous = part["sentence_evidence_check"]["response"]

    result, _ = ask(
        report["model"],
        (
            "Review your previous judgment using only the supplied evidence. "
            "Return supported only when all details are established, contradicted "
            "only for direct conflict, otherwise unsupported. "
            "Correct the inconsistent evidence ID: unsupported MUST use ID 0. "
            "Supported or contradicted MUST select one existing sentence ID. "
            "An unsupported judgment does not require a supporting sentence. "
            "Do not change your label merely to satisfy the ID format."
        ),
        {
            "statement": part["component"],
            "previous_response": previous,
            "evidence": [
                {"id": number, "text": text}
                for number, text in enumerate(sentences, start=1)
            ],
        },
        {
            "label": {
                "type": "string",
                "enum": ["supported", "unsupported", "contradicted"],
            },
            "evidence_id": {"type": "integer"},
            "reason": {"type": "string"},
        },
    )

    number = result["evidence_id"]
    valid = type(number) is int and (
        (result["label"] == "unsupported" and number == 0)
        or (
            result["label"] in {"supported", "contradicted"}
            and 1 <= number <= len(sentences)
        )
    )
    print("Statement:", part["component"])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Valid evidence selection:", valid)


if __name__ == "__main__":
    main()