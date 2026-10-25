"""Build a dated unified notebook for the owner-authorized benign T4 profile."""
import argparse
import ast
from pathlib import Path

import nbformat
from make_research_unified_nb import build

ROOT = Path(__file__).resolve().parents[2]

PREPARE = '''
# Owner authorized an actual T4 run on 2026-10-25. This is benign engineering only.
import time, json, subprocess, sys, hashlib
from pathlib import Path
PROFILE_ROOT = Path('/content/visual_T4_20261025_PRIVATE')
PROFILE_ROOT.mkdir(parents=True, exist_ok=True)
profile_clock = PROFILE_ROOT/'profile_clock_PRIVATE.json'
profile_started = time.time()
if profile_clock.exists():
    profile_started = json.loads(profile_clock.read_text())['started']
else:
    profile_clock.write_text(json.dumps(dict(started=profile_started, minutes=30)))
profile_deadline = profile_started + 30*60
if time.time() >= profile_deadline:
    raise TimeoutError('Original benign GPU profile expired; preserve partial artifacts')
import torch
if not torch.cuda.is_available():
    raise RuntimeError('Connect the selected T4 GPU runtime first')
profile_gpu = torch.cuda.get_device_name(0)
if 'T4' not in profile_gpu:
    raise RuntimeError('Only the requested T4 scope is authorized by this profile')
print('Actual GPU:', profile_gpu, '| total GB:', torch.cuda.get_device_properties(0).total_memory/1e9)
subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet',
    'transformers==4.57.1', 'Pillow==11.3.0'], check=True,
    timeout=max(1,int(profile_deadline-time.time())))
print('Reviewed dependencies installed; timer includes installation and model loading.')
'''

RUN = '''
from PIL import Image, ImageDraw
from dataclasses import asdict
import shutil
if time.time() >= profile_deadline:
    raise TimeoutError('Deadline before profile')
status_path = PROFILE_ROOT/'profile_aggregate_status.json'
if status_path.exists():
    print(json.loads(status_path.read_text()))
    print('Saved profile found; no repeat model load or failed-identity retry.')
else:
    image_path = PROFILE_ROOT/'synthetic_PRIVATE.png'
    image = Image.new('RGB',(224,224),'white')
    ImageDraw.Draw(image).rectangle((48,48,176,176),fill=(210,35,35))
    image.save(image_path)
    profile_rows = [dict(id='synthetic_color_01', image=str(image_path),
        image_sha256=hashlib.sha256(image_path.read_bytes()).hexdigest(),
        prompt='What color is the square? Answer with one color word.', target='blue',
        split='development', intent_group='synthetic_color', image_group='synthetic_square',
        track='perception', provenance='Locally generated geometric image; no benchmark data')]
    visual_core.atomic_json(PROFILE_ROOT/'manifest_PRIVATE.json',profile_rows)
    profile_config = visual_core.AttackConfig(method='pgd',steps=3,epsilon=8/255,alpha=2/255)
    profile_contract = dict(kind='benign_engineering_only',date='2026-10-25',
        source_hashes=SOURCE_HASHES,model=visual_adapter.QwenAttackAdapter.MODEL,
        revision=visual_adapter.QwenAttackAdapter.REVISION,attack=asdict(profile_config),
        max_new_tokens=32,canvas=224,minutes=30,manifest_hash=visual_core.digest(profile_rows))
    profile_adapter = None
    profile_status = dict(status='starting',scientific_result=False,gpu=profile_gpu)
    visual_core.atomic_json(status_path,profile_status)
    try:
        print(visual_tests.run_architecture_check(visual_adapter))
        if time.time() >= profile_deadline:
            raise TimeoutError('Deadline before pretrained model load')
        load_begin = time.monotonic()
        torch.cuda.reset_peak_memory_stats()
        profile_adapter = visual_adapter.QwenAttackAdapter(max_new=32)
        profile_status['model_load_seconds'] = time.monotonic()-load_begin
        profile_status['loaded_peak_gb'] = torch.cuda.max_memory_allocated()/1e9
        print('Pinned pretrained VLM loaded. Beginning parity, input gradients and three PGD steps.')
        result = visual_core.run_private(profile_adapter,profile_rows,profile_config,
            PROFILE_ROOT,profile_contract,profile_deadline)
        profile_status.update(status='complete' if result['completed']==1 else 'failed',counts=result)
        records = [json.loads(p.read_text()) for p in PROFILE_ROOT.glob('*_PRIVATE.json')]
        finished = [r for r in records if isinstance(r,dict) and r.get('status')=='complete' and 'metrics' in r]
        if finished:
            record = finished[0]
            profile_status.update(parity=record['parity'],delivered_linf=record['delivered_linf'],
                baseline_objective=record['metrics']['baseline_objective'],
                best_objective=record['metrics']['best_objective'],
                optimization_steps=len(record['metrics']['trace']),
                case_seconds=record['elapsed_seconds'],
                max_generation_peak_gb=max(v['peak_allocated_gb'] for v in record['responses'].values()))
        failures = [r['error_type'] for r in records if isinstance(r,dict) and r.get('status')=='failed']
        if failures:
            profile_status['error_types'] = failures
    except Exception as error:
        profile_status.update(status='failed',error_type=type(error).__name__)
        print('Profile stopped:',type(error).__name__)
    finally:
        profile_status['elapsed_wall_seconds'] = time.time()-profile_started
        visual_core.atomic_json(status_path,profile_status)
        if profile_adapter is not None:
            profile_adapter.close()
    print(profile_status)  # Aggregates only, not model responses.
    shutil.make_archive(str(PROFILE_ROOT),'zip',PROFILE_ROOT)
print('Private artifact archive:',str(PROFILE_ROOT)+'.zip')
print('This one synthetic perception case does not measure safety or jailbreak success.')
'''

