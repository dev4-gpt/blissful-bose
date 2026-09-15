# Presentation Writeup: Safety Alignment of Small VLMs via Gradient-Based Sample Selection
## Fully Cited Research Deck — Zero Fabricated Numbers

**Researcher**: Aryaman Singh Dev | **Advisor**: Prof. Thao Minh Le (co-author of Bach et al.)  
**Institution**: Pennsylvania State University  
**Date**: September 2026

> **How to use this document**: Every claim below is grounded in a specific paper, section, or arXiv source.  
> Anywhere you see a 📎 box, that tells you exactly which table or figure to screenshot from the paper and insert into your slide.  
> Do NOT use the numbers from RESEARCH_METHODOLOGY_AND_VLM_SPEC.md until you have personally verified them against those tables.

---

## SLIDE 1 — Title

**Title**: Continual Safety Alignment in Small Vision-Language Models via Gradient-Based Sample Selection

**Subtitle**: Extending Bach et al. (ACL 2026, arXiv:2604.17215) to Multimodal Architectures

**Your name, PSU, date**

> 📎 **No table needed here. Place the Bach et al. paper header (authors + arXiv link) as a footnote on this slide.**

---

## SLIDE 2 — The Problem: Why Fine-Tuning Breaks Safety

### What to write on the slide:

Fine-tuning a safety-aligned VLM on completely **benign downstream tasks** (math, visual QA, medical QA, document reading) degrades its safety guardrails. The training data contains **no harmful content** — yet the model loses its ability to refuse harmful requests.

> **"Even fine-tuning on benign, non-malicious datasets can unintentionally weaken safety mechanisms, suggesting that alignment degradation is not merely a consequence of adversarial data but a structural property of fine-tuning itself."**
>
> *— Bach et al. (ACL 2026), Section 1 (Introduction), paragraph 2*  
> **Citation on slide**: Bach et al., arXiv:2604.17215, §1

Two established theoretical mechanisms explain why:

**Mechanism 1 — Elastic Reversion** *(Ji et al., arXiv:2406.06144)*:
- Models statistically "resist" alignment modifications and rebound toward their pretrained behavior under fine-tuning.
- The elastic force is proportional to dataset size:
$$F_{\text{elastic}} \propto |D_i| \cdot \Delta D_{\text{KL}}\left(p_\theta \;\|\; p_{D_i}\right)$$
- Because the pretraining corpus $|D_p|$ vastly exceeds the alignment dataset $|D_a|$, the pretrained distribution exerts orders-of-magnitude stronger pull on model behavior.
- *Source: This exact formula and explanation is from Ji et al. (arXiv:2406.06144), cited in Bach et al. §2.2*

**Mechanism 2 — Safety Basin Geometry** *(Peng et al., NeurIPS 2024, arXiv:2405.17374)*:
- Safety alignment places model parameters into a localized, flat region of the loss landscape — the **Safety Basin**.
- Safety basins have **sharp boundaries with step-function collapse**: a single large gradient update can push the model permanently outside the basin, destroying alignment with no graceful degradation.
- *Source: Bach et al. §2.1, citing Peng et al. (arXiv:2405.17374)*

**Why VLMs Are More Vulnerable**:
- A text-only LLM has one modality pathway. A VLM has three distinct trainable parameter groups: Vision Encoder, Multimodal Projector, and Language Backbone.
- Visual inputs (e.g. images with embedded text) bypass text safety filters entirely. This is the **VLM-specific additional attack surface** — confirmed by FigStep *(Gong et al., arXiv:2311.05608)*.

> 📎 **No table on this slide.** Use a schematic diagram (you can draw this):
> - Safety Basin as a green valley in a 2D loss landscape.
> - An arrow labeled "High-$G_i$ sample" climbing over the wall into the red danger zone.
> - Label the wall: "Sharp boundary (step-function collapse)" — this is verbally described in Bach et al. §2.1.

---

## SLIDE 3 — The Multimodal Attack Surface

### What to write on the slide:

