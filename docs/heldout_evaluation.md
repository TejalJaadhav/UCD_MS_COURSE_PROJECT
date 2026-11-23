# Held-out evaluation protocol

The 30-example raw dev comparison used a fixed sample with ten examples
per label. These results informed development and are separate from the
held-out comparison.

| Method | Correct | Macro-F1 |
|---|---:|---:|
| Majority | 10/30 | 0.167 |
| Whole-claim LLM | 11/30 | 0.297 |
| Components with fallback | 11/30 | 0.372 |
| Whole-claim NLI | 10/30 | 0.214 |

The component method fell back to the whole-claim LLM on 15 examples.
Its partial-support recall was 3/10, compared with 6/10 for the whole-claim
LLM and 9/10 for NLI. NLI predicted partial support on 26 of 30 examples.

The final comparison uses all records in the cleaned test split. This
version excludes exact duplicates and known statement–source URL overlaps
with earlier splits. The preprocessing audit records 1,085 retained test
records and preserves original labels and record IDs. Fit the majority
baseline and NLI mapping on the cleaned training split.

Use Qwen2.5 3B through Ollama for both prompted methods. Keep the current
passage ranking, version 3 decomposition prompt, split coverage check,
model review, and whole-claim fallback. For NLI, use the existing
DeBERTa checkpoint and fit the mapping on 30 distinct training claims
per label with seed 42. Record the Git revision and the installed Ollama
model ID before running.

Run from the repository root with the project virtual environment active:

```bash
git rev-parse --short HEAD
ollama list
python -m src.baselines.run_majority --split test --dataset-version cleaned
python -m src.evaluation.run_prompted nli --split test --dataset-version cleaned --train-per-label 30 --limit 1085
python -m src.evaluation.run_prompted llm --model ollama:qwen2.5:3b --split test --dataset-version cleaned --limit 1085
python -m src.evaluation.run_prompted components --model ollama:qwen2.5:3b --split test --dataset-version cleaned --limit 1085
```

Before comparing results, verify that the four reports have identical
example IDs and dataset fingerprints. Report accuracy, macro-F1, per-label
precision and recall, and the component fallback count. Use test errors
for final analysis after the methods are fixed.
