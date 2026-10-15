# Baseline Results

## Majority Baseline

The most common training label is complete_support.
This baseline predicts that label for every development record.

Evaluation uses all 1,106 development records.

| Metric | Score |
|---|---:|
| Accuracy | 0.7505 |
| Macro-F1 | 0.2858 |
| Full-support F1 | 0.8574 |
| Partial-support F1 | 0.0000 |
| No-support F1 | 0.0000 |

The baseline detects no partial-support or no-support cases.
Its accuracy reflects the large proportion of full-support records.

No test-set evaluation has been performed.