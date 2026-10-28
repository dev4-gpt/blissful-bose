"""Create native-paper protocol notebook; original-run claims stay unexecuted."""
import json
from pathlib import Path
import sys
import nbformat

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from vlm_paper_protocols import PAPERS  # noqa: E402

CARDS={
'fgsm':r'''**Objective:** maximize a classification loss under an infinity-norm bound:
$\delta^*=\epsilon\,\mathrm{sign}(\nabla_x\ell(f(x),y))$ from a first-order approximation.
Here $x$ is the original pixel tensor, $y$ its class label and $\epsilon$ the declared scale.
The original classification setup is not a generative VLM safety experiment.
Recover its actual trained checkpoint and preprocessing before reproducing a table.
Targeted token-NLL minimization changes the task and reverses the update sign.''',
'pgd':r'''**Objective:** the inner maximization
$\max_{\delta\in S}\ell(f_\theta(x+\delta),y)$, with fixed weights for attack evaluation.
The update is $x_{t+1}=\Pi_{[0,1]\cap B_\infty(x,\epsilon)}
(x_t+\alpha\,\mathrm{sign}(\nabla\ell))$ when pixels use that scale.
The paper's outer weight-minimization is excluded by our no-training scope.
Select a particular original checkpoint/configuration; do not merge the MNIST and
CIFAR challenge defaults or assume a release config is every paper-table attack.''',
'patch':r'''**Objective:** $\max_p\mathbb E_{x,t,l}\log P(\hat y\mid A(p,x,l,t))$.
$p$ is the shared replacement patch, $x$ a background, $t$ its transformation and $l$
the placement. The classifier target $\hat y$ is fixed. Training and evaluation
backgrounds/distributions must match the chosen original experiment. A bounded,
per-image square at one location is not this complete universal/physical procedure.''',
'qi':r'''**Objective:** minimize corpus sequence NLL
$J(x')=-\sum_j\log p_\theta(a_j\mid x',\varnothing)$ under the selected image bound.
$a_j$ are **released** corpus entries, not newly generated continuations.
Native route: original MiniGPT-4/Vicuna checkpoint → original processor → corpus sampling
→ constrained/unconstrained optimization → native manual/toxicity evaluation.
Do not replace native evaluation with eight HarmBench questions and call the result faithful.
The inspected entrypoint and inclusive update loop, rather than a flag's apparent name,
determine actual iteration count. Exact source references are in the audit below.''',
'pieces':r'''**Objective:** $\min_{x'}\|E_I(x')-h_{target}\|_2$ with the original CLIP encoder.
$h_{target}$ comes from the selected original text/OCR/visual/combined trigger branch.
This is encoder access, not end-to-end decoder NLL. Use the actual published trigger;
do not substitute an arbitrary feature image. The released script uses an Adam loop,
box clamping and JPEG output; distinguish this released example from the paper's
convergence algorithm and complete four-trigger evaluation. No success is inferred
from embedding proximity alone; downstream behavior has its own evaluation.''',
'hijacks':r'''**Behavior matching:** minimize
$\sum_{c\in C} CE(B(c),M_\theta(x',c))$ using the native teacher-forced construction.
For prompt matching, $B_p(c)=M_\theta(I,p\Vert c)$ supplies soft output distributions.
$C$ is the context distribution, $p$ the original behavior instruction and $I$ the teacher
image. A single fixed continuation is not full-context prompt matching. Recover
the task-specific splits/validation selection and original checkpoint. Leak-context
experiments evaluate generated text only: no tool/email execution is authorized.''',
'bap':r'''**Two stages:** maximize corpus likelihood for a query-agnostic image within
the paper's pixel bound, then iteratively update textual input using previous
model responses and the paper's feedback judge. A fixed candidate list omits that
feedback mechanism. Preserve the original corpus, original merged/deduplicated evaluation
set, iteration cutoff and native decoding. Replacing original ChatGPT with an open
model is a declared methodological adaptation, not a faithful closed-model reproduction.''',
'physical_injection':r'''**Objective:** select visual instruction content and scene placement that induce
an unauthorized behavior on a legitimate task under the paper's access assumptions.
This is black-box prompt/location selection, not an FGSM objective. Preserve scene,
viewpoint, camera and task protocols and distinguish simulation from photographed
evidence. A released CyberSecEval3 image-marker test does not reproduce this paper.
Upstream's incomplete-run warning remains an explicit blocker.''',
'mmj':'''**Role:** common-benchmark evaluation pipeline. Generate attack cases, collect target
completions, then label them under the chosen original judge; measure benign utility
separately. This is useful for our later matched comparison, but it intentionally
changes some original attack evaluations. Keep native-paper and common-benchmark
tables separate. Do not count the benchmark itself as another attack.''',
'adashield':'''**Role:** inference-time defense. Static prompting and adaptive refinement/retrieval
are separate versions. Original attack datasets and benign utility matter. An unrelated
fixed prefix does not reproduce either version automatically; exact prompts/pools must
come from the audited release and remain private. Original API-dependent stages require
an explicit scope decision; no silent open-model replacement.''',
'jailguard':r'''**Role:** detector, not an image optimizer. Produce the paper's input mutations,
query the target, embed/compare responses and apply its divergence decision policy.
Report detection precision/recall/false-positive rates and target behavior separately.
Restore the original policy, sample budget, encoder, thresholds and split before a
reproduction. Flip-aware PGD alone is not JailGuard.''',
'survey':'''**Role:** discovery and taxonomy only. Follow citations to original experiments;
the survey cannot verify another paper's exact code/data or supply an independent ASR.'''
}


