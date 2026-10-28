"""Generate a self-contained repair appendix; preserves the original benchmark stage."""
import json
from pathlib import Path
import nbformat

ROOT=Path(__file__).resolve().parents[2]
DRIVER=r'''
import json,subprocess,sys,time,traceback
from pathlib import Path
base,root,deadline=Path(sys.argv[1]),Path(sys.argv[2]),float(sys.argv[3]);source=Path(__file__).parent
status={'stage':'amendment_12_repair','finished':False,'jobs':[]}
def save():
    temp=root/'driver_status.tmp';temp.write_text(json.dumps(status));temp.replace(root/'driver_status.json')
def job(mode,minutes,reserve=0):
    remaining=min(minutes*60,deadline-time.time()-reserve*60)
    if remaining<=0:return
    command=[sys.executable,'-u',str(source/'vlm_published_repair.py'),'--base',str(base),
             '--root',str(root),'--mode',mode,'--deadline',str(time.time()+remaining)]
    record={'mode':mode,'started':time.time()};status['jobs'].append(record);save()
    with (root/(mode+'_execution_PRIVATE.log')).open('w') as log:
        try:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=max(1,remaining))
            record['exit_code']=result.returncode
        except subprocess.TimeoutExpired:record['budget_stop']=True
    record['finished']=time.time();save()
try:
    job('prepare',2,reserve=45)
    job('smol',15,reserve=35)
    job('qwen',20,reserve=15)
    job('injection',8,reserve=10)
    # Only repair responses are judged; never repeat the old classifier evaluations.
    remaining=deadline-time.time()-60
    if remaining>0:
        record={'mode':'judge','started':time.time()};status['jobs'].append(record);save()
        with (root/'judge_execution_PRIVATE.log').open('w') as log:
            try:
                result=subprocess.run([sys.executable,'-u',str(source/'vlm_benchmark_judge.py'),
                    '--root',str(root),'--deadline',str(time.time()+remaining)],stdout=log,
                    stderr=subprocess.STDOUT,timeout=remaining)
                record['exit_code']=result.returncode
            except subprocess.TimeoutExpired:record['budget_stop']=True
        record['finished']=time.time();save()
except Exception as error:
    status['error_type']=type(error).__name__
    (root/'driver_error_PRIVATE.txt').write_text(traceback.format_exc())
finally:
    sys.path.insert(0,str(source))
    try:
        from vlm_published_repair import reconcile,preserve
        status['complete_cases']=reconcile(base,root)['total_completed']
        status['finished']=True;save()
        preserve(root)
    except Exception as error:
        status.update(finished=True,preservation_error=type(error).__name__);save()
        (root/'preservation_error_PRIVATE.txt').write_text(traceback.format_exc())
'''
LAUNCH=r'''
# Amendment 12. Owner authorized finishing missing cells; original stage is immutable.
import hashlib,json,subprocess,sys,time
from pathlib import Path
REPAIR_BASE=Path('/content/drive/MyDrive/VLM_Published_Benchmarks_20261026_PRIVATE')
REPAIR_ROOT=Path('/content/drive/MyDrive/VLM_Published_Repair_20261027_PRIVATE')
def launch_repair():
    if not REPAIR_BASE.is_dir():raise RuntimeError('Mount college Drive first')
    if not json.loads((REPAIR_BASE/'driver_status.json').read_text()).get('finished'):
        raise RuntimeError('Original stage is not finished')
    REPAIR_ROOT.mkdir(exist_ok=True)
    if (REPAIR_ROOT/'launch_PRIVATE.json').exists():
        print('Repair previously launched; use monitor. No duplicate or clock reset.');return
    import torch
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('Requested T4 required')
    contract=hashlib.sha256(json.dumps(REPAIR_SOURCES,sort_keys=True).encode()).hexdigest()
    clock=REPAIR_ROOT/'stage_clock_PRIVATE.json'
    if clock.exists():
        state=json.loads(clock.read_text())
        if state['contract']!=contract:raise ValueError('Repair sources differ from frozen contract')
    else:
        state=dict(started=time.time(),minutes=60,contract=contract)
        with clock.open('x') as handle:json.dump(state,handle)
    deadline=state['started']+3600
    if time.time()>=deadline:raise TimeoutError('Original repair allowance expired; no reset')
    source=REPAIR_ROOT/'source_PRIVATE';source.mkdir(exist_ok=True)
    for name,text in REPAIR_SOURCES.items():
        path=source/name
        if path.exists() and path.read_text()!=text:raise ValueError('Saved repair source changed')
        path.write_text(text)
    # Preserve a distinct aggregate snapshot without model responses or stimuli.
    snapshot=REPAIR_ROOT/'previous_safety_aggregates.json'
    if not snapshot.exists():snapshot.write_bytes((REPAIR_BASE/'safety_aggregates.json').read_bytes())
    with (REPAIR_ROOT/'installation_PRIVATE.log').open('w') as log:
        subprocess.run([sys.executable,'-m','pip','install','--quiet','transformers==4.57.1',
            'accelerate==1.11.0','bitsandbytes==0.48.1','sentencepiece'],check=True,
            stdout=log,stderr=subprocess.STDOUT,timeout=max(1,int(deadline-time.time())))
    with (REPAIR_ROOT/'launch_PRIVATE.json').open('x') as handle:
        json.dump(dict(contract=contract,started=time.time()),handle)
    with (REPAIR_ROOT/'driver_execution_PRIVATE.log').open('w') as log:
        process=subprocess.Popen([sys.executable,'-u',str(source/'repair_driver.py'),
            str(REPAIR_BASE),str(REPAIR_ROOT),str(deadline)],stdout=log,stderr=subprocess.STDOUT)
    print(dict(stage='published_data_repair',pid=process.pid,contract=contract,
        deadline_utc=__import__('datetime').datetime.fromtimestamp(deadline,__import__('datetime').timezone.utc).isoformat()))
launch_repair()
'''
MONITOR=r'''
import json,time
from pathlib import Path
REPAIR_ROOT=Path('/content/drive/MyDrive/VLM_Published_Repair_20261027_PRIVATE')
for name in ('driver_status.json','smol_PRIVATE/status.json','qwen_PRIVATE/status.json',
             'qwen_injection_PRIVATE/aggregate.json','judge_status.json','numerics_v2_status.json',
             'numerics_v2_PRIVATE/qwen_PRIVATE/status.json',
             'numerics_v2_PRIVATE/qwen_injection_PRIVATE/aggregate.json',
             'numerics_v2_PRIVATE/judge_status.json'):
    path=REPAIR_ROOT/name
    if path.exists():
        value=json.loads(path.read_text())
        print(name,{k:v for k,v in value.items() if k in ('status','finished','methods','conditions',
            'completed','failed','error_type','jobs','complete_cases','preservation_error','weights_unchanged')})
    else:print(name,'not yet available')
path=REPAIR_ROOT/'coverage_aggregates.json'
if path.exists():
    value=json.loads(path.read_text());print('coverage',value['counts'],'total',value['total_completed'],'planned',144)
path=REPAIR_ROOT/'stage_clock_PRIVATE.json'
if path.exists():print('remaining_minutes',max(0,(json.loads(path.read_text())['started']+3600-time.time())/60))
'''


