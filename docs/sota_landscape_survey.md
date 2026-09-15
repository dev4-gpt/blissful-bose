# SOTA Landscape: Full Research Survey
## Continual Safety Alignment in Small VLMs via Gradient-Based Sample Selection

**Lead Researcher**: Aryaman Singh Dev (`asd5520@psu.edu`)  
**Advisor**: Prof. Thao Minh Le (`mxl6224@psu.edu`)  
**Document Policy**: Every paper has a verified source. Papers confirmed from primary search are marked ✅. Papers identified from search summaries (author-confirmed, venue-confirmed) are marked 🔍. Any claim without a source is labeled `[Source not verified]`.

---

## Why This Survey Exists

**The core gap**: No prior work combines (a) continual alignment preservation with (b) gradient-based data selection with (c) small VLMs. The three fields — continual learning for LLMs, gradient-based data selection, and VLM safety — have largely developed in parallel silos. This survey maps the full SOTA in all three pillars and identifies exactly what each paper does and does NOT address.

---

## Pillar 1: Foundational Papers (Already in Our Registry)

These are the papers directly cited in the methodology. Already fully documented in `gradient_strategy_dossier.md`.

| # | Paper | Venue / ID | Our Use |
|:--|:---|:---|:---|
| 1 | Bach et al. — *Continual Safety Alignment via Gradient-Based Sample Selection* | ACL 2026 / arXiv:2604.17215 ✅ | **PRIMARY METHOD** — the text-only LLM method we extend to VLMs |
| 2 | Peng et al. — *Navigating the Safety Landscape* (Safety Basin / VISAGE) | NeurIPS 2024 / arXiv:2405.17374 ✅ | Safety Basin geometry; VISAGE metric for evaluating basin retention |
| 3 | Ji et al. — *Language Models Resist Alignment* (Elasticity) | arXiv:2406.06144 ✅ | Theoretical grounding for WHY fine-tuning reverses alignment |
| 4 | Liu et al. — SafeVLM | arXiv:2405.13581 ✅ | Architectural safety (Safety Projector + Tokens + Head) for VLMs |
| 5 | VLMGuard-R1 | ACL 2026 / arXiv:2504.12661 ✅ | Input-stage proactive guardrail via reasoning-driven prompt rewriting |
| 6 | Gong et al. — FigStep | arXiv:2311.05608 ✅ | Typographic jailbreak attack — 82.50% avg ASR |
| 7 | Liu et al. — MM-SafetyBench | arXiv:2311.17600 ✅ | 5,040 pairs, 13 scenarios — our primary eval benchmark |
| 8 | Mazeika et al. — HarmBench | arXiv:2402.04249 ✅ | Standardized red teaming evaluation |
| 9 | Li et al. — POPE | arXiv:2305.10355 ✅ | Hallucination detection (object polling) |
| 10 | Zou et al. — GCG / AdvBench | arXiv:2307.15043 🔍 | 520 harmful behaviors benchmark — our text-jailbreak baseline |
| 11 | Luo et al. — JailBreakV-28K | COLM 2024 / arXiv:2404.03027 ✅ | 28K multimodal jailbreak test cases (20K text + 8K image) |

---

## Pillar 2: Continual Learning Approaches to Safety Preservation

These papers all try to solve the same problem as Bach et al. — preserve safety during sequential fine-tuning — but with different mechanisms. These are the **primary baselines** our method must beat.

### 2.1 Unforgotten Safety (Dec 2025)
**Paper**: *Unforgotten Safety: Preserving Safety Alignment of Large Language Models with Continual Learning*  
**arXiv**: 2512.10150 🔍 (confirmed from search: Alssum, Itani, Hammoud, Torr, Bibi, Ghanem)  
**Venue**: arXiv preprint, Dec 2025  

**What it does**: Systematically evaluates standard CL techniques (regularization-based, memory-based, model-merging) applied to safety alignment in LLMs. Tests on LLaMA2-7B, Mistral-7B, and Gemma-2B across tasks GSM8K, SST2, and Code.