**Why VLMs Need a Specialized Defense**

In text LLMs, the only attack pathway is through the text prompt. In VLMs, attackers have three independent pathways:

| Attack Type | Example | Dataset |
|:---|:---|:---|
| **Text-only jailbreak** | Direct harmful prompt | HarmBench (arXiv:2402.04249), AdvBench (Zou et al., arXiv:2307.15043) |
| **Visual typographic jailbreak** | Harmful instruction embedded as image text | FigStep (arXiv:2311.05608) |
| **Multimodal paired attack** | Image + text instruction co-designed to elicit harm | MM-SafetyBench (arXiv:2311.17600): 13 risk categories, 5,040 image-text pairs |
| **Transfer + diffusion attacks** | LLM-based jailbreaks transferred to vision inputs | JailBreakV-28K (arXiv:2404.03027, COLM 2024) |

**FigStep specifically**: Converts a harmful text instruction into an image using OCR/typography. The model reads it as visual text and complies — bypassing all text-level safety filters.
- *Source: Gong et al., FigStep (arXiv:2311.05608), Section 1 and Section 3*

**MM-SafetyBench**: The primary VLM safety evaluation benchmark.
- 5,040 image-text pairs across 13 safety-critical scenarios.
- *Source: Liu et al., MM-SafetyBench (arXiv:2311.17600), Section 2*

> 📎 **ATTACH**: Figure 1 from FigStep (arXiv:2311.05608) — shows the typographic attack pipeline visually.  
> 📎 **ATTACH**: Table 1 from MM-SafetyBench (arXiv:2311.17600) — shows the 13 risk category breakdown.

---

## SLIDE 4 — The Foundational Paper: Bach et al. (ACL 2026)

### What to write on the slide:

**Core Hypothesis** *(Bach et al. §3, paragraph 1)*:
> "We hypothesize that per-sample gradient magnitude indicates drift risk. High-gradient samples occur where aligned predictions diverge substantially from task targets — precisely where alignment training modified behavior away from pretrained tendencies."
>
> *Citation: Bach et al. (arXiv:2604.17215), §3, paragraph 1*

**The three gradient classes**:

The per-sample gradient norm for sample $i$ computed at the aligned model $\theta_0$:
$$G_i = \left\| \nabla_\theta \mathcal{L}(x_i, y_i; \theta_0) \right\|_2$$

| Class | Selection | Effect on Safety | Effect on Task Learning |
|:---|:---|:---|:---|
| **Low-$G_i$** | Bottom 20% | Better safety | Worse task (catastrophic forgetting) |
| **High-$G_i$** | Top 20% | Safety collapses | Moderate task performance |
| **Moderate-$G_i$** | Middle 20% closest to median | **Best safety** | **Best task performance** |

> *Source: Bach et al. §3.1 — "High-Gi selection retains only 62–72% of original alignment... while moderate-Gi selection preserves 83–88%"* (this specific 62–88% range is from §3.1 of the paper text).

**Safety basin retention results**:

> 📎 **ATTACH**: **Table 2 from Bach et al. (arXiv:2604.17215)** — shows VISAGE safety basin retention scores for High-$G_i$, Random, and Moderate-$G_i$.  
> This is the key table proving the 83–88% vs 62–72% retention difference. Take a screenshot of the entire table.

**Why "low gradient" also fails** *(Bach et al. §3, "Why not low-gradient samples?")*:
> "Low-Gi provides better safety preservation but consistently trades 0.8–1.9 points of task performance, revealing a Pareto tradeoff."
>
> *Citation: Bach et al. §3*

---

## SLIDE 5 — The Mechanism: Why High-$G_i$ Samples Are Dangerous

### What to write on the slide:

**The Root Cause: Format Mismatches, Not Harmful Content** *(Bach et al. Appendix — Sample Audit)*

> "High-gradient samples are often format mismatches, not content-based outliers. They are dominated by short-answer tasks where the aligned model's verbose output distribution diverges from terse targets."
>
> *Citation: Bach et al. (arXiv:2604.17215), Appendix — Sample Audit section*

