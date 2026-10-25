"""Offline acceptance checks; no pretrained weights, benchmark data or GPU needed."""
import hashlib
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F


def run_cpu_checks(core, adapter_module):
    torch.set_num_threads(1)
    clean = torch.full((1, 3, 28, 28), 128/255, dtype=torch.float64)
    objective = lambda x: (x.mean() - .2).square()
    losses = {}
    for method in ('fgsm', 'pgd', 'patch', 'universal', 'universal_patch', 'feature', 'prompt_match', 'bimodal'):
        cfg = core.AttackConfig(method=method, epsilon=.1, alpha=.03,
                steps=1 if method == 'fgsm' else 3, patch_fraction=.04)
        objectives = [objective, lambda x: (x.mean()-.3).square()] if method.startswith('universal') else [objective]
        result, metrics = core.optimize(clean, objectives, cfg)
        assert (result-clean).abs().max() <= cfg.epsilon + 1e-12
        assert result.min() >= 0 and result.max() <= 1
        assert metrics['best_objective'] < metrics['baseline_objective']
        if 'patch' in method:
            mask = core.patch_mask(clean, cfg.patch_fraction)
            assert torch.equal(result[mask == 0], clean[mask == 0])
        quantized = core.quantize_bounded(result, clean, cfg.epsilon)
        assert (quantized-clean).abs().max() <= cfg.epsilon + 1e-12
        losses[method] = metrics['best_objective']
    cfg = core.AttackConfig(steps=2, restarts=2, transform='flip_pair')
    eot_cfg = core.AttackConfig(method='universal_eot',epsilon=1,steps=3,alpha=.1)
    eot, eot_metrics = core.optimize_shared_patch([clean,clean*.9],[objective,objective],clean,eot_cfg)
    assert eot_metrics['best_objective'] < eot_metrics['baseline_objective']
    eot_mask = core.patch_mask(clean,eot_cfg.patch_fraction)
    assert torch.equal(eot[eot_mask==0],clean[eot_mask==0])
    a, _ = core.optimize(clean, [objective], cfg)
    b, _ = core.optimize(clean, [objective], cfg)
    assert torch.equal(a, b)
    try:
        core.optimize(clean, [objective], cfg, deadline=time.time()-1)
    except TimeoutError:
        pass
    else:
        raise AssertionError('Expired deadline accepted')
    for bad in [dict(epsilon=-1), dict(steps=0), dict(alpha=float('nan')), dict(method='missing')]:
        try:
            core.AttackConfig(**bad).validate()
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid configuration accepted')
    try:
        core.optimize(clean, [lambda x: x.mean()*float('nan')], cfg)
    except FloatingPointError:
        pass
    else:
        raise AssertionError('Nonfinite loss accepted')

    proc = SimpleNamespace(patch_size=14, merge_size=2, temporal_patch_size=2,
            image_mean=[.48145466, .4578275, .40821073], image_std=[.26862954, .26130258, .27577711])
    raw = torch.linspace(0, 1, 3*56*28, dtype=torch.float32).reshape(1, 3, 56, 28).requires_grad_(True)
    actual = adapter_module.patchify(raw, proc)
    z = (raw.detach().numpy()-np.array(proc.image_mean, dtype=np.float32).reshape(1,3,1,1))/np.array(proc.image_std,dtype=np.float32).reshape(1,3,1,1)
    reference = np.repeat(z, 2, axis=0).reshape(1,2,3,2,2,14,1,2,14).transpose(0,3,6,4,7,2,1,5,8).reshape(8,1176)
    assert np.allclose(actual.detach().numpy(), reference, atol=2e-6)
    gradient, = torch.autograd.grad(actual.square().mean(), raw)
    assert torch.isfinite(gradient).all() and gradient.abs().max() > 0
    logits = torch.randn(1, 6, 7, generator=torch.Generator().manual_seed(1), requires_grad=True)
    ids = torch.tensor([[1,2,3,4,5,6]])
    value = adapter_module.shifted_nll(logits, ids, 4)
    expected = F.cross_entropy(logits[:,3:5].reshape(-1,7), ids[:,4:].reshape(-1))
    assert torch.allclose(value, expected)
    value.backward()
    assert logits.grad[:,:3].abs().sum() == 0 and logits.grad[:,3:5].abs().sum() > 0
    assert logits.grad[:,5:].abs().sum() == 0

    class FakeAdapter:
        identity = dict(model='CPU_STUB', revision='offline')
        def read_image(self, path):
            im = np.asarray(Image.open(path).convert('RGB'), dtype=np.float64)/255
            return torch.tensor(im.transpose(2,0,1)[None])
        def parity_check(self, image, prompt, target):
            return dict(processor_max_error=0.)
        def frozen_fingerprint(self):
            return [('frozen', 0)]
        def objective(self, clean, prompt, target):
            if target == 'FAIL_TEST':
                return lambda x: x.mean()*float('nan')
            return objective
        def feature_objective(self, target):
            return objective
        def match_objective(self, clean, prompt, target, teacher_prompt):
            return objective
        def generate(self, image, prompt):
            return dict(response='PRIVATE_TEST_SENTINEL', cap_hit=False)

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        image = root/'input.png'
        Image.fromarray(np.full((28,28,3),128,dtype=np.uint8)).save(image)
        row = dict(id='dev', image=str(image), image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                prompt='PRIVATE_TEST_SENTINEL', target='TEST_TARGET', intent_group='d', image_group='d',
                track='integrity', split='development', injection_image=str(image),
                injection_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                feature_image=str(image), feature_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
                teacher_prompt='TEST_TEACHER', candidate_prompts=['TEST_CANDIDATE'], defense_prefix='TEST_DEFENSE')
        opt_image = root/'optimization.png'
        Image.fromarray(np.full((28,28,3),127,dtype=np.uint8)).save(opt_image)
        opt = dict(row, id='opt', split='optimization', intent_group='o', image_group='o',
                image=str(opt_image),image_sha256=hashlib.sha256(opt_image.read_bytes()).hexdigest())
        for method in ('fgsm','pgd','patch','universal','universal_patch','universal_eot','feature','prompt_match','injection','bimodal'):
            out = root/(method+'_PRIVATE')
            cfg = core.AttackConfig(method=method, steps=1 if method=='fgsm' else 2,
                    epsilon=1 if method=='universal_eot' else 8/255)
            contract = dict(test=method)
            counts = core.run_private(FakeAdapter(), [row,opt], cfg, out, contract, time.time()+60)
            assert counts['completed']==1 and counts['failed']==0
            counts = core.run_private(FakeAdapter(), [row,opt], cfg, out, contract, time.time()+60)
            assert counts['cached']==1 and counts['completed']==0
            export = json.loads((out/'aggregate_status.json').read_text())
            assert 'PRIVATE_TEST_SENTINEL' not in json.dumps(export)
            try:
                core.run_private(FakeAdapter(),[row,opt],cfg,out,dict(test='changed'),time.time()+60)
            except ValueError:
                pass
            else:
                raise AssertionError('Changed contract reused run directory')
        reserved = dict(row,id='eval',split='evaluation',intent_group='e',image_group='e')
        out = root/'reserved_PRIVATE'
        assert core.run_private(FakeAdapter(),[reserved],cfg,out,{},time.time()+60)['completed']==0
        try:
            core.validate_manifest([row,dict(row,id='leak',split='evaluation')])
        except ValueError:
            pass
        else:
            raise AssertionError('Group leakage accepted')
        bad = dict(row,target='FAIL_TEST')
        out = root/'failure_PRIVATE'
        counts = core.run_private(FakeAdapter(),[bad],core.AttackConfig(),out,{},time.time()+60)
        assert counts['failed']==1
        assert core.run_private(FakeAdapter(),[bad],core.AttackConfig(),out,{},time.time()+60)['cached_failed']==1
        changed = dict(row,image_sha256='invalid')
        try:
            core.validate_manifest([changed])
        except ValueError:
            pass
        else:
            raise AssertionError('Changed image accepted')
    return dict(optimizer_methods=len(losses)+1, private_runner_methods=10, processor_layout='passed',
                causal_target_mask='passed', resume_failure_privacy='passed', gpu='not_tested')


