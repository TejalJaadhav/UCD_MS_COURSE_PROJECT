# Dataset Summary

## Source

This project uses the dataset released with:
Liu, Zhang, and Liang (2023),
“Evaluating Verifiability in Generative Search Engines.”

Repository:
https://github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines

Each record pairs an AI-generated statement with a cited source
and a human-assigned support label.

## Dataset Size and Labels

| Split | Full support | Partial support | No support | Total |
|---|---:|---:|---:|---:|
| Train | 6,415 | 1,552 | 867 | 8,834 |
| Development | 830 | 165 | 111 | 1,106 |
| Test | 797 | 183 | 117 | 1,097 |
| Total | 8,042 | 1,900 | 1,095 | 11,037 |

The original label names are complete_support, partial_support,
and no_support.

Full-support examples are the largest group. Evaluation will
therefore include macro-F1 and per-class results alongside accuracy.

## Data Quality Checks

| Check | Train | Development | Test |
|---|---:|---:|---:|
| Missing or blank claims | 0 | 0 | 0 |
| Missing or blank source text | 0 | 0 | 0 |
| Missing or invalid labels | 0 | 0 | 0 |
| Missing optional human-selected evidence | 1,072 | 130 | 140 |

Missing human-selected evidence does not mean the full source
text is missing. These records are retained.

These checks confirm that text is present. They do not establish
whether the source text is complete or correctly extracted.

## Split Checks

| Split | Unique questions |
|---|---:|
| Train | 1,156 |
| Development | 148 |
| Test | 139 |

No exact question strings are shared between any pair of splits.
This check does not detect differently worded versions of the
same question.

The original splits will be preserved.

## Initial Manual Review

Training examples from all three support labels were inspected.

Observations:
- Relevant evidence may appear outside the human-selected passage.
- The full AI response can help explain words such as “Others.”
- Source qualifiers, such as “unofficial,” require careful review.
- Some dataset labels are difficult to explain from the available
  evidence and should be flagged for review.

The original labels have not been changed. Early review notes
are recorded in annotation/pilot_notes.md.

## Scripts Used

- src/data/inspect_dataset.py: counts records and labels.
- src/data/view_example.py: displays a training example by label.
- src/data/check_dataset.py: checks missing text and invalid labels.
- src/data/check_splits.py: checks exact question overlap.