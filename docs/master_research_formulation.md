# Master Research Formulation
## Safety Alignment of Small VLMs via Gradient-Based Sample Selection

**Researcher**: Aryaman Singh Dev | **Advisor**: Prof. Thao Minh Le (co-author of Bach et al.)  
**Affiliation**: Pennsylvania State University  
**Target Venue**: CVPR / ACL / NeurIPS (Safety & Multimodal Track)

---

## The Core Idea in One Sentence

Bach et al. (ACL 2026) proved that a specific class of training samples — high-gradient ones — are the primary cause of safety erosion in fine-tuned text LLMs. **We replicate this finding in Small Vision-Language Models, replacing every text-only component with a multimodal equivalent.**

---

## PART 1: WHAT BACH ET AL. DID (The Procedure We Are Following)

This is the exact procedure from the paper. Every section below maps directly to a section of Bach et al. 2026.

### Step 1 — Problem Formulation [Bach et al. §2.3]

**Their setting**: An aligned text LLM must learn T tasks sequentially from benign downstream datasets $\{D_1, ..., D_T\}$ (Dolly → GSM8K → MedMCQA → SQuAD v2). After fine-tuning, safety guardrails (refusal of harmful requests, truthfulness) are eroded — even though the training data had no harmful content.

**Their core question**: *Which training samples cause this drift, and can we simply avoid them?*

**Their answer**: Per-sample gradient norm $G_i = \|\nabla_\theta \mathcal{L}(x_i, y_i; \theta_0)\|_2$ computed at the aligned model predicts alignment drift risk. High-$G_i$ samples trigger elastic reversion toward the unaligned pretrained distribution.

**Their constraint framing**: Standard continual learning preserves task knowledge. Their problem adds a second constraint — the model must remain within the **safety basin** throughout training.

---

### Step 2 — Mechanism Analysis [Bach et al. §3]

**Their hypothesis**: High-gradient samples occur where the aligned model's predictions diverge from task targets — exactly where alignment training modified the model *away* from pretrained behavior. Training on them reverses those modifications.

**Their validation (two experiments)**:

*Experiment A — Safety Basin Retention (VISAGE):*
Fine-tune on 20% of Dolly with different selection strategies. Measure VISAGE score retention.
- High-$G_i$: retains 62–72% of safety basin
- Random: retains 72–73%
- **Moderate-$G_i$: retains 83–88%** ← their method wins
[Source: Bach et al. Table 2]

*Experiment B — Gradient Direction Analysis (TopK-Cosine):*
Compute TopK-cosine similarity ($k=1000$) between each sample's gradient and the reversion vector $\mathbf{r} = \theta_{\text{pretrain}} - \theta_{\text{aligned}}$.
- High-$G_i$ samples show significantly higher directional alignment with reversion vector in **final-layer parameters** (V/O projections in Qwen, MLP in LLaMA)
- Middle layers: no significant signal ($p > 0.38$)
[Source: Bach et al. §3.2, Table 4]

**Their mechanistic finding (Appendix E.1)**: High-gradient samples are **format mismatches** — short-answer tasks (single-token "Yes", "No") where the aligned model's verbose distribution diverges from the terse target. They are NOT content-based outliers.

---

### Step 3 — The Algorithm [Bach et al. §4.1]

Three stages, ratio $\rho = 0.2$:

```
STAGE 1: Loss Pre-Filter
  Remove bottom 16% and top 16% by loss → reduces backward pass cost by ~32%
  
STAGE 2: Per-Sample Gradient Norm G_i
  Single-sample backward pass (B=1) for each remaining candidate
  G_i = ||∇_θ L(x_i, y_i; θ_0)||_2 over target parameter subset
  
STAGE 3: Moderate-Gi Selection
  μ_G = median(G_i)
  Select fraction ρ closest to μ_G (not lowest, not highest — nearest to median)
  Reason: LOW-Gi = no learning signal, HIGH-Gi = alignment reversing, MODERATE = Pareto optimal
```

**Robustness checks (Bach et al. §4.2)**: Tested $\rho \in [0.1, 0.4]$ — method is stable. Tested 4 different task orderings — method is stable. Training overhead: ~51% (Appendix). Inference cost: unchanged.

---

### Step 4 — Baselines [Bach et al. §5.1]

They compare against 6 baselines:

