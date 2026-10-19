"""Aggregate-only exploratory reanalysis of the frozen v6 scientific run.

No inference, private caches, new labels or confirmatory outcomes are read.
Paired transitions are reconstructed from saved valid-pair counts and margins,
then checked against every stored margin. Raw/harm transitions are unavailable.
"""
import hashlib
import json
import math
from pathlib import Path

MODELS = {
    'Qwen/Qwen2-VL-2B-Instruct': 'Qwen2-VL-2B',
    'Qwen/Qwen2.5-VL-3B-Instruct': 'Qwen2.5-VL-3B',
    'llava-hf/llava-1.5-7b-hf': 'LLaVA-1.5-7B',
}
GUARDS = ('qwen3guard', 'wildguard')
MAIN_PAIRS = {
    'gap_B_minus_C': ('B', 'C'),
    'P_B_minus_E': ('B', 'E'),
    'modality_E_minus_C': ('E', 'C'),
    'modW0_Ftxt_minus_Fimg': ('F_txt', 'F_img'),
    'modW1_W1txt_minus_W1img': ('W1_txt', 'W1_img'),
    'modW2_Gfull_minus_W2img': ('G_full', 'W2_img'),
}
FS_PAIRS = {
    'gap_FSB_minus_FSF': ('FS_B', 'FS_F'),
    'wrapper_FSB_minus_FSE': ('FS_B', 'FS_E'),
    'modality_FSE_minus_FSF': ('FS_E', 'FS_F'),
    'modalityW0_FSW0t_minus_FSW0i': ('FS_W0t', 'FS_W0i'),
}


def number(value, lower=None, upper=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite numeric aggregate')
    if (lower is not None and value < lower) or (upper is not None and value > upper):
        raise ValueError('Aggregate outside its declared bounds')
    return float(value)


def count(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError('Expected a nonnegative integer count')
    return value


def paired_counts(contrast):
    """2x2: a-only, b-only, both, neither, on jointly valid saved pairs."""
    n = count(contrast['n'])
    if not n:
        raise ValueError('Empty paired comparison')
    a, b = number(contrast['rate_a'], 0, 1), number(contrast['rate_b'], 0, 1)
    off_a, off_b = (count(x) for x in contrast['mcnemar_b_c_p'][:2])
    margin = a*n
    if not math.isclose(margin, round(margin), abs_tol=1e-7):
        raise ValueError('Saved paired margin is not an integer count')
    both = round(margin)-off_a
    neither = n-off_a-off_b-both
    cells = [neither, off_b, off_a, both]
    if any(x < 0 for x in cells) or sum(cells) != n:
        raise ValueError('Inconsistent saved paired table')
    if not math.isclose((both+off_b)/n, b, abs_tol=1e-9):
        raise ValueError('Second paired margin does not match saved counts')
    net = (off_a-off_b)/n
    if not math.isclose(net, number(contrast['diff'], -1, 1), abs_tol=1e-9):
        raise ValueError('Saved effect does not match paired counts')
    return dict(paired_n=n, a_only_refuses=off_a, b_only_refuses=off_b,
                both_refuse=both, neither_refuses=neither,
                net_gap_pp=100*net, changed_refusal_pct=100*(off_a+off_b)/n)


def missing_bounds(n, positive, unresolved):
    """Identification bounds only; requires actual counts, never rounded rates."""
    n, positive, unresolved = count(n), count(positive), count(unresolved)
    if not n or positive+unresolved > n:
        raise ValueError('Inconsistent scheduled/observed counts')
    return [positive/n, (positive+unresolved)/n]


def analyze_saved(source):
    source = Path(source)
    raw = source.read_bytes()
    data = json.loads(raw)
    if data['meta']['version'] != 'v6' or data['meta']['smoke'] is not False:
        raise ValueError('Expected frozen v6 full-run scientific aggregates')
    transitions, sensitivity, unavailable = [], [], []
    for benchmark, pool, pairs in [('MM-SafetyBench', data['results'], MAIN_PAIRS),
                                   ('FigStep', data['figstep'], FS_PAIRS)]:
        for model, short in MODELS.items():
            record = pool.get(model)
            if record is None:
                unavailable.append(dict(benchmark=benchmark, model=short, reason='model_absent'))
                continue
            scheduled = count(record['n'])
            for judge in GUARDS:
                contrasts = record.get('contrasts', {}).get(judge, {})
                for name, (a, b) in pairs.items():
                    contrast = contrasts.get(name)
                    if contrast is None:
                        unavailable.append(dict(benchmark=benchmark, model=short, judge=judge,
                                                condition_a=a, condition_b=b, reason='contrast_absent'))
                        continue
                    row = dict(benchmark=benchmark, model=short, judge=judge,
                               condition_a=a, condition_b=b, recorded_items=scheduled,
                               outcome='frozen_v6_nc_adjusted_refusal', **paired_counts(contrast))
                    if row['paired_n'] > scheduled:
                        raise ValueError('Paired count exceeds recorded item count')
                    row['outside_valid_pair_count'] = scheduled-row['paired_n']
                    transitions.append(row)
                if benchmark == 'MM-SafetyBench':
                    rates = record.get('rates', {}).get(judge, {})
                    for cond in ['B', 'E', 'C', 'F_txt', 'F_img', 'W1_txt', 'W1_img', 'G_full', 'W2_img']:
                        values = rates.get(cond)
                        if not isinstance(values, dict):
                            continue
                        row = dict(benchmark=benchmark, model=short, judge=judge, condition=cond,
                                   recorded_items=scheduled, valid_label_count=None,
                                   denominator_status='valid_cell_denominators_not_exported_by_v6')
                        for key in ['refuse_raw', 'refuse3', 'notcomp']:
                            row[key] = 100*number(values[key], 0, 1)
                        harm = record.get('unsafe_rate_all', {}).get(judge, {}).get(cond)
                        row['unsafe_pct'] = None if harm is None else 100*number(harm, 0, 1)
                        sensitivity.append(row)
    return dict(schema='vlm-saved-analysis-1', evidence='exploratory_guard_labelled',
                source_version='v6', source_sha256=hashlib.sha256(raw).hexdigest(),
                transitions=transitions, scoring_sensitivity=sensitivity, unavailable=unavailable,
                human_correction_status='pending_human_reference_and_verified_sampling_design',
                missing_bounds_status='unavailable_without_scheduled_positive_unresolved_cell_counts',
                limitations=[
                    'Reanalysis of historical outcomes; no new independent experiment',
                    'Transition counts use the frozen NC-adjusted refusal construct only',
                    'Neither-refuses does not mean harmful or helpful',
                    'Harm and NC transitions cannot be recovered from marginal rates',
                    'Cell-valid denominators are not present in the aggregate; none are invented',
                    'Existing scenario intervals are not intervals for the new transition summaries',
                    'No new p-values, human corrections or confirmatory claims are produced'])


def markdown_table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(str(v) for v in row)+' |' for row in rows])


