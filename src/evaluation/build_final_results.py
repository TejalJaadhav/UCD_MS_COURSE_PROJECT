"""Build validated final tables and figures from explicit saved reports."""

import json
from pathlib import Path
from src.evaluation.overall import evaluate
from src.evaluation.evaluate_localization import score

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'outputs/annotation_pilot/evaluation'
RUNS = [
    ('Majority', 'majority_test_20261111T221104_803708Z.json'),
    ('NLI', 'nli_test_20261111T221445_798912Z.json'),
    ('Whole-claim 3B', 'llm_test_20261112T034120_341499Z.json'),
    ('Components 3B', 'components_test_20261112T201634_714712Z.json'),
    ('Components 7B', 'components_verified_test_20261126T014726_177544Z_before_verification.json'),
    ('Verified 7B', 'components_verified_test_20261126T014726_177544Z.json'),
]


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    output = ROOT / 'results/final'
    output.mkdir(parents=True, exist_ok=True)
    reports, fingerprint, example_ids = {}, None, None
    for name, filename in RUNS:
        report = json.loads((FOLDER / filename).read_text(encoding='utf-8'))
        measured = evaluate(report)
        if fingerprint is None:
            fingerprint, example_ids = report['dataset_sha256'], set(report['example_ids'])
        if report['dataset_sha256'] != fingerprint or set(report['example_ids']) != example_ids:
            raise ValueError('Evaluation examples differ.')
        reports[name] = {'report': filename, 'metrics': measured}
    localization = {}
    for name, filename in [('Components 3B', 'component_matching.json'),
                            ('Components 7B', 'component_matching_7b_before_verification.json')]:
        localization[name] = score(json.loads((ROOT / 'annotation' / filename).read_text()))
    references = {r['example_id']: r for r in json.loads((ROOT / 'annotation/mismatch_review.json').read_text())}
    review = json.loads((ROOT / 'annotation/mismatch_diagnostic_review.json').read_text())
    predictions = {r['example_id']: r for r in json.loads((FOLDER / review['prediction_report']).read_text())['predictions']}
    categories = {}
    for case in review['cases']:
        parts = references[case['example_id']]['reference_parts']
        actual_parts = predictions[case['example_id']].get('details', {}).get('components', [])
        for match in case['reference_matches']:
            ref = parts[match['reference_number'] - 1]
            if ref['label'] != match['reference_label']:
                raise ValueError('Diagnostic reference label differs.')
            labels = [actual_parts[n - 1]['label'] for n in match['prediction_numbers']]
            if any(label != match['predicted_label'] for label in labels):
                raise ValueError('Diagnostic predicted label differs.')
            if not labels and match['predicted_label'] is not None:
                raise ValueError('Missing diagnostic output not marked null.')
            for tag in set(ref['mismatch_types']):
                group = categories.setdefault(tag, {'total': 0, 'correct': 0, 'no_output': 0})
                group['total'] += 1
                group['correct'] += bool(labels) and all(label == ref['label'] for label in labels)
                group['no_output'] += not bool(labels)
    artifact = {'dataset_sha256': fingerprint, 'overall': reports,
                'localization': localization, 'targeted_verified_diagnostics': categories,
                'diagnostic_note': 'Overlapping categories; targeted nonrepresentative examples; not pooled with test review.'}
    (output / 'metrics.json').write_text(json.dumps(artifact, indent=2) + '\n')
    table = ['| Method | Accuracy | Macro-F1 | Failures |', '|---|---:|---:|---:|']
    for name, item in reports.items():
        m = item['metrics']
        table.append(f"| {name} | {m['accuracy']:.2%} | {m['macro_f1']:.4f} | {m['failed']} |")
    (output / 'overall_table.md').write_text('\n'.join(table) + '\n')
    names = list(reports)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for ax, measure, title in zip(axes, ['accuracy', 'macro_f1'], ['Accuracy', 'Macro-F1']):
        values = [reports[n]['metrics'][measure] for n in names]
        bars = ax.barh(names, values, color=['#808080'] * 4 + ['#2878b5', '#ca7635'])
        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.set_title(title)
        ax.bar_label(bars, fmt='%.3f', padding=3)
        ax.grid(axis='x', alpha=.2)
        ax.set_axisbelow(True)
    fig.suptitle('Overall support classification — 1,085 cleaned test pairs')
    fig.savefig(output / 'overall_results.png', dpi=200)
    fig.savefig(output / 'overall_results.pdf')
    plt.close(fig)
    matrix = reports['Components 7B']['metrics']['confusion_matrix']
    labels = ['complete_support', 'partial_support', 'no_support']
    data = [[matrix[g][p] for p in labels + ['failed']] for g in labels]
    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
    image = ax.imshow(data, cmap='Blues')
    ax.set_xticks(range(4), ['Complete', 'Partial', 'No support', 'Failed'])
    ax.set_yticks(range(3), ['Complete', 'Partial', 'No support'])
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('Dataset label')
    ax.set_title('Components 7B before verification — confusion counts')
    for i, row in enumerate(data):
        for j, number in enumerate(row):
            ax.text(j, i, str(number), ha='center', va='center', color='white' if number > max(map(max, data)) / 2 else 'black')
    fig.colorbar(image, ax=ax)
    fig.savefig(output / 'confusion_7b.png', dpi=200)
    fig.savefig(output / 'confusion_7b.pdf')
    plt.close(fig)
    print('Validated all six reports and diagnostic labels.')
    print('Generated:', output)


if __name__ == '__main__':
    main()