| Baseline | Category | Why It Fails |
|:---|:---|:---|
| Standard full fine-tuning | No protection | ASR: 36.7% on Qwen2.5-7B [Sec. 5.2] |
| Random selection (20%) | Data-centric | ASR: 31.1% — some protection by chance [Sec. 5.2] |
| Low-$G_i$ (bottom 20%) | Data-centric | Best safety, but 0.8–1.9pt task loss [Table 1] |
| EWC (Elastic Weight Consolidation) | Parameter-centric | ASR: 31.0% — **worse than baseline** [Sec. 5.2] |
| KL Divergence Regularization | Parameter-centric | ASR: 27.7% — minimal improvement [Sec. 5.2] |
| Gradient Clipping | Gradient-centric | Reduces step size but keeps all samples; direction unchanged [App.] |
| O-LoRA | Parameter-centric | Competitive LoRA variant; HarmBench ASR: 10.0% [Sec. 5.2] |

**Their method (Moderate-$G_i$)**: AdvBench ASR 10.2% (Qwen2.5-7B), HarmBench ASR 5.0%, BWT −4.3% vs −18.5% baseline [Qwen3-4B, Sec. 5.4]

---

### Step 5 — Evaluation Metrics [Bach et al. §5.1]

| Metric | What It Measures | Tool |
|:---|:---|:---|
| AdvBench ASR ↓ | Direct harmful instruction attacks (520 prompts, GCG suffixes) | Keyword matching + judge |
| HarmBench ASR ↓ | Diverse standardized harmful behavior | HarmBench judge |
| TruthfulQA ↑ | Factual accuracy / truthfulness | Standard benchmark |
| VISAGE Score ↑ | Safety basin volume retention | Custom perturbation analysis |
| BWT (Backward Transfer) ↑ | Catastrophic forgetting of earlier tasks | Accuracy matrix diagonal |
| FM (Forgetting Measure) ↓ | Maximum performance drop across tasks | Accuracy matrix |
| ARC-C, BoolQ, HellaSwag, Winogrande | General capability regression | Standard benchmarks |

---

### Step 6 — Models & Task Sequence [Bach et al. §5.1]

**Models**: Qwen2.5-7B-Instruct, LLaMA-3.1-8B-Instruct, Qwen3-4B-Instruct  
**Task sequence**: Dolly (15K general instructions) → GSM8K (math) → MedMCQA (medical) → SQuAD v2 (reading comprehension)  
**Selection**: 20% of each task's training data (3,000 samples from Dolly)

---

## PART 2: OUR VLM ADAPTATION — THE DIRECT MAPPING

Every step above gets a VLM-specific replacement. This is the exact contribution of our research.

### VLM-Step 1 — Problem Formulation (Extended)

**Our setting**: An aligned Small VLM (`Qwen2-VL-2B-Instruct`) must learn T vision-language tasks sequentially from benign visual datasets. After fine-tuning, safety guardrails are eroded — and the model becomes vulnerable to **multimodal jailbreaks** that exploit the visual modality as an attack surface.

**Our additional challenge vs. text-only**: Visual inputs create a **cross-modal attack surface** that text-only safety training cannot cover. A model may correctly refuse a harmful text prompt but comply when the same instruction is embedded in an image via FigStep-style typographic attack. [Source: FigStep, arXiv:2311.05608 — 82.50% avg ASR on 6 LVLMs]

**Research question extension**: *Does per-sample gradient norm, computed over multimodal inputs, still predict alignment drift? Which parameter subset — language backbone or multimodal projector — drives this drift?*

---

### VLM-Step 2 — Mechanism Analysis (VLM Version)

**New hypothesis**: In a VLM with frozen vision encoder, the gradient signal splits across:
- Language LoRA ($G_i^{(L)}$): signal from the language decoder
- Projector ($G_i^{(P)}$): signal from the cross-modal spatial merger
- Joint ($G_i^{(J)}$): combined signal

**VLM-specific prediction**: Final-layer alignment-critical parameters in the language backbone will show the same TopK-cosine signal as in text LLMs. The projector may show an *additional* signal specific to visual modality mismatches.

**New experiment**: Replicate Bach et al.'s TopK-cosine analysis on Qwen2-VL-2B with all three attribution modes. This is an **ablation study** that text-only papers cannot do — it is the primary novel scientific contribution.