def transition_readout(result):
    selected = [r for r in result['transitions'] if
                (r['condition_a'], r['condition_b']) in [('E', 'C'), ('FS_E', 'FS_F')]]
    table = markdown_table(['Benchmark', 'Model', 'Guard', 'Paired n', 'Text only refuses',
                            'Image only refuses', 'Net gap pp', 'Changed refusal %'],
                           [[r['benchmark'], r['model'], r['judge'], r['paired_n'],
                             r['a_only_refuses'], r['b_only_refuses'],
                             f"{r['net_gap_pp']:.1f}", f"{r['changed_refusal_pct']:.1f}"] for r in selected])
    qwen = next((r for r in selected if r['benchmark']=='MM-SafetyBench' and
                 r['model']=='Qwen2-VL-2B' and r['judge']=='qwen3guard'), None)
    explanation = ''
    if qwen:
        explanation = (f"\n\nFor Qwen2-VL-2B under Qwen3Guard, {qwen['a_only_refuses']} paired items "
                       f"refused only in E and {qwen['b_only_refuses']} only in C. The net gap is "
                       f"{qwen['net_gap_pp']:.1f} percentage points, while "
                       f"{qwen['changed_refusal_pct']:.1f}% of pairs changed refusal label. "
                       'A small average difference can therefore conceal opposing response changes.')
    return ('## Paired response transitions — actual saved v6 results\n\n'+table+explanation+
            '\n\nThese are observed paired labels from one completion per condition. '
            'They do not establish that a model changed its internal safety policy. '
            'The labels are guard-based and use the frozen v6 NC rule. '
            'Non-refusal is not proof of harmful assistance. No human correction has been applied.')


def sensitivity_readout(result):
    rows = [r for r in result['scoring_sensitivity'] if r['condition']=='C']
    table = markdown_table(['Model', 'Guard', 'Raw refusal %', 'NC-adjusted refusal %',
                            'NC %', 'Unsafe %'],
                           [[r['model'], r['judge'], *[f'{r[k]:.1f}' if r[k] is not None else 'unavailable'
                             for k in ['refuse_raw', 'refuse3', 'notcomp', 'unsafe_pct']]] for r in rows])
    return ('## Scoring sensitivity — separate outcomes\n\n'+table+
            '\n\nRaw refusal, NC-adjusted refusal and harmful assistance measure different constructs. '
            'Compare both guards; do not average these columns into one score. '
            'V6 exported valid-label means without all cell-valid denominators. '
            'The recorded item count must not be presented as a verified valid-label denominator. '
            'Exact missing-label bounds and human-corrected estimates remain unavailable here.')


