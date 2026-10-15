# Review of Very Short Training Sources

We reviewed all 10 training records with source texts of
10 words or fewer. These are initial review decisions.

| Training line | Saved source text | Review finding |
|---|---|---|
| 1518 | # Title Album Date added | Only table headings; song information is missing. |
| 1523 | # Title Album Date added | Only table headings; song information is missing. |
| 2050 | 2001 -2005 6 Seasons BBC One Drama | Usable when the saved source title is included: the title identifies Judge John Deed, and the text states “6 Seasons.” |
| 4230 | From To | Route information is missing. |
| 4233 | From To | Route information is missing. |
| 5045 | Log in Sign up | Episode information is missing. |
| 5046 | Log in Sign up | Episode information is missing. |
| 6026 | General Information | Map information is missing. |
| 6532 | ^ Back to Top | Only navigation text; bone information is missing. |
| 6872 | Damaris' Journey to Stardom | Does not establish the season number or winner. |

## Findings

For all 10 records, source_raw_text contains the same text
as source_text. It does not recover additional information.

Nine records have insufficient saved source text for reliable
comparison with their original labels.

Record 2050 needs further review because “6 Seasons” is relevant,
but the saved text does not identify the show.

## Decision

Keep the original files and labels unchanged.
Flag these records for data-quality review.

Do not replace missing source content with human-selected evidence
in the full-source experiment. That would give the model information
taken from the reference annotation.

Short length alone will not be used to remove records.