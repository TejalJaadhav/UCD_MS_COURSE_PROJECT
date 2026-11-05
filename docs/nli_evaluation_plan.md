# Evaluation Plan

## Project scope

This project uses the majority-label baseline, a local NLI model, and a
small manual component-review pilot. It does not include an API-based
prompted-model baseline.

The original dataset labels remain unchanged:
`complete_support`, `partial_support`, and `no_support`.

## Majority-label baseline

The baseline selects the most common label in the original training split
and predicts it for every original dev example.

On dev, it achieved 0.7505 accuracy and 0.2858 macro-F1. It predicted
`complete_support` for every example and missed both other labels.

This baseline provides a reference point for the project.

## NLI experiment

The local model is `cross-encoder/nli-deberta-v3-small`. It produces
`entailment`, `neutral`, and `contradiction` scores for a source and claim.

These outputs do not map directly to the dataset's three labels.
In particular, `neutral` can mean that the source gives partial support
or gives no support. The NLI experiment will therefore report model output
counts grouped by dataset gold label. It will not report three-class
accuracy or macro-F1 without a justified mapping.

A 15-example dev pilot compared full-source input with localized evidence
when available. On this small sample, full-source predictions were often
`neutral`, including for all five `complete_support` and all five
`partial_support` examples. Localized-evidence predictions were more mixed
and produced `entailment` for four of five sampled `complete_support`
examples. These are descriptive pilot results, not overall performance
estimates.

The model also missed evidence in controlled checks on individual examples.
For original dev line 749, it predicted `entailment` when given the
matching source sentence, but `neutral` when given the long source truncated
to the model's 512-token input limit.

## Component-review pilot

Six dev examples were manually reviewed at the claim-component level.
The reviews identified supported, unsupported, and contradicted claim
parts, with draft overall judgments recorded separately from the dataset
labels.

This pilot is exploratory. It was reviewed by one annotator and does not
establish annotation agreement or component-level model performance.
The original dataset labels were not changed.

## Data split use and reporting

The original train and dev files are used for baseline development and
pilot analysis. The test split has not been used for model or rule
development.

If a final test evaluation is conducted, the method and decision rules
must first be fixed. Report its results separately and leave the original
dataset labels unchanged.

## Limits and next work

The current NLI setup is not a validated three-class classifier for the
dataset labels. Do not convert its outputs directly into
`complete_support`, `partial_support`, and `no_support`.

The component-review pilot is too small for quantitative performance
claims. Further work would require a larger, reviewed annotation subset
and clear annotation guidelines.