# Decision Log

## D001 - Preserve Raw Data

The original dataset files in `data/raw/` will never be modified.

All cleaning and transformations will be written to `data/processed/`.

## D002 - Missing Localized Evidence

Examples with missing `source_localized_evidence` will be retained.

The processed `evidence` field will be null when localized evidence is unavailable. The full `source_text` will still be preserved.

## D003 - Exact Duplicate Rows

Exact duplicate rows will be removed during preprocessing.

The original raw files will remain unchanged.

## D004 - Cross-Split Overlap

Identical `statement + source_url` pairs should not occur across processed splits.

For overlaps:

- Train takes priority over Dev and Test.
- Dev takes priority over Test.
- Lower-priority overlapping examples will be removed.

This is intended to prevent evaluation leakage.


## Dataset preprocessing audit

The original compressed dataset files and support labels remain unchanged.
Preprocessing has only been inspected in memory; no processed files have
been saved yet.

### Duplicate and overlap counts

| Split | Original | Within-split duplicates | Cross-split overlaps | Remaining under proposed rule |
|---|---:|---:|---:|---:|
| Train | 8834 | 116 | 0 | 8718 |
| Dev | 1106 | 11 | 4 | 1091 |
| Test | 1097 | 7 | 5 | 1085 |

Within-split duplicates are defined using the normalized fields, not every
field in the original raw records.

Cross-split overlaps are identified by matching statement and source URL.
All nine inspected overlaps also have identical source text.

### Annotation differences

One overlapping mandatory-voting statement has different support labels:
partial_support in train and no_support in test. Neither label was changed.
Two overlaps have different evidence annotations.

### Evaluation decision still pending

The proposed cleaning rule keeps the earliest occurrence across train,
dev, then test. This changes the evaluation sets, so these counts are
provisional.

We will preserve the original splits for reference and explicitly document
any filtered evaluation version. The test example inspected during this
audit will not be used to tune the model.

### Traceability

Before saving processed data, preserve each record's original split and
raw line number so processed examples can be traced back to their source.