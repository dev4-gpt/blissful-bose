"""Generate the portable CPU teaching notebook; no datasets, network or VLM calls.

Usage: python3 tools/nb_gen/make_visual_attacks_nb.py --execute
Tests of mathematical mechanics live in the generated notebook, not an experiment runner.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[2]
DOSSIER = ROOT / 'docs/VISUAL_ATTACKS_RESEARCH_DOSSIER.md'
OUTPUT = ROOT / 'notebooks/vlm_visual_attacks_teaching.ipynb'

SETUP = '''
import math
import torch
import torch.nn.functional as F

torch.set_num_threads(1)
DTYPE = torch.float64
DEVICE = torch.device('cpu')
SEED = 20261024
assert not torch.empty(0, device=DEVICE).is_cuda
print('CPU toy mechanics only. No VLM, data download, Drive mount or GPU branch.')

class FrozenMean(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.scale = torch.nn.Parameter(torch.tensor(10., dtype=DTYPE), requires_grad=False)

    def forward(self, pixels):
        score = self.scale * (pixels.mean(dim=(1, 2, 3)) - .5)
        return torch.stack((score, -score), dim=1)

model = FrozenMean().eval()
x = torch.full((1, 3, 8, 8), .55, dtype=DTYPE, device=DEVICE)
true_y = torch.tensor([0])
target_y = torch.tensor([1])
weights_before = {k: v.clone() for k, v in model.state_dict().items()}
print('Clean toy class:', model(x).argmax(1).item())
'''

ATTACKS = '''
def validate(x0, epsilon, steps, alpha, mask):
    if x0.device.type != 'cpu' or x0.ndim != 4 or not x0.is_floating_point():
        raise ValueError('Teaching API expects a CPU floating NCHW tensor')
    if not torch.isfinite(x0).all() or x0.min() < 0 or x0.max() > 1:
        raise ValueError('Raw pixels must be finite and in [0,1]')
    if not math.isfinite(epsilon) or not 0 <= epsilon <= 1:
        raise ValueError('Invalid raw-pixel epsilon')
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ValueError('Positive integer step count required')
    if not math.isfinite(alpha) or alpha < 0:
        raise ValueError('Invalid step size')
    if mask.shape != x0.shape or mask.device != x0.device:
        raise ValueError('Mask must match input shape/device')
    if not torch.all((mask == 0) | (mask == 1)):
        raise ValueError('Mask must be binary')

def project(candidate, clean, epsilon, mask):
    # Box intersection first, then exact restoration outside local support.
    lo = torch.clamp(clean - epsilon, min=0.)
    hi = torch.clamp(clean + epsilon, max=1.)
    bounded = torch.maximum(lo, torch.minimum(hi, candidate))
    return torch.where(mask.bool(), bounded, clean).detach()

def pixel_attack(forward, clean, labels, *, epsilon, steps=1, alpha=None,
                 targeted=False, mask=None, random_start=False, seed=SEED):
    # A teaching optimizer, deliberately NOT a production VLM interface.
    clean = clean.detach().clone()
    mask = torch.ones_like(clean) if mask is None else mask.detach().clone()
    alpha = epsilon if alpha is None else alpha
    validate(clean, epsilon, steps, alpha, mask)
    current = clean.clone()
    if random_start:
        rng = torch.Generator(device='cpu').manual_seed(seed)
        noise = torch.rand(clean.shape, generator=rng, dtype=clean.dtype) * 2 - 1
        current = project(clean + epsilon * noise, clean, epsilon, mask)
    for _ in range(steps):
        current = current.detach().requires_grad_(True)
        loss = F.cross_entropy(forward(current), labels)
        grad, = torch.autograd.grad(loss, current)
        if not torch.isfinite(grad).all():
            raise FloatingPointError('Nonfinite input gradient')
        direction = -1 if targeted else 1
        current = project(current + direction * alpha * grad.sign(), clean, epsilon, mask)
    return current

fgsm = pixel_attack(model, x, true_y, epsilon=.1)
pgd = pixel_attack(model, x, true_y, epsilon=.1, steps=10, alpha=.02,
                   random_start=True)
targeted = pixel_attack(model, x, target_y, epsilon=.1, steps=10, alpha=.02,
                        targeted=True)
mask = torch.zeros_like(x)
mask[:, :, :4, :4] = 1
patch = pixel_attack(model, x, target_y, epsilon=.25, steps=10, alpha=.05,
                    targeted=True, mask=mask)
print('Toy classes:', {k: model(v).argmax(1).item() for k, v in
      [('clean', x), ('FGSM', fgsm), ('PGD', pgd), ('targeted', targeted), ('patch', patch)]})
print('Patch area fraction:', mask.mean().item())
'''

CHECKS = '''
# Finite-difference check uses a single coordinate of the raw input.
probe = x.clone().requires_grad_(True)
grad, = torch.autograd.grad(F.cross_entropy(model(probe), true_y), probe)
plus, minus = x.clone(), x.clone()
h = 1e-5
plus[0, 0, 0, 0] += h
minus[0, 0, 0, 0] -= h
fd = (F.cross_entropy(model(plus), true_y) - F.cross_entropy(model(minus), true_y)) / (2*h)
assert torch.allclose(grad[0, 0, 0, 0], fd, atol=1e-8, rtol=1e-5)
assert torch.isfinite(grad).all() and grad.abs().max() > 0

for value, budget in [(fgsm, .1), (pgd, .1), (targeted, .1), (patch, .25)]:
    assert value.min() >= 0 and value.max() <= 1
    assert (value - x).abs().max() <= budget + 1e-12
assert torch.equal(patch[mask == 0], x[mask == 0])
assert F.cross_entropy(model(fgsm), true_y) > F.cross_entropy(model(x), true_y)
assert F.cross_entropy(model(targeted), target_y) < F.cross_entropy(model(x), target_y)
assert model(targeted).argmax(1).item() == target_y.item()
assert model(patch).argmax(1).item() == target_y.item()
assert torch.equal(pgd, pixel_attack(model, x, true_y, epsilon=.1, steps=10,
                                    alpha=.02, random_start=True))
assert torch.equal(x, pixel_attack(model, x, true_y, epsilon=0.))
assert torch.equal(x, pixel_attack(model, x, true_y, epsilon=.1, mask=torch.zeros_like(x)))
edge = torch.zeros_like(x)
edge[:, :, :, 4:] = 1
edge_adv = pixel_attack(model, edge, true_y, epsilon=.1)
assert edge_adv.min() >= 0 and edge_adv.max() <= 1
assert (edge_adv - edge).abs().max() <= .1 + 1e-12
assert torch.equal(model.scale.detach(), weights_before['scale'])
assert model.scale.grad is None

invalid = [dict(epsilon=-.1), dict(epsilon=float('nan')), dict(epsilon=.1, steps=0),
           dict(epsilon=.1, alpha=float('inf')), dict(epsilon=.1, mask=mask+.5)]
for kwargs in invalid:
    try:
        pixel_attack(model, x, true_y, **kwargs)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid configuration accepted')
try:
    pixel_attack(lambda z: model(z) * float('nan'), x, true_y, epsilon=.1)
except FloatingPointError:
    pass
else:
    raise AssertionError('Nonfinite gradient accepted')
print('Passed: finite differences, objective direction, bounds, patch support, seeds,')
print('zero budget/mask, boundary pixels, frozen weights, invalid input and NaN rejection.')
'''

NORMALIZATION = '''
sigma = torch.tensor([.229, .224, .225], dtype=DTYPE)
print('Raw bounds implied by normalized epsilon=.02:', (.02 * sigma).tolist())
# Quantization can slightly exceed a continuous budget: validate the actual artifact.
artifact_epsilon = .02
continuous = torch.tensor([.5 + artifact_epsilon], dtype=DTYPE)
reloaded = torch.round(continuous * 255).to(torch.uint8).to(DTYPE) / 255
effective = (reloaded - .5).abs().item()
print('8-bit roundtrip effective raw budget:', effective)
print('Inside declared .02 budget:', effective <= artifact_epsilon)
assert effective > artifact_epsilon  # This example catches naive roundtrip drift.
# Quantize inside the permitted integer interval for an exactly representable artifact.
lo = math.ceil((.5 - artifact_epsilon) * 255)
hi = math.floor((.5 + artifact_epsilon) * 255)
saved = torch.clamp(torch.round(continuous * 255), min=lo, max=hi)
restored = saved.to(torch.uint8).to(DTYPE) / 255
assert (restored - .5).abs().max() <= artifact_epsilon + 1e-12
print('Constrained integer artifact passes; repeat after actual resize/normalization.')
'''

SEQUENCE = '''
# Harmless numeric tokens: target loss is over response positions only.
logits = torch.tensor([[[2., 0., -1.], [0., 2., -1.], [-1., 0., 2.]]], dtype=DTYPE)
labels = torch.tensor([[-100, 1, 2]])
masked = F.cross_entropy(logits.reshape(-1, 3), labels.reshape(-1), ignore_index=-100)
response_only = F.cross_entropy(logits[:, 1:].reshape(-1, 3), labels[:, 1:].reshape(-1))
assert torch.allclose(masked, response_only)
print('Toy response-only cross entropy:', masked.item())
# Here logits are already aligned to predicted targets. An actual causal LM must
# shift labels/logits once and account for its image-token expansion.

# Differentiable transformation averaging (horizontal flip), NOT a reproduced defense.
eot_input = x.clone().requires_grad_(True)
losses = [F.cross_entropy(model(view), true_y) for view in
          [eot_input, torch.flip(eot_input, dims=(-1,))]]
eot_grad, = torch.autograd.grad(torch.stack(losses).mean(), eot_input)
assert torch.isfinite(eot_grad).all() and eot_grad.abs().max() > 0
print('Toy transformation-averaged gradient is finite and nonzero.')
'''

EVALUATION = '''
# Synthetic outcomes, not collected model responses or human annotations.
attempted, confirmed_unsafe, unresolved = 10, 2, 3
lower = confirmed_unsafe / attempted
upper = (confirmed_unsafe + unresolved) / attempted
resolved_only = confirmed_unsafe / (attempted - unresolved)
assert lower <= resolved_only <= upper
print({'synthetic_confirmed_fraction': lower, 'missing_fraction': unresolved/attempted,
       'unsafe_bounds': [lower, upper], 'resolved_only': resolved_only})

# Symbolic trust-boundary demo: no image, OCR engine or language model is used.
def symbolic_policy(user_action, visual_action, trust_visual=False):
    return visual_action if trust_visual else user_action

assert symbolic_policy('count', 'redirect') == 'count'
assert symbolic_policy('count', 'redirect', True) == 'redirect'
print('Symbolic demonstration distinguishes user authority from visual data.')
print('This is not evidence that any defense protects a real VLM.')
'''


def build(execute=False, output=OUTPUT):
    dossier = DOSSIER.read_text()
    cells = []

    def add(kind, source):
        source = textwrap.dedent(source).strip() + '\n'
        if kind == 'code':
            ast.parse(source)
        cell = dict(cell_type=kind, id=f'visual-{len(cells):03d}', metadata={}, source=source)
        if kind == 'code':
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)

    def explanation(source):
        add('markdown', '### Interpretation — editable\n\n' + source)

    add('markdown', r'''# Visual attacks on VLMs: mathematics and evidence
    **October 24, 2026 | CPU teaching edition | no scientific model runs**

    Run all uses PyTorch on CPU with a frozen analytic toy model. No installation,
    network call, data fetch, Drive mount or secret is required. This notebook embeds
    the dossier for portable reading. It does not implement a runnable VLM jailbreak suite.
    ''')
    add('markdown', r'''## 1. From image to generated answer
    Raw image $x$ → preprocessing $P$ → visual encoder $V$ → connector $C$ → language model $M$.
    The model distribution is $p_\theta(y\mid x,t)$, with fixed weights $\theta$ and text $t$.
    Classifier cross entropy $L=-\log p(y_{true}\mid x)$ is not an unsafe-answer score.
    A targeted generation surrogate is $-\sum_j\log p_\theta(y_j^*\mid x,t,y^*_{<j})$.
    Target likelihood must still be checked against actual generated behavior.
    See Qi et al. §3/Eq.1 and Image Hijacks §2/Eq.1 in the reading register below.
    ''')
    add('code', SETUP)
    explanation('The toy model classifies mean pixel brightness. Its fixed weights provide exact '
                'gradient checks. A class change here establishes only a toy perception failure.')
    add('markdown', r'''## 2. FGSM, PGD and localized patch mathematics
    For raw pixels $x\in[0,1]^d$, let $\mathcal C=[0,1]^d\cap B_\infty(x,\epsilon)$.
    First-order expansion gives $L(x+\delta)\approx L(x)+\nabla_xL^\top\delta$;
    maximizing over $|\delta_i|\le\epsilon$ yields $\delta_i=\epsilon\,\mathrm{sign}(\partial_iL)$.
    FGSM takes one step and projects to $\mathcal C$.
    PGD repeats $x_{k+1}=\Pi_{\mathcal C}(x_k+\alpha\,\mathrm{sign}(\nabla_{x_k}L))$.
    Targeted attacks minimize target loss, so replace plus with minus.
    A binary support mask $A$ yields $x'=x+A\odot\delta$ for bounded local changes.
    A replacement patch instead uses $x'=(1-A)\odot x+A\odot p$.
    Goodfellow §§3–4; Madry §2; Brown §2/Eq.1 are the original reading sources.
    ''')
    add('code', ATTACKS)
    explanation('All three methods from DL_final are demonstrated as CPU mechanics. '
                'PGD and FGSM can tie on this linear toy; that is not a comparative VLM result. '
                'The localized patch is per-image, not a universal Brown patch.')
    add('code', CHECKS)
    explanation('Assertions check numerical gradients and attack directions, not just function output. '
                'Passing these tests does not establish gradients through a real VLM processor.')
    add('markdown', r'''## 3. Scaling and saved-image validity
    With $z=(x-\mu)/\sigma$, $\delta_x=\sigma\delta_z$.
    An epsilon specified after normalization changes its meaning by channel.
    Quantization and resizing are part of the threat model; validate the delivered artifact.
    Brown §2 and Image Hijacks §2 explicitly motivate artifact and transformation checks.
    ''')
    add('code', NORMALIZATION)
    explanation('The example measures quantization rather than assuming it preserves an inequality. '
                'A valid raw artifact can still be changed by model-specific preprocessing.')
    add('markdown', r'''## 4. Generative loss and transformation averaging
    Teacher forcing scores known target response tokens; it does not differentiate through greedy sampling.
    Mask prompt, image and padding positions. Causal alignment must shift exactly once.
    Universal patches minimize expected target loss across development images and transformations;
    per-example optimization does not establish universality. EOT differentiates an average of losses,
    $\nabla_x\mathbb E_T L(f(T(x)))$, approximated by sampled transforms.
    Brown §2/Eq.1; Image Hijacks §2; Qi §3 provide distinct constructions, not one shared attack.
    ''')
    add('code', SEQUENCE)
    explanation('Numeric vocabulary IDs illustrate response-only loss masking. '
                'A real adapter needs model-specific token expansion and reference-logit parity. '
                'The flip-invariant toy does not demonstrate robustness to transformations.')
    add('markdown', '## 5. Evaluation and visual prompt injection\n\n'
        'Perception error, instruction deviation and harmful assistance need distinct labels. '
        'Injection requires a legitimate user task and lower-trust content; it can be readable text '
        'inside a scene without pixel optimization. No benchmark injection content is embedded here.')
    add('code', EVALUATION)
    explanation('Missing cases produce an interval, not automatic safe labels. '
                'The symbolic policy is an explanatory analogy, not a visual injection reproduction. '
                'Two independent humans must inspect task and image where scoring requires them.')
    add('markdown', '## 6. Portable dossier and research register\n\n'
        f'Dossier SHA256: `{hashlib.sha256(dossier.encode()).hexdigest()}`. '
        'Inspection status and execution gates below apply to every experiment proposal.')
    for section in dossier.split('\n## ')[1:]:
        add('markdown', '## ' + section)
    add('markdown', '## Acceptance and next step\n\n'
        'CPU assertions pass only when all code cells execute. Scientific runs remain gated by '
        'the accepted amendment, reviewed data and an approved bounded compute profile. '
        'No toy outcome is a VLM safety result. Rebuild with '
        '`python3 tools/nb_gen/make_visual_attacks_nb.py --execute`.')
    nb = dict(nbformat=4, nbformat_minor=5, cells=cells, metadata=dict(
        kernelspec=dict(display_name='Python 3', language='python', name='python3'),
        language_info=dict(name='python', version='3.11.6')))
    import nbformat
    nbformat.validate(nbformat.from_dict(nb))
    if execute:
        # Trusted generated Python cells only; no Jupyter sockets needed in sandbox.
        import contextlib
        import io
        namespace = {'__name__': '__main__'}
        count = 0
        for cell in cells:
            if cell['cell_type'] != 'code':
                continue
            count += 1
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exec(compile(cell['source'], cell['id'], 'exec'), namespace)
            cell['execution_count'] = count
            for name, stream in [('stdout', stdout), ('stderr', stderr)]:
                if stream.getvalue():
                    cell['outputs'].append(dict(output_type='stream', name=name, text=stream.getvalue()))
        nbformat.validate(nbformat.from_dict(nb))
    # One JSON cell per physical line keeps the generated notebook below 500 lines.
    payload = '{"cells":[\n' + ',\n'.join(json.dumps(c, ensure_ascii=False) for c in nb['cells'])
    payload += '\n],"metadata":' + json.dumps(nb['metadata']) + ',"nbformat":4,"nbformat_minor":5}\n'
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text(payload)
    temporary.replace(output)
    print(f'Wrote {len(cells)} cells to {output}; CPU executed={execute}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.execute, args.output)
