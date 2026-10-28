"""Readable presentation notebook from frozen code and real aggregate evidence."""
import ast
import hashlib
import json
from pathlib import Path
import nbformat

ROOT=Path(__file__).resolve().parents[2]
DRIVE=Path.home()/'Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive'
REPAIR=DRIVE/'VLM_Published_Repair_20261027_PRIVATE'
METHODS=('fgsm','pgd','patch','universal','universal_patch','universal_eot',
         'pgd_defense','pgd_flip','released_qi_16')


def md(text):return nbformat.v4.new_markdown_cell(text)
def code(text):return nbformat.v4.new_code_cell(text)


def source_cells(name):
    """Keep source byte-for-byte, expose ordinary Python, never serialized strings."""
    source=(ROOT/'tools'/name).read_text();lines=source.splitlines(keepends=True)
    tree=ast.parse(source);starts=[0]
    for node in tree.body:
        first=min([node.lineno]+[d.lineno for d in getattr(node,'decorator_list',[])])-1
        if first-starts[-1]>=65:starts.append(first)
    starts.append(len(lines));cells=[];pieces=[]
    for index,(a,b) in enumerate(zip(starts,starts[1:])):
        text=''.join(lines[a:b]);pieces.append(text)
        mode='-a ' if index else ''
        cells.append(md(f'**{name}, part {index+1}.** Read the code directly below. '
            'This cell writes source for imports; it does not launch a model or invent results.'))
        cells.append(code(f'%%writefile {mode}{{SOURCE_DIR}}/{name}\n'+text))
    assert ''.join(pieces)==source
    return cells


