"""Package exact saved-data analysis inputs; never include keys, venvs or model weights."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.evaluation.build_final_results import RUNS
from src.evaluation.overall import evaluate

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'outputs/annotation_pilot/evaluation'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members.')
        manifest = json.loads(archive.read('MANIFEST.json'))
        if set(names) != set(manifest['files']) | {'MANIFEST.json'}:
            raise ValueError('Unexpected or missing archive members.')
        for name, info in manifest['files'].items():
            if name.startswith('/') or '..' in Path(name).parts:
                raise ValueError('Unsafe archive path.')
            data = archive.read(name)
            if len(data) != info['bytes'] or sha(data) != info['sha256']:
                raise ValueError(f'Archive content mismatch: {name}')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.verify:
        if args.output:
            parser.error('Choose output or verify, not both.')
        manifest = verify(args.verify)
        print(f"Verified {len(manifest['files'])} checksummed files.")
        return
    if not args.output:
        parser.error('--output or --verify is required.')
    if args.output.exists():
        parser.error('Output already exists; choose a new filename.')
    required = [FOLDER / name for _, name in RUNS]
    required += [ROOT/'outputs/preprocessing/cleaned/test.jsonl.gz',
                 FOLDER/'mismatch_review_verified_20261122T193333_338992Z.json']
    for path in required:
        if not path.is_file():
            raise ValueError(f'Missing required artifact: {path}')
    for _, filename in RUNS:
        evaluate(json.loads((FOLDER/filename).read_text(encoding='utf-8')))
    paths = set(required)
    for directory, pattern in [('src','*.py'),('tests','*.py'),('annotation','*.json')]:
        paths.update((ROOT/directory).rglob(pattern))
    paths.update((ROOT/'tests/fixtures').glob('*.json'))
    for name in ['requirements.txt','requirements-analysis.txt','README.md','data/README.md',
                 'experiments/evaluation_summary.json','docs/localization_evaluation.md']:
        paths.add(ROOT/name)
    for name in ['metrics.json','completed_component_review.json','overall_results.png',
                 'overall_results.pdf','confusion_7b.png','confusion_7b.pdf',
                 'expanded_review_table.md','overall_table.md','dependency_snapshot.json',
                 'model_inventory.json','cli_smoke_results.json','run_settings.json']:
        path=ROOT/'results/final'/name
        if path.exists(): paths.add(path)
    files={}
    for path in sorted(paths):
        relative=path.relative_to(ROOT).as_posix()
        if path.is_symlink(): raise ValueError('Symlinks are not packaged.')
        data=path.read_bytes()
        files[relative]={'bytes':len(data),'sha256':sha(data)}
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())
    manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),'git_head':git_head,
              'working_tree_has_uncommitted_changes':git_dirty,'python':sys.version,
              'platform':platform.platform(),'files':files,
              'scope':'Saved test-analysis reproduction, not a guarantee of identical fresh model generations. Includes the exact compressed cleaned-test snapshot required by existing dataset fingerprints.',
              'annotation_status':json.loads((ROOT/'annotation/expanded_mismatch_review.json').read_text())['provenance'],
              'commands':['python -m unittest discover -s tests',
                          'python -m src.evaluation.compare_runs outputs/annotation_pilot/evaluation/*_test_*.json',
                          'python -m src.evaluation.complete_component_review',
                          'python -m src.evaluation.build_final_results'],
              'data_attribution':'Liu, Zhang, and Liang (2023), Evaluating Verifiability in Generative Search Engines. Original dataset authors retain attribution; source text and source labels are preserved.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            archive.write(ROOT/relative,relative)
        archive.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    verify(args.output)
    print(f'Packaged and verified {len(files)} files: {args.output.resolve()}')


if __name__=='__main__':
    main()
