"""CPU regressions for audit provenance, partial labels, blinding and escaping."""
import contextlib
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'tools'), str(Path(__file__).parent)]
from e2e_crossover import fixture  # noqa: E402
from prepare_crossover_audit import build, read, write, sha, verify_source, reviewer_html, GUARDS  # noqa: E402
from analyze_crossover_audit import analyze, package, agreement  # noqa: E402


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        ns, _, target = fixture()
        target.identity = dict(model=ns['MODEL_CX'], revision=ns['PINS_CX'][ns['MODEL_CX']])
        original = ns['Guard7']
        class Guard(original):
            def __init__(self, judge, *_):
                self.identity = dict(model=GUARDS[judge], revision=ns['PINS_CX'][GUARDS[judge]])
        ns['Guard7'] = Guard
        ns['tier_cx'] = lambda *_: dict(add_second_block=False)
        from make_nb7 import frozen_helpers
        hashes = {'nc_helpers': hashlib.sha256(frozen_helpers().encode()).hexdigest()}
        run = ns['CrossoverRun'](self.root, 'synthetic', ns['time'].time(), hashes,
                                 lambda: {'cells': [{'cell_type': 'code', 'source': ['# synthetic']}]})
        with contextlib.redirect_stdout(io.StringIO()):
            run.run(self.root/'weights')
        self.source, self.out = run.out, self.root/'audit_PRIVATE'
        self.expected = self.source/'results_crossover.json'
        self.manifest = build(self.source, self.out, expected=self.expected)
        self.key = read(self.out/'analyst_PRIVATE/key_PRIVATE.json')

    def review(self, slot, label='NO', kind='human'):
        data = dict(schema='crossover-human-review-1', package_id=self.manifest['package_id'],
            reviewer_slot=slot, reviewer='Person '+slot, reference_kind=kind,
            labels=[dict(row_id=r['row_id'], refusal=label, harm=label,
                         comprehension='UNDERSTANDING' if label else '', notes='PRIVATE_NOTE_CANARY') for r in self.key])
        path = self.root/(slot+'.json')
        write(path, data)
        return path

    def test_full_provenance_and_reviewers_are_blinded(self):
        self.assertEqual(self.manifest['answering_rows'], 48)
        self.assertEqual(self.manifest['items'], 8)
        for slot in ('A', 'B'):
            html = (self.out/f'reviewer_{slot}_PRIVATE.html').read_text()
            for hidden in ('generation_key', 'qwen3guard', 'wildguard', 'P_txt', 'S_img', 'hypothesis', self.key[0]['uid']):
                self.assertNotIn(hidden, html)
            self.assertNotIn('fetch(', html)
            self.assertNotIn('localStorage', html)
        self.assertEqual(len(package(self.out)[1]), 48)
        with self.assertRaises(ValueError): build(self.source, self.out, expected=self.expected)

    def test_response_html_cannot_escape_json_script(self):
        html = reviewer_html('x', 'A', [dict(row_id='x', prompt='</script><script>ATTACK',
                                           response='<img onerror=ATTACK>', image=None)])
        self.assertNotIn('</script><script>ATTACK', html)
        self.assertIn('\\u003c/script>', html)
        self.assertIn('.textContent=r.response', html)
        self.assertNotIn('innerHTML', html)

    @unittest.skipUnless(shutil.which('node'), 'Node is required for the DOM unit fixture')
    def test_reviewer_download_and_resume_logic(self):
        html = reviewer_html('test-package', 'A', [dict(row_id=str(i), prompt='Name a color.',
                                                    response='Blue.', image=None) for i in range(2)])
        payload = re.search(r'type="application/json">(.*?)</script>', html, re.S)[1]
        source = re.findall(r'<script>(.*?)</script>', html, re.S)[0]
        harness = r'''
const vm=require('node:vm'),assert=require('node:assert/strict');
const ids={},alerts=[],downloads=[];
function element(){const e={value:'',textContent:'',children:[],files:[],handlers:{},append(x){this.children.push(x)},
 addEventListener(n,f){this.handlers[n]=f},removeAttribute(){},click(){},hidden:false};
 Object.defineProperty(e,'id',{set(id){ids[id]=this}});return e;}
for(const id of ['data','reviewer','kind','labels','notes','status','position','prompt','response','image','go','prev','next','save','load'])ids[id]=element();
ids.data.textContent=PAYLOAD;
const sandbox={document:{getElementById:id=>ids[id],createElement:()=>element()},alert:m=>alerts.push(m),
 Blob:class{constructor(parts){this.parts=parts}},URL:{createObjectURL(b){downloads.push(b.parts.join(''));return 'blob:test'},revokeObjectURL(){}}};
vm.runInNewContext(SOURCE,sandbox);
ids.reviewer.value='Person A';ids.kind.value='human';
ids.refusal.value='NO';ids.harm.value='NO';ids.comprehension.value='UNDERSTANDING';ids.notes.value='Synthetic note';
ids.save.onclick();const saved=JSON.parse(downloads[0]);
assert.equal(saved.labels[0].refusal,'NO');assert.equal(saved.labels[1].refusal,'');
ids.next.onclick();assert.equal(ids.refusal.value,'');ids.prev.onclick();assert.equal(ids.notes.value,'Synthetic note');
(async()=>{ids.load.files=[{text:async()=>JSON.stringify(saved)}];await ids.load.onchange();assert.equal(ids.refusal.value,'NO');
 const bad={...saved,package_id:'wrong'};ids.load.files=[{text:async()=>JSON.stringify(bad)}];await ids.load.onchange();
 assert.equal(alerts.length,1);assert.equal(ids.refusal.value,'NO');})().catch(e=>{console.error(e);process.exitCode=1});
'''.replace('PAYLOAD', json.dumps(payload)).replace('SOURCE', json.dumps(source))
        completed = subprocess.run([shutil.which('node'), '-'], input=harness, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_generation_tamper_and_rehashed_index_tamper_fail(self):
        p = next((self.source/'generations').glob('*.json'))
        data = read(p)
        data['value']['response'] = 'modified synthetic answer'
        write(p, data)
        with self.assertRaises(ValueError): verify_source(self.source, self.expected)
        from prepare_crossover_audit import digest
        data['value_hash'] = digest(data['value'])
        write(p, data)
        with self.assertRaises(ValueError): verify_source(self.source, self.expected)

    def test_analysis_nc_tamper_and_package_tamper_fail(self):
        p = self.source/'analysis_rows_PRIVATE.json'
        rows = read(p)
        rows[0]['nc'] = not rows[0]['nc']
        write(p, rows)
        with self.assertRaises(ValueError): verify_source(self.source, self.expected)
        p = self.out/'reviewer_A_PRIVATE.html'
        p.write_text(p.read_text()+'tamper')
        with self.assertRaises(ValueError): package(self.out)

    def test_missing_uncertain_and_degenerate_kappa(self):
        path = self.review('A', '')
        data = read(path)
        data['labels'] = data['labels'][:1]
        data['labels'][0]['refusal'] = 'UNCERTAIN'
        write(path, data)
        result = analyze(self.out, [path])
        cell = result['outcomes'][0]['cells'][0]
        self.assertEqual(cell['valid'], 0)
        self.assertEqual(cell['bounds'], [0, 1])
        self.assertIsNone(cell['observed_rate'])
        self.assertIsNone(agreement([(False, False)]*5)['kappa'])
        self.assertEqual(result['confirmatory_gate'], 'not_satisfied')

    def test_disagreement_retained_and_public_fields_are_allowlisted(self):
        result = analyze(self.out, [self.review('A'), self.review('B', 'YES')])
        consensus = result['outcomes'][2]
        refusal = [r for r in consensus['cells'] if r['axis'] == 'refusal']
        self.assertTrue(all(r['valid'] == 0 and r['bounds'] == [0, 1] for r in refusal))
        for forbidden in ('PRIVATE_NOTE_CANARY', self.key[0]['uid'], self.key[0]['row_id'], 'Person A', 'response_sha256'):
            self.assertNotIn(forbidden, json.dumps(result))

    def test_bad_label_duplicate_wrong_package_and_llm_provenance(self):
        path = self.review('A', kind='llm_annotator')
        self.assertFalse(analyze(self.out, [path])['all_references_human'])
        original = read(path)
        for mutation in ('bad_label', 'duplicate', 'package'):
            data = json.loads(json.dumps(original))
            if mutation == 'bad_label': data['labels'][0]['harm'] = 'SAFE'
            if mutation == 'duplicate': data['labels'].append(data['labels'][0])
            if mutation == 'package': data['package_id'] = 'wrong'
            write(path, data)
            with self.assertRaises(ValueError): analyze(self.out, [path])

    def test_counts_and_originals_preserved(self):
        before = sha(self.expected)
        paths = [self.review('A'), self.review('B')]
        result = analyze(self.out, paths)
        self.assertTrue(result['all_references_human'])
        self.assertEqual(result['reviewer_coverage'][0]['complete_rows'], 48)
        self.assertTrue(all(c['valid'] == 8 for c in result['outcomes'][0]['cells']))
        self.assertEqual(result['between_reviewers'][0]['agreement'], 1)
        self.assertEqual(before, sha(self.expected))
        duplicate = read(paths[1]);duplicate['reviewer'] = 'Person A';write(paths[1], duplicate)
        with self.assertRaises(ValueError): analyze(self.out, paths)

    def test_portable_next_stage_notebook_and_embedded_analysis(self):
        sys.path.insert(0, str(ROOT/'tools/nb_gen'))
        from make_human_validation_nb import build as build_notebook
        nb = build_notebook(package_folder=self.out.name,
                            package_manifest_sha256=sha(self.out/'analyst_PRIVATE/package_manifest_PRIVATE.json'))
        scope = {}
        with contextlib.redirect_stdout(io.StringIO()):
            for cell in nb['cells']:
                if cell['cell_type'] == 'code':
                    exec(compile(''.join(cell['source']), 'notebook_cpu_fixture', 'exec'), scope)
        self.assertFalse(scope['LOAD_PRIVATE_AUDIT'])
        self.assertIsNone(scope['PRIVATE_PACKAGE'])
        self.assertIsNone(scope['human_analysis'])
        path = self.review('A')
        self.assertEqual(scope['analyze'](self.out, [path]), analyze(self.out, [path]))
        source = json.dumps(nb)
        for row in self.key:
            self.assertNotIn(row['row_id'], source)
            self.assertNotIn(row['uid'], source)


if __name__ == '__main__':
    unittest.main()
