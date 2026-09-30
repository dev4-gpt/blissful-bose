# Literature Review & Methodology Synthesis
## Continual Safety Alignment for Vision-Language Models (Claude-run search, 2026-09-25)

**Purpose.** Prof. Le asked for a review of recent SOTA and a methodology grounded in it. This is
the "Claude search" arm; the "ResearchingOS Scout" arm is audited in `PIPELINE_SCOUT_AUDIT.md`.

**How this was built (so you can judge how far to trust it).**
1. ~12 web searches across seven sub-topics (see Section 1).
2. Every paper cited below was re-fetched from its `arxiv.org/abs/<id>` page and its **title, author
   list, and date matched** the claim (`arxiv_verified.json`, 47 IDs, 0 missing).
3. Characterisations marked **[A]** come from an abstract I read in full for this review. Anything
   marked **[T]** is title/ID-verified only; my description of it is from search snippets and should
   be re-read before you cite it in the paper.
4. Verification confirms the paper *exists and is what I say it is*. It does **not** confirm that any
   reported number replicates. Numbers quoted are quotes of abstracts, nothing more.

---

## 0. Headline findings (read this first)

1. **The gap in the proposal survives, but it is narrower than the repo's own survey claims.**
   I found no paper that combines (a) VLMs, (b) *sequential/continual* fine-tuning, and (c) *per-sample
   selection* of benign data. That is an absence in one search session, not proof of absence; run one
   more sweep (Google Scholar "cited by" on Bach et al. and on DataShield) right before submission.
2. **The text-LLM competitors are newer and closer than the repo lists.** Between Bach et al.
   (arXiv 2026-04-19) and now there are several *sample-level, benign-data* filters that directly
   compete with Moderate-Gᵢ: **DataShield** (2606.00160), **SQSD** (2605.04572), **TOSS** (2603.01185).
   Older: **Bi-Anchoring** (2404.01099), **SEAL** (2410.07471). None is in the current survey.
   Reviewers will expect at least DataShield and Bi-Anchoring as baselines.
3. **A continual-setting text competitor exists:** **SafeAnchor** (2604.17691, three-domain
   medicine/law/code sequence) — parameter-space, not data-selection. Also **Unforgotten Safety**
   (2512.10150) which the repo already has.
4. **VLM-specific evidence that the problem is real and worse multimodally:** Gulati & Raval
   (2602.16931) report multimodal evaluation shows higher misalignment than text-only (70.71 vs 41.19
   at LoRA rank 128, Gemma3-4B) **[A]**, but their setup is *harmful* narrow data, not benign continual.
5. **Errors in existing repo docs** (Section 6) — OGPSA, "Aligned Model Merging" and LARF were
   described incorrectly, and one SaLoRA arXiv ID was wrong. **Fixed 2026-09-25.** (An earlier draft of
   this review also called the "Nie et al." attribution an error; that was my mistake — see §6.)
6. **Benchmark-validity risk:** VLSBench (2411.19939) argues existing multimodal safety benchmarks leak
   the harmful content into the *text* query so a text-only refusal suffices **[A]**. Since your
   proposal leans on MM-SafetyBench, this needs an explicit mitigation (Section 5.3).

---

## 1. Search coverage

| Sub-topic | Found |
|---|---|
| Safety degradation from fine-tuning VLMs | 2410.09047, 2602.16931, 2402.02207, 2501.18533, 2405.13581 |
| Continual / sequential safety preservation | 2604.17215, 2604.17691, 2512.10150, 2602.07892 |
| Benign-data selection / filtering (text) | 2404.01099, 2505.06843, 2410.07471, 2603.01185, 2605.04572, 2606.00160, 2601.07200 |
| Parameter-space / LoRA defenses | 2501.01765, 2405.16833, 2506.08473, 2603.07445, 2409.01586 |
| Theory / geometry of alignment fragility | 2405.17374, 2406.06144, 2506.05346, 2310.03693, 2502.17424 |
| Multimodal continual learning (non-safety) | 2311.16206, 2506.03189, 2607.02020 |
| VLM safety benchmarks / judges | 2311.17600, 2311.05608, 2404.03027, 2411.19939, 2506.04704, 2401.12915, 2308.01263 |
| Surveys | 2409.18169 (harmful FT, LLM), 2502.14881 (LVLM safety) |

Not searched (gaps in *my* coverage): VLM unlearning, safety RL/DPO for VLMs beyond SPA-VL, non-English
sources, industry technical reports, and papers after ~mid-Sept 2026.

---

## 2. Landscape

