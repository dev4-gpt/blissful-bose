"""Reproduce aggregate-only paper tables; never export nested samples or replies."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [('v1', 'v1_full_n30/results.json'), ('v2', 'v2_run/results.json'),
         ('v3', 'v3_final_four_judges/results.json'),
         ('v5', 'v5_full/results_v5.json'), ('v6', 'v6_full/results_v6.json')]
NAMES = {'Qwen/Qwen2-VL-2B-Instruct': 'Qwen2-VL-2B',
         'Qwen/Qwen2.5-VL-3B-Instruct': 'Qwen2.5-VL-3B',
         'llava-hf/llava-1.5-7b-hf': 'LLaVA-1.5-7B'}


def load(root=ROOT):
    return {v: json.loads((root / p).read_text()) for v, p in FILES}


def rate(value):
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get('refuse3', value.get('rate'))
    return float(value) if value is not None else None


def rows(data):
    out = []
    old_keys = dict(A='A_llm_text', B='B_vlm_text', C='C_vlm_vision',
                    D='D_vlm_blank', E='E_vlm_phrase_text')
    for version, document in data.items():
        for model, record in document['results'].items():
            if model.startswith('_'):
                continue
            if not record.get('rates') and not record.get('judges'):
                out.append(dict(version=version, model=NAMES.get(model, model), judge='unavailable',
                                n=record.get('n', '—'), **dict.fromkeys('ABCDE'), gap=None))
                continue
            if version in ('v1', 'v2'):
                judges = {'legacy': {k: record['rates'].get(v) for k, v in old_keys.items()}}
            elif version in ('v3', 'v5'):
                judges = {j: record['judges'][j]['rates'] for j in ('qwen3guard', 'wildguard')
                          if j in record['judges']}
            else:
                judges = {j: record['rates'][j] for j in ('qwen3guard', 'wildguard')}
            for judge, values in judges.items():
                cells = {c: rate(values.get(c)) for c in 'ABCDE'}
                gap = cells['B'] - cells['C'] if None not in (cells['B'], cells['C']) else None
                out.append(dict(version=version, model=NAMES.get(model, model), judge=judge,
                                n=record['n'], **cells, gap=gap))
    return out


def percent(value):
    return '—' if value is None else f'{100 * value:.1f}'


def table(headers, records):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(str(cell).replace('|', r'\|') for cell in r) + ' |'
                      for r in records])


def blocks(data):
    r = rows(data)
    cross = table(['Version', 'Model', 'Judge', 'n', 'A %', 'B %', 'C %', 'D %', 'E %', 'B−C pp'],
                  [[x['version'], x['model'], x['judge'], x['n']] +
                   [percent(x[c]) for c in ['A', 'B', 'C', 'D', 'E', 'gap']] for x in r])
    latest = []
    for model, x in data['v6']['results'].items():
        rates = x['rates']['qwen3guard']
        gap = x['contrasts']['qwen3guard']['gap_B_minus_C']
        latest.append([NAMES.get(model, model), x['n']] +
                      [percent(rate(rates[c])) for c in ['B', 'E', 'C']] +
                      [percent(gap['diff']), ' to '.join(percent(z) for z in gap['t_ci']),
                       percent(x['unsafe_rate_all']['qwen3guard']['C'])])
    current = table(['Model', 'n', 'Plain B %', 'Text twin E %', 'Image C %',
                     'B−C pp', 'Scenario 95% CI pp', 'Unsafe C %'], latest)
    figstep = table(['Model', 'n', 'Plain %', 'Text twin %', 'Image %'],
                    [[NAMES.get(m, m), x['n']] + [percent(x['rates']['qwen3guard'][c])
                      for c in ['FS_B', 'FS_E', 'FS_F']] for m, x in data['v6']['figstep'].items()])
    coupling = table(['Version', 'Model', 'Item phi', 'Scenario Spearman'],
                     [[v, NAMES.get(m, m), f"{x['coupling']['item_phi']:.3f}",
                       f"{x['coupling']['scenario_spearman']:.3f}"] for v in ('v1', 'v2')
                      for m, x in data[v]['results'].items() if x.get('coupling')])
    steering = []
    for model, x in data['v2'].get('steering', {}).items():
        for key, value in x['results'].items():
            # Deliberately select numeric rates; the source also contains private sample text.
            if key.endswith('|0.0') or key.endswith('|0.5'):
                steering.append([NAMES.get(model, model), key, value['n'], percent(value['refusal'])])
    return dict(current=current, cross=cross, figstep=figstep, coupling=coupling,
                steering=table(['Model', 'Arm and strength', 'n', 'Refusal %'], steering))


def figure(data, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, judge, title in zip(axes, ('qwen3guard', 'wildguard'), ('Qwen3Guard', 'WildGuard')):
        models = list(data['v6']['results'])
        pos = np.arange(len(models))
        for offset, cond, label, color in [(-.24, 'B', 'Plain text (B)', '#355f8d'),
                                           (0, 'E', 'Text + benchmark wrapper (E)', '#d89038'),
                                           (.24, 'C', 'Image + benchmark wrapper (C)', '#328875')]:
            vals = [100 * rate(data['v6']['results'][m]['rates'][judge][cond]) for m in models]
            bars = ax.bar(pos + offset, vals, width=.23, label=label, color=color)
            ax.bar_label(bars, fmt='%.1f', fontsize=8, padding=3)
        ax.set_xticks(pos, [NAMES[m].replace('-Instruct', '') for m in models], fontsize=9)
        ax.set_title(title)
        ax.set_ylim(0, 100)
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.15)
        ax.set_axisbelow(True)
    axes[0].set_ylabel('Refusal rate (%)')
    axes[0].legend(loc='upper left', fontsize=8, frameon=False)
    fig.suptitle('V6 exploratory results: the apparent image gap depends on the text control', fontsize=12)
    fig.text(.5, .015, 'MM-SafetyBench: n=304 per Qwen, n=152 for LLaVA. Guard-labelled; no human validation. '
             'B and E also differ in content form.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, .95))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220)
    fig.savefig(path.with_suffix('.svg'))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-doc', type=Path)
    parser.add_argument('--write-doc', type=Path)
    parser.add_argument('--figure', type=Path)
    args = parser.parse_args()
    data = load()
    rendered = blocks(data)
    if args.write_doc:
        text = args.write_doc.read_text()
        for name, block in rendered.items():
            start, end = f'<!-- generated:{name}:start -->', f'<!-- generated:{name}:end -->'
            if start in text and end in text:
                before, rest = text.split(start, 1)
                _, after = rest.split(end, 1)
                text = before + start + '\n' + block + '\n' + end + after
        args.write_doc.write_text(text)
    if args.check_doc:
        text = args.check_doc.read_text()
        for name, block in rendered.items():
            start, end = f'<!-- generated:{name}:start -->', f'<!-- generated:{name}:end -->'
            if text.count(start) != 1 or text.count(end) != 1:
                raise SystemExit('Missing or duplicated table markers: ' + name)
            actual = text.split(start, 1)[1].split(end, 1)[0].strip()
            if actual != block:
                raise SystemExit('Table mismatch: ' + name)
        print('Every marked aggregate table matches the source result files.')
    if args.figure:
        figure(data, args.figure)
    if not args.check_doc and not args.write_doc:
        for name, block in rendered.items():
            print('\n' + name + '\n\n' + block)
        print('\nSource SHA-256:')
        for _, filename in FILES:
            print(filename, hashlib.sha256((ROOT / filename).read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