DOWNLOAD = '''
from google.colab import files
# Keep the private archive and completed notebook before changing any run settings.
files.download(str(PROFILE_ROOT)+'.zip')
'''

MONITOR = '''
# This cell reads progress; it never repeats the model run.
print('Process exit:',profile_process.poll() if 'profile_process' in globals() else 'not launched here')
if (child_root/'execution_PRIVATE.log').exists():
    print((child_root/'execution_PRIVATE.log').read_text()[-3500:])
if (child_root/'profile_aggregate_status.json').exists():
    print(json.loads((child_root/'profile_aggregate_status.json').read_text()))
'''

ISOLATED = '''
# A fresh process isolates newly installed libraries without restarting this runtime.
import subprocess, sys, json, time
from pathlib import Path
if time.time() >= profile_deadline:
    raise TimeoutError('Original profile deadline expired')
child_root = Path('/content/visual_T4_20261025_PRIVATE/fresh_process_PRIVATE')
child_root.mkdir(parents=True,exist_ok=True)
child_script = child_root/'profile_runner_PRIVATE.py'
child_lines = ['import sys, types, time, json, hashlib, torch', 'from pathlib import Path']
for name, source in [('visual_core',visual_core_SOURCE),('visual_adapter',visual_adapter_SOURCE),
                     ('visual_tests',visual_tests_SOURCE)]:
    child_lines += [f'{name} = types.ModuleType({name!r})',f'sys.modules[{name!r}] = {name}',
                   f'exec(compile({source!r},{name!r},"exec"),{name}.__dict__)']
child_lines += [f'SOURCE_HASHES = {SOURCE_HASHES!r}',f'PROFILE_ROOT = Path({str(child_root)!r})',
                f'profile_deadline = {profile_deadline!r}',f'profile_started = {profile_started!r}',
                "profile_gpu = torch.cuda.get_device_name(0)", PROFILE_RUN_SOURCE]
child_script.write_text('\\n'.join(child_lines))
if (child_root/'profile_aggregate_status.json').exists():
    print('Existing attempt preserved; no automatic retry.')
else:
    profile_log = (child_root/'execution_PRIVATE.log').open('w')
    profile_process = subprocess.Popen([sys.executable,'-u',str(child_script)],
        stdout=profile_log,stderr=subprocess.STDOUT)
    print('Targeted GPU process started:',profile_process.pid,'| original deadline retained')
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    notebook = nbformat.from_dict(build(args.output,False))
    notebook.cells.append(nbformat.v4.new_markdown_cell('''## Owner-authorized T4 feasibility run — 25 October

One generated red square, harmless color question, fixed target "blue", three PGD
steps, raw epsilon 8/255, 32 output tokens, one pinned Qwen2.5-VL-3B, thirty wall
minutes including install/download/load. This tests real model mechanics and memory;
it is not a benchmark or a safety experiment. Earlier scientific gates stay locked.
Private outputs remain in this runtime and a downloadable archive. Download and
save them with this completed notebook; runtime storage alone is not a durable archive.
No Drive permissions, paid purchase or model training is needed.'''))
    notebook.cells.append(nbformat.v4.new_code_cell('PROFILE_RUN_SOURCE = '+repr(RUN)))
    for source in (PREPARE,ISOLATED,MONITOR):
        ast.parse(source)
        notebook.cells.append(nbformat.v4.new_code_cell(source))
    notebook.cells.append(nbformat.v4.new_markdown_cell('''### GPU readout — editable

Read the saved profile status. Report the actual GPU, load/elapsed time, parity,
gradient/optimization failures, delivered budget and objective change. Even lower
target NLL does not imply the generated answer changed. Interpret only this synthetic
engineering case; do not call it a completed attack benchmark or novel result.'''))
    for index,cell in enumerate(notebook.cells):
        cell.id=f'unified-{index:03d}'
    notebook.metadata.update(accelerator='GPU',colab=dict(provenance=[],gpuType='T4'))
    nbformat.validate(notebook)
    nbformat.write(notebook,args.output)
    print('Prepared bounded GPU notebook:',args.output)


if __name__=='__main__':
    main()
