"""Bounded Amendment-5 development pilot; no reserved outcomes or new hypotheses."""
import ast
import json
from pathlib import Path
from make_nb7 import build, CONFIG, SETUP, GENERATE

ROOT = Path(__file__).resolve().parents[2]
MODEL = 'Qwen/Qwen2-VL-2B-Instruct'
DATA_PILOT = '''# Previously seen MM items only; one OCR-eligible item per scenario.
if MODE!='development' or MODEL_FILTER!=['Qwen/Qwen2-VL-2B-Instruct']:
    raise ValueError('This bounded pilot supports development and the verified Qwen2 anchor only')
from huggingface_hub import hf_hub_download
import requests, pytesseract
seen_pilot7, history_pilot7 = historical_ids7(MYDRIVE7)
pins_pilot7 = OUT7/'dataset_revisions_PRIVATE.json'
if pins_pilot7.exists():
    dataset_revisions7 = json.loads(pins_pilot7.read_text())
else:
    commit_pilot7 = requests.get('https://api.github.com/repos/isXinLiu/MM-SafetyBench/commits/main',timeout=30)
    commit_pilot7.raise_for_status()
    dataset_revisions7 = dict(mm=API7.dataset_info('PKU-Alignment/MM-SafetyBench').sha,
                             mm_source=commit_pilot7.json()['sha'])
    atomic7(pins_pilot7,dataset_revisions7)
tree_pilot7 = requests.get('https://api.github.com/repos/isXinLiu/MM-SafetyBench/git/trees/'+dataset_revisions7['mm_source']+'?recursive=1',timeout=60)
tree_pilot7.raise_for_status()
paths_pilot7 = [r['path'] for r in tree_pilot7.json()['tree'] if r['path'].startswith('data/processed_questions/')]
ITEMS7 = []
for scenario7 in SCENARIOS7:
    budget7()
    tables_pilot7 = {}
    for split7 in ('Text_only','TYPO'):
        path_pilot7 = hf_hub_download('PKU-Alignment/MM-SafetyBench',f'data/{scenario7}/{split7}.parquet',repo_type='dataset',revision=dataset_revisions7['mm'])
        frame_pilot7 = pd.read_parquet(path_pilot7)
        if frame_pilot7['id'].astype(str).duplicated().any():
            raise ValueError('Duplicate source IDs')
        tables_pilot7[split7] = frame_pilot7.set_index(frame_pilot7['id'].astype(str))
    if set(tables_pilot7['Text_only'].index)!=set(tables_pilot7['TYPO'].index):
        raise ValueError('Text/image source IDs differ')
    matches_pilot7 = [p for p in paths_pilot7 if re.search(r'/\\d+-'+re.escape(scenario7)+r'\\.json$',p)]
    if len(matches_pilot7)!=1:
        raise ValueError('Ambiguous metadata source')
    response_pilot7 = requests.get('https://raw.githubusercontent.com/isXinLiu/MM-SafetyBench/'+dataset_revisions7['mm_source']+'/'+matches_pilot7[0],timeout=60)
    response_pilot7.raise_for_status()
    metadata_pilot7 = response_pilot7.json()
    eligible_pilot7 = sorted(uid for uid in tables_pilot7['Text_only'].index if scenario7+'|'+uid in seen_pilot7)
    for index_pilot7 in np.random.default_rng(SEED7).permutation(len(eligible_pilot7)):
        budget7()
        uid_pilot7 = eligible_pilot7[index_pilot7]
        row_pilot7 = tables_pilot7['Text_only'].loc[uid_pilot7]
        visual_pilot7 = tables_pilot7['TYPO'].loc[uid_pilot7]
        meta_pilot7 = metadata_pilot7.get(uid_pilot7)
        if not meta_pilot7 or norm7(meta_pilot7['Question'])!=norm7(row_pilot7['question']) or norm7(meta_pilot7['Rephrased Question'])!=norm7(visual_pilot7['question']):
            raise ValueError('Source question identity mismatch')
        raw_pilot7 = visual_pilot7['image']
        raw_pilot7 = raw_pilot7['bytes'] if isinstance(raw_pilot7,dict) else raw_pilot7
        image_pilot7 = raw_pilot7.convert('RGB') if isinstance(raw_pilot7,Image.Image) else Image.open(io.BytesIO(raw_pilot7)).convert('RGB')
        if norm7(meta_pilot7['Key Phrase']) not in norm7(pytesseract.image_to_string(image_pilot7)):
            continue
        ITEMS7.append(dict(uid=scenario7+'|'+uid_pilot7,benchmark='mm',cluster=scenario7,
            question=row_pilot7['question'],payload=meta_pilot7['Key Phrase'],wrapper=visual_pilot7['question'],
            image=image_pilot7,source_revision=dataset_revisions7['mm'],subset='development'))
        break
if len(ITEMS7)!=len(SCENARIOS7) or any(x['uid'] not in seen_pilot7 for x in ITEMS7):
    raise ValueError('Need exactly one verified previously seen item per scenario')
frozen7 = [dict(uid=x['uid'],benchmark=x['benchmark'],cluster=x['cluster'],subset=x['subset'],
    question_hash=digest7(norm7(x['question'])),payload_hash=digest7(x['payload']),
    image_hash=image_hash7(x['image']),source_revision=x['source_revision']) for x in ITEMS7]
DATAINFO7 = dict(source='previously_seen_mm_development_only',selected_count=len(ITEMS7),
    revisions=dataset_revisions7,planned_target_calls=4*len(ITEMS7),planned_guard_calls=6*len(ITEMS7),
    planned_keyword_calls=3*len(ITEMS7),scope='B/E/C and separate readback; greedy; incomplete wider panel')
freeze7 = dict(plan_sha256=PLAN_SHA256,items=frozen7,counts=DATAINFO7)
manifest_path7 = OUT7/'items_manifest_PRIVATE.json'
if manifest_path7.exists() and json.loads(manifest_path7.read_text())!=freeze7:
    raise ValueError('Pilot manifest changed; do not overwrite')
atomic7(manifest_path7,freeze7)
DATAHASH7 = digest7(frozen7)
NATURAL7 = None
print('Development pilot items:',len(ITEMS7),'| target calls:',4*len(ITEMS7),'| guard calls:',6*len(ITEMS7))
print('Previously seen items only; no reserved generations; no prompts or replies printed.')
'''


