"""Generate the real VLM attack laboratory. Default Run all is offline CPU tests.

No model calls, installs, benchmark loads or Drive mounts during notebook generation.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'notebooks/vlm_visual_attack_lab.ipynb'

REGISTRY = [
    ('P01 FGSM', '1412.6572v3 §§3–4', 'fgsm', 'Implemented generative adaptation; not original classifier reproduction'),
    ('P02 PGD', '1706.06083v4 §2', 'pgd', 'Implemented constrained input optimizer; no adversarial training'),
    ('P03 Adversarial Patch', '1712.09665v2 §2 Eq.1', 'patch / universal_eot', 'Bounded local and shared replacement EOT mechanisms implemented; original distribution/model/physical reproduction pending'),
    ('P04 Vision-attack survey', '2410.23687v2 §7', 'taxonomy', 'Reading map, not an executable attack'),
    ('P05 Qi visual adversarial examples', '2306.13213v2 §3 Eq.1', 'universal', 'Corpus-NLL adaptation implemented; original model/corpus/5000-step reproduction pending'),
    ('P06 Jailbreak in Pieces', '2307.14539v2 §3.1 Eq.4', 'feature', 'Qwen visual-feature Adam adaptation; original CLIP joint-space triggers pending'),
    ('P07 Image Hijacks', '2309.00236v4 §2 Eq.1', 'prompt_match', 'Teacher-forced soft-target matching implemented; original context-set/SGD reproduction pending'),
    ('P08 BAP', '2406.04031v2 §4 Eqs.3–4', 'bimodal', 'Corpus image plus private candidate-text search implemented; original feedback/LLM generator pending'),
    ('P09 MMJ-Bench', 'AAAI 2025 DOI 10.1609/aaai.v39i26.34983', 'comparison protocol', 'Benchmark importer and exact published configurations pending'),
    ('P10 Physical Prompt Injection', '2601.17383v1 §§III–VI', 'injection', 'Real prebuilt image-artifact evaluation; physical generation/placement/camera tests pending'),
    ('P11 AdaShield', '2403.09513v1 §3', 'private defense_prefix', 'Static prompt comparison implemented; adaptive prompt-pool retrieval pending'),
    ('P12 JailGuard', '2312.10766v4 §4 Eqs.4–7', 'not implemented', 'Mathematics explained; original similarity encoder/mutators/detector not reproduced'),
]

CONFIG = '''
# Leave these false for reading and offline acceptance checks.
RUN_GPU = False
INSTALL_REVIEWED_DEPENDENCIES = False
MOUNT_DRIVE = False
COMPUTE_APPROVED = False
SCIENTIFIC_AMENDMENT_ACCEPTED = False
APPROVED_SCOPE_SHA256 = ''
MANIFEST_PATH = ''  # Private JSON list. Never paste benchmark text into this notebook.
OUT_DIR = ''  # New private run folder under mounted /content/drive/MyDrive/.
METHOD = 'pgd'  # Also: fgsm/patch/universal/universal_patch/universal_eot/feature/prompt_match/injection/bimodal
DEFENSE_AWARE = False  # Require a fixed private defense_prefix; unsupported for feature/injection.
MAX_WALL_MINUTES = 30  # Starts BEFORE install/load; do not reset on resume.
MAX_NEW_TOKENS = 256
RUN_ID = 'visual_development_v1'
'''

GATE = '''
import time
from pathlib import Path
from dataclasses import asdict
import hashlib
import json

config = visual_core.AttackConfig(method=METHOD, steps=1 if METHOD=='fgsm' else 10,
                                 epsilon=1 if METHOD=='universal_eot' else 8/255,
                                 defense_aware=DEFENSE_AWARE)
config.validate()
run_result = None
if RUN_GPU:
    if not COMPUTE_APPROVED or not SCIENTIFIC_AMENDMENT_ACCEPTED:
        raise RuntimeError('Review and accept the dated amendment and this compute scope first')
    if not MANIFEST_PATH or not OUT_DIR or not 1 <= MAX_WALL_MINUTES <= 30:
        raise ValueError('Private manifest/output and a 1..30 minute development budget required')
    manifest_bytes = Path(MANIFEST_PATH).read_bytes()
    rows = visual_core.validate_manifest(json.loads(manifest_bytes))
    scope = dict(run_id=RUN_ID, source_hashes=SOURCE_HASHES, method=asdict(config),
            manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(), max_minutes=MAX_WALL_MINUTES,
            model=visual_adapter.QwenAttackAdapter.MODEL,
            revision=visual_adapter.QwenAttackAdapter.REVISION, canvas=224, max_new=MAX_NEW_TOKENS)
    scope_hash = visual_core.digest(scope)
    if APPROVED_SCOPE_SHA256 != scope_hash:
        raise RuntimeError('Record this exact approved scope hash: ' + scope_hash)
    if not any(r['split']=='development' for r in rows):
        raise ValueError('No development rows; reserved evaluation is locked')
    if len([r for r in rows if r['split']=='development']) > 4:
        raise ValueError('First real stage capped at four development items')
    if len([r for r in rows if r['split']=='optimization']) > 8:
        raise ValueError('First real stage capped at eight optimization contexts')
    if not Path('/content/drive/MyDrive').is_dir():
        if not MOUNT_DRIVE:
            raise RuntimeError('Mount college Drive explicitly before starting the bounded run')
        from google.colab import drive
        drive.mount('/content/drive')  # Owner handles Google permission interaction.
    root = Path(OUT_DIR).resolve()
    base = Path('/content/drive/MyDrive').resolve()
    if base not in root.parents or 'PRIVATE' not in root.name:
        raise ValueError('Use a distinct PRIVATE output folder inside mounted college Drive')
    root.mkdir(parents=True, exist_ok=True)
    clock = root/'clock_PRIVATE.json'
    deadline = time.time() + MAX_WALL_MINUTES*60
    if clock.exists():
        state = json.loads(clock.read_text())
        if state['contract'] != scope_hash:
            raise ValueError('Output directory has a different experiment identity')
        deadline = min(deadline, state['deadline'])
    else:
        visual_core.atomic_json(clock, dict(contract=scope_hash, deadline=deadline))
    if time.time() >= deadline:
        raise TimeoutError('Original time budget expired; preserve partial outputs')
else:
    print('GPU OFF: no installations, Drive mounts, model downloads or inference.')
'''

INSTALL = '''
if RUN_GPU:
    import importlib.metadata
    import subprocess
    import sys
    if INSTALL_REVIEWED_DEPENDENCIES:
        if time.time() >= deadline:
            raise TimeoutError('Deadline before installation')
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet',
                        'transformers==4.57.1', 'Pillow==11.3.0'],
                        check=True, timeout=max(1, int(deadline-time.time())))
        if importlib.metadata.version('transformers') != '4.57.1':
            raise RuntimeError('Dependency installation did not select reviewed version')
    print('Dependency stage complete. If transformers was already imported, restart and resume; clock persists.')
'''

RUN = '''
if RUN_GPU:
    if time.time() >= deadline:
        raise TimeoutError('Deadline before model loading')
    # Model load may itself overrun a deadline; no new call begins after it.
    adapter = None
    try:
        print(visual_tests.run_architecture_check(visual_adapter))
        if time.time() >= deadline:
            raise TimeoutError('Deadline after native CPU architecture check')
        adapter = visual_adapter.QwenAttackAdapter(max_new=MAX_NEW_TOKENS)
        if time.time() >= deadline:
            raise TimeoutError('Deadline after model loading')
        run_result = visual_core.run_private(adapter, rows, config, root, scope, deadline)
        print(run_result)  # Counts only. Responses and artifacts stay private.
    except Exception as error:
        visual_core.atomic_json(root/'startup_status_PRIVATE.json',
                dict(status='stopped', error_type=type(error).__name__, scope_sha256=scope_hash))
        print('Stopped:', type(error).__name__, 'See private status; no automatic retries.')
    finally:
        if adapter is not None:
            adapter.close()
else:
    print('Real model run not started. Offline adapter/runner checks are above.')
'''


def build(output=OUTPUT, execute=False):
    sources = {name:(ROOT/path).read_text() for name,path in dict(
        visual_core='tools/vlm_visual_attacks.py',
        visual_adapter='tools/vlm_visual_adapter.py',
        visual_tests='tools/nb_gen/e2e/e2e_visual_attacks.py').items()}
    hashes = {name:hashlib.sha256(source.encode()).hexdigest() for name,source in sources.items()}
    hashes['analysis_plan'] = hashlib.sha256((ROOT/'docs/ANALYSIS_PLAN_MODALITY_SAFETY.md').read_bytes()).hexdigest()
    cells = []

    def add(kind, text):
        text = textwrap.dedent(text).strip()+'\n'
        if kind=='code':
            ast.parse(text)
        cell = dict(cell_type=kind,id=f'lab-{len(cells):03d}',metadata={},source=text)
        if kind=='code':
            cell.update(execution_count=None,outputs=[])
        cells.append(cell)

    def explain(text):
        add('markdown','### Readout — editable\n\n'+text)

    add('markdown', '''# Real visual attacks on VLMs: evidence and experiment laboratory
    **October 25, 2026 — implementation, not a completed study.**

    This notebook embeds real input optimizers, a differentiable Qwen2.5-VL adapter and
    a private paired-generation runner. Unlike the teaching notebook, it can load and attack
    a pretrained VLM when explicitly enabled with private data and an accepted compute scope.
    Default Run all is CPU acceptance checks. No paper reproduction or novel claim is established.
    All implemented paper-derived methods are adaptations unless independently verified otherwise.
    ''')
    add('code', CONFIG)
    explain('GPU is off. Keep earlier completed notebooks intact. Use a new dated run folder; '
            'save actual code and outputs plus the numeric status snapshot before changing methods.')
    table='| Paper | Checked mathematical source | Entry point | Coverage |\n|---|---|---|---|\n'
    table+='\n'.join('| '+' | '.join(row)+' |' for row in REGISTRY)
    add('markdown','## 1. What is already present — paper coverage\n\n'+table+'\n\n'
        'P01–P12 refer to the source-linked dossier embedded below. “Implemented” means code exists; '
        'it does not mean GPU validated or faithful reproduction. Surveys and benchmarks are not individual attacks. '
        'No full AdaShield-A or JailGuard reproduction is claimed.')
    add('markdown',r'''## 2. Mathematical specification
    Let $f_\theta(x,t)$ be the fixed VLM, $x\in[0,1]^{3\times224\times224}$ the delivered attack canvas,
    $t$ the fixed user text, and $y^*$ a private target continuation.
    $L_{NLL}(x,t,y^*)=-\frac1{|y^*|}\sum_j\log p_\theta(y_j^*\mid x,t,y^*_{<j})$.
    Image, prompt and padding tokens do not contribute; causal prediction is shifted exactly once.

    **FGSM:** $x'=\Pi_{\mathcal C}(x-\epsilon\,sign(\nabla_x L_{NLL}))$ for targeted minimization.
    **PGD:** repeat $x_{k+1}=\Pi_{\mathcal C}(x_k-\alpha\,sign(\nabla L))$.
    Here $\mathcal C=[0,1]^d\cap B_\infty(x,\epsilon)$. Untargeted true-label maximization
    has the opposite sign; this real runner uses targeted generation loss, not classifier accuracy.

    **Localized patch:** $x'=(1-A)x+A p$, with a fixed binary top-left mask $A$;
    constrain $p$ to the original patch's epsilon interval. Record measured area.
    **Corpus image:** minimize the mean NLL over separate optimization contexts, one image shared across contexts.
    **Universal patch adaptation:** same shared context objective with a patch mask. It does not yet
    sample new background images, placements and rotations as Brown Eq.1 does.
    **Replacement EOT patch (`universal_eot`):** optimize one shared $p\in[0,1]$ across separate
    optimization backgrounds, seeded translations and right-angle rotations; deploy on a held-out background.
    This uses a box-only replacement threat model (`epsilon=1` inside the patch), not an imperceptible
    full-image budget. The small fixed transformation sample is recorded, not a physical camera simulation.

    **Feature matching:** $\min_{x'\in\mathcal C}\|V_\theta(x')-V_\theta(x_{target})\|_2^2$ via Adam.
    Current $V$ is Qwen's merged visual features, not original CLIP's joint embedding space.
    **Behavior matching:** minimize $-\sum_j q_j^T\log p_j(x',t)$ under the same teacher-forced
    continuation, with detached teacher distributions produced using a private teacher prompt.
    Full prompt-matching context generation in Image Hijacks remains to reproduce.

    **Bimodal adaptation:** first optimize the corpus image, then choose among 1–8 private text candidates
    by target NLL on development only. Save image-only, text-only and combined outputs. This does not
    reproduce BAP's feedback-driven ChatGPT candidate generation.
    **Injection:** evaluate a prebuilt instruction-bearing image against its paired clean image and fixed task.
    No gradient is required. Physical realism and placement optimization are not established.

    **Defenses:** compare private fixed-prefix generations on clean and attacked inputs. Optional flip-pair
    loss averaging implements a small EOT example, not a universal defense. JailGuard's mathematical
    pipeline is $S_{ij}=cos(v_i,v_j)$, $Q_i=S_i/\|S_i\|_1$, $D_{ij}=KL(Q_i\|Q_j)$;
    its published encoder, policy, thresholds and refusal handling still need implementation.
    ''')
    add('markdown','## 3. Embedded implementation — review before enabling GPU\n\n'
        'All source hashes participate in the exact run identity. Raw media/text remain in private files. '
        'Image loading defines a 224-pixel square canvas before optimization; conclusions do not extend '
        'to perturbation budgets at the original source resolution.')
    add('code',f'SOURCE_HASHES = {hashes!r}\nimport sys, types\n')
    for name,source in sources.items():
        # Literal newlines keep embedded implementation reviewable in the editor.
        if "'''" in source:
            raise ValueError('Source delimiter needs review')
        add('code',f"{name}_SOURCE = r'''\n{source}'''\n"
            f'{name} = types.ModuleType({name!r})\nsys.modules[{name!r}] = {name}\n'
            f'exec(compile({name}_SOURCE, {name!r}, "exec"), {name}.__dict__)\n')
    add('code','CPU_CHECKS = visual_tests.run_cpu_checks(visual_core, visual_adapter)\nprint(CPU_CHECKS)')
    explain('These acceptance tests use analytic objectives and a fake adapter, never a pretrained VLM. '
            'They cover all runner paths, saved bounds, target masking, group leakage, identity, deadlines, '
            'failure caches and numeric-only summaries. These CPU tests alone do not establish T4 fit; '
            'the dossier separately records the single synthetic pretrained PGD profile.')
    add('markdown','## 4. Private data contract\n\n'
        'MANIFEST_PATH points to a private JSON list. Required row fields: '
        '`id,image,image_sha256,prompt,target,split,intent_group,image_group,track`. '
        'Splits: `optimization/development/evaluation`; tracks: `perception/integrity/safety`. '
        'No template embeds actual prompts or replies. For injection add `injection_image,injection_sha256`; '
        'feature matching uses `feature_image,feature_sha256`; behavior matching uses `teacher_prompt`; '
        'bimodal search uses `candidate_prompts`; static defense uses `defense_prefix`. '
        'Paths are absolute private runtime paths. Group by underlying image and intent across all variants. '
        'The first runner processes at most four development rows and never opens reserved evaluation outcomes. '
        'Universal optimization requires separate optimization rows. Artifact and group checks run before loading weights.')
    add('code', GATE)
    explain('The source/plan/manifest/config hash is the exact scope to review. Set it only after scope approval. '
            'The persisted deadline includes installations and downloads; a resumed run cannot reset it. '
            'Do not delete a previous clock or repurpose its folder to extend a stage.')
    add('code', INSTALL)
    explain('No installation occurs with GPU off. The real adapter refuses unreviewed Transformers versions. '
            'Restart if an old version was already imported; outputs and the deadline stay on Drive.')
    add('code', RUN)
    explain('Read counts only here. Actual responses, delivered PNGs, token IDs, parity errors and optimization '
            'traces are stored privately. Failed or timed-out conditions are explicit and not automatically retried. '
            'Paired text-only and random-noise/patch controls are also saved. '
            'NLL improvement is not jailbreak success. No automated guard rate is invented.')
    add('markdown',r'''## 5. Evaluation and claims gate
    Evaluate three distinct outcomes: perceptual error, instruction deviation and unsafe assistance.
    Human reviewers see actual images/tasks; blind model, attack, defense and automatic labels.
    For $N$ attempted cases, $H$ resolved unsafe and $M$ unresolved, report $H/N$, $M/N$ and
    $[H/N,(H+M)/N]$ bounds. Refusal, comprehension and cap hits remain separate.
    The private runner currently collects responses and status, not final human scores or inferential ASR.
    Reserved evaluation, weighted dual-review analysis and a full benchmark importer remain pending.

    Before any novel claim: verify the closest papers/configurations, reproduce a baseline, freeze
    data/estimands/compute, then evaluate held-out outcomes. Candidate studies:
    1. Does saved-image/preprocessing variation change transfer at the same delivered budget?
    2. Do defenses generalize across pixel/patch/injection at matched benign utility and query cost?
    3. Does a carefully measured reproduction change an existing conclusion?
    For each write the closest prior art, falsifiable prediction, primary outcome, controls,
    failure criterion and held-out test. None is currently a novel finding.
    ''')
    dossier=(ROOT/'docs/VISUAL_ATTACKS_RESEARCH_DOSSIER.md').read_text()
    add('markdown','## 6. Source-linked reading register and evidence limits\n\n'+dossier)
    notebook=dict(nbformat=4,nbformat_minor=5,cells=cells,metadata=dict(
        kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python')))
    import nbformat
    nbformat.validate(nbformat.from_dict(notebook))
    if execute:
        import contextlib
        import io
        namespace={'__name__':'notebook'}
        count=0
        for cell in cells:
            if cell['cell_type']!='code':
                continue
            count+=1
            stdout,stderr=io.StringIO(),io.StringIO()
            with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
                exec(compile(cell['source'],cell['id'],'exec'),namespace)
            cell['execution_count']=count
            for name,stream in [('stdout',stdout),('stderr',stderr)]:
                if stream.getvalue():
                    cell['outputs'].append(dict(output_type='stream',name=name,text=stream.getvalue()))
        nbformat.validate(nbformat.from_dict(notebook))
    output=Path(output)
    payload='{"cells":[\n'+',\n'.join(json.dumps(c,ensure_ascii=False) for c in cells)
    payload+='\n],"metadata":'+json.dumps(notebook['metadata'])+',"nbformat":4,"nbformat_minor":5}\n'
    output.write_text(payload)
    print(f'Generated {len(cells)} cells: {output}; offline execution={execute}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--output',type=Path,default=OUTPUT)
    args=parser.parse_args()
    build(args.output,args.execute)
