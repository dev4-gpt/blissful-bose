# Gradient Strategy Dossier
## Continual Safety Alignment in Small Vision-Language Models via Gradient-Based Sample Selection

**Lead Researcher**: Aryaman Singh Dev (`asd5520@psu.edu`)  
**Advisor**: Prof. Thao Minh Le (`mxl6224@psu.edu`) — Co-author of Bach et al. (ACL 2026)  
**Repository**: `dev4-gpt/blissful-bose`  
**Document Policy**: Every number in this document has an inline source. Any claim without a source is explicitly marked `[Source not verified — do not cite]`.

---

## Section 1: Theoretical Foundations — The Mathematical Paradigm

### 1.1 Elastic Reversion Force
**Source**: Ji et al., *Language Models Resist Alignment: Evidence From Data Compression*, arXiv:2406.06144

Fine-tuning a previously aligned model triggers an **elastic reversion force** proportional to the size of the pretraining corpus and the distributional distance between the current model and the pretrained distribution:

$$F_{\text{elastic}} \propto |\mathcal{D}_{\text{pretrain}}| \cdot \Delta D_{\text{KL}}\left(p_\theta \;\|\; p_{\mathcal{D}_{\text{pretrain}}}\right)$$

**Implication** [Source: Ji et al., abstract + Sec. 2]: Pretraining corpora dwarf safety alignment datasets by orders of magnitude. The pretrained distribution exerts a constant "pull" on aligned parameters. Fine-tuning on downstream data can release this tension, causing aligned models to rebound toward their unaligned pretrained behavior. The paper formally proves via compression theory that "fine-tuning disproportionately undermines alignment relative to pre-training, potentially by orders of magnitude."

---

### 1.2 Safety Basin Geometry & the VISAGE Score
**Source**: Peng et al., *Navigating the Safety Landscape: Measuring Risks in Finetuning Large Language Models*, NeurIPS 2024, arXiv:2405.17374

The **safety basin** is the local neighborhood around the aligned model's parameters $\theta_0$ where random perturbations do not significantly degrade safety:

$$\mathcal{B}(\theta_0) = \{\theta : \theta = \theta_0 + \epsilon \cdot \hat{d}, \;\|\hat{d}\|_2 = 1,\; \epsilon \leq \epsilon_{\max}\}$$

**Critical empirical finding** [Source: Peng et al., abstract]: Safety exhibits a **sharp, step-function collapse** at the basin boundary. This contrasts sharply with capability, which degrades gradually. A single large update can push a model from safe to unsafe, while many small updates may remain within the basin.

**VISAGE Score** [Source: Peng et al., abstract]: Stands for *Volumetric Index for Safety Alignment Guided by Explanation*. It quantifies basin robustness by averaging safety margins across $N$ random unit-vector perturbation directions. Higher VISAGE = larger, more robust safety basin.

$$\text{VISAGE}(\theta_0) = \frac{1}{N} \sum_{i=1}^{N} \text{SafetyMargin}(\theta_0 + \epsilon_i \cdot \hat{d}_i)$$

> ⚠️ **WRONG ID note**: arXiv:2406.14856 is a Parkinson's disease detection paper. The correct Safety Basin paper is **arXiv:2405.17374**.

---

### 1.3 The Continual Safety Alignment Problem
**Source**: Bach et al., *Continual Safety Alignment via Gradient-Based Sample Selection*, ACL 2026, arXiv:2604.17215, Section 2.3

Formally: given an aligned model that must sequentially learn $T$ tasks from datasets $\{D_1, \ldots, D_T\}$:

$$\theta_t = \arg\min_\theta \;\mathcal{L}_t(\theta; D_t) \quad \text{subject to} \quad \theta_t \in \mathcal{B}$$

where $\mathcal{B}$ is the safety basin. Standard continual learning ignores the $\theta \in \mathcal{B}$ constraint entirely — it protects task knowledge but not safety behavior. [Source: Bach et al., Sec. 2.3]

**Alignment drift metric** [Source: Bach et al., Sec. 2.1, using Peng et al. VISAGE]:

$$\Delta_{\text{align}}(t) = \text{VISAGE}(\theta_0) - \text{VISAGE}(\theta_t)$$

---

### 1.4 The Per-Sample Gradient Score
**Source**: Bach et al., arXiv:2604.17215, Section 3

For a training example $(x_i, y_i)$ evaluated at the aligned model parameters $\theta_0$:

