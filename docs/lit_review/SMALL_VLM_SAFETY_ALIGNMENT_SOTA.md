# Safety and Alignment of Small Vision-Language Models
## Problem Formulation, SOTA, Research Challenges, Attacks, Baselines, Benchmarks
### Claude-run review, 2026-09-27

**Scope note, per your advisor's direction.** This does **not** propose extending Bach et al.'s
LLM continual-safety-alignment method to VLMs. It maps what is already being studied under "safety
and alignment of small VLMs" and structures it — problem, SOTA, challenges, attacks, baselines,
benchmarks. It is a sibling document to `LITERATURE_REVIEW_CLAUDE.md` (the earlier, continual-FT-specific
review) and to Codex's `vlm_safety_alignment_research_review.md` (broader VLM safety, not
size-focused); this one is scoped specifically to **small/efficient VLMs**, per your professor's ask.

**"Small" here** means models built or evaluated for resource-constrained deployment: ≲7B total
parameters, edge/on-device targets, or explicitly-efficient architectures (SmolVLM, MobileVLM,
TinyLLaVA-class, PaliGemma, Moondream, or a 7B-and-under backbone such as Qwen2-VL-2B/7B, LLaVA-1.5-7B).
Most VLM safety literature does not stratify by size, so a fair amount of the material below is
**general VLM safety with a small-model instance**, and I say so per entry, rather than overstating a
"small-model" framing the paper itself doesn't make.

**Evidence grading**, consistent with the earlier review: **[A]** = I read the abstract in full this
session and it supports the characterization. **[T]** = existence/title/authors/date checked via
arXiv, description from search snippets — reread before citing. Every arXiv ID below was independently
verified against its `arxiv.org/abs/<id>` page (`arxiv_verified2.json`, 17 IDs, 0 missing, alongside the
47 from the earlier review).

---

## 1. Problem Formulation

### 1.1 Two words, two different failure modes

- **Alignment** = whether the model's *objective* matches intended behavior (helpful, harmless,
  honest — the HHH framing from RLHF/Constitutional-AI-era work) **[general framing, not itself a
  single VLM paper — see §4]**.
- **Safety** = the *operational* outcome: does the deployed model actually refuse to assist harm,
  avoid leaking private data from an image, and avoid confidently wrong (hallucinated) answers, under
  both benign and adversarial inputs.
- A VLM can be "aligned" on paper (its LLM backbone went through RLHF) and still be **unsafe in
  practice**, because the vision pathway was never part of that alignment process. This is the central,
  well-evidenced fact the whole field turns on — see §1.3.

### 1.2 Formal statement

Given a small VLM with parameters $\theta$ (typically an LLM backbone $\theta_L$ aligned via RLHF/DPO,
a vision encoder $\theta_V$, and a cross-modal connector $\theta_P$ — projector, adapter, or
cross-attention), and an input $x=(I,T)$ (image, text):

$$
y=f_\theta(I,T), \qquad \text{safe}(y \mid x) \in \{0,1\}
$$

The problem is to characterize and improve $\Pr[\text{safe}(y\mid x)=1]$ across:

1. **benign inputs** (should be helpful, not over-refuse),
2. **directly harmful inputs** (text or image alone states the harmful request),
3. **compositionally harmful inputs** (neither $I$ nor $T$ alone is harmful; the harm is in their
   combination), and
4. **adversarially perturbed inputs** (optimization-based or hand-crafted $I,T$ designed to elicit
   unsafe $y$),

**subject to a parameter budget** that rules out the largest and most expensive defenses (huge
preference datasets, per-query heavy reasoning, ensembles) — the part of the problem "small" adds.

### 1.3 Why this is a distinct problem from LLM safety (the evidence)

- **The vision pathway is not covered by the backbone's text-only alignment.** VLGuard finds that
  VLM instruction-tuning data itself often contains harmful content and that fine-tuning can cause
  the underlying LLM's safety alignment to be *forgotten* — [VLGuard, Zong et al., arXiv:2402.02207](https://arxiv.org/abs/2402.02207) **[A]**.
