"""Validate aggregate-only evidence and regenerate the visual development report tables.

No inference, private response reads, dataset access or network calls.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'visual_development_20261026/numeric_summary.json'
REPORT = ROOT / 'docs/VISUAL_ATTACKS_DEVELOPMENT_RESULTS.md'
GUIDE = ROOT / 'docs/VISUAL_ATTACKS_END_TO_END_GUIDE.md'


def render(data):
    rows = data['rows']
    audit = data['case_audit']
    assert len(rows) == 24 and len(audit) == 68
    assert len({(r['model'], r['method'], r['case_id']) for r in audit}) == 68
    lines = [
        '| Model | Variant | n | Clean correct | Attack correct | Attack target | Random correct | Defended attack correct | Defended attack target | Objective decreased |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for row in rows:
        c = row['conditions']
        matching = [r for r in audit if (r['model'], r['method']) == (row['model'], row['method'])]
        assert len(matching) == c['clean'][0]
        for condition, values in c.items():
            subset = [r['conditions'][condition] for r in matching if condition in r['conditions']]
            assert values[:3] == [len(subset), sum(v['correct_exact'] for v in subset),
                                  sum(v['target_match'] for v in subset)]
            assert 0 <= values[3] <= values[0]
        n = c['clean'][0]
        objective = f"{row['objective_decreased']}/{row['objective_n']}" if row['objective_n'] else 'N/A'
        values = [row['model'], row['method'], n, c['clean'][1], c['attack'][1],
                  c['attack'][2], c['random_control'][1], c['defended_attack'][1],
                  c['defended_attack'][2], objective]
        lines.append('| ' + ' | '.join(map(str, values)) + ' |')
    assert all(d['response_calls'] == 240 and d['cap_hits'] == 0 for d in data['diagnostics'].values())
    assert all(v['n'] == 4 and v['attack_target'] == 0 for v in data['transfer'].values())
    # Exact source identities, not filenames alone, distinguish this execution from the prior panel.
    assert data['source_sha256'] == '6832b9a0febbf910c71574c52ea910c9f355fa158ae2dea02fb339ae9d11747c'
    cost = ['| Quantity | Qwen | SmolVLM |', '|---|---:|---:|']
    for key in ('load_seconds', 'elapsed_seconds', 'case_seconds', 'generation_seconds',
                'generation_peak_gb', 'observed_pre_generation_peak_gb', 'processor_max',
                'logits_max', 'linf_max_bounded', 'response_calls', 'cap_hits'):
        cost.append('| ' + key + ' | ' + ' | '.join(str(data['diagnostics'][m][key]) for m in ('qwen', 'smol')) + ' |')
    asr = ['| Variant | Primary condition | Qwen target ASR | Qwen + prefix | Smol target ASR | Smol + prefix |',
           '|---|---|---:|---:|---:|---:|']
    index = {(r['model'], r['method']): r for r in rows}
    for method in sorted({r['method'] for r in rows}):
        primary = {'injection': 'injection', 'bimodal': 'combined'}.get(method, 'attack')
        values = []
        for model in ('qwen', 'smol'):
            conditions = index[model, method]['conditions']
            for condition in (primary, 'defended_attack'):
                n, _, hits, _ = conditions[condition]
                assert n > 0
                values.append(f'{hits}/{n} ({100*hits/n:g}%)')
        asr.append('| ' + ' | '.join([method, primary] + values) + ' |')
    # Reconcile the worked example without treating a pre-existing capability failure as induced.
    smol_pgd = [r for r in audit if r['model'] == 'smol' and r['method'] == 'pgd']
    assert sum(r['conditions']['clean']['correct_exact'] for r in smol_pgd) == 3
    assert sum(r['conditions']['clean']['correct_exact'] and not r['conditions']['attack']['correct_exact']
               for r in smol_pgd) == 2
    return {'OUTCOMES': '\n'.join(lines), 'COST': '\n'.join(cost), 'ASR': '\n'.join(asr)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Update only marked report tables')
    args = parser.parse_args()
    tables = render(json.loads(DATA.read_text()))
    for document, names in ((REPORT, ('OUTCOMES', 'COST')), (GUIDE, ('ASR',))):
        text = document.read_text()
        for name in names:
            start, end = f'<!-- {name}:START -->', f'<!-- {name}:END -->'
            assert text.count(start) == text.count(end) == 1
            prefix, tail = text.split(start)
            old, suffix = tail.split(end)
            expected = '\n\n' + tables[name] + '\n\n'
            if args.write:
                text = prefix + start + expected + end + suffix
            else:
                assert old == expected, f'{document.name}: {name} differs from saved evidence'
        if args.write:
            document.write_text(text)
    print('PASS: 68 records, 24 variant rows, paired example, outcome/cost/primary-condition ASR tables')


if __name__ == '__main__':
    main()