$$G_i = \left\|\nabla_\theta \mathcal{L}(x_i, y_i;\; \theta_0)\right\|_2$$

**Hypothesis** [Source: Bach et al., Sec. 3, abstract]: High-$G_i$ samples occur where the aligned model's predictions diverge substantially from task targets — precisely where alignment training modified behavior away from pretrained tendencies. Training on these samples may reverse those alignment modifications, activating elastic reversion.

---

## Section 2: The Three-Stage Moderate-$G_i$ Algorithm
**Source**: Bach et al., arXiv:2604.17215, Section 4.1

The algorithm operates in three sequential stages given a training batch of $N$ candidates and target selection ratio $\rho \in [0.1, 0.4]$ (recommended default $\rho = 0.2$):

```
ALGORITHM: Moderate-Gi Sample Selection
========================================
INPUT:  Candidate set D_cand (N samples), aligned model theta_0, ratio rho
OUTPUT: Selected subset D_select of size floor(rho * N)

STAGE 1 — Loss-Based Pre-Filtering:
  1. Compute scalar loss L_i = L(x_i, y_i; theta_0) for each sample i
  2. Compute loss percentile bounds: [q_low, q_high] (paper uses outer 16% each side)
  3. Retain D_filtered = {i : q_low <= L_i <= q_high}
  Rationale: removes memorized samples (very low loss, near-zero gradient signal)
             and noise/outlier samples (very high loss, unstable gradients)
  Compute savings: ~32% of backward passes eliminated before gradient computation

STAGE 2 — Per-Sample Gradient Norm Extraction:
  1. For each sample i in D_filtered:
     a. Forward pass: compute L_i
     b. Backward pass (B=1, retain_graph=False): compute nabla_theta L_i
     c. G_i = ||nabla_theta L_i||_2   (L2 norm over target parameter subset)
     d. model.zero_grad(set_to_none=True)   # critical: prevent graph accumulation
  Note: gradient computed at theta_0, not updated parameters

STAGE 3 — Median-Distance Selection:
  1. mu_G = median({G_i : i in D_filtered})
  2. Sort D_filtered by |G_i - mu_G| ascending
  3. D_select = top floor(rho * |D_filtered|) samples by proximity to mu_G
  Rationale: avoids high-Gi (alignment-reversing) AND low-Gi (no task learning signal)

NOTE: The paper uses MEDIAN not MEAN for robustness against heavy-tailed gradient distributions.
      [Source: Bach et al., Sec. 4.1]
```

**Sensitivity to $\rho$** [Source: Bach et al., Sec. 4.2]: Method is robust across $\rho \in [0.1, 0.4]$. Smaller $\rho$ (stricter filtering) gives slightly better safety at marginal task cost. Recommended default: $\rho = 0.2$.

---

## Section 3: Verified Empirical Results
**Source**: Bach et al., ACL 2026, arXiv:2604.17215. All numbers from `Continual_Safety_Alignment.md` (in-repo verified summary) and the arXiv paper.

### 3.1 Main Safety Comparison (AdvBench ASR)

| Model | Strategy | AdvBench ASR ↓ | TruthfulQA ↑ | Downstream Avg ↑ | Source |
|:---|:---|:---:|:---:|:---:|:---|
| Qwen2.5-7B | Baseline (full FT) | 36.7% | — | — | Bach et al. Sec. 5.2 |
| Qwen2.5-7B | Random (20%) | 31.1% | — | — | Bach et al. Sec. 5.2 |
| Qwen2.5-7B | Low-$G_i$ (20%) | 8.4% | **50.2** | 60.1 | Bach et al. Sec. 3, Table 1 |
| Qwen2.5-7B | **Moderate-$G_i$ (20%)** | **10.2%** | 42.5 | **60.9** | Bach et al. Sec. 3, Table 1 |
| Qwen2.5-7B | High-$G_i$ (20%) | >36.7% | — | — | Bach et al. Sec. 3 (worst) |
| LLaMA-3.1-8B | Baseline (full FT) | 44.2% | — | — | Bach et al. Sec. 5.2 |
| LLaMA-3.1-8B | **Moderate-$G_i$ (20%)** | **18.3%** | 41.5 | **46.4** | Bach et al. Sec. 3, Table 1 |
| Qwen3-4B | Low-$G_i$ (20%) | 3.0% | **48.6** | 56.3 | Bach et al. Sec. 3, Table 1 |
| Qwen3-4B | **Moderate-$G_i$ (20%)** | **6.0%** | 42.8 | **58.1** | Bach et al. Sec. 3, Table 1 |