- **A quantifiable "modality gap" predicts how unsafe a VLM will be.** [Yang, Stice, Payani,
  Mirzasoleiman, arXiv:2505.24208](https://arxiv.org/abs/2505.24208) **[A]**: even a *blank or
  irrelevant image* can make an LVLM answer a prompt it would refuse in text-only mode; the size of the
  representational gap between image and text embeddings is "highly inversely correlated with VLMs'
  safety," and this gap is introduced during pretraining and persists through fine-tuning. This gives
  the field an actual mechanism, not just an observation, and it's a training-time (pretraining-level)
  finding — distinct from any fine-tuning-time story.
- **Visual jailbreaks generalize worse than text jailbreaks, and don't require gradients.** [Azulay et
  al., arXiv:2605.00583](https://arxiv.org/abs/2605.00583) **[A]**: four zero-gradient visual attacks
  (symbol-cipher-in-image, benign-object substitution, in-image text substitution, visual analogy
  puzzles) expose a "cross-modality alignment gap" across six frontier VLMs — e.g. a visual cipher gets
  40.9% attack success on one model vs. 10.7% for the textual-only equivalent.
- **The vulnerability is not just at the input/output surface — it's internal.** [JailBound, Song et
  al., arXiv:2505.19610](https://arxiv.org/abs/2505.19610) **[A]** argues VLMs encode an *implicit
  safety decision boundary* inside fusion-layer representations and attacks it directly, rather than
  the input text/image.

### 1.4 Why "small" changes the problem, not just the budget

- **Small models are not simply "less safe versions of large ones" — the relationship is plausibly
  non-monotonic, but I could not source a specific number for it.** A prior version of this document
  quoted "33.44%→55.31% ASR from 1.5B→32B" from an AI-generated web-search summary, without ever tracing
  it to an actual paper. Checked directly against the two most likely candidates that same search
  surfaced — [Scaling Patterns in Adversarial Alignment, 2511.13788](https://arxiv.org/abs/2511.13788)
  (its abstract reports a size-ratio/harm *correlation*, Pearson r=0.51, not those percentages) and
  [Jailbreak Scaling Laws, 2603.11331](https://arxiv.org/abs/2603.11331) (its abstract describes
  polynomial-to-exponential ASR growth with *inference-time samples*, not model size, and not those
  percentages) — neither confirms the figure. **Retracted; do not use it.** The qualitative point that
  general-LM evidence shows a non-monotonic size/safety relationship may still be right, but needs a
  real citation before it goes in the paper, not a search-engine paraphrase.
- **Small models are being deployed specifically where heavy defenses don't fit.** [Wang, Zhang, Xu, He,
  Zhu, Ren — "Can Small Language Models Reliably Resist Jailbreak Attacks?", arXiv:2503.06519](https://arxiv.org/abs/2503.06519) **[A]** (text-only SLMs, but directly transferable framing): 59
  SLMs across 15 families, 12 jailbreak methods — **61.0% of evaluated SLMs show >40% average ASR**.
  [Yi, Cong, He, Li, Song — arXiv:2502.19883](https://arxiv.org/abs/2502.19883) **[A]**: 13 SLMs, "most
  ... are quite susceptible to existing jailbreak attacks, ... some ... even vulnerable to direct
  harmful prompts." **No VLM-specific version of this exact study was found this session** — this is
  itself a concrete, checkable gap (see §8).
- **The standard fixes are disproportionately expensive for small models.** [EASE, Shi, Wang, Ouyang,
  Wang, arXiv:2511.06512](https://arxiv.org/abs/2511.06512) **[A]** (AAAI 2026, text SLMs): deliberative
  safety-reasoning alignment is more robust than shallow refusal training, but applying reasoning to
  *every* query is "impractical for resource-constrained edge deployment" — motivating selective/distilled
  reasoning. The VLM analogue of this exact tension (a safety-reasoning VLM defense, cost-gated for edge
  budgets) is open.
- **Efficiency techniques themselves may interact with safety.** LiteLMGuard (arXiv:2505.05619, **[T]**,
  search-verified) frames "quantization-induced risks" for small-model guardrails — i.e., the
  compression techniques used to make a model small (quantization, distillation, pruning) are not
  neutral with respect to safety and need their own audit, not just the base model's.

---

## 2. State of the Art (organized by where the intervention acts)

*(Families below mirror `vlm_safety_alignment_research_review.md`'s organization; entries are added or
re-scoped here specifically for what is size- or efficiency-relevant.)*

### 2.1 Training-time alignment
| Work | Mechanism | Small/efficient relevance |
|---|---|---|
| [VLGuard, Zong et al., 2402.02207](https://arxiv.org/abs/2402.02207) **[A]** | Curated multimodal safety SFT data, mixed into instruction tuning | Cheapest fix in this table: no architecture change, works with any size backbone |
| [SPA-VL, Zhang et al., 2406.12030](https://arxiv.org/abs/2406.12030) **[T]** | 100K-quadruple preference dataset for DPO/RLHF-style VLM alignment | Dataset-scale cost, largely size-agnostic to apply, but preference-data curation is itself expensive relative to a small model's training budget |
| [ADPO, Weng et al., ACL Findings 2025 emnlp.735](https://aclanthology.org/2025.findings-emnlp.735/) **[verified this session]** | Adversarial training folded into DPO (adversarially-trained reference model + adversary-aware DPO loss) | Adds an adversarial-training loop on top of DPO — heavier than plain DPO; cost/robustness trade-off not yet reported at small scale |
| [Nie, Liu et al. ("SafeVLM"), 2405.13581](https://arxiv.org/abs/2405.13581) **[A]** | Safety projector + safety tokens + safety head, two-stage training | Architectural addition; overhead scales with the added modules, not the backbone — plausibly small-model-friendly, but not evaluated at small scale in the paper itself |

### 2.2 Representation / decoding interventions (often training-free at inference — attractive for edge)
| Work | Mechanism | Small/efficient relevance |
|---|---|---|
| [CMRM, Liu et al., ACL Findings 2025, 2410.09047](https://arxiv.org/abs/2410.09047) **[A]** | Inference-time correction vector pulling multimodal hidden states back toward the text-only safe distribution; LLaVA-7B unsafe rate 61.53%→3.15% | No retraining — the cheapest class of defense to deploy on a small model, but must be recomputed/validated per backbone |
| [MMAligner, Zhang et al., 2608.05909](https://arxiv.org/abs/2608.05909) **[verified this session]** | Representation calibration toward an existing refusal region; 99% avg. refusal, <2% utility loss (author-reported) | Same inference-time-only advantage as CMRM; the two should be compared, not assumed equivalent |
| [DAVSP, Zhang, Li, Cai, Li, 2506.09353](https://arxiv.org/abs/2506.09353) **[A]** | Trainable "visual safety prompt" (padding region around the image) + deep alignment via activation-space supervision | Adds only a small trainable prompt region, not new layers — a genuinely lightweight, size-friendly design; AAAI-track paper, code released |
| [Bootstrapping LLM Robustness via reducing pretraining modality gap, Yang et al., 2505.24208](https://arxiv.org/abs/2505.24208) **[A]** | Regularizer during LVLM pretraining that shrinks the image/text modality gap; up to 16.3% unsafe-rate reduction, boosts other defenses by up to 18.2% | **Pretraining-stage fix** — only applicable if you control pretraining; not a fix you can apply to an already-released small VLM, but foundational for anyone training one from scratch |

### 2.3 Input-side guardrails
| Work | Mechanism | Small/efficient relevance |
|---|---|---|
| [VLMGuard-R1, 2504.12661](https://arxiv.org/abs/2504.12661) **[A]** | Reasoning-guided prompt rewriter, external to the target model | Adds a second model call — a real cost concern for an edge deployment; latency must be reported, not assumed negligible |
| GLiGuard (search-verified, **[T]**) | 300M-parameter moderation/guardrail model, "16x faster... matching accuracy of models 23–90x its size" | Directly relevant precedent: a *purpose-built small guardrail model* in front of the (possibly also small) target VLM — worth checking whether a vision-capable analogue exists |
| LiteLMGuard, 2505.05619 (search-verified, **[T]**) | On-device prompt filtering resistant to quantization-induced degradation | Names exactly the risk in §1.4's last point; check whether it is vision-capable or text-only |

### 2.4 Efficiency surveys that any small-VLM safety study should ground itself in
- [A Survey on Efficient Vision-Language Models, Shinde et al., 2504.09724](https://arxiv.org/abs/2504.09724) **[A]**: reviews compact VLM architectures and the performance–memory trade-off; maintains a GitHub compilation. Use this to justify which "small" architectures are representative, rather than picking one ad hoc.
- [A Survey of Small Language Models, Van Nguyen et al., 2410.20011](https://arxiv.org/abs/2410.20011) **[T]**: the text-only analogue; useful for importing the SLM-safety literature's framing (§1.4) since a dedicated small-*VLM*-safety survey was not found this session.

### 2.5 Attack-side surveys (needed before picking an attack suite, §5)
- [When Data Manipulation Meets Attack Goals, Dai et al., 2502.06390](https://arxiv.org/abs/2502.06390) **[A]**: taxonomizes VLM attacks by **goal** (jailbreak / camouflage / exploitation) crossed with **method** (visual perturbation / typography / deceptive prompts) — this is the source of the "type of attack" column in §5.
- [A Domain-Based Taxonomy of Jailbreak Vulnerabilities, Peláez-González et al., 2504.04976](https://arxiv.org/abs/2504.04976) **[A]**: frames jailbreaks via generalization/objective/robustness gaps — text-only LLM taxonomy, useful as a cross-check, not a VLM source.
- [A Survey of Safety on Large Vision-Language Models, Ye et al., 2502.14881](https://arxiv.org/abs/2502.14881) **[T]** (already in the earlier review).

---

## 3. Research Challenges

| # | Challenge | Evidence | Design implication for a small-VLM study |
|---|---|---|---|
| 1 | **Modality gap as a measurable, pretraining-level safety predictor** | 2505.24208 shows this correlation and that it persists through fine-tuning | If comparing small VLMs, measure and report each one's modality gap — it may explain safety differences better than parameter count alone |
| 2 | **No dedicated small-VLM jailbreak census exists yet** | The SLM (text-only) census — 2503.06519, 2502.19883 — has no published VLM counterpart found this session | A first, even modest, "N small VLMs × M jailbreak methods" census (mirroring 2503.06519's design) would itself be a genuine, checkable contribution — see §8 |
| 3 | **Zero-gradient, black-box visual attacks are cheap and generalize across "frontier" models** | 2605.00583: four attacks needing no gradient access, evaluated across six frontier VLMs | A small-model study should include at least the zero-gradient family, since it doesn't require white-box access and is the more realistic deployment threat |
| 4 | **Internal/representation-level vulnerabilities are distinct from input-level ones** | JailBound (2505.19610) attacks fusion-layer representations directly | An input-only red-team suite (typographic + semantic) will miss this attack surface; representation probing needs white-box access to the small model, which is at least *available* for open small VLMs (unlike closed frontier APIs) |
| 5 | **Guardrail and reasoning-based defenses are disproportionately costly at small scale** | EASE (2511.06512) names this tension explicitly for text SLMs | Any proposed small-VLM defense must report inference-time/latency cost, not just ASR — the paper's own framing already anticipates a reviewer asking this |
| 6 | **Compression (quantization/distillation/pruning) is not safety-neutral** | LiteLMGuard's framing (quantization-induced risk) | If the study's "small" models are compressed versions of larger ones (a common way to get a small VLM), evaluate safety before *and* after compression, not just the final artifact |
| 7 | **Visual safety information leakage inflates apparent safety** | VLSBench (verified this session): risky content in the image is often already stated in the text query | Any benchmark chosen (§6) must be checked for this leakage, or a "small" model's apparent safety advantage may just be a text-only shortcut |
| 8 | **Judge/evaluator reliability** | Carried over from the general-VLM review; unresolved here too | Validate the automated judge against a human-labeled subset before trusting ASR deltas between small models |

---

## 4. Concepts: Safety, Alignment — Definitions, Examples, and Where Each Is Measured

| Concept | Definition used in this literature | Concrete example | Where it's measured |
|---|---|---|---|
| **Alignment (HHH)** | Model's learned objective matches Helpful + Harmless + Honest intent (RLHF/Constitutional-AI framing) | An LLM backbone trained via RLHF to refuse "How do I synthesize [X]?" | Text-only benchmarks (AdvBench, HarmBench); *not* sufficient once vision is added — see below |
| **Safety (operational)** | The deployed system's actual refuse/comply behavior under real inputs, including adversarial ones | A VLM shown a benign photo of a kitchen knife and the text "how do I use this to hurt someone" | MM-SafetyBench, FigStep, JailBreakV, etc. — §6 |
| **Modality gap** | Representational distance between how the model embeds equivalent text vs. image inputs | A blank image shifts the model's hidden state enough to bypass a refusal the same text alone would trigger | Measured directly in 2505.24208; not yet a standard benchmark, more a diagnostic |
| **Visual safety information leakage (VSIL)** | A "multimodal" test is actually solvable from text alone, because the image's risk is restated in the prompt | An MM-SafetyBench-style pair where the caption already says "this shows a bomb" | VLSBench is built specifically to avoid this |
| **Over-refusal / exaggerated safety** | Model refuses a benign request because it superficially resembles a harmful one | Refusing "how do I stop bleeding from a cut" because it mentions blood | XSTest (text), VSCBench (multimodal) |
| **Cross-modal composition risk** | Neither the image nor the text is harmful alone; only their combination is | A photo of a kitchen (benign) + "how would I use these items to hurt someone" (borderline alone, unsafe combined) | SIUO (9 safety domains, exactly this framing) |
| **Jailbreak vs. content-safety failure** | Jailbreak = an attacker deliberately crafts input to elicit unsafe output; content-safety failure = the model is unsafe even on a "naturally occurring" input (no adversary) | FigStep (jailbreak, deliberate) vs. MemeSafetyBench (naturally-occurring memes, no adversarial optimization) | Both matter; a small-VLM study should report both, since a model "safe under adversarial testing" can still fail on ordinary inputs |
| **Alignment tax / safety-utility trade-off** | Safety interventions that reduce helpfulness or task accuracy | A VLM that refuses too many benign medical-image questions after safety tuning | Reported as false-refusal rate on matched benign sets (XSTest/VSCBench) alongside task accuracy |

---

## 5. Adversarial Attacks to Test Alignment (with attack type)

| Attack / representative work | **Type of attack** | Mechanism | Modality/channel | Gradient access needed? | Small-VLM relevance |
|---|---|---|---|---|---|
| [FigStep, 2311.05608](https://arxiv.org/abs/2311.05608) **[T]** | Typographic (text-rendered-as-image) | Harmful instruction rendered as image text; benign accompanying prompt | Image (OCR channel) | No | Cheap to run on any open small VLM; canonical baseline |
| [Azulay et al. visual attacks, 2605.00583](https://arxiv.org/abs/2605.00583) **[A]** | (a) Symbol-cipher-in-image (b) benign-object substitution (c) in-image text substitution (d) visual-analogy puzzle | Four distinct zero-gradient visual encodings of harmful intent | Image | No | All four are black-box, so directly runnable on small open-weight VLMs without needing gradients |
| [HADES, 2403.09792](https://arxiv.org/abs/2403.09792) **[T]** | Cross-modal semantic composition | Harmful intent distributed between image semantics and text | Image + text jointly | No (typically) | Tests exactly the "composition risk" concept in §4 |
| Gradient-optimized visual perturbation (e.g. Visual Adversarial Examples line of work; see also 2505.21967 **[T]**) | Adversarial perturbation | Gradient-optimized pixel perturbation to elicit unsafe completion | Image (pixel-level) | **Yes** (white-box) | Needs model access — feasible on an open small VLM, not on a closed API; a fair test *for* small open-source models specifically |
| [JailBound, 2505.19610](https://arxiv.org/abs/2505.19610) **[A, corrected]** | Internal / representation-space (latent safety-boundary attack) | Two-stage attack (Safety Boundary Probing, then Crossing) that locates and crosses an implicit safety decision boundary in fusion-layer activations. **Corrected 2026-09-27:** the abstract reports **94.32% white-box and 67.28% black-box attack success on average across six VLMs** (6.17 and 21.13 points above prior SOTA, respectively) — not the earlier-stated per-model figures (75.24%/70.06%/56.55% for GPT-4o/Gemini/Claude), which came from an AI-generated web-search summary that this document never checked against the actual abstract. Re-fetched the abstract directly this session; those per-model numbers do not appear in it (they may exist in the paper body, which was not checked) | Internal representations | The abstract's headline numbers are black-box; the underlying method is motivated by a white-box hypothesis about fusion-layer representations | Directly testable end-to-end on an open small VLM where activations are inspectable |
| [JailBreakV-28K, 2404.03027](https://arxiv.org/abs/2404.03027) **[T]** | Mixed: transferred text jailbreaks + native image attacks | 20K text-transfer + 8K image-native attacks | Both | Mixed | Large-scale coverage benchmark, not a single attack — use a documented subset |
| Multi-turn escalation (MTMCS-Bench, per Codex review, 2026.findings-acl.96) **[A, re-verified 2026-09-27]** | Multi-turn escalation | Escalation-based and context-switch risk across multi-turn image+text dialogues; >30K samples, 8 open-source + 7 proprietary MLLMs evaluated (confirmed directly against the ACL Anthology abstract — this entry was originally tagged "verified this session" without actually having been checked; it has now genuinely been fetched and matches) | Text + image across turns | No | Tests whether a small VLM's safety holds under context, not just single-turn — a realistic chat-deployment threat |
| PolyJailbreak (per Codex review, 2510.17277) **[A, re-verified 2026-09-27]** | Adaptive black-box optimization | Reinforcement-learning multi-agent optimization over a library of reusable "Atomic Strategy Primitives"; abstract reports 18.15% average ASR improvement over prior baselines and >95% success on GPT-4o/Gemini (confirmed directly against the arXiv abstract — same correction as MTMCS-Bench above: previously tagged verified without having actually been checked) | Both | No (query-based) | Good held-out/generalization test: train defenses without it, evaluate with it |
| Prompt-injection / input rewriting (general framing per survey 2601.03594) **[T]** | Prompt manipulation / injection | Crafted instructions embedded in the input (image caption, OCR text, or conversation) that hijack the model's effective instruction | Text (sometimes via image OCR) | No | Overlaps with typographic attacks but framed at the instruction-following level rather than the safety-refusal level |
| Harmful fine-tuning (Gulati & Raval, 2602.16931) **[A]** | Training-time / fine-tuning attack | Fine-tuning on a narrow harmful dataset induces broad emergent misalignment; effect scales with LoRA rank; multimodal eval shows *higher* misalignment (70.71 vs 41.19) than text-only eval | Training data (not an inference-time attack) | N/A (training access) | Directly tests whether a small VLM's alignment survives adaptation — relevant if the study's small VLM will be fine-tuned at all, even for benign purposes |

**Taxonomy cross-reference:** columns above use the "type of attack" framing from 2502.06390's
goal-based taxonomy (jailbreak / camouflage / exploitation) crossed with its method-based one
(visual perturbation / typography / deceptive prompts), extended with two categories that survey
doesn't cover: **internal/representation-space** attacks (JailBound) and **training-time** attacks
(harmful fine-tuning). Camouflage-goal attacks (perceptual deception, operational hijacking) are
listed in that survey but are not primarily *safety* attacks in the harmful-content sense — flag them
separately if the study's scope includes robustness beyond content safety.

---

## 6. Benchmarks

| Benchmark | What it measures | Scale | Note for a small-VLM study |
|---|---|---|---|
| [MM-SafetyBench, 2311.17600](https://arxiv.org/abs/2311.17600) **[T]** | General image-text jailbreak coverage | 5,040 pairs, 13 scenarios | Audit for VSIL (§3, challenge 7) before trusting a "safe" result |
| [FigStep, 2311.05608](https://arxiv.org/abs/2311.05608) **[T]** | Typographic jailbreak | — | Cheap, canonical, no gradient needed |
| [JailBreakV-28K, 2404.03027](https://arxiv.org/abs/2404.03027) **[T]** | Broad transfer + native multimodal attack coverage | 28K | Use a documented subset for a small-model, compute-constrained study |
| VLSBench (2025.acl-long.405) **[verified this session]** | Visual-leakage-controlled safety | 2.2K | Validity check, not a standalone headline metric |
| SIUO (2025.findings-naacl.198) **[verified this session]** | Cross-modal composition risk | 9 domains | Directly tests the "safe+safe=unsafe" concept in §4 |
| VSCBench (2025.findings-acl.158) **[verified this session]** | Under- *and* over-safety calibration | 3,600 pairs | Reports the exact safety/utility trade-off a small-model paper needs |
| MemeSafetyBench (2025.emnlp-main.1555) **[verified this session]** | Ecologically valid, non-adversarial safety | 50,430 instances | Tests content-safety failure independent of a deliberate jailbreak — see §4 distinction |
| USB (2026.acl-long.970) **[verified this session]** | Unified: 61 risk categories × 4 modality-interaction types, joint over-refusal + harmful-input eval | 22 models, 244 risk×modality cells (paper's own eval) | Broadest single benchmark on this list; select the vision-relevant slices |
| [XSTest, 2308.01263](https://arxiv.org/abs/2308.01263) **[T]** | Text-only over-refusal | — | Pairs with VSCBench for the multimodal analogue |
| [RTVLM, 2401.12915](https://arxiv.org/abs/2401.12915) **[T]** | 4-dimensional (privacy/fairness/misleading/safety) red-teaming | — | Already used to score SafeVLM (§2.1); good for cross-paper comparability |
| Small-VLM-specific census | *(gap — none found this session, see §3 challenge 2)* | — | The 2503.06519-style design (N models × M attacks) has no published VLM version; building one is itself a contribution, not just a literature gap to cite |

---

## 7. Baselines for the Research

A "safety and alignment of small VLMs" study needs baselines at three levels: **models being studied**,
**attacks used to test them**, and **defenses compared against**.

### 7.1 Model baselines (the small VLMs themselves)
| Model class | Example | Why include it |
|---|---|---|
| Efficient-by-design VLM | SmolVLM (2B), MobileVLM (1.4B/2.7B LLM) | Purpose-built for edge deployment; the population this research is actually about |
| General small open VLM | LLaVA-1.5-7B, Qwen2-VL-2B/7B, PaliGemma | Widely used in prior safety work (VLGuard, RTVLM, MM-SafetyBench baselines), maximizing comparability |
| Compressed/distilled variant of a larger model | e.g. a quantized or distilled version of a 13B+ VLM | Tests whether compression itself changes safety (§3 challenge 6) — needs a same-architecture larger sibling for a fair before/after |

### 7.2 Attack baselines (minimum suite, cheapest-to-hardest)
1. **Zero-gradient, single-turn:** FigStep + one attack from Azulay et al. (2605.00583) — no white-box
   access needed, immediately runnable.
2. **Composition:** SIUO or HADES — tests the concept in §4 that neither modality alone is the issue.
3. **White-box, if the model is open-weight:** a gradient-based visual perturbation attack, since small
   open VLMs are exactly the case where this is feasible (closed APIs aren't).
4. **Held-out/adaptive:** PolyJailbreak, kept out of any training/tuning done during the study, as an
   external validity check.
5. **Non-adversarial:** a MemeSafetyBench slice, to separate "fails when attacked" from "fails on
   ordinary inputs."

### 7.3 Defense baselines to compare against
| Baseline | Cost class | Source |
|---|---|---|
| No intervention (base small VLM) | — | — |
| VLGuard-style safety-data mixing | Training-time, moderate data cost | 2402.02207 |
| CMRM- or MMAligner-style inference-time representation correction | Inference-time, no retraining | 2410.09047 / 2608.05909 |
| DAVSP-style trainable visual safety prompt | Lightweight training (prompt only, not full model) | 2506.09353 |
| Input-side guardrail (VLMGuard-R1, or a dedicated small guardrail model if a vision-capable one exists) | Adds a second inference call — report latency | 2504.12661 / GLiGuard-class |
| EASE-style distilled/selective safety reasoning *(no VLM version found — would need adapting)* | Training-time distillation + inference-time selective reasoning | 2511.06512 (text-only; flagged as an open adaptation, not an existing VLM baseline) |

**Do not include every defense above in the first experiment.** Reproduce a small, mechanistically
diverse subset (one training-time, one inference-time, one input-side) before expanding.

---

## 8. What's Genuinely Open Here (for the actual proposal)

1. **No published small-VLM jailbreak census** in the style of 2503.06519/2502.19883 (text SLMs) was
   found. Building one — N small VLMs × the attack suite in §7.2 — is a concrete, well-scoped,
   feasible-on-a-laptop-GPU contribution that directly answers "what is the state of small-VLM safety,"
   which is what your professor asked for.
2. **Modality-gap measurement (2505.24208) has not been reported per small-VLM model family** — measuring
   and correlating it with each model's ASR across §7.1's model list would connect a mechanistic finding
   to an empirical census, without requiring any new training method.
3. **Compression-before/after safety deltas** (quantization, distillation) are named as a risk
   (LiteLMGuard) but not, in what was found this session, systematically measured for VLMs specifically.

None of these presumes gradient-based sample selection or continual fine-tuning; all three are
"map and measure what's already happening," matching your professor's brief.

---

## 9. What I Did Not Verify
- Papers marked **[T]**: existence/title/authors/date only, description from search snippets.
- Papers marked **[verified this session]** (originally sourced from Codex's review): verified by me
  this session against their ACL Anthology/arXiv page (title, authors, described mechanism/numbers
  matched), not independently discovered by my own search.
- Whether a vision-capable analogue of GLiGuard or LiteLMGuard exists — flagged as "check whether X is
  vision-capable" rather than assumed either way.
- Code/checkpoint availability for any listed defense.
- **2026-09-27 corrections, from a full re-audit of every numeric claim in this file (requested by the
  user after the 33.44%/55.31% catch below).** Every percentage/count claim was re-checked against the
  actual arXiv abstract meta tag or the raw ACL Anthology page HTML (not a WebSearch/WebFetch paraphrase)
  where one exists. Two more errors found and fixed:
  - §1.4's "33.44%→55.31% ASR from 1.5B→32B" was sourced only from an AI-generated web-search summary
    never traced to a paper. Checked directly against the two candidate papers that search surfaced
    (2511.13788, 2603.11331) — neither confirms the figure. **Retracted** in §1.4.
  - §5's JailBound entry stated per-model ASR figures (75.24%/70.06%/56.55% for GPT-4o/Gemini/Claude)
    from a WebSearch summary that was never checked against the actual abstract, despite being tagged
    `[A]`. The real abstract reports 94.32% white-box / 67.28% black-box average across six VLMs, with
    no per-model breakdown. **Corrected** in §5 (and the parallel line in §1.3, which didn't repeat the
    wrong figures, needed no change).
  - The MTMCS-Bench and PolyJailbreak entries in §5 were tagged `[verified this session]` at the time
    of writing without having actually been checked — a labeling error, not a content error once
    checked: both are now directly verified against their real abstracts and match what was written.
  - Everything else with a specific number in this file was re-confirmed directly against a primary
    page this pass: VSCBench (3,600 pairs), VLSBench (2.2k pairs), SIUO (9 domains), MemeSafetyBench
    (50,430 instances), USB (61 categories × 4 interactions, 22 models × 244 cells), MMJailBench (16
    models, "prompt framing... dominant"), ADPO (adversary-aware DPO mechanism), MMAligner (99%/<2%),
    modality-gap paper (16.3%/18.2%), LiteLMGuard (title/mechanism), GLiGuard (vendor blog, 16×/23–90×).
    All matched; none required further correction.