MONITOR+=r'''
for name in ('scoring_recovery_status.json','judge_status.json'):
    path=REPAIR_ROOT/name
    if path.exists():print(name,json.loads(path.read_text()))
path=REPAIR_ROOT/'combined_PRIVATE/safety_aggregates.json'
if path.exists():
    from IPython.display import display,Markdown
    rows=json.loads(path.read_text())['rows']
    table=['| Model | Method | Condition | Yes / planned | Unresolved |',
           '|---|---|---|---:|---:|']
    for row in rows:
        if row['condition'] in ('clean','attack','defended_attack'):
            table.append('| '+row['model']+' | '+row['method']+' | '+row['condition']+
                         ' | '+str(row['yes'])+'/8 | '+str(row['unresolved'])+' |')
    display(Markdown('\n'.join(table)))
'''


def build():
    names=('vlm_visual_attacks.py','vlm_visual_adapter.py','vlm_visual_smol_adapter.py',
           'vlm_published_benchmarks.py','vlm_benchmark_judge.py','vlm_published_repair.py')
    sources={name:(ROOT/'tools'/name).read_text() for name in names}
    sources['repair_driver.py']=DRIVER
    sources['PUBLISHED_BENCHMARK_PROTOCOL.md']=(ROOT/'docs/PUBLISHED_BENCHMARK_PROTOCOL.md').read_text()
    sources['ANALYSIS_PLAN_MODALITY_SAFETY.md']=(ROOT/'docs/ANALYSIS_PLAN_MODALITY_SAFETY.md').read_text()
    heading='# Published-data repair — Amendment 12\n\n27 October 2026. Finish missing cases only; '
    heading+='separate 60-minute clock. Original notebook/output archive is preserved. '
    heading+='No synthetic base data, manufactured labels, parity-tolerance relaxation or training. '
    heading+='Qwen repaired attention arithmetic is a distinct numerical adaptation, with paired controls. '
    heading+='Feature/teacher/BAP original-paper implementations and human review remain open.'
    cells=[nbformat.v4.new_markdown_cell(heading),
           nbformat.v4.new_code_cell('REPAIR_SOURCES = '+repr(sources)+'\n'+LAUNCH),
           nbformat.v4.new_markdown_cell('The launch cell starts at most one bounded driver. '
               'Completion must be checked from files below; a process ID is not a result.'),
           nbformat.v4.new_code_cell(MONITOR),
           nbformat.v4.new_markdown_cell('Editable interpretation: record remaining gaps, '
               'stage/precision deviations, ASR denominators and the private archive checksum.')]
    n=nbformat.v4.new_notebook(cells=cells,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3')))
    path=ROOT/'notebooks/vlm_published_repair_20261027.ipynb'
    path.write_text(json.dumps(n,ensure_ascii=False,separators=(',',':')))
    print(path)


if __name__=='__main__':build()