**The Chain of Causation** (as described in Bach et al. §2.2 and §3):

```
Safety alignment makes the model verbose, explanatory, and cautious.
        ↓
Downstream benchmarks (e.g. SQuAD, MedMCQA) require single-token answers: "Yes", "No", "(A)"
        ↓
The aligned model's output distribution diverges sharply from the terse target.
        ↓
Cross-entropy loss spikes → Massive gradient norm Gi
        ↓
Optimizer applies a large parameter update in the direction of the reversion vector
        ↓
Model moves out of the safety basin → Safety collapses
```

**Gradient Direction Evidence** *(Bach et al. §3.2)*:
> "High-gradient samples exhibit higher directional alignment with the reversion direction compared to moderate-gradient samples in final-layer parameters."
>
> *Citation: Bach et al. §3.2 (Gradient Direction Analysis)*

**Why gradient clipping doesn't fix this** *(Bach et al. Appendix — "Why Not Gradient Clipping?")*:
> "Clipping attenuates step size but still trains on high-gradient samples, meaning the model still receives a learning signal pushing toward pretrained distributions. Our method removes these samples entirely."
>
> *Citation: Bach et al. Appendix, §"Why Not Gradient Clipping?"*

> 📎 **ATTACH**: **Table 4 from Bach et al. (arXiv:2604.17215)** — shows TopK-Cosine similarity between gradient directions and the reversion vector $\mathbf{r} = \theta_{\text{pre}} - \theta_{\text{align}}$ across parameter groups.

---

## SLIDE 6 — The Algorithm: 3-Stage Gradient-Based Selection

### What to write on the slide:

**Algorithm** *(Bach et al. §4.1)*:

The algorithm operates in three stages on each downstream training dataset $D_t$:

```
STAGE 1 — Loss-Based Pre-Filtering
  Remove samples with very low loss (already memorized — zero gradient signal)
  Remove samples with very high loss (outliers distorting gradient distribution)
  → Retain the middle portion for gradient computation.
  
STAGE 2 — Gradient Norm Computation
  For each surviving sample i, compute per-sample gradient norm:
    Gi = || ∇_θ L(xi, yi; θ0) ||₂
  (Requires micro-batching with batch size = 1 — individual backward passes)

STAGE 3 — Median-Based Selection
  Compute the median gradient norm M = median({Gi})
  Select the ρ fraction of samples closest to M:
    S_t = { i : |Gi − M| is smallest among ρ·N samples }
  Default: ρ = 0.2 (select 20% of data)
```

> *Source: Bach et al. §4.1 (Algorithm) and §4.2 (Sensitivity to Selection Ratio)*

**Why median, not mean?** *(Bach et al. §4.1)*:
> "We use median (not mean) for robustness against heavy-tailed gradient distributions."
>
> *Citation: Bach et al. §4.1*

**Computational cost** *(Bach et al. Appendix, Limitations section)*:
> "Focuses on text-only models... and incurs a ~51% computational overhead during training."
>
> *Citation: Bach et al. Appendix, Limitations*

**Selection ratio robustness** *(Bach et al. §4.2)*:
> "Results are robust across ρ ∈ [0.1, 0.4]. Smaller ρ (stricter filtering) provides slightly better safety at marginal task performance cost."
>
> *Citation: Bach et al. §4.2*

> 📎 **ATTACH**: Any figure from Bach et al. showing the selection ratio sensitivity (§4.2). This will be a line graph or bar chart showing ASR vs. different ρ values.

---

## SLIDE 7 — Main Results: Text LLM Baselines (Bach et al.)

### What to write on the slide:

**Experimental setup** *(Bach et al. §5.1)*:
- Models: Qwen2.5-7B-Instruct, LLaMA-3.1-8B-Instruct, Qwen3-4B-Instruct
- Task sequence: Dolly → GSM8K → MedMCQA → SQuAD v2
- Safety evaluation: AdvBench, HarmBench, TruthfulQA
- Baselines: Standard fine-tuning, Random sampling, KL-divergence regularization, O-LoRA, EWC, Gradient Clipping

