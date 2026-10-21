"""Refresh local reading notices, preserving all experiment code and outputs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = '<!-- project-status:start -->'
END = '<!-- project-status:end -->'


def code_digest(nb):
    code = [c for c in nb['cells'] if c['cell_type'] == 'code']
    return hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest()


def refresh(path):
    nb = json.loads(path.read_text())
    before = code_digest(nb)
    name = path.name
    if name == 'vlm_window_study.ipynb':
        role = ('Completed GPU study: 32 responses, 64 units, 128 guard evaluations, '
                'zero failures. Both guards retained all paired labels; eight full cap hits. '
                'New human review is pending. CPU defaults display saved outcomes; do not rerun generation.')
    elif name == 'vlm_project_companion.ipynb':
        role = 'Current aggregate-only walkthrough. Run all uses CPU and makes zero model calls.'
    elif name == 'vlm_next_stage_human_validation.ipynb':
        role = ('Earlier 48-answer review tooling. That original assisted human review and auxiliary '
                'LLM comparison are recorded separately. The next annotation is the new 64-unit window packet.')
    else:
        role = ('Historical experiment or preparation notebook. Its original code and outputs are retained. '
                'Read its dated claims alongside the current result ledger; it is not the next run to launch.')
    notice = (START + '\n**Project status — 20 October 2026.** ' + role + '\n\n'
              'Read [the complete explanation and advisor walkthrough](../docs/STATUS_AND_PAPER_PLAN.md) '
              '(especially §§17–18), or [the unified companion](vlm_project_companion.ipynb). '
              'The predicted matched crossover was not observed. All studies remain exploratory; '
              'reserved confirmation is locked. Original executed archives and private annotations stay on college Drive.\n'
              + END + '\n\n')
    first = next(c for c in nb['cells'] if c['cell_type'] == 'markdown')
    text = ''.join(first['source'])
    if START in text:
        left, tail = text.split(START, 1)
        _, right = tail.split(END, 1)
        text = left + right.lstrip('\n')
    first['source'] = (notice + text).splitlines(True)
    assert code_digest(nb) == before, 'A reading update must not change code or outputs'
    pretty = path.name in {'vlm_modality_tradeoff'+v+'.ipynb' for v in ('', '_v2', '_v3', '_v4', '_v5', '_v6')}
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1 if pretty else None) + '\n')


if __name__ == '__main__':
    paths = sorted(p for p in (ROOT/'notebooks').glob('vlm_*.ipynb'))
    for path in paths:
        refresh(path)
    print('Updated reading status in', len(paths), 'local notebooks; code/output cells unchanged.')
