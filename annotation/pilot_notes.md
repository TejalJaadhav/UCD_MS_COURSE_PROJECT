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