**VLM complication — label masking**:
In text LLMs, the loss $\mathcal{L}(x_i, y_i)$ is computed over the entire output. In VLMs, the input contains visual tokens (`<|vision_start|>...<|vision_end|>`) that must be masked (`labels = -100`). Failing to mask them inflates gradient norms with image-complexity signal, not alignment-drift signal. This is a VLM-specific engineering requirement with no equivalent in text LLMs.

---

### VLM-Step 3 — Algorithm (VLM Version)

Same 3 stages, with VLM-specific modifications:

```
STAGE 1: Loss Pre-Filter (same logic, different implementation)
  DIFFERENCE: Labels masked for visual tokens before computing loss
  DIFFERENCE: Micro-batched forward (torch.no_grad()) for VRAM safety
  → Implementation: src/selection/gradient_selector.py

STAGE 2: Per-Sample Gradient Norm G_i (VLM version)
  DIFFERENCE: Single-sample B=1 backward with retain_graph=False
  DIFFERENCE: zero_grad(set_to_none=True) after EACH sample (not each batch)
  DIFFERENCE: Three attribution modes — Language, Projector, Joint (new ablation)
  
  LANGUAGE mode: gradient norm over LoRA adapters on LLM backbone only
  PROJECTOR mode: gradient norm over spatial merger projector parameters
  JOINT mode: sqrt(||G_language||^2 + ||G_projector||^2)
  
  → Research question: which mode best predicts multimodal safety drift?

STAGE 3: Median-Gi Selection (identical logic)
  μ_G = median(G_i)
  Select fraction ρ = 0.2 closest to median
  → Same as Bach et al. — tests whether the same filter works in VLMs
```

**VRAM constraint solution**: High-resolution images (448×448 → ~1024 image tokens) create large computation graphs. Solution: three-pass micro-batching — no_grad forward, then per-sample backward with graph freed immediately. [See src/training/trainer.py]

---

### VLM-Step 4 — Baselines (VLM version)

We keep all of Bach et al.'s text baselines AND add VLM-specific baselines:

| Baseline | Source | Why We Include It |
|:---|:---|:---|
| **Full fine-tuning (no selection)** | Bach et al. §5.1 | Primary baseline — measures scale of problem |
| **Random selection (20%)** | Bach et al. §5.1 | Data-centric chance baseline |
| **Low-$G_i$ (bottom 20%)** | Bach et al. §5.1 | Upper bound on safety preservation |
| **High-$G_i$ (top 20%)** | Bach et al. §5.1 | Lower bound — worst case |
| **EWC** | Kirkpatrick et al. 2017 | Parameter regularization — Bach et al. showed it HURTS safety (31.0% vs 27.8% baseline) |
| **KL Regularization** | Bach et al. §5.1 | Distribution regularization baseline |
| **O-LoRA** | Bach et al. §5.1 | Best competing method in text LLMs (10.0% HarmBench ASR) |
| **VLGuard mixing** | arXiv:2402.02207, ICML 2024 | VLM-specific: adds safety data to mixture — tests if data augmentation is better than our filtering |
| **Moderate-$G_i$ Language only** | Ours | Ablation: does language backbone gradient alone suffice? |
| **Moderate-$G_i$ Projector only** | Ours | Ablation: does projector gradient alone suffice? |
| **Moderate-$G_i$ Joint** | Ours — **proposed method** | Does combining both beat either alone? |

---

### VLM-Step 5 — Evaluation Metrics (VLM version)

Text-only metrics from Bach et al. are replaced or augmented:

| Bach et al. Metric | VLM Equivalent | Notes |
|:---|:---|:---|
| AdvBench ASR (text prompt) | **MM-SafetyBench ASR** (arXiv:2311.17600) | 5,040 text-image pairs, 13 risk categories — multimodal safety eval |
| AdvBench ASR (text) | Retain AdvBench text subset | Tests whether text safety is also preserved |
| HarmBench ASR | **FigStep ASR** (arXiv:2311.05608) | Typographic jailbreak — the modality-specific attack we must defeat |
| HarmBench ASR | **JailBreakV-28K** (arXiv:2404.03027) | 28K multimodal test cases; transfer-based attacks |
| TruthfulQA | **POPE** (arXiv:2305.10355) | Object hallucination — 3 splits (Random / Popular / Adversarial) |
| VISAGE score | VISAGE (same — model-agnostic perturbation metric) | Apply to VLM trainable parameters (projector + LM backbone) |
| BWT / FM | BWT / FM (same formula) | Computed over 4 visual task sequence |
| ARC-C, BoolQ, etc. | **MMBench / SEEDBench** | General VLM capability regression |
| Judge model: keyword filter | **Llama-Guard-3-8B** judge | Stronger, LLM-based binary safety classifier |

