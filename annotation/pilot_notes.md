# Pilot Annotation Notes

## Purpose

These notes record observations from a small set of practice examples.
They will help us develop clear annotation rules before reviewing
a larger set of claims.


The judgments below are preliminary, not final annotations.

## Example 1: Limits on Sugary-Drink Sizes

### AI-Generated Claim

“Some argue that such limits would help combat obesity and other
public health concerns, while others believe that people should
be free to make their own decisions.”

### Dataset Label

`partial_support`

### Component Review

| Claim component | Initial judgment | Reason |
|---|---|---|
| Some people argue that size limits would reduce obesity. | Supported | The source presents an argument for limiting drink sizes to address obesity. |
| Size limits would address other public health concerns. | Needs review | The source discusses health education and medical costs, but it is unclear whether these support this broader phrase. |
| Others believe people should make their own choices. | Supported | The source discusses personal freedom and objections to limiting food and drink choices. |

### Possible Unsupported Detail

The phrase “other public health concerns” may go beyond the evidence
provided in the source. However, the dataset does not identify this
phrase as the reason for its partial-support label.

### Annotation Question

Should references to health education and medical costs count as
support for “other public health concerns”?

“Needs review” is a temporary note, not a final component label.

### Key Observation

The full source provides evidence that is missing from the short
human-selected passage. Component judgments should therefore consider
the full source.


## Example 2: Drink-Size Limits and Sugar Consumption

### AI-Generated Claim

“Others believe that limiting the size of sugary drinks can help
reduce sugar consumption.”

### Dataset Label

`no_support`

### Initial Review

The source describes a proposed limit on sugary-drink sizes.
It also reports that opposing companies believed the limit
would make people drink less of these beverages.

This passage may support part of the claim, so the reason for
the no-support label is not clear.


### Annotation Questions

- Does drinking less of these beverages mean consuming less sugar?
- Who does “Others” refer to in the full AI-generated response?
- Does the surrounding response help explain the claim?

### Current Decision

Keep the original dataset label.
Mark this example for further review.

### Key Observation

A human-assigned dataset label can still require review.
We should record uncertainty rather than force an explanation.

### Review of the Full AI Response

“Others” refers to people with a different opinion from those
mentioned in the previous sentence. No specific group is named.

The claim reports a belief; it does not say that reduced sugar
consumption has been scientifically proven.

The source contains a related statement about people drinking
less sugary beverages. The reason for the no-support label
therefore remains unclear.

Decision: Keep the original label and flag this example for review.

## Example 3: NHL Shots Record

The dataset labels this claim `complete_support`. The claim says
that 92 shots is the record for a single team in an NHL game.

The source says the 92-shot figure is unofficial and gives 88 as
the record in the NHL record books. The claim leaves out the word
“unofficial.”

The NLI model predicted contradiction for several source sections
and did not predict entailment for any section.

This example needs manual review. Leaving out “unofficial” may change
the meaning of the claim. Keep the original dataset label, and use
this example when we decide how to handle missing qualifiers.


### Possible label issue: dev line 726

- Dataset label: `no_support`
- The source text appears to state the claim directly.
- The human-selected evidence field is empty.
- The NLI model predicted entailment.
- Flag this example for review; keep the original dataset label unchanged for now.

### Ambiguous case: dev line 925

- Dataset label: `partial_support`
- The selected evidence gives reasons for changes in artistic style beyond changing preferences.
- The NLI model predicted entailment.
- The reason for the partial-support label is unclear from this example.
- Keep the original label unchanged and flag it for review.


### Partial-support false positive: dev line 698

- The claim includes regret, responsibility, and a remedy.
- The selected evidence mainly supports the regret part.
- The full source discusses responsibility and ways to repair harm elsewhere.
- The NLI model predicted entailment for one section, so the pilot rule marked the whole claim fully supported.
- Keep the dataset label unchanged. This example shows that one entailed section may not support every part of a claim.

### Missed support: dev line 870

- Dataset label: `complete_support`
- The human-selected evidence directly supports the claim.
- The NLI model predicted `neutral` for the strongest section.
- This may be a model miss on a context-dependent claim.
- Keep the dataset label unchanged.


### Missed support with a qualification: dev line 1009

- Dataset label: `complete_support`
- The selected evidence lists the same Silver, Gold, and Diamond subscriber thresholds as the claim.
- The NLI model predicted `neutral` for its strongest section.
- The source later says awards are not automatic and depend on eligibility, which may add ambiguity.
- Keep the dataset label unchanged.

### Missed support with an unclear reference: dev line 361

- Dataset label: `complete_support`
- The selected evidence directly supports the facts about Wai.
- The NLI model predicted `neutral` for its strongest section.
- The phrase “Some of them” may need context from before the claim.
- Keep the dataset label unchanged.

### Missed direct evidence: dev line 320

- Dataset label: `complete_support`
- The human-selected evidence directly matches the claim.
- The NLI model predicted `neutral` for its strongest section.
- Keep the dataset label unchanged.


### Pilot limitation: partial support

This pilot predicts only two groups: `fully_supported` and `not_fully_supported`. It does not predict `partial_support` by itself.

The current rule calls a claim fully supported if any one source section gets an entailment prediction. For a claim with several parts, that section may support only some of them. We need a better rule before the model can reliably separate complete support from partial support.