# Evaluating Evidential Support of Citations in AI-Generated Content

**Author:** Tejal Jadhav  
**Course:** CSCI 6970 – MS Course Project  
**Term:** Fall 2026

## Purpose

Given an AI-generated claim and its cited source text, this project
evaluates overall support and identifies supported, unsupported, or
contradicted claim components.

Research questions:

1. How accurately can NLP methods classify overall citation support?
2. Can decomposition and evidence alignment localize unsupported details?
3. What kinds of evidential mismatch cause failures?

## Pipeline

The component pipeline:

1. Decomposes a claim into smaller statements.
2. Checks decomposition coverage and fidelity.
3. Retrieves relevant source passages for each component.
4. Assigns supported, unsupported, or contradicted labels.
5. Aggregates component judgments into an overall label.

Overall labels are:

- `complete_support`: all components are supported.
- `partial_support`: some, but not all, components are supported.
- `no_support`: none of the components are supported.

Rejected decompositions use a whole-claim fallback. Invalid outputs
are recorded as failures rather than removed from evaluation.

An experimental verification stage selects source sentences and checks
component judgments again. It reduced full-test performance and is
retained for comparison rather than enabled by default.

## Setup

Use Python 3.11. From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install and start Ollama, then download the local models:

```bash
ollama pull qwen2.5:7b
ollama pull qwen2.5:3b
```

The local prompted methods do not require an OpenAI API key.

## Check a Claim

Create a UTF-8 text file containing the cited source, then run:

```bash
python -m src.evaluation.check_claim \
  --claim "Your claim here." \
  --source /absolute/path/to/source.txt
```

The default is the Qwen 2.5 7B component method.

Options:

- `--prepare-only`: validate inputs without model calls.
- `--method components_verified`: use experimental verification.
- `--output /absolute/path/to/new_report.json`: save detailed results.

The command evaluates supplied source text; it does not fetch URLs.
Component output is unavailable when whole-claim fallback is used.

## Dataset

The project uses the dataset accompanying Liu, Zhang, and Liang (2023),
*Evaluating Verifiability in Generative Search Engines*:

https://github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines

Original files are stored locally under `data/raw/` and excluded from Git.
Experimental cleaning preserves source labels and original record IDs.

The cleaned test set contains 1,085 claim-source pairs:

- 787 complete support
- 183 partial support
- 115 no support

See `data/README.md` and `src/data/preprocess.py` for data preparation.

## Overall Results

All rows below use the same 1,085 cleaned test examples.
Failures remain in metric denominators.

| Method | Accuracy | Macro-F1 | Failures |
|---|---:|---:|---:|
| Majority | 72.53% | 0.2803 | 0 |
| NLI | 19.35% | 0.1765 | 0 |
| Whole-claim Qwen 3B | 18.62% | 0.2160 | 0 |
| Components Qwen 3B | 45.35% | 0.4042 | 48 |
| Components Qwen 7B, before verification | 67.19% | 0.5378 | 19 |
| Components Qwen 7B, after verification | 55.48% | 0.4998 | 49 |

The NLI model is `cross-encoder/nli-deberta-v3-small`.

The 7B pre-verification results were reconstructed from judgments saved
inside the verified run, not obtained through an independent rerun.

The component 7B method achieved the highest macro-F1; majority achieved
the highest accuracy. Verification fixed 74 predictions but changed
201 previously correct predictions to incorrect answers or failures.

## Component-Level Review

An exploratory subset contains 15 claims and 35 reference details.

| Measure | Components 3B | Components 7B before verification |
|---|---:|---:|
| Correct among matched reference details | 15/24 | 10/15 |
| Correctly covered reference details | 15/35 | 10/35 |
| Details without component output | 9 | 20 |

Higher overall classification performance did not imply better localized
coverage. Neither method correctly labeled the 11 unsupported reference
details in this small sample.

References were AI-assisted and user-reviewed after exposure to model
outputs. Remaining 7B component matching was assistant-completed at the
user's request, with ambiguous alignments noted in the worksheet.

## Reproduce Analysis

With the saved local reports available:

```bash
python -m src.evaluation.compare_runs \
  outputs/annotation_pilot/evaluation/*_test_*.json
```

Compare two reports with paired bootstrap intervals:

```bash
python -m src.evaluation.bootstrap_compare BASELINE.json CANDIDATE.json
```

Run existing automated tests:

```bash
python -m unittest discover -s tests
```

Generated reports and SQLite checkpoints are excluded from Git.
Tracked annotation worksheets are in `annotation/`.

## Limitations

- Revised methods were developed after inspecting earlier test errors;
  the reused test set is not an untouched final evaluation.
- Comparing 3B and 7B methods does not isolate the effect of verification.
  The saved 7B before/after comparison addresses that distinction.
- Manual annotations and targeted diagnostics are small, exploratory,
  and do not establish a general ranking of mismatch difficulty.
- Decomposition, retrieval, fallback behavior, and contradiction labeling
  remain sources of error.
- Example-level bootstrap intervals do not account for related questions
  or sources, model-run variation, or method selection.
- The system evaluates support relative to supplied evidence, not
  independent real-world truth.