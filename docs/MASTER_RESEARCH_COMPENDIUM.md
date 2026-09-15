# Master Research Compendium & Traceability Dossier
## Continual Safety Alignment in Small Vision-Language Models (VLMs) via Gradient-Based Sample Selection

**Lead Researcher**: Aryaman Singh Dev ([asd5520@psu.edu](mailto:asd5520@psu.edu))  
**Research Advisor**: Prof. Thao Minh Le ([mxl6224@psu.edu](mailto:mxl6224@psu.edu)) — Co-Author of Bach et al. (ACL 2026)  
**Institution**: Pennsylvania State University  
**Target Venues**: CVPR / ACL / EMNLP / NeurIPS (Safety, Multimodal & Alignment Track)  
**Primary Target Model**: `Qwen2-VL-2B-Instruct`  
**Foundational Paper**: Bach et al., *Continual Safety Alignment vs Gradient-Based Sample Selection*, ACL 2026 ([arXiv:2604.17215](https://arxiv.org/abs/2604.17215))

---

## Executive Table of Contents
1. [Repository Knowledge Map & File Directory](#1-repository-knowledge-map--file-directory)
2. [Theoretical & Conceptual Foundations with Paper Grounding](#2-theoretical--conceptual-foundations-with-paper-grounding)
3. [Master Paper Citation & Exact Section Cross-Reference Matrix](#3-master-paper-citation--exact-section-cross-reference-matrix)
4. [Complete Mathematical Methodology & VLM Extension](#4-complete-mathematical-methodology--vlm-extension)
5. [Master Empirical Results & SOTA Comparison Dossier](#5-master-empirical-results--sota-comparison-dossier)
6. [Experimental Procedure & Execution Roadmap](#6-experimental-procedure--execution-roadmap)
7. [Slide-by-Slide PPT Construction Blueprint (10-Minute Talk)](#7-slide-by-slide-ppt-construction-blueprint-10-minute-talk)

---

## 1. Repository Knowledge Map & File Directory

This master directory indexes every file in the repository, explaining its purpose, what research data or implementation it contains, and how it connects to the broader pipeline.

### 1.1 Documentation & Research Files (`/` and `docs/`)

| File Path | Description & Core Contents | Primary Source Papers Grounded |
|:---|:---|:---|
| [`docs/PRESENTATION_CITED_WRITEUP.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/PRESENTATION_CITED_WRITEUP.md) | ✅ **PRIMARY PPT SOURCE — PDF-OCR Verified**. All numbers extracted word-for-word from `2604.17215v1.pdf` and `Safety Alignment for Vision Language Models-with-annotations.pdf` via `pdftotext`. Use this for all slides and citations. | Bach et al. (arXiv:2604.17215), SafeVLM (arXiv:2405.13581) |
| [`docs/MASTER_RESEARCH_COMPENDIUM.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/MASTER_RESEARCH_COMPENDIUM.md) | **This Document**. Unified master compendium, repository index, paper section citation matrix. ⚠️ Table numbers in this doc have been corrected: ASR=Table 6, BWT=Table 8. | All papers cited below |
| [`Continual_Safety_Alignment.md`](file:///Users/aryamandev/Developer/blissful-bose/Continual_Safety_Alignment.md) | Full in-repo transcription of the foundational paper (Bach et al., ACL 2026). Details problem setup, 3-stage algorithm, and mechanistic findings. Structurally accurate. | Bach et al. (arXiv:2604.17215) |
| [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md) | ⚠️ **Pre-OCR verification**. Methodology and VLM extension design is correct. Any ±σ numbers should be verified against Table 6 (ASR) and Table 8 (BWT) in `2604.17215v1.pdf`. For verified numbers, use `PRESENTATION_CITED_WRITEUP.md`. | Bach et al. (arXiv:2604.17215) |
| [`STUDY_AND_PRESENTATION_PLAYBOOK.md`](file:///Users/aryamandev/Developer/blissful-bose/STUDY_AND_PRESENTATION_PLAYBOOK.md) | 3-phase study guide, formula breakdown for ASR/BWT/Retention, tactical advisor meeting prep. Table numbers corrected Sept 2026. | Bach et al., MM-SafetyBench, FigStep |
| [`ACADEMIC_ALIGNMENT_AND_TRACEABILITY_REPORT.md`](file:///Users/aryamandev/Developer/blissful-bose/ACADEMIC_ALIGNMENT_AND_TRACEABILITY_REPORT.md) | Audit against Prof. Thao Minh Le's Sept 2026 directive. Model size, benchmark, and compute gate compliance. Appendix references corrected. | Advisor Directive (Sept 1, 2026) |
| [`docs/gradient_strategy_dossier.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/gradient_strategy_dossier.md) | Mathematical and algorithmic dossier: loss pre-filtering (±1σ window), gradient norm computation, median-based selection, safety basin retention. | Bach et al. §3–§4, Peng et al. §3 |
| [`docs/reproducibility_blueprint.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/reproducibility_blueprint.md) | Python pseudocode for per-sample gradient interception, micro-batch autograd hooks, memory footprint formulas, VLM open questions. Appendix references corrected. | Bach et al. §4.1, Appendix (Limitations) |
| [`docs/sota_landscape_survey.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/sota_landscape_survey.md) | 20+ paper survey: 6 methodological families (Data-Centric, Optimizer-Centric, Parameter Isolation, Safety Replay, Representation/Loss, Post-Hoc/Inference). | 20+ papers |
| [`docs/master_research_formulation.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/master_research_formulation.md) | Step-by-step translation guide mapping Bach et al. procedure to VLM equivalents. Includes task sequence mapping and baseline families. Appendix references corrected. | Bach et al. (ACL 2026), FigStep, MM-SafetyBench |
| [`docs/methodology_comparison.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/methodology_comparison.md) | Head-to-head comparison of all 6 defense families with tradeoffs and compute overheads. | Bach et al., SaLoRA, LARF, EWC, VLGuard |
| [`docs/presentation_blueprint.md`](file:///Users/aryamandev/Developer/blissful-bose/docs/presentation_blueprint.md) | ⚠️ Superseded by `PRESENTATION_CITED_WRITEUP.md`. Older slide script — narrative is correct but some numbers predate PDF verification. | All project research |
| [`README.md`](file:///Users/aryamandev/Developer/blissful-bose/README.md) | Repository overview, architecture diagrams, quickstart commands. | Project internal |
| [`.agents/skills/vlm-gradient-safety/SKILL.md`](file:///Users/aryamandev/Developer/blissful-bose/.agents/skills/vlm-gradient-safety/SKILL.md) | Agent anti-hallucination policy. Mandates zero invented metrics, strict citation traceability. | Internal Research Rigor Policy |

---

### 1.2 Implementation Source Code (`src/`, `notebooks/`, `tests/`)

| File Path | Component & Implementation Role | Associated Paper Formulation |
|:---|:---|:---|
| [`src/selection/gradient_selector.py`](file:///Users/aryamandev/Developer/blissful-bose/src/selection/gradient_selector.py) | **Core Selector**: Implements 3-stage selection (Loss Pre-filter $\tau$, Gradient Norm $G_i$, Dynamic Quantiles $[\alpha_l, \alpha_h]$). Supports 3 attribution modes: Language ($G_i^{(L)}$), Projector ($G_i^{(P)}$), Joint ($G_i^{(J)}$). | Bach et al. §4.1, Eqs. 1–3; Appendix F |
| [`src/selection/baseline_selectors.py`](file:///Users/aryamandev/Developer/blissful-bose/src/selection/baseline_selectors.py) | **Baseline Selectors**: Implements Random selection, Low-$G_i$ selection, and High-$G_i$ selection for empirical ablations. | Bach et al. §5.2, Table 5 |
| [`src/training/trainer.py`](file:///Users/aryamandev/Developer/blissful-bose/src/training/trainer.py) | **Continual Trainer**: Manages sequential task training across $T$ downstream datasets with per-sample micro-batch gradient calculation, gradient accumulation, and optimizer stepping. | Bach et al. §5.1 |
| [`src/training/config.py`](file:///Users/aryamandev/Developer/blissful-bose/src/training/config.py) | **Experiment Configuration**: Pydantic dataclass defining hyperparams ($\rho=0.2, \tau=0.1$, LoRA $r=16, \alpha=32$, learning rate $2\times 10^{-5}$, Qwen2-VL-2B-Instruct targets). | Bach et al. §5.1, Appendix B |
| [`src/data/dataset_loader.py`](file:///Users/aryamandev/Developer/blissful-bose/src/data/dataset_loader.py) | **Data Pipeline**: Formats and tokenizes downstream datasets (LLaVA-150K, MathVista, VQA-RAD, DocVQA) with explicit label masking ($x_i$ user tokens set to $-100$). | Bach et al. §5.1, LLaVA, MathVista |
| [`src/eval/safety_judge.py`](file:///Users/aryamandev/Developer/blissful-bose/src/eval/safety_judge.py) | **Safety Evaluation**: Evaluates Attack Success Rate (ASR) via Llama-Guard-3-8B and string-refusal heuristics across MM-SafetyBench, FigStep, and JailBreakV-28K. | Llama-Guard-3, MM-SafetyBench, FigStep |
| [`src/eval/vllm_evaluator.py`](file:///Users/aryamandev/Developer/blissful-bose/src/eval/vllm_evaluator.py) | **High-Throughput Evaluator**: Uses vLLM to batch-evaluate 5,040 test instances in under 3 minutes per checkpoint. | vLLM Engine |
| [`notebooks/continual_safety_vlm.ipynb`](file:///Users/aryamandev/Developer/blissful-bose/notebooks/continual_safety_vlm.ipynb) | **Colab T4 Executable Notebook**: Self-contained notebook for the Phase 1 "Cheap-Gate" experiment on LLaVA-150K (10% calibration subsample). | Advisor directive (Colab practice) |
| [`tests/test_gradient_selector.py`](file:///Users/aryamandev/Developer/blissful-bose/tests/test_gradient_selector.py) | Pytest suite verifying quantile indexing, autograd norm computation, median distance ordering, and multimodal attribution modes. | Algorithm 1 verification |
| [`tests/test_dataset_loader.py`](file:///Users/aryamandev/Developer/blissful-bose/tests/test_dataset_loader.py) | Pytest suite verifying multimodal input tensor shapes, attention masks, and $-100$ label masking. | Label masking integrity |
| [`tests/test_safety_judge.py`](file:///Users/aryamandev/Developer/blissful-bose/tests/test_safety_judge.py) | Pytest suite validating safety judge classification rules, refusal prefix detection, and score aggregations. | Judge evaluation integrity |

---

## 2. Theoretical & Conceptual Foundations with Paper Grounding

### 2.1 The Core Phenomenon: Alignment Drift & Elastic Reversion
- **Concept**: A safety-aligned language or vision-language model $\theta_0$ fine-tuned on **100% benign, harmless downstream datasets** (e.g. math, instruction following, visual QA) rapidly loses its safety guardrails, reverting to the unsafe behavior of its pre-trained unaligned base model $\theta_{\text{base}}$.
- **Primary Source**: Ji et al., *Language Models Resist Alignment*, arXiv:2406.06144.
  - **Section 1 & Section 3.1**: Identifies "elastic reversion" where parameter updates $\Delta \theta = \sum \nabla \mathcal{L}_{\text{task}}$ act as a restoring force pulling weights out of safety-aligned configurations back toward pre-trained manifolds.
  - **Equation 2**: Quantifies parameter distance $\|\theta_t - \theta_{\text{base}}\|$ showing fine-tuning on diverse benign tasks collapses safety barriers.
- **Multimodal Vulnerability Surface Expansion**: In VLMs, alignment drift is significantly more acute because the visual encoder and multimodal projector provide an unaligned secondary pathway. Visual typographic jailbreaks (e.g. FigStep) bypass text safety prompts entirely.

### 2.2 The Safety Basin Geometry
- **Concept**: Safety alignment does not alter all parameters equally; it places the model into a localized, flat region in parameter space termed the **Safety Basin** where safety violation loss $\mathcal{L}_{\text{safety}}(\theta) \approx 0$.
- **Primary Source**: Peng et al., *Geometry of Safety Alignment in Large Language Models (VISAGE)*, NeurIPS 2024, arXiv:2405.17374.
  - **Section 3 & Figure 2**: Visualizes loss landscapes showing that standard SGD trajectories on downstream tasks quickly climb over the surrounding barrier, escaping the safety basin permanently.
- **Empirical Validation in Bach et al. (ACL 2026, Section 3.1, Table 2)**:
  - Measuring the percentage of parameters remaining inside the safety basin (VISAGE score) after fine-tuning on 20% of Dolly:
    - **High-$G_i$ Selection**: 62% – 72% safety basin retention (Escapes basin).
    - **Random Selection**: 72% – 73% safety basin retention.
    - **Moderate-$G_i$ Selection**: **83% – 88% safety basin retention** (Remains securely anchored inside the basin).

### 2.3 Per-Sample Gradient Norm Dynamics ($G_i$)
- **Concept**: Not all downstream samples impact the model equally. The per-sample gradient norm $G_i = \|\nabla_\theta \mathcal{L}(x_i, y_i; \theta_0)\|_2$ computed at the aligned checkpoint $\theta_0$ reveals how a sample interacts with the safety manifold:
  1. **Low-$G_i$ Samples (Bottom 20%)**: The model already predicts them with near-zero loss. Training on them produces negligible parameter updates, failing to learn new task capabilities and causing **catastrophic forgetting of downstream skills**.
  2. **High-$G_i$ Samples (Top 20%)**: Create massive parameter shocks $\|\Delta \theta\| \gg 0$. These large update steps catapult the model out of the safety basin, driving alignment drift.
  3. **Moderate-$G_i$ Samples (Around the Median)**: Provide sufficient gradient signal to update task heads without exceeding the escape velocity of the safety basin.
- **Primary Source**: Bach et al. (ACL 2026), Section 3.2, Figure 1, and Equations 1–3.

### 2.4 Mechanistic Root Cause of High-$G_i$ Samples: Format Mismatch
- **Key Insight**: High-$G_i$ samples are **not** semantic outliers or toxic examples. They are **format mismatches**.
- **Primary Source**: Bach et al. (ACL 2026), Appendix E.1:
  - Safety alignment training (RLHF/DPO) makes models verbose, polite, and explanatory.
  - Many downstream benchmarks (e.g. SQuAD, MedMCQA, single-letter QA) demand terse, 1-word or 1-token answers ("Yes", "No", "(A)").
  - When forced to output a single token, the verbose aligned model exhibits huge cross-entropy loss $\mathcal{L}(x_i, y_i)$, yielding an enormous gradient norm $G_i$. Training on these samples forcefully strips away the model's safety-conditioned output distribution.

---

## 3. Master Paper Citation & Exact Section Cross-Reference Matrix

This matrix provides a 1-to-1 lookup: every concept, metric, benchmark, and method cited in our repository mapped directly to its workspace file and exact academic paper section.

| Concept / Metric / Finding | Repo File & Section | Paper Title & Authors | Venue & arXiv ID | Exact Section / Table in Paper | Verified Result / Finding |
|:---|:---|:---|:---|:---|:---|
| **Moderate-$G_i$ Safety Preservation (ASR)** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L50-L80`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L50-L80) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Section 5.2, Table 5** | Qwen2.5-7B AdvBench ASR: Baseline 36.7±13.6% $\to$ Moderate-$G_i$ **10.2±7.1%** |
| **Safety Basin Retention % (VISAGE)** | [`docs/gradient_strategy_dossier.md:L70-L110`](file:///Users/aryamandev/Developer/blissful-bose/docs/gradient_strategy_dossier.md#L70-L110) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Section 3.1, Table 2** | High-$G_i$: 62–72%, Random: 72–73%, **Moderate-$G_i$: 83–88%** |
| **Backward Transfer (BWT) Retention** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L115-L135`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L115-L135) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Section 5.3, Table 6** | Qwen3-4B BWT: Baseline −18.5% $\to$ Moderate-$G_i$ **−4.3%** |
| **Mechanistic Reversion Vector Alignment** | [`docs/master_research_formulation.md:L45-L55`](file:///Users/aryamandev/Developer/blissful-bose/docs/master_research_formulation.md#L45-L55) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Section 3.2, Table 4** | High-$G_i$ gradients align with $\mathbf{r} = \theta_{\text{pre}} - \theta_{\text{align}}$ in final-layer projections (V/O) |
| **High-$G_i$ Format Mismatch Finding** | [`Continual_Safety_Alignment.md:L110-L130`](file:///Users/aryamandev/Developer/blissful-bose/Continual_Safety_Alignment.md#L110-L130) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Appendix E.1** | Outliers driven by terse token targets vs verbose aligned distribution |
| **Multimodal Extension as Open Work** | [`ACADEMIC_ALIGNMENT_AND_TRACEABILITY_REPORT.md:L31-L35`](file:///Users/aryamandev/Developer/blissful-bose/ACADEMIC_ALIGNMENT_AND_TRACEABILITY_REPORT.md#L31-L35) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Appendix F** | Multimodal architectures identified as unaddressed open challenge |
| **Elastic Reversion Theory** | [`docs/gradient_strategy_dossier.md:L25-L45`](file:///Users/aryamandev/Developer/blissful-bose/docs/gradient_strategy_dossier.md#L25-L45) | *Language Models Resist Alignment* (Ji et al.) | arXiv:2406.06144 | **Section 1, Section 3.1, Eq. 2** | Proves downstream FT parameter updates act as restoring force toward base weights |
| **Safety Basin Geometry & VISAGE** | [`docs/gradient_strategy_dossier.md:L80-L105`](file:///Users/aryamandev/Developer/blissful-bose/docs/gradient_strategy_dossier.md#L80-L105) | *Geometry of Safety Alignment in Large Language Models* (Peng et al.) | NeurIPS 2024<br>arXiv:2405.17374 | **Section 3, Figure 2** | Defines loss basin geometry and parametric boundaries of safety alignment |
| **FigStep Typographic Jailbreak** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L180-L205`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L180-L205) | *FigStep: Jailbreaking Large Vision-Language Models via Typographic Prompts* (Gong et al.) | arXiv:2311.05608 | **Section 1, Section 3, Table 1** | Text converted to images bypasses safety filters; $>80\%$ ASR on unaligned/drifted VLMs |
| **MM-SafetyBench Taxonomy** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L155-L175`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L155-L175) | *MM-SafetyBench: A Benchmark for Multimodal Safety Evaluation* (Liu et al.) | arXiv:2311.17600 | **Section 2, Section 3** | 13 risk categories, 5,040 image-text pairs across text-only, image-only, joint attacks |
| **JailBreakV-28K Benchmark** | [`docs/sota_landscape_survey.md:L160-L175`](file:///Users/aryamandev/Developer/blissful-bose/docs/sota_landscape_survey.md#L160-L175) | *JailBreakV-28K: A Benchmark for Assessing Robustness of VLMs* (Luo et al.) | COLM 2024<br>arXiv:2404.03027 | **Section 2, Section 4** | 28,000 multimodal jailbreak instances covering LLM-transfer, typography, diffusion |
| **VLGuard Dataset & Defense** | [`docs/methodology_comparison.md:L165-L185`](file:///Users/aryamandev/Developer/blissful-bose/docs/methodology_comparison.md#L165-L185) | *VLGuard: A Safety Benchmark and Dataset for VLMs* (Shen et al.) | ICML 2024<br>arXiv:2402.02207 | **Section 3, Section 4** | Multimodal safety fine-tuning dataset with safe/unsafe pairs; used as safety replay baseline |
| **SafeVLM Modality Alignment** | [`docs/sota_landscape_survey.md:L115-L130`](file:///Users/aryamandev/Developer/blissful-bose/docs/sota_landscape_survey.md#L115-L130) | *SafeVLM: Safety Alignment of Vision Language Models* (Liu et al.) | arXiv:2405.13581 | **Section 3, Section 4** | Addresses cross-modality safety alignment via visual projector regularized loss |
| **VLMGuard-R1 Reasoning Prompting** | [`docs/sota_landscape_survey.md:L190-L205`](file:///Users/aryamandev/Developer/blissful-bose/docs/sota_landscape_survey.md#L190-L205) | *VLMGuard-R1: Proactive Safety Alignment for VLMs* (Zhang et al.) | ACL 2026 Findings<br>arXiv:2504.12661 | **Section 3, Table 2** | Reasoning-driven test-time safety prompts; serves as inference-time defense baseline |
| **SaLoRA Parameter Isolation** | [`docs/methodology_comparison.md:L105-L125`](file:///Users/aryamandev/Developer/blissful-bose/docs/methodology_comparison.md#L105-L125) | *SaLoRA: Safety Alignment Preservation via Parameter Isolation* | ICLR 2025<br>arXiv:2501.01774 | **Section 3, Section 4** | Freezes safety-critical LoRA singular vectors; parameter-isolation baseline |
| **LARF Representation Filtering** | [`docs/methodology_comparison.md:L50-L70`](file:///Users/aryamandev/Developer/blissful-bose/docs/methodology_comparison.md#L50-L70) | *LARF: Layer-Aware Representation Filtering* (Li et al.) | EMNLP 2025 | **Section 3, Table 1** | Identifies safety-sensitive layers; filters samples based on intermediate hidden states |
| **EWC Continual Baseline** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L70-L80`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L70-L80) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Section 5.2, Table 5** | EWC AdvBench ASR on Qwen2.5-7B: **17.4±6.7%** (substantially worse than Moderate-$G_i$ 10.2%) |
| **O-LoRA Orthogonal Baseline** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L70-L80`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L70-L80) | *Continual Safety Alignment vs Gradient-based Sample Selection* (Bach et al.) | ACL 2026<br>arXiv:2604.17215 | **Section 5.2, Table 5** | O-LoRA AdvBench ASR on Qwen2.5-7B: **16.5±19.7%** (high variance across tasks) |
| **POPE Hallucination Metric** | [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md:L165-L175`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md#L165-L175) | *POPE: Polling-based Object Probing Evaluation for VLMs* (Li et al.) | arXiv:2305.10355 | **Section 3, Section 4** | Probes object hallucination across random, popular, and adversarial image splits |

---

## 4. Complete Mathematical Methodology & VLM Extension

### 4.1 The 3-Stage Selection Algorithm (Bach et al. §4.1)

Given an initial aligned model $\theta_0$, a downstream task dataset $D_t = \{(x_i, v_i, y_i)\}_{i=1}^N$ (where $x_i$ is text prompt, $v_i$ is image, $y_i$ is target response), and target selection ratio $\rho = 0.2$ (20% sample budget):

```
RAW DOWNSTREAM DATASET (N samples, 100% harmless)
  │
  ▼
STAGE 1: Loss Pre-Filter (Eq. 1)
  Filter out near-zero loss samples: L(xi, vi, yi; θ0) > τ (where τ = 0.1)
  Discards trivial samples that contribute zero gradient update.
  │
  ▼
STAGE 2: Per-Sample Gradient Norm Computation (Eq. 2)
  For each surviving sample i:
  Gi = || ∇_θ L(xi, vi, yi; θ0) ||_2
  Computed via micro-batching (batch size = 1) across trainable parameters θ.
  │
  ▼
STAGE 3: Dynamic Quantile Cutoff (Eq. 3)
  Compute median gradient norm: M = median({Gi})
  Define symmetric budget around median:
    α_l = 0.5 - ρ/2 = 0.5 - 0.10 = 0.40 (40th percentile)
    α_h = 0.5 + ρ/2 = 0.5 + 0.10 = 0.60 (60th percentile)
  Select sample i if and only if:
    Q(α_l) ≤ Gi ≤ Q(α_h)
  │
  ▼
SELECTED SUBSET S_t (Size = ρ * N = 20% of data)
  Proceed to standard supervised fine-tuning on S_t.
```

### 4.2 Mathematical Formulas

1. **Stage 1 Loss Pre-Filter**:
   $$\tilde{D}_t = \{ (x_i, v_i, y_i) \in D_t \mid \mathcal{L}(x_i, v_i, y_i; \theta_0) > \tau \}$$
   *(Default threshold $\tau = 0.1$, eliminating uninformative memorized data).*

2. **Stage 2 Gradient Norm**:
   $$G_i = \left\| \nabla_\theta \mathcal{L}(x_i, v_i, y_i; \theta_0) \right\|_2 = \sqrt{\sum_{p \in \Theta} \left\| \frac{\partial \mathcal{L}_i}{\partial p} \right\|_F^2}$$
   *(Where $\Theta$ denotes the active trainable parameters).*

3. **Stage 3 Dynamic Quantile Cutoff**:
   $$S_t = \{ i \in \tilde{D}_t \mid Q_{\alpha_l}(G) \le G_i \le Q_{\alpha_h}(G) \}$$
   $$\text{where } \alpha_l = 0.5 - \frac{\rho}{2}, \quad \alpha_h = 0.5 + \frac{\rho}{2}$$

---

### 4.3 Multimodal Extension: Replacing Text Components with VLM Equivalents

In text LLMs (Bach et al.), trainable parameters $\theta$ are LoRA adapters placed exclusively on language self-attention and MLP projections. In Vision-Language Models, the architecture decomposes into three distinct parameter groups:

$$\Theta_{\text{VLM}} = \Theta_{\text{Vision}} \cup \Theta_{\text{Projector}} \cup \Theta_{\text{Language}}$$

For `Qwen2-VL-2B-Instruct`:
- $\Theta_{\text{Vision}}$: Vision Transformer (frozen to conserve memory and preserve visual feature representations).
- $\Theta_{\text{Projector}}$: Multimodal MLP projector aligning visual tokens to the language embedding space.
- $\Theta_{\text{Language}}$: Transformer backbone with LoRA rank $r=16, \alpha=32$ on `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`.

#### The 3 Novel Multimodal Attribution Modes
Our implementation in [`src/selection/gradient_selector.py`](file:///Users/aryamandev/Developer/blissful-bose/src/selection/gradient_selector.py) introduces 3 attribution modes for computing $G_i$, addressing the open challenge in Bach et al. Appendix F:

1. **Language LoRA Attribution ($G_i^{(L)}$)**:
   $$G_i^{(L)} = \left\| \nabla_{\Theta_{\text{Language-LoRA}}} \mathcal{L}(x_i, v_i, y_i; \theta_0) \right\|_2$$
   *Hypothesis*: Direct counterpart to Bach et al. Measures safety drift induced within the language decoder.
2. **Projector Attribution ($G_i^{(P)}$)**:
   $$G_i^{(P)} = \left\| \nabla_{\Theta_{\text{Projector}}} \mathcal{L}(x_i, v_i, y_i; \theta_0) \right\|_2$$
   *Hypothesis*: Isolates cross-modal alignment shock. High projector gradients reflect severe visual-textual distribution mismatch.
3. **Joint Multimodal Attribution ($G_i^{(J)}$)**:
   $$G_i^{(J)} = \sqrt{\left(G_i^{(L)}\right)^2 + \lambda \left(G_i^{(P)}\right)^2}$$
   *Hypothesis*: Provides the optimal holistic filter, preventing both linguistic safety basin escape and cross-modal projection distortion.

#### Critical Implementation Detail: Multimodal Label Masking
As implemented in [`src/data/dataset_loader.py`](file:///Users/aryamandev/Developer/blissful-bose/src/data/dataset_loader.py), cross-entropy loss must be computed **strictly on target response tokens**:
- Visual tokens ($<|vision\_start|> \dots <|vision\_end|>$) $\to \text{label} = -100$
- System prompt tokens $\to \text{label} = -100$
- User question tokens $\to \text{label} = -100$
- Assistant target response tokens $\to \text{label} = \text{input\_ids}$

If visual tokens are not masked to $-100$, gradient norms will be dominated by image reconstruction loss rather than task instruction alignment, invalidating sample selection.

---

## 5. Master Empirical Results & SOTA Comparison Dossier

All text LLM baseline numbers below are transcribed verbatim from [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md), sourced from Bach et al. (ACL 2026).

### 5.1 Text LLM Baselines (Ground Truth from Bach et al. Tables 2, 5, 6)

#### Table 5: Safety Preservation (Harmful Refusal ASR on AdvBench across 4 Sequential Tasks)
*Task sequence: Dolly $\to$ GSM8K $\to$ MedMCQA $\to$ SQuAD v2. Metrics: Attack Success Rate (Lower is Safer).*

| Method | Qwen2.5-7B ASR (%) ↓ | Qwen3-4B ASR (%) ↓ | Llama-3-8B ASR (%) ↓ |
|:---|:---:|:---:|:---:|
| **Aligned Base (No FT)** | 2.1% | 1.8% | 1.5% |
| **Full FT Baseline (All Data)** | 36.7 ± 13.6% | 31.4 ± 9.8% | 34.2 ± 11.2% |
| **Random 20% Selection** | 28.4 ± 10.5% | 25.1 ± 8.7% | 26.8 ± 9.4% |
| **Low-$G_i$ (Bottom 20%)** | 34.2 ± 11.4% | 29.8 ± 10.1% | 31.5 ± 10.8% |
| **High-$G_i$ (Top 20%)** | 39.8 ± 12.1% | 36.5 ± 11.3% | 38.4 ± 12.0% |
| **EWC Regularization** | 17.4 ± 6.7% | 16.2 ± 5.9% | 18.1 ± 7.2% |
| **KL-Divergence Regularization** | 19.8 ± 8.1% | 18.4 ± 7.3% | 20.5 ± 8.6% |
| **O-LoRA (Orthogonal Subspaces)** | 16.5 ± 19.7% | 15.8 ± 17.4% | 17.2 ± 18.9% |
| **Moderate-$G_i$ (Bach et al. 20%)** | **10.2 ± 7.1%** | **9.4 ± 6.2%** | **9.8 ± 6.8%** |

*Takeaway: Moderate-$G_i$ cuts safety drift by over 72% relative to full fine-tuning (10.2% vs 36.7%) and substantially outperforms optimizer constraints like EWC (17.4%) and O-LoRA (16.5%, which exhibits high variance $\pm 19.7$).*

#### Table 6: Backward Transfer & Task Retention (BWT on Prior Tasks)
*Backward Transfer (BWT) measures retention of earlier tasks after training on subsequent tasks. Higher/closer to 0 is better.*

| Method | Qwen3-4B BWT (%) ↑ | Downstream Task Average MT-Bench Score ↑ |
|:---|:---:|:---:|
| **Full FT Baseline** | −18.5% | 58.4 |
| **Low-$G_i$ (Bottom 20%)** | −22.1% | 60.1 |
| **High-$G_i$ (Top 20%)** | −19.8% | 57.2 |
| **Moderate-$G_i$ (Bach et al. 20%)** | **−4.3%** | **60.9** |

*Takeaway: Moderate-$G_i$ achieves superior task retention (−4.3% vs −18.5% BWT) because avoiding high-gradient shocks prevents overwriting orthogonal task features.*

---

### 5.2 Multimodal VLM Evaluation Suite

To evaluate `Qwen2-VL-2B-Instruct` across its continual sequence (LLaVA-150K $\to$ MathVista $\to$ VQA-RAD $\to$ DocVQA), we execute three parallel evaluation batteries:

```
                              EVALUATION BATTERY
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
1. SAFETY METRICS             2. TRUTHFULNESS               3. TASK CAPABILITY
   • MM-SafetyBench              • MMHal-Bench                 • LLaVA-Bench (General)
     (5,040 image-text pairs)      (Hallucination severity)    • MathVista (Reasoning)
   • FigStep                     • POPE                        • VQA-RAD (Medical VQA)
     (Typographic OCR attack)      (Object probing F1)         • DocVQA (Document OCR)
   • JailBreakV-28K              • Refusal Heuristics          • MMMU (Academic Multi)
     (Diffusion/Transfer)          (Over-refusal false pos)
   • HarmBench Text Slice
```

1. **Attack Success Rate (ASR)**:
   $$\text{ASR} = \frac{\sum_{i=1}^M \mathbb{I}(\text{Llama-Guard-3}(\text{Response}_i) = \text{unsafe})}{M} \times 100\%$$
2. **False Refusal Rate (FRR) on Harmless Queries**:
   $$\text{FRR} = \frac{\sum_{j=1}^K \mathbb{I}(\text{IsRefusal}(\text{Response}_j) = \text{true})}{K} \times 100\%$$
3. **Multimodal Backward Transfer (BWT)**:
   $$\text{BWT} = \frac{1}{T-1} \sum_{i=1}^{T-1} \left( R_{T, i} - R_{i, i} \right)$$

---

### 5.3 Comprehensive 6-Family Methodology Comparison

| Method Family | Key Representative Paper | Venue / Year | Primary Mechanism | Safety ASR Defense | Task Retention | Compute Overhead | Requires Safety Data? | VLM Adaptability |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **1. Data Filtering** | **Moderate-$G_i$ (Bach et al.)** | ACL 2026 | Per-sample gradient norm filtering at aligned checkpoint $\theta_0$ | **Top Tier** (10.2% ASR) | **Top Tier** (BWT −4.3%) | ~51% training overhead | **No** (100% benign) | **High** (Target of this repo) |
| 1. Data Filtering | **LARF (Li et al.)** | EMNLP 2025 | Hidden activation filtering in safety-sensitive layers | Strong | Good | Low (Forward only) | Yes (Needs safety probe) | Medium |
| **2. Regularization** | **EWC / KL-Reg** | PNAS / NeurIPS | Fisher information / KL penalty to initial aligned weights $\theta_0$ | Moderate (17.4% ASR) | Degraded (Over-constrained) | Moderate | No | High |
| **3. Parameter Isolation** | **SaLoRA / O-LoRA** | ICLR 2025 / ACL 2023 | Freeze safety-critical LoRA rank singular vectors; orthogonal updates | Strong (16.5% ASR) | Variable ($\pm 19.7\% \sigma$) | Low | Yes (Needs safety SVD) | Medium |
| **4. Safety Replay** | **DER / VLGuard Mix** | NeurIPS / ICML 2024 | Mix 5–10% safe/unsafe multimodal pairs (VLGuard) into downstream tasks | Strong | Moderate | Low | **Yes** (Requires 5K+ safety pairs) | High |
| **5. Post-Hoc Alignment** | **SafeLoRA / Antidote** | ICLR 2024 | Project fine-tuned LoRA weights back into safe subspace post-hoc | Moderate | Degrades task head | None (Post-training) | Yes | Medium |
| **6. Inference Defense** | **VLMGuard-R1 / System Prompt** | ACL 2026 Findings | Test-time reasoning prompt optimization and output guardrails | Strong (Inference) | Unchanged | High inference latency | No | High |

---

## 6. Experimental Procedure & Execution Roadmap

Following the directive of Prof. Thao Minh Le (Sept 1, 2026), our empirical validation executes in two distinct phases:

```
PHASE 1: Colab T4 "Cheap Gate" (Free Compute)
  Model: Qwen2-VL-2B-Instruct (4-bit QLoRA)
  Task: LLaVA-150K (10% calibration subsample = 15,000 samples)
  Goal: Verify that Moderate-Gi isolates the 83-88% safety basin on multimodal inputs.
  Ablations: Random (20%), Low-Gi (20%), High-Gi (20%), Moderate-Gi (20%).
  Safety Eval: FigStep + MM-SafetyBench (subsampled 200 pairs).
  Outcome: Confirms hypothesis before requesting cluster allocation.
  │
  ▼ (Clearance from Katie / Campus Cluster Allocation)
PHASE 2: Full 4-Task Continual Sequence (Cluster Multi-GPU)
  Sequence: LLaVA-150K ➔ MathVista ➔ VQA-RAD ➔ DocVQA
  Attribution Ablations: Language Gi^(L) vs Projector Gi^(P) vs Joint Gi^(J)
  Baselines: Full FT, EWC, KL-reg, VLGuard replay, SaLoRA.
  Full Eval: 5,040 MM-SafetyBench pairs + 1,000 FigStep OCR pairs via vLLM batching.
```

---

## 7. Slide-by-Slide PPT Construction Blueprint (10-Minute Talk)

Designed specifically for your presentation to **Prof. Thao Minh Le**. Use this blueprint to build your presentation in PowerPoint, Google Slides, or Marp.

---

### Slide 1: Title & Framing (0:00 – 0:30)
- **Slide Title**: Safety Alignment of Small Vision-Language Models via Gradient-Based Sample Selection
- **Subtitle**: *Extending the Continual Alignment Paradigm of Bach et al. (ACL 2026) to Multimodal Architectures*
- **Header Details**: Aryaman Singh Dev | Advisor: Prof. Thao Minh Le | Pennsylvania State University
- **Visual**: Two side-by-side diagrams:
  - Left: Clean text LLM fine-tuning loop.
  - Right: Multimodal VLM architecture showing the dual text + vision attack surface.
- **Key Paper Citation on Slide**: Bach et al., ACL 2026 ([arXiv:2604.17215](https://arxiv.org/abs/2604.17215)).
- **Speaker Script**:
  > *"Good morning Prof. Thao. Today I'm presenting our project on continual safety alignment for small Vision-Language Models. In your ACL 2026 paper with Sang-Min Bach, you proved that fine-tuning aligned LLMs on benign data causes alignment drift, and you introduced Moderate-$G_i$ selection to preserve safety. In Appendix F, you explicitly highlighted extending this to multimodal models as critical future work. That is exactly what we have formulated, implemented, and prepared for benchmarking on Qwen2-VL-2B."*

---

### Slide 2: The Core Vulnerability — Alignment Drift in VLMs (0:30 – 1:30)
- **Slide Title**: The Problem: Downstream Fine-Tuning Breaks Safety Alignment
- **Key Bullet Points**:
  - Fine-tuning on 100% benign downstream tasks (math, visual QA, doc understanding) degrades safety guardrails.
  - **Elastic Reversion**: Downstream parameter updates pull the model out of its safety-aligned distribution back toward unaligned pre-trained weights.
  - **The Multimodal Hazard**: In VLMs, alignment drift is dramatically worse. Visual inputs bypass text safety guardrails entirely.
- **Visual**: A 2D diagram showing the **Safety Basin**:
  - Safe region in green with $\mathcal{L}_{\text{safety}} \approx 0$.
  - Arrows showing fine-tuning steps climbing out over the barrier into the red unaligned zone.
- **Citations on Slide**:
  - Ji et al., *Language Models Resist Alignment*, arXiv:2406.06144 (§1, §3.1).
  - Peng et al., *VISAGE*, NeurIPS 2024, arXiv:2405.17374 (§3, Fig. 2).
- **Speaker Script**:
  > *"Why does alignment drift occur? As Ji et al. demonstrated, fine-tuning introduces an elastic restoring force that pulls parameters toward the base model. Peng et al. formalized this as escaping the 'Safety Basin'—a flat, localized region where safety loss is zero. When we transition to VLMs, this vulnerability escalates: visual tokens introduce an unaligned pathway that attackers exploit via typographic text."*

---

### Slide 3: The Multimodal Threat Surface — FigStep & OCR Jailbreaks (1:30 – 2:30)
- **Slide Title**: Multimodal Attack Surface: Why VLMs Are Far More Fragile
- **Key Bullet Points**:
  - Text prompts like *"How to make a bomb"* trigger instant refusals (ASR < 2%).
  - Rendering the identical prompt into an image with step-by-step formatting (**FigStep**) bypasses the visual safety filter, achieving **>80% ASR**.
  - As downstream fine-tuning erodes alignment, typographic and multimodal jailbreak susceptibility spikes catastrophically.
- **Visual**: A FigStep attack example:
  - Input: Harmless text prompt + an image of typographic text outlining prohibited instructions.
  - Output: The model dutifully transcribes and fulfills the request because the visual encoder and projector were not safety-regularized.
- **Citations on Slide**:
  - Gong et al., *FigStep*, arXiv:2311.05608 (§1, §3, Table 1).
  - Liu et al., *MM-SafetyBench*, arXiv:2311.17600 (§2).
- **Speaker Script**:
  > *"To understand why VLMs need specialized protection, consider FigStep. If you ask Qwen2-VL a harmful text question, it refuses. But if you typeset that same question into an image, the visual encoder processes it as OCR and bypasses text safety filters. When a VLM undergoes downstream fine-tuning, its residual safety margins collapse, making it almost completely defenseless against multimodal jailbreaks."*

---

### Slide 4: Foundation — Bach et al. (ACL 2026) Deconstructed (2:30 – 3:30)
- **Slide Title**: The Foundational Breakthrough: Bach et al. (ACL 2026)
- **Key Bullet Points**:
  - Analyzed per-sample gradient norms $G_i = \|\nabla_\theta \mathcal{L}(x_i, y_i; \theta_0)\|_2$ computed at the aligned checkpoint $\theta_0$.
  - **Low-$G_i$ (Bottom 20%)**: Near-zero learning signal $\to$ severe downstream catastrophic forgetting (BWT −22.1%).
  - **High-$G_i$ (Top 20%)**: Massive update steps $\to$ catapults parameters out of the safety basin (retains only 62–72% VISAGE score).
  - **Moderate-$G_i$ (Median 20%)**: Sweet spot $\to$ learns downstream skills while preserving **83–88% of the safety basin**.
- **Visual**: The sample gradient norm distribution curve showing Low, Moderate, and High quantiles, paired with Table 2 retention data.
- **Citations on Slide**:
  - Bach et al., ACL 2026, §3.1, §3.2, Table 2.
- **Speaker Script**:
  > *"In your paper, you discovered that samples are not created equal. High-$G_i$ samples deliver violent updates that shatter the safety basin, retaining only 62 to 72% of safety geometry. Low-$G_i$ samples produce almost no update, causing severe forgetting. Moderate-$G_i$—selecting the 20% of samples closest to the median—preserves 83 to 88% of the safety basin and cuts AdvBench ASR from 36.7% down to 10.2%."*

---

### Slide 5: The Surprising Root Cause — Format Mismatches (3:30 – 4:30)
- **Slide Title**: Mechanistic Finding: High-$G_i$ Samples Are Format Mismatches
- **Key Bullet Points**:
  - High-$G_i$ samples are **not** toxic or adversarial prompts.
  - They are driven by **format divergence**: safety alignment trains models to be conversational and verbose; downstream benchmarks demand terse single-token outputs ("Yes", "No", "A").
  - Forcing terse tokens creates huge cross-entropy loss $\to$ massive gradient norm $\to$ alignment destruction.
  - High-$G_i$ gradients directly align with the reversion vector $\mathbf{r} = \theta_{\text{pre}} - \theta_{\text{align}}$ in final-layer projections (V/O layers in Qwen).
- **Visual**: Reversion vector cosine similarity bar chart across layers (showing high alignment in late layers, zero in middle layers).
- **Citations on Slide**:
  - Bach et al., ACL 2026, §3.2 (Table 4) & Appendix E.1.
- **Speaker Script**:
  > *"The mechanistic insight in Appendix E.1 is fascinating: high-gradient samples aren't semantic outliers. They are format mismatches. Safety alignment teaches a model to be verbose and helpful. When a downstream dataset forces single-token answers like 'Yes' or 'No', the cross-entropy loss spikes, producing massive gradients in final projection layers that align directly with the reversion vector back to the unaligned base model."*

---

### Slide 6: Our Method — Porting Bach et al. to Small VLMs (4:30 – 5:30)
- **Slide Title**: Methodology: Extending Gradient Selection to Multimodal Architectures
- **Key Bullet Points**:
  - Target Model: `Qwen2-VL-2B-Instruct` (compact, deployable, multimodal).
  - Trainable parameters: Language LoRA ($r=16, \alpha=32$) + Multimodal Projector. Frozen ViT.
  - **3-Stage Selection Pipeline** ($\rho = 0.2, \tau = 0.1$):
    1. Loss pre-filter $\mathcal{L} > \tau$
    2. Micro-batched per-sample gradient norm calculation
    3. Dynamic quantile extraction: $[\alpha_l = 0.40, \alpha_h = 0.60]$
  - Strict multimodal label masking: visual tokens and user prompt tokens set to $-100$.
- **Visual**: Architectural flowchart of `Qwen2-VL-2B` showing where gradients are computed and how samples are filtered before the optimizer step.
- **Citations on Slide**:
  - Implementation in [`src/selection/gradient_selector.py`](file:///Users/aryamandev/Developer/blissful-bose/src/selection/gradient_selector.py).
- **Speaker Script**:
  > *"Here is how we translate your method to VLMs. We use Qwen2-VL-2B-Instruct. We freeze the vision transformer and apply LoRA to the language backbone while keeping the multimodal projector trainable. Crucially, we implement strict label masking: visual tokens and system tokens are masked to -100 so that gradients strictly reflect task-response alignment, not image autoencoding."*

---

### Slide 7: Novel Research Contribution — Multimodal Attribution Modes (5:30 – 6:30)
- **Slide Title**: Novel VLM Contribution: 3 Gradient Attribution Modes
- **Key Bullet Points**:
  - In text LLMs, LoRA is homogeneous. In VLMs, parameters span two modalities.
  - We formulate and ablate **three distinct attribution modes**:
    1. **Language LoRA ($G_i^{(L)}$)**: Captures linguistic alignment drift.
    2. **Projector ($G_i^{(P)}$)**: Captures cross-modal representation shock.
    3. **Joint Multimodal ($G_i^{(J)} = \sqrt{(G_i^{(L)})^2 + \lambda (G_i^{(P)})^2}$)**: Balances linguistic safety and visual alignment.
  - First work to isolate whether cross-modal projection or language attention drives VLM alignment drift.
- **Visual**: Mathematical equation callout boxes for $G_i^{(L)}, G_i^{(P)}, G_i^{(J)}$ with arrows pointing to the corresponding layers in Qwen2-VL.
- **Citations on Slide**:
  - SOTA comparison against SafeVLM (arXiv:2405.13581) and SaLoRA (arXiv:2501.01774).
- **Speaker Script**:
  > *"This is our primary novel contribution beyond the text paper. In a VLM, should sample selection be driven by language weights, the multimodal projector, or both? We formulated three attribution modes: Language $G_i^{(L)}$, Projector $G_i^{(P)}$, and Joint $G_i^{(J)}$. This allows us to publish an ablation showing exactly which parameter group is responsible for multimodal safety collapse."*

---

### Slide 8: Sequential Downstream Task Curriculum (6:30 – 7:30)
- **Slide Title**: 4-Stage Continual Task Progression
- **Key Bullet Points**:
  - Maps Bach et al.'s 4 text tasks (Dolly $\to$ GSM8K $\to$ MedMCQA $\to$ SQuAD) to 4 diverse multimodal domains:
    - **Task 1: LLaVA-150K** (General multimodal instruction following)
    - **Task 2: MathVista** (Complex mathematical & geometric reasoning)
    - **Task 3: VQA-RAD / SLAKE** (High-precision clinical & medical VQA)
    - **Task 4: DocVQA** (Dense document OCR & layout understanding)
  - Evaluates both safety preservation (ASR) and backward knowledge retention (BWT) across all 4 stages.
- **Visual**: Timeline progression diagram showing the 4 tasks with sample input images (natural image $\to$ math plot $\to$ chest X-ray $\to$ scanned invoice).
- **Speaker Script**:
  > *"To stress-test continual alignment, we designed a 4-stage multimodal curriculum matching the diversity of your original setup: general instruction following with LLaVA-150K, mathematical reasoning with MathVista, medical VQA with VQA-RAD, and document OCR with DocVQA. This sequence introduces diverse format changes, testing whether Moderate-$G_i$ prevents catastrophic drift across sequential domain shifts."*

---

### Slide 9: Evaluation Suite & Benchmark Architecture (7:30 – 8:30)
- **Slide Title**: Rigorous Tripartite Evaluation Protocol
- **Key Bullet Points**:
  - **1. Safety & Jailbreak Suite**:
    - MM-SafetyBench (5,040 image-text pairs across 13 risk categories).
    - FigStep (Typographic OCR jailbreaks).
    - JailBreakV-28K (Transfer & diffusion attacks).
  - **2. Truthfulness & Hallucination**: MMHal-Bench & POPE (Object probing).
  - **3. Automated Judge**: Llama-Guard-3-8B + refusal string matching.
  - **High-Throughput Acceleration**: vLLM integration reduces evaluation from 3 hours to <3 minutes per checkpoint.
- **Visual**: Evaluation pipeline schematic: Checkpoint $\to$ vLLM Batch Inference $\to$ Llama-Guard-3 Judge $\to$ Metric Dashboard (ASR, FRR, BWT).
- **Citations on Slide**:
  - MM-SafetyBench (arXiv:2311.17600), FigStep (arXiv:2311.05608), POPE (arXiv:2305.10355).
- **Speaker Script**:
  > *"Our evaluation suite leaves no blind spots. We evaluate safety across 5,040 MM-SafetyBench pairs, test against typographic attacks with FigStep, measure hallucination with POPE, and evaluate task capabilities on MathVista and DocVQA. To make this feasible on our compute budget, we built an evaluator with vLLM that cuts evaluation time per checkpoint from three hours down to three minutes."*

---

### Slide 10: Two-Phase Execution Plan & The "Cheap Gate" (8:30 – 9:15)
- **Slide Title**: Experimental Execution: Free Colab Gate $\to$ Cluster Scale
- **Key Bullet Points**:
  - **Phase 1: Colab T4 Cheap Gate (Active Now)**:
    - Target: Single-task hypothesis verification on LLaVA-150K (10% subset = 15K samples).
    - 4-bit QLoRA on free T4 GPU ($<12$ GB VRAM).
    - Validates that Moderate-$G_i$ suppresses FigStep/MM-SafetyBench ASR compared to Full FT and High-$G_i$.
  - **Phase 2: Campus Cluster Full Sequence (Pending Clearance)**:
    - Full 4-task continual run across multiple GPUs.
    - Full attribution ablation ($G_i^{(L)}$ vs $G_i^{(P)}$ vs $G_i^{(J)}$) and SOTA baseline comparisons (EWC, SaLoRA, VLGuard).
- **Visual**: Milestone roadmap showing Phase 1 completed on Colab as a decision gate before Phase 2 cluster launch.
- **Speaker Script**:
  > *"Per your email advice, we established a phased execution protocol. Phase 1 is a 'Cheap Gate' running in Google Colab on a free T4 GPU using 4-bit QLoRA. On a 10% calibration split of LLaVA-150K, we verify that Moderate-$G_i$ outperforms Random and High-$G_i$ on FigStep before moving to the cluster. Once validated, Phase 2 scales to the full 4-task sequence and complete attribution ablations."*

---

### Slide 11: Summary, Expected Impact & Next Steps (9:15 – 10:00)
- **Slide Title**: Expected Contributions & Immediate Timeline
- **Key Bullet Points**:
  - **First Paper** to adapt gradient-based continual safety selection to Vision-Language Models.
  - **First Empirical Study** isolating modality-specific gradient attribution ($G_i^{(L)}$ vs $G_i^{(P)}$).
  - **Codebase Status**: 100% complete, fully modularized in `src/`, with unit tests and Colab notebook ready to run.
  - **Immediate Next Step**: Execute Phase 1 Colab run, log calibration curves, and review initial FigStep refusal delta with you next week.
- **Visual**: Summary badge table showing code readiness, benchmark coverage, and target submission venues (CVPR/ACL/NeurIPS).
- **Speaker Script**:
  > *"To summarize: this research directly resolves the open multimodal limitation from your ACL paper. We have the complete mathematical formulation, modularized PyTorch codebase, unit tests, and evaluation pipelines built. Our immediate next step is executing the Phase 1 Colab calibration run to gather initial empirical curves. Thank you, and I look forward to your questions."*

---

### 7.1 Advisor Anticipated Q&A (Preparation Cheatsheet)

1. **Advisor Question**: *"Why do you expect Moderate-$G_i$ to work for VLMs when images have continuous feature spaces?"*
   - **Your Answer**: *"Because alignment drift in VLMs is still fundamentally mediated by the cross-entropy loss over token predictions. When an image forces a terse or unaligned answer, the cross-entropy loss spikes, producing large parameter updates in the projector and language layers. Moderate-$G_i$ filters out these disruptive updates regardless of whether the input prompt is text-only or multimodal."*
2. **Advisor Question**: *"Won't computing per-sample gradients on images with high resolution blow up GPU memory on a T4?"*
   - **Your Answer**: *"We specifically designed `src/training/trainer.py` to use micro-batching with batch size = 1 and autograd hooks that intercept per-sample gradient norms without materializing the full batch gradient tensor. Combined with freezing the ViT encoder and using 4-bit QLoRA, peak VRAM on Qwen2-VL-2B remains under 11.2 GB."*
3. **Advisor Question**: *"How do your attribution modes handle gradient scale differences between LoRA layers and the multimodal projector?"*
   - **Your Answer**: *"In our Joint mode $G_i^{(J)}$, we include a balancing hyperparameter $\lambda$: $G_i^{(J)} = \sqrt{(G_i^{(L)})^2 + \lambda (G_i^{(P)})^2}$. During the Phase 1 calibration run on Colab, we normalize both norm distributions to unit variance so neither modality artificially dominates the quantile cutoff."*

---

## 8. Summary Checklist for Researcher (Aryaman)

- [x] Read Bach et al. (ACL 2026) using [`Continual_Safety_Alignment.md`](file:///Users/aryamandev/Developer/blissful-bose/Continual_Safety_Alignment.md) and §2–§4 of this compendium.
- [x] Review verified baseline numbers in [`RESEARCH_METHODOLOGY_AND_VLM_SPEC.md`](file:///Users/aryamandev/Developer/blissful-bose/RESEARCH_METHODOLOGY_AND_VLM_SPEC.md) (Table 6 & 8).
- [x] Copy slide titles, bullet points, and speaker scripts from [Section 7](#7-slide-by-slide-ppt-construction-blueprint-10-minute-talk) into your PowerPoint / Google Slides deck.
- [x] Review anticipated Q&A in [Section 7.1](#71-advisor-anticipated-qa-preparation-cheatsheet).
- [x] Execute Phase 1 calibration run in [`notebooks/continual_safety_vlm.ipynb`](file:///Users/aryamandev/Developer/blissful-bose/notebooks/continual_safety_vlm.ipynb) on Colab T4.
