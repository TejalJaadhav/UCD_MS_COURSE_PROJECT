# Dataset

## Primary Dataset

This project uses the dataset released with:

**Liu, Zhang, and Liang (2023), "Evaluating Verifiability in Generative Search Engines."**

The dataset contains AI-generated statements paired with cited sources and human judgments about whether the source supports the statement.

## Raw Files

The original compressed JSON Lines files are stored in `data/raw/`:

- `verifiability_judgments_train.jsonl.gz`
- `verifiability_judgments_dev.jsonl.gz`
- `verifiability_judgments_test.jsonl.gz`

Raw files are preserved without modification.

## Dataset Size

| Split | Examples |
|---|---:|
| Train | 8,834 |
| Dev | 1,106 |
| Test | 1,097 |
| **Total** | **11,037** |

## Support Labels

The field `source_supports_statement` contains the human support judgment.

The observed labels are:

- `complete_support`
- `partial_support`
- `no_support`

### Label Distribution

| Split | Complete | Partial | No Support |
|---|---:|---:|---:|
| Train | 6,415 | 1,552 | 867 |
| Dev | 830 | 165 | 111 |
| Test | 797 | 183 | 117 |

The dataset is imbalanced toward `complete_support`.

## Important Fields

The raw dataset contains the following fields:

- `query`
- `response`
- `statement`
- `source_title`
- `source_content_title`
- `source_date`
- `source_author`
- `source_text`
- `source_raw_text`
- `source_localized_evidence`
- `source_supports_statement`
- `source_url`

For this project, the main fields are:

- `statement` — AI-generated claim
- `source_localized_evidence` — human-identified supporting evidence when available
- `source_text` — cited source text
- `source_supports_statement` — human support label
- `source_url` — cited source

## Localized Evidence

Localized evidence is generally available for `complete_support` and
`partial_support` examples.

Some complete and partial support examples have missing localized evidence.

`no_support` examples generally do not contain localized supporting evidence.

## Repeated Statements and Duplicates

Repeated statements occur frequently in the dataset.

Many repeated statements are associated with different source URLs, meaning
that they represent different citation relationships rather than simple
duplicate examples.

Therefore, repeated statements should not automatically be removed during
preprocessing.

Exact duplicate rows were also observed:

| Split | Exact Duplicate Rows |
|---|---:|
| Train | 109 |
| Dev | 10 |
| Test | 2 |

Handling of exact duplicates will be determined during preprocessing.

## Cross-Split Overlap

A small number of identical `statement + source_url` pairs occur across the
provided dataset splits:

| Splits | Overlapping Pairs |
|---|---:|
| Train / Dev | 4 |
| Train / Test | 4 |
| Dev / Test | 1 |

These overlaps will be handled during preprocessing to avoid leakage during
evaluation.

## Data Handling Policy

Files under `data/raw/` are treated as immutable original data.

Any cleaning, normalization, duplicate handling, or split adjustments will
produce separate files under `data/processed/`.

All preprocessing decisions will be documented.