def run_architecture_check(adapter_module):
    """Exact reviewed native API, randomly initialized tiny weights; no downloads."""
    import transformers
    from transformers import Qwen2_5_VLConfig, Qwen2_5_VLForConditionalGeneration
    from transformers.models.qwen2_vl.image_processing_qwen2_vl import Qwen2VLImageProcessor
    if transformers.__version__ != '4.57.1':
        raise RuntimeError('Architecture check requires transformers==4.57.1')
    torch.set_num_threads(1)
    raw = (torch.arange(3*56*56).reshape(1,3,56,56)%256).float()/255
    proc = Qwen2VLImageProcessor(min_pixels=56*56,max_pixels=56*56)
    image = Image.fromarray((raw[0].permute(1,2,0).numpy()*255).round().astype(np.uint8))
    reference = proc(images=[image],return_tensors='pt')['pixel_values']
    raw.requires_grad_(True)
    ours = adapter_module.patchify(raw,proc)
    assert torch.allclose(ours,reference,atol=2e-6,rtol=2e-6)
    config = Qwen2_5_VLConfig(text_config=dict(vocab_size=32,hidden_size=32,intermediate_size=64,
            num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=2,
            rope_scaling={'type':'mrope','mrope_section':[2,1,1]}),
            vision_config=dict(depth=1,hidden_size=32,intermediate_size=64,num_heads=4,
            out_hidden_size=32,patch_size=14,spatial_merge_size=2,temporal_patch_size=2,
            window_size=28,fullatt_block_indexes=[0]),image_token_id=5,video_token_id=4,
            vision_start_token_id=6,vision_end_token_id=7)
    config._attn_implementation = 'eager'
    with torch.random.fork_rng():
        torch.manual_seed(1)
        model = Qwen2_5_VLForConditionalGeneration(config).eval().requires_grad_(False)
    ids = torch.tensor([[1,6,5,5,5,5,7,8,9]])
    grid = torch.tensor([[1,4,4]])
    out = model(input_ids=ids,attention_mask=torch.ones_like(ids),pixel_values=ours,
                image_grid_thw=grid,use_cache=False)
    gradient, = torch.autograd.grad(adapter_module.shifted_nll(out.logits,ids,8),raw)
    assert torch.isfinite(gradient).all() and gradient.abs().max()>0
    assert isinstance(model.model.visual(ours,grid_thw=grid),torch.Tensor)
    return dict(native_api=transformers.__version__,preprocessor='passed',
                native_image_gradient='passed',pretrained_weights=False,gpu=False)


if __name__ == '__main__':
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
    import vlm_visual_attacks as core_module
    import vlm_visual_adapter as adapter_module
    print(run_cpu_checks(core_module,adapter_module))
    if '--architecture' in sys.argv:
        print(run_architecture_check(adapter_module))
