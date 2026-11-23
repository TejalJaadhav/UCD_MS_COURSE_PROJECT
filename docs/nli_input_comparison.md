# NLI Input Comparison Pilot

## Setup

The script `src/baselines/nli_input_comparison.py` selected five examples
from each original dev label using random seed 42.

It scored each claim against the full source. For examples with localized
evidence, it also scored the claim against that evidence. No test examples
were used.

NLI outputs are `contradiction`, `entailment`, and `neutral`. Dataset labels
are `complete_support`, `partial_support`, and `no_support`. The counts
below summarize NLI outputs by dataset gold label. They are not accuracy
scores because the label sets do not match.

## Prediction Counts

| Gold dataset label | Input | Contradiction | Entailment | Neutral |
|---|---|---:|---:|---:|
| complete_support | Full source | 0 | 0 | 5 |
| complete_support | Localized evidence | 1 | 4 | 0 |
| partial_support | Full source | 0 | 0 | 5 |
| partial_support | Localized evidence | 0 | 1 | 4 |
| no_support | Full source | 2 | 0 | 3 |
| no_support | Localized evidence | — | — | No examples |

## Interpretation

On this small sample, the full-source input produced `neutral` for all
complete-support and partial-support examples. Localized evidence produced
more `entailment` predictions for complete-support examples, but its
predictions for partial-support examples were mixed.

Dev examples with the `no_support` label had no localized evidence, so that
input method could not be compared for that class. The results are
descriptive counts from a 15-example pilot. They do not establish overall
accuracy, macro-F1, or which input method performs best on the full dev set.

The gold dataset labels were not changed.