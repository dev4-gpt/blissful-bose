# Visual attacks: prior art, implementation fidelity and proposed contributions

**26 October 2026 · companion to the [end-to-end guide](VISUAL_ATTACKS_END_TO_END_GUIDE.md)**

## 1. What “copied from papers” means in this project

We implement established mathematical mechanisms and cite their origins. We have not
established line-for-line upstream source reuse or faithful reproduction of the named
VLM papers. The frozen execution source, not a matching attack name, determines what ran.
This document is a provenance and fidelity account, not an originality certificate.

Use four labels consistently:

| Label | Required evidence |
|---|---|
| Faithful reproduction | Supported original checkpoint, data, objective, preprocessing, attack/decoding configuration and evaluation protocol |
| Reduced-scale reproduction | Same essential method/protocol with declared sample/compute reductions and their consequences |
| Adaptation | Changed model, objective, preprocessing, access, target construction or task |
| Proposed / not executed | Design only; no result may be attributed to it |

**The completed panel's paper-derived mechanisms are adaptations.** Twelve configuration
variants do not mean twelve faithfully reproduced papers. Software tests establish code
behavior under their fixtures; the pretrained T4 run establishes operation of the declared
deployments; neither establishes paper-result replication by itself.

## 2. Original sources and what each contributes

Titles, method locations and inspection limits are recorded in the
[core-paper dossier](VISUAL_ATTACKS_RESEARCH_DOSSIER.md#3-core-reading-register).
Original method pages were revisited for this expansion. No paper is upgraded to
full-text/appendix/code verified on the basis of a method-section read. Published numerical
ASRs are intentionally not mixed into our result tables: their data, targets, models,
budgets and judges differ.

| Original source / method location | Previously studied mechanism | Our implementation and decisive difference | Fidelity / evidence |
|---|---|---|---|
| Goodfellow, Shlens, Szegedy, *Explaining and Harnessing Adversarial Examples*, [1412.6572v3, §§3–4](https://arxiv.org/html/1412.6572v3) | First-order signed input gradient under a norm constraint | Targeted generative sequence NLL, frozen VLM, raw-pixel projection | Adaptation; four synthetic cases/model; no target hits |
| Madry et al., *Towards Deep Learning Models Resistant to Adversarial Attacks*, [1706.06083v4, §2](https://arxiv.org/html/1706.06083v4) | Constrained inner adversarial search and outer robust training | Five-step targeted input PGD only; no outer training | Adaptation; one ordinary Smol target hit; not a robustness guarantee |
| Brown et al., *Adversarial Patch*, [1712.09665v2, §2/Eq.1](https://arxiv.org/html/1712.09665v2) | Replacement patch optimized over images, placements and transformations | Bounded local patch plus a separate small finite-transformation replacement patch; no physical capture | Adaptations; shared replacement evaluated on one carrier/model; no target hits |
| Zhang et al., *Adversarial Attacks of Vision Tasks in the Past 10 Years: A Survey*, [2410.23687v2, §§3–5,7](https://arxiv.org/html/2410.23687v2) | Field taxonomy and discovery map | Terminology/access/dataset organization | Review source, not an attack reproduced or evidence of original-paper results |
| Qi et al., *Visual Adversarial Examples Jailbreak Aligned Large Language Models*, [2306.13213v2, §§3.1–3.3](https://arxiv.org/html/2306.13213v2) | Optimize an image using likelihood of a corpus of target continuations | Synthetic context-average loss on newer models; no harmful corpus or published safety evaluation | Adaptation; one development carrier/model; no universal safety claim |
| Shayegani, Dong, Abu-Ghazaleh, *Jailbreak in pieces*, [2307.14539v2, §3.1/Eqs.3–4](https://arxiv.org/html/2307.14539v2) | Match trigger embeddings using a vision encoder, including CLIP joint-space constructions | Own-model visual-feature MSE against an arbitrary synthetic reference | Mechanism adaptation; not original CLIP triggers or encoder-only access demonstration |
| Bailey, Ong, Russell, Emmons, *Image Hijacks*, [2309.00236v4, §§2.1–2.2](https://arxiv.org/html/2309.00236v4) | Behavior matching and prompt matching over contexts | Detached teacher soft cross-entropy on one fixed continuation per case | Adaptation; context distribution/teacher construction changed; no image-only target hits |
| Ying et al., *Jailbreak Vision Language Models via Bi-Modal Adversarial Prompt*, [2406.04031v2, §§4.1–4.2](https://arxiv.org/html/2406.04031v2) | Query-agnostic image optimization followed by intent-specific text optimization | Shared image plus selection from a very small fixed candidate set | Adaptation; feedback-driven text generator and original experiments not reproduced |
| Weng et al., *MMJ-Bench*, [AAAI 2025, benchmark setup](https://ojs.aaai.org/index.php/AAAI/article/download/34983/37138) | Existing attack/defense comparison including normal-task utility | Guides planned protocol/baseline selection | Partially inspected; artifact/model/configuration reproduction pending |
| Ling et al., *Physical Prompt Injection Attacks on Large Vision–Language Models*, [2601.17383v1, §§III–V](https://arxiv.org/html/2601.17383v1) | Visual insertion with specified attacker access and physical evaluation | Known-task, prebuilt synthetic digital instruction-bearing images | Related mechanism only; physical attack, capture and source configurations not reproduced |
| Wang et al., *AdaShield*, [2403.09513v1, §§3.2–3.3](https://arxiv.org/html/2403.09513v1) | Manual static prompting and adaptive defense-prompt refinement/retrieval | Our own fixed untrusted-image prefix | Generic prompting baseline; not the published prompt or full AdaShield-S/A system reproduction |
| Zhang et al., *JailGuard*, [2312.10766v4, §4](https://arxiv.org/html/2312.10766v4) | Input mutations, response-similarity distributions and divergence-based detection | Not implemented in the completed panel | Review/planned extension; flip-pair PGD is not a JailGuard detector |

### 2.1 Why objective and access differences matter

Qi's corpus likelihood, a feature-space distance and a target behavior distribution are
different surrogates. Their values cannot be compared as a common score. Our own-model
feature access does not demonstrate the original encoder-only attack's assumptions.
Using an arbitrary reference image does not establish a harmful trigger representation.

BAP's second stage searches text with feedback; selecting a fixed candidate is narrower.
The single Qwen combined-condition hit shows that our selected image/text combination
can change this task's answer. It does not reproduce BAP's published safety experiments.

Brown's universal replacement patch can modify pixels substantially within its region;
our bounded local patch has a different threat model. Software rotations are not
photographic evidence. A single evaluation background cannot establish universal transfer.

The fixed prefix resembles a broad defense-prompting strategy, but it neither instantiates
AdaShield's full construction nor changes model parameters. The observed mixed utility
results cannot be described as improved model-weight safety alignment.

### 2.2 What published evaluations tested, versus our current endpoints

| Prior evaluation | Published result location / endpoint | Why our number is not directly comparable |
|---|---|---|
| FGSM / robust PGD foundations | Goodfellow §4 and Madry §5: classifier error/accuracy under specified threats | Our token target and exact-answer output are different tasks; no robust training was done |
| Adversarial Patch | Brown §3: classifier target behavior, controls and image/patch transformations | Our small synthetic set, fixed support and brief optimization differ; no photographed evaluation |
| Visual Adversarial Examples | Qi §§4.2–4.5: human harmful-scenario evaluation, toxicity benchmark and transfer | Fixed harmless target hits do not estimate harmful assistance or toxicity |
| Image Hijacks | Bailey §4, Table 1: behavior/attack results under the paper's generation and judging setup | Our fixed teacher continuation and contexts differ; code coverage is not table reproduction |
| Bi-Modal Adversarial Prompt | Ying §5, Table 1: harmful-intent image/text jailbreak evaluation | Our limited candidate selector and one combined perception example do not reproduce that endpoint |
| AdaShield | Wang §4.2/Table 2 and utility ablations: attack defense and normal-task behavior | Our prefix differs, safety labels are absent, and utility currently covers only geometry |
| JailGuard | Zhang §6.2/Table 4: detector performance under a mutation policy | Detector accuracy/precision/recall differ from target ASR; no detector ran here |
| MMJ-Bench | Benchmark evaluation and normal-task utility comparisons | Exact released artifact/model/scorer reproduction is still pending |

Original paper links and inspection depth are in the table above and the dossier's
P01–P12 cards. Reported literature figures remain that paper's results, not our observations.
To claim reproduction, extract the original table cell with its denominator and protocol,
rerun the matched configuration, report our estimate/uncertainty, and document every deviation.
This source comparison is incomplete until appendix/code and artifact audits are finished.

## 3. What we actually tried and tested

| Layer | Tested evidence | What remains untested |
|---|---|---|
| Teaching mechanics | CPU toy FGSM/PGD/patch demonstrations | They say nothing about pretrained VLM safety |
| Runner/control flow | CPU optimizer/runner checks, failure isolation and resume fixtures | These are not scientific experiment replications |
| Initial T4 profile | One synthetic Qwen case at 224 square; three PGD steps | Not pooled with the later 448-square panel |
| Broader T4 panel | Qwen and Smol, 34 method–task records/model, 12 variants/model | Four underlying tasks; no representative benchmark claims |
| Gradient/preprocessing gates | Native/reference comparisons, image gradients and saved-pixel bounds | No complete guarantee for arbitrary images, templates or library revisions |
| Paired outcomes | Clean, attack, random, text-only, injection and defended conditions | Some are repeated controls or have mechanism-specific semantics |
| Cross-model transfer | Qwen PGD/patch artifacts → Smol, eight cases | Reverse transfer and source-success-conditioned transfer |
| Human validation | Probability packet prepared: 120 of 480 in-panel records | Independent labels, agreement and adjudication |
| Safety benchmarks | Data/protocol preparation | No held-out unsafe-assistance evaluation in this evidence set |
| External injection benchmark | Frozen eight-case diagnostic prepared | Not executed in the inspected synthetic-panel results |

The [results report](VISUAL_ATTACKS_DEVELOPMENT_RESULTS.md) identifies the exact inspected
execution, source aggregate SHA256 and preserved archive. An earlier panel has the same
source contract but a different output hash. Do not pool them or switch the runtime
timings between them. The current checkout also includes extensions beyond the frozen
panel code; reproduction must begin with the archived source identity.

### 3.1 What we reused from `DL_final` and the historical project

The earlier classifier notebook provides a conceptual starting point for FGSM, PGD and
a per-example local patch. The static audit found normalized-space budget issues,
valid-pixel clamping problems, label-map uncertainty and ambiguous target scoring.
The new raw-pixel VLM runner addresses those mechanics with a different sequence loss,
native differentiable adapters and paired artifacts. It does not validate the original
README's classifier accuracy figures. See the [audit findings](VISUAL_ATTACKS_RESEARCH_DOSSIER.md#5-original-notebook-audit-static-not-reproduction).

The historical typographic studies supply lessons about prompt wording, image presence,
comprehension and label validity. Their prompts/data/results are separate from this new
visual perturbation panel. The earlier “see-saw” hypothesis is not a premise for the new
study, and neither typographic refusal gaps nor image presence effects establish pixel
attack effectiveness. Reuse validated infrastructure and controls, not unsupported hypotheses.

## 4. What counts as our contribution today?

**Implementation contribution to the project:** a frozen-weight, model-specific input-gradient
workflow, delivered-artifact constraints, controls, exact output identities, private evidence
preservation and aggregate reconciliation. This is useful research infrastructure.

**Scientific contribution currently supported:** limited descriptive feasibility and
behavioral measurements under stated adaptations. There is no established novel attack,
general defense, causal architecture explanation or validated safety improvement.

Novelty is not established by combining familiar attacks in one notebook. Prior work
already studies multimodal attacks, shared artifacts, transfer, defense prompting and
attack/defense utility comparisons. The dossier's later partial forward review also flags
preprocessing-aware transfer and visual degradation as occupied directions. Those leads
require complete source/code checks; they are not evidence that all possible narrower
questions have been exhausted.

## 5. Proposed research directions: hypotheses rather than claims

These proposal cards are prospective. They do not amend the scientific plan automatically,
authorize a new GPU run, or declare an idea novel. The owner reviews a concrete protocol
after prior-art/data/cost checks. Preserve existing outcomes as development evidence.

### Proposal A — joint-channel interaction under matched component controls

**Motivation:** Qwen's single combined-condition target hit was absent in its image-only
and text-candidate-only controls. This is a lead from a perception example, not a safety result.

**Question:** on held-out legitimate tasks, does a fixed joint image/text manipulation
increase predefined unauthorized behavior beyond either component alone?

**Design:** freeze four cells: clean image/base text, attacked image/base text, clean
image/selected text, attacked image/selected text. Select artifacts/text using development
only. Evaluate identical held-out requests/carriers, output budgets and scoring windows.
Include neutral text controls and review whether the added text itself legitimately
changes the authorized task. That distinction is essential for instruction-integrity claims.

**Estimand:** for success probabilities \(p_{ab}\), report the risk-scale interaction
\(I=p_{11}-p_{10}-p_{01}+p_{00}\). This is scale-specific; a positive risk interaction
does not imply a unique causal safety mechanism or statistical interaction on every scale.

**Needed evidence:** adequate held-out task coverage, paired request-cluster uncertainty,
semantic validation, independent labels and closest-prior-art exclusion. If the combined
effect vanishes, is driven by explicit task override, or is already known under this exact
design, reject the novelty claim and report the limitation or replication.

### Proposal B — defense effects across mechanisms at matched utility and cost

**Motivation:** the prefix recovers one Qwen patch exact answer but worsens its ordinary
PGD correctness count, and does not remove the observed targeted successes.

**Question:** does a prespecified inference wrapper reduce unsafe assistance/instruction
deviation under defense-aware attacks while respecting a benign-utility and cost constraint?

**Design:** no defense, fixed prefix, simple transformation, and one affordable reviewed
detector if profiling permits. Each has clean benign, attacked and adapted-attacked
conditions. Match or explicitly report pixel/area constraints, optimization strength,
queries and inference overhead. Tune all thresholds on development, never held-out labels.

**Decision rule:** require the prespecified safety/integrity benefit and utility constraint
together; report both paired effects, unresolved bounds and cost. Choose the minimum
meaningful benefit and utility tolerance before held-out outputs rather than reverse-engineering
them from an attractive result. A failed utility constraint invalidates a blanket “better defense.”

**Novelty gate:** attack/defense comparison is already established, including MMJ-Bench;
prompt defenses and mutation detectors are existing methods. Only a specific consequential
finding that survives closest-baseline comparison and held-out validation may qualify.

### Proposal C — a narrow artifact/preprocessing reproducibility study

**Question:** does a documented preprocessing/save/deployment difference materially change
the interpretation of a named baseline's attack outcome?

**Design:** faithfully reproduce one supported original configuration, then vary one factor
at a time: source versus delivered budget, resizing, patch support, tokenization or numerical
precision. Preserve paired images/requests and compare identical scoring. This is not a
generic “preprocessing matters” novelty claim; existing work already studies that direction.

**Go/no-go:** the effect must replicate, affect a meaningful conclusion and not merely
reflect a broken implementation. If it is an engineering bug without a generalizable finding,
release a correction/reproduction note rather than manufacturing a new attack contribution.

## 6. A concrete sequence before further scientific conclusions

1. Freeze the completed notebook/code/output identity and retain the existing numeric report.
2. Obtain independent semantic review of the probability sample plus a separately identified
   diagnostic review of all target hits/exact-correctness transitions.
3. Select one supported original baseline and complete its methods/appendix/code/config audit.
4. Resolve source permissions and connected-group historical overlap; prepare true clean pairs.
5. On development only, check stronger iterations/restarts, placements, bounds and scorer validity.
6. Choose one proposal after closest-prior-art review; freeze endpoints, sample size and budget
   through a new accepted amendment before reserved outputs.
7. Run the small held-out comparison with benign utility, adapted attacks, costs and uncertainty.
8. Write the paper around the strongest supported finding, including failed predictions.

**Completion standard:** another researcher can distinguish copied mathematical ideas,
changed implementations, executed experiments, measured outcomes and untested proposals;
can reproduce the reported numeric tables; and can identify every limitation that changes
the interpretation. Publication readiness requires evidence beyond this documentation.