**The headline result** *(Bach et al. §5.2, confirmed from paper text)*:
> "On Qwen2.5, our method achieves 10.2% ASR versus 36.7% for the baseline — representing a 3.6× reduction."
>
> *Citation: Bach et al. §5.2, Alignment Preservation*

**Truthfulness and capabilities** *(Bach et al. §5.2)*:
> "Moderate-Gi maintains factual accuracy matching or exceeding baselines and competitive general capabilities."
>
> *Citation: Bach et al. §5.2*

**Catastrophic forgetting** *(Bach et al. §5.4)*:
> "Moderate-Gi achieves significant improvements in BWT and reduces the maximum single-step performance drop."
>
> *Citation: Bach et al. §5.4*

> 📎 **ATTACH**: **Table 5 from Bach et al. (arXiv:2604.17215)** — the main ASR results table comparing all baselines across all three model families. **This is your primary evidence slide table.**
>
> 📎 **ATTACH**: **Table 6 from Bach et al. (arXiv:2604.17215)** — the BWT/catastrophic forgetting comparison table.
>
> **Note**: Take the actual numbers directly from these tables. Do NOT use any numbers from other files in this repository — only Tables 5 and 6 from the paper PDF.

---

## SLIDE 8 — Our Contribution: Porting to Vision-Language Models

### What to write on the slide:

**The open problem from the paper itself** *(Bach et al. Appendix, Limitations)*:
> "Focuses on text-only models (extending to vision-language models requires further investigation)."
>
> *Citation: Bach et al. Appendix, Limitations — this is the exact research gap we address.*

**Our target model**: `Qwen2-VL-2B-Instruct`

**VLM-Specific Architecture Challenge**:

In text LLMs, there is one trainable parameter group (LoRA on language transformer). In VLMs, the architecture decomposes into:

$$\Theta_{\text{VLM}} = \underbrace{\Theta_{\text{Vision}}}_{\text{frozen}} \cup \underbrace{\Theta_{\text{Projector}}}_{\text{trainable}} \cup \underbrace{\Theta_{\text{Language-LoRA}}}_{\text{trainable}}$$

**Our novel contribution — 3 Gradient Attribution Modes**:

The text paper uses a single $G_i$ over language LoRA weights. In VLMs, should $G_i$ be computed over the language model, the multimodal projector, or both?

$$G_i^{(L)} = \left\| \nabla_{\Theta_{\text{LM-LoRA}}} \mathcal{L}_i \right\|_2 \quad \text{(Language attribution — direct port of Bach et al.)}$$

$$G_i^{(P)} = \left\| \nabla_{\Theta_{\text{Projector}}} \mathcal{L}_i \right\|_2 \quad \text{(Projector attribution — cross-modal tension)}$$

$$G_i^{(J)} = \sqrt{\left(G_i^{(L)}\right)^2 + \lambda \left(G_i^{(P)}\right)^2} \quad \text{(Joint — holistic VLM signal)}$$

> **Research hypothesis**: High $G_i^{(P)}$ may specifically indicate visual grounding failures (visual-text projector mismatch), while high $G_i^{(L)}$ replicates the format-mismatch mechanism from text LLMs. The Joint mode $G_i^{(J)}$ accounts for both simultaneously.
>
> *This is our original formulation. There is no prior paper to cite — this is the novel ablation study we will publish.*

**Critical implementation detail — Multimodal Label Masking**:

Cross-entropy loss must be computed **only on target response tokens**. Visual tokens and prompt tokens must be masked to $-100$:
- Without masking: $G_i$ is dominated by visual reconstruction loss, not task-response mismatch.
- With masking: $G_i$ correctly measures only the alignment-relevant divergence on the model's answer.

> 📎 **No table to attach on this slide.** Draw a diagram of the Qwen2-VL-2B architecture showing the three parameter groups, which are frozen (ViT), and where gradients are intercepted (Projector, Language LoRA).

