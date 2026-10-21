"""Synthetic CPU acceptance tests. No model/network/real private inputs."""
import datetime as dt
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from e2e_crossover import fixture, ROOT
sys.path.insert(0,str(ROOT/'tools'))
import prepare_crossover_audit as audit
import analyze_crossover_audit as analysis


def setup(folder):
    ns,allitems,Target=fixture()
    exec((ROOT/'tools/vlm_window.py').read_text(),ns)
    items=[dict(x) for x in allitems[::2]]
    for i in items:
        i['original']={s['cond']:dict(response='short',text_hash=ns['digest7'](s['text']),image_hash=ns['image_hash7'](s['image'])) for s in ns['specs_cx'](i) if s['cond'] in ns['WINDOW_ARMS']}
    class Tokenizer:
        def decode(self,ids,**kw):return ' '.join(map(str,ids))
    class Model(Target):
        calls=0
        def __init__(self,*args):self.processor=types.SimpleNamespace(tokenizer=Tokenizer())
        def generate(self,spec,*args):
            Model.calls+=1
            return dict(response=Tokenizer().decode(list(range(300))),generated_token_ids=list(range(300)),new_tokens=300,ended_eos=True,seconds=2,order_verified='before')
    ns['Model7']=Model
    seed=Path(folder)/'seed.json'
    seed.write_text(json.dumps(dict(items=items,revisions=ns['PINS_CX'],model_identity=Model.identity)))
    now=[1000.]
    run=ns['WindowRun'](folder,'window_test',now[0],{'test':'v1'},seed,ns['hashlib'].sha256(seed.read_bytes()).hexdigest(),lambda:dict(cells=[dict(cell_type='markdown',source=['synthetic'])]),now=lambda:now[0])
    return ns,run,Model,now,seed


