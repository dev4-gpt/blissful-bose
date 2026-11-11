"""Regenerate aggregate-only baseline evidence. No prompts, replies or API calls.

Read the completed private scenario table; export counts/rates/bounds only.
No paired significance test is inferred from marginal aggregate counts.
"""
import argparse
import csv
import hashlib
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARM = {'01', '02', '03', '04', '05', '06', '07', '09'}
CONDITIONS = {'TEXT', 'SD', 'TYPO', 'SD_TYPO'}
MODELS = {'qwen25', 'llava', 'instructblip'}
COUNTS = ('planned', 'no_response', 'safety_judged', 'unsafe', 'refusal_judged', 'refused')


def default_source():
    return (Path.home() / 'Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com'
            / 'My Drive/MM_SafetyBench_Full_20261102_PRIVATE/Runs/Judge_Handoff_PRIVATE'
            / 'Azure_Preparation_20261108T153750Z_PRIVATE/Full_Metrics_20261108_PRIVATE'
            / 'Combined_Results_PRIVATE/ASR_RR_by_model_scenario_condition_PRIVATE.csv')


def rate(a, n):
    return a / n if n else None


def validate(rows):
    if len(rows) != 312:
        raise ValueError('Expected 3 models × 2 cohorts × 13 scenarios × 4 conditions')
    keys = set()
    for row in rows:
        key = tuple(row[k] for k in ('model', 'cohort', 'scenario', 'condition'))
        if key in keys:
            raise ValueError('Duplicate aggregate cell')
        keys.add(key)
        if row['model'] not in MODELS or row['condition'] not in CONDITIONS:
            raise ValueError('Unknown model or condition')
        if row['cohort'] not in {'full', 'released_tiny'}:
            raise ValueError('Unknown cohort')
        if row['scenario'][:2] not in {f'{i:02d}' for i in range(1, 14)}:
            raise ValueError('Unknown scenario')
        for k in COUNTS:
            value = int(row[k])
            if value < 0 or str(value) != str(row[k]):
                raise ValueError('Counts must be nonnegative integers')
            row[k] = value
        n, empty = row['planned'], row['no_response']
        for judged, positive, field in [('safety_judged', 'unsafe', 'ASR_among_judged'),
                                        ('refusal_judged', 'refused', 'RR_among_judged')]:
            if not 0 <= row[positive] <= row[judged] <= n - empty:
                raise ValueError('Inconsistent judged/empty/count denominator')
            expected = rate(row[positive], row[judged])
            recorded = row.get(field)
            if expected is not None and not math.isclose(float(recorded), expected, abs_tol=1e-12):
                raise ValueError('Recorded rate does not match counts')
    for model in MODELS:
        for cohort, n in [('full', 1680), ('released_tiny', 168)]:
            for condition in CONDITIONS:
                group = [r for r in rows if (r['model'], r['cohort'], r['condition']) ==
                         (model, cohort, condition)]
                if len(group) != 13 or len({r['scenario'][:2] for r in group}) != 13:
                    raise ValueError('Incomplete scenario coverage')
                if sum(r['planned'] for r in group) != n:
                    raise ValueError('Wrong planned condition count')
    return rows


def summarize(group, scope, source_sha):
    first = group[0]
    counts = {k: sum(r[k] for r in group) for k in COUNTS}
    n = counts['planned']
    row = dict(model=first['model'], cohort=first['cohort'], scope=scope,
               condition=first['condition'], scenarios=len(group), **counts)
    row['safety_unresolved'] = n - counts['safety_judged']
    row['refusal_unresolved'] = n - counts['refusal_judged']
    row['safety_filtered_or_other_unresolved'] = row['safety_unresolved'] - counts['no_response']
    row['refusal_filtered_or_other_unresolved'] = row['refusal_unresolved'] - counts['no_response']
    for metric, positive, judged in [('ASR', 'unsafe', 'safety_judged'),
                                      ('RR', 'refused', 'refusal_judged')]:
        row[metric + '_pooled_among_judged'] = rate(counts[positive], counts[judged])
        row[metric + '_planned_lower'] = rate(counts[positive], n)
        row[metric + '_planned_upper'] = rate(counts[positive] + n - counts[judged], n)
        values = [rate(r[positive], r[judged]) for r in group]
        row[metric + '_macro_scenarios'] = (sum(values) / len(values)
                                           if all(v is not None for v in values) else None)
    row['safety_semantics'] = ('harmful_assistance_proxy' if all(r['scenario'][:2] in HARM for r in group)
                                else 'released_scenario_policy_rubric;not_uniform_harm')
    row['evidence'] = 'exploratory_GPT4.1;not_human_validated'
    row['source_sha256'] = source_sha
    return row


def analyze(source, output):
    raw = source.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    rows = validate(list(csv.DictReader(raw.decode().splitlines())))
    groups = defaultdict(list)
    for row in rows:
        common = (row['model'], row['cohort'], row['condition'])
        for scope in [row['scenario'], 'ALL_13',
                      'HARM_8' if row['scenario'][:2] in HARM else 'POLICY_5']:
            groups[(*common, scope)].append(row)
    results = [summarize(g, key[-1], sha) for key, g in sorted(groups.items())]
    assert len(results) == 384
    # Differences are descriptive, with outcome-specific missingness; not paired effects.
    text = {(r['model'], r['cohort'], r['scope']): r for r in results if r['condition'] == 'TEXT'}
    for row in results:
        baseline = text[(row['model'], row['cohort'], row['scope'])]
        for metric in ('ASR', 'RR'):
            a, b = row[metric + '_pooled_among_judged'], baseline[metric + '_pooled_among_judged']
            row[metric + '_minus_TEXT_descriptive'] = a - b if a is not None and b is not None else None
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    for row in results:
        if row['cohort'] == 'full' and row['scope'] == 'ALL_13':
            print({k: row[k] for k in ('model', 'condition', 'planned', 'no_response',
                   'ASR_pooled_among_judged', 'RR_pooled_among_judged')})
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=default_source())
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/activation_safety_baseline.csv')
    args = parser.parse_args()
    analyze(args.source, args.output)
