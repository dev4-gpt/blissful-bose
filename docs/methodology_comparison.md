# Methodology Comparison: Continual Safety Alignment in VLMs
## All Known Approaches, Honest Tradeoffs, and Our Recommended Strategy

**Lead Researcher**: Aryaman Singh Dev  
**Policy**: Every claim is cited. "✅ Verified" = arXiv abstract confirmed. "🔍 Confirmed" = author/venue/content confirmed from search. Papers without confirmed IDs are explicitly flagged.

---

## The Taxonomy

There are **6 distinct families** of methods for preserving safety alignment during fine-tuning. They differ fundamentally in *when* they intervene and *what* they modify.

```
INTERVENTION TIMELINE:
─────────────────────────────────────────────────────────────────────
BEFORE FT          DURING FT              AFTER FT        INFERENCE
─────────────────────────────────────────────────────────────────────
Vaccine            Moderate-Gi (Bach)     Antidote        CMRM
RepNoise           LARF                   SafeLoRA*       HiddenDetect
Booster            SaLoRA                 Model Merging   VLMGuard-R1
                   EWC / KL-reg           (Repair)        System Prompt
                   O-LoRA / DER
                   VLGuard (data mix)
─────────────────────────────────────────────────────────────────────
* SafeLoRA can also be applied post-hoc to LoRA weights
```

---

## Family 1: Data-Centric Filtering (During FT)

**Core idea**: Select which training samples to use. Don't change the optimizer, architecture, or loss function — just decide what the model sees.

### Method 1A: Moderate-$G_i$ (Bach et al., ACL 2026)
**arXiv**: 2604.17215 ✅  
**Mechanism**: Compute per-sample gradient norm at the aligned model. Select the 20% of samples closest to the median norm. Avoids both alignment-reversing (high-$G_i$) and useless (low-$G_i$) samples.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐⭐ | AdvBench ASR: 10.2% vs 36.7% baseline [Table 1] |
| Task performance | ⭐⭐⭐⭐ | Downstream avg: 60.9% (vs 60.1% Low-Gi, 58.1% Qwen3-4B) [Table 1] |
| Compute cost | ⭐⭐⭐ | ~51% training overhead [Appendix] |
| Requires safety data | ✅ No | Works on any benign downstream dataset |
| VLM adaptation needed | 🔧 Yes | Label masking, micro-batching, attribution mode selection |
| Implementation complexity | Medium | 3-stage algorithm; existing code in src/selection/ |

**Best for**: Our primary method. Starting point for Phase 1.

---

