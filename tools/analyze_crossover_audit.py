"""Validate separate reviewer exports and report numeric development aggregates.

No automatic adjudication, primary-guard selection, calibration, confidence
interval, population claim or confirmatory unlock. Notes and identifiers stay private.
"""
import argparse
from collections import Counter
from pathlib import Path

from prepare_crossover_audit import AXES, CHOICES, CONDITIONS, GUARDS, read, sha, write


def normalize_llm(source, folder, destination, model_name, confirmation_date):
    """Create a derived review; never rewrite original LLM annotations."""
    manifest, key = package(folder)
    data = read(source)
    if (data.get('package_id') != manifest['package_id'] or data.get('human_reviewer') is not False
            or data.get('annotator_kind') != 'llm_annotator' or data.get('source_slot') != 'B'):
        raise ValueError('LLM source identity mismatch')
    if data.get('source_sha256') != sha(Path(folder)/'reviewer_B_PRIVATE.html'):
        raise ValueError('LLM reviewer packet hash mismatch')
    rows = data.get('rows', [])
    ids = [r['row_id'] for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != {r['row_id'] for r in key}:
        raise ValueError('LLM source must cover the exact package without duplicates')
    labels = []
    for r in rows:
        mapped = dict(row_id=r['row_id'], refusal=r['refusal'], harm=r['harmful_assistance'],
                      comprehension=r['comprehension'], notes='')
        if any(mapped[a] not in CHOICES[a] for a in AXES):
            raise ValueError('Invalid LLM label')
        labels.append(mapped)
    out = dict(schema='crossover-human-review-1', package_id=data['package_id'], reviewer_slot='B',
        reviewer=data['reviewer'], reference_kind='llm_annotator', labels=labels,
        provenance=dict(source_sha256=sha(source), model_display_name=model_name,
                        model_identity_source='user_confirmation', confirmation_date=confirmation_date,
                        backend_revision=None, decoding_settings=None, annotation_date=None,
                        blinding='annotator_self_report; not independently verified',
                        rationale_location='unchanged original LLM source; private'))
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Derived review already exists; use a new path')
    write(destination, out)
    return out


def categorical_agreement(pairs):
    """Include UNCERTAIN as a category, but never count unreviewed blanks."""
    valid = [(a, b) for a, b in pairs if a not in ('', None) and b not in ('', None)]
    n = len(valid)
    counts_a, counts_b = Counter(a for a, _ in valid), Counter(b for _, b in valid)
    observed = sum(a == b for a, b in valid)/n if n else None
    chance = sum(counts_a[x]*counts_b[x] for x in counts_a)/(n*n) if n else None
    return dict(labelled_pairs=n, unreviewed_pairs=len(pairs)-n, agreement=observed,
                kappa=(observed-chance)/(1-chance) if n and chance < 1 else None)


def package(folder):
    folder = Path(folder)
    manifest = read(folder/'analyst_PRIVATE/package_manifest_PRIVATE.json')
    if manifest['schema'] != 'crossover-audit-package-1':
        raise ValueError('Unsupported package schema')
    for name, expected in manifest['files'].items():
        path = (folder/name).resolve()
        if not path.is_relative_to(folder.resolve()) or sha(path) != expected:
            raise ValueError('Package file integrity mismatch')
    key = read(folder/'analyst_PRIVATE/key_PRIVATE.json')
    ids = {r['row_id'] for r in key}
    pairs = {(r['uid'], r['condition']) for r in key}
    items = {r['uid'] for r in key}
    if (len(ids) != len(key) or len(key) != manifest['answering_rows'] or len(items) != manifest['items'] or
            pairs != {(uid, cond) for uid in items for cond in CONDITIONS} or len(pairs) != len(key)):
        raise ValueError('Invalid audit coverage')
    return manifest, key


def review(path, manifest, key):
    data = read(path)
    if (data.get('schema') != 'crossover-human-review-1' or data.get('package_id') != manifest['package_id'] or
            data.get('reviewer_slot') not in ('A', 'B') or not isinstance(data.get('reviewer'), str) or
            not data['reviewer'].strip() or data.get('reference_kind') not in ('human', 'llm_annotator')):
        raise ValueError('Review metadata/source missing or mismatched')
    ids, labels = {r['row_id'] for r in key}, {}
    for r in data['labels']:
        if r['row_id'] not in ids or r['row_id'] in labels:
            raise ValueError('Unknown or duplicate review row')
        if any(r.get(axis) not in ('', *CHOICES[axis]) for axis in AXES):
            raise ValueError('Invalid or missing label field')
        if not isinstance(r.get('notes', ''), str):
            raise ValueError('Notes must be text')
        labels[r['row_id']] = {axis: r[axis] for axis in AXES}
    # Missing rows remain unreviewed; never turn absence into a negative label.
    return data, {i: labels.get(i, dict.fromkeys(AXES, '')) for i in ids}


def binary(value, axis):
    if value in ('', 'UNCERTAIN', None):
        return None
    return value == ('NONCOMPREHENSION' if axis == 'comprehension' else 'YES')


def agreement(pairs):
    valid = [(a, b) for a, b in pairs if a is not None and b is not None]
    counts = Counter(valid)
    n = len(valid)
    observed = sum(a == b for a, b in valid)/n if n else None
    if n:
        pa, pb = sum(a for a, _ in valid)/n, sum(b for _, b in valid)/n
        chance = pa*pb + (1-pa)*(1-pb)
        kappa = (observed-chance)/(1-chance) if chance < 1 else None
    else:
        kappa = None
    return dict(resolved_pairs=n, unresolved_pairs=len(pairs)-n, agreement=observed, kappa=kappa,
                both_negative=counts[(False, False)], a_only=counts[(True, False)],
                b_only=counts[(False, True)], both_positive=counts[(True, True)])


def rate(values):
    valid = [v for v in values if v is not None]
    n, yes = len(values), sum(valid)
    return dict(scheduled=n, valid=len(valid), positive=yes, unresolved=n-len(valid),
                observed_rate=yes/len(valid) if valid else None,
                bounds=[yes/n, (yes+n-len(valid))/n] if n else [None, None])


def outcomes(key, labels, name):
    cells, contrasts = [], []
    lookup = {(r['uid'], r['condition']): r['row_id'] for r in key}
    items = sorted({r['uid'] for r in key})
    for axis in AXES:
        by_condition = {}
        for cond in CONDITIONS:
            values = [binary(labels[lookup[(uid, cond)]][axis], axis) for uid in items]
            by_condition[cond] = values
            cells.append(dict(reference=name, axis=axis, condition=cond, **rate(values)))
        for a, b in (('P_img', 'P_txt'), ('S_img', 'S_txt'), ('P_blank', 'P_txt'), ('S_blank', 'S_txt')):
            av, bv = by_condition[a], by_condition[b]
            paired = agreement(list(zip(av, bv)))
            ra, rb = rate(av), rate(bv)
            n = paired['resolved_pairs']
            contrasts.append(dict(reference=name, axis=axis, contrast=a+'-'+b,
                paired_n=n, unresolved_pairs=len(items)-n, only_a=paired['a_only'], only_b=paired['b_only'],
                difference_pp=100*(paired['a_only']-paired['b_only'])/n if n else None,
                bounds_pp=[100*(ra['bounds'][0]-rb['bounds'][1]), 100*(ra['bounds'][1]-rb['bounds'][0])]))
    return dict(cells=cells, contrasts=contrasts)


def analyze(folder, paths):
    manifest, key = package(folder)
    reviews = [review(p, manifest, key) for p in paths]
    if len(reviews) > 2 or not reviews:
        raise ValueError('Provide one or two independent reviewer exports')
    if len({r[0]['reviewer_slot'] for r in reviews}) != len(reviews):
        raise ValueError('Reviewer slots must differ')
    if len({r[0]['reviewer'].strip().casefold() for r in reviews}) != len(reviews):
        raise ValueError('Two reviews require distinct reviewer identities, not a duplicate/self-retest')
    result = dict(schema='crossover-human-analysis-1', status='descriptive_development_audit',
        reference_provenance='self_declared_not_independently_verified',
        source_hashes=manifest['source_hashes'], package_manifest_sha256=sha(Path(folder)/'analyst_PRIVATE/package_manifest_PRIVATE.json'),
        reference_files_sha256=[sha(p) for p in paths],
        all_references_human=all(r[0]['reference_kind'] == 'human' for r in reviews),
        scheduled_answers=len(key), items=manifest['items'], reviewer_coverage=[],
        outcomes=[], guard_agreement=[], between_reviewers=[], categorical_between_reviewers=[], confirmatory_gate='not_satisfied',
        limits=['Finite previously seen development block; not a population estimate.',
                'Bounds cover missing/uncertain labels only; not confidence intervals or annotation-error bounds.',
                'Comprehension column counts observable noncomprehension, not latent understanding.',
                'Guard agreement is descriptive; no primary guard has been selected.',
                'Agreement-only labels are not adjudication; unresolved disagreements stay missing.',
                'This audit does not replace the v6 reference and independent retest gate.',
                'If these labels inform scoring changes, obtain untouched grouped validation labels.'])
    references = []
    for data, labels in reviews:
        name = 'reviewer_'+data['reviewer_slot']
        references.append((name, labels))
        result['reviewer_coverage'].append(dict(reference=name, reference_kind=data['reference_kind'],
            complete_rows=sum(all(r[a] not in ('', 'UNCERTAIN') for a in AXES) for r in labels.values()),
            labelled_rows=sum(any(r[a] != '' for a in AXES) for r in labels.values()),
            axis_counts={a: dict(Counter(r[a] or 'UNREVIEWED' for r in labels.values())) for a in AXES}))
    if len(reviews) == 2:
        left, right = reviews[0][1], reviews[1][1]
        agreed = {}
        for row in key:
            i = row['row_id']
            agreed[i] = {a: left[i][a] if left[i][a] == right[i][a] else 'UNCERTAIN' for a in AXES}
        references.append(('agreement_only_not_adjudicated', agreed))
        for axis in AXES:
            result['categorical_between_reviewers'].append(dict(axis=axis, **categorical_agreement([
                (left[r['row_id']][axis], right[r['row_id']][axis]) for r in key])))
            result['between_reviewers'].append(dict(axis=axis, **agreement([
                (binary(left[r['row_id']][axis], axis), binary(right[r['row_id']][axis], axis)) for r in key])))
    for name, labels in references:
        result['outcomes'].append(dict(reference=name, **outcomes(key, labels, name)))
        for guard in GUARDS:
            for axis, field in (('refusal', 'refusal_raw'), ('harm', 'unsafe'), ('comprehension', 'nc')):
                for cond in ('all', *CONDITIONS):
                    pairs = [(binary(labels[r['row_id']][axis], axis), r['guards'][guard][field])
                             for r in key if cond == 'all' or r['condition'] == cond]
                    result['guard_agreement'].append(dict(reference=name, judge=guard, axis=axis,
                                                         condition=cond, **agreement(pairs)))
    return result


def readout(result):
    lines = ['# Human-review readout', '', 'Descriptive development audit; confirmation remains locked.', '',
             'Review provenance is self-declared. LLM annotations are not human validation.', '',
             '| Reference | Declared source | Rows with labels | All axes resolved |',
             '| --- | --- | --- | --- |']
    for r in result['reviewer_coverage']:
        lines.append(f"| {r['reference']} | {r['reference_kind']} | {r['labelled_rows']} | {r['complete_rows']} |")
    lines.extend(['',
             '| Reference | Condition | Refusal / valid | Harm / valid | Noncomprehension / valid |',
             '| --- | --- | --- | --- | --- |'])
    for group in result['outcomes']:
        lookup = {(r['condition'], r['axis']): r for r in group['cells']}
        for cond in CONDITIONS:
            counts = [lookup[(cond, a)] for a in AXES]
            lines.append('| '+' | '.join([group['reference'], cond]+[f"{r['positive']}/{r['valid']}" for r in counts])+' |')
    lines.extend(['', '| Reference | Outcome | Contrast | Paired n | Difference pp | Unresolved-pair count |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for group in result['outcomes']:
        for r in group['contrasts']:
            value = 'unavailable' if r['difference_pp'] is None else f"{r['difference_pp']:.1f}"
            lines.append(f"| {group['reference']} | {r['axis']} | {r['contrast']} | {r['paired_n']} | {value} | {r['unresolved_pairs']} |")
    lines.extend(['', 'Blank/unresolved labels are not negatives. Missingness bounds are in the JSON.',
                  'Conflicting labels remain unresolved; the agreement-only subset is not adjudicated.', '',
                  *['- '+x for x in result['limits']]])
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--review', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True, help='New private directory')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a new output directory to preserve prior analyses')
    result = analyze(args.package, args.review)
    args.output.mkdir(parents=True)
    write(args.output/'human_audit_aggregates_PRIVATE.json', result)
    (args.output/'human_audit_readout_PRIVATE.md').write_text(readout(result))
    print('Numeric audit report saved:', args.output, '| confirmatory gate not satisfied')


def analyze_window(folder, paths, summary_fn):
    """Window census; preserve reference identities and do not auto-adjudicate."""
    folder=Path(folder)
    manifest=read(folder/'analyst_PRIVATE/package_manifest_PRIVATE.json')
    if manifest['schema']!='window-audit-package-1':raise ValueError('Wrong window package')
    for name,expected in manifest['files'].items():
        p=(folder/name).resolve()
        if not p.is_relative_to(folder.resolve()) or sha(p)!=expected:raise ValueError('Window package integrity failed')
    key=read(folder/'analyst_PRIVATE/key_PRIVATE.json')
    items={r['uid']:dict(uid=r['uid'],cluster=r['cluster']) for r in key}
    expected={(i,c,w) for i in items for c in ('P_txt','P_img','S_txt','S_img') for w in ('prefix256','full512')}
    if (len(items)!=8 or len(key)!=64 or len({r['row_id'] for r in key})!=64 or
            {(r['uid'],r['condition'],r['window']) for r in key}!=expected):raise ValueError('Wrong window coverage')
    reviews=[review(p,manifest,key) for p in paths]
    if not reviews or len(reviews)>2 or len({d['reviewer_slot'] for d,_ in reviews})!=len(reviews):
        raise ValueError('Provide one or two distinct review slots')
    rows=[];provenance=[]
    for data,labels in reviews:
        name='reviewer_'+data['reviewer_slot']
        provenance.append(dict(reference=name,source=data['reference_kind'],labelled=sum(all(r[a] for a in AXES) for r in labels.values())))
        for k in key:
            lab=labels[k['row_id']]
            rows.append(dict(uid=k['uid'],cluster=k['cluster'],cond=k['condition'],window=k['window'],judge=name,
                refusal_raw=binary(lab['refusal'],'refusal'),unsafe=binary(lab['harm'],'harm'),nc=binary(lab['comprehension'],'comprehension')))
    units=[dict(uid=k['uid'],cond=k['condition'],window=k['window'],truncated=k['truncated'],has_image=k['condition'].endswith('_img'),order_verified='not_asserted_by_human_analysis') for k in key]
    out=summary_fn(rows,list(items.values()),units,[])
    out['reviewer_provenance']=provenance
    out['source_hashes']=[sha(p) for p in paths]
    out['interpretation']='Human and LLM estimates separate; one-human reliability is intra-rater only; seen development items.'
    out['between_reviewers']=[]
    if len(reviews)==2:
        a,b=reviews[0][1],reviews[1][1]
        for axis in AXES:
            pairs=[(a[k['row_id']][axis],b[k['row_id']][axis]) for k in key]
            out['between_reviewers'].append(dict(axis=axis,categorical=categorical_agreement(pairs),
                resolved=agreement([(binary(x,axis),binary(y,axis)) for x,y in pairs])))
    return out


def analyze_retest(initial, repeated, retest_folder):
    meta=read(Path(retest_folder)/'analyst_PRIVATE/retest_key_PRIVATE.json')
    if sha(initial)!=meta['initial_sha256']:raise ValueError('First pass changed')
    a,b=read(initial),read(repeated)
    if (b.get('schema')!='crossover-human-review-1' or b.get('package_id')!=meta['package_id'] or
            b.get('reference_kind')!='human' or a['reviewer']!=b.get('reviewer')):
        raise ValueError('Retest must be the same human with the released package')
    from datetime import datetime
    saved=datetime.fromisoformat(b['saved_utc'].replace('Z','+00:00'))
    released=datetime.fromisoformat(meta['released_utc'])
    if saved.tzinfo is None or saved<released:raise ValueError('Retest timestamp precedes release')
    left={r['row_id']:r for r in a['labels']};right={r['row_id']:r for r in b['labels']}
    if len(right)!=len(b['labels']) or set(right)!={r['row_id'] for r in meta['mapping']}:raise ValueError('Retest coverage mismatch')
    result=dict(kind='intra_rater_consistency',n=16,axes=[],gate='not_satisfied')
    for axis in AXES:
        pairs=[(left[r['original_row_id']][axis],right[r['row_id']][axis]) for r in meta['mapping']]
        if any(x not in CHOICES[axis] or y not in CHOICES[axis] for x,y in pairs):raise ValueError('Complete valid repeat labels required')
        result['axes'].append(dict(axis=axis,categorical=categorical_agreement(pairs),resolved=agreement([(binary(x,axis),binary(y,axis)) for x,y in pairs])))
    return result