**Additional VLM-specific metric**: Measure **False Refusal Rate** on XSTest-style safe visual inputs. SafeVLM's own ablation (arXiv:2405.13581) found over-refusal on benign celebrity images, artwork, and code — we must show our method doesn't introduce this.

---

### VLM-Step 6 — Model & Task Sequence (VLM version)

**Model**: `Qwen2-VL-2B-Instruct` (HuggingFace: `Qwen/Qwen2-VL-2B-Instruct`)
- 2B parameters — runnable on Colab T4 (16GB) with LoRA + gradient checkpointing
- Already safety-aligned by Alibaba using RLHF
- Strong visual understanding (SoTA for 2B scale at time of writing)
- Chosen by Prof. Thao — confirmed in email 01/09/2026

**Task sequence** (4 visual domains, sequential):
| Task # | Dataset | Domain | Task Type | Approx Size |
|:--|:---|:---|:---|:---|
| 1 | LLaVA-Instruct-150K | General visual instruction following | Open-ended VQA | 150K (subsample 15K) |
| 2 | MathVista | Mathematical visual reasoning | Multiple choice + free-form | 6,141 |
| 3 | VQA-RAD + SLAKE | Medical visual QA | Short answer (radiology) | ~3,500 combined |
| 4 | DocVQA | Document understanding | Exact match / free-form | 50K (subsample 10K) |

**Why this sequence**: Visual domains span general→specialized→medical→document, matching the variety of Bach et al.'s text domains (Dolly→GSM8K→MedMCQA→SQuAD). Medical QA (Task 3) is the highest-stakes real-world application.

**Fine-tuning config**: LoRA rank=16, alpha=32, applied to attention (Q, K, V, O) + MLP; vision encoder frozen; batch size 4 with gradient accumulation 8.

---

## PART 3: RELATED WORK THAT CAN BE DIRECTLY REUSED IN OUR PIPELINE

This is the practical answer to "what can we borrow and implement right now?"

### Category A: Directly Usable — Drop-In Components

| Component | Source Paper | What We Reuse | Where in Our Code |
|:---|:---|:---|:---|
| **vLLM offline batched VLM inference** | vLLM docs (PagedAttention) | High-throughput eval: 5,040 MM-SafetyBench pairs in minutes not hours | `src/eval/vllm_evaluator.py` |
| **Llama-Guard-3-8B judge** | Meta AI Safety (2024) | Binary safe/unsafe classifier for all generated responses | `src/eval/safety_judge.py` |
| **Qwen2-VL LoRA adapter** | HuggingFace PEFT | Training framework — well-documented, Colab-compatible | `src/training/config.py` |
| **MM-SafetyBench dataset** | arXiv:2311.17600 | Primary safety benchmark — 5,040 image-text pairs, available on HuggingFace | `src/data/dataset_loader.py` |
| **FigStep attack images** | arXiv:2311.05608 | Typographic jailbreak test set — available on GitHub (ThuCCSLab/FigStep) | `src/data/dataset_loader.py` |
| **JailBreakV-28K** | arXiv:2404.03027 (COLM 2024) | Transfer-based multimodal jailbreak set — available on HuggingFace | `src/data/dataset_loader.py` |
| **POPE evaluation script** | arXiv:2305.10355 | Object hallucination evaluation — available on GitHub (RUCAIBox/POPE) | `src/eval/safety_judge.py` |
| **HarmBench eval harness** | arXiv:2402.04249 | Standardized red-teaming — GitHub: centerforaisafety/HarmBench | `src/eval/safety_judge.py` |
| **VISAGE metric** | arXiv:2405.17374 | Safety basin volume — reference implementation at ShengYun-Peng/llm-landscape | `src/eval/metrics.py` |

### Category B: Reference & Adapt — Need Modification for VLMs

| Paper | What to Adapt | How |
|:---|:---|:---|
| **Bach et al. Stage 3 Median Selection** (arXiv:2604.17215) | Exact median-distance ranking — port to multimodal by changing which params G_i covers | Already implemented in `src/selection/gradient_selector.py` |
| **CMRM representation correction** (ACL 2025) | The "representation gap" concept informs why projector gradient matters | Use as motivation in §2 (VLM-specific alignment challenge) |
| **VLGuard SFT dataset** (arXiv:2402.02207) | Use as baseline comparison: "mixing VLGuard data vs. filtering by gradient" | Add as one of our baselines in Table |
| **LARF layer identification** (EMNLP 2025) | Their finding: which layers are safety-sensitive in text LLMs → investigate if same layers are safety-sensitive in VLM projector | Inform our gradient attribution ablation |

