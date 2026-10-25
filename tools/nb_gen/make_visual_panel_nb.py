"""Generate a standalone bounded visual-panel appendix for the unified Colab notebook."""
import argparse
from pathlib import Path

import nbformat

ROOT=Path(__file__).resolve().parents[2]

DRIVER='''
import json,subprocess,sys,time
from pathlib import Path
root=Path(sys.argv[1]); deadline=float(sys.argv[2]); source=Path(__file__).parent
status={'stage':'synthetic_development','models':{}}
for model in ('qwen','smol'):
    if time.time()>=deadline:
        status['stopped_at_deadline']=True;break
    with (root/(model+'_execution_PRIVATE.log')).open('w') as handle:
        try:
            result=subprocess.run([sys.executable,'-u',str(source/'vlm_visual_panel.py'),
                '--root',str(root),'--model',model,'--deadline',str(deadline)],stdout=handle,
                stderr=subprocess.STDOUT,timeout=max(1,int(deadline-time.time())))
            status['models'][model]={'exit_code':result.returncode}
        except subprocess.TimeoutExpired:
            status['models'][model]={'status':'deadline'}
    (root/'driver_status.json').write_text(json.dumps(status))
result=subprocess.run([sys.executable,str(source/'vlm_visual_panel.py'),'--root',str(root),'--summarize'],
    capture_output=True,text=True,timeout=180)
(root/'summary_execution_PRIVATE.log').write_text(result.stdout+result.stderr)
status['summary_exit_code']=result.returncode
status['finished']=True
(root/'driver_status.json').write_text(json.dumps(status))
print(status)
'''

LAUNCH='''
# Owner authorized broader development on 2026-10-25. Do not rerun completed identities.
import hashlib,json,time,sys,subprocess,importlib.metadata
from pathlib import Path
import torch
if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
    raise RuntimeError('Use the requested T4 runtime')
if importlib.metadata.version('transformers')!='4.57.1':
    raise RuntimeError('Install reviewed Transformers 4.57.1 before this stage')
PANEL_ROOT=Path('/content/visual_panel_20261025_PRIVATE')
PANEL_ROOT.mkdir(exist_ok=True)
panel_contract=hashlib.sha256(json.dumps(PANEL_SOURCES,sort_keys=True).encode()).hexdigest()
panel_clock=PANEL_ROOT/'stage_clock_PRIVATE.json'
if panel_clock.exists():
    panel_state=json.loads(panel_clock.read_text())
    if panel_state['contract']!=panel_contract:
        raise ValueError('Existing stage has different source identity')
else:
    panel_state=dict(contract=panel_contract,started=time.time(),minutes=120)
    with panel_clock.open('x') as handle: json.dump(panel_state,handle)
panel_deadline=panel_state['started']+120*60
if time.time()>=panel_deadline: raise TimeoutError('Original stage deadline expired')
panel_source_dir=PANEL_ROOT/'source_PRIVATE';panel_source_dir.mkdir(exist_ok=True)
for filename,source in PANEL_SOURCES.items():
    destination=panel_source_dir/filename
    if destination.exists() and destination.read_text()!=source:
        raise ValueError('Existing source changed')
    destination.write_text(source)
panel_launch=PANEL_ROOT/'launch_PRIVATE.json'
if panel_launch.exists():
    print('Stage already launched. Use monitor; no duplicate process.')
else:
    with panel_launch.open('x') as handle:json.dump(dict(contract=panel_contract,time=time.time()),handle)
    panel_log=(PANEL_ROOT/'driver_execution_PRIVATE.log').open('w')
    panel_process=subprocess.Popen([sys.executable,'-u',str(panel_source_dir/'panel_driver.py'),
        str(PANEL_ROOT),str(panel_deadline)],stdout=panel_log,stderr=subprocess.STDOUT)
    print('Broader panel launched on',torch.cuda.get_device_name(0),'| driver pid:',panel_process.pid)
print('Stage contract:',panel_contract)
'''

MONITOR='''
print('Process exit:',panel_process.poll() if 'panel_process' in globals() else 'see saved status')
for filename in ('driver_status.json','qwen/model_status.json','smol/model_status.json','review_status.json'):
    path=PANEL_ROOT/filename
    if path.exists(): print(filename,json.loads(path.read_text()))
for model in ('qwen','smol'):
    log=PANEL_ROOT/(model+'_execution_PRIVATE.log')
    if log.exists(): print(model,'log tail:',log.read_text()[-1200:])
'''