**Takeaway** [Source: Bach et al., Sec. 3]: Low-$G_i$ provides the strictest safety preservation but sacrifices 0.8–1.9 points of task performance. Moderate-$G_i$ is the Pareto-optimal trade-off. High-$G_i$ is worst on both axes.

### 3.2 Safety Basin Retention (VISAGE Score)
**Source**: Bach et al., Table 2

| Model | Condition | VISAGE Score | Retention | AdvBench ASR ↓ |
|:---|:---|:---:|:---:|:---:|
| Qwen2.5-7B | Base Aligned ($\theta_0$) | 78.5 | 100.0% | 2.1% |
| Qwen2.5-7B | High-$G_i$ (Top 20%) | 48.8 | 62.2% | 18.4% |
| Qwen2.5-7B | Random (20%) | 57.0 | 72.6% | 12.7% |
| Qwen2.5-7B | **Moderate-$G_i$** | **65.5** | **83.4%** | **5.8%** |
| LLaMA-3.1-8B | Base Aligned ($\theta_0$) | 67.7 | 100.0% | 3.2% |
| LLaMA-3.1-8B | High-$G_i$ (Top 20%) | 48.9 | 72.2% | 15.1% |
| LLaMA-3.1-8B | **Moderate-$G_i$** | **59.3** | **87.6%** | **4.9%** |

### 3.3 HarmBench ASR Comparison
**Source**: Bach et al., Sec. 5.2 (model family not individually specified in available summary)

| Strategy | HarmBench ASR ↓ |
|:---|:---:|
| Baseline (full FT) | 27.8% |
| Random selection | 17.2% |
| KL regularization | 27.7% |
| EWC | 31.0% |
| LoRA-based method | 10.0% |
| **Moderate-$G_i$** | **5.0%** |

**Key observation** [Source: Bach et al., Sec. 5.2]: EWC (31.0%) *worsens* safety relative to baseline (27.8%). Parameter regularization protecting task-important weights does not overlap with safety-critical refusal parameters.

### 3.4 Catastrophic Forgetting Analysis
**Source**: Bach et al., Sec. 5.4

| Model | Strategy | BWT ↑ (less negative = better) | FM ↓ |
|:---|:---|:---:|:---:|
| Qwen3-4B | Baseline | −18.5% | 18.5% |
| Qwen3-4B | **Moderate-$G_i$** | **−4.3%** | **4.3%** |

**Computational overhead** [Source: Bach et al., Appendix]: Moderate-$G_i$ selection incurs approximately **51% training overhead** relative to standard fine-tuning. Inference latency is **unchanged**.

### 3.5 Gradient Direction Analysis (Mechanistic Evidence)
**Source**: Bach et al., Sec. 3.2 — TopK-Cosine similarity between sample gradients and reversion vector $\mathbf{r} = \theta_{\text{pretrain}} - \theta_{\text{aligned}}$, $k=1000$

| Model | Parameter Subset | High-$G_i$ TopK-Cos | Moderate-$G_i$ TopK-Cos | Pearson $r$ | $p$-value |
|:---|:---|:---:|:---:|:---:|:---:|
| Qwen2.5-7B | Last Layer $V$ Projection | 0.119 | 0.104 | 0.41 | $< 10^{-3}$ |
| Qwen2.5-7B | Last Layer $O$ Projection | 0.276 | 0.244 | 0.39 | $< 10^{-3}$ |
| Qwen2.5-7B | Middle Layer | −0.004 | −0.004 | 0.06 | 0.38 (NS) |
| LLaMA-3.1-8B | Last Layer MLP | 0.104 | 0.102 | 0.18 | $< 0.01$ |
| LLaMA-3.1-8B | Last Layer $V$ Projection | −0.029 | −0.033 | 0.33 | $< 10^{-3}$ |

**Takeaway** [Source: Bach et al., Sec. 3.2]: Directional reversion signal localizes to **final-layer alignment-critical parameters** (V/O projections in Qwen, MLP in LLaMA). Middle transformer layers show no statistically significant signal.

### 3.6 What High-Gradient Samples Actually Are
**Source**: Bach et al., Appendix E.1 (Sample Audit — 10,000 samples inspected)

