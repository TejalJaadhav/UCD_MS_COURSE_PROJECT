# Component Review Pilot

## Purpose

This pilot explores whether reviewing individual claim parts helps explain how
a cited source supports a claim. The review began with three dev examples,
expanded to six, and then included a 12-example NLI scoring run. The manual
component judgments and draft overall judgments are recorded alongside the
original dataset labels.

## Initial Three Reviewed Examples

### Original dev line 29

- Original dataset label: `complete_support`
- Claim: Dallas won Super Bowl XXX against the Pittsburgh Steelers, 27–17.
- Source evidence: The source lists the Super Bowl XXX win against Pittsburgh
  and gives the same score.
- Component judgment: The win, opponent, and score are supported.
- Draft overall judgment: `complete_support`

### Original dev line 408

- Original dataset label: `partial_support`
- Claim: Cream of tartar can be replaced with vinegar or lemon juice in a 1:2 ratio.
- Source evidence: The source says to use an equal amount of lemon juice or
  distilled white vinegar.
- Component judgments: Both replacement options are supported. The 1:2 ratio
  is contradicted by the equal-amount instruction.
- Draft overall judgment: `partial_support`

### Original dev line 97

- Original dataset label: `no_support`
- Claim: “Cleveland Cavaliers: 69 points.”
- Source evidence: The source lists 2,048 points against Cleveland in a table
  of Michael Jordan's points by opponent. The claim leaves the meaning of the
  69-point figure unclear.
- Component judgment: The 69-point figure is unsupported by the reviewed passage.
- Draft overall judgment: `uncertain`, pending review of what the figure refers to.

## NLI Comparison for the Initial Examples

The earlier 15-example dev pilot scored whole claims using the full source
or the dataset's localized evidence when available.

| Original dev line | Gold label | Localized evidence NLI | Full source NLI |
|---:|---|---|---|
| 29 | `complete_support` | `entailment` | `neutral` |
| 408 | `partial_support` | `neutral` | `neutral` |
| 97 | `no_support` | Unavailable | `contradiction` |

For line 97, the NLI prediction was `contradiction`, while the manual review
marked the 69-point figure as unsupported. The source's 2,048-point total
and the claim's 69-point figure may refer to different measures.

## Draft Rule for Combining Component Judgments

- `complete_support`: Every independently checkable claim part is supported.
- `partial_support`: At least one part is supported and at least one is
  unsupported or contradicted.
- `no_support`: The review is conclusive and none of the claim parts is supported.
- `uncertain`: An unresolved ambiguity prevents an overall judgment. This is
  a review status for the pilot.

## Additional Reviews from the Six-Example Pilot

### Original dev line 872

- Original dataset label: `complete_support`
- Claim parts: Room-temperature water (20°C / 68°F) is best for flavor, and
  chilled water (6°C / 43°F) is best for refreshment.
- Component judgments: The source supports both temperature and purpose pairings.
- Draft overall judgment: `complete_support`

### Original dev line 228

- Original dataset label: `partial_support`
- Claim parts: “Non, Je Ne Regrette Rien” is an Edith Piaf song, and it is sung
  in *Madagascar 3*.
- Component judgments: The source supports the song identity. It mentions
  *Inception* and leaves the claim about *Madagascar 3* unsupported.
- Draft overall judgment: `partial_support`

### Original dev line 32

- Original dataset label: `no_support`
- Claim parts: Dallas last won the Super Bowl in 1995, defeated Pittsburgh
  27–17 in Super Bowl XXX, and played the game at Sun Devil Stadium in Arizona.
- Component judgments: The reviewed source supports the 1995 win, opponent,
  and score. It leaves the stadium location unsupported.
- Draft overall judgment: `partial_support`

## Component NLI Scoring on Six Examples

The `cross-encoder/nli-deberta-v3-small` model scored 12 components with
recorded evidence passages and skipped two without a specific passage.

After the evidence passages were revised to include more context, the
prediction for the Dallas win on line 29 changed from `contradiction` to
`entailment`. The prediction for the matchup and score on line 32 changed
from `neutral` to `entailment`. These changes show that the choice of passage
can affect the prediction.

Two differences remained:

- Dev line 408: The reviewer marked the 1:2 ratio `contradicted` because the
  source specifies equal amounts. NLI predicted `neutral`.
- Dev line 97: The reviewer marked the 69-point figure `unsupported`.
  NLI predicted `contradiction`.

## Twelve-Example Scoring Summary

In the expanded pilot, the NLI model scored 25 claim components. Four
components were skipped because they had no recorded evidence passage.
The model often predicted `entailment` for components marked supported by
the reviewer. It also predicted `neutral` for some components marked
supported or contradicted, and `contradiction` for some marked unsupported.

These comparisons show where model predictions and manual judgments differ
on this pilot. The run reported descriptive results and did not calculate
accuracy. The pilot judgments and model outputs are recorded separately
from the original dataset labels.


## Context Check for Dev Line 874

The original evidence passage gave the game counts but omitted the
preceding explanation that each team plays every other team. We expanded
both component evidence passages to include that explanation and the
number of teams.

Both predictions remained neutral. The neutral score changed from 0.9914
to 0.9981 for the men's and women's component, and from 0.8953 to 0.9830
for mixed doubles.

The expanded passage supports the reviewed game counts and tournament
format, but the model still failed to recognize support. This case
illustrates a limitation of the current NLI setup.