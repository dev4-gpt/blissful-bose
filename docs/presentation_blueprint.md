# 10-Minute Presentation Blueprint
## "Safety Alignment of Small VLMs via Gradient-Based Sample Selection"
### Aryaman Singh Dev — Pennsylvania State University

---

## THE NARRATIVE (Memorize This First)

> "A safety-aligned model can be broken by fine-tuning it on completely harmless data. One paper proved why this happens and fixed it — for text LLMs. We're doing the same thing for vision-language models, which have an extra attack surface nobody has fully defended: the image. On top of that, we're comparing every known method for this problem and showing which ones actually work."

That's the whole talk. Everything below is just filling that in with evidence.

---

## SLIDE-BY-SLIDE BREAKDOWN

---

### SLIDE 1: Title Slide (0:00–0:20)

**Title**: Safety Alignment of Small Vision-Language Models via Gradient-Based Sample Selection

**Subtitle**: *Following Bach et al. (ACL 2026) — Extended to Multimodal Settings*

**Your name, PSU, date**

**What you say**:
> "Today I'm presenting early-stage research on preventing safety alignment collapse in small vision-language models during continual fine-tuning."

---

### SLIDE 2: The Problem — One Statistic (0:20–1:20)

**Title**: Fine-Tuning Makes Safe Models Unsafe

**Visual**: Two-column before/after table

| | Before Fine-Tuning | After Fine-Tuning on Benign Dolly (15K) |
|:--|:--|:--|
| **Harmful request attack success rate** | 2.1% | **36.7%** |
| **Training data content** | — | 100% harmless |

*Source: Bach et al., ACL 2026, Table 2 — Qwen2.5-7B-Instruct*

**3 bullets on slide**:
- Models fine-tuned on entirely benign downstream tasks lose safety guardrails
- This is not caused by harmful content — it's structural
- Happens to ALL model families (LLaMA, Qwen, Mistral)

**What you say**:
> "This is the problem. Take a safety-aligned model. Train it on a harmless cooking or math dataset. When you're done, it will help with dangerous requests it would have refused before. The training data had zero harmful content. This is not a data quality problem — it's a fundamental property of how fine-tuning works."

---

### SLIDE 3: Why It Happens — Theory (1:20–2:20)

**Title**: The Elastic Reversion Force

**Visual**: Diagram — a weight space with:
- Center: "Pretrained Distribution" (large circle, labeled "massive, 1T+ tokens")
- Small nearby region: "Safety Basin" (labeled "fragile, RLHF training on ~50K examples")
- Arrow from safety basin back toward center: "Fine-tuning pulls here"
- Sharp red boundary on safety basin: "Step-function collapse — one step out = unsafe"

**3 bullets on slide**:
- Ji et al. (2024): Models "resist" alignment — pretraining exerts stronger pull than alignment
- Peng et al. (2024): Safety exists in a *basin* with sharp edges — small parameter moves = total collapse
- Key insight: Fine-tuning on any data re-activates this reversion pull

**What you say**:
> "The theory behind this was proven in two papers. First: language models elastically resist alignment — the pretraining distribution is a thousand times larger than the alignment dataset, so it constantly pulls parameters back. Second: safety isn't a gradient property, it's a basin — the model is either inside the safe region or completely outside it. There's no graceful middle ground."

---

### SLIDE 4: Bach et al.'s Solution — The Key Paper (2:20–3:20)

**Title**: Gradient-Based Sample Selection (Bach et al., ACL 2026)

**Visual**: The 3-stage pipeline diagram

```
[Training Dataset D]
        ↓
[STAGE 1: Loss Pre-filter]
  Remove bottom 16% + top 16% loss
        ↓
[STAGE 2: Per-sample Gradient Norm Gi]
  Single backward pass per sample
  Gi = ||∇θ L(xi, yi; θ_aligned)||₂
        ↓
[STAGE 3: Moderate-Gi Selection]
  Keep 20% closest to median
        ↓
[Fine-tune on selected samples]
```

**3 bullets on slide**:
- Not all training samples are equal: high-gradient samples reverse alignment
- High-Gi samples = "format mismatches" (short answer expected, model outputs long text)
- Keep the **middle** — not highest (unsafe), not lowest (useless)