**Key finding**: DER (Dark Experience Replay) outperforms other CL methods at balancing safety and task utility.

**Gap relative to our work**:
- Text-only LLMs only
- Tests only on benign vs. harmful data scenarios — does NOT study fine-tuning on *entirely benign downstream tasks* (the setting Bach et al. and we study)
- Does NOT use gradient-based sample selection — applies CL methods at the optimizer level
- Does NOT address multimodal parameter spaces

**Position in our paper**: Related Work, §2. Establishes that naive CL methods are insufficient for safety because they protect task-important weights, NOT safety-critical refusal parameters. (Cite alongside Bach et al. EWC comparison: EWC HarmBench ASR 31.0% — worse than baseline 27.8%)

---

### 2.2 LARF — Layer-Aware Representation Filtering (EMNLP 2025)
**Paper**: *Layer-Aware Representation Filtering: Purifying Finetuning Data to Preserve LLM Safety Alignment*  
**Venue**: EMNLP 2025 🔍 (confirmed from search: Li, Li, Lu, Wei, Li, Shao, Sha — Shanghai AI Lab)  
**Code**: https://github.com/LLLeoLi/LARF  

**What it does**: Identifies safety-sensitive layers in the LLM, then filters fine-tuning samples based on their representations within those layers. Removes samples with safety-degrading features before training.

**How it compares to Bach et al.**:
- Both are data-centric (filter before training), not parameter-centric
- LARF: uses *layer-specific representation space* to detect harmful data samples
- Bach et al.: uses *gradient norm in parameter space* to detect alignment-reversing samples
- LARF targets *representation similarity to harmful distributions*; Bach et al. targets *gradient direction aligned with reversion vector*

**Gap relative to our work**:
- Text-only LLMs (no multimodal)
- Filters *content-unsafe* samples from fine-tuning data — designed for cases where fine-tuning data may itself be harmful
- Our target: *entirely benign downstream tasks* (e.g., medical VQA) where content is safe but gradient dynamics erode alignment
- LARF would filter nothing in a clean medical dataset; Moderate-Gi would still protect safety

**Position in our paper**: Related Work, §2. Key baseline to distinguish from — "LARF filters semantically unsafe fine-tuning data; our method filters format-mismatching samples that trigger elastic reversion regardless of semantic content."

---

### 2.3 CMRM — Cross-Modality Representation Manipulation (ACL 2025)
**Paper**: *Unraveling and Mitigating Safety Alignment Degradation of Vision-Language Models*  
**Venue**: ACL 2025 Findings 🔍 (confirmed: Liu, Shang et al., October 2024 preprint)  

**What it does**: Inference-time intervention that recalibrates multimodal hidden states by applying a correction vector that pulls them back toward the safe text-only distribution. No retraining required.

**Key result** [Source: search summary — needs primary paper confirmation]: LLaVA-7B unsafe rate on multimodal inputs reduced from 61.53% to ~3.15%.

**How it addresses the problem**:
- Identifies the "representation gap" — multimodal inputs shift hidden states away from the text distribution where safety is optimized
- At inference time: computes shift vector $\delta$ between text-only and multimodal representations at safety-sensitive layers, then applies $h_{\text{corrected}} = h_{\text{mm}} - \alpha \delta$

**Gap relative to our work**:
- **Inference-time only**: CMRM does NOT protect against fine-tuning safety erosion. If you fine-tune a VLM on new tasks, CMRM still needs to be reapplied, and the underlying alignment is now degraded.
- Does NOT address the *continual learning* setting — each new task could shift the representation space further
- Our method protects the weight space during training; CMRM corrects the representation space at inference

**Position in our paper**: Related Work, §3 (VLM Safety — Inference-Time Methods). "CMRM addresses initial alignment gap at inference time; we address continual alignment preservation during training."

---