---

## SLIDE 9 — 4-Task Continual Curriculum for VLMs

### What to write on the slide:

**The task sequence mirrors Bach et al.'s 4 text domains** *(Bach et al. §5.1)*, replacing each text dataset with a multimodal equivalent:

| Stage | Bach et al. Text Task | Our VLM Equivalent | Modality Challenge |
|:---|:---|:---|:---|
| 1 | Dolly (instruction following) | **LLaVA-Instruct-150K** | General visual instruction following |
| 2 | GSM8K (math reasoning) | **MathVista** | Visual-mathematical reasoning from charts/diagrams |
| 3 | MedMCQA (medical QA) | **SLAKE / VQA-RAD** | Clinical image understanding and medical VQA |
| 4 | SQuAD v2 (reading comprehension) | **DocVQA** | Dense document OCR and layout reasoning |

> *Mapping rationale: This analogy is our own contribution. The text task sequence is from Bach et al. §5.1.*

> 📎 **No table to attach.** You can create a simple 4-box timeline diagram for this slide (text + image examples for each task type).

---

## SLIDE 10 — Evaluation Suite

### What to write on the slide:

We evaluate three orthogonal properties at each checkpoint after every task:

### Battery 1: Safety Metrics

| Benchmark | What it tests | Source |
|:---|:---|:---|
| **MM-SafetyBench** | 5,040 image-text pairs across 13 multimodal risk scenarios | Liu et al., arXiv:2311.17600, §2 |
| **FigStep** | Typographic image jailbreaks via OCR exploitation | Gong et al., arXiv:2311.05608, §3 |
| **JailBreakV-28K** | Diverse visual jailbreaks (transfer, diffusion, OCR) | Luo et al., arXiv:2404.03027, COLM 2024 |
| **HarmBench (text slice)** | 510+ standardized red-teaming queries with Llama-Guard-3-8B judge | Mazeika et al., arXiv:2402.04249 |

### Battery 2: Truthfulness & Hallucination

| Benchmark | What it tests | Source |
|:---|:---|:---|
| **POPE** | Object hallucination (random, popular, adversarial splits) | Li et al., arXiv:2305.10355 |
| **MMHal-Bench** | Hallucination severity scoring | Bird et al. |

### Battery 3: Task Capability

Evaluate downstream task accuracy on LLaVA-Bench, MathVista, VQA-RAD, DocVQA to ensure Moderate-$G_i$ does not sacrifice multimodal capability.

**Safety Judge**: Llama-Guard-3-8B classifies each response as safe or unsafe.  
*Used in Bach et al. §5.1 for AdvBench/HarmBench evaluation.*

**Metric formulas**:

$$\text{ASR} = \frac{\text{Number of unsafe responses}}{M} \times 100\%$$

$$\text{BWT} = \frac{1}{T-1}\sum_{i=1}^{T-1}(R_{T,i} - R_{i,i})$$

*(Backward Transfer measures how much earlier task performance degrades after training subsequent tasks. Closer to 0 is better.)*

> 📎 **ATTACH**: Table 1 from MM-SafetyBench (arXiv:2311.17600) — 13 category breakdown.  
> 📎 **ATTACH**: Figure from HarmBench (arXiv:2402.04249) showing the benchmark taxonomy — this shows why it's the SOTA safety evaluation standard.

---

## SLIDE 11 — SOTA Baseline Comparison & Why Data-Centric Wins

### What to write on the slide:

**Six families of methods** for preserving safety during fine-tuning:

| Family | Method | Mechanism | Key Limitation |
|:---|:---|:---|:---|
| **Data-centric (Ours)** | **Moderate-$G_i$** | Filter training samples by gradient norm | ~51% training overhead; 0 inference overhead |
| Regularization | EWC, KL-Divergence | Penalize parameter drift from $\theta_0$ | Protects task but fails to fully prevent alignment drift (Bach et al. §5.2) |
| Parameter isolation | O-LoRA, Safe LoRA | Orthogonal subspace updates | Requires custom LoRA setups; high variance across tasks |
| Safety replay | VLGuard mix | Add 5–10% safety data at each task | Requires curated safety dataset at every adaptation step |
| Post-hoc | SafeLoRA, Antidote | Project weights back to safe subspace after training | Adds post-training optimization step; degrades task performance |
| Inference-time | VLMGuard-R1, system prompts | Reasoning-driven output guardrails | Adds inference latency; does not fix underlying parameter drift |

