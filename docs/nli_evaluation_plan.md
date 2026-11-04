# NLI Evaluation Plan

## Dataset labels and NLI outputs

The dataset uses `complete_support`, `partial_support`, and `no_support`.
The NLI model outputs `entailment`, `neutral`, and `contradiction`.

These labels describe related ideas, but they are not interchangeable.
In particular, `neutral` alone cannot distinguish partial support from
no support. Therefore, the NLI output will not be directly converted into
the dataset's three labels.

## Planned NLI reporting

The NLI baseline will report its three output categories separately.
Results will be grouped by the dataset's gold label so we can see how
often each NLI category occurs for complete, partial, and no support.

We will not report three-class accuracy or macro-F1 for NLI unless we
define and justify a mapping from NLI outputs to dataset labels.

## Input text comparison

The small dev pilot compares each claim against the full source and,
where available, localized evidence. The pilot is descriptive. It does
not establish which input method performs best.

No-support examples in this dataset have no localized evidence, so
localized-evidence scoring cannot be compared for that label.

## Fine-grained component analysis

A separate component-level method may help distinguish partial support
from no support by checking which parts of a claim are supported. This
requires a small manually reviewed dev subset and explicit annotation
guidelines.

Any component-level results will be reported separately from the NLI
baseline. Original dataset labels will remain unchanged.

## Data split use

Use the training split to develop methods where appropriate. Use dev for
method development and pilot analysis. Keep test examples out of model
and rule development, and use test only for final evaluation after the
method and decision rules are fixed.

## Findings from the 15-example pilot

The pilot sampled five examples from each original dev label using random
seed 42. NLI outputs were summarized separately from the dataset labels
because the two label sets do not map directly.

For full-source input, the model predicted `neutral` for all five
`complete_support` and all five `partial_support` examples. For the five
`no_support` examples, it predicted `contradiction` twice and `neutral`
three times.

For localized-evidence input, which was available for the sampled
`complete_support` and `partial_support` examples, predictions were:

| Gold dataset label | Contradiction | Entailment | Neutral |
|---|---:|---:|---:|
| `complete_support` | 1 | 4 | 0 |
| `partial_support` | 0 | 1 | 4 |

The pilot also included three examples reviewed manually at the claim
component level. The model's predictions did not consistently match those
component judgments. These small, selected results are descriptive and do
not establish overall model performance.

## Current evaluation decision

Do not scale the current full-source NLI scoring setup to the whole dev
set. Treat NLI as an exploratory baseline and report its three output
categories separately by gold dataset label.

Further work should focus on refining claim-component annotation and
reviewing a small set of examples. Keep original dataset labels unchanged
and keep test examples out of development.