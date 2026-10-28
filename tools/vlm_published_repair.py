"""Amendment 12: fill only frozen missing cells; never mutate the original stage.

Real released inputs only. Numerical Qwen adaptations remain visible per record.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

import torch
import vlm_published_benchmarks as bench
from vlm_visual_attacks import atomic_json
from vlm_visual_adapter import QwenAttackAdapter


class StableQwenAdapter(QwenAttackAdapter):
    """Frozen FP16 weights, FP32 attention arithmetic, reference-exact CPU processor."""
    def __init__(self,*args,**kwargs):
        import vlm_visual_adapter as adapter_module
        import transformers.models.qwen2_5_vl.modeling_qwen2_5_vl as modeling
        original_patchify=adapter_module.patchify
        original_attention=modeling.eager_attention_forward
        def cpu_patchify(image,processor):
            return original_patchify(image.to('cpu'),processor).to(image.device)
        def attention(module,query,key,value,attention_mask,scaling,dropout=0.,**kw):
            dtype=query.dtype
            output,weights=original_attention(module,query.float(),key.float(),value.float(),
                None if attention_mask is None else attention_mask.float(),scaling,dropout=dropout,**kw)
            return output.to(dtype),weights
        adapter_module.patchify=cpu_patchify
        modeling.eager_attention_forward=attention
        self._original_patchify=original_patchify
        self._original_attention=original_attention
        self._modeling=modeling
        super().__init__(*args,**kwargs)
        self.identity.update(attention='eager_fp32_qkv_arithmetic',
                             preprocessing='differentiable_cpu_reference_arithmetic',
                             input_pixels='cpu_uint8_float32_div255_then_transfer_v2')

    def read_image(self,path):
        import numpy as np
        from PIL import Image
        image=Image.open(path).convert('RGB')
        if image.size!=(self.canvas,self.canvas):
            image=image.resize((self.canvas,self.canvas),Image.Resampling.BICUBIC)
        # Match published uint8 -> float32 rescaling on CPU BEFORE GPU transfer.
        # The raw-pixel budget is unchanged; GPU scalar division can round differently.
        value=torch.from_numpy(np.array(image,copy=True)).permute(2,0,1)[None].float()/255
        return value.to(self.device)

    def parity_check(self,image,prompt,target):
        import numpy as np
        from PIL import Image
        import vlm_visual_adapter as adapter_module
        pil=Image.fromarray((image[0].detach().cpu().permute(1,2,0).numpy()*255).round().astype(np.uint8))
        native=self.processor.image_processor(images=[pil],return_tensors='pt')['pixel_values']
        ours=adapter_module.patchify(image,self.processor.image_processor)
        if not torch.equal(ours.half().cpu(),native.half()):
            raise ValueError('Delivered FP16 processor tensors are not exactly reference-equal')
        result=super().parity_check(image,prompt,target)
        result['delivered_fp16_processor_exact']=True
        return result

    def close(self):
        import vlm_visual_adapter as adapter_module
        super().close()
        adapter_module.patchify=self._original_patchify
        self._modeling.eager_attention_forward=self._original_attention


def prepare_repair(base,root):
    base,root=Path(base),Path(root)
    if 'PRIVATE' not in str(root):raise ValueError('Private output root required')
    prior=json.loads((base/'driver_status.json').read_text())
    if not prior.get('finished'):raise ValueError('Original stage must be finished')
    root.mkdir(exist_ok=True,parents=True)
    for folder in ('sources_PRIVATE','injection_sources_PRIVATE'):
        if not (root/folder).exists():shutil.copytree(base/folder,root/folder)
    manifest=bench.prepare(root)
    original=json.loads((base/'manifest_PRIVATE.json').read_text())
    if manifest['safety']!=original['safety'] or manifest['optimization']!=original['optimization']:
        raise ValueError('Repair changed source selection')
    selection={}
    for model,methods in (('smol',('pgd_flip','released_qi_16')),('qwen',('universal_eot',))):
        selection[model]={}
        for method in methods:
            missing=[]
            for row in manifest['safety']:
                path=base/(model+'_PRIVATE')/(method+'__'+row['id']+'_case_PRIVATE.json')
                if not path.exists() or json.loads(path.read_text()).get('status')!='complete':missing.append(row['id'])
            if missing:selection[model][method]=missing
    path=root/'selection_PRIVATE.json'
    frozen=dict(base_manifest_sha256=bench.sha(base/'manifest_PRIVATE.json'),selection=selection,
                qwen_numerical_adaptation='FP16 weights; FP32 attention; differentiable CPU normalization',
                new_synthetic_data=False)
    if path.exists() and json.loads(path.read_text())!=frozen:raise ValueError('Repair selection changed')
    atomic_json(path,frozen)
    return selection


def reconcile(base,root,extra=None):
    """Private combined view; original complete cases win, repaired missing cells retain origin."""
    from vlm_benchmark_judge import summarize
    base,root=Path(base),Path(root);extra=Path(extra) if extra else None
    combined=root/'combined_PRIVATE';combined.mkdir(exist_ok=True)
    stages=[('original',base),('repair',root)]+([('qwen_numerics_v2',extra)] if extra else [])
    counts={};ledger=[]
    for model in ('smol','qwen'):
        dest=combined/(model+'_PRIVATE');dest.mkdir(exist_ok=True)
        for stage,source in stages:
            for path in (source/(model+'_PRIVATE')).glob('*_case_PRIVATE.json'):
                record=json.loads(path.read_text());out=dest/path.name
                if out.exists() and json.loads(out.read_text()).get('status')=='complete':continue
                if record.get('status')!='complete':continue
                record['source_stage']=stage
                record['source_case_sha256']=bench.sha(path)
                atomic_json(out,record)
        cases=[json.loads(p.read_text()) for p in dest.glob('*_case_PRIVATE.json')]
        counts[model]={method:sum(c['method']==method for c in cases) for method in bench.METHODS}
        for method in bench.METHODS:
            rows=[c for c in cases if c['method']==method]
            ledger.append(dict(model=model,method=method,complete=len(rows),planned=8,
                original=sum(c['source_stage']=='original' for c in rows),repair=sum(c['source_stage']!='original' for c in rows),
                qwen_repair_precision_change=model=='qwen' and any(c['source_stage']!='original' for c in rows)))
    labels=combined/'labels_PRIVATE';labels.mkdir(exist_ok=True)
    for stage,source in stages:
        for path in (source/'labels_PRIVATE').glob('*_PRIVATE.json'):
            out=labels/path.name
            if out.exists() and out.read_bytes()!=path.read_bytes():raise ValueError('Conflicting judge identity')
            if not out.exists():shutil.copyfile(path,out)
    summarize(combined)
    injection={}
    for model in ('smol','qwen'):
        source=base if model=='smol' else (extra or root)
        path=source/(model+'_injection_PRIVATE')/'aggregate.json'
        injection[model]=json.loads(path.read_text()) if path.exists() else dict(status='missing')
    status=dict(coverage=ledger,counts=counts,total_completed=sum(sum(c.values()) for c in counts.values()),
                planned_cases=144,injection=injection,evidence='development_not_human_validated',
                pooling_warning='Qwen repair uses FP32 attention arithmetic; compare paired controls within that configuration.')
    atomic_json(root/'coverage_aggregates.json',status)
    return status


def preserve(root):
    root=Path(root)
    archive=Path(shutil.make_archive(str(root)+'_FINISHED_PRIVATE','zip',root))
    h=hashlib.sha256()
    with archive.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):h.update(chunk)
    result=dict(archive=str(archive),bytes=archive.stat().st_size,sha256=h.hexdigest())
    atomic_json(root.parent/(root.name+'_preservation_PRIVATE.json'),result)
    return result



def followup(base,root,deadline):
    """Wait for immutable v1 jobs, then use a separate v2 source/output namespace."""
    base,root=Path(base),Path(root);extra=root/'numerics_v2_PRIVATE'
    status=dict(stage='qwen_numerical_followup',finished=False,jobs=[])
    output=root/'numerics_v2_status.json'
    atomic_json(output,status)
    # The original driver/judge owns the GPU until it has finished. No concurrent models.
    while not json.loads((root/'driver_status.json').read_text()).get('finished'):
        bench.check(deadline-60);time.sleep(5)
    previous=root.parent/(root.name+'_FINISHED_PRIVATE.zip')
    while not (root.parent/(root.name+'_preservation_PRIVATE.json')).exists():
        bench.check(deadline-60);time.sleep(5)
    before=root.parent/(root.name+'_BEFORE_NUMERICS_V2_PRIVATE.zip')
    if previous.exists() and not before.exists():shutil.copyfile(previous,before)
    previous_meta=root.parent/(root.name+'_preservation_PRIVATE.json')
    before_meta=root.parent/(root.name+'_BEFORE_NUMERICS_V2_preservation_PRIVATE.json')
    if not before_meta.exists():shutil.copyfile(previous_meta,before_meta)
    prepare_repair(base,extra)
    atomic_json(extra/'source_identity_PRIVATE.json',dict(source_sha256=bench.sha(__file__),
        parent_clock_sha256=bench.sha(root/'stage_clock_PRIVATE.json'),
        reason='Actual source image: CPU scaling zero mismatches; GPU scaling 4834',
        parent_deadline=deadline,clock_reset=False))
    source=Path(__file__).parent
    for mode,minutes,reserve in (('qwen',20,10),('injection',8,8),('judge',60,1)):
        available=min(minutes*60,deadline-time.time()-reserve*60)
        if available<=0:
            status['jobs'].append(dict(mode=mode,status='insufficient_original_budget'));continue
        if mode=='judge':
            command=[sys.executable,'-u',str(source/'vlm_benchmark_judge.py'),
                     '--root',str(extra),'--deadline',str(time.time()+available)]
        else:
            command=[sys.executable,'-u',str(source/'vlm_published_repair.py'),'--base',str(base),
                     '--root',str(extra),'--mode',mode,'--deadline',str(time.time()+available)]
        entry=dict(mode=mode,started=time.time());status['jobs'].append(entry);atomic_json(output,status)
        with (extra/(mode+'_execution_PRIVATE.log')).open('w') as log:
            try:
                run=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=available)
                entry['exit_code']=run.returncode
            except subprocess.TimeoutExpired:entry['budget_stop']=True
        entry['finished']=time.time();atomic_json(output,status)
    coverage=reconcile(base,root,extra)
    status.update(finished=True,complete_cases=coverage['total_completed'])
    atomic_json(output,status)
    preserve(root)
    return status


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--deadline',type=float)
    parser.add_argument('--mode',choices=('prepare','smol','qwen','injection','reconcile','preserve','followup'),required=True)
    args=parser.parse_args()
    if args.mode=='followup':
        if args.deadline is None:parser.error('Original persisted deadline required')
        print(followup(args.base,args.root,args.deadline));return
    selection=prepare_repair(args.base,args.root)
    if args.mode=='prepare':print({k:{m:len(v) for m,v in d.items()} for k,d in selection.items()});return
    if args.mode=='reconcile':print({'completed':reconcile(args.base,args.root)['total_completed']});return
    if args.mode=='preserve':print(preserve(args.root));return
    if args.deadline is None:parser.error('Persisted repair deadline required')
    bench.check(args.deadline)
    try:
        if args.mode in ('smol','qwen'):
            result=bench.run_model(args.root,args.mode,args.deadline,selection=selection[args.mode],
                adapter_class=StableQwenAdapter if args.mode=='qwen' else None)
        else:result=bench.run_injection(args.root,'qwen',args.deadline,adapter_class=StableQwenAdapter)
        print({k:v for k,v in result.items() if k in ('status','error_type','methods','conditions','weights_unchanged')})
    except Exception:
        (args.root/(args.mode+'_execution_error_PRIVATE.txt')).write_text(traceback.format_exc())
        raise


if __name__=='__main__':main()