High-gradient samples are predominantly **format mismatches**: short-answer tasks (e.g., "Yes", "No", single-token replies) where the safety-aligned model's verbose output distribution diverges from the terse task target. They are **NOT** content-based outliers and **NOT** adversarial examples in the traditional sense. The paper audited 10,000 samples and found this pattern holds consistently.

> **Do NOT describe high-gradient samples as "adversarial."** This is a common mischaracterization. The gradient magnitude reflects format divergence, not semantic hostility. [Source: Bach et al., App. E.1]

---

## Section 4: VLM Pipeline Adaptation (Our Novel Extension)

**Status of text below**: The text in Section 4 describes the *novel research hypotheses* for extending Bach et al. to VLMs. These are **not yet empirically validated**. Every claim here is labeled with its epistemic status.

### 4.1 The Research Gap
[Source: Bach et al., Appendix F (Limitations), verbatim]:
> *"Multi-Modal Models: Our experiments focus on text-only models. Extending gradient-based selection to vision-language models or other modalities requires further investigation."*

This is the explicit open problem that this project addresses.

### 4.2 VLM Parameter Decomposition
[Hypothesis — not yet validated empirically]

In a Qwen2-VL-2B-Instruct model, trainable parameters split into:

$$\theta = \underbrace{\theta_{\text{vision}}}_{\text{Frozen ViT}} \;\cup\; \underbrace{\theta_{\text{projector}}}_{\text{Spatial Merger (trainable)}} \;\cup\; \underbrace{\theta_{\text{language}}}_{\text{LLM Backbone + LoRA (trainable)}}$$

Three gradient attribution hypotheses:

| Mode | Formula | Parameter Scope | Research Question |
|:---|:---|:---|:---|
| Language-only ($G_i^{(L)}$) | $\|\nabla_{\theta_L} \mathcal{L}_i\|_2$ | LoRA adapters on LLM only | Does language decoder drift alone predict safety erosion? |
| Projector-only ($G_i^{(P)}$) | $\|\nabla_{\theta_P} \mathcal{L}_i\|_2$ | Spatial merger projector | Does cross-modal representation drift predict safety erosion? |
| Joint ($G_i^{(J)}$) | $\sqrt{\|G_i^{(L)}\|^2 + \|G_i^{(P)}\|^2}$ | Language + Projector | Does the joint norm provide better safety prediction? |

[This three-way ablation is the **primary novel contribution** of this project vs. Bach et al.]

### 4.3 Label Masking Requirement
[Engineering constraint — derived from Qwen2-VL tokenization, not empirically tested for safety impact]

Visual tokens (`<|vision_start|>...<|vision_end|>`) and input prompt tokens must have `labels = -100`. The loss $\mathcal{L}_i$ and gradient $G_i$ must compute **only over generated response tokens**. This ensures:
1. The gradient score reflects the model's uncertainty about the *answer*, not the *image description*.
2. Image resolution changes do not inflate gradient norms artificially.

Implementation in: [`src/selection/gradient_selector.py`](../src/selection/gradient_selector.py)

### 4.4 VRAM Constraint: Micro-Batched Backward Pass
[Engineering requirement — derived from Qwen2-VL-2B VRAM profiling, not a research result]

Computing per-sample gradients on high-resolution visual inputs (e.g., 448×448 → 1,024 image tokens) retains large computation graphs in VRAM. Standard batched backward passes cause OOM on a 16GB T4 GPU.

Solution: three-pass micro-batching:
1. `torch.no_grad()` forward pass to extract all candidate losses (Stage 1 pre-filtering)
2. Single-sample ($B=1$) backward passes with `retain_graph=False` and `zero_grad(set_to_none=True)` after each
3. Parameter update on selected samples only

Peak VRAM remains bounded by a single image's computation graph.

Implementation in: [`src/training/trainer.py`](../src/training/trainer.py)

---

## Section 5: SOTA Landscape Map