EXPORT='''
# Run only after driver_status.finished; preserve actual code, outputs and distinct aggregates.
import shutil
from IPython.display import display,Markdown
state=json.loads((PANEL_ROOT/'driver_status.json').read_text())
if not state.get('finished'):raise RuntimeError('Panel is still running')
archive=Path('/content/visual_panel_20261025_COMPLETE_PRIVATE.zip')
if not archive.exists():
    shutil.make_archive(str(archive.with_suffix('')),'zip',PANEL_ROOT)
archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
drive_root=Path('/content/drive/MyDrive')
if not drive_root.is_dir():raise RuntimeError('Owner must connect college Drive before private preservation')
destination=drive_root/'VLM_Visual_Attacks_20261025_PRIVATE'/('panel_'+panel_contract[:12])
destination.mkdir(parents=True,exist_ok=True)
for original in (archive,PANEL_ROOT/'panel_aggregates.json',PANEL_ROOT/'driver_status.json',PANEL_ROOT/'review_status.json'):
    copy=destination/original.name
    expected=hashlib.sha256(original.read_bytes()).hexdigest()
    if copy.exists() and hashlib.sha256(copy.read_bytes()).hexdigest()!=expected:
        raise ValueError('Refuse to overwrite a different saved artifact')
    if not copy.exists():shutil.copyfile(original,copy)
    if hashlib.sha256(copy.read_bytes()).hexdigest()!=expected:raise ValueError('Drive copy checksum failed')
(PANEL_ROOT/'preserved_drive_PRIVATE.json').write_text(json.dumps(dict(archive=str(destination/archive.name),sha256=archive_hash)))
print('Private archive and distinct numeric snapshots verified in college Drive:',str(destination))
print('DRIVER_STATUS_JSON',json.dumps(state))
if (PANEL_ROOT/'panel_aggregates.json').exists():
    aggregate=json.loads((PANEL_ROOT/'panel_aggregates.json').read_text())
    print('Completed records:',len(aggregate['cases']))
display(Markdown('**Interpretation:** these are synthetic development cases and adaptations, not safety benchmark scores or verified novelty. Review packets are unlabelled. Keep public exports aggregate-only; preserve the private archive.'))
'''

EXTERNAL_DRIVER='''
import json,subprocess,sys,time
from pathlib import Path
root=Path(sys.argv[1]);deadline=float(sys.argv[2]);source=Path(__file__).parent
status={'stage':'external_injection_only','models':{}}
for model in ('qwen','smol'):
    if time.time()>=deadline:break
    with (root/(model+'_log_PRIVATE.txt')).open('w') as handle:
        try:
            result=subprocess.run([sys.executable,'-u',str(source/'vlm_visual_panel.py'),
                '--external-injection','--root',str(root),'--model',model,'--deadline',str(deadline)],
                stdout=handle,stderr=subprocess.STDOUT,timeout=max(1,int(deadline-time.time())))
            status['models'][model]={'exit_code':result.returncode}
        except subprocess.TimeoutExpired:status['models'][model]={'status':'deadline'}
    (root/'driver_status.json').write_text(json.dumps(status))
(root/'review_generation_PRIVATE.log').write_text(subprocess.run([sys.executable,
    str(source/'vlm_visual_panel.py'),'--external-review','--root',str(root)],
    capture_output=True,text=True,timeout=120).stdout)
status['finished']=True
(root/'driver_status.json').write_text(json.dumps(status))
print(status)
'''