### 2.1 Foundations: why fine-tuning erodes safety
- **Qi et al. 2310.03693 [T]** — fine-tuning aligned LLMs compromises safety even without malicious intent. Canonical citation for "benign fine-tuning hurts".
- **Elasticity — Ji et al. 2406.06144 [A]** — post-alignment models revert toward pretraining behaviour; frames *why*. Bach et al. build on this.
- **Safety basin — Peng et al. 2405.17374 [A]** — random weight perturbations keep safety within a basin; fine-tuning can exit it. Source of VISAGE.
- **AsFT 2506.08473 [A]** — perturbations *orthogonal to the alignment direction* (aligned − unaligned weights) break safety fast; updates along it are benign ("narrow safety basin"). Directly relevant to your gradient-*direction* idea.
- **Why guardrails collapse 2506.05346 [A]** — attributes collapse to similarity between the original alignment data and the fine-tuning data (upstream factor).
- **Emergent misalignment 2502.17424 [T]** — narrow fine-tuning yields broad misalignment.

### 2.2 The data-centric line (closest to Moderate-Gᵢ) — all text-only LLMs
| Method | Signal | Direction of selection | Note |
|---|---|---|---|
| **Bach et al.** 2604.17215 [A] | per-sample gradient **norm** | drop high-norm, keep near-median | continual (Dolly→GSM8K→MedMCQA→SQuAD v2); paper states text-only + ~51% compute overhead |
| **Bi-Anchoring** 2404.01099 [A] | gradient & representation **similarity** to harmful vs safe anchors | *select* samples near harmful (to attack) / avoid them (to defend) | needs harmful & safe anchor sets |
| **Self-Inf-N** 2505.06843 [A] | outlier detection in gradient space | 100 outlier benign samples break safety | shows the *attack* side; useful as a stress test |
| **SEAL** 2410.07471 [A] | bilevel-learned data ranker | up-rank safe/high-quality | learned, heavier |
| **TOSS** 2603.01185 [A] | *token*-level loss gap, safety-degraded vs utility model | drop unsafe tokens | finer granularity than sample level |
| **SQSD** 2605.04572 [A] | sample contribution to parameter drift toward "danger-aligned" directions | drop high-risk | gradient-adjacent, mechanistic |
| **DataShield** 2606.00160 [A] | compliance-vector–based score at an auto-selected layer | drop safety-degrading | pitched as cheaper/less noisy than gradient methods |
| **DualSelect** 2606.09866 [A] | coupled selection of task samples *and* safety references, minimax view | keep samples compatible with the induced reference direction | 1B–8B LLMs; abstract claims ≥5.10-point Safety Avg. gain over strongest baseline (their judge) |
| **LARF** 2507.18631 [A] (EMNLP 2025) | representations in safety-sensitive layers vs safe/unsafe references | drop benign samples with safety-degrading features | single-task; text-only; **direct competitor** |
| **Push-Pull OT (SOT)** 2601.07200 [A] | optimal-transport distribution alignment | distribution-level, not instance | argues instance heuristics ignore global geometry |
| **ForgetFilter** 2312.12736 [A] | which examples the model forgets most | filter unsafe data | targets *unsafe* content in noisy data |

