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
## Additional Reviews from the Six-Example Pilot

These are exploratory component judgments. Original dataset labels remain
unchanged.

### Original dev line 872

- Original dataset label: `complete_support`
- Claim parts:
  - Room-temperature water (20°C / 68°F) is best for flavor.
  - Chilled water (6°C / 43°F) is best for refreshment.
- Component judgments: Both parts are supported.
- Reason: The source states the same temperatures and purposes. “Flavor”
  and “flavour” are spelling variants with the same meaning.
- Draft overall judgment: `complete_support`.

### Original dev line 228

- Original dataset label: `partial_support`
- Claim parts:
  - “Non, Je Ne Regrette Rien” is an Edith Piaf song.
  - The song is sung in *Madagascar 3*.
- Component judgments:
  - Song identity: supported by the source.
  - Use in *Madagascar 3*: unsupported by the source reviewed.
- Reason: The source identifies the song and says it was featured in
  *Inception*. It does not mention *Madagascar 3*.
- Draft overall judgment: `partial_support`.

### Original dev line 32

- Original dataset label: `no_support`
- Claim parts:
  - Dallas last won the Super Bowl in 1995.
  - Dallas defeated Pittsburgh 27–17 in Super Bowl XXX.
  - The game was at Sun Devil Stadium in Arizona.
- Component judgments:
  - The 1995 win, Pittsburgh matchup, and 27–17 score: supported.
  - Sun Devil Stadium in Arizona: unsupported by the source reviewed.
- Reason: The source gives the matchup and score but does not establish the
  stadium location.
- Draft overall judgment: `partial_support`.

These draft overall judgments are project annotations for the pilot.
They do not replace or modify the dataset's gold labels.

## Component-Level NLI Scoring Check

The component scorer compared the six reviewed examples with the
`cross-encoder/nli-deberta-v3-small` model. It scored 12 components that
had recorded evidence passages and skipped two without a specific passage.

After the evidence passages were made more self-contained, the Super Bowl
components on dev lines 29 and 32 changed to `entailment`. This suggests
that the context included in an evidence passage can affect the model's
prediction.

Two differences remained:

- Dev line 408: the human component label for the 1:2 ratio was
  `contradicted`; NLI predicted `neutral`, despite the source specifying
  equal amounts.
- Dev line 97: the human component label was `unsupported`; NLI predicted
  `contradiction`. The source lists 2,048 points against Cleveland, while
  the claim's 69-point figure remains unclear. Keep this case flagged for
  review.

These results come from six exploratory examples. They are not a
performance estimate. NLI outputs are recorded separately from component
labels, and the original dataset gold labels remain unchanged.