EXTERNAL_LAUNCH='''
# Run after the synthetic stage has finished and been archived. No optimization on source test data.
import json,time,hashlib,subprocess,sys
from pathlib import Path
previous=json.loads((PANEL_ROOT/'driver_status.json').read_text())
if not previous.get('finished'):raise RuntimeError('Wait for synthetic panel completion')
preservation=json.loads((PANEL_ROOT/'preserved_drive_PRIVATE.json').read_text())
if hashlib.sha256(Path(preservation['archive']).read_bytes()).hexdigest()!=preservation['sha256']:
    raise ValueError('Completed private archive must be verified on Drive before this stage')
EXTERNAL_ROOT=Path('/content/visual_external_20261025_PRIVATE');EXTERNAL_ROOT.mkdir(exist_ok=True)
external_contract=hashlib.sha256(json.dumps(EXTERNAL_SOURCES,sort_keys=True).encode()).hexdigest()
clock=EXTERNAL_ROOT/'clock_PRIVATE.json'
if clock.exists():
    external_state=json.loads(clock.read_text())
    if external_state['contract']!=external_contract:raise ValueError('External scope changed')
else:
    external_state=dict(contract=external_contract,deadline=min(panel_deadline,time.time()+20*60))
    with clock.open('x') as handle:json.dump(external_state,handle)
if time.time()>=external_state['deadline']:raise TimeoutError('Original budget expired')
external_source=EXTERNAL_ROOT/'source_PRIVATE';external_source.mkdir(exist_ok=True)
for filename,source in EXTERNAL_SOURCES.items():
    path=external_source/filename
    if path.exists() and path.read_text()!=source:raise ValueError('External source changed')
    path.write_text(source)
launch=EXTERNAL_ROOT/'launch_PRIVATE.json'
if launch.exists():print('External stage already launched; monitor only')
else:
    with launch.open('x') as handle:json.dump(external_state,handle)
    external_log=(EXTERNAL_ROOT/'driver_log_PRIVATE.txt').open('w')
    external_process=subprocess.Popen([sys.executable,'-u',str(external_source/'external_driver.py'),
        str(EXTERNAL_ROOT),str(external_state['deadline'])],stdout=external_log,stderr=subprocess.STDOUT)
    print('Frozen external diagnostic launched:',external_process.pid)
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--external',action='store_true')
    args=parser.parse_args()
    paths=['tools/vlm_visual_attacks.py','tools/vlm_visual_adapter.py',
           'tools/vlm_visual_smol_adapter.py','tools/vlm_visual_panel.py']
    sources={Path(p).name:(ROOT/p).read_text() for p in paths}
    sources['external_driver.py' if args.external else 'panel_driver.py']=EXTERNAL_DRIVER if args.external else DRIVER
    sources['analysis_plan_snapshot.md']=(ROOT/'docs/ANALYSIS_PLAN_MODALITY_SAFETY.md').read_text()
    cells=[nbformat.v4.new_markdown_cell('''# Broader visual panel — Amendment 9

Two architectures, ten mechanisms, static-prefix comparisons, defense-aware PGD,
flip-pair EOT with a flip defense and directional Qwen-to-Smol artifact transfer.
Four synthetic development tasks, four separate optimization contexts, common 448-square
delivered canvas. One model per process, 120 T4 wall minutes total. No training.
FP16 Qwen versus FP32 Smol are explicit deployment settings, not a causal architecture comparison.
Model/processor/code hashes and actual stimulus images are retained privately. Universal
modes use one development carrier; faithful original-paper reproduction is not claimed.

Run the **source** and **launch** cells once; rerun **monitor** to inspect progress.
Run **export** after finished. The last stage's completed notebook must already be saved.
The panel produces an unlabelled two-reviewer packet; it cannot perform human validation.''')]
    cells.append(nbformat.v4.new_code_cell(('EXTERNAL_SOURCES' if args.external else 'PANEL_SOURCES')+' = '+repr(sources)))
    for source in ((EXTERNAL_LAUNCH,) if args.external else (LAUNCH,MONITOR,EXPORT)):
        cells.append(nbformat.v4.new_code_cell(source))
        cells.append(nbformat.v4.new_markdown_cell('### Readout — editable\n\nRecord completed/failed/stopped coverage, clean accuracy and exact-target changes. Loss changes are not safety outcomes. Preserve failures and architecture/precision differences; do not pool synthetic cases with historical or held-out evidence.'))
    notebook=nbformat.v4.new_notebook(cells=cells,metadata=dict(
        kernelspec=dict(display_name='Python 3',language='python',name='python3'),
        accelerator='GPU',colab=dict(provenance=[],gpuType='T4')))
    nbformat.validate(notebook)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    nbformat.write(notebook,args.output)
    print('Generated bounded panel appendix:',args.output)


if __name__=='__main__':
    main()
