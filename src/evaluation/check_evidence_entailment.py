"""Check whether selected evidence establishes a claim's numerical detail."""

import json

from src.evaluation.run_prompted import ask


def main():
    """Test a supported case and a missing-value case with the same model."""
    cases = [
        {
            "name": "Missing overall weight",
            "statement": "The average American man weighs around 198 pounds.",
            "evidence": "The average American man 20 years old and up weighs .",
        },
        {
            "name": "Explicit overall weight",
            "statement": "The average American man weighs around 198 pounds.",
            "evidence": (
                "The average American man 20 years old and up weighs "
                "198 pounds."
            ),
        },
    ]

    for case in cases:
        result, _ = ask(
            "ollama:qwen2.5:7b",
            (
                "Verify whether the supplied evidence establishes the statement. "
                "Use only the evidence. Do not supply missing facts from memory. "
                "A missing numerical value does not establish a claimed number. "
                "Return supported only if every detail is established, "
                "contradicted only for direct conflict, otherwise unsupported."
            ),
            {
                "statement": case["statement"],
                "evidence": case["evidence"],
            },
            {
                "label": {
                    "type": "string",
                    "enum": ["supported", "unsupported", "contradicted"],
                },
                "reason": {"type": "string"},
            },
        )

        print(f"\n{case['name']}")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()