# Localization evaluation protocol

This analysis addresses the proposal's RQ2 without equating a correct overall label with a correct decomposition. Reference labels remain distinct from the dataset's original overall labels.

The fixed exploratory sample contains 15 claims and 35 reference details: 24 supported and 11 unsupported. It has no contradicted reference details. Model outputs were seen before reference annotation; reference drafts were AI-assisted and user-reviewed. The remaining 7B alignments were completed by the assistant at the user's request, not by an independent human annotator. Ambiguities are noted in the tracked worksheets.

## Measures

1. **Matched-label agreement:** reference details for which every linked prediction has exactly the reference label, divided by matched reference details.
2. **Exact reference coverage:** the same exact-correct numerator, divided by all 35 reference details. Omissions, fallback and failures remain in the denominator.
3. **Reference-aligned error detection:** an unsupported or contradicted reference detail is a positive. It is detected if any linked model component is labeled unsupported or contradicted. Detection with the wrong error subtype is not exact labeling.

A false positive is a supported reference detail linked to an error label. A false negative is an error detail with no error-labeled match, including absent component output. Each reference is counted once even if it has multiple matches. Uncovered supported details are reported separately. Unmatched error-labeled predictions are counted separately, because they require annotation before being called false alarms. These measures are therefore **not span-level or prediction-level precision/recall**.

## Results

| Measure | Components 3B | Components 7B before verification |
|---|---:|---:|
| Matched-label agreement | 15/24 (62.50%) | 10/15 (66.67%) |
| Exact reference coverage | 15/35 (42.86%) | 10/35 (28.57%) |
| Reference-aligned error TP / FP / FN | 1 / 1 / 10 | 2 / 1 / 9 |
| Reference-aligned error precision | 50.00% | 66.67% |
| Reference-aligned error recall | 9.09% | 18.18% |
| Reference-aligned error F1 | 0.1538 | 0.2857 |
| Unmatched error predictions requiring review | 0 | 1 |

The model can detect an error while confusing unsupported with contradicted. Neither method assigns the exact correct label to any of the 11 unsupported reference details. The conditional precision values must not be presented as comprehensive localization precision. The comparison is descriptive, with different matching provenance and a small sample; it does not establish superiority on general localization.

## Reproduction

Run from the repository root:

```bash
python -m src.evaluation.evaluate_localization annotation/component_matching.json
python -m src.evaluation.evaluate_localization annotation/component_matching_7b_before_verification.json
```

The scorer validates link IDs and labels and rejects incomplete matching. Tests exercise subtype confusion, fallbacks, shared links, false alarms and unmatched predictions.


## Completed prediction and alignment audit

Run `python -m src.evaluation.complete_component_review` to regenerate the audit and supplementary tables in `results/final/`.

The original 7B worksheet contains four error-labeled predictions. A separate source-based assistant review in `annotation/localization_audit_7b.json` covers all four, including the previously unmatched “Several artists have covered it” prediction. The saved source establishes Joe Cocker alone, so rejecting “several artists” is correct relative to that source. This is not a claim that no other artists actually covered the song.

Three of four error predictions identify unsupported content, for prediction-unit binary error precision of 75%. One causal interpretation is sensitive; excluding it gives 2/3. These tiny counts do not establish reliable population precision. They must not be combined with reference-unit recall into a single F1. Complete span-level evaluation would require annotated original-claim spans and source-level reference judgments for every generated component, beyond this alignment audit.

The original contextual alignments remain unchanged. A conservative sensitivity rejects five 7B matches requiring missing recommendation, attribution, comparison or causal context to be reconstructed. Exact reference coverage becomes 6/35 (17.14%), compared with 10/35 contextually. The corresponding 3B sensitivity rejects the recommendation fragment and three changed-subject helper relations. Report both policies rather than presenting a favorable alignment as uniquely correct.

## Expanded category analysis

`annotation/expanded_mismatch_review.json` contains ten additional natural test pairs and 21 selected target details. They were purposively screened from non-complete dataset labels; model predictions were inspected after the initial source-based draft, then alignment-unit wording was refined with that exposure recorded. Every evidence quote is checked against the saved source and the source text is fingerprinted. All 21 selected detail labels were confirmed by the user after assistant-guided review of saved-source evidence and explanations (`human_reviewed=true` for all ten cases). They remain AI-assisted annotations, not independently annotated human gold.

Targets include missing dates, incorrect ranking points, absent school counts, unsupported artist/album associations, institution-to-general scope extrapolation, an unstated December restriction, a reversed winner/loser relation, changed quantitative denominators, and precision/accuracy confusion. Supported target controls are included. Cause categories overlap; direct contradiction is a support outcome, not an exclusive cause category. The source-relative targets are not necessarily real-world falsehoods.

The 3B, pre-verification 7B and verified 7B outputs are aligned to the same selected references in `annotation/expanded_mismatch_matching.json`. Generated text and labels are validated against hash-checked parent reports. An invalid linked label remains in the denominator. The additional sample is not pooled into the original 15-claim headline scores, and is not a fresh held-out test.

All proposal categories are examined descriptively across the existing and expanded samples. The small, purposive, overlapping counts still cannot support a reliable general ranking of category difficulty. The review worksheet records user confirmation separately from assistant annotation; this confirmation does not remove selection bias or prior model-output exposure.