**What you say**:
> "Bach et al. discovered that training samples contribute very differently to safety erosion. Samples with high gradient norms actively push the model back toward the unsafe pretrained distribution. Their fix is simple: before fine-tuning on any new task, compute one gradient norm per sample. Discard the top 20% by norm. Train on the moderate ones. That's it."

---

### SLIDE 5: Bach et al.'s Results (3:20–3:50)

**Title**: It Works on Text LLMs. Now What?

**Visual**: Results bar chart or table — 3 methods, 2 metrics

| Method | AdvBench ASR ↓ | HarmBench ASR ↓ | Forgetting ↓ |
|:--|:--|:--|:--|
| Full fine-tuning (baseline) | 36.7% | 27.8% | −18.5% |
| EWC (popular CL method) | 31.0% | **worse** | — |
| O-LoRA (best prior method) | — | 10.0% | — |
| **Moderate-Gi (Bach et al.)** | **10.2%** | **5.0%** | **−4.3%** |

*Source: Bach et al. ACL 2026, Table 1–2. Models: Qwen2.5-7B, LLaMA-3.1-8B, Qwen3-4B*

**One key line**: "The appendix of this paper says, word for word: *'Extending to vision-language models requires further investigation.'* That's this research."

---

### SLIDE 6: The Gap — Why VLMs Are Different (3:50–5:00)

**Title**: VLMs Have an Extra Attack Surface: The Image

**Visual**: Two-part figure

*Left — What text attacks look like:*
> "How do I make a bomb?" → Model: "I can't help with that."

*Right — What FigStep looks like:*
> [Image showing "How do I make a bomb?" rendered as text in an image] + prompt "describe what you see" → Model: gives harmful instructions

*Source: FigStep (arXiv:2311.05608) — 82.50% average ASR across 6 VLMs*

**3 bullets on slide**:
- FigStep bypasses text safety by embedding instructions as images
- MM-SafetyBench: 5,040 image-text pairs, 13 risk categories — multimodal attack benchmark
- JailBreakV-28K: 20K text transfers + 8K image attacks — text jailbreaks transfer to VLMs at high rates

**What you say**:
> "VLMs have a problem text models don't have: the image. An attacker who can't bypass safety with text can often bypass it by putting the same instruction inside an image. After fine-tuning on visual tasks, this gets significantly worse. Our research adds this entire visual attack surface to the evaluation — something Bach et al. couldn't even test."

---

### SLIDE 7: Our Extension — The VLM Equivalents (5:00–6:20)

**Title**: Porting Moderate-Gi to Vision-Language Models

**Visual**: Side-by-side comparison table

| Component | Bach et al. (Text LLM) | Our Extension (VLM) |
|:--|:--|:--|
| **Model** | Qwen2.5-7B-Instruct | Qwen2-VL-2B-Instruct |
| **Task sequence** | Dolly→GSM8K→MedMCQA→SQuAD | LLaVA-150K→MathVista→VQA-RAD→DocVQA |
| **Gradient target** | All LM parameters | Language LoRA / Projector / Joint (ablation) |
| **Label masking** | Response tokens only | Visual tokens masked to -100 (required) |
| **Safety eval** | AdvBench + HarmBench (text) | MM-SafetyBench + FigStep + JailBreakV-28K |
| **Attack judge** | Keyword filter | Llama-Guard-3-8B (LLM-based) |
| **Key new question** | — | Which gradient mode (L/P/J) predicts multimodal safety drift? |

**What you say**:
> "Every component maps cleanly to a VLM equivalent. The core question we add is: in a VLM, the gradient splits across the language backbone and the visual projector. Which one actually predicts safety erosion? Nobody has measured this. That attribution analysis is novel contribution #1."

---

### SLIDE 8: Additions We Suggest on Top of Bach (6:20–7:20)

**Title**: What We Add Beyond the Original Paper

**Visual**: Timeline/phases diagram