### Category C: Benchmark Infrastructure (Off-the-Shelf)

All of these are available today and can be integrated with standard HuggingFace `evaluate` or standalone scripts:

```
MM-SafetyBench   → pip install datasets; load_dataset("LMiC/MM-SafetyBench")
FigStep          → github.com/ThuCCSLab/FigStep (images + questions)
JailBreakV-28K   → github.com/EddyLuo1232/JailBreakV-28K
POPE             → github.com/RUCAIBox/POPE
HarmBench        → github.com/centerforaisafety/HarmBench
VISAGE           → github.com/ShengYun-Peng/llm-landscape (port to VLM params)
VLGuard dataset  → HuggingFace: ys-zong/VLGuard
```

---

## PART 4: RESEARCH CHALLENGES (VLM-Specific, Not in Bach et al.)

These are challenges that DO NOT exist in the text-only paper. Solving them = novelty.

### Challenge 1: Visual Token Label Masking
**Problem**: If visual tokens contribute to loss, gradient norms measure image complexity, not alignment drift risk.  
**Solution**: Mask all non-response tokens (`labels = -100`) before computing $G_i$.  
**Open question**: Does the optimal masking strategy (response-only vs. prompt+response) affect which samples are selected? [OPEN — not yet validated]

### Challenge 2: Gradient Attribution Across Modalities
**Problem**: In text LLMs, there is only one type of trainable parameter. In VLMs, gradients split across language LoRA and projector. Which predicts safety drift better?  
**Solution**: Systematic ablation across $G_i^{(L)}$, $G_i^{(P)}$, $G_i^{(J)}$.  
**This is novel contribution #1** — no paper has done this analysis.

### Challenge 3: VRAM Constraints for Per-Sample Backward Passes
**Problem**: A single Qwen2-VL image at 448×448 generates ~1024 image tokens. Computing per-sample gradients retains large computation graphs, causing OOM on T4 16GB GPU.  
**Solution**: Three-pass micro-batching — Stage 1 (no_grad), Stage 2 (B=1 backward, graph freed immediately), Stage 3 (update selected only).  
**This is an engineering contribution** — enables the method on free-tier Colab.

### Challenge 4: Cross-Modal Jailbreak Evaluation (No Text-Only Equivalent)
**Problem**: After fine-tuning, the model may remain safe against text attacks but become vulnerable to FigStep typographic jailbreaks. Bach et al. only evaluate text attacks.  
**Solution**: Evaluate on FigStep, MM-SafetyBench, and JailBreakV-28K — full multimodal attack surface.  
**This is novel contribution #2** — evaluating the visual attack surface, not just text.

### Challenge 5: Over-Refusal on Benign Visual Inputs
**Problem**: Safety interventions in VLMs can cause over-refusal on benign visual inputs (SafeVLM: arXiv:2405.13581 reports false positives on celebrity images, artwork, code).  
**Solution**: Evaluate false refusal rate on a balanced safe/unsafe test set.  
**This is required for publication** — any reviewer will ask about it.

### Challenge 6: Compute Gate — Phase 1 on Colab, Phase 2 on Campus Cluster
**Problem**: Full 4-task 100K-sample pipeline requires more than Colab T4 can handle.  
**Solution**: Phase 1 (1-task "Cheap Gate") on Colab with 10% subsampling. Phase 2 (full 4-task) on campus cluster after Katie's clearance confirmation.  
**Source**: Prof. Thao email 01/09/2026: "Please start by setting up and practicing on free GPU services like Google Colab and Lightning AI."

---

## PART 5: ADVERSARIAL ATTACKS TO USE FOR ALIGNMENT TESTING

These are the exact attacks included in our evaluation, organized by modality and mechanism.

### A. Text-Based Attacks (Inherited from Bach et al.)

| Attack | Paper | Mechanism | Dataset |
|:---|:---|:---|:---|
| **GCG (Greedy Coordinate Gradient)** | Zou et al. 2023, arXiv:2307.15043 | Automated adversarial suffix optimization | AdvBench (520 harmful behaviors) |
| **Direct harmful prompting** | AdvBench baseline | No optimization; just direct harmful requests | AdvBench |
| **HarmBench red-team attacks** | arXiv:2402.04249 | 18 standardized attack methods | HarmBench behavior set |

