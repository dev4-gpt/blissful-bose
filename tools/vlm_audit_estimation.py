"""Offline methodology prototype: finite-population, stratified difference estimation.

Not wired into approved v7 scientific inference. Requires a documented SRSWOR audit,
fixed census autorater predictions, and a named reference. No model calls or raw text.
Related methods: Fisch et al., arXiv:2406.04291, Sections 3-4; classical survey
difference estimation. This finite-census implementation is not a reproduction of
StratPPI's independent-sample asymptotic confidence intervals.
"""
import math
from collections import defaultdict
from statistics import mean, variance


def stratified_difference(population, audit, *, design, reference, bounds=(0., 1.)):
    """Estimate one fixed finite-population mean, or a precomputed paired contrast.

    population: [{stratum, population_size, auto_mean}], with census auto_mean.
    audit: [{stratum, unit_id, human, auto}], numeric labels/predictions only.
    For a paired contrast, human/auto must already be within-item differences;
    use bounds=(-1, 1). Separate unpaired cell samples are not interchangeable.
    No fitted lambda, clipping, p-value, or nominal confidence interval is produced.
    """
    if design != 'stratified_srswor':
        raise ValueError('Document stratified simple random sampling without replacement')
    if reference not in {'human', 'llm_annotator', 'synthetic'}:
        raise ValueError('Name the reference: human, llm_annotator, or synthetic')
    low, high = map(float, bounds)
    if not math.isfinite(low) or not math.isfinite(high) or low >= high:
        raise ValueError('Finite ordered label bounds required')
    pools = {}
    for row in population:
        if set(row) != {'stratum', 'population_size', 'auto_mean'}:
            raise ValueError('Population input must contain numeric summaries only')
        name, size, prediction = row['stratum'], row['population_size'], row['auto_mean']
        if name in pools or not isinstance(name, str) or not name:
            raise ValueError('Unique nonempty stratum names required')
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError('Positive integer population sizes required')
        if not isinstance(prediction, (int, float)) or not math.isfinite(prediction) or not low <= prediction <= high:
            raise ValueError('Census autorater mean outside label bounds')
        pools[name] = row
    if not pools:
        raise ValueError('Population is empty')
    groups, seen = defaultdict(list), set()
    for row in audit:
        if set(row) != {'stratum', 'unit_id', 'human', 'auto'}:
            raise ValueError('Audit input must contain numeric labels and opaque IDs only')
        if row['stratum'] not in pools:
            raise ValueError('Audit stratum absent from population')
        if not isinstance(row['unit_id'], str) or not row['unit_id'] or row['unit_id'] in seen:
            raise ValueError('Unique nonempty sampling-unit IDs required')
        seen.add(row['unit_id'])
        for field in ('human', 'auto'):
            value = row[field]
            if not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError('Missing, nonnumeric, or out-of-range audit label')
        groups[row['stratum']].append(row)
    total = sum(x['population_size'] for x in pools.values())
    corrected = human_only = auto_only = design_var = lower = upper = 0.
    variance_available, all_census = True, True
    warnings, sizes = [], []
    for name, info in pools.items():
        sample = groups[name]
        size, n = info['population_size'], len(sample)
        if not 0 < n <= size:
            raise ValueError('Every populated stratum needs a nonempty sample no larger than its population')
        weight = size / total
        residuals = [x['human'] - x['auto'] for x in sample]
        observed_sum = sum(x['human'] for x in sample)
        auto_sum = sum(x['auto'] for x in sample)
        census_sum = size * info['auto_mean']
        if not auto_sum + (size-n)*low - 1e-10 <= census_sum <= auto_sum + (size-n)*high + 1e-10:
            raise ValueError('Census autorater mean is inconsistent with sampled predictions')
        corrected += weight * (info['auto_mean'] + mean(residuals))
        human_only += weight * observed_sum / n
        auto_only += weight * info['auto_mean']
        lower += weight * (observed_sum + (size - n) * low) / size
        upper += weight * (observed_sum + (size - n) * high) / size
        if n == size:
            if not math.isclose(mean(x['auto'] for x in sample), info['auto_mean'], abs_tol=1e-10):
                raise ValueError('Census autorater mean does not match census audit predictions')
        else:
            all_census = False
            if n < 2:
                variance_available = False
            else:
                residual_var = variance(residuals)
                design_var += weight**2 * (1 - n / size) * residual_var / n
                if residual_var == 0:
                    warnings.append('A noncensus stratum has zero sampled residual variance; unseen errors remain possible')
        sizes.append(dict(population_size=size, sample_size=n, population_weight=weight))
    if not low <= corrected <= high:
        warnings.append('Unclipped difference estimate lies outside the label range; inspect sampling uncertainty')
    if reference != 'human':
        warnings.append('Reference is not human validation; do not report human-corrected scientific results')
    return dict(status='methodology_prototype', reference=reference, target='fixed_finite_population',
                population_size=total, audited_units=len(seen), corrected_mean=corrected,
                human_only_stratified_mean=human_only, autorater_census_mean=auto_only,
                naive_audit_mean=mean(x['human'] for rows in groups.values() for x in rows),
                design_variance_estimate=design_var if variance_available else None,
                standard_error=math.sqrt(design_var) if variance_available else None,
                uncertainty_status='census_exact_relative_to_reference' if all_census else
                    'variance_only_no_validated_confidence_interval' if variance_available else
                    'variance_unavailable_singleton_noncensus_stratum',
                deterministic_label_bounds=[lower, upper], stratum_sizes=sizes, warnings=warnings,
                limitations=['Requires correct population totals and fixed census predictions',
                    'Requires the declared within-stratum random sampling design and complete labels',
                    'Finite-population uncertainty is not uncertainty over new scenarios or models',
                    'Reference-label error and correlated annotations are not corrected',
                    'No confidence-interval coverage or efficiency guarantee is claimed here'])


def synthetic_demo():
    """Toy population only: disagreement oversampling makes a raw audit misleading."""
    population = [dict(stratum='ordinary', population_size=90, auto_mean=0.),
                  dict(stratum='contested', population_size=10, auto_mean=0.)]
    audit = [dict(stratum=h, unit_id=h+str(i), human=y, auto=0.)
             for h, y in [('ordinary', 0.), ('contested', 1.)] for i in range(2)]
    return stratified_difference(population, audit, design='stratified_srswor', reference='synthetic')
