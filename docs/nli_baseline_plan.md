# NLI Baseline Plan

## What the model reads

For each example, give the model:

- The claim: the generated statement.
- The evidence: the saved source title and source text.

Do not give the model the human-selected evidence passage.

## NLI labels

The model returns one of these labels:

- Entailment: the evidence supports the claim.
- Neutral: the evidence does not establish the claim.
- Contradiction: the evidence conflicts with the claim.

## First comparison

The first NLI experiment will answer this question:

“Does the source fully support the claim?”

Use two groups:

- Fully supported: complete_support
- Not fully supported: partial_support or no_support

If the model predicts entailment, predict “fully supported.”
If it predicts neutral or contradiction, predict “not fully supported.”

This NLI result cannot distinguish partial support from no support.
We will report it as a two-group comparison, not as a three-label result.

## Long sources

After choosing a model, divide long sources into overlapping sections
that fit the model’s input limit. Check the whole claim against each
section. Record the rule for combining section results before running
the experiment.

## Evaluation

Use the development split to check the setup and report accuracy,
macro-F1, and results for each group. Keep the test split for final
evaluation after decisions are complete.

## First Model Check

We tried the model on three short practice examples.

- Complete support: entailment score 0.9977.
- Partial support: neutral score 0.7042.
- No support: neutral score 0.9989.

This was a basic check that the model loads and returns scores.
It is not an experiment result because the examples were prepared
for practice.

The model gave a neutral result for both the partial and no-support
examples. This shows why the NLI baseline will first be evaluated
as a two-group task: fully supported versus not fully supported.

## Long Sources

Split the source text into sections of 200 tokens, with 50 tokens
repeated between neighboring sections. Include the source title
with each section.

Check the whole claim against every section. Keep the claim intact.
Each title, section, and claim pair must fit within the model's
512-token limit. If a pair does not fit, flag that record for review.

If any section is predicted as entailment, predict “fully supported.”
If no section is predicted as entailment, predict “not fully supported.”

Also record contradiction scores for review. The two-group result
does not separate partial support from no support.

This rule may miss evidence that is spread across different sections.


## Long Sources

Split each source into sections of 200 tokens, with 50 tokens
repeated between neighboring sections. Include the source title
with each section and compare it with the whole claim.

Check every section and save its contradiction, entailment, and
neutral scores.

For the first overall result:
- If any section's highest score is entailment, predict fully supported.
- Otherwise, predict not fully supported.

Review the saved scores to see whether evidence may be spread across
sections. This first rule may miss claims supported by evidence that
only makes sense when sections are read together.

Keep the claim intact. Check that each title, section, and claim fits
within the model's 512-token limit. Flag pairs that do not fit.