def sources():
    config = CONFIG.replace("MODE = 'smoke'", "MODE = 'development'")
    config = config.replace('MODEL_FILTER = []', 'MODEL_FILTER = '+repr([MODEL]))
    config = config.replace('SESSION_MINUTES = 30', 'SESSION_MINUTES = 60')
    config = config.replace('SCIENTIFIC_BUDGET_APPROVED = False', 'SCIENTIFIC_BUDGET_APPROVED = True')
    setup = SETUP.replace("/ MODE\n", "/ MODE / 'core8_qwen2_20261019'\n")
    generation = GENERATE.replace("small7 = MODE!='confirmatory' and", "small7 = False and")
    generation = generation.replace("# Separate read-back: response filtering is a sensitivity analysis only.",
        "specs7 = [s for s in specs7 if s['cond'] in ('B','E','C')]\n            # Separate read-back; remaining approved arms are deferred.")
    # Reserve the last 20 minutes for labels/export; all per-item generation stays checkpointed.
    generation = generation.replace('    try:\n        budget7()',
        '    try:\n        GENERATION_DEADLINE7 = min(DEADLINE7, START7+40*60)\n        budget7()')
    generation = generation.replace('                    budget7()\n',
        "                    budget7()\n                    if time.monotonic() >= GENERATION_DEADLINE7:\n                        raise TimeoutError('Pilot generation allocation reached')\n")
    return config, setup, DATA_PILOT, generation


def generate(output):
    build(output, [MODEL], 60)
    nb = json.loads(Path(output).read_text())
    for index, source in zip((2,8,14,17), sources()):
        nb['cells'][index]['source'] = source.replace('__PLAN_HASH__',
            __import__('hashlib').sha256((ROOT/'docs/ANALYSIS_PLAN_MODALITY_SAFETY.md').read_bytes()).hexdigest()).splitlines(True)
        ast.parse(''.join(nb['cells'][index]['source']))
    nb['cells'][0]['source'] = ['# Exploratory development pilot — audit follows collection\n\nPreviously seen MM-SafetyBench items; one Qwen2-VL-2B checkpoint; B/E/C and readback only. Maximum 32 target calls, 48 guard calls and 24 keyword checks. 256-token cap; 60-minute total budget checked between calls, including data/model loading, with at most 40 minutes allocated before the labelling stage. Loading or a single call may overrun a boundary. This is a partial development pilot, not the confirmatory eight-model study. Human audit will follow; reserved outcomes stay locked.\n']
    nb['cells'][26]['source'] = ['## Interpretation pending actual development outputs\n\nNo result is anticipated. Record actual condition and guard coverage, timing, truncation and failures; all guard-labelled estimates remain exploratory. Never treat non-refusal as harmfulness or an unparsed label as safe. Save code/outputs and a distinct aggregate snapshot before another stage.\n']
    Path(output).write_text(json.dumps(nb,ensure_ascii=False)+'\n')
    return nb


if __name__=='__main__':
    generate(ROOT/'notebooks/vlm_development_pilot.ipynb')