### B. Multimodal Attacks (New — No Equivalent in Bach et al.)

| Attack | Paper | Mechanism | Dataset |
|:---|:---|:---|:---|
| **FigStep** | arXiv:2311.05608 | Harmful instructions embedded as typography in images → bypass text safety | FigStep dataset (GitHub: ThuCCSLab) |
| **Query-Relevant Image Injection** | MM-SafetyBench, arXiv:2311.17600 | SD-generated images contextually paired with harmful text to amplify attack | MM-SafetyBench (5,040 pairs) |
| **LLM-to-VLM Text Transfer** | JailBreakV-28K, arXiv:2404.03027 | Text jailbreaks crafted for LLMs transferred to VLM context | JailBreakV 20K text portion |
| **Image-Based Jailbreak** | JailBreakV-28K | Image-based jailbreak inputs from recent MLLM research | JailBreakV 8K image portion |

### C. Why These Attacks Cover Our Threat Model

```
THREAT MODEL: Attacker knows the model has been fine-tuned on downstream tasks
              and attempts to exploit the resulting safety erosion.

Text attacks  → Test: does text safety hold after visual fine-tuning?
FigStep       → Test: does the projector's visual safety channel hold?  
MM-SafetyBench→ Test: 13 standardized risk scenarios across modalities
JailBreakV    → Test: do text transfer attacks exploit the language backbone?
```

---

## PART 6: THE 10-MINUTE PRESENTATION SCRIPT

### Slide 1 — The Problem (1 min)
**Title**: "Fine-Tuning Makes Safe Models Unsafe — Even on Benign Data"

> "You take a safety-aligned model. You fine-tune it on a completely harmless dataset — medical Q&A, visual reasoning. When you're done, the model will help with harmful requests it would have refused before. This isn't because you trained it on bad data. It's a structural property of fine-tuning itself."

**Visual**: Show AdvBench ASR going from 2.1% (aligned) → 36.7% (after full fine-tuning on benign Dolly) [Source: Bach et al. Table 2]

---

### Slide 2 — Why It Happens: Elastic Reversion (1 min)
**Title**: "The Elastic Reversion Force"

> "Ji et al. (2024) proved this formally: the pretrained corpus is so large that it exerts a constant gravitational pull on model parameters. Safety alignment is a thin coating over this massive pretrained distribution. Fine-tuning releases that tension — the model snaps back."

$$F_{\text{elastic}} \propto |\mathcal{D}_{\text{pretrain}}| \cdot \Delta D_{\text{KL}}$$

**Visual**: Safety basin diagram — parameters inside a small safe region, fine-tuning pushes them out [Source: Peng et al. arXiv:2405.17374]

---

### Slide 3 — The Insight: Not All Samples Are Equal (1 min)
**Title**: "High-Gradient Samples Are the Culprits"

> "Bach et al. (ACL 2026) discovered that training samples contribute unequally. The ones that cause safety erosion are the ones with the highest gradient norms — format mismatches where the aligned model's verbose output disagrees with a terse task target. If you just skip those samples, safety is preserved."

**Visual**: Bar chart — High-Gi (18.4% ASR), Random (12.7%), Moderate-Gi (5.8%) vs baseline (2.1%) [Source: Bach et al. Table 2, Qwen2.5-7B]

---

### Slide 4 — The Method (1 min)
**Title**: "Three Stages: Filter, Score, Select"

> "The algorithm is simple: before training on any new task, compute a gradient norm for each training sample at the currently aligned model. Discard the ones with extreme norms. Train only on the samples closest to the median."

**Visual**: Three-stage pipeline diagram (Loss pre-filter → G_i computation → Median selection)

---

### Slide 5 — Results: It Works on Text LLMs (1 min)
**Title**: "This Works on Text LLMs — Can We Replicate It for VLMs?"

Show the main results table from Bach et al.:
- Qwen2.5-7B: Moderate-Gi ASR **10.2%** vs baseline **36.7%** (3.6× reduction)
- HarmBench: **5.0%** vs baseline **27.8%** (5.6× reduction)
- BWT: **−4.3%** vs **−18.5%** (less forgetting too)

