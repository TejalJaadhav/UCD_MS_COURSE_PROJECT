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


## NLI Comparison for Reviewed Examples

The same 15-example dev pilot included lines 29, 97, and 408. NLI outputs
are recorded here separately from the manual component judgments.

| Original dev line | Gold label | Localized-evidence NLI | Full-source NLI | Manual review |
|---:|---|---|---|---|
| 29 | `complete_support` | `entailment` | `neutral` | Matchup and score supported |
| 408 | `partial_support` | `neutral` | `neutral` | Replacement options supported; 1:2 ratio contradicted |
| 97 | `no_support` | unavailable | `contradiction` | “69 points” unsupported by the source as reviewed |

The line 97 model output and manual judgment differ. The source lists
2,048 points against Cleveland, but does not explain what the claim's
69-point figure refers to. This difference should be reviewed carefully.
NLI outputs are not treated as component labels, and the dataset gold
labels remain unchanged.

## Draft Rule for Combining Component Labels

This is a project annotation rule for further piloting. It does not change
the original dataset labels.

- `complete_support`: every independently checkable claim part is supported.
- `partial_support`: at least one part is supported, and at least one part
  is unsupported or contradicted.
- `no_support`: no claim part is supported.

A claim with both supported and contradicted parts is `partial_support`
under this draft rule. A claim with only contradicted parts is `no_support`.

### Applying the Draft Rule to Reviewed Examples

- Original dev line 29: all reviewed parts are supported. Draft overall
  judgment: `complete_support`.
- Original dev line 408: the replacement options are supported, while the
  stated ratio is contradicted. Draft overall judgment: `partial_support`.
- Original dev line 97: the source does not establish what “69 points”
  refers to, and lists 2,048 points against Cleveland. Draft overall
  judgment: uncertain. Review whether the source directly contradicts the
  claim before assigning an overall project judgment.

These draft judgments are exploratory project annotations. The dataset's
gold labels remain unchanged.