"""Check one claim against a local source-text file."""

import argparse
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--model", default="ollama:qwen2.5:7b")
    parser.add_argument(
        "--method",
        choices=["components", "components_verified"],
        default="components",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--prepare-only", action="store_true",
        help="Validate inputs without calling the model.",
    )
    parser.add_argument(
        "--show-evidence", action="store_true",
        help="Display retrieved source passages (not independently verified quotes).",
    )
    args = parser.parse_args(argv)

    if not args.claim.strip():
        parser.error("Claim must not be empty.")
    if not args.source.is_file():
        parser.error("Source must be an existing UTF-8 text file.")
    try:
        source = args.source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.error(f"Cannot read UTF-8 source: {exc}")
    if not source.strip():
        parser.error("Source file is empty.")
    if not args.model.strip():
        parser.error("Model must not be empty.")
    if args.output:
        if args.output.exists():
            parser.error("Output already exists; choose a new filename.")
        if not args.output.parent.is_dir():
            parser.error("Output parent directory must already exist.")

    if args.prepare_only:
        print("Claim:", args.claim)
        print("Source:", args.source.resolve())
        print("Source characters:", len(source))
        print("Inputs valid. No model calls made.")
        return 0

    try:
        if args.method == "components":
            from src.evaluation.run_prompted import predict
            label, details = predict(
                "components", args.model, args.claim, source
            )
        else:
            from src.evaluation.verified_pipeline import predict_verified
            label, details = predict_verified(
                args.model, args.claim, source
            )
        error = None
    except ValueError as exc:
        label, details, error = None, {}, str(exc)

    report = {
        "method": args.method,
        "model": args.model,
        "claim": args.claim,
        "source_file": str(args.source.resolve()),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "prediction": label,
        "details": details,
        "error": error,
    }

    print("Overall:", label or "FAILED")
    if details.get("fallback"):
        print("Whole-claim fallback:", details["fallback"])
        print("No localized component judgments were produced.")
        if args.show_evidence:
            for number, passage in enumerate(
                details.get("whole_claim_result", {}).get("passages", []), 1
            ):
                print(f"Retrieved passage {number} (not independently verified):", passage["text"])

    for number, part in enumerate(details.get("components", []), 1):
        print(f"\n{number}. {part['component']}")
        print("Label:", part.get("label") or "FAILED")

        if args.show_evidence:
            for index, passage in enumerate(part.get("passages", []), 1):
                print(f"Retrieved passage {index} (not independently verified):", passage["text"])
        selection = part.get("sentence_evidence_check") or {}
        if selection.get("selected_evidence"):
            print("Evidence:", selection["selected_evidence"])

        verification = (
            part.get("evidence_verification", {}).get("response", {})
        )
        reason = verification.get("reason") or (
            selection.get("response", {}).get("reason")
        )
        if reason:
            print("Reason:", reason)
        if part.get("verification_error"):
            print("Error:", part["verification_error"])

    if error:
        print("Error:", error)

    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        print("\nSaved:", args.output.resolve())

    return 0 if label is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
