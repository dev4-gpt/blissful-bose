"""Meaningful CPU tests for real v7 cells and failure isolation; no downloads/GPU."""
import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import vlm7_core as core  # noqa: E402
sys.path.insert(0,str(ROOT/'tools/nb_gen'))
from vlm7_explanations import AFTER, run_readout7  # noqa: E402
from vlm_audit_estimation import stratified_difference, synthetic_demo  # noqa: E402


class AuditEstimationTests(unittest.TestCase):
    def test_companion_notebook_executes_only_synthetic_cpu_example(self):
        nb = json.loads((ROOT/'notebooks/vlm_methodology_review.ipynb').read_text())
        code_cells = [c for c in nb['cells'] if c['cell_type']=='code']
        self.assertEqual(len(code_cells), 1)
        source = ''.join(code_cells[0]['source'])
        for forbidden in ('import torch', 'google.colab', 'drive.mount', 'HF_TOKEN', 'import requests'):
            self.assertNotIn(forbidden, source)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exec(compile(source, 'companion_demo', 'exec'), {})
        self.assertEqual(out.getvalue(), ''.join(code_cells[0]['outputs'][0]['text']))
        self.assertEqual(json.loads(out.getvalue())['reference'], 'synthetic')

    def test_oversampling_does_not_turn_half_the_audit_into_half_the_population(self):
        result = synthetic_demo()
        self.assertAlmostEqual(result['naive_audit_mean'], .5)
        self.assertAlmostEqual(result['corrected_mean'], .1)
        self.assertEqual(result['reference'], 'synthetic')
        self.assertTrue(result['warnings'])
        self.assertNotIn('ci95', result)

    def test_exact_enumeration_checks_unbiasedness_and_variance(self):
        from itertools import combinations
        from statistics import mean, pvariance
        y, auto = [0., 1., 1., 0.], [0., 0., 1., 1.]
        population = [dict(stratum='h', population_size=4, auto_mean=.5)]
        results = []
        for selected in combinations(range(4), 2):
            audit = [dict(stratum='h', unit_id=str(i), human=y[i], auto=auto[i]) for i in selected]
            results.append(stratified_difference(population, audit,
                design='stratified_srswor', reference='synthetic'))
        estimates = [r['corrected_mean'] for r in results]
        self.assertAlmostEqual(mean(estimates), mean(y))
        self.assertAlmostEqual(mean(r['design_variance_estimate'] for r in results), pvariance(estimates))

    def test_census_and_paired_contrast_are_exact(self):
        population = [dict(stratum='h', population_size=2, auto_mean=0.)]
        audit = [dict(stratum='h', unit_id=str(i), human=y, auto=0.) for i,y in enumerate([-1.,0.])]
        result = stratified_difference(population, audit, design='stratified_srswor',
            reference='human', bounds=(-1., 1.))
        self.assertEqual(result['corrected_mean'], -.5)
        self.assertEqual(result['deterministic_label_bounds'], [-.5, -.5])
        self.assertEqual(result['design_variance_estimate'], 0.)

    def test_missing_strata_duplicate_units_and_nonrandom_design_fail_closed(self):
        population = [dict(stratum='h', population_size=4, auto_mean=.5)]
        row = dict(stratum='h', unit_id='unit', human=1., auto=0.)
        for audit, design in [([], 'stratified_srswor'), ([row,row], 'stratified_srswor'),
                              ([row], 'disagreement_convenience')]:
            with self.assertRaises(ValueError):
                stratified_difference(population, audit, design=design, reference='human')

    def test_singletons_and_unclipped_estimates_are_not_falsely_precise(self):
        population = [dict(stratum='h', population_size=4, auto_mean=.5)]
        row = dict(stratum='h', unit_id='unit', human=1., auto=0.)
        result = stratified_difference(population, [row], design='stratified_srswor', reference='human')
        self.assertIsNone(result['standard_error'])
        self.assertEqual(result['corrected_mean'], 1.5)
        self.assertEqual(result['deterministic_label_bounds'], [.25, 1.])

    def test_no_raw_payloads_or_inconsistent_census_can_enter_the_prototype(self):
        population = [dict(stratum='h', population_size=1, auto_mean=1.)]
        row = dict(stratum='h', unit_id='unit', human=1., auto=0.)
        for sample in ([row], [dict(row, response='PRIVATE_RESPONSE_SENTINEL')]):
            with self.assertRaises(ValueError):
                stratified_difference(population, sample, design='stratified_srswor', reference='human')


