"""Validate and score the expanded review and localization sensitivity audit."""

import copy
import hashlib
import json
from pathlib import Path
from src.evaluation.evaluate_localization import score
from src.evaluation.overall import load_split

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def strict_rows(rows, decisions):
    rows = copy.deepcopy(rows)
    for decision in decisions:
        row = next(r for r in rows if r['example_id'] == decision['example_id'])
        ref = next(p for p in row['reference_parts'] if p['reference_number'] == decision['reference_number'])
        ref.update(matched_prediction_numbers=[], match_status='omitted')
    return rows


def main():
    audit = read('annotation/localization_audit_7b.json')
    worksheet = read(audit['worksheet'])
    expected = {(r['example_id'], p['prediction_number']): p for r in worksheet
                for p in r['predicted_parts'] if p['label'] in {'unsupported','contradicted'}}
    actual = {(r['example_id'], r['prediction_number']): r for r in audit['prediction_reviews']}
    if len(actual) != len(audit['prediction_reviews']) or expected.keys() != actual.keys():
        raise ValueError('Every error-labeled prediction needs one adjudication.')
    records, fingerprint = load_split('test', 'cleaned')
    sources = {r['example_id']: r for r in records}
    for key, review in actual.items():
        if review['text'] != expected[key]['text'] or review['predicted_label'] != expected[key]['label']:
            raise ValueError('Audit differs from generated prediction.')
        if review['reference_label'] not in {'supported','unsupported','contradicted'}:
            raise ValueError('Invalid prediction-level reference.')
        if review.get('source_quote') and review['source_quote'] not in sources[key[0]]['source']:
            raise ValueError('Invalid source quote.')
    positives = list(actual.values())
    correct = sum(r['reference_label'] in {'unsupported','contradicted'} for r in positives)
    unambiguous = [r for r in positives if not r.get('interpretation_sensitive')]
    prediction_precision = dict(correct_binary_error_predictions=correct,
                                total_error_predictions=len(positives),precision=correct/len(positives),
                                excluding_interpretation_sensitive_precision=sum(r['reference_label'] in {'unsupported','contradicted'} for r in unambiguous)/len(unambiguous),
                                caveat='Prediction-level precision on assistant-reviewed error outputs; do not combine with reference-unit recall as a single F1.')
    supplement = read('annotation/expanded_mismatch_review.json')
    matches = read('annotation/expanded_mismatch_matching.json')
    if supplement['dataset_sha256'] != fingerprint:
        raise ValueError('Dataset changed.')
    for case in supplement['cases']:
        source = sources[case['example_id']]
        if source['claim'] != case['claim'] or hashlib.sha256(source['source'].encode()).hexdigest() != case['source_sha256']:
            raise ValueError('Supplement differs from source record.')
        if any(p['evidence_quote'] not in source['source'] for p in case['reference_parts']):
            raise ValueError('Invalid supplemental source quote.')
    scores = {}
    for method, bundle in matches.items():
        path=ROOT/'outputs/annotation_pilot/evaluation'/bundle['parent_report']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=bundle['parent_report_sha256']:
            raise ValueError('Parent report changed.')
        original={r['example_id']:r for r in json.loads(path.read_text())['predictions']}
        expected_references={r['example_id']:r for r in supplement['cases']}
        if len(bundle['rows'])!=len(expected_references) or {r['example_id'] for r in bundle['rows']}!=expected_references.keys():
            raise ValueError('Supplementary case IDs differ.')
        for row in bundle['rows']:
            expected_parts=expected_references[row['example_id']]['reference_parts']
            if len(expected_parts)!=len(row['reference_parts']): raise ValueError('Reference detail count differs.')
            for expected_ref,saved_ref in zip(expected_parts,row['reference_parts']):
                if any(expected_ref[k]!=saved_ref[k] for k in ['text','label','mismatch_types']):
                    raise ValueError('Supplementary reference differs from frozen annotation.')
            generated=(original[row['example_id']].get('details') or {}).get('components',[])
            if len(generated)!=len(row['predicted_parts']): raise ValueError('Prediction count differs.')
            for saved,part in zip(generated,row['predicted_parts']):
                if saved['component']!=part['text'] or saved['label']!=part['label']: raise ValueError('Prediction modified.')
        scores[method]=score(bundle['rows'])
    original_3b=read('annotation/component_matching.json')
    strict_3b=[dict(example_id='test_00154',reference_number=1)]+[dict(example_id='test_01094',reference_number=n) for n in [4,5,6]]
    result=dict(original_3b_contextual_alignment=score(original_3b),
                original_3b_strict_alignment=score(strict_rows(original_3b,strict_3b)),
                strict_3b_note='Reject recommendation fragment and the three film-as-helper-subject distortions. Original contextual matches preserved.',
                original_7b_contextual_alignment=score(worksheet),
                original_7b_strict_alignment=score(strict_rows(worksheet,audit['alignment_sensitivity'])),
                prediction_level_error_precision=prediction_precision,
                expanded_targeted_review=scores,
                provenance=f"Supplement: 10 natural test pairs, 21 selected target details; AI-assisted annotations; user-confirmed cases: {sum(bool(c.get('human_reviewed')) for c in supplement['cases'])}/{len(supplement['cases'])}; not independent human gold. Original 15-claim review kept separate. No representative sampling or category ranking claimed.")
    folder=ROOT/'results/final';folder.mkdir(parents=True,exist_ok=True)
    (folder/'completed_component_review.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Expanded targeted mismatch review','',result['provenance'],'',
           '| Method | Target details | Exact-correct labels | Error detection TP / FP / FN |',
           '|---|---:|---:|---|']
    for method,item in scores.items():
        c=item['counts']; lines.append(f"| {method} | {c['reference_details']} | {c['exact_correct']} | {c['tp']} / {c['fp']} / {c['fn']} |")
    lines += ['', 'These are selected targets, not exhaustive claim decompositions. Counts are descriptive and do not rank general category difficulty.', '',
              '| Category | Details | 3B exact correct | 7B exact correct | Verified 7B exact correct |','|---|---:|---:|---:|---:|']
    categories=sorted(set().union(*(r['categories'] for r in scores.values())))
    for category in categories:
        groups=[scores[m]['categories'].get(category,{}) for m in ['3b','7b','verified7b']]
        lines.append(f"| {category} | {groups[0].get('total',0)} | {groups[0].get('exact_correct',0)} | {groups[1].get('exact_correct',0)} | {groups[2].get('exact_correct',0)} |")
    lines+=['','Contradiction is a reference-label outcome, not a mutually exclusive mismatch cause. Category tags overlap. Numbers, dates, entities, qualifier restrictions, scope and unsupported additions are represented; conceptual relation is an extra category.', '',
            'Review status is recorded per case in the annotation file; confirmation followed assistant-guided evidence review. A source quote attached to an unsupported target provides context, not a proof of absence. Historical sources are assessed as saved, not against current world facts.']
    (folder/'expanded_review_table.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines));print('\n7B error-prediction precision:',prediction_precision)
    for mode in ['original_7b_contextual_alignment','original_7b_strict_alignment']:
        print(mode, result[mode]['counts'], result[mode]['exact_reference_coverage'])
    print('\nSaved:',folder/'completed_component_review.json')


if __name__=='__main__':
    main()