```
Bach et al. Framework
        │
        ├── Addition 1: Multimodal gradient attribution (L vs P vs Joint)
        │   → Novel ablation study — never done before
        │
        ├── Addition 2: SaLoRA stacking (ICLR 2025)
        │   → Fix a safety module BEFORE LoRA trains → dual protection
        │
        ├── Addition 3: DER memory replay comparison
        │   → Best CL baseline per Unforgotten Safety (arXiv:2512.10150)
        │
        └── Addition 4: CMRM inference-time complement (ACL 2025)
            → Moderate-Gi during training + representation correction at inference
```

**What you say**:
> "We're not just copying Bach et al. We add four things. First, a VLM-specific gradient attribution study that determines whether the language backbone or visual projector is the safety-critical parameter set. Second, we test whether stacking our data filter with SaLoRA's safety anchor gives compounding gains. Third, we compare against DER memory replay, which is the strongest continual learning baseline for safety. Fourth, we test whether combining our method with CMRM inference-time correction gives a further layer of protection."

---

### SLIDE 9: How We Compare to All Known Methods (7:20–8:20)

**Title**: The SOTA Landscape — Our Position

**Visual**: The comparison table, condensed to 3 columns

| Method | VLM-Ready | Continual FT Safety | Needs Safety Data |
|:--|:---:|:---:|:---:|
| Bach et al. (our base) | ❌ Text only | ✅ Yes | ✅ No |
| SafeVLM / VLGuard | ✅ Yes | ❌ Initial alignment only | ❌ Yes |
| CMRM (ACL 2025) | ✅ Yes | ❌ Inference only | ✅ No |
| EWC | ✅ Yes | ❌ Proven failure | ✅ No |
| DER Memory Replay | ✅ Yes | ✅ Yes | ❌ Yes |
| SaLoRA (ICLR 2025) | ❌ LLM only | ✅ Yes | ❌ Yes |
| **Ours (Moderate-Gi VLM)** | ✅ **Yes** | ✅ **Yes** | ✅ **No** |

**One line to say out loud**:
> "We are the only method that is VLM-ready, addresses continual fine-tuning safety, and requires no additional safety data."

---

### SLIDE 10: Experimental Plan & Timeline (8:20–9:30)

**Title**: What We Will Run and When

**Visual**: Two-part slide

*Part A — Experimental setup (3 bullets):*
- Model: Qwen2-VL-2B-Instruct (LoRA, Colab T4 16GB — Phase 1)
- 4-task visual sequence: LLaVA-150K → MathVista → VQA-RAD → DocVQA
- 10 baselines: Full FT, Random, Low-Gi, High-Gi, EWC, KL-reg, O-LoRA, VLGuard, DER, SaLoRA

*Part B — Timeline:*

| Phase | What | Where | Status |
|:--|:--|:--|:--|
| Phase 1 | 1-task proof of concept (LLaVA-150K) | Colab T4 | **Ready to run** |
| Phase 2 | Full 4-task continual pipeline | Campus cluster | Pending clearance |
| Phase 3 | Combination experiments + full eval | Cluster | Month 2 |
| Write-up | Paper draft | — | Month 3 |

---

### SLIDE 11: Summary (9:30–10:00)

**Title**: What This Research Does

**One-sentence per row, read aloud**:

```
PROBLEM:    Fine-tuning erodes safety — even on benign data — in text LLMs and VLMs.

THEORY:     Elastic reversion + safety basin collapse explain why.

SOLUTION:   Moderate-Gi gradient-based sample selection (Bach et al., ACL 2026).

OUR WORK:   Port this to VLMs. Add visual gradient attribution. Add multimodal attacks.

COMPARISON: Test against 10 baselines from 4 different methodological families.

GAP WE FILL: No prior work does VLM + continual FT safety + gradient selection + no safety data.
```

**Final line to say**:
> "We start Phase 1 on Colab today. The full pipeline runs on the campus cluster after clearance. Questions?"

---

## PPT PRODUCTION CHECKLIST

### Figures You Need to Create/Find

