"""Check paired-table reconstruction, refusal cancellation and safe exports."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from vlm_saved_analysis import (analyze_saved, measurement_sensitivity,
                                missing_bounds, paired_counts)  # noqa: E402


class SavedAnalysisTests(unittest.TestCase):
    def test_equal_marginals_can_hide_opposing_changes(self):
        result = paired_counts(dict(n=10, rate_a=.6, rate_b=.6, diff=0., mcnemar_b_c_p=[2,2,1.]))
        self.assertEqual(result['both_refuse'], 4)
        self.assertEqual(result['neither_refuses'], 2)
        self.assertEqual(result['net_gap_pp'], 0.)
        self.assertEqual(result['changed_refusal_pct'], 40.)

    def test_inconsistent_saved_margins_rejected(self):
        source = dict(n=10, rate_a=.6, rate_b=.6, diff=0., mcnemar_b_c_p=[2,2,1.])
        for key, value in [('rate_a', .61), ('rate_b', .7), ('diff', .1),
                           ('mcnemar_b_c_p', [7,2,1.]), ('n', True)]:
            altered = dict(source, **{key:value})
            with self.assertRaises(ValueError):
                paired_counts(altered)

    def test_bounds_use_unresolved_counts_without_safe_imputation(self):
        self.assertEqual(missing_bounds(10, 3, 2), [.3, .5])
        for values in [(0,0,0), (10,9,2), (10,-1,2), (10,3,2.1)]:
            with self.assertRaises(ValueError):
                missing_bounds(*values)

    def test_real_aggregate_reconstruction_and_no_fabricated_denominators(self):
        result = analyze_saved(ROOT/'v6_full/results_v6.json')
        self.assertEqual(len(result['transitions']), 60)
        self.assertEqual(len(result['scoring_sensitivity']), 54)
        self.assertTrue(all(r['valid_label_count'] is None for r in result['scoring_sensitivity']))
        row = next(r for r in result['transitions'] if r['model']=='Qwen2-VL-2B' and
                   r['judge']=='qwen3guard' and (r['condition_a'],r['condition_b'])==('E','C'))
        self.assertEqual((row['a_only_refuses'], row['b_only_refuses']), (31,21))
        self.assertAlmostEqual(row['net_gap_pp'], 100*10/304)

    def test_unrecognized_nested_text_never_enters_export(self):
        from tempfile import TemporaryDirectory
        source = json.loads((ROOT/'v6_full/results_v6.json').read_text())
        source['meta']['private_reply'] = 'PRIVATE_PAYLOAD_SENTINEL'
        source['results']['Qwen/Qwen2-VL-2B-Instruct']['private_sample'] = 'PRIVATE_PAYLOAD_SENTINEL'
        with TemporaryDirectory() as tmp:
            path = Path(tmp)/'source.json'
            path.write_text(json.dumps(source))
            out = analyze_saved(path)
        self.assertNotIn('PRIVATE_PAYLOAD_SENTINEL', json.dumps(out))
        self.assertEqual(out['evidence'], 'exploratory_guard_labelled')

    def test_smoke_cannot_be_mislabeled_as_scientific_source(self):
        from tempfile import TemporaryDirectory
        source = copy.deepcopy(json.loads((ROOT/'v6_full/results_v6.json').read_text()))
        source['meta']['smoke'] = True
        with TemporaryDirectory() as tmp:
            path = Path(tmp)/'source.json'
            path.write_text(json.dumps(source))
            with self.assertRaises(ValueError):
                analyze_saved(path)

    def test_measurement_analysis_preserves_missing_harm_and_rejects_duplicate_cells(self):
        source = analyze_saved(ROOT/'v6_full/results_v6.json')
        result = measurement_sensitivity(source)
        self.assertEqual(len(result['scoring_rule_shifts']), 54)
        self.assertEqual(len(result['guard_differences']), 81)
        self.assertEqual(len(result['cell_mean_contrasts']), 108)
        source['scoring_sensitivity'][0]['unsafe_pct'] = None
        absent = measurement_sensitivity(source)
        row = next(r for r in absent['guard_differences'] if
                   r['model']=='Qwen2-VL-2B' and r['condition']=='B' and r['outcome']=='unsafe_pct')
        self.assertIsNone(row['qwen_minus_wild_pp'])
        source['scoring_sensitivity'].append(source['scoring_sensitivity'][0])
        with self.assertRaises(ValueError):
            measurement_sensitivity(source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