**Takeaway for the paper:** Bach et al.'s novelty was "gradient-norm, keep the median". By Sept 2026
that idea is one of ~8 selection signals. The VLM contribution therefore needs to stand on the
*multimodal* question (which parameter group's gradient predicts drift?), not on "gradients help".

### 2.3 Parameter- / optimiser-side defenses
- **SafeAnchor 2604.17691 [A]** — Fisher-information low-rank safety subspaces in LoRA space, project domain gradients to the orthogonal complement, plus drift-triggered replay. Abstract claims 93.2% safety retention on Llama-2-7B-Chat / Mistral-7B, three-domain sequence. **Strongest continual-setting baseline; text-only.**
- **SaLoRA 2501.01765 [A]** (ICLR 2025), **Safe LoRA 2405.16833 [A]** — LoRA projected/initialised to preserve safety subspace. Your deck already cites SaLoRA.
- **Few-Tokens 2603.07445 [A]** — constrain updates on a small set of safety-critical tokens.
- **OGPSA 2602.07892 [A]** — *see correction §6*: this is about the **alignment tax** (safety updates overwriting capability), not preventing fine-tuning from eroding safety.
- **Unforgotten Safety 2512.10150 [A]** — treats safety preservation as CL; evaluates regularisation / replay / merging families on LLMs.
- **Merging:** SafeMERGE 2503.17239 [A] (selective layer merge post-FT), Model Merging & Safety 2406.14563 [T].

### 2.4 VLM-specific safety
- **Safety degradation from adding vision — CMRM 2410.09047 [A]:** multimodal inputs shift representations away from the text distribution the LLM was aligned on ("representation gap"); inference-time correction.
- **VLGuard 2402.02207 [A]:** finds harmful data in VL instruction-tuning data and that VLLM fine-tuning can cause *forgetting of the LLM's safety alignment*; releases a safe-instruction dataset, mixed into fine-tuning. **This is the closest VLM statement of your exact problem** and should be positioned as the primary VLM motivation + a *replay-style baseline*.
- **Liu et al. 2405.13581 [A]:** safety projector + safety tokens + safety head, two-stage; LLaVA-v1.5 RTVLM score 8.26 (abstract). *Attribution note in §6.*
- **Ding et al. 2501.18533 [A]:** safety fine-tuning of VLMs lacks visual safety *reasoning*; multi-image + safety-CoT dataset (MIS).
- **VLMGuard-R1 2504.12661 [A]:** input-side reasoning-driven prompt rewriting.
- **HoliSafe 2506.04704 [A]:** holistic image-text safety dataset/benchmark plus architectural change.
- **SPA-VL 2406.12030 [T]:** 100K preference-alignment set for VLMs (initial alignment).
- **Gulati & Raval 2602.16931 [A]:** narrow harmful fine-tuning of Gemma3-4B; misalignment grows with LoRA rank; multimodal eval > text-only eval; even 10% harmful data hurts.
- **Audio analogue 2604.16659 [A]:** benign fine-tuning breaks safety in Audio LLMs using proximity-to-harmful filtering; its abstract states prior work shows benign fine-tuning degrades safety in *text and vision* — a useful pointer, but I did not locate the vision reference it refers to. **Chase that citation.**
- **Surveys:** LVLM safety survey 2502.14881 [T]; harmful-FT survey 2409.18169 [T] (LLM-only).

### 2.5 Multimodal continual learning (utility side, not safety)
- **Continual Instruction Tuning for LMMs 2311.16206 [A]** — asks whether LMMs forget in continual instruction tuning and how existing CL methods fare; a benchmark-style reference for your task sequence.
- **Aligned Model Merging for VLM CL 2506.03189 [A]** — stability/plasticity via merging in VLMs; *no safety focus* (§6).
- **Hidden Forgetting 2607.02020 [A]** — accuracy survives but evidence-use (visual vs text/OCR) shifts. **Relevant to your modality-tension diagnostic**: it gives a precedent for measuring *how* a VLM uses each modality, not just answers.

### 2.6 Benchmarks & judges
- **MM-SafetyBench 2311.17600 [T]**, **FigStep 2311.05608 [T]**, **JailBreakV 2404.03027 [T]**, **HarmBench 2402.04249 [T]**, **RTVLM 2401.12915 [T]**, **XSTest 2308.01263 [T]**, **MMHal 2309.14525 [T]**.
- **VLSBench 2411.19939 [A]:** *visual safety information leakage* — risky content in the image is often already stated in the text query, so text-only refusals look safe. Also reports that textual unlearning matches image-text alignment on those benchmarks.
- Judge reliability: search snippets indicate Llama-Guard-3 (text) and even the vision variant can fail to perceive image-borne risk; Llama Guard 4 is natively multimodal. **[unverified — snippet only; read the source papers before asserting this]**

---

## 3. Gap analysis

| Requirement | Closest existing work | What is missing |
|---|---|---|
| VLM + benign fine-tuning drift | VLGuard, Gulati & Raval, CMRM | Gulati uses *harmful* data; VLGuard uses *safety-data mixing*; CMRM is inference-time |
| Continual (multi-task) safety | SafeAnchor, Unforgotten Safety, Bach | all text-only |
| Sample selection for safety | DataShield, SQSD, TOSS, Bi-Anchoring, SEAL, Bach | all text-only; none studies *which modality's parameters* drive the signal |
| **All three together** | — (none found) | **This project** |

**Two defensible novelty claims, ranked by how well the evidence supports them:**
1. *Empirical:* first measurement of whether gradient-based drift prediction transfers from LLMs to
   small VLMs. A negative result is publishable and is the honest baseline expectation — see §4.
2. *Analytical:* parameter-group attribution (language-LoRA vs projector vs joint) of the selection
   signal. This is the part with no precedent in the papers above.

---

## 4. Risks a reviewer will raise (and what the literature says)

1. **"Gradient norm is not the only, or best, signal."** DataShield and SQSD argue for
   compliance/direction-based scores; Bi-Anchoring uses direction. Include at least one
   direction-based baseline; SQSD/DataShield are the newest.
2. **Bach et al.'s mechanism is "format mismatch"** (short targets vs verbose aligned outputs). VLM
   tasks in your sequence (VQA-RAD, DocVQA) are short-answer by construction, so *many* samples may be
   high-norm for format rather than safety reasons. Report the fraction dropped per task and audit a
   sample, as Bach et al. do, or the method may just be a length filter. Add a **length-matched
   random** control.
3. **Compute overhead.** Bach et al. state ~51% overhead. VLM per-sample gradients through a vision
   tower are heavier; restricting to LoRA/projector params (your Gᴸ, Gᴾ, Gᴶ) is the right mitigation
   and should be reported as cost, not hidden.
4. **Small-model / limited-compute credibility.** Gulati & Raval show effects scale with LoRA rank;
   results at r=16 on a 2B model may not generalise. State the scope.
5. **Benchmark leakage (VLSBench).** See §5.3.
6. **Seed/variance.** Selection at ρ=0.2 on 4 tasks is cheap to replicate; report ≥3 seeds and CIs.

---

## 5. Methodology synthesis (what to run)

### 5.1 Setting
Base: Qwen2-VL-2B-Instruct (as in the repo). Sequence: LLaVA-Instruct → MathVista → VQA-RAD/SLAKE →
DocVQA (task analogues of Dolly→GSM8K→MedMCQA→SQuAD v2). *I verified the Bach sequence from the
paper; the VLM analogue mapping is your design choice, not something from the literature.*

### 5.2 Methods to compare
| Group | Method | Source |
|---|---|---|
| Reference | Standard sequential FT; Random-ρ; **length-matched random** | — |
| Ours | Moderate-Gᵢ with Gᴸ / Gᴾ / Gᴶ attribution | 2604.17215 (+ your extension) |
| Selection baselines | High-Gᵢ, Low-Gᵢ (Bach ablations); **LARF**; **Bi-Anchoring**; **DataShield**; **SQSD**; **DualSelect** (as compute allows) | 2507.18631, 2404.01099, 2606.00160, 2605.04572, 2606.09866 |
| Parameter-space | **SafeAnchor**, **SaLoRA** / Safe LoRA, AsFT | 2604.17691, 2501.01765, 2405.16833, 2506.08473 |
| Data-mixing | **VLGuard replay** (safe VL data mixed in) | 2402.02207 |
| CL classics | EWC, gradient clipping, KL-reg (as Bach) | as in Bach et al. |

Cost note: DataShield, SQSD, SafeAnchor each need their own implementation or released code — check
for official repos before committing; I did not verify code availability.

### 5.3 Evaluation
- **Safety (ASR):** MM-SafetyBench, FigStep, JailBreakV subset, HarmBench text slice (as Bach).
  **Mitigation for leakage:** add **VLSBench** and report MM-SafetyBench results *split* into
  "text query alone is refusable" vs not (a text-only baseline pass), so image-dependence is explicit.
- **Over-refusal:** XSTest, plus refusal rate on benign task inputs, to avoid rewarding a model that
  refuses everything (already in your slide 23).
- **Capability:** per-task score after each stage; BWT and forgetting (FM) as in Bach.
- **Basin metric:** VISAGE per Peng et al. (needs perturbation sweeps; report cost).
- **Multimodal diagnostics (your slides 26–29):** modality-reliance profile after each task, following
  the counterfactual-channel idea in Hidden Forgetting (2607.02020); representation-gap tracking à la
  CMRM (2410.09047).
- **Judge:** use a multimodal judge (image + instruction + response), keep raw responses, and audit a
  stratified manual sample per attack category with inter-annotator agreement. Validate the judge
  itself on a small human-labelled set before trusting ASR deltas.
- **Stats:** ≥3 seeds, bootstrap CIs, paired tests across selection methods on identical task orders;
  vary task order (Bach et al. do).

### 5.4 Ablations that would carry the paper
1. Attribution group: Gᴸ vs Gᴾ vs Gᴶ (and layer-restricted variants).
2. ρ ∈ {0.1, 0.2, 0.4} (Bach: robust in [0.1,0.4] on text).
3. Norm vs direction (cosine to a safety/alignment direction — AsFT-style) as the score.
4. Fraction of dropped samples that are format-mismatch vs semantic outliers (manual audit).
5. Text-only vs multimodal evaluation gap, mirroring Gulati & Raval's observation.

### 5.5 Pre-registered honest expectations
Hypothesis H1 (transfer): Moderate-Gᵢ reduces ASR vs standard FT on the VLM. H2 (attribution): the
projector-inclusive signal outperforms language-only. **State up front that H1 or H2 may fail;** the
ResearchingOS repo's own experiments found negative results informative (its HANDOFF.md), so frame a
null result as a contribution rather than hiding it.

---

## 6. Corrections to existing repo documents

| Where | Existing claim | What I found | Action |
|---|---|---|---|
| `docs/sota_landscape_survey.md` #2.6, master table; deck slide 31 refs | OGPSA = "Orthogonal Gradient Projection for Continual Safety Alignment"; projects downstream gradients away from safety-critical gradients | Actual title *"Safety Alignment as Continual Learning: Mitigating the Alignment Tax via Orthogonal Gradient Projection"* (2602.07892). It projects **safety updates orthogonal to a capability subspace** — the reverse role, addressing capability loss from safety training | Rewrite entry; do not list as a continual-safety-preservation baseline. **Better baseline: SafeAnchor** |
| survey #2.7 & master table | arXiv 2506.03189 = "Aligned Model Merging: Preserving Safety and Plasticity in Large Models", safety-restoring merge, tagged "Vision-Language" | Actual: *"Continual Learning in Vision-Language Models via Aligned Model Merging"* (Sokar et al.). Stability/plasticity, **no safety focus** | Retitle; move to §2.5 (multimodal CL). Use SafeMERGE / 2406.14563 for safety merging |
| README, survey Pillar 1 #4, deck slides 2 & 7 | 2405.13581 = "SafeVLM" by **Nie et al.** | **RETRACTED — not an error.** The paper's own PDF (v1) lists Yuanbi Nie first (∗ equal contribution) then Zhendong Liu, and uses the name "SafeVLM" 55 times. Only arXiv's *metadata* lists Liu first. | Kept as "Nie et al.", matching the PDF the deck cites. In the bibliography, use the author order from the version you cite and check for an equal-contribution note |
| survey §2.2 LARF | LARF "filters *content-unsafe* samples… would filter nothing in a clean medical dataset" | **Wrong.** LARF (arXiv 2507.18631, EMNLP 2025) abstract: it identifies *benign* data with safety-degrading features. It is a direct competitor in the same regime as Moderate-Gᵢ | Fixed; LARF is now a required baseline |
| `docs/methodology_comparison.md`, `MASTER_RESEARCH_COMPENDIUM.md` | SaLoRA = arXiv 2501.01774 | 2501.01774 is an unrelated RL paper. SaLoRA is **2501.01765** (Li, Mingjie et al.) | Fixed |
| survey header | "Every paper has a verified source … ✅ marks primary confirmation" | Two of the ✅ entries above were wrong in substance | Do not treat ✅ in that file as verification |
| survey Pillar 2 items marked 🔍 | LARF, CMRM numbers (61.53%→3.15%), LESS, IPROX, PSA-VLM, HiddenDetect, SafeEraser | I did not re-verify these; CMRM's 2410.09047 exists and the mechanism matches, but I did not check the quoted numbers | Verify each against the PDF before use |
| README | Bach et al. is "ACL 2026 Findings" | **Correct** — the arXiv abs page for 2604.17215 states "ACL 2026 (Findings)". (My earlier "unverified" note was wrong; ACL Anthology search returned nothing, likely because proceedings are not yet indexed.) | None |

---

## 7. What I did NOT verify
- Any quantitative result beyond quotes from abstracts. Nothing was replicated.
- Papers marked [T] — existence/title/authors/date only.
- Foundational citations not fetched this session: EWC, LESS, Koh & Liang influence functions, LLaVA,
  MathVista, DocVQA, POPE, VQA-RAD/SLAKE, O-LoRA, LARF.
- Code availability and licences of any baseline.
- Whether the ACL 2026 camera-ready of Bach et al. differs from the arXiv v1 (venue itself confirmed on the arXiv page).

## 8. Suggested next actions
1. Read in full (not abstract): Bach et al. Appendix (sample audit), DataShield, SQSD, SafeAnchor, VLGuard, Gulati & Raval.
2. Decide the baseline set in §5.2 with Prof. Le (compute is the binding constraint).
3. Fix §6 items in `docs/`, the deck (slides 7–8, 31), and README before anything is reused.
4. Re-run the sweep for post-Sept-2026 work close to submission.
