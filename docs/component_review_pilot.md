# Component Review Pilot

## Purpose

This note records exploratory manual reviews of three original dev
examples. The component judgments are separate from the dataset's original
labels. No original labels were changed.

## Reviewed examples

### Original dev line 29

- Original dataset label: `complete_support`
- Claim: The team won Super Bowl XXX against the Pittsburgh Steelers with
  a score of 27-17.
- Source evidence: The source says the 1995 season included a win against
  the Pittsburgh Steelers in Super Bowl XXX, 27-17.
- Component judgment: The matchup, event, and score are supported.
- Reason: The source passage states these details directly.

### Original dev line 408

- Original dataset label: `partial_support`
- Claim: Cream of tartar can be replaced with vinegar or lemon juice in a
  1:2 ratio.
- Source evidence: The source says to use an equal amount of lemon juice
  or distilled white vinegar as a replacement.
- Component judgments:
  - Replacement with lemon juice: supported.
  - Replacement with vinegar: supported.
  - A 1:2 ratio: contradicted.
- Reason: The source gives an equal-amount ratio, which conflicts with
  the claim's 1:2 ratio.

### Original dev line 97

- Original dataset label: `no_support`
- Claim: “Cleveland Cavaliers: 69 points.”
- Source evidence: The source lists Michael Jordan's points by opponent,
  including 2,048 against Cleveland. It does not explain what the claimed
  69 points refers to.
- Component judgment: Unsupported.
- Reason: The source does not establish the 69-point detail, and it does
  not directly state that detail is false.

## Scope and limits

These are three exploratory examples, not a representative evaluation
sample. The notes do not establish annotation agreement or validate a
component-level method. Original dataset labels remain unchanged.
