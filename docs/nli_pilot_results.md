# NLI Pilot Results

We tested the NLI method on 30 development examples:
10 from each original dataset label.

For this two-group comparison, complete_support means
“fully supported.” Partial_support and no_support both mean
“not fully supported.”

| Measure | Score |
|---|---:|
| Accuracy | 0.6667 |
| Macro-F1 | 0.5739 |
| Fully supported: precision | 0.5000 |
| Fully supported: recall | 0.3000 |
| Fully supported: F1 | 0.3750 |
| Not fully supported: precision | 0.7083 |
| Not fully supported: recall | 0.8500 |
| Not fully supported: F1 | 0.7727 |

On this sample, always predicting “not fully supported” would also
get 0.6667 accuracy and 0.4000 macro-F1.

This is an early check on 30 examples, not a final result.
The full development set still needs to be evaluated.