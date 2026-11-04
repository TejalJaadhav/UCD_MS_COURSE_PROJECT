# NLI Check: Original Dev Line 749

## Purpose

Check whether the NLI model's neutral prediction on this example is caused
by the claim or by the amount of source text given to the model.

## Example

- Original split and line: dev, 749
- Gold dataset label: `no_support`
- Claim part checked: “Americans are among the most supportive of free speech.”
- Matching source sentence: A 38-nation Pew Research Center survey conducted
  in 2015 found that Americans were among the most supportive of free speech,
  freedom of the press and the right to use the internet without government
  censorship.

The source sentence directly supports the claim part. The dataset's overall
label remains `no_support`.

## Controlled Results

Model: `cross-encoder/nli-deberta-v3-small`

| Input | Contradiction | Entailment | Neutral | Prediction |
|---|---:|---:|---:|---|
| Evidence sentence only | 0.0001 | 0.9971 | 0.0028 | entailment |
| Evidence sentence with nearby context | 0.0001 | 0.9926 | 0.0073 | entailment |
| Full source, truncated to 512 tokens | 0.0006 | 0.0020 | 0.9974 | neutral |

The full source produced 666 tokens before truncation. The evidence sentence
was retained in the truncated model input. Adding the claim's survey
qualification also produced `neutral` with the full-source input.

## Interpretation

The model recognizes the evidence when given the relevant sentence alone,
and when given that sentence with nearby context. It predicts `neutral` for
this example when given the long source with the current truncation setup,
even though the evidence sentence is retained.

This is one controlled example. It suggests that long-source input handling
can affect NLI scores. It does not establish how frequently this occurs.

The dataset label was not changed.

## Next Question

Before evaluating a larger set, compare a few source-scoring approaches,
such as scoring localized evidence when available, selecting relevant source
sentences, and scoring source sections. Record which input approach is used
and evaluate it consistently.