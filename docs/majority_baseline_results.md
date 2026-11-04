# Majority-Label Baseline Results

## Setup

Script: `src/baselines/majority.py`

The baseline selects the most frequent label from the original training
split and predicts that label for every original dev example.

The experimental cleaned splits were not used.
No test evaluation was performed.

Training records: 8,834.
Selected label: `complete_support` (6,415 training records).

## Dev Results

Dev records: 1,106.

| Label | Precision | Recall | F1 | Count |
|---|---:|---:|---:|---:|
| complete_support | 0.7505 | 1.0000 | 0.8574 | 830 |
| partial_support | 0.0000 | 0.0000 | 0.0000 | 165 |
| no_support | 0.0000 | 0.0000 | 0.0000 | 111 |

Accuracy: 0.7505.
Macro-F1: 0.2858.

Undefined precision values are reported as zero.

## Interpretation

The baseline achieves high accuracy because complete_support is the
largest class. It cannot recognize partial_support or no_support.

It does not examine claims or sources. These results provide a reference
for evaluating more advanced methods, with attention to macro-F1 and
performance on each label.