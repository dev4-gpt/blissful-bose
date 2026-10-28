"""Pinned paper/release audit; no automatic scientific runs or synthetic fallback."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

PAPERS = [
    {"id":"fgsm","authors":"Goodfellow et al.","title":"Explaining and Harnessing Adversarial Examples","arxiv":"1412.6572v3","role":"foundation","repo":None,"revision":None,"variants":["untargeted classification"],"datasets":["MNIST"],"blocker":"Original maxout checkpoint/configuration unresolved.","paper_url":"https://arxiv.org/html/1412.6572v3","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"pgd","authors":"Madry et al.","title":"Towards Deep Learning Models Resistant to Adversarial Attacks","arxiv":"1706.06083v4","role":"foundation","repo":"MadryLab/cifar10_challenge","revision":"f15682d9f1e26eb47a2d3b371ef8b6c7abcf6276","variants":["MNIST inner attack","CIFAR-10 inner attack"],"datasets":["MNIST","CIFAR-10"],"blocker":"Challenge release defaults are not automatically paper-table settings; original weights/splits not audited.","paper_url":"https://arxiv.org/html/1706.06083v4","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"patch","authors":"Brown et al.","title":"Adversarial Patch","arxiv":"1712.09665v2","role":"foundation","repo":None,"revision":None,"variants":["single-model","ensemble","transfer","camouflage","physical"],"datasets":["ImageNet"],"blocker":"Original transformations, image selection and code provenance incomplete; a VLM version changes the task.","paper_url":"https://arxiv.org/html/1712.09665v2","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"qi","authors":"Qi et al.","title":"Visual Adversarial Examples Jailbreak Aligned Large Language Models","arxiv":"2306.13213v2","role":"VLM attack","repo":"Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models","revision":"5fc9883cfa9b4183cf05c6eceef49e449e45e9c9","variants":["MiniGPT-4","InstructBLIP","LLaVA-LLaMA-2","constrained","unconstrained"],"datasets":["released 66-sentence corpus","40 manual requests","RealToxicityPrompts challenging subset"],"blocker":"Original weights/human evaluation/Perspective scoring unrun; A100 configuration differs from T4.","paper_url":"https://arxiv.org/html/2306.13213v2","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"pieces","authors":"Shayegani et al.","title":"Jailbreak in pieces: Compositional Adversarial Attacks on Multi-Modal Language Models","arxiv":"2307.14539v2","role":"VLM attack","repo":"erfanshayegani/Jailbreak-In-Pieces","revision":"b7b2bce812adada23f583f63f63e564f84d277c6","variants":["text trigger","OCR trigger","visual trigger","OCR+visual trigger"],"datasets":["paper trigger/scenario collection","AdvBench supplementary subset"],"blocker":"Release supplies examples and encoder code; complete paper collection/splits and version alignment unresolved.","paper_url":"https://arxiv.org/html/2307.14539v2","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"hijacks","authors":"Bailey et al.","title":"Image Hijacks: Adversarial Images can Control Generative Models at Runtime","arxiv":"2309.00236v4","role":"VLM attack","repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","variants":["specific string","leak-context format","jailbreak behavior","disinformation prompt matching"],"datasets":["Alpaca","AdvBench","demo Alpaca/LLaVA mixture"],"blocker":"Public demo is not full paper experiment suite; jailbreak/prompt-matching configs and original weights unresolved.","paper_url":"https://arxiv.org/html/2309.00236v4","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"bap","authors":"Ying et al.","title":"Jailbreak Vision Language Models via Bi-Modal Adversarial Prompt","arxiv":"2406.04031v2","role":"VLM attack","repo":"NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt","revision":"5350c0bfeb01d9e485603b85a03500280886d275","variants":["query-agnostic visual PGD","feedback-driven image/text search"],"datasets":["paper SafetyBench scenarios","deduplicated AdvBench","query-agnostic corpus"],"blocker":"Original ChatGPT feedback/judging conflicts with open-only scope; original corpus and merged split need frozen artifacts.","paper_url":"https://arxiv.org/html/2406.04031v2","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"physical_injection","authors":"Ling et al.","title":"Physical Prompt Injection Attacks on Large Vision-Language Models","arxiv":"2601.17383v1","role":"VLM attack","repo":"2023cghacker/Physical-Prompt-Injection-Attack","revision":"7291d92ee05c4b9079ef824e0b4bd12e8e14316c","variants":["prompt selection","location search","simulation","physical capture"],"datasets":["Embodied City","Habitat","physical vehicle trials"],"blocker":"Upstream states code not fully runnable; physical data/hardware outside initial approved scope.","paper_url":"https://arxiv.org/html/2601.17383v1","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"mmj","authors":"Weng et al.","title":"MMJ-Bench: A Comprehensive Study on Jailbreak Attacks and Defenses for Vision Language Models","arxiv":None,"role":"benchmark","repo":"thunxxx/MLLM-Jailbreak-evaluation-MMJ-Bench","revision":"68922de9209478923dbc0a1b4eccb18a69e2c87e","variants":["attack generation","completions","scoring","utility"],"datasets":["HarmBench","MM-Vet"],"blocker":"Original artifact/model/table coverage and GPT-4 utility scoring not reproduced.","paper_url":"https://ojs.aaai.org/index.php/AAAI/article/download/34983/37138","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"adashield","authors":"Wang et al.","title":"AdaShield: Safeguarding Multimodal Large Language Models from Structure-based Attack via Adaptive Shield Prompting","arxiv":"2403.09513v1","role":"defense","repo":"SaFo-Lab/AdaShield","revision":"b6d02c6747bd6984a99ee2e1db1e52736a6a05cc","variants":["AdaShield-S","AdaShield-A"],"datasets":["FigStep","MM-SafetyBench QR","MM-Vet"],"blocker":"Generic prefix is not AdaShield; original pool/splits and GPT-4 steps need audit and open-only deviation.","paper_url":"https://arxiv.org/html/2403.09513v1","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"jailguard","authors":"Zhang et al.","title":"JailGuard: A Universal Detection Framework for Prompt-based Attacks on LLM Systems","arxiv":"2312.10766v4","role":"defense","repo":"shiningrain/JailGuard","revision":"419e1d3d08f4d02998a11a687f925518d2d5dd0c","variants":["visual mutators","combination policy","divergence detector"],"datasets":["official attack/benign release"],"blocker":"Original policy, encoder, split, threshold and targets not reproduced; no detector run.","paper_url":"https://arxiv.org/html/2312.10766v4","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
    {"id":"survey","authors":"Zhang et al.","title":"Adversarial Attacks of Vision Tasks in the Past 10 Years: A Survey","arxiv":"2410.23687v2","role":"survey","repo":None,"revision":None,"variants":[],"datasets":[],"blocker":"Taxonomy/discovery source; not an attack experiment.","paper_url":"https://arxiv.org/html/2410.23687v2","inspection":"Methods/setup and selected appendices/code inspected; full experiment audit incomplete","reproduction_status":"NOT_RUN"},
]

REVIEWED_FILES = [
    {"repo":"Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models","revision":"5fc9883cfa9b4183cf05c6eceef49e449e45e9c9","path":"README.md","git_blob":"f2468d6882fff91a3a6a6176d1ee10963aa3e252"},
    {"repo":"erfanshayegani/Jailbreak-In-Pieces","revision":"b7b2bce812adada23f583f63f63e564f84d277c6","path":"README.md","git_blob":"6fad07fcc15f576f189e20b4a8b6c814ceeaad64"},
    {"repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","path":"README.md","git_blob":"eb3274ab29cd4cae51ac4f2dd79aac33ce17662f"},
    {"repo":"NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt","revision":"5350c0bfeb01d9e485603b85a03500280886d275","path":"README.md","git_blob":"3fc4b0182e26945ac4f6dee3d9217eb18a07e0fb"},
    {"repo":"2023cghacker/Physical-Prompt-Injection-Attack","revision":"7291d92ee05c4b9079ef824e0b4bd12e8e14316c","path":"README.md","git_blob":"39db3833a94bd88ba775d58f9f1f7ccc9256a22d"},
    {"repo":"thunxxx/MLLM-Jailbreak-evaluation-MMJ-Bench","revision":"68922de9209478923dbc0a1b4eccb18a69e2c87e","path":"README.md","git_blob":"331b103bf7b21ccc7bdc301f74c830b23e2d6a93"},
    {"repo":"SaFo-Lab/AdaShield","revision":"b6d02c6747bd6984a99ee2e1db1e52736a6a05cc","path":"README.md","git_blob":"801e74f78b0a86be05d8f50d45b745953d0d42d8"},
    {"repo":"shiningrain/JailGuard","revision":"419e1d3d08f4d02998a11a687f925518d2d5dd0c","path":"README.md","git_blob":"3f7e0c2d533dca9a25d0066448c5882ebb4a3a54"},
    {"repo":"Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models","revision":"5fc9883cfa9b4183cf05c6eceef49e449e45e9c9","path":"minigpt_visual_attack.py","git_blob":"55d27fdea7b5e899952ca6646ca49ab4c03eb60b"},
    {"repo":"Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models","revision":"5fc9883cfa9b4183cf05c6eceef49e449e45e9c9","path":"minigpt_utils/visual_attacker.py","git_blob":"74832621b9f37e128a68d763e32cf91c39e18e76"},
    {"repo":"Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models","revision":"5fc9883cfa9b4183cf05c6eceef49e449e45e9c9","path":"eval_configs/minigpt4_eval.yaml","git_blob":"54128ba4a62bdf873b9172d846ef4d08b356de72"},
    {"repo":"erfanshayegani/Jailbreak-In-Pieces","revision":"b7b2bce812adada23f583f63f63e564f84d277c6","path":"src/adv_image.py","git_blob":"b9cd5f79bfd087f92481ead5443e10b0e3dd14fa"},
    {"repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","path":"experiments/exp_demo_imgs/config.py","git_blob":"d87a7f8f04ff8597a963f78d052b16641fcea9d0"},
    {"repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","path":"image_hijacks/data.py","git_blob":"05359db3f60f3bcf15fbf3d671d83e569c44068a"},
    {"repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","path":"image_hijacks/config.py","git_blob":"413b62b2772340c8f99094ac0dc4d71d17146497"},
    {"repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","path":"image_hijacks/components/loss.py","git_blob":"6834ac42eb58b5586211a7e7701b9083df7add0d"},
    {"repo":"euanong/image-hijacks","revision":"2a4403cf67e8578afdd6e56096ff31524aaa63e7","path":"image_hijacks/components/optim.py","git_blob":"e02e6c89728c75144582d58e627056d402d0ed46"},
    {"repo":"NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt","revision":"5350c0bfeb01d9e485603b85a03500280886d275","path":"VAP.py","git_blob":"410381b2da3998b024db9ec28ae1d539768e29c9"},
    {"repo":"NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt","revision":"5350c0bfeb01d9e485603b85a03500280886d275","path":"CoT.py","git_blob":"32c219e78fe5ed16869a8527ca72e96cb34d2aea"},
    {"repo":"NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt","revision":"5350c0bfeb01d9e485603b85a03500280886d275","path":"Eval.py","git_blob":"36a7f9353dd533e1eba2a15b7958118dae19fa69"},
    {"repo":"MadryLab/cifar10_challenge","revision":"f15682d9f1e26eb47a2d3b371ef8b6c7abcf6276","path":"config.json","git_blob":"613efd2e235b892df14bf084defddfac67f3fe82"},
    {"repo":"MadryLab/mnist_challenge","revision":"3ee3643c4a8c59458d8c191b84027f4a6cbd9580","path":"config.json","git_blob":"af5efb1f138af0217d8891740b62e2b3faa59df3"},
]



def source_url(entry):
    return 'https://raw.githubusercontent.com/'+entry['repo']+'/'+entry['revision']+'/'+entry['path']


def audit_source(entry, private_root):
    """Download one reviewed source file only; verify Git blob identity; never execute it."""
    if entry not in REVIEWED_FILES:
        raise ValueError('Source not in reviewed allowlist')
    root=Path(private_root)
    if 'PRIVATE' not in str(root):
        raise ValueError('Private review folder required')
    dest=root/entry['repo']/entry['path']
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():
        request=urllib.request.Request(source_url(entry),headers={'User-Agent':'VLM-paper-audit'})
        with urllib.request.urlopen(request,timeout=45) as response:
            payload=response.read(2_000_001)
        if len(payload)>2_000_000:raise ValueError('Unexpected large source file')
        dest.write_bytes(payload)
    data=dest.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!=entry['git_blob']:raise ValueError('Pinned source identity mismatch')
    syntax=dict(status='not_python')
    if entry['path'].endswith('.py'):
        try:
            compile(data,str(dest),'exec');syntax=dict(status='passed')
        except SyntaxError as error:
            syntax=dict(status='invalid_upstream_source',error_type=type(error).__name__,line=error.lineno)
    return dict(repo=entry['repo'],path=entry['path'],revision=entry['revision'],
                git_blob_verified=True,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),syntax=syntax)


def classify_evidence(record):
    """A name match never promotes a run into faithful reproduction."""
    required=('paper_version','code_revision','checkpoint_hash','processor_hash',
              'dataset_hashes','split_ids_hash','objective_id','optimizer_settings',
              'decoding_settings','judge_protocol','source_result_location',
              'raw_output_manifest_hash','completion_audit')
    missing=[key for key in required if not record.get(key)]
    differences=record.get('deviations',[])
    if missing:return dict(label='UNRESOLVED',missing=missing,deviations=differences)
    if differences:return dict(label='ADAPTATION',missing=[],deviations=differences)
    if record.get('scale_reduced'):return dict(label='REDUCED_SCALE_CANDIDATE',requires='review of retained methodology')
    return dict(label='FAITHFUL_CANDIDATE',requires='independent protocol/result review; not automatic validation')


def reference_command(paper_id, private_checkout, output_dir):
    """Only entrypoints actually inspected. Separate environments are still required."""
    paper=next(p for p in PAPERS if p['id']==paper_id)
    checkout=Path(private_checkout)
    if 'PRIVATE' not in str(checkout) or 'PRIVATE' not in str(output_dir):
        raise ValueError('Private source/output folders required')
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
    if revision!=paper['revision']:raise ValueError('Original source revision differs')
    if paper_id=='qi':
        # Upstream parser uses underscores. It hardcodes num_iter=5000 and batch_size=8.
        return [sys.executable,'minigpt_visual_attack.py','--cfg_path',
                'eval_configs/minigpt4_eval.yaml','--gpu_id','0','--n_iters','5000',
                '--constrained','--eps','16','--alpha','1','--save_dir',str(output_dir)],checkout
    if paper_id=='pieces':
        # Upstream demo: CLIP 336, released trigger/white image, Adam .1, 5000 updates.
        return [sys.executable,'adv_image.py'],checkout/'src'
    raise ValueError('No fully reviewed runnable original entrypoint for this paper')


def run_reference(paper_id, private_checkout, output_dir, approval):
    """Never called by default. Missing scientific/compute approvals block model execution."""
    required=('owner_approved','amendment_approved','source_execution_approved',
              'original_weights_verified','original_data_verified','environment_verified',
              'evaluation_protocol_frozen','compute_profile_verified')
    missing=[key for key in required if approval.get(key) is not True]
    if missing:raise ValueError('Unmet original-run gates: '+', '.join(missing))
    command,cwd=reference_command(paper_id,private_checkout,output_dir)
    budget=approval.get('wall_seconds')
    if not isinstance(budget,int) or budget<=0:raise ValueError('Explicit wall-time budget required')
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    clock=out/'reference_clock_PRIVATE.json'
    if clock.exists():
        raise ValueError('Existing attempt preserved; do not reset or replay its clock')
    state=dict(paper=paper_id,started=time.time(),wall_seconds=budget,status='running',
               code_revision=next(p['revision'] for p in PAPERS if p['id']==paper_id))
    clock.write_text(json.dumps(state))
    try:
        with (out/'execution_PRIVATE.log').open('w') as log:
            completed=subprocess.run(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,timeout=budget)
        state.update(exit_code=completed.returncode,status='process_finished_requires_result_audit')
    except subprocess.TimeoutExpired:state['status']='budget_stopped_incomplete'
    finally:
        state['finished']=time.time();clock.write_text(json.dumps(state))
    return state