class WindowTests(unittest.TestCase):
    def test_tokens_and_early_eos(self):
        with tempfile.TemporaryDirectory() as d:
            ns,run,_,_,_=setup(d)
            views=ns['window_views'](dict(response='1 2',generated_token_ids=[1,2],new_tokens=2,ended_eos=True),lambda ids:' '.join(map(str,ids)))
            self.assertEqual(views[0]['response'],views[1]['response']);self.assertFalse(any(v['truncated'] for v in views))
            for bad in [dict(response='x',generated_token_ids=[1],new_tokens=1,ended_eos=True),dict(response='',generated_token_ids=[],new_tokens=0,ended_eos=False)]:
                with self.assertRaises(ValueError):ns['window_views'](bad,str)

    def test_full_run_exports_resume_and_privacy(self):
        with tempfile.TemporaryDirectory() as d:
            ns,w,Model,now,seed=setup(d)
            result=w.run(Path(d)/'cache')
            self.assertEqual((Model.calls,len(w.units),len(w.rows)),(32,64,128))
            self.assertEqual(result['full_cap_hits'],0);self.assertEqual(result['prefix_drift'],32)
            self.assertEqual(len(list((w.out/'labels').glob('*.json'))),128)
            text=json.dumps(result)
            for forbidden in ('Name a color','generated_token_ids','stimulus','payload','generation_key','row_id'):
                self.assertNotIn(forbidden,text)
            now[0]+=100
            resumed=ns['WindowRun'](d,'window_test',now[0],{'test':'v1'},seed,ns['hashlib'].sha256(seed.read_bytes()).hexdigest(),w.snapshotter,now=lambda:now[0])
            self.assertEqual(resumed.started,1000.);resumed.run(Path(d)/'cache');self.assertEqual(Model.calls,32)
            state=w.out/'state_PRIVATE.json';obj=json.loads(state.read_text());obj['units'][0]['response']='tampered';state.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):ns['WindowRun'](d,'window_test',now[0],{'test':'v1'},seed,ns['hashlib'].sha256(seed.read_bytes()).hexdigest(),w.snapshotter)

    def test_deadline_partial_and_identity(self):
        with tempfile.TemporaryDirectory() as d:
            ns,w,Model,now,seed=setup(d);now[0]=w.deadline
            result=w.run(Path(d)/'cache');self.assertEqual(Model.calls,0);self.assertEqual(result['target_completed'],0);self.assertGreater(result['failures'],0)
            with self.assertRaises(ValueError):ns['WindowRun'](d,'window_test',now[0],{'test':'changed'},seed,ns['hashlib'].sha256(seed.read_bytes()).hexdigest(),w.snapshotter)

    def test_review_package_analysis_and_delayed_retest(self):
        with tempfile.TemporaryDirectory() as d:
            ns,w,Model,now,seed=setup(d);w.run(Path(d)/'cache')
            pkg=Path(d)/'review';m=audit.build_window_package(w,pkg,ns['WINDOW_RUBRIC'],ns['specs_cx'])
            key=audit.read(pkg/'analyst_PRIVATE/key_PRIVATE.json')
            a=Path(d)/'human.json';saved=dt.datetime(2026,10,20,tzinfo=dt.timezone.utc)
            obj=dict(schema='crossover-human-review-1',package_id=m['package_id'],reviewer_slot='A',reviewer='Test human',reference_kind='human',saved_utc=saved.isoformat(),labels=[dict(row_id=k['row_id'],refusal='NO',harm='NO',comprehension='UNDERSTANDING',notes='') for k in key]);audit.write(a,obj)
            out=analysis.analyze_window(pkg,[a],ns['window_summary']);self.assertEqual(out['changes'][0]['conclusion'],'unchanged_on_eight_seen_items')
            repeat=Path(d)/'repeat'
            with self.assertRaises(ValueError):audit.window_retest(pkg,a,repeat,now=saved+dt.timedelta(hours=23))
            self.assertEqual(audit.window_retest(pkg,a,repeat,now=saved+dt.timedelta(hours=25))['units'],16)
            meta=audit.read(repeat/'analyst_PRIVATE/retest_key_PRIVATE.json')
            self.assertEqual(len(meta['mapping']),16)
            bad=dict(obj,labels=obj['labels']+[obj['labels'][0]]);audit.write(a,bad)
            with self.assertRaises(ValueError):analysis.analyze_window(pkg,[a],ns['window_summary'])
            audit.write(a,obj);obj['labels'][0]['harm']='INVALID';audit.write(a,obj)
            with self.assertRaises(ValueError):analysis.analyze_window(pkg,[a],ns['window_summary'])

    def test_normalization_rejects_duplicate_and_invalid_source(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);(folder/'reviewer_B_PRIVATE.html').write_text('synthetic packet')
            source=folder/'b.json';dest=folder/'derived.json'
            record=dict(package_id='p',human_reviewer=False,annotator_kind='llm_annotator',source_slot='B',reviewer='LLM',source_sha256=audit.sha(folder/'reviewer_B_PRIVATE.html'),rows=[dict(row_id='one',refusal='NO',harmful_assistance='NO',comprehension='UNCERTAIN')])
            audit.write(source,record);original=source.read_bytes()
            with patch.object(analysis,'package',return_value=({'package_id':'p'},[{'row_id':'one'}])):
                derived=analysis.normalize_llm(source,folder,dest,'GPT-6.1-Sol','2026-10-20')
                self.assertEqual(source.read_bytes(),original)
                self.assertEqual(derived['reference_kind'],'llm_annotator')
                self.assertIsNone(derived['provenance']['backend_revision'])
                record['rows']*=2;audit.write(source,record)
                with self.assertRaises(ValueError):analysis.normalize_llm(source,folder,folder/'bad.json','GPT-6.1-Sol','2026-10-20')
                record['rows']=record['rows'][:1];record['source_sha256']='wrong';audit.write(source,record)
                with self.assertRaises(ValueError):analysis.normalize_llm(source,folder,folder/'bad.json','GPT-6.1-Sol','2026-10-20')

    def test_embedded_dependencies(self):
        sys.path.insert(0,str(ROOT/'tools/nb_gen'))
        from make_window_nb import build
        with tempfile.TemporaryDirectory() as d:
            nb=build(Path(d)/'window.ipynb',execute=False)
            config={}
            # Extract only the literal embedded sources without executing GPU branches.
            import ast
            for c in nb['cells']:
                if c['cell_type']=='code':
                    for node in ast.parse(''.join(c['source'])).body:
                        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCES' for t in node.targets):config=ast.literal_eval(node.value)
            embedded=dict(json=json,Path=Path,hashlib=__import__('hashlib'),CHOICES=audit.CHOICES)
            exec(config['package'],embedded)
            self.assertIn('Private human review',embedded['reviewer_html']('id','A',[]))

if __name__=='__main__':unittest.main()
