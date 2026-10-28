"""Private, bounded reproduction candidate of the released JIP encoder example.

No model, network or GPU operations on import. No synthetic research inputs.
"""
import hashlib
import json
from pathlib import Path
import platform
import time
import urllib.request

REVISION = 'b7b2bce812adada23f583f63f63e564f84d277c6'
REPO = 'erfanshayegani/Jailbreak-In-Pieces'
MODEL = 'openai/clip-vit-large-patch14-336'
TOKEN = 'AMENDMENT_13_JIP_ENCODER_60_MIN_FREE_ONLY'
FILES = {
    'src/adv_image.py': 'b9cd5f79bfd087f92481ead5443e10b0e3dd14fa',
    'images/meth_pill.png': '70dee0d7a36dc78f56bf1e65d8ecba4280d7cab7',
    'images/white.jpeg': '743f5240ddabe0c05f367f5b5b9f9af4f011c638',
    'LICENSE': '1f766cee9a8e1a493544165fcaa8ac2cea639152',
}


def save(path, record):
    path = Path(path)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(record, indent=2))
    temp.replace(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(state):
    if time.time() >= state['deadline']:
        raise TimeoutError('Original attempt deadline expired; preserve, do not reset')


def start(root, acceptance, platform_name):
    """Start clock before installation; no implicit continuation or overwrite."""
    root = Path(root)
    if acceptance != TOKEN or platform_name != 'colab_free_t4':
        raise ValueError('Approved token and primary free Colab scope required')
    if 'PRIVATE' not in str(root):
        raise ValueError('Private persistent folder required')
    root.mkdir(parents=True, exist_ok=True)
    clock = root/'attempt_clock_PRIVATE.json'
    state = dict(started=time.time(), status='started', platform=platform_name,
                 max_seconds=3600, approval_token=acceptance)
    state['deadline'] = state['started'] + state['max_seconds']
    with clock.open('x') as handle:
        json.dump(state, handle)
    return state


def sources(root, state):
    root = Path(root)
    records = []
    for name, expected in FILES.items():
        check(state)
        path = root/'upstream_PRIVATE'/name
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f'https://raw.githubusercontent.com/{REPO}/{REVISION}/{name}'
        request = urllib.request.Request(url, headers={'User-Agent':'JIP-source-reproduction'})
        with urllib.request.urlopen(request, timeout=min(45, max(1, state['deadline']-time.time()))) as response:
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError('Unexpected source size')
        blob = hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
        if blob != expected:
            raise ValueError('Published input/source blob mismatch: '+name)
        path.write_bytes(payload)
        records.append(dict(path=name, git_blob=blob, sha256=sha(path), bytes=len(payload)))
    save(root/'source_manifest_PRIVATE.json', records)
    return records


def weights_digest(model):
    """Hash actual state tensors without copying the whole checkpoint at once."""
    value = hashlib.sha256()
    for key, tensor in model.state_dict().items():
        value.update(key.encode())
        value.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return value.hexdigest()


def run(root, state):
    import importlib.metadata
    import numpy as np
    from PIL import Image
    import PIL
    import torch
    from huggingface_hub import HfApi
    from transformers import CLIPModel, CLIPImageProcessor

    root = Path(root)
    check(state)
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('An allocated Colab T4 is required; do not pay or silently change device')
    torch.manual_seed(42); np.random.seed(42)
    sources(root, state)
    check(state)
    model_revision = HfApi().model_info(MODEL, timeout=45).sha
    identity = dict(model=MODEL, model_revision=model_revision, source_revision=REVISION,
        device=torch.cuda.get_device_name(0), python=platform.python_version(),
        libraries={name:importlib.metadata.version(name) for name in ('torch','transformers','huggingface-hub','numpy')},
        pillow=PIL.__version__, precision='float32', seed=42,
        fidelity='encoder-method adaptation / release-reproduction candidate',
        deviations=['Reimplemented inspected loop; upstream imports not executed',
                    'Frozen parameter gradients; current resolved model/library revisions',
                    'Profile then separately restarted release-length run; no downstream ASR'])
    save(root/'identity_PRIVATE.json', identity)
    check(state)
    processor = CLIPImageProcessor.from_pretrained(MODEL, revision=model_revision)
    processor.do_normalize = False
    model = CLIPModel.from_pretrained(MODEL, revision=model_revision, torch_dtype=torch.float32).eval().to('cuda')
    model.requires_grad_(False)
    check(state)
    identity['processor'] = processor.to_dict()
    identity['weights_before'] = weights_digest(model)
    save(root/'identity_PRIVATE.json', identity)
    with Image.open(root/'upstream_PRIVATE/images/meth_pill.png') as image:
        target = processor(images=image, return_tensors='pt')['pixel_values'].to('cuda')
    with Image.open(root/'upstream_PRIVATE/images/white.jpeg') as image:
        initial = processor(images=image, return_tensors='pt')['pixel_values'].to('cuda')
    if initial.shape != (1,3,336,336) or target.shape != initial.shape:
        raise ValueError('Original CLIP canvas dimensions not recovered')
    with torch.no_grad():
        target_features = model.get_image_features(pixel_values=target).detach()
    distance = torch.nn.PairwiseDistance(p=2)

    def attempt(name, steps):
        check(state)
        folder = root/name
        folder.mkdir(exist_ok=False)
        x = initial.detach().clone().requires_grad_(True)
        optimizer = torch.optim.Adam([x], lr=0.1)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize(); began = time.monotonic()
        with torch.no_grad():
            before = float(distance(model.get_image_features(pixel_values=x), target_features).item())
        trace = []
        record = dict(status='running', planned_updates=steps, completed_updates=0, initial_distance=before)
        save(folder/'status_PRIVATE.json', record)
        try:
            for step in range(steps):
                check(state); optimizer.zero_grad(set_to_none=True)
                loss = distance(model.get_image_features(pixel_values=x), target_features).mean()
                if not torch.isfinite(loss):
                    raise FloatingPointError('Nonfinite feature distance')
                loss.backward()
                if x.grad is None or not torch.isfinite(x.grad).all() or x.grad.abs().max()==0:
                    raise FloatingPointError('Invalid image gradient')
                gradient_max = float(x.grad.abs().max())
                optimizer.step()
                with torch.no_grad(): x.clamp_(0,1)
                trace.append(dict(update=step+1, pre_update_distance=float(loss.detach()), gradient_max=gradient_max))
                record['completed_updates'] = step+1
                if (step+1)%10==0:
                    save(folder/'trace_PRIVATE.json', trace); save(folder/'status_PRIVATE.json', record)
            record['status'] = 'completed_encoder_only'
        except Exception as error:
            record.update(status='incomplete', error_type=type(error).__name__)
            save(folder/'status_PRIVATE.json', record)
            raise
        finally:
            torch.cuda.synchronize()
            record['elapsed_seconds'] = time.monotonic()-began
            record['peak_allocated_bytes'] = torch.cuda.max_memory_allocated()
            save(folder/'trace_PRIVATE.json', trace)
            with torch.no_grad():
                record['final_tensor_distance'] = float(distance(model.get_image_features(pixel_values=x),target_features).item())
            pixels=(x.detach().cpu()*255).clamp(0,255).to(torch.uint8)[0].permute(1,2,0).numpy()
            artifact = folder/'optimized_PRIVATE.jpg'
            Image.fromarray(pixels).save(artifact)
            with Image.open(artifact) as image:
                reloaded=processor(images=image,return_tensors='pt')['pixel_values'].to('cuda')
            with torch.no_grad():
                record['jpeg_reload_distance']=float(distance(model.get_image_features(pixel_values=reloaded),target_features).item())
            record['artifact_sha256']=sha(artifact)
            record['asr']='NOT_MEASURED'
            save(folder/'status_PRIVATE.json',record)
        return record

    results = {'profile_50': attempt('profile_50',50)}
    profile = results['profile_50']
    projected = profile['elapsed_seconds'] * 100
    remaining = state['deadline'] - time.time()
    if profile['final_tensor_distance'] >= profile['initial_distance']:
        results['release_5000'] = dict(status='blocked_profile_no_objective_improvement')
    elif projected*1.5 + 300 >= remaining:
        results['release_5000'] = dict(status='not_run_budget_projection',projected_seconds=projected,remaining_seconds=remaining)
    else:
        results['release_5000'] = attempt('release_5000',5000)
    identity['weights_after'] = weights_digest(model)
    identity['weights_unchanged'] = identity['weights_before']==identity['weights_after']
    save(root/'identity_PRIVATE.json',identity)
    if not identity['weights_unchanged']:
        raise RuntimeError('Frozen-weight identity failed')
    save(root/'encoder_summary_PRIVATE.json',dict(identity=identity,results=results))
    return results