### Method 1B: LARF — Layer-Aware Representation Filtering (EMNLP 2025)
**Venue**: EMNLP 2025 🔍 (Li, Li, Lu, Wei, Li, Shao, Sha — Shanghai AI Lab)  
**Code**: github.com/LLLeoLi/LARF  
**Mechanism**: Identifies safety-sensitive layers. Filters fine-tuning samples based on their representation in those layers — samples that activate "safety-degrading" patterns are removed.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐ | Confirmed effective on harmful fine-tuning attacks [EMNLP 2025] |
| Task performance | ⭐⭐⭐⭐ | Minimal task degradation reported |
| Compute cost | ⭐⭐⭐⭐ | Forward pass only per sample (cheaper than Bach's backward pass) |
| Requires safety data | ⚠️ Indirectly | Needs to identify "safety-degrading" signal |
| VLM adaptation needed | 🔧 Yes | Need to identify which VLM layers are safety-sensitive |
| Implementation complexity | High | Requires internal layer activation analysis |

**Critical distinction**: LARF filters samples that *look* unsafe in representation space. Bach et al. filter samples whose *gradients* point toward unsafe territory — even if the content is perfectly benign. For clean medical/visual datasets, LARF would filter nothing; Bach et al. still filters ~80% of the data.

**Best for**: Complement to Moderate-Gi when some training data may contain problematic content.

---

### Method 1C: VLGuard Data Mixing (ICML 2024)
**arXiv**: 2402.02207 ✅ (Zong et al.)  
**Mechanism**: Adds ~2,000 curated safety image-text pairs into every fine-tuning batch as a protective buffer. No filtering — just augmentation.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐ | Works in controlled settings [ICML 2024] |
| Task performance | ⭐⭐⭐⭐ | "Almost no cost" per paper title |
| Compute cost | ⭐⭐⭐⭐⭐ | No overhead — just adding samples |
| Requires safety data | ❌ Yes | Needs VLGuard dataset available |
| VLM adaptation needed | ✅ No | Already a VLM method (LLaVA-1.5 tested) |
| Implementation complexity | Low | Drop-in dataset augmentation |

**Best for**: Our VLM-specific baseline. Easy to implement, published VLM result, directly comparable.

---

## Family 2: Parameter-Centric Regularization (During FT)

**Core idea**: Add a penalty to the loss that prevents parameters from moving too far from the aligned model.

### Method 2A: EWC — Elastic Weight Consolidation (Kirkpatrick et al., Science 2017)
**Mechanism**: Identifies "important" parameters via Fisher information matrix. Adds quadratic penalty to prevent their modification.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐ | **Hurts**: HarmBench ASR 31.0% vs 27.8% baseline [Bach et al. §5.2] |
| Task performance | ⭐⭐⭐ | Originally designed for task preservation |
| Requires safety data | ✅ No | Intrinsic method |
| Key flaw | ❌ | Fisher importance ≠ safety importance. Safety parameters ≠ task parameters. |

**Verdict**: **Failed method for safety**. Bach et al. proved this experimentally. EWC protects task-critical weights, but safety-critical weights overlap poorly. Include as baseline only to show it fails.

---

### Method 2B: KL Divergence Regularization
**Mechanism**: Adds $\text{KL}(p_\theta \| p_{\theta_0})$ to the loss, penalizing output distribution shift from aligned model.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐ | HarmBench ASR: 27.7% vs 27.8% baseline [Bach et al. §5.2] — negligible |
| Task performance | ⭐⭐⭐ | Moderate; KL weight must be tuned |
| Key flaw | ❌ | Constrains *output distribution* globally, not safety-specific behavior |

**Verdict**: Marginally better than nothing. Include as baseline.

---

### Method 2C: O-LoRA / Orthogonal Gradient (ICLR 2024 area)
**Mechanism**: Enforces LoRA updates to be orthogonal to previous task gradients, preventing overwriting prior knowledge.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐ | HarmBench ASR: 10.0% [Bach et al. §5.2] — competitive |
| Task performance | ⭐⭐⭐⭐ | Good continual learning performance |
| Requires safety data | ✅ No | Intrinsic method |
| Key insight | ⚠️ | Best competing parameter-centric method. Bach et al.'s Moderate-Gi still beats it (5.0% vs 10.0%). |

**Best for**: Strong non-data-centric baseline in our comparison table.

---

### Method 2D: OGPSA — Orthogonal Gradient Projection for Continual Safety Alignment
**arXiv**: [arXiv:2602.07892](https://arxiv.org/abs/2602.07892) (HTML: [arxiv.org/html/2602.07892v1](https://arxiv.org/html/2602.07892v1)) ✅  
**Mechanism**: Projects task gradients into the null-space/orthogonal complement of the safety-critical subspace throughout training. Ensures that parameter updates do not alter alignment representations.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐ | Strong theoretical bounds on orthogonal protection |
| Task performance | ⭐⭐⭐ | Capacity reduction as gradient space is constrained |
| Compute cost | ⭐⭐ | High; maintains and updates projection basis matrix online |
| Requires safety data | ⚠️ Yes | Needs safety data to construct safety gradient subspace |
| VLM adaptation needed | 🔧 Yes | Must compute cross-modal safety projections |

**Critical distinction**: OGPSA modifies the *optimizer* step using an explicit projection matrix; Bach et al. and our method modify the *input dataset* via sample filtering. Our method works with vanilla optimizers and standard LoRA/SFT pipelines.

---

## Family 3: LoRA Subspace Methods (During FT — Parameter-Efficient)

**Core idea**: Constrain or project LoRA weight updates to stay within "safe" subspaces of parameter space.

### Method 3A: SafeLoRA (Hsu et al., 2024)
**arXiv**: Confirmed from search (Hsu et al., 2024, post-hoc projection method) 🔍  
**Mechanism**: Identifies "safety-aligned subspaces" from the displacement vector between base and aligned models ($\theta_{\text{aligned}} - \theta_{\text{base}}$). Projects LoRA adapter weights onto this subspace after fine-tuning. If cosine similarity between new weights and safety direction drops below threshold, hard-project back.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐ | Confirmed effective across harmful fine-tuning scenarios [arXiv] |
| Task performance | ⭐⭐⭐ | Projection can reduce task-specific expressivity |
| Requires safety data | ⚠️ Implicitly | Needs access to base + aligned model pair |
| VLM adaptation | 🔧 Possible | Project language backbone LoRA using VLM alignment delta |
| Key advantage | | Works post-hoc on already-trained LoRA |
| Key flaw | | Requires knowing the "safe direction" a priori |

**How to adapt for VLMs**: The "safety subspace" would be computed from $\theta_{\text{Qwen2-VL-Instruct}} - \theta_{\text{Qwen2-VL-base}}$. Apply projection to language LoRA adapters after each task's fine-tuning.

**Best for**: Phase 2 complement. Easy to layer on top of our Moderate-Gi method as a post-hoc correction step.

---

### Method 3B: SaLoRA — Safety-Alignment Preserved LoRA (ICLR 2025)
**arXiv**: 2501.01774 🔍 (Li et al., ICLR 2025)  
**Mechanism**: Splits LoRA into two components: (1) a **fixed safety module** initialized from safety data that is frozen during fine-tuning; (2) a task-specific trainable module initialized to preserve safety trajectory. The fixed module acts as a permanent safety anchor.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐⭐ | ICLR 2025 — strong results claimed |
| Task performance | ⭐⭐⭐⭐ | Task module has full expressivity |
| Requires safety data | ❌ Yes | Safety module initialization requires safety-labeled data |
| VLM adaptation | 🔧 Possible | Safety module would cover both language LoRA and projector |
| Implementation complexity | High | Requires modifying LoRA initialization |

**Best for**: Phase 2 or 3, when we have VLGuard safety data available as the anchor dataset.

---

## Family 4: Pre-FT Alignment Hardening (Before Fine-Tuning Happens)

**Core idea**: Make the aligned model more robust to future fine-tuning attacks *before* deploying it for fine-tuning. Analogy: vaccination before exposure.

### Method 4A: Vaccine (Huang et al., 2024)
**Venue**: 2024, Huang et al. 🔍  
**Mechanism**: During alignment stage (before deployment), perturb embeddings to simulate future fine-tuning drifts. Train the model to maintain safety despite these perturbations.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐ | Strong against harmful fine-tuning attacks |
| Applies to our setting | ⚠️ Partial | We're fine-tuning an *already deployed* aligned model — Vaccine must be applied before deployment |
| VLM adaptation | 🔧 Possible | Perturb visual embeddings too |
| Key constraint | ❌ | Requires re-running alignment — we don't control Qwen2-VL's initial training |

**Verdict**: Theoretically compelling but inapplicable to our exact setting (we use a pre-trained aligned model as-is). Good to cite in Related Work as a "complementary alignment-stage defense."

---

### Method 4B: RepNoise — Representation Noising (Rosati et al., 2024)
**Mechanism**: During alignment, inject noise into harmful representations across all layers, making them hard to recover via fine-tuning.

Same applicability constraint as Vaccine — requires controlling the initial alignment stage. **Include in Related Work only.**

---

## Family 5: Memory-Based Continual Learning (During FT)

**Core idea**: Store a replay buffer of alignment-critical examples and interleave them during fine-tuning to prevent forgetting.

### Method 5A: DER — Dark Experience Replay (Buzzega et al., NeurIPS 2020)
**Venue**: NeurIPS 2020  
**Key evidence**: Unforgotten Safety (arXiv:2512.10150) found **DER outperforms all other CL methods** for safety preservation across LLaMA2-7B, Mistral-7B, and Gemma-2B. 🔍

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐⭐ | Best CL baseline per Unforgotten Safety [arXiv:2512.10150] |
| Task performance | ⭐⭐⭐ | Replay buffer competes with new task samples |
| Requires safety data | ❌ Yes | Needs a replay buffer of safety examples |
| VLM adaptation | 🔧 Possible | Add multimodal safety examples to replay buffer |
| Key advantage | | Well-studied; off-the-shelf implementations exist |

**Best for**: A strong CL baseline that's different from both data-filtering and parameter-regularization. Makes our paper's comparison richer.

---

## Family 6: Post-FT Repair & Inference-Time Methods

### Method 6A: Antidote (Huang et al., arXiv:2408.09600)
**Mechanism**: After harmful fine-tuning has occurred, identifies and prunes the specific weights introduced during fine-tuning. Restores safety post-hoc.

**Not applicable to our setting**: We prevent drift proactively. Antidote fixes it after. Include in Related Work as "reactive vs. proactive" contrast.

### Method 6B: CMRM (ACL 2025)
**Mechanism**: Inference-time representation correction — pulls multimodal hidden states toward text-only safe distribution.

**Not applicable for training-time protection**, but may be complementary: apply Moderate-Gi during training + CMRM at inference for dual protection. This could be a Phase 3 "defense combination" experiment.

### Method 6C: Aligned Model Merging (2025)
**arXiv**: [arXiv:2506.03189](https://arxiv.org/abs/2506.03189) (PDF: [arxiv.org/pdf/2506.03189](https://arxiv.org/pdf/2506.03189)) ✅  
**Mechanism**: Post-hoc weight merging and task-vector arithmetic between downstream fine-tuned weights and initial safety-aligned checkpoints.

| Dimension | Rating | Evidence |
|:---|:---:|:---|
| Safety preservation | ⭐⭐⭐ | Partially recovers safety |
| Task performance | ⭐⭐⭐ | Task interference across long sequences |
| Compute cost | ⭐⭐⭐⭐⭐ | Minimal post-hoc compute |
| Requires safety data | ✅ No | Merges model checkpoints |
| VLM adaptation | 🔧 Possible | Can merge vision projector and language LoRA weights |

**Critical limitation**: Model merging degrades quickly when applied sequentially across multiple tasks ($T > 2$), as task vectors begin cancelling each other.

---

## The Decision Matrix: Which Methods to Include and When

```
PHASE 1 — "CHEAP GATE" (Colab, 1 task, prove the hypothesis works in VLMs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRIMARY METHOD:   Moderate-Gi (Joint) [Our Proposed Method]
  BASELINES:        Full FT, Random, Low-Gi, High-Gi, EWC, KL-reg, O-LoRA
  VLM BASELINES:    VLGuard data mixing

PHASE 2 — FULL 4-TASK PIPELINE (Campus cluster)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ADD:              Moderate-Gi ablations (Language only, Projector only, Joint)
  ADD:              DER memory replay (strongest CL competitor)
  ADD:              SaLoRA or SafeLoRA (strongest LoRA-subspace competitor)
  ADD:              LARF (strongest representation-filtering competitor)
  ADD:              OGPSA (orthogonal gradient projection competitor)

PHASE 3 — COMBINATION & PUBLICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EXPLORE:          Moderate-Gi + SafeLoRA post-hoc projection (stacking)
  EXPLORE:          Moderate-Gi + CMRM inference correction (dual defense)
  EXPLORE:          Moderate-Gi + DER replay (data filtering + memory)
  EXPLORE:          Aligned Model Merging vs. Data Selection across $T > 2$ tasks
  CITE NOT IMPL:    Vaccine, RepNoise, Booster (pre-deployment methods)
```

---

## The Grand Comparison Table

All methods scored consistently for our specific setting: **continual fine-tuning of a pre-aligned Small VLM on benign visual downstream tasks.**

| Method | Family | Modality | Needs Safety Data | Requires Arch Change | VLM-Ready | Compute Overhead | Safety Score | Task Score | **Our Role** |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Moderate-$G_i$ Joint** (Bach 2026) | Data-filter | LLM only | ✅ No | ✅ No | 🔧 Adapt | ~51% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **PRIMARY METHOD** |
| **Moderate-$G_i$ Language** | Data-filter | LLM only | ✅ No | ✅ No | 🔧 Adapt | ~51% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Ablation |
| **Moderate-$G_i$ Projector** | Data-filter | LLM only | ✅ No | ✅ No | 🔧 Adapt | ~51% | ⭐⭐⭐ | ⭐⭐⭐⭐ | Ablation |
| LARF (EMNLP 2025) | Data-filter | LLM only | ⚠️ Partial | ✅ No | 🔧 Adapt | Low | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Phase 2 baseline |
| VLGuard mixing (ICML 2024) | Data-augment | VLM ✅ | ❌ Yes | ✅ No | ✅ Ready | None | ⭐⭐⭐ | ⭐⭐⭐⭐ | VLM baseline |
| OGPSA (2026, [arXiv:2602.07892](https://arxiv.org/abs/2602.07892)) | Param-proj | LLM only | ⚠️ Partial | ✅ No | 🔧 Adapt | High | ⭐⭐⭐⭐ | ⭐⭐⭐ | Phase 2 competitor |
| EWC (Kirkpatrick 2017) | Param-reg | Any | ✅ No | ✅ No | ✅ Ready | High | ⭐ FAILS | ⭐⭐⭐ | Baseline (shows failure) |
| KL Regularization | Param-reg | Any | ✅ No | ✅ No | ✅ Ready | Low | ⭐⭐ | ⭐⭐⭐ | Baseline |
| O-LoRA | Param-LoRA | LLM only | ✅ No | ✅ No | 🔧 Adapt | Medium | ⭐⭐⭐ | ⭐⭐⭐⭐ | Baseline |
| DER Replay (NeurIPS 2020) | CL memory | Any | ❌ Yes | ✅ No | 🔧 Adapt | Medium | ⭐⭐⭐⭐ | ⭐⭐⭐ | Phase 2 CL baseline |
| SafeLoRA (2024) | LoRA-subspace | LLM only | ⚠️ Partial | ✅ No | 🔧 Adapt | Post-hoc | ⭐⭐⭐⭐ | ⭐⭐⭐ | Phase 2 combo |
| SaLoRA (ICLR 2025) | LoRA-subspace | LLM only | ❌ Yes | ✅ No | 🔧 Adapt | None extra | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Phase 2 combo |
| Vaccine (2024) | Pre-FT hardening | LLM only | ❌ Yes | ✅ No | 🔧 Adapt | Pre-train only | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Related Work only |
| RepNoise (2024) | Pre-FT hardening | LLM only | ❌ Yes | ✅ No | 🔧 Adapt | Pre-train only | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Related Work only |
| CMRM (ACL 2025) | Inference | VLM ✅ | ✅ No | ✅ No | ✅ Ready | Inference | ⭐⭐⭐ | ⭐⭐⭐⭐ | Phase 3 combo |
| Aligned Model Merging ([arXiv:2506.03189](https://arxiv.org/abs/2506.03189)) | Post-FT merge | VLM ✅ | ✅ No | ✅ No | 🔧 Adapt | Low | ⭐⭐⭐ | ⭐⭐⭐ | Phase 3 comparison |
| Antidote (2024) | Post-FT repair | LLM only | ❌ Yes | ✅ No | 🔧 Adapt | Post-hoc | ⭐⭐⭐ | ⭐⭐⭐ | Related Work only |

---

## Our Recommendation: A Layered Strategy Over 3 Phases

**The key insight**: No single method dominates across all dimensions. The research opportunity is to show that Moderate-Gi is the **best single method that requires no safety data** for the VLM continual fine-tuning setting — and then to explore whether combining it with complementary methods (SaLoRA for LoRA-subspace anchoring, CMRM for inference hardening) gives additional gains.

### What Makes Our Paper Novel vs. Any Prior Work

| Claim | Prior Work | Our Contribution |
|:---|:---|:---|
| Gradient-based sample selection works | Bach et al. (text LLMs only) | We replicate in VLMs |
| Visual projector contributes to alignment drift | [OPEN — never studied] | Our novel ablation |
| Multimodal attack surface (FigStep, MM-Safety) | Never evaluated in this setting | We evaluate it |
| Comparison of data-filter vs param-reg vs LoRA-subspace on VLMs | [Fragmented across 3 separate text-only papers] | Our unified VLM comparison |

---

## Suggested Reading Order (For You to Build Up Understanding)

If you want to deeply understand the field before the presentation:

**Week 1 — The Foundation**
1. `Continual_Safety_Alignment.md` (Bach et al. in-repo notes) — already have this ✅
2. Ji et al. arXiv:2406.06144 — *why* alignment breaks (elasticity proof, 15min read)
3. Peng et al. arXiv:2405.17374 — the safety basin geometry (VISAGE visual, 20min read)

**Week 2 — The VLM Safety Landscape**
4. SafeVLM arXiv:2405.13581 — architectural safety approach (20min)
5. FigStep arXiv:2311.05608 — the attack we must defend against (15min)
6. CMRM (ACL 2025) — inference-time alternative (15min)

**Week 3 — The Competing Methods**
7. Unforgotten Safety arXiv:2512.10150 — DER as the CL comparison point (20min)
8. SaLoRA arXiv:2501.01774 — best LoRA-subspace method (20min)
9. VLGuard arXiv:2402.02207 — data mixing baseline (10min)

**Week 4 — The Implementation**
10. `docs/gradient_strategy_dossier.md` — our math ✅
11. `docs/reproducibility_blueprint.md` — our code ✅
12. `src/selection/gradient_selector.py` — run the unit tests ✅