> "This is the paper. **But it only works for text.** The paper's own Appendix F says: 'Extending gradient-based selection to vision-language models requires further investigation.' That's our research."

---

### Slide 6 — Our Contribution: VLM Extension (1.5 min)
**Title**: "Our Research: Same Idea, Multimodal Parameter Space"

> "In a VLM, the gradient isn't a single number — it splits across the language backbone and the visual projector. We investigate which one predicts safety drift. We also face a new threat: visual modality attacks like FigStep that text models can't even see."

**Visual**: VLM architecture diagram — ViT (frozen) → Projector → LLM backbone → Three gradient attribution modes ($G_i^{(L)}$, $G_i^{(P)}$, $G_i^{(J)}$)

**Key challenges we solve**:
1. Label masking for visual tokens (no equivalent in text LLMs)
2. VRAM-safe per-sample backward pass (micro-batching)
3. Multimodal attack evaluation (FigStep, MM-SafetyBench, JailBreakV-28K)

---

### Slide 7 — SOTA Landscape (1 min)
**Title**: "Where We Sit in the Literature"

Show the gap table — 3 rows, highlighted:
- Bach et al. (2026): gradient selection ✓, text only ✗, VLM ✗
- SafeVLM / VLGuard: VLM ✓, initial alignment only ✗, continual FT ✗
- **Our work**: gradient selection ✓, VLM ✓, continual FT ✓

---

### Slide 8 — Experimental Setup (0.5 min)
**Title**: "Our Setup"

- **Model**: Qwen2-VL-2B-Instruct (2B params, LoRA fine-tuning, Colab T4)
- **4-task sequence**: LLaVA-150K → MathVista → VQA-RAD/SLAKE → DocVQA
- **Safety benchmarks**: MM-SafetyBench, FigStep, JailBreakV-28K, AdvBench
- **Judge**: Llama-Guard-3-8B
- **Comparison**: 10 baselines including Bach et al.'s text-only baselines + VLGuard mixing

---

### Slide 9 — Expected Results & Hypotheses (0.5 min)
**Title**: "What We Expect to Find"

Three hypotheses, each falsifiable:
1. Moderate-Gi selection reduces multimodal ASR by ≥2× compared to full fine-tuning
2. Joint attribution ($G_i^{(J)}$) outperforms language-only ($G_i^{(L)}$) for multimodal safety
3. VLM safety basin (measured by VISAGE on trainable params) shows same step-function collapse geometry as text LLMs

---

### Slide 10 — Timeline & Next Steps (0.5 min)
**Title**: "Timeline"

| Phase | Milestone | Compute | When |
|:---|:---|:---|:---|
| Phase 1 | 1-task "Cheap Gate" (LLaVA-150K only) | Colab T4 | Now → 2 weeks |
| Phase 2 | Full 4-task sequence | Campus cluster | After clearance |
| Phase 3 | Full multimodal attack evaluation | Cluster | Month 2 |
| Write-up | Paper draft | — | Month 3 |

---

## PART 7: DOCUMENT INDEX (Where Everything Lives)

| What | File | Status |
|:---|:---|:---|
| Original Bach et al. notes | `Continual_Safety_Alignment.md` | ✅ Done |
| Full mathematical formulation + verified numbers | `docs/gradient_strategy_dossier.md` | ✅ Done |
| Python pseudocode + open questions + limitations | `docs/reproducibility_blueprint.md` | ✅ Done |
| 20+ paper SOTA survey + master comparison table | `docs/sota_landscape_survey.md` | ✅ Done |
| Anti-hallucination research skill | `.agents/skills/vlm-gradient-safety/SKILL.md` | ✅ Done |
| This document (procedure mapping + presentation) | `docs/master_research_formulation.md` | ✅ This file |
| Study & presentation playbook | `STUDY_AND_PRESENTATION_PLAYBOOK.md` | ✅ Done |
| Advisor alignment audit | `ACADEMIC_ALIGNMENT_AND_TRACEABILITY_REPORT.md` | ✅ Done |
| Full research spec | `RESEARCH_METHODOLOGY_AND_VLM_SPEC.md` | ✅ Done |
| Implementation (gradient selector) | `src/selection/gradient_selector.py` | ✅ Done |
| Implementation (trainer) | `src/training/trainer.py` | ✅ Done |
| Implementation (safety judge + vLLM eval) | `src/eval/` | ✅ Done |
| Colab notebook | `notebooks/continual_safety_vlm.ipynb` | ✅ Done |