class CoreTests(unittest.TestCase):
    def test_readout_uses_aggregates_and_does_not_call_smoke_safety_evidence(self):
        result=dict(status='benign_smoke_only',attempted_models=2,responding_models=1,failures=[{}],
                    model_checks={'m':{'B':True,'E':True,'C':False,'READ_C':False}},
                    response='PRIVATE_RESPONSE_SENTINEL',meta={'requires_python_restart':True})
        text=run_readout7(result)
        self.assertIn('no safety finding',text)
        self.assertIn('Selected checkpoints: 2',text)
        self.assertIn('| m | B, E |',text)
        self.assertIn('CUDA context invalid',text)
        self.assertNotIn('PRIVATE_RESPONSE_SENTINEL',text)
        text=run_readout7(dict(status='guard_labelled_exploratory',contrasts=[dict(model='m',
            benchmark='mm',judge='j',contrast='E-C',n=8,diff=-.12,ci95=[-.2,-.04])]))
        self.assertIn('-12.0 | -20.0 to -4.0',text)
        self.assertIn('No hypothesis verdict',text)

    def test_each_result_block_has_an_editable_explanation(self):
        cells=json.loads((ROOT/'notebooks/vlm_modality_tradeoff_v7.ipynb').read_text())['cells']
        for title in AFTER:
            i=next(i for i,c in enumerate(cells) if ''.join(c['source']).strip()=='## '+title)
            self.assertEqual(cells[i+1]['cell_type'],'code')
            self.assertEqual(cells[i+2]['cell_type'],'markdown')
            self.assertEqual(''.join(cells[i+2]['source']),AFTER[title])
        self.assertIn('awaiting review',''.join(cells[-1]['source']))

    def test_logits_guard_rejects_invalid_scores_without_repair(self):
        import torch
        from vlm7_models import ValidLogits7
        guard=ValidLogits7()
        ids=torch.tensor([[1]])
        for values in ([[float('nan'),0.]],[[float('inf'),0.]],[[float('-inf'),float('-inf')]]):
            with self.assertRaises(FloatingPointError):
                guard(ids,torch.tensor(values))
        good=torch.tensor([[float('-inf'),1.]])
        self.assertTrue(torch.equal(guard(ids,good),good))

    def test_checkpoint_identity_and_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            calls = []
            operation = lambda: calls.append(1) or dict(response='private benign fixture')
            ctx = dict(model='m',revision='r1',seed=0)
            a,hit = core.cached7(folder,'gen',ctx,operation)
            self.assertFalse(hit)
            self.assertEqual(core.cached7(folder,'gen',ctx,operation),(a,True))
            self.assertEqual(len(calls),1)
            core.cached7(folder,'gen',dict(ctx,seed=1),operation)
            self.assertEqual(len(calls),2)
            path = next(Path(folder).glob('*'+core.digest7(ctx)+'.json'))
            record = json.loads(path.read_text())
            record['value']['response'] = 'corrupt'
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError,'content mismatch'):
                core.cached7(folder,'gen',ctx,operation)

    def test_partition_duplicate_exclusion_and_determinism(self):
        items = [dict(uid=str(i),cluster='a',question='Question '+str(i)) for i in range(12)]
        items.append(dict(uid='alias',cluster='b',question='Question 1'))
        selected,counts = core.split_items7(items,{'1'},2,5)
        self.assertEqual((selected,counts),core.split_items7(list(reversed(items)),{'1'},2,5))
        fresh = [x for x in selected if x['subset']=='confirmatory']
        self.assertTrue(all(x['uid'] not in {'1','alias'} for x in fresh))
        dev = {core.norm7(x['question']) for x in selected if x['subset']=='development'}
        self.assertFalse(dev & {core.norm7(x['question']) for x in fresh})

    def test_image_payload_clipping_rejected(self):
        with self.assertRaises(ValueError):
            core.text_image7('word '*10000)

    def test_data_loader_uses_original_ids_and_source_paths(self):
        import pandas as pd
        image = core.text_image7('Benign fixture instruction')
        stream = io.BytesIO()
        image.save(stream,format='PNG')
        raw = stream.getvalue()
        source = {str(i):{'Question':'Benign question '+str(i),'Key Phrase':'Benign fixture instruction',
            'Rephrased Question':'The image shows a phrase.'} for i in range(3)}
        paths = [f'data/processed_questions/{(9 if s=="Privacy_Violence" else j):02d}-{s}.json'
                 for j,s in enumerate(core.SCENARIOS7,1)]
        requested=[]
        def get(url,**_):
            requested.append(url)
            data = {'tree':[{'path':p} for p in paths]} if '/git/trees/' in url else source
            return types.SimpleNamespace(raise_for_status=lambda:None,json=lambda:data)
        def parquet(path):
            if 'test-00000' in path:
                return pd.DataFrame([dict(category_id=1,task_id=i,question='FS question '+str(i),
                    instruction='Benign fixture instruction',jailbreak_prompt='The image shows a list.',image={'bytes':raw}) for i in range(22)])
            if 'Text_only' in path:
                return pd.DataFrame([dict(id=i,question='Benign question '+str(i)) for i in [2,0,1]])
            return pd.DataFrame([dict(id=i,question='The image shows a phrase.',image=raw) for i in [1,2,0]])
        hub=types.ModuleType('huggingface_hub')
        hub.hf_hub_download=lambda repo,fname,**_:fname
        ocr=types.ModuleType('pytesseract')
        ocr.image_to_string=lambda _: 'Benign fixture instruction'
        with patch.dict(sys.modules,{'huggingface_hub':hub,'pytesseract':ocr}),patch('requests.get',get),patch('pandas.read_parquet',parquet),patch.object(core,'historical_ids7',return_value=({'Illegal_Activitiy|0'},[])):
            items,info=core.load_items7('/unused',{'mm':'mmsha','figstep':'fssha','mm_source':'gitsha'})
        self.assertEqual(info['ocr_verified_mm'],24)
        self.assertTrue(any('09-Privacy_Violence.json' in u for u in requested))
        self.assertEqual(sum(x['benchmark']=='figstep' and x['subset']=='confirmatory' for x in items),2)

    def test_group_held_out_forecast(self):
        points = [dict(model=str(i),family=str(i//2),B=i/8,E=i/9,C=.1+i/10) for i in range(8)]
        forecast = core.forecast7(points)
        self.assertAlmostEqual(forecast['r2'],1.)
        self.assertAlmostEqual(forecast['mae'],0.)
        self.assertIn('fewer_than_eight',core.forecast7(points[:7])['status'])
        self.assertIsNone(core.forecast7([dict(p,C=.2) for p in points])['r2'])

    def test_greedy_and_sampling_remain_separate(self):
        rows = []
        for draw in range(-1,8):
            rows.append(dict(model='m',family='f',benchmark='mm',judge='keyword',cond='B',
                uid='u',cluster='c',draw=draw,refusal=draw>=0,unsafe=None,nc=False,tokens=None))
        result = core.summarize7(rows,bootstrap=8)
        self.assertEqual(result['rates'][0]['refusal'],0.)
        self.assertEqual(result['sampling'][0]['k_hist']['8'],1)
        self.assertEqual(result['rates'][0]['unsafe_missing'],1)

    def test_no_unpaired_or_incomplete_forecast_claim(self):
        rows=[]
        for m in range(8):
            for uid in range(4):
                for cond in ('B','E','C'):
                    if m==7 and uid==3 and cond=='C':
                        continue
                    rows.append(dict(model=str(m),family=str(m//2),benchmark='mm',judge='qwen3guard',
                        cond=cond,uid=str(uid),cluster=str(uid//2),draw=-1,refusal=(m+uid)%2==0,
                        unsafe=False,nc=False,tokens=None))
        result=core.summarize7(rows,bootstrap=8,expected={'mm':[str(i) for i in range(4)]})
        self.assertIn('incomplete',result['h29']['mm/qwen3guard']['status'])
        self.assertIsNone(result['h28']['mm/qwen3guard']['one_sided_p'])

    def test_audit_has_probabilities_and_no_reply_in_key(self):
        rows=[]
        for i in range(12):
            for j in ('qwen3guard','wildguard'):
                rows.append(dict(model='m',benchmark='mm',cond='C',uid=str(i),judge=j,
                    refusal=(i<6 and j=='qwen3guard'),nc=False,draw=-1,stimulus='benign',response='fixture'))
        with tempfile.TemporaryDirectory() as folder:
            core.audit7(rows,folder)
            keys=json.loads((Path(folder)/'audit_v7_key_PRIVATE.json').read_text())
            self.assertEqual(len(keys),8)
            self.assertTrue(all(x['population_size']==6 and x['inclusion_probability']==4/6 for x in keys))
            self.assertTrue(all('response' not in x and 'stimulus' not in x for x in keys))


class NotebookTests(unittest.TestCase):
    def run_cells(self, mode='smoke', fail_model=False, fail_guard=False, fail_generation=False, fatal_cuda=False):
        notebook=json.loads((ROOT/'notebooks/vlm_modality_tradeoff_v7.ipynb').read_text())
        ns={'__name__':'v7_notebook_test'}
        with tempfile.TemporaryDirectory() as temp:
            content=Path(temp)/'content'
            content.mkdir()
            (content/'drive/MyDrive').mkdir(parents=True)
            torch=types.ModuleType('torch')
            torch.cuda=types.SimpleNamespace(is_available=lambda:True,empty_cache=lambda:None)
            transformers=types.ModuleType('transformers')
            for n in ('AutoModelForImageTextToText','AutoModelForCausalLM','AutoProcessor','AutoTokenizer','BitsAndBytesConfig','LogitsProcessor'):
                setattr(transformers,n,type(n,(),{}))
            colab=types.ModuleType('google.colab')
            colab.drive=types.SimpleNamespace(mount=lambda _:None)
            colab.userdata=types.SimpleNamespace(get=lambda _: (_ for _ in ()).throw(KeyError()))
            hub=types.ModuleType('huggingface_hub')
            hub.HfApi=lambda:types.SimpleNamespace(model_info=lambda _:types.SimpleNamespace(sha='fixed-sha'))
            calls=[]
            class FakeModel:
                def __init__(self,name,revision,four_bit,cache_dir):
                    if fail_model and 'llava' in name:
                        raise MemoryError('simulated')
                    self.name=name
                    self.identity=dict(model=name,revision=revision)
                def generate(self,spec,max_new,seed):
                    calls.append(spec['cond'])
                    if fatal_cuda and spec['cond']=='C' and seed==0:
                        raise RuntimeError('CUDA error: device-side assert triggered')
                    if fail_generation and spec['cond']=='C':
                        raise RuntimeError('simulated')
                    return dict(response='I cannot help.' if spec['cond']=='B' else 'Two colors are red and blue.',
                        tokens=32 if spec['image'] else None,seconds=.01,peak_gpu_gb=.1,
                        new_tokens=8,input_tokens=16,order_verified=spec['position'])
                def close(self):
                    if fatal_cuda:
                        raise RuntimeError('CUDA error: device-side assert triggered')
            class FakeGuard:
                def __init__(self,judge,revision,cache_dir):
                    if fail_guard and judge=='wildguard':
                        raise OSError('simulated gated failure')
                    self.identity=dict(model=judge,revision=revision)
                def label(self,stimulus,reply):
                    return dict(refuse='cannot' in reply,unsafe=False)
                def close(self):
                    pass
            modules={'torch':torch,'transformers':transformers,'google.colab':colab,'huggingface_hub':hub}
            with patch.dict(sys.modules,modules),contextlib.redirect_stdout(io.StringIO()):
                for cell in notebook['cells']:
                    if cell['cell_type']!='code':
                        continue
                    source=''.join(cell['source'])
                    if source.startswith('%pip'):
                        continue
                    if source.startswith('MODE =') or source.startswith('# Owner-approved'):
                        source=source.replace("MODE = 'smoke'",f"MODE = '{mode}'").replace('SCIENTIFIC_BUDGET_APPROVED = False','SCIENTIFIC_BUDGET_APPROVED = True')
                    if 'drive.mount' in source:
                        source=source.replace('/content',str(content))
                    if source.startswith("if MODE == 'smoke':") and 'frozen7 =' in source:
                        # Real frozen-partition, hashing and immutability code; fixture replaces network data only.
                        source="ITEMS7, DATAINFO7 = smoke_items7(), dict(source='fixture')\n"+source[source.index('frozen7 ='):]
                    exec(compile(source,'<v7 cell>','exec'),ns)
                    if 'class Model7:' in source:
                        ns.update(Model7=FakeModel,Guard7=FakeGuard,environment7=lambda:dict(gpu='stub',packages={}))
                    if 'PANEL7 = ' in source:
                        ns['PANEL7']=[core.PANEL7[0],core.PANEL7[2],core.PANEL7[4]]
                    if 'def summarize7' in source:
                        original=ns['summarize7']
                        ns['summarize7']=lambda rows,expected=None:original(rows,bootstrap=8,expected=expected)
                out=content/'drive/MyDrive/vlm_tradeoff_out_v7'/mode
                result=json.loads((out/'results_v7.json').read_text())
                import zipfile
                with zipfile.ZipFile(out/'bundle_v7.zip') as bundle:
                    self.assertTrue(set(bundle.namelist())<= {'results_v7.json','v7_contrasts.csv','fig_v7_contrasts.png'})
                self.assertNotIn('Two colors',json.dumps(result))
                self.assertNotIn('I cannot help',json.dumps(result))
                return result,calls

    def test_actual_smoke_cells(self):
        result,calls=self.run_cells()
        self.assertEqual(result['responding_models'],3)
        self.assertIn('dose_224_after',calls)
        self.assertEqual(result['status'],'benign_smoke_only')

    def test_model_failure_isolated(self):
        result,_=self.run_cells(fail_model=True)
        self.assertEqual(result['responding_models'],2)
        self.assertTrue(result['failures'])

    def test_poisoned_cuda_stops_panel_and_still_exports(self):
        result,_=self.run_cells(fatal_cuda=True)
        self.assertEqual(result['responding_models'],1)
        self.assertTrue(result['meta']['requires_python_restart'])
        self.assertTrue(any(x.get('cond')=='C' and x.get('draw')==0 for x in result['failures']))

    def test_guard_and_condition_failure_isolated(self):
        result,_=self.run_cells(mode='development',fail_guard=True,fail_generation=True)
        self.assertTrue(any(x.get('judge')=='wildguard' for x in result['failures']))
        self.assertTrue(any(x.get('cond')=='C' for x in result['failures']))
        self.assertTrue(result['rates'])
        self.assertEqual(result['status'],'guard_labelled_exploratory')

    def test_confirmatory_mode_blocked_without_human_audit(self):
        with self.assertRaisesRegex(RuntimeError,'passing human gate'):
            self.run_cells(mode='confirmatory')


if __name__=='__main__':
    unittest.main(verbosity=2)
