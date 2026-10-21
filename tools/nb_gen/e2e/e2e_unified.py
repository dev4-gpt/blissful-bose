"""Regression checks for evidence separation, privacy and portable companion execution."""
import ast
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/nb_gen'))
from make_unified_nb import build, collect, definitions, digest, execute_cpu  # noqa: E402


class UnifiedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=collect(ROOT,ROOT/'audit_work/v7_autonomy_state_PRIVATE.json')

    def test_versions_roles_and_actual_item_counts(self):
        self.assertEqual([r['version'] for r in self.data['timeline']],
                         ['v1','v2','v3','v4','v5','v6','v7','development','crossover'])
        self.assertNotIn('v4',{r['version'] for r in self.data['historical']})
        self.assertTrue(all(r['n']==240 for r in self.data['historical'] if r['version']=='v1'))
        self.assertFalse(self.data['human_validated'])
        self.assertEqual(self.data['model_calls'],0)

    def test_two_pilots_not_pooled_and_failed_crossover_retained(self):
        self.assertEqual(self.data['pilot_counts']['target_responses'],32)
        self.assertEqual(self.data['crossover_counts']['completed_target'],56)
        self.assertEqual(self.data['crossover_counts']['completed_guard'],96)
        self.assertTrue(all(r['complete_guard_pattern'] is False for r in self.data['crossover_effects']))
        self.assertEqual(self.data['crossover_counts']['cap_hits'],17)

    def test_nested_private_canary_is_not_exported(self):
        import make_unified_nb as mod
        original=mod.load
        def contaminated(root):
            data=original(root)
            for record in data['v2']['steering'].values():
                record['samples']=['PRIVATE_RESPONSE_CANARY_DO_NOT_EXPORT']
            for record in data['v1']['results'].values():
                record['prompt']='PRIVATE_PROMPT_CANARY_DO_NOT_EXPORT'
            return data
        with patch.object(mod,'load',contaminated):
            data=collect(ROOT)
        text=json.dumps(data)
        self.assertNotIn('PRIVATE_RESPONSE_CANARY',text)
        self.assertNotIn('PRIVATE_PROMPT_CANARY',text)

    def test_notebook_output_and_source_bodies_are_not_copied(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'n.ipynb'
            p.write_text(json.dumps({'cells':[{'cell_type':'code','source':['def benign():\n    return "PRIVATE_SOURCE_CANARY"'],
                'outputs':[{'text':'PRIVATE_OUTPUT_CANARY'}]}]}))
            result=definitions(p)
        self.assertEqual(result[0]['name'],'benign')
        self.assertNotIn('CANARY',json.dumps(result))

    def test_portable_cells_have_no_inference_network_or_mount(self):
        with tempfile.TemporaryDirectory() as d:
            nb=build(Path(d)/'companion.ipynb')
        executable='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
        tree=ast.parse(executable)
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.extend(x.name for x in node.names)
            if isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        self.assertFalse(any(x.split('.')[0] in {'torch','transformers','requests','google','huggingface_hub'} for x in imports))
        self.assertNotIn('drive.mount(',executable)
        self.assertNotIn('Model7(',executable)
        self.assertNotIn('from_pretrained(',executable)
        self.assertEqual(nb['metadata']['companion']['model_calls'],0)

    def test_payload_integrity_rejects_changed_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            nb=build(Path(d)/'companion.ipynb')
        code=''.join(nb['cells'][2]['source'])
        altered=code.replace('"completed_target": 56','"completed_target": 55',1)
        self.assertNotEqual(altered,code)
        with self.assertRaises(AssertionError):exec(compile(altered,'test_payload','exec'),{})
        changed=copy.deepcopy(self.data)
        changed['human_validated']=True
        self.assertNotEqual(digest(changed),digest(self.data))

    def test_full_cpu_run_retains_all_tables_and_a_figure(self):
        with tempfile.TemporaryDirectory() as d:
            nb=execute_cpu(build(Path(d)/'companion.ipynb'))
        code=[c for c in nb['cells'] if c['cell_type']=='code']
        self.assertTrue(all(c['execution_count'] for c in code))
        self.assertFalse(any(o['output_type']=='error' for c in code for o in c['outputs']))
        self.assertTrue(any('image/png' in o.get('data',{}) for c in code for o in c['outputs']))
        outputs=json.dumps([c['outputs'] for c in code])
        self.assertIn('Snapshot hash:',outputs)
        self.assertIn('qwen3guard',outputs)


if __name__=='__main__':
    unittest.main()
