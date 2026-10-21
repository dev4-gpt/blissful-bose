"""Check paired missingness, duplicate rejection and private-checkpoint corruption."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from summarize_development_pilot import checked_record, digest, paired_table  # noqa: E402


class PilotSummaryTests(unittest.TestCase):
    def test_cancellation_and_missingness_are_not_fabricated_safety(self):
        rows = []
        for uid, values in enumerate([(True, False), (False, True), (True, True), (False, False), (None, True)]):
            for cond, value in zip(('E', 'C'), values):
                rows.append(dict(judge='g', model='m', uid=str(uid), draw=-1, cond=cond, unsafe=value))
        result = paired_table(rows, 'g', 'unsafe', 'E', 'C')
        self.assertEqual(result['paired_n'], 4)
        self.assertEqual(result['unresolved_pairs'], 1)
        self.assertEqual(result['net_difference_pp'], 0)
        self.assertEqual(result['changed_pct'], 50)
        with self.assertRaises(ValueError):
            paired_table(rows+rows[:1], 'g', 'unsafe', 'E', 'C')

    def test_checkpoint_values_are_verified_not_accepted_by_filename(self):
        context, value = {'fixture': 'benign'}, {'response': 'benign synthetic fixture'}
        record = dict(key=digest(context), context=context, value=value, value_hash=digest(value))
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/('gen_PRIVATE_'+record['key']+'.json')
            p.write_text(json.dumps(record))
            self.assertEqual(checked_record(p), record)
            record['value']['response'] = 'modified fixture'
            p.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                checked_record(p)

    def test_unavailable_labels_do_not_become_zero_harm(self):
        rows = [dict(judge='g', model='m', uid='u', draw=-1, cond=c, unsafe=None) for c in ('E', 'C')]
        result = paired_table(rows, 'g', 'unsafe', 'E', 'C')
        self.assertEqual(result['paired_n'], 0)
        self.assertIsNone(result['net_difference_pp'])
        self.assertEqual(result['unresolved_pairs'], 1)


if __name__ == '__main__':
    unittest.main()