### 2.4 VLGuard (ICML 2024)
**Paper**: *Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models*  
**Authors**: Zong et al.  
**Venue**: ICML 2024 / arXiv:2402.02207 ✅ (confirmed from search)  

**What it does**: Creates a multimodal safety SFT dataset (~2,000 images) for VLMs. Shows that mixing VLGuard data into standard fine-tuning can recover safety at near-zero cost to task performance.

**Data-centric approach**: Instead of filtering training data, VLGuard *adds* safety-curated data to the training mixture.

**Key distinction from our method**:
- VLGuard requires *access to curated safety data* mixed into every fine-tuning run — this is a data augmentation approach
- Our method requires NO additional safety data — it preserves safety by filtering from the downstream task data itself
- VLGuard is most useful when you control the training pipeline and can add safety data freely
- Our method is more applicable when you receive a fine-tuning dataset from a user or deployment context with no control over its composition

**Position in our paper**: Related Work, §3. Baseline to distinguish in our "data-centric" framing.

---

### 2.5 SPA-VL — Safety Preference Alignment Dataset (2024)
**Paper**: *SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision Language Model*  
**Authors**: Zhang et al.  
**arXiv**: 2406.12030 🔍 (confirmed from search)  

**What it does**: Large-scale preference alignment dataset for VLMs — 100,788 quadruples (question, image, chosen response, rejected response) covering 6 harm domains, 13 categories, 53 subcategories. Designed for DPO/RLHF-based safety alignment.

**Gap relative to our work**:
- SPA-VL aligns a model *from scratch* using preference data — it's an *initial alignment* strategy
- Does NOT address *continual fine-tuning* safety drift after the model is already aligned
- Requires 100K annotated quadruples — resource-heavy to create and maintain
- Our method works on any downstream fine-tuning dataset without requiring safety-labeled pairs

**Position in our paper**: Related Work, §3. "SPA-VL establishes safety via initial DPO training; our method preserves it during subsequent continual fine-tuning."

---

## Pillar 3: Gradient-Based Data Selection Methods

These papers share our gradient-signal methodology but address different goals.

### 3.1 Influence Functions (Koh & Liang, ICML 2017)
**Paper**: *Understanding Black-box Predictions via Influence Functions*  
**Venue**: ICML 2017  

**What it does**: The theoretical foundation for data selection via gradient signals. Estimates how removing a training point would affect the model's prediction via a Hessian-vector product approximation.

**Gap**: Computationally intractable for billion-parameter LLMs (requires Hessian inverse computation). Bach et al. use simple L2 gradient norm, which is orders of magnitude cheaper.

**Position in our paper**: Methods, §2.1 — establishes the gradient-as-influence-signal intuition that our method inherits.

---

### 3.2 LESS — Efficient Data Selection via Gradient Features (ICML 2024)
**Paper**: *LESS: Selecting Influential Data for Targeted Instruction Tuning*  
**Venue**: ICML 2024 🔍 (from search ecosystem)  

**What it does**: Uses compressed gradient features (low-rank projections via LoRA gradients) for efficient influence estimation. Selects training data that most improves performance on a target task.

**Goal difference**: LESS selects for *task capability*, not *safety preservation*. High-influence samples by LESS may be exactly the high-Gi samples Bach et al. discard.

**Gap relative to our work**: LESS maximizes capability; our method maximizes the capability/safety Pareto frontier.

**Position in our paper**: Related Work, §2.2 — "gradient-based selection for instruction quality, contrasted with our use for safety preservation."

---

### 3.3 IPROX — Influence-Preserving Proxies (2025)
**Paper**: Derives compressed influence-preserving proxies to make gradient-based selection scalable for large models  
**Venue**: 2025 conference 🔍 (confirmed from search, exact ID not retrieved)  

**Gap**: Targets computational efficiency of influence functions in general fine-tuning. Does not address safety/alignment preservation. Does not address multimodal models.

**Position in our paper**: Related Work, §2.2 — "scalable gradient-based selection infrastructure; our work applies gradient norms to a safety objective rather than a task-capability objective."

