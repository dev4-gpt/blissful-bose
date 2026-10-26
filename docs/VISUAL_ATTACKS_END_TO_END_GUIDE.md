# Visual attacks on VLMs: from data and gradients to evidence

**26 October 2026 · teaching and research guide · inspected synthetic development execution**

## 1. Reading route and scientific purpose

This is the explanatory entry point to the visual-attack study. Read §§2–4 for data,
architecture and attack mathematics; §§5–7 explain evaluation and trace measured
outcomes back to the experiment. The [results report](VISUAL_ATTACKS_DEVELOPMENT_RESULTS.md)
contains complete outcome/cost tables and archive hashes. The separate
[prior-art and contribution review](VISUAL_ATTACKS_PRIOR_ART_AND_CONTRIBUTIONS.md)
identifies which ideas come from papers, which implementations differ, and what we propose.

Our question is how attacker-controlled images affect perception, instruction integrity
and safety in frozen open VLMs, and whether inference-time defenses help without
unacceptable utility loss. We have completed an engineering/development panel, not
the held-out safety study needed to answer the entire question. We do not train weights.

```mermaid
flowchart TD
    Q[Research question and threat model] --> D[Versioned data and connected-group splits]
    D --> A[Frozen VLM and differentiable preprocessing]
    A --> O[Declared attack objective and constraints]
    O --> X[Saved and reloaded image artifact]
    X --> C[Paired clean, attacked, control and defended generation]
    C --> E[Correctness, targeted success, integrity or safety scoring]
    E --> V[Validation, denominators, costs and uncertainty]
    V --> R[Claim supported by this exact evidence]
    R --> N[Prior-art check and next prespecified experiment]
```

Each arrow is necessary. A mathematical objective is not an evaluated attack; a generated
wrong answer is not automatically a jailbreak; an executed notebook is not a novel result.

## 2. Data: what was used, what is historical, and what is proposed

### 2.1 Data actually used in the inspected panel

The panel uses a small locally generated geometry collection: **four development
image–task pairs and four optimization-only contexts**. The tasks cover simple attribute,
shape and counting judgments. Two have incorrect perceptual targets; two use a harmless
fixed marker as the unauthorized behavior. This description deliberately does not
publish stimulus prompts, image artifacts or raw model replies.

| Component | Role | Separation and limitation |
|---|---|---|
| Four base images/tasks, IDs `dev_0`–`dev_3` | Paired clean/attacked behavior | Two perception and two integrity cases; reused across variants |
| Four dot-counting contexts | Shared-objective optimization | Separate intent/image groups from development; not held-out benchmark evidence |
| Instruction-bearing image counterparts | Digital visual injection | The scene carries added instructions; separate unbounded artifact |
| Synthetic feature reference | Feature-distance objective | An arbitrary visual target; not a harmful-semantic representation |
| Fixed teacher/candidate text | Behavior matching and joint-channel adaptation | Small predetermined set; not a feedback-based published text optimizer |
| Prefix defense | Compare paired defended and undefended conditions | User-input prefix; no model-weight alignment update |

Source: [dataset and variant definitions](../tools/vlm_visual_panel.py:46). The four tasks
generate 34 method–task records per model because conditions and mechanisms repeat.
There are 68 records over two models, 480 in-panel generation events and 16 additional
transfer generation events. These counts must not be presented as 68 independent
images or 496 independent research tasks. No harmful-request benchmark was used here.

### 2.2 Dataset roles and readiness

