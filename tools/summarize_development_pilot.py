"""Verify private pilot provenance, then export only explicit numeric aggregate fields.

Never writes prompts, replies, item IDs, generation keys, or private label records.
Original exports remain untouched; this is descriptive post-run analysis.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

GUARDS = {'qwen3guard': 'Qwen/Qwen3Guard-Gen-4B', 'wildguard': 'allenai/wildguard',
          'keyword': 'keyword'}
CONDITIONS = ('B', 'E', 'C')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode()).hexdigest()


def checked_record(path):
    record = json.loads(Path(path).read_text())
    if record['key'] != digest(record['context']) or record['value_hash'] != digest(record['value']):
        raise ValueError('Private checkpoint integrity mismatch')
    if record['key'] not in Path(path).name:
        raise ValueError('Private checkpoint name/content mismatch')
    return record


def paired_table(rows, judge, outcome, a, b):
    table = {}
    for row in rows:
        if row['judge'] != judge or row['cond'] not in (a, b):
            continue
        key = (row['model'], row['uid'], row['draw'])
        pair = table.setdefault(key, {})
        if row['cond'] in pair:
            raise ValueError('Duplicate paired outcome')
        value = row[outcome]
        if value is not None and type(value) is not bool:
            raise ValueError('Outcome must be Boolean or missing')
        pair[row['cond']] = value
    counts = Counter()
    unresolved = 0
    for pair in table.values():
        if a not in pair or b not in pair or pair[a] is None or pair[b] is None:
            unresolved += 1
        else:
            counts[(pair[a], pair[b])] += 1
    n = sum(counts.values())
    return dict(judge=judge, outcome=outcome, contrast=a+'-'+b, paired_n=n,
                unresolved_pairs=unresolved, neither=counts[(False, False)],
                a_only=counts[(True, False)], b_only=counts[(False, True)],
                both=counts[(True, True)],
                net_difference_pp=100*(counts[(True, False)]-counts[(False, True)])/n if n else None,
                changed_pct=100*(counts[(True, False)]+counts[(False, True)])/n if n else None)


def verify_and_summarize(folder):
    folder = Path(folder)
    source = folder/'results_v7.json'
    result = json.loads(source.read_text())
    meta = result['meta']
    if meta['mode'] != 'development' or meta['human_gate']['passed']:
        raise ValueError('Expected unvalidated exploratory development pilot')
    manifest = json.loads((folder/'items_manifest_PRIVATE.json').read_text())
    if digest(manifest['items']) != meta['data_manifest_hash']:
        raise ValueError('Manifest hash does not match export')
    if manifest['plan_sha256'] != meta['plan_sha256'] or any(x['subset'] != 'development' for x in manifest['items']):
        raise ValueError('Unexpected plan or reserved item')
    items = {x['uid']: x for x in manifest['items']}
    if len(items) != len(manifest['items']) or len(items) != meta['data_counts']['selected_count']:
        raise ValueError('Item coverage mismatch')
    generations = {}
    for path in (folder/'generations').glob('gen_PRIVATE_*.json'):
        rec = checked_record(path)
        c = rec['context']
        ident = c['model']
        if c['data_manifest'] != meta['data_manifest_hash'] or c['plan'] != meta['plan_sha256']:
            raise ValueError('Generation belongs to another run')
        if ident['revision'] != meta['model_revisions'][ident['model']] or ident['adapter_code'] != meta['adapter_code_sha256']:
            raise ValueError('Generation revision or adapter mismatch')
        if c['uid'] not in items or c['cond'] not in CONDITIONS+('READ_C',) or c['do_sample']:
            raise ValueError('Generation outside pilot scope')
        if c['max_new'] != 256:
            raise ValueError('Unexpected generation cap')
        if c['cond'] in ('C', 'READ_C') and c['image'] != items[c['uid']]['image_hash']:
            raise ValueError('Image identity mismatch')
        generations[rec['key']] = rec
    panel = [x[0] for x in meta['panel']]
    scheduled = {(m, uid, c) for m in panel for uid in items for c in CONDITIONS+('READ_C',)}
    actual = [(r['context']['model']['model'], r['context']['uid'], r['context']['cond']) for r in generations.values()]
    if len(actual) != len(set(actual)) or set(actual) != scheduled:
        raise ValueError('Incomplete or duplicated generation coverage')
    rows = json.loads((folder/'analysis_rows_PRIVATE.json').read_text())
    label_records = [checked_record(p) for p in (folder/'labels').glob('lab_PRIVATE_*.json')]
    labels = {(x['context']['identity']['model'], x['context']['generation']): x for x in label_records}
    if len(labels) != len(label_records):
        raise ValueError('Duplicate label contexts')
    row_keys = set()
    for r in rows:
        key = (r['model'], r['uid'], r['cond'], r['judge'])
        if key in row_keys or r['draw'] != -1:
            raise ValueError('Duplicate or sampled analysis row')
        row_keys.add(key)
        g = generations[r['generation_key']]
        c = g['context']
        if (r['model'], r['uid'], r['cond']) != (c['model']['model'], c['uid'], c['cond']):
            raise ValueError('Label/generation identity mismatch')
        if r['response'] != g['value']['response']:
            raise ValueError('Response differs from exact generation')
        lab = labels[(GUARDS[r['judge']], r['generation_key'])]
        lc, lv = lab['context'], lab['value']
        expected_revision = 'v6-first200' if r['judge'] == 'keyword' else meta['model_revisions'][GUARDS[r['judge']]]
        if lc['identity']['revision'] != expected_revision:
            raise ValueError('Guard revision mismatch')
        if lc['stimulus'] != digest(r['stimulus']) or lc['response'] != digest(r['response']):
            raise ValueError('Label stimulus/response hash mismatch')
        if lc['nc_rule'] != meta['rule_version']:
            raise ValueError('NC rule version mismatch')
        expected_refusal = None if lv['refuse'] is None else bool(lv['refuse'] and not r['nc'])
        if r['refusal'] != expected_refusal or r['unsafe'] != lv['unsafe']:
            raise ValueError('Analysis outcome differs from frozen label')
    expected_rows = {(m, uid, c, j) for m in panel for uid in items for c in CONDITIONS for j in GUARDS}
    if row_keys != expected_rows:
        raise ValueError('Incomplete analysis label coverage')
    rates = []
    for saved in result['rates']:
        subset = [r for r in rows if all(r[k] == saved[k] for k in ('model', 'judge', 'cond'))]
        row = {k: saved[k] for k in ('model', 'judge', 'cond', 'n')}
        if len(subset) != saved['n']:
            raise ValueError('Export denominator mismatch')
        for field, public in [('refusal', 'refusal'), ('unsafe', 'unsafe'), ('nc', 'nc')]:
            values = [r[field] for r in subset if r[field] is not None]
            positive = sum(values)
            mean = positive/len(values) if values else None
            if (mean is None) != (saved[public] is None) or (mean is not None and not math.isclose(mean, saved[public])):
                raise ValueError('Export rate differs from exact label rows')
            row[public+'_positive'] = positive if values else None
            row[public+'_valid_n'] = len(values)
            row[public+'_rate'] = mean
        rates.append(row)
    pairs = [paired_table(rows, j, outcome, a, b) for j in GUARDS
             for outcome in ('refusal', 'unsafe', 'nc') for a, b in [('B', 'C'), ('B', 'E'), ('E', 'C')]]
    timings = []
    for modality in ('text', 'image'):
        values = [r['value'] for r in generations.values()
                  if (r['context']['image'] is not None) == (modality == 'image')]
        timings.append(dict(modality=modality, calls=len(values), seconds=sum(x['seconds'] for x in values),
                            new_tokens=sum(x['new_tokens'] for x in values),
                            calls_hitting_token_cap=sum(x['new_tokens'] >= 256 for x in values)))
    condition_timings = []
    for cond in CONDITIONS+('READ_C',):
        values = [r['value'] for r in generations.values() if r['context']['cond'] == cond]
        condition_timings.append(dict(cond=cond, calls=len(values), seconds=sum(x['seconds'] for x in values),
            new_tokens=sum(x['new_tokens'] for x in values), calls_hitting_token_cap=sum(x['new_tokens'] >= 256 for x in values)))
    agreement = []
    paired_guards = {(r['model'], r['uid'], r['cond']): {} for r in rows}
    for r in rows:
        if r['judge'] != 'keyword':
            paired_guards[(r['model'], r['uid'], r['cond'])][r['judge']] = r
    for outcome in ('refusal', 'unsafe', 'nc'):
        guard_pairs = [(v['qwen3guard'][outcome], v['wildguard'][outcome]) for v in paired_guards.values()]
        valid = [(a, b) for a, b in guard_pairs if a is not None and b is not None]
        agreement.append(dict(outcome=outcome, valid_n=len(valid), missing_n=len(guard_pairs)-len(valid),
                              disagreement_count=sum(a != b for a, b in valid)))
    return dict(status='exploratory_guard_labelled_descriptive_pilot', source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                items=len(items), target_responses=len(generations), label_records=len(rows), failures=len(result['failures']),
                exact_generation_and_label_provenance_verified=True, human_validated=False,
                elapsed_minutes=meta['elapsed_minutes'], rates=rates, paired_tables=pairs, timings=timings,
                condition_timings=condition_timings, guard_agreement=agreement,
                readback=result['readback'], historical_pooling_permitted=False,
                uncertainty_status='No population interval or equivalence verdict accepted for this eight-item seen pilot.',
                original_export_warning='Original zero-width intervals and equivalent=True at all-zero E/C outcomes retained in original snapshot, not endorsed here.',
                limits=['Previously seen items; one item per scenario; one model; one completion per condition.',
                        'B-E changes wording and content form; no pure wording attribution.',
                        'Separate readback is not comprehension evidence during answering.',
                        'Do not pool with v6 or infer a new replication, mechanism, safety certification or publication readiness.'])


def write_outputs(summary, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output/'pilot_summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    with (output/'pilot_rates.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary['rates'][0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(summary['rates'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Private completed-run folder')
    parser.add_argument('--output', type=Path, required=True, help='Aggregates-only output folder')
    args = parser.parse_args()
    summary = verify_and_summarize(args.source)
    write_outputs(summary, args.output)
    print('Verified:', summary['target_responses'], 'responses;', summary['label_records'], 'label records;', summary['items'], 'seen development items')