---

## Pillar 4: VLM Safety Architecture Papers

### 4.1 PSA-VLM — Progressive Safety Alignment (2024/2025)
**What it does**: Uses concept-bottleneck models to progressively shield VLMs from harmful visual inputs at the concept representation level.  
**Gap**: Architectural intervention requiring modification of the VLM architecture; does NOT address continual fine-tuning drift.

---

### 4.2 HiddenDetect (ACL 2025)
**Paper**: Inference-time jailbreak detection by monitoring hidden state activations  
**Venue**: ACL 2025 🔍 (confirmed)  

**What it does**: Projects hidden states at the final token position into vocabulary space via unembedding layer. Detects jailbreak attempts by analyzing refusal-related logits.

**Gap**: Detection-only at inference time; does NOT prevent alignment erosion during fine-tuning.  
**Position in our paper**: Related Work, §4 (Defense Taxonomy). "HiddenDetect catches attacks at inference; our method prevents the model from becoming vulnerable in the first place."

---

### 4.3 SafeEraser — Multimodal Machine Unlearning (ACL 2025)
**Venue**: ACL 2025 Findings 🔍 (confirmed)  

**What it does**: Uses "Prompt Decouple (PD) Loss" to surgically remove harmful knowledge from VLMs while maintaining general utility.

**Gap**: Unlearning approach assumes you know *which knowledge* to erase — requires identifying harmful content. Our method acts preemptively during fine-tuning without needing labeled harmful knowledge.

---

## Pillar 5: Multimodal Attack Benchmarks (Additional Coverage)

### 5.1 JailBreakV-28K (COLM 2024)
**arXiv**: 2404.03027 ✅ (confirmed — Luo, Ma, Liu, Guo, Xiao)  
**Size**: 28,000 test cases (20K text transfers + 8K image-based)  
**Key finding**: LLM-based text jailbreaks transfer to MLLMs at high rates — the vulnerability comes from the shared language decoder.  
**Use in our paper**: Attack evaluation. The transfer-based subset tests whether our method also protects against attacks that exploit the language backbone (not just visual injection).

---

### 5.2 AdvBench (Zou et al., 2023)
**arXiv**: 2307.15043 🔍 (confirmed: Zou, Wang, Kolter, Fredrikson — GCG attack paper)  
**Size**: 520 harmful behavior prompts  
**Method**: GCG (Greedy Coordinate Gradient) — automated adversarial suffix optimization  
**Use in our paper**: Primary ASR evaluation metric (used by Bach et al., direct comparison possible)

---

## Pillar 6: New Benchmarks We Should Add Beyond Original Plan

Based on the SOTA sweep, two new benchmarks have emerged that our evaluation should include:

### 6.1 RTVLM — Red Teaming Vision Language Models Benchmark
**Used by**: SafeVLM (arXiv:2405.13581) — SafeVLM-LLaVA scored 8.26 vs 7.92 GPT-4V  
**What it measures**: 4-dimensional safety: Privacy, Fairness, Misleading, Safety  
**Why to add**: Provides dimensional breakdown of safety — we can see *which type* of safety our method best preserves

### 6.2 XSTest — Over-Refusal Measurement
**Purpose**: Tests false positives — does the model refuse safe requests after safety training?  
**Why to add**: Any safety intervention must be measured for over-refusal. SafeVLM's own paper notes false positives on celebrity images, code, artwork. [Source: SafeVLM arXiv:2405.13581, ablation section per prior search]  
**Our use**: Measure Moderate-Gi false refusal rate — does filtering safe samples cause over-refusal?

---

## The SOTA Comparison Master Table

This table positions every relevant paper against our work. "✗" = does NOT address this dimension. "✓" = addresses it.

