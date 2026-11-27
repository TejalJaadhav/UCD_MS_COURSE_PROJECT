"""Evaluate error detection on reviewed reference alignments, without model calls."""

import argparse
import json
from collections import Counter
from pathlib import Path

LABELS = {'supported', 'unsupported', 'contradicted'}
NEGATIVE = {'unsupported', 'contradicted'}


def score(rows):
    if not rows or len({r['example_id'] for r in rows}) != len(rows):
        raise ValueError('Expected unique, nonempty reviewed examples.')
    counts = Counter()
    categories = {}
    for row in rows:
        if row.get('matching_reviewed') is not True:
            raise ValueError('Unreviewed matching.')
        predicted = {p['prediction_number']: p['label'] for p in row['predicted_parts']}
        if len(predicted) != len(row['predicted_parts']):
            raise ValueError('Duplicate prediction numbers.')
        if any(label not in LABELS and label is not None for label in predicted.values()):
            raise ValueError('Invalid predicted label.')
        used = set()
        for ref in row['reference_parts']:
            truth = ref['label']
            links = ref['matched_prediction_numbers']
            status = ref['match_status']
            if truth not in LABELS or len(links) != len(set(links)):
                raise ValueError('Invalid reference or duplicated links.')
            if status == 'matched':
                if not links or not set(links) <= predicted.keys():
                    raise ValueError('Missing or unknown prediction links.')
            elif status in {'omitted', 'no_component_output'}:
                if links:
                    raise ValueError('Unmatched reference has prediction links.')
            else:
                raise ValueError('Unknown matching status.')
            used.update(links)
            labels = [predicted[n] for n in links]
            actual_error = truth in NEGATIVE
            detected_error = any(label in NEGATIVE for label in labels)
            exact = bool(labels) and all(label == truth for label in labels)
            counts['reference_details'] += 1
            counts['matched'] += bool(labels)
            counts['exact_correct'] += exact
            counts['tp'] += actual_error and detected_error
            counts['fp'] += not actual_error and detected_error
            counts['fn'] += actual_error and not detected_error
            counts['uncovered'] += not bool(labels)
            counts['invalid_linked_judgment'] += any(label is None for label in labels)
            counts['uncovered_supported'] += truth == 'supported' and not labels
            for category in set(ref.get('mismatch_types', [])):
                group = categories.setdefault(category, Counter())
                group['total'] += 1
                group['exact_correct'] += exact
                group['detected_as_error'] += actual_error and detected_error
                group['no_output'] += not bool(labels)
        # Do not silently treat unmatched predictions as false alarms: they
        # need independent annotation before prediction-level precision exists.
        counts['unmatched_error_predictions'] += sum(
            label in NEGATIVE for n, label in predicted.items() if n not in used
        )
    precision = counts['tp'] / (counts['tp'] + counts['fp']) if counts['tp'] + counts['fp'] else None
    recall = counts['tp'] / (counts['tp'] + counts['fn']) if counts['tp'] + counts['fn'] else None
    f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else 0.0 if recall is not None else None
    return {
        'claims': len(rows), 'counts': dict(counts),
        'reference_aligned_error_detection': {'precision': precision, 'recall': recall, 'f1': f1},
        'exact_reference_coverage': counts['exact_correct'] / counts['reference_details'],
        'categories': {k: dict(v) for k, v in sorted(categories.items())},
        'limitations': [
            'Exploratory reference-aligned metrics, not span-level or prediction-level precision.',
            'Any linked unsupported/contradicted label detects a reference error; exact correctness requires all linked labels to equal the reference label.',
            'Missing error details, including fallbacks, count as false negatives. Uncovered supported details are reported separately.',
            'Many-to-many alignments count once per reference detail. Unmatched error predictions require review and are not included as false positives.',
            'Reference annotation and model matching provenance are recorded separately; assistant-completed matches are not independent human review.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('worksheet', type=Path)
    args = parser.parse_args()
    rows = json.loads(args.worksheet.read_text(encoding='utf-8'))
    print(json.dumps(score(rows), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