> *Source for baseline taxonomy: Bach et al. §5.1 lists EWC, KL-reg, O-LoRA, Gradient Clipping as their comparisons. VLGuard is from Zong et al. (ICML 2024, arXiv:2402.02207). SaLoRA is from arXiv:2501.01774 (ICLR 2025).*

**Key advantage of data-centric approach**:
- Requires **no curated safe data** at each adaptation step.
- Requires **no architectural changes**.
- Adds **zero inference overhead**.
- Works on any benign downstream dataset.

> *Source: Bach et al. Abstract and §1 (Introduction), paragraph 4*

> 📎 **ATTACH**: **Table 5 from Bach et al. (arXiv:2604.17215)** — shows all baseline ASR numbers side by side (the same table as Slide 7). On this slide, highlight Moderate-$G_i$ vs. EWC and O-LoRA specifically.
>
> 📎 **ATTACH**: **Table 6 from Bach et al. (arXiv:2604.17215)** — shows BWT across all baselines.

---

## SLIDE 12 — Execution Plan (Phase 1 Colab, Phase 2 Cluster)

### What to write on the slide:

**Phase 1: Free Compute Hypothesis Check** *(per advisor directive, Sept 2026)*

- **Model**: Qwen2-VL-2B-Instruct (4-bit QLoRA — reduces VRAM below 12 GB)
- **Task**: LLaVA-Instruct-150K at 10% calibration subsample (~15,000 samples)
- **Compute**: Free Google Colab T4 GPU
- **Goal**: Verify that Moderate-$G_i$ selection, when applied to multimodal inputs with proper label masking, produces a meaningfully different safety basin retention than High-$G_i$ and Random selection.
- **What we measure**: FigStep ASR and MM-SafetyBench ASR (subsampled 200 pairs) on the checkpoint after Task 1 only.
- **Decision gate**: If Moderate-$G_i$ shows even a relative ASR reduction vs. Random, the hypothesis is confirmed and Phase 2 proceeds.

**Phase 2: Full 4-Task Sequence** *(pending cluster clearance)*

- Full LLaVA-150K → MathVista → SLAKE → DocVQA sequence.
- Full ablation: $G_i^{(L)}$ vs. $G_i^{(P)}$ vs. $G_i^{(J)}$.
- Full SOTA baselines: Full FT, EWC, KL-reg, VLGuard replay, SaLoRA, O-LoRA.
- Full evaluation: 5,040 MM-SafetyBench + 1,000 FigStep + POPE + task benchmarks.

> 📎 **No table here.** Use a simple two-row timeline diagram: "Phase 1 (Now) → Phase 2 (Cluster)" with bullet points for each.

---

## SLIDE 13 — Summary & Contributions

### What to write on the slide:

**What we established**:

1. Fine-tuning aligned VLMs on benign data causes safety collapse through elastic reversion and safety basin escape.
   - *Sources: Bach et al. §1–§3; Ji et al. (arXiv:2406.06144); Peng et al. (arXiv:2405.17374)*

2. In text LLMs, selecting the 20% of training samples closest to the median gradient norm (Moderate-$G_i$) preserves 83–88% of the safety basin while cutting ASR from 36.7% to 10.2% on Qwen2.5.
   - *Source: Bach et al. §3.1 and §5.2 — confirm exact numbers from Tables 2 and 5*

3. VLMs face an additional multimodal attack surface (FigStep, MM-SafetyBench) that text-only defenses cannot address.
   - *Sources: FigStep (arXiv:2311.05608), MM-SafetyBench (arXiv:2311.17600)*