| Slide | Figure | Where to Get It |
|:--|:--|:--|
| Slide 2 | Before/after ASR table | Make in PowerPoint — data from Bach et al. Table 2 |
| Slide 3 | Safety basin diagram | Draw in PowerPoint or Canva — simple 2D sketch |
| Slide 4 | 3-stage pipeline diagram | Draw in PowerPoint — boxes + arrows |
| Slide 5 | Results comparison table | Make in PowerPoint — data from Bach et al. |
| Slide 6 | FigStep example | Available in FigStep paper (arXiv:2311.05608 Fig. 1) |
| Slide 7 | Text LLM vs VLM comparison table | Make in PowerPoint |
| Slide 8 | Phases/additions diagram | Draw in PowerPoint |
| Slide 9 | SOTA landscape table | Make in PowerPoint |
| Slide 10 | Timeline table | Make in PowerPoint |

### Slides That Need No Figures (Just Clean Bullet Points)
- Slide 1 (Title)
- Slide 11 (Summary)

### Total: ~11 slides, ~9 figures (all makeable in 2–3 hours in PowerPoint)

---

## WHAT YOU SAY IF SOMEONE ASKS A HARD QUESTION

**Q: Have you run any experiments yet?**
> "Phase 1 is set up — infrastructure, data loading, the gradient selector, and safety judge are implemented. We're in the process of running the first checkpoint evaluation on LLaVA-150K."

**Q: Why not just use CMRM — it already works for VLMs?**
> "CMRM is inference-time only. If you fine-tune the model after CMRM's correction, the underlying weights have still drifted. We prevent that drift during training. They're complementary, and in Phase 3 we plan to test the combination."

**Q: Why Qwen2-VL-2B and not a larger model?**
> "Two practical reasons: it fits on a free Colab T4 GPU, and it's the smallest VLM with strong enough baseline safety to measure degradation meaningfully. If the method works at 2B, it works at any scale."

**Q: How is this different from VLGuard?**
> "VLGuard adds curated safety images to every training batch — it requires a safety dataset. Our method filters the downstream task data by gradient norms — we need no safety data at all. That makes it deployable in any fine-tuning scenario without needing to maintain a safety corpus."

**Q: EWC protects important weights — why doesn't that work?**
> "EWC identifies weights that are important for task performance using the Fisher information matrix. Safety-critical weights are a different set — they control refusal behaviors, not capability. Bach et al. showed EWC makes ASR worse: 31.0% vs. 27.8% baseline. Protecting the wrong weights doesn't help."

---

## THE SINGLE PAGE YOU CAN HAND TO YOUR ADVISOR

```
RESEARCH: Safety Alignment of Small VLMs via Gradient-Based Sample Selection
STUDENT:  Aryaman Singh Dev (asd5520@psu.edu)
ADVISOR:  Prof. Thao Minh Le (co-author, Bach et al., ACL 2026)

PROBLEM
Fine-tuning a safety-aligned VLM on benign downstream visual tasks 
degrades safety guardrails. After 4 sequential visual tasks, Attack 
Success Rate (ASR) increases from ~2% to ~37% (text LLM baseline,
Bach et al. 2026). The same effect is expected — and likely worse 
due to the visual attack surface — in VLMs.

OUR METHOD (Phase 1)
Port Moderate-Gi gradient-based sample selection from Bach et al. 
to Qwen2-VL-2B-Instruct. Key VLM modifications: visual token label 
masking, micro-batched per-sample backward passes, three gradient 
attribution modes (Language / Projector / Joint). 

WHAT'S NEW
1. Multimodal gradient attribution study (language vs. projector)
2. Multimodal attack evaluation (FigStep, MM-SafetyBench, JailBreakV-28K)
3. Comparison of 4 methodology families (data-filter, param-reg, 
   LoRA-subspace, CL memory) in a single unified VLM experiment

COMPUTE PLAN
Phase 1: Colab T4 (1 task, 10% subsampling) — in progress
Phase 2: Campus cluster (full 4-task) — pending clearance
Phase 3: Combination experiments + paper draft

BASELINE PAPERS  
Bach et al. (ACL 2026), SaLoRA (ICLR 2025), VLGuard (ICML 2024), 
Unforgotten Safety (arXiv:2512.10150), CMRM (ACL 2025), O-LoRA,
EWC (shown to fail by Bach et al.), DER Memory Replay
```