def md(s):return nbformat.v4.new_markdown_cell(s)
def code(s):return nbformat.v4.new_code_cell(s)


def build():
    cells=[md('''# Native-paper visual attack reproduction workbench

28 October 2026. **New protocol/source-audit notebook, not a completed attack run.**
The earlier presentation documents our common-benchmark adaptations; this workbench
tracks each original paper's method, inputs, settings and evaluation separately.
Scope is twelve registered readings: foundations, VLM attacks, benchmark, defenses and survey.
“Covered in the ledger” never means “experiment successfully reproduced.”

Default execution performs CPU metadata/source checks only. No model weights, API calls,
new synthetic data or scientific attack outputs are generated. Original-run result fields
start as `NOT_RUN`. Changing checkpoint, data, objective or scoring creates an adaptation.'''),
    md('''## 1. Evidence lanes and completion rules

**Native-paper lane:** original supported checkpoint, data/targets, splits, preprocessing,
objective, optimizer, artifact encoding, decoding and judge. Reduced scale must be explicit.

**Matched-comparison lane:** one held-out benchmark and scorer across mechanisms; our
previous Qwen/Smol results belong here. It supports comparison but does not replicate
every native paper. No newly generated replacement corpus is allowed in either lane.

A faithful result requires an auditable artifact, not a paper title or matching algorithm name.
Full paper table replication remains pending where original releases/compute are unavailable.'''),
    md(r'''### Architecture learning map

Learn: backpropagation/cross-entropy → transformer attention → ViT → CLIP →
causal language decoder → multimodal connectors → full VLM attack path.

| Component | Mathematical object to understand | Why it matters here |
|---|---|---|
| Backpropagation | $\nabla_x L$ and the chain rule | Frozen weights still permit image gradients |
| Attention | $\mathrm{softmax}(QK^T/\sqrt{d_k})V$ | Token interactions in vision and language |
| ViT | Image patches → embeddings + positions → encoder tokens | Pixels become features the connector can use |
| CLIP | Image/text embedding spaces and their distance/similarity | Jailbreak-in-Pieces targets embeddings |
| Causal decoder | $p(y_t\mid y_{<t},q,z)$ | Qi/BAP optimize sequence likelihood |
| Connector | $z=C(E(P(x)))$ | Projection/merging/Q-Former paths differ across VLMs |

For pixel attacks the flow is image $x$ → preprocessing $P$ → encoder $E$ → connector
$C$ → decoder → loss. The gradient travels backward through that path:
$\nabla_x L=J_P^T J_E^T J_C^T\nabla_z L$.
For an encoder-only attack, stop the objective at the embedding; no decoder gradient is needed.

Architecture reading list (titles/abstracts checked; learning assignments, not full reviews):
[Transformer](https://arxiv.org/abs/1706.03762),
[ViT](https://arxiv.org/abs/2010.11929),
[CLIP](https://arxiv.org/abs/2103.00020),
[BLIP-2/Q-Former](https://arxiv.org/abs/2301.12597).
For tomorrow prioritize tracing one image through the VLM, explaining targeted NLL,
FGSM/PGD projection, patch support, and the difference between optimization loss and ASR.'''),
    code('from pathlib import Path\nimport tempfile,sys,hashlib,json\nfrom IPython.display import display,Markdown\nREVIEW_ROOT=Path(tempfile.mkdtemp(prefix="vlm_paper_review_PRIVATE_"))\nsys.path.insert(0,str(REVIEW_ROOT))\nprint("Private source review folder:",REVIEW_ROOT)'),
    md('''## 2. Explicit registry and verification code

The next cell contains ordinary Python metadata/functions. It writes a local module
for imports; it does not serialize another source bundle or execute upstream code.'''),
    code('%%writefile {REVIEW_ROOT}/vlm_paper_protocols.py\n'+(ROOT/'tools/vlm_paper_protocols.py').read_text()),
    code('from vlm_paper_protocols import PAPERS,REVIEWED_FILES,audit_source,classify_evidence,reference_command,run_reference\n'+
         'table=["| Study | Role | Native data | Reproduction status |","|---|---|---|---|"]\n'+
         'for p in PAPERS:\n    table.append("| "+p["id"]+" | "+p["role"]+" | "+", ".join(p["datasets"])+" | "+p["reproduction_status"]+" |")\n'+
         'display(Markdown("\\n".join(table)))\nprint("Reviewed source/config files:",len(REVIEWED_FILES))'),
    md('''**Interpretation:** all native-paper runs remain NOT_RUN. The registry describes
what must be reproduced, not invented results. The prior 136 cases do not fill these rows.''')]
    for p in PAPERS:
        title=f'## {p["title"]}\n\n{p["authors"]}. [{p["arxiv"] or "AAAI proceedings"}]({p["paper_url"]}).\n\n'
        title+='**Inspection:** '+p['inspection']+'.\n\n'+CARDS[p['id']]
        title+='\n\n**Versions to account for:** '+(', '.join(p['variants']) or 'not an attack')+'.'
        title+='\n\n**Native inputs:** '+(', '.join(p['datasets']) or 'citation chains')+'.'
        if p['repo']:
            title+=f'\n\n[Official source snapshot](https://github.com/{p["repo"]}/tree/{p["revision"]}); revision `{p["revision"]}`.'
        title+='\n\n**Unresolved:** '+p['blocker']+'\n\n**Our original-paper result:** NOT_RUN.'
        cells.append(md(title))
    cells+=[md('''## 3. Inspect pinned original source files without model execution

Optional small-file downloads only. Each file is pinned to a reviewed repository commit
and checked against its actual Git blob hash. Source/config files may contain published
prompts, so save them privately; do not print their full contents or commit them.
Compilation checks syntax only, not dependency compatibility or scientific correctness.'''),
    code('FETCH_REVIEWED_SOURCE=False\nsource_audit=[]\nif FETCH_REVIEWED_SOURCE:\n'+
         '    for entry in REVIEWED_FILES:\n        source_audit.append(audit_source(entry,REVIEW_ROOT/"upstream_PRIVATE"))\n'+
         '    display(source_audit)\nelse:\n    print("No network/model execution. Set FETCH_REVIEWED_SOURCE=True for the pinned small-file audit only.")'),
    md('''## 4. Exact original-code entrypoints — preparation, not execution

The inspected Qi parser requires underscore flags; iteration and batch settings are also
hardcoded inside its source. Its original weights/environment must be present first.
Jailbreak-in-Pieces has a released encoder example with fixed paths/settings.
Other methods remain blocked until their native experiment configurations are recovered.
Separate original environments are required; do not install every legacy dependency
into the current Colab kernel and assume compatibility.'''),
    code('RUN_ORIGINAL=False\nPAPER_ID="pieces"\nPRIVATE_CHECKOUT=None\nPRIVATE_OUTPUT=None\nAPPROVAL={}  # Populate only from a reviewed, approved scientific/compute protocol.\n'+
         'if RUN_ORIGINAL:\n    if PRIVATE_CHECKOUT is None or PRIVATE_OUTPUT is None:\n        raise ValueError("Provide verified private original checkout/output paths first")\n'+
         '    outcome=run_reference(PAPER_ID,PRIVATE_CHECKOUT,PRIVATE_OUTPUT,APPROVAL)\n    display(outcome)\n'+
         'else:\n    print("No original attack run. Scientific and compute gates remain closed.")'),
    md('''**Interpretation:** having a command is not a working reproduction. The original
checkpoint/data/environment must pass review; a process exit does not establish ASR.
An expired or interrupted budget must remain recorded, not silently reset.'''),
    md('''## 5. Required record for every actual attempt

Paper/version and target table; source revision; checkpoint and processor hashes;
dataset/target hashes and source IDs; exact split; transforms; objective; optimization
steps/restarts/selection; artifact encoding; decoding; judge; human rubric; attempts,
responses, unresolved labels, costs and failures. Store raw evidence privately.

The fidelity function below reports missing facts instead of manufacturing them.'''),
    code('CURRENT_ORIGINAL_RUN={}  # No scientific run has occurred in this notebook.\ndisplay(classify_evidence(CURRENT_ORIGINAL_RUN))'),
    md('''## 6. Evaluation mapping

Classifiers: clean/attacked class accuracy or targeted class success. Generative safety:
the original behavior rubric and sampling protocol. Injection: unauthorized task deviation.
Detection: attack/benign detection metrics and false positives. Benign utility: original
task scorer. These endpoints are not interchangeable and must not be pooled as one ASR.

For a later matched comparison, prespecify all attempted-case denominators, paired clean
controls, unresolved-output handling, request-clustered uncertainty, human review and
benign utility. Keep native-paper scoring as a separate table with its own provenance.'''),
    md('''## 7. What can be presented now

The prior presentation contains measured adaptation results. This notebook adds the
original-method ledger and executable source/fidelity checks. No new native-paper ASR
exists. Missing full releases, closed-model dependencies and original hardware needs
are findings about reproducibility, not permission to invent substitutes.

First proposed next stage: released Jailbreak-in-Pieces encoder feasibility on the T4,
after source/model/data revision and memory checks, with a new approved amendment/budget.
This feasibility exercise is not a complete four-trigger, downstream safety reproduction.
Then resolve native Qi checkpoints and missing full configs before expanding runs.'''),
    md('## Appendix: audit findings and exact source locations\n\n'+(ROOT/'docs/VISUAL_PAPER_REPRODUCTION_AUDIT.md').read_text())]
    n=nbformat.v4.new_notebook(cells=cells,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3'),
        original_paper_runs=0,contains_prior_asr_as_original_result=False))
    nbformat.validate(n)
    path=ROOT/'notebooks/vlm_paper_reproduction.ipynb'
    path.write_text(json.dumps(n,ensure_ascii=False,separators=(',',':')))
    print(path,len(cells),'cells')


if __name__=='__main__':build()