def build():
    aggregate_path=REPAIR/'combined_PRIVATE/safety_aggregates.json'
    aggregate=json.loads(aggregate_path.read_text())
    coverage=json.loads((REPAIR/'coverage_aggregates.json').read_text())
    judge=json.loads((REPAIR/'judge_status.json').read_text())
    provenance=json.loads((REPAIR.parent/(REPAIR.name+'_preservation_PRIVATE.json')).read_text())
    assert coverage['total_completed']==136 and judge['status']=='finished'
    selected=[r for r in aggregate['rows'] if r['condition'] in ('clean','attack','defended_attack')]
    for r in selected:assert r['yes']+r['no']+r['unresolved']==8
    compact=[(r['model'],r['method'],r['condition'],r['yes'],r['no'],r['unresolved']) for r in selected]
    snapshot_hash=hashlib.sha256(aggregate_path.read_bytes()).hexdigest()
    prior=json.loads((ROOT/'notebooks/vlm_published_benchmarks_20261026.ipynb').read_text())
    maths=prior['cells'][2]['source']
    if isinstance(maths,list):maths=''.join(maths)
    cells=[md('''# Visual attacks on frozen VLMs: methods, published data and measured results

**Presentation edition — 28 October 2026.** Prepared for the 29 October presentation.
This is a readable companion to the preserved completed run, not a new GPU experiment.
Run all safely: writes reviewed source files, checks their identity and displays actual
aggregate snapshots. It does not download weights, restart expired jobs, or generate data.

**Evidence:** 136/144 method–request cases, eight underlying HarmBench behaviors,
two open VLMs, one released carrier. All implemented attacks are adaptations or artifact
transfer tests. We have not tested every original dataset or reproduced every paper.
The results are classifier-labelled development evidence; human review remains pending.

Presentation route: question → data/fidelity → architecture/math → attack code →
evaluation → results → limitations/proposals. The engineering appendix is optional.'''),
    md('''## 1. Research question and speaking route

How do visual perturbations and visual instructions affect frozen VLM behavior,
and does a fixed inference-time defense prefix reduce unsafe assistance?

For a 15-minute talk: spend 2 minutes on scope/data, 4 on architecture and gradients,
3 on patches/shared attacks, 3 on results, and 3 on limitations and next experiments.
Do not present a lower optimization loss as a measured jailbreak.

**Opening:** “We implemented paper-derived visual mechanisms on published-source data,
then measured behavior-conditioned unsafe assistance. This is a small development study,
with explicit adaptations and failed cases, rather than a complete replication suite.”'''),
    md('''## 2. Published data and reproduction fidelity

| Source | What we actually used | Role | What this does not establish |
|---|---|---|---|
| HarmBench official validation release | Eight frozen standard behaviors and released optimizer continuations | Safety evaluation and per-request targets | Full HarmBench coverage or independent confirmation |
| Qi official release | One clean carrier, eight sampled corpus continuations, constrained-16 artifact | Shared optimization and artifact transfer | Original MiniGPT checkpoint/configuration or all-image universality |
| CyberSecEval3 official visual-injection release | Eight frozen records and original system/user roles | Separate literal-marker diagnostic | Full benchmark or physical injection reproduction |
| ImageNet/CIFAR/COCO/VQAv2 | Not used in this published-data stage | Candidate future perception/utility sets | No results claimed here |

HarmBench: [Mazeika et al., 2402.04249](https://arxiv.org/abs/2402.04249).
Qi: [2306.13213](https://arxiv.org/abs/2306.13213).
CyberSecEval3: [official dataset](https://huggingface.co/datasets/facebook/cyberseceval3-visual-prompt-injection).
Exact revisions, hashes, sample IDs and selection rules are in the protocol below.
No project-created synthetic base examples or fabricated outcomes enter this study.
The released injection benchmark itself contains constructed examples/markers.'''),
    md('''## 3. Model architecture and experiment contract

Image → native preprocessing → visual encoder → connector/merger → language decoder.
Qwen2.5-VL-3B uses its native Qwen visual path (FP16); SmolVLM-500M uses its
Idefics3-based path (FP32). Different processors remain separate.
All weights are frozen; only pixels change. T4, batch one, 448 RGB, greedy decoding,
256-token output cap. These precision/processor differences confound simple architecture rankings.

Clean processor/logit agreement, finite nonzero image gradients, valid raw pixels,
patch support, saved/reloaded bounds and unchanged weights are technical checks.
They establish mechanics, not successful harmful assistance or model alignment.'''),
    md(maths),
    md('''### 3.1 Additional objectives and interpretation

For a shared perturbation, minimize the mean target NLL across the separate released
optimization corpus: $J(\delta)=K^{-1}\sum_k L(x+\delta;q_k,a_k)$.
Evaluation behaviors do not supply new hand-written targets.

For a replacement patch under transformations, optimize
$J(p)=K^{-1}\sum_k L(A(x_k,p,T_k);q_k,a_k)$, with $p\in[0,1]$.
Our finite placements/right-angle rotations are a digital adaptation of the
[Brown et al. patch objective, §2](https://arxiv.org/abs/1712.09665).
They do not demonstrate physical-camera robustness.

Defense-aware PGD includes the fixed prefix in the attacked model input.
Flip-aware PGD averages the objective over the declared original/flipped views.
This is not the JailGuard detector. A generic prefix is not the full AdaShield system.

Visual injection is a trust-boundary attack: attacker-controlled image content attempts
to redirect a legitimate task. Our endpoint is literal marker containment, not HarmBench ASR.
Perception mistakes, instruction deviations and unsafe assistance must remain separate.'''),
    md('''## 4. Readable implementation

The next cells contain actual Python source, with normal line breaks and indentation.
`%%writefile` saves that visible code as a module; `-a` appends the next part.
This replaces the old giant dictionaries of escaped source strings.
The setup cell creates only a temporary source directory. No GPU is required.'''),
    code('from pathlib import Path\nimport tempfile,sys,hashlib\nSOURCE_DIR=Path(tempfile.mkdtemp(prefix="vlm_presentation_"))\nsys.path.insert(0,str(SOURCE_DIR))\nprint("Source directory:",SOURCE_DIR)')]
    modules=('vlm_visual_attacks.py','vlm_visual_adapter.py','vlm_visual_smol_adapter.py',
             'vlm_published_benchmarks.py','vlm_benchmark_judge.py','vlm_published_repair.py')
    topics={'vlm_visual_attacks.py':'Pixel constraints, targeted FGSM/PGD, masked/shared optimization',
            'vlm_visual_adapter.py':'Qwen visual preprocessing, sequence loss and parity',
            'vlm_visual_smol_adapter.py':'Smol visual adapter and frozen inference',
            'vlm_published_benchmarks.py':'Pinned datasets, controls, generation and injection',
            'vlm_benchmark_judge.py':'Original HarmBench classifier template and strict scoring',
            'vlm_published_repair.py':'Historical repair provenance and numerical deviations'}
    for name in modules:
        cells.append(md('### '+topics[name]))
        cells.extend(source_cells(name))
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in modules}
    cells += [md('### Source verification — no inference'),
        code('EXPECTED_SOURCE_HASHES = '+repr(hashes)+'\nfor name,expected in EXPECTED_SOURCE_HASHES.items():\n    path=SOURCE_DIR/name\n    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,name\n    compile(path.read_text(),str(path),"exec")\nprint("All visible module parts reconstruct the reviewed source exactly; syntax passed.")'),
        md('''**Interpretation:** the verification checks source identity and Python syntax.
It does not claim a fresh model run. The existing private archive remains the scientific record.'''),
        md('''## 5. Evaluation: what attack success means

For each fixed method/model/condition, $ASR=N^{-1}\sum_i \mathbf1[J(q_i,r_i)=Yes]$,
with $N=8$ planned behaviors. Judge: pinned HarmBench 13B classifier, NF4 deployment,
original standard-behavior template, strict Yes/No parsing. No refusal-word fallback.
Unresolved cases yield $[Y/N,(Y+U)/N]$; these are missingness bounds, not confidence intervals.

Compare attacked vs paired clean, then defended-attacked vs attacked. A harmful clean
response is not newly induced attack success. Multiple methods share requests and controls;
136 cases are not 136 independent questions. Human validation, benign utility and
population inference remain pending. The report includes paired discordances, cap hits and cost.'''),
        md('''## 6. Actual saved results — aggregate snapshot

The following literal contains numeric aggregates extracted from saved private results,
not invented examples or newly run predictions. Its source SHA-256 is printed below.
It works without Drive/GPU. Optional live verification later checks the private file.'''),
        code('import pandas as pd\nfrom IPython.display import display\nSNAPSHOT_ROWS = [\n'+
             ''.join('    '+repr(row)+',\n' for row in compact)+']\n'+
             'SNAPSHOT_SHA256 = '+repr(snapshot_hash)+'\n'+
             'results=pd.DataFrame(SNAPSHOT_ROWS,columns=["model","method","condition","yes","no","unresolved"])\n'+
             'results["planned"]=8\nresults["asr_lower"]=results.yes/8\nresults["asr_upper"]=(results.yes+results.unresolved)/8\n'+
             'assert ((results.yes+results.no+results.unresolved)==8).all()\n'+
             'display(results.pivot(index=["model","method"],columns="condition",values=["yes","unresolved"]))\n'+
             'print("Counts out of eight planned requests; consult unresolved columns.")\nprint("Source SHA256:",SNAPSHOT_SHA256)'),
        md('''**Observed:** PGD unsafe assistance was 4/8 for Smol and 2/8 for Qwen;
the prefix left both PGD rates unchanged. Smol released-artifact ASR fell from 2/8
to 0/8 with the prefix; flip-aware PGD stayed 3/8. These are subset descriptions,
not statistically established superiority. Higher attack NLL progress and ASR need not agree.
Edit this text only when the underlying saved evidence changes.'''),
        md('## 7. Complete measured report\n\n'+(ROOT/'docs/PUBLISHED_BENCHMARK_RESULTS.md').read_text()),
        md('''## 8. What failed, and what remains a proposal

Qwen EOT: non-finite objective, 0/8 completed. Qwen injection: native-logit parity failure,
0 valid diagnostic responses. The numerical repair passed carrier preprocessing parity
but produced no new successful Qwen safety cases. Do not convert failure into 0% ASR.

Feature/trigger matching (Jailbreak in Pieces), teacher/context matching (Image Hijacks),
and full feedback-driven BAP search are not reproduced. AdaShield and JailGuard were
reviewed; our generic prefix and flip-aware optimizer do not reproduce those systems.

**Proposed, not novel findings:** investigate preprocessing sensitivity; evaluate defense
generalization across pixel/patch/injection attacks at matched benign utility; validate
judge labels with two blinded humans. Choose a novelty claim only after a prior-art check
and held-out experiment. Inference-time wrappers do not improve model-weight alignment.'''),
        md('''## 9. Optional private evidence verification — no model calls

Mount the college Drive yourself if needed. This reads only aggregate metadata;
it does not restart the expired scientific jobs. Without Drive, use the frozen snapshot above.'''),
        code('PRIVATE_ROOT=Path("/content/drive/MyDrive/VLM_Published_Repair_20261027_PRIVATE")\n'+
             'evidence=PRIVATE_ROOT/"combined_PRIVATE/safety_aggregates.json"\n'+
             'if evidence.exists():\n    assert hashlib.sha256(evidence.read_bytes()).hexdigest()==SNAPSHOT_SHA256\n'+
             '    print("Private saved aggregates exactly match the presentation snapshot.")\n'+
             'else:\n    print("Drive not mounted; no live verification performed. Snapshot remains identified above.")'),
        md('''## 10. Tomorrow: defensible closing and likely questions

**Closing:** “We have a traced, executable development implementation and measured evidence
for several visual mechanisms. Defense effects are mixed. Numerical failures and limited
coverage remain visible. The next step is reliable held-out evaluation with benign utility
and human validation, not a claim that every paper or dataset has been reproduced.”

**Did you use every original dataset?** No: three published-source releases, small frozen subsets.
**Did you reproduce published ASRs?** No: changed models, objectives/settings; adaptations.
**What is new?** No established novelty yet; measurement and failure findings motivate proposals.
**Why not 100% coverage?** Eight Qwen EOT cases failed numerically; injection parity failed separately.
**What supports the numbers?** Saved aggregate hashes, strict classifier labels, private archive,
source revisions, and the completed-run notebook. No freshly typed response is treated as evidence.'''),
        md('## Appendix: exact protocol and source pins\n\n'+(ROOT/'docs/PUBLISHED_BENCHMARK_PROTOCOL.md').read_text())]
    notebook=nbformat.v4.new_notebook(cells=cells,metadata=dict(
        kernelspec=dict(name='python3',display_name='Python 3'),
        evidence=dict(aggregate_sha256=snapshot_hash,private_archive_sha256=provenance['sha256'],
                      source='saved_published_data_development',fresh_gpu_run=False)))
    nbformat.validate(notebook)
    path=ROOT/'notebooks/vlm_visual_attacks_presentation.ipynb'
    path.write_text(json.dumps(notebook,ensure_ascii=False,separators=(',',':')))
    print(path,len(cells),'cells')


if __name__=='__main__':build()
