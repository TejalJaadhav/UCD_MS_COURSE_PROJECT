# Manual Annotation

This folder will contain guidelines and human annotations
for a selected subset of training examples.

Each claim component will be labeled:
- Supported: the cited evidence establishes the component.
- Unsupported: the cited evidence does not establish it.
- Contradicted: the cited evidence directly conflicts with it.

The annotation guidelines will be refined through a pilot
before the full subset is annotated.

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