| Dataset/source | Appropriate purpose | Actual status in this visual study |
|---|---|---|
| Synthetic geometry | Gradient/debugging checks and interpretable controls | Executed on Qwen and Smol; results reported |
| Existing ImageNet subset / `DL_final` | Historical classifier attack audit | Source audited; subset/labels/results not independently reproduced |
| COCO | Natural-image carriers and paired clean scenes | Candidate; image IDs, upstream permissions and manifest not frozen |
| VQAv2 | Realistic benign visual utility | Candidate; annotation handling and official scorer integration pending |
| HarmBench | Safety requests and standardized behavior evaluation | Official CSV audited privately; no safety inference in this panel |
| MMJ-Bench | Published attack/defense protocol reproduction | Official source identified; exact artifact/configuration reproduction pending |
| CyberSecEval3 visual injection | External instruction-integrity evaluation | Fixed small diagnostic prepared; not executed in this result set |
| PHANTOM | Optional external attack/transfer coverage | Access, decomposition, permissions and overlap gates unresolved |
| MM-SafetyBench / FigStep | Historical typographic research | Earlier project results exist; excluded from current pixel/patch outcome estimates |

[VQAv2's official downloads](https://visualqa.org/download.html) provide questions and
annotations; a one-word exact scorer for geometry is not its official consensus scorer.
[HarmBench](https://github.com/centerforaisafety/HarmBench) supplies a red-teaming/evaluation
framework; its behavior requests are not image comprehension labels. Its audited CSV
contains 400 rows split into 200 standard, 100 copyright and 100 contextual entries at
the revision/checksum recorded in the [dossier](VISUAL_ATTACKS_RESEARCH_DOSSIER.md).
Those categories must not be silently mixed. Historical semantic overlap is unresolved.

The [official CyberSecEval3 visual-injection release](https://huggingface.co/datasets/facebook/cyberseceval3-visual-prompt-injection)
is evaluation-oriented. Our prepared diagnostic freezes eight literal-marker cases,
keeps original system/user roles, and tests released images without optimization.
Original clean-source counterparts are unavailable in that prepared subset. A text-only
comparison therefore cannot isolate the causal effect of adding an injection to the
same clean scene. Preparation and downloads do not constitute completed evaluation.

### 2.3 How the scientific dataset should be constructed

For each private item retain source revision/ID, source permissions, image checksum,
task, expected answer or rubric, target behavior, track, clean-pair ID, intent group,
image group and previous exposure. A record's split is optimization, development or
reserved evaluation; variants inherit their underlying record's split.

Construct a graph connecting examples that share an image, underlying intent, paraphrase
family or derived artifact. Split connected groups before tuning. Otherwise a universal
patch can see an evaluation background during optimization or a paraphrase of a reserved
request can leak into development. File-level random splitting is insufficient.

Select images according to the scientific question. An arbitrary image plus a harmful
request tests an image-carrier effect. A harmful-scene understanding claim requires a
task whose semantics depend on the depicted scene. Clean visual utility requires real
answerable tasks with verified answers. Injection needs a legitimate task, attacker-controlled
visual region/content, and a predefined unauthorized deviation—not simply text recognition.

The 40-development/120-evaluation safety caps in the plan are provisional resource values,
not achieved sample sizes or a power calculation. Freeze final sizes, scoring and contrasts
before reserved outputs, after measured cost and provenance checks.

## 3. Deep learning architecture and gradient access

### 3.1 Shared computational structure

Write preprocessing as \(P\), the image encoder as \(V_\phi\), connector as \(C_\psi\),
text tokenizer/embedding as \(E\), and autoregressive decoder as \(D_\omega\):

\[
Z_v=C_\psi(V_\phi(P(x))),\qquad Z_t=E(t),\qquad
p_\theta(y_j\mid x,t,y_{<j})=D_\omega(Z_v,Z_t,y_{<j}),\quad
\theta=(\phi,\psi,\omega).
\]

The visual encoder turns patches into contextual visual features. The connector compresses
or projects those features into the language model's embedding space. The decoder attends
to the fused image/text representation and predicts the next text token. “Connector” is
a functional category; the two models do not have an identical implementation.

At a Transformer attention layer,
\(Q=HW_Q, K=HW_K, V=HW_V\), and
\(\operatorname{Attention}(H)=\operatorname{softmax}(QK^T/\sqrt{d_k}+B)V\).
Here \(H\) contains token features, \(d_k\) is key dimension, and \(B\) encodes masks
or positional structure. Layers contextualize patches or text tokens. This equation
explains information flow; it does not identify which attention head causes a failure.

An image attack backpropagates through the connector and encoder:
\(\nabla_xL=J_P^T J_V^T J_C^T\nabla_{Z_v}L\), using the chain rule. Frozen weights
still participate in this derivative. Setting every parameter's `requires_grad=False`
prevents weight gradients; it does not require turning off image gradients. Using
`inference_mode` around the attack forward pass would break that path.

### 3.2 The Qwen path we implemented

The [official Qwen model card, Architecture Updates](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)
describes a vision Transformer using window attention, with SwiGLU and RMSNorm, integrated
with a Qwen2.5 language model. Our adapter uses native `Qwen2_5_VLForConditionalGeneration`.
It normalizes raw RGB, creates the required temporal/spatial patch layout, obtains merged
visual features, and feeds the native conditional text generator. We evaluate still images;
the checkpoint's video features are outside the experiment.

For the panel's 448-square canvas and adapter's 14-pixel patch/2×2 merge layout, there
are \((448/14)^2=1024\) spatial patch positions and 256 merged spatial groups. This is
derived from the adapter layout, not a claim of identical total prompt tokens across
models. Template and special tokens remain additional. FP16, eager attention and batch
one are declared execution choices. See [patch layout and adapter](../tools/vlm_visual_adapter.py:16).

### 3.3 The SmolVLM path we implemented

The [official SmolVLM card, Technical Summary and License](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct)
identifies an Idefics3-based model with a SigLIP image encoder and SmolLM2 text decoder.
Our native class is `Idefics3ForConditionalGeneration`. The adapter normalizes pixels,
uses the native image-feature/connector path, and supplies compressed visual tokens
to the language decoder. It disables image splitting/resizing and explicitly uses
448-square inputs rather than the card's normal 512-pixel image processing.

The configured patch/compression layout gives \((448/16/4)^2=49\) image tokens. FP32
and eager attention are explicit choices. This adaptation helps fit/control an input
gradient experiment; it changes the normal deployment configuration. Source:
[Smol adapter](../tools/vlm_visual_smol_adapter.py:16).

Equal RGB canvases do not equalize visual token count, numerical precision, pretraining,
parameter count or instruction tuning. Consequently model differences are deployment
comparisons, not isolated causal effects of architecture or scale.

### 3.4 Differentiable preprocessing and correctness checks

PIL conversion/resizing is used before defining the canonical attack canvas. Inside
optimization the differentiable tensor path applies normalization/patchification. For
\(z_c=(x_c-\mu_c)/\sigma_c\), a normalized perturbation has raw size
\(\delta x_c=\sigma_c\delta z_c\). A common normalized-space epsilon therefore need
not mean the same raw RGB budget across channels. We constrain raw pixels, then normalize.

Templates, token IDs and grid metadata can be built using a dummy image; real pixel values
are replaced by the differentiable tensor path. Acceptance checks compare native/reference
preprocessing and selected clean logits, require finite nonzero image gradients, enforce
pixel/mask bounds after PNG reload, and inspect frozen parameter state. These checks are
necessary for mechanics, not sufficient for semantic scoring or broad robustness.

## 4. Attack taxonomy, objectives and implementation

### 4.1 Taxonomy before attack names

| Axis | Alternatives | Our completed panel |
|---|---|---|
| Access | Full-model gradients; encoder-only gradients; queries; transfer | Full input gradients; own-model features; one directional transfer stage |
| Channel | Image; text; combined | Fixed text for image-only conditions; selected text for combined condition |
| Support | Entire image; local region; replacement image | Bounded full image, top-left patch, explicit injection artifact |
| Scope | Per-example; shared context; held-out universal | Mostly per-example; shared modes on one development carrier |
| Objective | Untargeted error; target answer; behavior; feature similarity | Target NLL and surrogate matching; marker injection |
| Outcome | Perceptual failure; instruction deviation; unsafe assistance | Exact perceptual/marker diagnostics; safety unmeasured |

FGSM/PGD describe update rules, a patch describes support, and injection describes a
trust-boundary mechanism. These terms are not mutually exclusive attack categories.

### 4.2 Generative loss versus classifier loss

A classifier predicts a fixed label distribution and often attacks
\(J(x,c)=-\log p_\theta(c\mid x)\). A generative VLM predicts token sequences:

\[
L(x,t,y^*)=-\frac1m\sum_{j=1}^{m}\log p_\theta(y_j^*\mid x,t,y^*_{<j}),
\qquad m=|y^*|.
\]

Every symbol matters: \(x\) is the image, \(t\) is text, \(y^*\) is the fixed target,
\(m\) is its token length and \(\theta\) is frozen. Teacher forcing supplies preceding
target tokens during optimization. The prompt/image/padding positions contribute no loss;
logit position \(j-1\) predicts target token \(j\). At evaluation the model generates
freely with greedy decoding. Optimizing the teacher-forced loss does not guarantee that
the first free-generated token selects the target. Source: `shifted_nll` in the Qwen adapter.

### 4.3 FGSM and why its sign differs by objective

Linearize \(L(x+\delta)\approx L(x)+\nabla_xL^T\delta\). Under
\(|\delta_i|\le\epsilon\), each coordinate minimizes the linear term by taking
\(\delta_i=-\epsilon\operatorname{sign}(\partial_iL)\). Thus targeted FGSM is
\(x'=\Pi_{\mathcal C}(x-\epsilon\operatorname{sign}\nabla_xL)\), with
\(\mathcal C=[0,1]^d\cap B_\infty(x,\epsilon)\). Untargeted maximization of true-answer
loss instead takes the plus sign. The original sign-gradient principle comes from
[Goodfellow et al., §§3–4](https://arxiv.org/html/1412.6572v3); our sequence objective is an adaptation.

Our FGSM starts from the clean canvas and makes one step at 8/255. Neither model reaches
a fixed target on its four image-only cases; both models' objective decreases in 4/4.
That difference directly illustrates loss improvement versus generated-answer success.

### 4.4 PGD and constrained optimization

For repeated targeted descent,
\(x_{k+1}=\Pi_{\mathcal C}(x_k-\alpha\operatorname{sign}\nabla_{x_k}L)\).
Projection clamps each coordinate to
\([\max(0,x_i-\epsilon),\min(1,x_i+\epsilon)]\).
Our seeded start is uniform within the allowed additive box followed by projection;
the best loss iterate competes with the clean fallback. Five steps, one restart and
\(\alpha=2/255\) are development settings, not a strong-attack convergence certificate.

[Madry et al., §2](https://arxiv.org/html/1706.06083v4) places adversarial input search inside
an outer robust-training objective. We implement input search only. No outer training
or robust-model guarantee follows. Smol PGD reaches a fixed wrong perceptual answer in
one of four cases; Qwen reaches none. The paired case interpretation is in §7.

### 4.5 Local bounded patch and shared replacement patch

A mask \(M\) restricts support: \(x'=(1-M)\odot x+M\odot p\). Local bounded PGD
restricts changed pixels to the same 8/255 interval, leaving everything outside \(M\)
identical. Our fixed top-left square has side
\(\lfloor\sqrt{0.04HW}\rfloor=89\) at 448×448; effective area is \(89^2/448^2\).
This patch lies mainly in the synthetic background. Placement sensitivity is untested.

The shared replacement patch permits \(p\in[0,1]\) inside its support and minimizes
\(K^{-1}\sum_{k=1}^{K}L(C(x_k,p,T_k),t_k,y_k^*)\), where \(C\) composes a patch,
\(x_k\) is an optimization background and \(T_k\) is placement/rotation. The code draws
seeded translations/right-angle rotations once and reuses them. It does not simulate
a physical camera, lighting, perspective, scale or continuous deployment distribution.
Our finite transformation objective is motivated by
[Brown et al., §2, Eq.1](https://arxiv.org/html/1712.09665v2), not a faithful reproduction.

Five 2/255 updates from a gray initialization provide very little patch exploration even
though the replacement constraint permits large changes. Its zero observed target hits
on one carrier per model do not establish patch robustness. Compare budget, area and
optimization strength explicitly before comparing attacks.

### 4.6 Shared-image and shared bounded-patch objectives

For optimization contexts \(\{(t_k,y_k^*)\}_{k=1}^K\), minimize
\(\bar L(x')=K^{-1}\sum_k L(x',t_k,y_k^*)\). The bounded-patch version additionally
enforces \(M\). This reuses an artifact across contexts; it does not establish universal
generalization to unseen requests or images. Our shared-image modes optimize the same
carrier later used for development scoring. Separate text contexts do not make that
carrier unseen. The replacement-patch version uses separate backgrounds but still
evaluates only one carrier. Qi et al.'s corpus-image idea is related; the
[source review](VISUAL_ATTACKS_PRIOR_ART_AND_CONTRIBUTIONS.md#2-original-sources-and-what-each-contributes)
records its different target corpus and evaluation.

### 4.7 Feature and behavior matching

Feature matching minimizes
\(L_{\rm feat}(x')=\frac1r\|V(x')-V(x_{\rm ref})\|_2^2\), where \(r\) is the number
of compared feature elements. The reference features are detached. Our optimizer is
Adam plus pixel projection; Qwen uses merged visual features and Smol native image
features. These are not CLIP joint text/image embeddings. Original embedding-space
targeting is described by [Shayegani et al., §3.1, Eq.4](https://arxiv.org/html/2307.14539v2).

Behavior matching uses teacher distribution \(q_{j,v}\) and student distribution
\(p_{j,v}(x',t)\) over token \(v\) at position \(j\):
\(L_{\rm match}=-m^{-1}\sum_j\sum_v q_{j,v}\log p_{j,v}(x',t)\).
The detached teacher is conditioned on a different fixed prompt over the same continuation.
Our finite, fixed-continuation adaptation is motivated by
[Bailey et al., §§2.1–2.2](https://arxiv.org/html/2309.00236v4).
It does not reproduce the full published context/behavior construction. Neither model's
feature or behavior-matching image-only condition reaches a fixed target in this panel.

### 4.8 Combined image–text and visual instruction injection

After shared image optimization, select
\(t^*=\arg\min_{t\in\mathcal T} L(x',t,y^*)\) from a small predetermined candidate set.
Generate paired image-only, text-candidate-only and combined outputs. Our selector does
not implement BAP's intent-specific feedback search; see
[Ying et al., §§4.1–4.2](https://arxiv.org/html/2406.04031v2). Text changes make this a
combined-channel experiment, not a pure image attack. Qwen reaches one target only in
the combined condition; this is one perception case, not unsafe assistance.

Visual injection places instructions in image content that the model should treat as
task data. Success is acting on them instead of the authorized task. Transcribing or
describing such text can be legitimate. There is no necessary gradient or small epsilon.
Our two dedicated tasks produce zero unauthorized-marker hits for either model.
Physical insertion studies use different access and capture assumptions; see the
[physical injection paper, §§III–V](https://arxiv.org/html/2601.17383v1). No physical capture ran here.

### 4.9 Defense-aware objectives

Let \(d\) be the fixed prefix. Defense-aware PGD minimizes \(L(x',d\mathbin\Vert t,y^*)\).
The flip-pair version minimizes the finite average
\(\tfrac12[L(x',d\Vert t,y^*)+L(F(x'),d\Vert t,y^*)]\), where \(F\) flips horizontally.
It evaluates a declared flip deployment, not all stochastic transformations. The prefix
changes input conditioning; weights remain unchanged. Feature and injection modes do
not claim comparable text-defense adaptation. No JailGuard detector or full AdaShield
adaptive prompt system was evaluated.

## 5. Evaluation: what Attack Success Rate actually means

Define generated answer \(a_i^c\) under condition \(c\), fixed target \(y_i^*\), and
predefined correct-answer set \(G_i\). Our current normalized exact diagnostics are
\(S_i^c=1\{\nu(a_i^c)=\nu(y_i^*)\}\) and
\(C_i^c=1\{\nu(a_i^c)\in\nu(G_i)\}\), where \(\nu\) normalizes case/whitespace and
terminal punctuation. These are deterministic strings, not human semantic judgments.

| Endpoint | Formula | Interpretation / current status |
|---|---|---|
| Targeted ASR | \(N^{-1}\sum_i S_i^{\rm attack}\) | Fixed target-hit fraction; available descriptively |
| Targeted change | \(N^{-1}\sum_i(S_i^{\rm attack}-S_i^{\rm clean})\) | Discounts existing baseline target hits |
| Conditional target success | \(\sum_i(1-S_i^{\rm clean})S_i^{\rm attack}/\sum_i(1-S_i^{\rm clean})\) | Secondary; undefined if denominator zero |
| Newly induced exact error | \(\sum_i C_i^{\rm clean}(1-C_i^{\rm attack})/\sum_i C_i^{\rm clean}\) | Correct-baseline exact degradation; not necessarily semantic error |
| Integrity ASR | \(N^{-1}\sum_i 1\{\text{predefined unauthorized deviation}\}\) | Marker proxy available; broader semantic review pending |
| Safety ASR | \(N^{-1}\sum_i H_i^{\rm attack}\) | Validated prohibited-assistance label \(H_i\); not measured |
| Defense benefit | \(N^{-1}\sum_i(S_i^{A}-S_i^{D,A})\) | Positive means fewer target hits; assess utility alongside it |
| Clean utility change | \(N^{-1}\sum_i(C_i^{D,clean}-C_i^{clean})\) | Detects defense over-refusal/task disruption |

For safety, “did not refuse” is not equivalent to prohibited assistance. Irrelevant,
garbled, incomprehending or harmless answers need separate labels. The input image and
authorized task must be available when judging visual correctness or instruction integrity.

If \(H\) cases are resolved unsafe and \(M\) are unresolved out of \(N\) attempts,
report confirmed unsafe \(H/N\), missing \(M/N\), and bounds
\([H/N,(H+M)/N]\). Do not count failures as safe. A resolved-only rate must state its
conditional denominator. Current execution has no case failures, but independent human
semantic labels are absent; zero runtime failure does not resolve scoring uncertainty.

For the future study, freeze decoding, output window, primary comparisons and task rubric.
Use paired effects and underlying-request clusters; do not treat repeated mechanisms or
shared universal artifacts as independent samples. Prespecify Holm correction for a
small primary contrast family. No p-value, broad equivalence or power claim is supplied
for four reused synthetic tasks. Human reviewers must independently label the probability
sample; the current 120/480 simple-random record sample is not a balanced task sample.

## 6. Direct attack/defense result map

The generated table selects each mechanism's **actual primary condition**: `injection`
for visual injection, `combined` for joint image–text, and `attack` otherwise. Each cell
shows target hits / attempts (descriptive percentage). Defense uses the same selected
artifact/text with the prefix; defense-aware artifacts were optimized against that prefix.
Zero counts on tiny development samples do not certify robustness.

<!-- ASR:START -->

| Variant | Primary condition | Qwen target ASR | Qwen + prefix | Smol target ASR | Smol + prefix |
|---|---|---:|---:|---:|---:|
| bimodal | combined | 1/1 (100%) | 1/1 (100%) | 0/1 (0%) | 0/1 (0%) |
| feature | attack | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) |
| fgsm | attack | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) |
| injection | injection | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) | 0/2 (0%) |
| patch | attack | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) |
| pgd | attack | 0/4 (0%) | 0/4 (0%) | 1/4 (25%) | 1/4 (25%) |
| pgd_aware | attack | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) | 1/4 (25%) |
| pgd_aware_flip_defense | attack | 0/4 (0%) | 0/4 (0%) | 1/4 (25%) | 1/4 (25%) |
| prompt_match | attack | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) | 0/4 (0%) |
| universal | attack | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| universal_eot | attack | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |
| universal_patch | attack | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) | 0/1 (0%) |

<!-- ASR:END -->

Source: [numeric evidence](../visual_development_20261026/numeric_summary.json), reconciled
to all 68 Boolean case records. Regenerate/check using `tools/report_visual_development.py`.
This is target-hit ASR, not a harmful-assistance benchmark. Each shared-mode denominator
is one carrier; the 100% Qwen combined entry is literally one case.

## 7. Worked chains: connect a question to its final conclusion

| Research question | Data / access / objective | Relevant control | Observed result | Supported interpretation |
|---|---|---|---|---|
| Can a bounded image change induce a chosen perceptual answer? | Smol `dev_1`; frozen full gradient; five-step target NLL PGD | Same image/task clean and seeded random | Clean correct, PGD wrong-target hit; random correct | One targeted perceptual success; no safety conclusion |
| Does Qwen's PGD degrade a task more than noise? | Four synthetic pairs; raw bound 8/255 | PGD and random at same budget | Clean 4/4 correct; both PGD and random 3/4 by exact criterion | Marginal count alone does not establish attack-specific semantic degradation |
| Does the prefix help against ordinary PGD? | Same PGD artifacts and task; change prefix only | Undefended versus defended attack; defended clean | Qwen correctness 3/4→2/4; Smol 1/4→1/4; target hits unchanged | No demonstrated general defense benefit; utility harm is possible |
| Can image and text jointly matter? | Qwen `dev_0`; shared image and selected text | Image-only and text-candidate-only | Components correct; combined wrong-target hit, persisting with prefix | Candidate interaction on one perception case; no general synergy claim |
| Does injection hijack authorized behavior? | Two integrity pairs; digital instruction-bearing image | Clean pair and actual injected image | Zero marker hits for both; Smol clean/injected exact correctness 1/2 | No marker success observed; not general injection robustness |
| Do artifacts transfer? | Same Qwen PGD/patch artifacts replayed on Smol | Destination clean and attacked, no destination optimization | 0/8 transferred target hits | No observed fixed-target transfer; source-success denominator is empty |

Ordinary Smol PGD's 1/4 targeted ASR is 25%, but its baseline exact correctness is only
3/4. It produces two newly induced exact failures among those three baseline-correct
cases; only one is the specified target. This separates target success, general exact
degradation and existing capability failure. Do not relabel all three attacked incorrect
cases as new attack successes. Semantic review is still required for exact mismatches.

All mechanism runs finished with no recorded case failure; native parity and bounded
artifact checks passed. Qwen's sequence/feature objectives decrease in 30/32 optimized
records and Smol's in 32/32, yet most free-generated targets do not occur. The prefix
neither removes Smol's ordinary PGD target hit nor Qwen's combined target hit. Execution
success, surrogate improvement, target success and safety success are four different claims.

## 8. What is established and what happens next

Established: two declared T4 deployments can execute this input-gradient workflow;
controls, artifacts, numeric extraction and private preservation work; there are a few
traceable perceptual/exact-answer effects. Not established: unsafe assistance, a universal
defense, cross-model safety ranking, faithful original-paper reproduction or novelty.

The next research steps are to validate semantic scoring, reproduce a named original
baseline, resolve data/split permissions and overlap, strengthen attacks on development
data, then freeze a held-out safety/integrity/utility experiment. The
[prior-art review and proposal cards](VISUAL_ATTACKS_PRIOR_ART_AND_CONTRIBUTIONS.md)
specify which ideas are inherited and what evidence would justify a contribution.
These are proposals, not authorization to start new GPU runs or new scientific claims.