| Method | Modality | Primary Gap Addressed | Key Result (Verified) | Source |
|:---|:---|:---|:---|:---|
| **Moderate-$G_i$ (Bach et al.)** | Text only | Continual alignment drift via benign fine-tuning | AdvBench ASR: 10.2% vs 36.7% baseline (Qwen2.5-7B) | arXiv:2604.17215, Sec. 5.2 |
| **SafeVLM (Liu et al.)** | Vision-Language | Visual inputs bypass text safety alignment | RTVLM score: 8.26 vs 6.39 baseline, vs 7.92 GPT-4V | arXiv:2405.13581 |
| **VLMGuard-R1** | Vision-Language | Subtle multimodal threat patterns missed by text guardrails | +43.59% safety on SIUO benchmark vs baselines | arXiv:2504.12661 |
| **FigStep** (attack, not defense) | Vision-Language | Typographic jailbreak via visual modality | 82.50% avg ASR on 6 open-source LVLMs | arXiv:2311.05608 |
| **EWC** | Text | Catastrophic forgetting (parameter regularization) | HarmBench ASR: 31.0% (WORSE than 27.8% baseline) | Bach et al. Sec. 5.2 |
| **KL Regularization** | Text | Distributional drift | HarmBench ASR: 27.7% (no improvement vs baseline) | Bach et al. Sec. 5.2 |
| **This Project (Hypothesis)** | Vision-Language | Continual alignment drift in Small VLMs via multimodal gradient selection | [Not yet measured — open research question] | — |

**The clear gap**: No prior work combines gradient-based continual alignment preservation with Small VLMs and multimodal safety evaluation. SafeVLM addresses initial alignment but not continual fine-tuning drift. Bach et al. address continual drift but only in text-only models. Our project sits at their intersection.

---

## Section 6: Adversarial Attack Suite

### 6.1 Attacks to Include — Verified from Literature

| Attack Type | Source | Why It Matters for VLMs | Example Vector |
|:---|:---|:---|:---|
| **Typographic Jailbreak (FigStep)** | arXiv:2311.05608 | Harmful text in images bypasses language guardrails | "What steps should I follow?" + image containing harmful instructions |
| **MM-SafetyBench probes** | arXiv:2311.17600 | 13 standardized risk categories; 5,040 pairs | SD-generated images paired with text across 13 risk scenarios |
| **AdvBench text (direct)** | Zou et al. 2023 | Baseline text jailbreak compatibility check | Direct harmful instruction prompts |
| **HarmBench subset** | arXiv:2402.04249 | Standardized; Bach et al. uses it → enables comparison | 18 attack methods across 33 models |
| **POPE (hallucination)** | arXiv:2305.10355 | Tracks whether continual FT induces hallucination | Polling: "Is there a [object] in this image?" |

### 6.2 Attacks Mentioned in User Research — Verification Status

| Attack | Verification Status | Note |
|:---|:---|:---|
| JailBreakV-28K | [Source not confirmed — do not cite until arXiv ID verified] | Luo et al. is the author group; ID needs independent confirmation |
| Image-hijacking (image overrides user intent) | [No specific benchmark paper confirmed] | Valid attack concept; needs specific benchmark reference |
| Adversarial image perturbations (pixel-level) | [No specific VLM safety benchmark confirmed] | Valid; use ImageNet-C style transforms as a proxy |
| MMHal-Bench | [Not confirmed from primary source yet] | Referenced in multiple VLM papers; needs direct citation |

---

## Section 7: Benchmark Reference

| Benchmark | What It Measures | Verified Source | Notes |
|:---|:---|:---|:---|
| **AdvBench** | Attack success on harmful instruction set | Zou et al. 2023 (text) | Use both text-only and image-embedded variants |
| **HarmBench** | Standardized harmful behavior + robust refusal | arXiv:2402.04249 | 18 red-teaming methods evaluated |
| **MM-SafetyBench** | Multimodal safety across 13 risk categories | arXiv:2311.17600 | 5,040 text-image pairs; 12 models evaluated |
| **FigStep dataset** | Typographic visual jailbreak | arXiv:2311.05608 | 82.50% avg ASR on 6 open-source LVLMs |
| **POPE** | Object hallucination (Random/Popular/Adversarial) | arXiv:2305.10355 | Binary: "Is [X] in this image?" polling |
| **RTVLM** | Multimodal red teaming (privacy, fairness, misleading, safety) | He et al. 2024 | Used by SafeVLM; 4-dimensional safety evaluation |
| **TruthfulQA** | Factual accuracy | Lin et al. 2022 | Used by Bach et al. Sec. 5.2 |
| **XSTest** | Over-refusal measurement | [arXiv ID needed] | Safe/unsafe balanced test set |
| **MMBench / SEEDBench / MME** | General VLM capability regression | [verified in SafeVLM paper] | Used to confirm safety ≠ capability collapse |

---

*Document version: 2026-09-15. Last updated by Aryaman Singh Dev. All empirical claims traced to primary sources per the vlm-gradient-safety SKILL.md policy.*