| Method | Modality | Continual FT Safety | Data-Centric | No Safety Data Needed | Small Model | Key Limitation |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **Our Method (Moderate-Gi VLM)** | Vision-Language | ✓ | ✓ | ✓ | ✓ | [Not yet validated experimentally] |
| Bach et al. (2026) | Text-only | ✓ | ✓ | ✓ | ✓ | Text-only (our extension target) |
| Unforgotten Safety (2025) | Text-only | ✓ | ✗ | ✗ | ✓ | Parameter-level CL; no gradient filtering |
| LARF (EMNLP 2025) | Text-only | ✗ | ✓ | ✗ | ✓ | Filters content-unsafe data; not format-mismatches |
| SafeVLM (2024) | Vision-Language | ✗ | ✗ | ✗ | ✓ | Initial alignment only; not continual FT |
| VLMGuard-R1 (ACL 2026) | Vision-Language | ✗ | ✗ | ✗ | ✓ | Input guardrail; no FT protection |
| VLGuard / Zong et al. (ICML 2024) | Vision-Language | Partial | ✓ | ✗ | ✓ | Requires curated safety data mixture |
| SPA-VL (2024) | Vision-Language | ✗ | ✗ | ✗ | ✓ | Initial DPO alignment; not continual FT |
| CMRM (ACL 2025) | Vision-Language | ✗ | ✗ | ✓ | ✓ | Inference-time only; FT still erodes alignment |
| EWC (Kirkpatrick et al.) | Text | ✗ | ✗ | ✓ | ✓ | Protects task weights ≠ safety weights; WORSE than baseline |
| KL Regularization | Text | ✗ | ✗ | ✓ | ✓ | Distributional constraint insufficient for safety |
| LESS (ICML 2024) | Text | ✗ | ✓ | ✓ | ✓ | Optimizes task capability, not safety preservation |
| HiddenDetect (ACL 2025) | Vision-Language | ✗ | ✗ | ✓ | ✓ | Inference detection only |
| SafeEraser (ACL 2025) | Vision-Language | ✗ | ✗ | ✗ | ✓ | Post-hoc unlearning; not proactive |

---

## The Three-Line Novel Contribution Summary (For Paper Introduction)

Based on this full SOTA sweep, our work is uniquely positioned at the intersection of three gaps:

1. **Bach et al. (ACL 2026)** solves continual alignment drift via gradient selection — but only for *text LLMs*. Appendix (Limitations) explicitly states VLMs are future work.
2. **SafeVLM, VLMGuard-R1, CMRM, VLGuard, SPA-VL** address VLM safety — but through *initial alignment* or *inference-time intervention*, not continual fine-tuning data selection.
3. **Unforgotten Safety, LARF** extend continual alignment to more domains — but without *gradient-norm-based* selection, and not for *multimodal* models.

**The gap we fill**: *Gradient-based sample selection applied to continual fine-tuning of Small VLMs, with multimodal parameter attribution analysis.*

---

## Papers Still Needed (Honest Gaps in This Survey)

| What's Missing | Why It Matters | How to Find |
|:---|:---|:---|
| MMHal-Bench primary citation | Used in our evaluation plan; original paper not confirmed | Search: "MMHal" hallucination evaluation VLM |
| RTVLM primary citation | Used by SafeVLM; need direct arXiv ID | Search: "Red Teaming Vision Language Models" benchmark 2024 |
| XSTest primary citation | Need for over-refusal evaluation | Search: "XSTest" over-refusal benchmark Röttger |
| Orthogonal Gradient Projection (OGD/OGPSA) | Mentioned as competing technique; need primary paper | Search: "orthogonal gradient projection safety alignment" LLM |
| Catastrophic Forgetting baseline papers | EWC (Kirkpatrick 2017), DER (Buzzega 2020) | Already well-established; add to Related Work citations |
| "Aligned Model Merging" VLM (2025) | Mentioned in search; new continual approach for VLMs | Search: "aligned model merging" VLM safety plasticity 2025 |

---

*Document version: 2026-09-15. All verified arXiv IDs confirmed from web search or primary paper access. Papers marked 🔍 have been author/venue/content confirmed from search summaries. Papers marked ✅ have had their abstracts directly verified.*