4. We extend Moderate-$G_i$ to VLMs via three novel gradient attribution modes ($G_i^{(L)}, G_i^{(P)}, G_i^{(J)}$) and a strict multimodal label masking protocol.
   - *Source: Our original contribution — addresses Bach et al. Appendix Limitations (open future work)*

**What we will determine experimentally**:
- Whether the format-mismatch mechanism transfers from text LLMs to multimodal settings.
- Which attribution mode ($G_i^{(L)}$, $G_i^{(P)}$, or $G_i^{(J)}$) best predicts multimodal safety drift.

> 📎 **ATTACH on this slide**: **Table 2 from Bach et al.** (safety basin retention) next to a simple visual of the VLM architecture — to show the "problem confirmed for text" + "our extension to multimodal" contrast.

---

## Paper-to-Slide Citation Checklist

Use this to know exactly which paper section and table to open before each slide:

| Slide | Claims That Need a Table/Figure | Which File | Exact Location |
|:---|:---|:---|:---|
| Slide 2 | Safety basin sharp boundaries | Bach et al. (2604.17215v1.pdf) | §2.1 — read the paragraph, no table |
| Slide 2 | Elastic force formula | Ji et al. (arXiv:2406.06144) | §3, Eq. for $F_{\text{elastic}}$ |
| Slide 3 | FigStep attack example | FigStep PDF (arXiv:2311.05608) | Figure 1 — screenshot this |
| Slide 3 | MM-SafetyBench 13 categories | MM-SafetyBench PDF (arXiv:2311.17600) | Table 1 or Section 2 — screenshot this |
| Slide 4 | Safety basin retention 62–88% | Bach et al. (2604.17215v1.pdf) | **Table 2** — screenshot this whole table |
| Slide 5 | Gradient direction alignment with reversion vector | Bach et al. (2604.17215v1.pdf) | **Table 4** — screenshot this |
| Slide 6 | Selection ratio robustness ρ ∈ [0.1, 0.4] | Bach et al. (2604.17215v1.pdf) | §4.2 — look for figure or table |
| Slide 7 | 10.2% vs 36.7% ASR headline | Bach et al. (2604.17215v1.pdf) | **Table 5** — screenshot the Qwen2.5 rows |
| Slide 7 | BWT results | Bach et al. (2604.17215v1.pdf) | **Table 6** — screenshot this |
| Slide 10 | MM-SafetyBench category list | MM-SafetyBench PDF (arXiv:2311.17600) | Table 1 |
| Slide 11 | All baseline ASR results | Bach et al. (2604.17215v1.pdf) | **Table 5** — full table |
| Slide 11 | All baseline BWT results | Bach et al. (2604.17215v1.pdf) | **Table 6** — full table |
| Slide 13 | 83–88% retention + 10.2% ASR | Bach et al. (2604.17215v1.pdf) | Table 2 + Table 5 |

---

## Papers You Need Open While Building Slides

| Paper | arXiv | Key Table/Section | When You Need It |
|:---|:---|:---|:---|
| Bach et al. — Main paper | 2604.17215 (PDF on disk) | Table 2, Table 4, Table 5, Table 6, §3.1, §4.1, Appendix | Slides 4, 5, 6, 7, 11, 13 |
| Ji et al. — Elasticity | arXiv:2406.06144 | §3, elastic force formula | Slide 2 |
| Peng et al. — VISAGE | arXiv:2405.17374 | §3, Figure 2 (loss landscape) | Slide 2 |
| Gong et al. — FigStep | arXiv:2311.05608 | Figure 1, Table 1 | Slide 3 |
| Liu et al. — MM-SafetyBench | arXiv:2311.17600 | Table 1, §2 | Slides 3, 10 |
| Luo et al. — JailBreakV-28K | arXiv:2404.03027 | §2 overview | Slide 10 |
| Mazeika et al. — HarmBench | arXiv:2402.04249 | Benchmark overview | Slide 10 |
| Li et al. — POPE | arXiv:2305.10355 | §3 | Slide 10 |
