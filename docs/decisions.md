# Decision Log

## D001 - Preserve Raw Data

The original compressed dataset files in `data/raw/` will never be modified.

Experimental cleaned copies are saved in `outputs/preprocessing/cleaned/`
as compressed `.jsonl.gz` files. This directory is ignored by Git.

The current preprocessing script does not save files to `data/processed/`.

## D002 - Missing Localized Evidence

Examples with missing `source_localized_evidence` are retained.

The normalized `evidence` field is null when localized evidence is missing
or empty. The full `source_text` is preserved.

## D003 - Duplicate Records

Records that are identical across the normalized content fields are
removed within each split, keeping the first occurrence.

The original raw line number is excluded from the duplicate comparison.
These are duplicates of the normalized records, not necessarily identical
across every field in the raw dataset.

The original raw files remain unchanged.

## D004 - Cross-Split Overlap

For the experimental cleaned version, matching `statement + source_url`
pairs are excluded from later splits using this priority:

- Train takes priority over Dev and Test.
- Dev takes priority over Test.

This step checks against earlier splits only. It does not remove repeated
pairs within the same split unless they meet the duplicate-record rule.

This reduces overlap of identical claim–source pairs across splits.
It does not guarantee that all other forms of overlap or leakage are absent.

The choice of dataset version for final evaluation remains pending.

## D005 - Preserve Gold Labels

Original support labels are retained without modification:

- `complete_support`
- `partial_support`
- `no_support`

Observed label disagreements are documented, not corrected automatically.

## D006 - Preserve Traceability

Each retained record includes its original split and one-based
`raw_line_number`.

Its `example_id` is constructed from these values. For example,
original dev line 749 receives the ID `dev_00749` if retained.

IDs are not renumbered after cleaning, so gaps are expected.

## Dataset Preprocessing Audit

The experimental cleaned splits have been saved successfully.
The original compressed dataset files remain unchanged.

### Duplicate and Overlap Counts

| Split | Original | Within-split duplicates removed | Cross-split overlaps removed | Saved |
|---|---:|---:|---:|---:|
| Train | 8834 | 116 | 0 | 8718 |
| Dev | 1106 | 11 | 4 | 1091 |
| Test | 1097 | 7 | 5 | 1085 |

Cross-split overlaps were identified by matching statement and source URL.
All nine inspected overlapping records also had identical source text
to the earlier occurrence used for comparison.

### Annotation Differences

One overlapping mandatory-voting statement has different support labels:
`partial_support` in train and `no_support` in test.

Neither original label was changed. Under the experimental cleaning rule,
the train record is retained and the overlapping test record is excluded.

Two inspected overlaps have different evidence annotations.

### Validation Completed

Before saving, all retained records passed checks confirming that:

- Their raw line numbers are within the original file's bounds.
- Their IDs match their split and original raw line number.
- Their IDs are unique across the cleaned splits.
- Their support labels match the corresponding original raw records.

### Saved Files

- `outputs/preprocessing/cleaned/train.jsonl.gz`
- `outputs/preprocessing/cleaned/dev.jsonl.gz`
- `outputs/preprocessing/cleaned/test.jsonl.gz`

All three generated files are ignored by Git.
Rerunning the preprocessing script replaces these generated copies.

### Evaluation Decision Still Pending

These files represent an experimental cleaned version.
The final evaluation dataset has not yet been selected.

Removing records changes the evaluation sets. Any results using the
cleaned version must identify that version and report its record counts.

The original splits are preserved for reference. The test example
inspected during this audit will not be used to tune the model.