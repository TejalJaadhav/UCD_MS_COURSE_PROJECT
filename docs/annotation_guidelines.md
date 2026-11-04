# Claim Component Annotation Guidelines

## Purpose

These guidelines are for a small pilot that examines which parts of a
claim are supported by its cited source. They do not change the dataset's
original labels.

## Unit of annotation

Break a statement into the smallest parts that can be checked against the
source on their own. Keep important details such as names, dates, numbers,
locations, and qualifiers attached to the part they change.

For each part, record the source text that supports or conflicts with it,
if any.

## Component labels

Assign one label to each claim part:

- `supported`: the source provides enough information to establish the part.
- `unsupported`: the source does not establish the part.
- `contradicted`: the source states something that conflicts with the part.

Use `unsupported` when the source is silent. Use `contradicted` only when
there is a direct conflict.

## Overall interpretation

Record the component labels first. Do not automatically derive an overall
label during this pilot. In particular, keep component judgments separate
from the dataset's original `complete_support`, `partial_support`, or
`no_support` label.

## Annotation record

For each example, record:

- Original split and line number
- Original statement
- Original dataset label
- Source passage reviewed
- Claim parts
- Component label for each part
- Short reason for each label
- Any uncertainty or disagreement

## Scope

This is an exploratory pilot. The labels and notes describe the reviewed
examples only and are not new gold labels for the dataset.