def make_figure(result):
    import matplotlib.pyplot as plt
    selected = [r for r in result['transitions'] if r['benchmark']=='MM-SafetyBench' and
                (r['condition_a'], r['condition_b'])==('E', 'C')]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    positions = list(range(len(selected)))
    ax.barh(positions, [100*r['a_only_refuses']/r['paired_n'] for r in selected],
            label='Only matched text refuses', color='#367c9c')
    ax.barh(positions, [-100*r['b_only_refuses']/r['paired_n'] for r in selected],
            label='Only image refuses', color='#d58d4a')
    ax.scatter([r['net_gap_pp'] for r in selected], positions, c='black', s=24, label='Net text−image gap')
    ax.set_yticks(positions, [r['model']+' / '+r['judge'] for r in selected])
    ax.axvline(0, color='gray', linewidth=.7)
    ax.set_xlabel('Percentage of jointly valid pairs (image-only bars point left)')
    ax.set_title('V6 exploratory: opposing refusal transitions can cancel')
    ax.legend(fontsize=8, loc='best')
    fig.tight_layout()
    return fig


def measurement_sensitivity(result):
    """Descriptive differences of exported cell means, never paired tests."""
    cells = {}
    shifts = []
    for row in result['scoring_sensitivity']:
        key = (row['model'], row['judge'], row['condition'])
        if key in cells:
            raise ValueError('Duplicate scoring cell')
        cells[key] = row
        shifts.append(dict(model=key[0], judge=key[1], condition=key[2],
                           raw_minus_nc_pp=row['refuse_raw']-row['refuse3'],
                           valid_label_count=None))
    guard_differences, contrasts = [], []
    for model in MODELS.values():
        for cond in ['B', 'E', 'C', 'F_txt', 'F_img', 'W1_txt', 'W1_img', 'G_full', 'W2_img']:
            left, right = (cells.get((model, judge, cond)) for judge in GUARDS)
            if left is None or right is None:
                continue
            for outcome in ['refuse_raw', 'refuse3', 'unsafe_pct']:
                a, b = left[outcome], right[outcome]
                guard_differences.append(dict(model=model, condition=cond, outcome=outcome,
                    qwen_minus_wild_pp=None if a is None or b is None else a-b))
        for a, b in MAIN_PAIRS.values():
            for judge in GUARDS:
                left, right = cells.get((model, judge, a)), cells.get((model, judge, b))
                if left is None or right is None:
                    continue
                for outcome in ['refuse_raw', 'refuse3', 'unsafe_pct']:
                    x, y = left[outcome], right[outcome]
                    diff = None if x is None or y is None else x-y
                    contrasts.append(dict(model=model, judge=judge, condition_a=a,
                        condition_b=b, outcome=outcome, difference_of_cell_means_pp=diff,
                        nominal_direction=None if diff is None else
                        ('zero' if abs(diff)<1e-9 else 'positive' if diff>0 else 'negative')))
    return dict(schema='vlm-measurement-sensitivity-1',
                evidence='exploratory_guard_labelled', source_sha256=result['source_sha256'],
                scoring_rule_shifts=shifts, guard_differences=guard_differences,
                cell_mean_contrasts=contrasts,
                limitations=[
                    'Descriptive reanalysis of the same historical v6 outcomes',
                    'Differences of cell-valid means are not jointly valid paired estimates',
                    'Missing parse counts and human reference are unavailable',
                    'Nominal direction is not statistical significance or equivalence',
                    'Guard disagreement does not identify which judge is correct',
                    'No joint harm table, missed-harm rate or cost-saving policy is estimated',
                    'Checkpoint samples differ; no model ranking is claimed'])


def measurement_readout(result):
    shifts = sorted(result['scoring_rule_shifts'], key=lambda r:abs(r['raw_minus_nc_pp']), reverse=True)
    gaps = sorted([r for r in result['guard_differences'] if r['outcome']=='unsafe_pct'
                   and r['qwen_minus_wild_pp'] is not None],
                  key=lambda r:abs(r['qwen_minus_wild_pp']), reverse=True)
    contrasts = [r for r in result['cell_mean_contrasts'] if
                 (r['condition_a'],r['condition_b'])==('E','C')]
    return ('## Where measurement changes the descriptive result\n\n'
        'Largest raw-to-NC refusal shifts (percentage points; all cells retained in JSON):\n\n'+
        markdown_table(['Model','Guard','Condition','Raw minus NC pp'],
            [[r['model'],r['judge'],r['condition'],f"{r['raw_minus_nc_pp']:.2f}"] for r in shifts[:8]])+
        '\n\nLargest between-guard harmfulness-rate differences (Qwen3Guard minus WildGuard):\n\n'+
        markdown_table(['Model','Condition','Harmfulness difference pp'],
            [[r['model'],r['condition'],f"{r['qwen_minus_wild_pp']:.2f}"] for r in gaps[:8]])+
        '\n\nMatched E minus C, separately for refusal definitions and harmfulness:\n\n'+
        markdown_table(['Model','Guard','Outcome','Difference of cell means pp'],
            [[r['model'],r['judge'],r['outcome'],
              'unavailable' if r['difference_of_cell_means_pp'] is None else
              f"{r['difference_of_cell_means_pp']:.2f}"] for r in contrasts])+
        '\n\nThese are differences of exported cell-valid means, not new paired tests. '
        'A positive refusal difference means more refusal in E; a positive harmfulness '
        'difference means more harmful assistance in E. They are distinct outcomes. '
        'The human reference and valid-parse denominator checks are still pending.')
