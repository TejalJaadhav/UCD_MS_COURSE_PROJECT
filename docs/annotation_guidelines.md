# Claim Component Annotation Guidelines

## Purpose

These guidelines support the project’s exploratory study of which parts
of a claim are supported by its cited source. Component labels are project
annotations. They do not change the dataset’s original labels.

## Split a claim into parts

Split a statement into the smallest claims that can be checked separately
against the source.

Keep details that affect meaning together with the part they describe.
For example, keep a number with the quantity it measures and keep a date
with the event it dates.

Do not split a phrase when doing so would make it unclear or change its
meaning. If a claim cannot be split confidently, keep it together and
record the uncertainty.

## Label each part

Assign one label to each component:

- `supported`: the source gives enough information to establish the claim.
- `unsupported`: the source does not establish the claim.
- `contradicted`: the source directly states something that conflicts with
  the claim.

Use `unsupported` when the source is silent or does not give enough
information. Use `contradicted` only when the source provides conflicting
information.

## Record evidence and reasons

For each component, record:

- The component text
- Its label
- The source passage used to judge it, if any
- A short reason for the judgment

If no passage supports or conflicts with a component, record that no
matching passage was found.

## Overall project judgment

For pilot analysis, use this draft rule after labeling the components:

- `complete_support`: all components are supported.
- `partial_support`: at least one component is supported and at least one
  is unsupported or contradicted.
- `no_support`: no components are supported.

If the components or overall judgment are unclear, mark the case
`uncertain` and explain why. Do not force a label.

This overall project judgment is recorded separately from the dataset’s
original gold label. Never overwrite or alter the gold label.

## Annotation record

For every example, retain:

- Original split and one-based raw line number
- Original dataset gold label
- Original claim and cited source
- Localized evidence, when provided
- Claim components
- Component labels, evidence passages, and reasons
- Draft overall project judgment
- Uncertainty or disagreement notes

## Review procedure

Read the claim and source before assigning component labels. Use localized
evidence as a helpful passage when available, then check the full source
when needed. Do not assume the localized evidence contains every relevant
passage.

Mark uncertain cases for review. These pilot annotations are not new gold
labels and do not establish model performance or annotator agreement.