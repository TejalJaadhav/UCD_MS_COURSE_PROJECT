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


# Review of Very Short Training Sources

We reviewed 10 training records whose saved source text has
10 words or fewer.

For records 1518, 1523, 4230, 4233, 5045, 5046, 6026,
6532, and 6872, the saved source text looks too short to assess
the claim by itself.

We have not checked the source title for these nine records.
Their final status is still unknown.

Record 2050 is different. Its source title is
“Judge John Deed - Full Cast & Crew,” and its source text says
“6 Seasons.” Together, these support the claim that the show has
six series.

Original dataset labels remain unchanged.
Short source text alone is not a reason to remove a record.


## Source Title Review

We checked the source titles for all 10 records.

- Lines 1518 and 1523: The title says *Guardians of the Galaxy Vol. 3*, while the claims concern *Vol. 2*. The saved text does not include the song list.
- Line 2050: The title names *Judge John Deed*, and the text says “6 Seasons.” Together, they support the claim.
- Lines 4230 and 4233: The title describes a route to Delhi Gate. The claims discuss India Gate, and the route details are missing.
- Lines 5045 and 5046: The titles name the exact season and episodes, supporting the claims.
- Line 6026: The title identifies a map of Reggio Emilia. It does not confirm the claim about four other map sites.
- Line 6532: The title names the appendicular skeleton, but the saved text does not state the number of carpal bones.
- Line 6872: The title says “Finalists,” which does not establish that Damaris Phillips won.

These are review findings based on saved titles and text.
The original dataset labels have not been changed.