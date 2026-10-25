"""Real input optimizers and private runner. No model loading on import.

All methods minimize a supplied differentiable scalar objective. Original paper
settings and model-specific reproductions are separate from these adaptations.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import time

import torch


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, sort_keys=True, allow_nan=False))
    os.replace(tmp, path)


@dataclass(frozen=True)
class AttackConfig:
    method: str = 'pgd'
    epsilon: float = 8/255
    steps: int = 20
    alpha: float = 2/255
    restarts: int = 1
    seed: int = 20261025
    patch_fraction: float = .04
    transform: str = 'identity'
    defense_aware: bool = False

    def validate(self):
        if self.method not in {'fgsm', 'pgd', 'patch', 'universal', 'universal_patch', 'universal_eot', 'feature', 'prompt_match', 'injection', 'bimodal'}:
            raise ValueError('Unsupported attack method')
        for v in (self.epsilon, self.alpha, self.patch_fraction):
            if not math.isfinite(v):
                raise ValueError('Nonfinite attack setting')
        if not 0 <= self.epsilon <= 1 or not 0 < self.alpha <= 1 or not 0 < self.patch_fraction <= 1:
            raise ValueError('Invalid attack bounds')
        if any(type(v) is not int or v < 1 for v in (self.steps, self.restarts)):
            raise ValueError('Positive integer steps/restarts required')
        if self.method == 'fgsm' and (self.steps != 1 or self.restarts != 1):
            raise ValueError('FGSM must have exactly one step and restart')
        if self.transform not in {'identity', 'flip_pair'}:
            raise ValueError('Unknown transform')
        if type(self.defense_aware) is not bool:
            raise ValueError('defense_aware must be boolean')
        if self.defense_aware and self.method in {'feature', 'injection'}:
            raise ValueError('This objective cannot optimize against a text defense')
        if self.method == 'universal_eot' and self.epsilon != 1:
            raise ValueError('Replacement EOT patch uses box-only pixels, epsilon=1; report its area')
        if self.method == 'universal_eot' and self.restarts != 1:
            raise ValueError('EOT patch adaptation supports one start; do not silently ignore restarts')


def pixels_valid(x):
    if x.ndim != 4 or x.shape[0] != 1 or x.shape[1] != 3 or not x.is_floating_point():
        raise ValueError('Expected one floating RGB NCHW image')
    if not torch.isfinite(x).all() or x.min() < 0 or x.max() > 1:
        raise ValueError('Pixels outside finite [0,1] range')


def patch_mask(x, fraction):
    h, w = x.shape[-2:]
    side = max(1, int(math.sqrt(fraction * h * w)))
    ph, pw = min(side, h), min(side, w)
    mask = torch.zeros_like(x)
    mask[..., :ph, :pw] = 1  # Fixed top-left location, recorded, never selected on test.
    return mask


def project(x, clean, epsilon, mask):
    low, high = (clean - epsilon).clamp(0, 1), (clean + epsilon).clamp(0, 1)
    bounded = torch.maximum(low, torch.minimum(high, x))
    return torch.where(mask.bool(), bounded, clean).detach()


def optimize(clean, objectives, config, deadline=None):
    """Minimize mean loss; universal modes share one image across private contexts.

    'feature' uses Adam; PGD variants use signed descent. Best iterate/restart is
    selected on optimization loss, never on held-out generations or guard labels.
    """
    config.validate()
    if config.method == 'injection':
        raise ValueError('Injection is an artifact evaluation, not gradient optimization')
    pixels_valid(clean)
    if not objectives:
        raise ValueError('At least one objective required')
    clean = clean.detach().clone()
    local = config.method in {'patch', 'universal_patch'}
    mask = patch_mask(clean, config.patch_fraction) if local else torch.ones_like(clean)
    best, best_loss, calls = clean.clone(), math.inf, 0
    trace = []

    def check_time():
        if deadline is not None and time.time() >= deadline:
            raise TimeoutError('Persistent run deadline reached')

    def score(x):
        nonlocal calls
        total = 0.
        with torch.no_grad():
            for objective in objectives:
                for view in ([x] if config.transform == 'identity' else [x, x.flip(-1)]):
                    check_time()
                    loss = objective(view)
                    calls += 1
                    if loss.ndim or not torch.isfinite(loss):
                        raise FloatingPointError('Invalid scalar objective')
                    total += float(loss)
        return total / (len(objectives) * (1 if config.transform == 'identity' else 2))

    baseline = score(clean)
    best_loss = baseline
    for restart in range(config.restarts):
        rng = torch.Generator(device=clean.device).manual_seed(config.seed + restart)
        if config.method == 'fgsm':
            x = clean.clone()
        else:
            noise = 2 * torch.rand(clean.shape, device=clean.device, dtype=clean.dtype, generator=rng) - 1
            x = project(clean + config.epsilon * noise, clean, config.epsilon, mask)
        adam = torch.optim.Adam([x.requires_grad_(True)], lr=config.alpha) if config.method == 'feature' else None
        for step in range(config.steps):
            check_time()
            x.requires_grad_(True)
            gradient = torch.zeros_like(x)
            count = len(objectives) * (1 if config.transform == 'identity' else 2)
            for objective in objectives:
                for flipped in ([False] if config.transform == 'identity' else [False, True]):
                    check_time()
                    loss = objective(x.flip(-1) if flipped else x)
                    calls += 1
                    if loss.ndim or not torch.isfinite(loss):
                        raise FloatingPointError('Invalid scalar objective')
                    grad, = torch.autograd.grad(loss, x)
                    if not torch.isfinite(grad).all():
                        raise FloatingPointError('Nonfinite image gradient')
                    gradient.add_(grad / count)
                    del loss, grad
            if gradient.abs().max() == 0 and config.epsilon > 0:
                raise FloatingPointError('Zero image gradient; attack not validated')
            if adam is not None:
                adam.zero_grad(set_to_none=True)
                x.grad = gradient
                adam.step()
                with torch.no_grad():
                    x.copy_(project(x, clean, config.epsilon, mask))
            else:
                step_size = config.epsilon if config.method == 'fgsm' else config.alpha
                x = project(x - step_size * gradient.sign(), clean, config.epsilon, mask)
            value = score(x)
            trace.append(dict(restart=restart, step=step+1, objective=value))
            if value < best_loss:
                best, best_loss = x.detach().clone(), value
    return best, dict(baseline_objective=baseline, best_objective=best_loss, forward_calls=calls,
                      trace=trace, effective_patch_fraction=float(mask.mean()) if local else None)


def quantize_bounded(candidate, clean, epsilon, mask=None):
    """Deliver valid uint8 pixels; reject budgets with no representable interval."""
    low = torch.ceil((clean - epsilon).clamp(0, 1) * 255)
    high = torch.floor((clean + epsilon).clamp(0, 1) * 255)
    if (low > high).any():
        raise ValueError('No representable pixel in declared budget')
    value = torch.maximum(low, torch.minimum(high, torch.round(candidate * 255))) / 255
    if mask is not None:
        value = torch.where(mask.bool(), value, clean)
    return value.detach()


def optimize_shared_patch(backgrounds, objectives, clean, config, deadline=None):
    """Shared replacement patch over backgrounds, translations and right-angle rotations.

    This is an EOT mechanism adaptation; it does not simulate a physical camera.
    Evaluation uses a fixed top-left placement and a background outside optimization.
    """
    config.validate()
    if config.method != 'universal_eot' or len(backgrounds) != len(objectives) or not backgrounds:
        raise ValueError('EOT requires paired optimization backgrounds/objectives')
    for image in backgrounds + [clean]:
        pixels_valid(image)
        if image.shape != clean.shape:
            raise ValueError('Shared patch needs equal canonical canvas shapes')
    mask = patch_mask(clean, config.patch_fraction)
    side = int(mask[0, 0].sum(1).max())
    h, w = clean.shape[-2:]
    rng = torch.Generator(device='cpu').manual_seed(config.seed)
    placements = [(int(torch.randint(h-side+1, (), generator=rng)),
                   int(torch.randint(w-side+1, (), generator=rng)),
                   int(torch.randint(4, (), generator=rng))) for _ in backgrounds]
    def compose(image, patch, placement):
        top, left, rotation = placement
        pad = (left, w-side-left, top, h-side-top)
        support = torch.nn.functional.pad(torch.ones_like(patch), pad)
        value = torch.nn.functional.pad(patch.rot90(rotation, (-2,-1)), pad)
        return image*(1-support)+value
    def check():
        if deadline is not None and time.time() >= deadline:
            raise TimeoutError('Deadline in shared-patch optimization')
    def score(patch):
        total = 0.
        with torch.no_grad():
            for image, objective, placement in zip(backgrounds, objectives, placements):
                check()
                loss = objective(compose(image, patch, placement))
                if loss.ndim or not torch.isfinite(loss):
                    raise FloatingPointError('Invalid EOT objective')
                total += float(loss)/len(backgrounds)
        return total
    patch = torch.full_like(clean[..., :side, :side], .5)  # No evaluation-background initialization.
    baseline = best_loss = score(patch)
    best, trace = patch.clone(), []
    for step in range(config.steps):
        patch = patch.detach().requires_grad_(True)
        gradient = torch.zeros_like(patch)
        for image, objective, placement in zip(backgrounds, objectives, placements):
            check()
            loss = objective(compose(image, patch, placement))
            if loss.ndim or not torch.isfinite(loss):
                raise FloatingPointError('Invalid EOT objective')
            grad, = torch.autograd.grad(loss, patch)
            gradient.add_(grad/len(backgrounds))
        if not torch.isfinite(gradient).all() or gradient.abs().max()==0:
            raise FloatingPointError('Invalid EOT gradient')
        patch = (patch-config.alpha*gradient.sign()).clamp(0,1).detach()
        value = score(patch)
        trace.append(dict(step=step+1, objective=value))
        if value < best_loss:
            best, best_loss = patch.clone(), value
    delivered = compose(clean, best, (0,0,0)).detach()
    return delivered, dict(baseline_objective=baseline, best_objective=best_loss, trace=trace,
            optimization_backgrounds=len(backgrounds), transformation_draws=len(placements),
            effective_patch_fraction=float(mask.mean()), evaluation_placement='top_left')


def validate_manifest(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Private manifest must be a nonempty list')
    ids, groups = set(), {}
    for row in rows:
        for key in ('id', 'image', 'image_sha256', 'prompt', 'target', 'split', 'intent_group', 'image_group', 'track'):
            if not isinstance(row.get(key), str) or not row[key]:
                raise ValueError('Missing or invalid manifest field: ' + key)
        if row['id'] in ids or row['split'] not in {'optimization', 'development', 'evaluation'}:
            raise ValueError('Duplicate ID or unknown split')
        if row['track'] not in {'perception', 'integrity', 'safety'}:
            raise ValueError('Unknown track')
        ids.add(row['id'])
        for key in ('intent_group', 'image_group'):
            group = (key, row[key])
            if group in groups and groups[group] != row['split']:
                raise ValueError('Group leakage across splits')
            groups[group] = row['split']
        exact_image = ('image_sha256', row['image_sha256'])
        if exact_image in groups and groups[exact_image] != row['split']:
            raise ValueError('Identical image content crosses splits')
        groups[exact_image] = row['split']
        raw = Path(row['image']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['image_sha256']:
            raise ValueError('Image identity mismatch')
        if row['track'] == 'integrity' and 'injection_image' in row:
            expected = row.get('injection_sha256')
            if hashlib.sha256(Path(row['injection_image']).read_bytes()).hexdigest() != expected:
                raise ValueError('Injection image identity mismatch')
    return rows


def run_private(adapter, rows, config, out_dir, contract, deadline):
    """Paired generations, private artifacts, exact-resume keys; no automatic ASR."""
    from PIL import Image
    import numpy as np
    validate_manifest(rows)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if not any(part == 'audit_work' or 'PRIVATE' in part for part in out.parts):
        raise ValueError('Outputs must be in an explicitly private directory')
    config.validate()
    clock = out / 'clock_PRIVATE.json'
    if clock.exists():
        saved = json.loads(clock.read_text())
        if saved['contract'] != digest(contract):
            raise ValueError('Run directory belongs to a different contract')
        deadline = min(deadline, saved['deadline'])
    else:
        atomic_json(clock, dict(contract=digest(contract), deadline=deadline))
    counts = dict(completed=0, cached=0, cached_failed=0, failed=0, stopped=0)
    def generate_checked(image, text):
        if time.time() >= deadline:
            raise TimeoutError('Deadline before generation')
        return adapter.generate(image, text)

    for row in rows:
        if row['split'] != 'development':
            continue  # Reserved evaluation cannot be opened by this development runner.
        if time.time() >= deadline:
            counts['stopped'] += 1
            break
        identity = dict(contract=contract, row=row, attack=asdict(config), adapter=adapter.identity)
        key = digest(identity)
        dest = out / (key + '_PRIVATE.json')
        if dest.exists():
            cached = json.loads(dest.read_text())
            if cached.get('key') != key or cached.get('status') not in {'complete', 'failed'}:
                raise ValueError('Corrupt cache identity')
            if cached['status'] == 'complete':
                artifact = out / (key + '_PRIVATE.png')
                if cached.get('identity') != identity or not artifact.exists() or hashlib.sha256(artifact.read_bytes()).hexdigest() != cached['artifact_sha256']:
                    raise ValueError('Completed cache or artifact identity changed')
            counts['cached' if cached['status'] == 'complete' else 'cached_failed'] += 1
            continue
        start = time.monotonic()
        responses = {}
        try:
            clean = adapter.read_image(row['image'])
            parity = adapter.parity_check(clean, row['prompt'], row['target'])
            if time.time() >= deadline:
                raise TimeoutError('Deadline after parity gate')
            weights_before = adapter.frozen_fingerprint()
            defense = row.get('defense_prefix', '')
            if config.defense_aware and not defense:
                raise ValueError('Defense-aware optimization requires a fixed defense prefix')
            optimization_prompt = (defense if config.defense_aware else '') + row['prompt']
            target_loss = adapter.objective(clean, optimization_prompt, row['target'])
            if config.method != 'injection':
                initial = clean.clone().requires_grad_(True)
                grad, = torch.autograd.grad(target_loss(initial), initial)
                if not torch.isfinite(grad).all() or grad.abs().max() == 0:
                    raise FloatingPointError('Gradient gate failed')
                del initial, grad
            if config.method == 'injection':
                if not row.get('injection_image'):
                    raise ValueError('Injection artifact required')
                objectives = []
            elif config.method in {'universal', 'universal_patch', 'universal_eot', 'bimodal'}:
                corpus = [r for r in rows if r['split'] == 'optimization']
                if not corpus:
                    raise ValueError('Universal method requires separate optimization contexts')
                objectives = [adapter.objective(clean, (defense if config.defense_aware else '')+r['prompt'], r['target']) for r in corpus]
            elif config.method == 'feature':
                if 'feature_image' not in row or 'feature_sha256' not in row:
                    raise ValueError('Feature target artifact is required')
                if hashlib.sha256(Path(row['feature_image']).read_bytes()).hexdigest() != row['feature_sha256']:
                    raise ValueError('Feature target identity mismatch')
                objectives = [adapter.feature_objective(adapter.read_image(row['feature_image']))]
            elif config.method == 'prompt_match':
                if not row.get('teacher_prompt'):
                    raise ValueError('Private teacher_prompt required')
                objectives = [adapter.match_objective(clean, optimization_prompt, row['target'], row['teacher_prompt'])]
            else:
                objectives = [target_loss]
            if config.method == 'injection':
                attacked, metrics = clean.clone(), dict(gradient_optimization=False)
            elif config.method == 'universal_eot':
                backgrounds = [adapter.read_image(r['image']) for r in corpus]
                attacked, metrics = optimize_shared_patch(backgrounds, objectives, clean, config, deadline)
            else:
                attacked, metrics = optimize(clean, objectives, config, deadline)
            mask = patch_mask(clean, config.patch_fraction) if config.method in {'patch', 'universal_patch', 'universal_eot'} else None
            attacked = quantize_bounded(attacked, clean, config.epsilon, mask)
            artifact = out / (key + '_PRIVATE.png')
            arr = (attacked[0].permute(1, 2, 0).cpu().numpy() * 255).round().astype(np.uint8)
            tmp = artifact.with_suffix('.tmp')
            Image.fromarray(arr).save(tmp, format='PNG')
            os.replace(tmp, artifact)
            delivered = adapter.read_image(artifact)
            if (delivered - clean).abs().max() > config.epsilon + 1e-6:
                raise ValueError('Delivered artifact exceeds raw-pixel budget')
            if mask is not None and not torch.equal(delivered[mask == 0], clean[mask == 0]):
                raise ValueError('Delivered patch changed pixels outside mask')
            active_prompt = row['prompt']
            candidate_evaluations = 0
            if config.method == 'bimodal':
                candidates = row.get('candidate_prompts', [])
                if not candidates or len(candidates) > 8 or any(not isinstance(p, str) or not p for p in candidates):
                    raise ValueError('Bimodal adaptation needs 1..8 private candidate prompts')
                values = []
                with torch.no_grad():
                    for prompt in [row['prompt']] + candidates:
                        if time.time() >= deadline:
                            raise TimeoutError('Deadline during text candidate search')
                        values.append(float(adapter.objective(clean, (defense if config.defense_aware else '')+prompt, row['target'])(delivered)))
                active_prompt = ([row['prompt']] + candidates)[min(range(len(values)), key=values.__getitem__)]
                candidate_evaluations = len(values)
            responses = {}
            for name, image in [('clean', clean), ('attack', delivered)]:
                if time.time() >= deadline:
                    raise TimeoutError('Deadline before paired generation')
                responses[name] = generate_checked(image, row['prompt'])
            responses['text_only'] = generate_checked(None, row['prompt'])
            rng = torch.Generator(device=clean.device).manual_seed(config.seed)
            noise = (torch.rand(clean.shape, device=clean.device, dtype=clean.dtype, generator=rng)*2-1)*config.epsilon
            random_image = quantize_bounded((clean+noise).clamp(0,1), clean, config.epsilon)
            if mask is not None:
                random_image = torch.where(mask.bool(), random_image, clean)
            responses['random_control'] = generate_checked(random_image, row['prompt'])
            if active_prompt != row['prompt']:
                if time.time() >= deadline:
                    raise TimeoutError('Deadline before combined generation')
                responses['combined'] = generate_checked(delivered, active_prompt)
                responses['text_candidate_only'] = generate_checked(clean, active_prompt)
            if row.get('injection_image'):
                if time.time() >= deadline:
                    raise TimeoutError('Deadline before injection generation')
                injection = adapter.read_image(row['injection_image'])
                responses['injection'] = generate_checked(injection, row['prompt'])
            if row.get('defense_prefix'):
                if time.time() >= deadline:
                    raise TimeoutError('Deadline before defense generation')
                defended_image = injection if config.method == 'injection' else delivered
                responses['defended_attack'] = generate_checked(defended_image, row['defense_prefix'] + active_prompt)
                if time.time() >= deadline:
                    raise TimeoutError('Deadline before clean defense generation')
                responses['defended_clean'] = generate_checked(clean, row['defense_prefix'] + row['prompt'])
            if adapter.frozen_fingerprint() != weights_before:
                raise ValueError('Model weights changed during input optimization')
            atomic_json(dest, dict(key=key, status='complete', identity=identity, responses=responses,
                                  metrics=metrics, parity=parity, selected_prompt=active_prompt,
                                  candidate_evaluations=candidate_evaluations, elapsed_seconds=time.monotonic()-start,
                                  artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                                  delivered_linf=float((delivered-clean).abs().max())))
            counts['completed'] += 1
        except Exception as error:
            # Error messages can contain prompts: store only type and never print replies.
            atomic_json(dest, dict(key=key, status='failed', error_type=type(error).__name__,
                                  partial_responses=responses, elapsed_seconds=time.monotonic()-start))
            counts['failed'] += 1
            if isinstance(error, (TimeoutError, torch.OutOfMemoryError)) or 'device-side' in str(error):
                counts['stopped'] += 1
                break
    atomic_json(out / 'aggregate_status.json', dict(**counts, contract_hash=digest(contract),
                safety_labels='not_collected', claim_status='development_only', deadline=deadline))
    return counts
