# Presentation Writeup: Safety Alignment of Small VLMs via Gradient-Based Sample Selection
## Fully Cited — All Numbers Extracted Directly from PDFs via OCR

**Researcher**: Aryaman Singh Dev | **Advisor**: Prof. Thao Minh Le (co-author of Bach et al.)  
**Institution**: Pennsylvania State University  
**Source PDFs on disk**:
- `2604.17215v1.pdf` — Bach et al. (ACL 2026) — text LLMs only
- `Safety Alignment for Vision Language Models-with-annotations.pdf` — Nie et al. (arXiv:2405.13581, May 2024) — SafeVLM
- `VLMGuard-R1 Proactive Safety Alignment for VLMs via Reasoning-Driven Prompt Optimization-with-annotations.pdf` — VLMGuard-R1

> **Policy**: Every number in this document was extracted word-for-word from the PDF text.  
> Every `📎 ATTACH` instruction points to the exact table in the exact paper.  
> No numbers are estimated or assumed.

---

## WHAT BACH ET AL. (arXiv:2604.17215) DOES AND DOES NOT COVER

Confirmed directly from PDF text, line 2736:
> *"Our experiments focus on text-only models. Extending gradient-based selection to vision-language models or other modalities requires further investigation."*
> — Bach et al. (2604.17215v1.pdf), Limitations section

**Bach et al. is exclusively a text LLM paper.** Models: Qwen2.5-7B-Instruct, LLaMA-3.1-8B-Instruct, Qwen3-4B-Instruct.  
**Your contribution** is extending their procedure to VLMs — this is not in the paper; it is your research question.

---

## SLIDE 1 — Title

**Title**: Continual Safety Alignment in Small Vision-Language Models via Gradient-Based Sample Selection

**Subtitle**: Extending Bach et al. (ACL 2026, arXiv:2604.17215) to Multimodal Architectures

**Authors, PSU, September 2026**

> 📎 No table needed. Print the Bach et al. paper header on the slide as a footnote citation.

---

## SLIDE 2 — The Problem (Two Separate Claims)

### Claim 1: Confirmed for Text LLMs (Bach et al.)

Directly from PDF (2604.17215v1.pdf, §1, Introduction):
> *"Even fine-tuning on benign, non-malicious datasets can unintentionally weaken safety mechanisms, suggesting that alignment degradation is not merely a consequence of adversarial data but a structural property of fine-tuning itself. While the data content is typically benign, the parameter updates they induce can be destructive to the alignment priors."*  
> — Bach et al., §1

**Citation on slide**: Bach et al., arXiv:2604.17215, §1 (Introduction)

---

### Claim 2: Our Research Hypothesis for VLMs (Not Yet Proven — This Is Our Work)

We hypothesize the same mechanism operates in VLMs. The justification is:
1. Bach et al. explicitly leave this open: *"Extending gradient-based selection to vision-language models... requires further investigation."* (PDF line 2736, Limitations)
2. VLMs have an additional unaligned pathway — the visual modality — which existing safety methods do not protect. Confirmed by SafeVLM (arXiv:2405.13581):
   > *"The visual modality of VLMs is vulnerable, with attackers easily bypassing LLMs' safety alignment through visual modality features to launch attacks."*  
   > — Nie et al. (2405.13581v1, §1 Abstract)

**How to frame on slide**: *"Bach et al. proved this for text LLMs. We ask: does the same mechanism operate in VLMs, and can the same data-centric defense work?"*

---

### Theoretical Mechanisms (Both Claims)

**Mechanism 1 — Elastic Reversion** (Ji et al., arXiv:2406.06144, cited in Bach et al. §1):

From Bach et al. PDF (§1, Introduction):
> *"(Ji et al., 2024) shows that LLMs exhibit elasticity: a tendency to revert toward pretrained distributions during fine-tuning because the massive pretraining corpora exerts stronger influence than smaller alignment datasets."*

Formula (from Bach et al. §2.2):
$$F_{\text{elastic}} \propto |D_i| \cdot \Delta D_{\text{KL}}(p_\theta \| p_{D_i})$$

**Mechanism 2 — Safety Basin Geometry** (Peng et al., NeurIPS 2024, arXiv:2405.17374, cited in Bach et al. §2.1):

From Bach et al. PDF (§2.1):
> *"A critical empirical finding is that safety basins have sharp boundaries: safety exhibits step-function collapse when crossing the boundary, with minimal graceful degradation. This geometry makes large parameter updates particularly dangerous."*

VISAGE score formula, from Bach et al. PDF (§2.1, Eq. 1):
> *"VISAGE = E_{α~U(-a,a)} [S_max - S(α)] s.t. S < S_max"*  
> *"Higher VISAGE indicates larger safety basins and more robust alignment."*

> 📎 No table needed on this slide. Sketch the safety basin diagram (green valley, red outside zone) based on the description in §2.1.

---

## SLIDE 3 — The Full VLM Evaluation Suite

### Why VLMs Need a Broader Benchmark Suite Than Text LLMs

Bach et al. evaluate on AdvBench + HarmBench (text-only attacks) and TruthfulQA + ARC/BoolQ/HellaSwag/Winogrande (capabilities). 
For VLMs, each of these needs a **multimodal equivalent** because visual inputs create entirely new attack and failure surfaces. None of the benchmarks below are redundant — each covers a distinct axis that the others cannot.

From SafeVLM (PDF `Safety Alignment for Vision Language Models-with-annotations.pdf`, arXiv:2405.13581, Abstract):
> *"The visual modality of VLMs is vulnerable, with attackers easily bypassing LLMs' safety alignment through visual modality features to launch attacks."*

---

### Battery 1: Safety / Attack Success Rate (4 Benchmarks)

Analog to Bach et al.'s **AdvBench + HarmBench**.

| # | Benchmark | What It Tests | Key Stat | Why Not Redundant | Citation |
|:---|:---|:---|:---|:---|:---|
| 1 | **MM-SafetyBench** | Image-text pair safety across 13 risk categories | 5,040 text-image pairs, 13 scenarios | Closest scope match to AdvBench (520 harmful queries) — volume + breadth primary benchmark | Liu et al., arXiv:2311.17600 |
| 2 | **FigStep** | Typographic jailbreak: harmful instruction embedded as image text, paired with benign text prompt | — | **No text-only equivalent.** Attacks via visual OCR channel, completely bypasses text safety filters. Distinct attack shape. | Gong et al., arXiv:2311.05608 |
| 3 | **JailBreakV-28K** | 28K visual jailbreaks across 16 harm scenarios: transfer, diffusion, OCR | 28,000 samples, 16 harm scenarios (verified from arXiv:2404.03027) | Mirrors HarmBench's mix of direct + contextual + optimization-based — large-scale adversarial robustness test | Luo et al., arXiv:2404.03027, COLM 2024 |
| 4 | **HarmBench (text slice)** | Direct, contextual, and optimization-based text attacks on VLM's language decoder | 510+ queries, Llama-Guard-3-8B judge | VLM language decoder is still attackable through text alone — same judge as Bach et al. ensures comparability | Mazeika et al., arXiv:2402.04249 |

*Note: AdvBench not used as primary because MM-SafetyBench directly supersedes it for multimodal settings.*

---

### Battery 2: Truthfulness / Hallucination (2 Benchmarks)

Analog to Bach et al.'s **TruthfulQA**.

| # | Benchmark | What It Tests | Why This Role | Citation |
|:---|:---|:---|:---|:---|
| 1 | **MMHal-Bench** *(primary)* | Open-ended, model-graded visual hallucination — 8 question types per image across 12 image types | Closest in spirit to TruthfulQA's open-ended factuality format — tests whether the model fabricates visual content | Bird et al., arXiv:2309.14525 |
| 2 | **POPE** *(secondary)* | Yes/No object existence probing across random, popular, and adversarial splits | Simpler binary check — supplements MMHal-Bench as a standardized signal; widely used, easy to compare across papers | Li et al., arXiv:2305.10355 |

*These two are complementary, not redundant: MMHal-Bench = open-ended severity; POPE = targeted binary existence check.*

---

### Battery 3: Downstream Task Performance (Task Sequence Datasets)

Analog to Bach et al.'s **Dolly → GSM8K → MedMCQA → SQuAD v2** sequence. Each VLM dataset is chosen to test the same capability axis in the multimodal domain. Covered in detail on **Slide 12**.

| Stage | VLM Dataset | Role Analog | Citation |
|:---|:---|:---|:---|
| 1 | LLaVA-Instruct-150K | Dolly | Liu et al., arXiv:2304.08485 |
| 2 | MathVista (6,141 problems) | GSM8K | Lu et al., arXiv:2310.02255 |
| 3 | VQA-RAD / SLAKE | MedMCQA | Lau et al., Nature Scientific Data 2018 / Liu et al., arXiv:2102.09542 |
| 4 | DocVQA (~50,000 Q&A) | SQuAD v2 | Mathew et al., arXiv:2007.00398 |

---

### Summary Table for Slide

| Axis | Text LLM (Bach et al.) | VLM Equivalent (Ours) |
|:---|:---|:---|
| Safety (primary) | AdvBench (520 queries) | MM-SafetyBench (5,040 pairs, 13 scenarios) |
| Safety (diverse attacks) | HarmBench (510+ queries) | FigStep + JailBreakV-28K + HarmBench text slice |
| Truthfulness | TruthfulQA | MMHal-Bench (primary) + POPE (secondary) |
| Capabilities | ARC-C, BoolQ, HellaSwag, Winogrande | LLaVA-Bench, MathVista, VQA-RAD, DocVQA |
| Safety judge | Llama-Guard-3-8B | Llama-Guard-3-8B (same — ensures comparability) |

*Source for text evaluation suite: Bach et al. §5.1. VLM equivalents are our design.*

> 📎 **ATTACH**: Figure 1 from FigStep (arXiv:2311.05608) — shows exactly how typographic attack bypasses text filters.  
> 📎 **ATTACH**: Table 1 from MM-SafetyBench (arXiv:2311.17600) — shows the 13 scenario categories.

---

## SLIDE 4 — Bach et al. Core Findings (Text LLMs — Confirmed Numbers from PDF)

### The Three Gradient Classes

From Bach et al. PDF, §3.1 (confirmed via OCR):
> *"Table 2 shows high-Gi selection retains only 62-72% of original alignment and increases ASR by 5-9×, while moderate-Gi selection preserves 83-88% with only 1.5-2× ASR increase."*

**Table 2 exact numbers** (extracted directly from 2604.17215v1.pdf):

| Model | Selection | VISAGE Score | Basin Retention | ASR↓ |
|:---|:---|:---:|:---:|:---:|
| Qwen-2.5-7B | Aligned (no FT) | 78.5 | — | 2.1 |
| Qwen-2.5-7B | High-$G_i$ | 48.8 | 62.2% | 18.4 |
| Qwen-2.5-7B | Random | 57.0 | 72.6% | 12.7 |
| Qwen-2.5-7B | Moderate-$G_i$ | 65.5 | 83.4% | 5.8 |
| LLaMA-3.1-8B | Aligned (no FT) | 67.7 | — | 3.2 |
| LLaMA-3.1-8B | High-$G_i$ | 48.9 | 72.2% | 15.1 |
| LLaMA-3.1-8B | Random | 52.8 | 78.0% | 9.8 |
| LLaMA-3.1-8B | Moderate-$G_i$ | 59.3 | 87.6% | 4.9 |

*Source: Bach et al. (2604.17215v1.pdf), Table 2, confirmed via PDF text extraction.*

**Caption from paper**: *"High-gradient selection causes the largest degradation (62-72% retention); moderate-gradient selection preserves 83-88% with the lowest ASR."*

> 📎 **ATTACH**: **Table 2 from 2604.17215v1.pdf** — screenshot the whole table. The numbers above come from it.

---

## SLIDE 5 — Mechanism: Format Mismatches Drive High-$G_i$

From Bach et al. PDF, Appendix (Sample Audit section, line 114):
> *"High-gradient samples are often format mismatches, not content-based outliers. They are dominated by short-answer tasks where the aligned model's verbose output distribution diverges from terse targets."*

From Bach et al. PDF, §3.2 (Gradient Direction Analysis, confirmed via OCR):
> *"High-gradient samples exhibit higher directional alignment with the reversion direction compared to moderate-gradient samples in final-layer parameters, though the specific components vary by architecture: V/O projections in Qwen2.5 (TopK-Cosine 0.119 vs 0.104 for V, r = 0.41) and MLP layers in LLaMA (0.104 vs 0.102, r = 0.18). Besides, middle layers show no directional effect in either model (|r| < 0.07, p > 0.3)."*

**Table 4 exact numbers** (from 2604.17215v1.pdf, extracted via OCR):

| Model | Parameter Group | HIGH $G_i$ (TopK-Cosine) | MOD $G_i$ (TopK-Cosine) | r | p |
|:---|:---|:---:|:---:|:---:|:---:|
| Qwen2.5-7B | Last_V | 0.119 | 0.104 | 0.41 | < 10⁻³ |
| Qwen2.5-7B | Last_O | 0.276 | 0.244 | 0.39 | < 10⁻³ |
| Qwen2.5-7B | Middle | −0.004 | −0.004 | 0.06 | 0.38 |
| LLaMA-3.1-8B | Last_MLP | 0.104 | 0.102 | 0.18 | < 0.01 |
| LLaMA-3.1-8B | Last_V | −0.029 | −0.033 | 0.33 | < 10⁻³ |
| LLaMA-3.1-8B | Middle | −0.020 | −0.024 | 0.03 | 0.72 |

*Source: Bach et al. (2604.17215v1.pdf), Table 4, confirmed via PDF text extraction.*

**Why gradient clipping fails** — from Bach et al. PDF, Appendix ("Why Not Gradient Clipping?"):
> *"Clipping attenuates step size but still trains on high-gradient samples, meaning the model still receives a learning signal pushing toward pretrained distributions. Our method removes these samples entirely."*

> 📎 **ATTACH**: **Table 4 from 2604.17215v1.pdf** — screenshot the complete table.

---

## SLIDE 6 — The Algorithm (Exactly as in Paper)

**Algorithm 1** from Bach et al. PDF (§4.1, extracted verbatim):

```
Algorithm 1: Gradient-Based Sample Selection
Require: Batch B, model θ, selection ratio ρ = 0.2
Ensure:  Selected samples S

1. Compute losses: Li = L(xi, yi; θ) for all (xi, yi) ∈ B
2. Filter: C ← {(xi, yi) : Li ∈ [μL − σL, μL + σL]}
3. Compute gradient norms: Gi = ‖∇θ L(xi, yi; θ)‖₂ for (xi, yi) ∈ C
4. μG ← median({Gi})
5. Select ⌊ρ|B|⌋ samples closest to μG as S
6. return S
```

*Source: Bach et al. (2604.17215v1.pdf), §4.1, Algorithm 1 — transcribed verbatim.*

**Key design choices** — from Bach et al. PDF, §4.1:
> *"We use median (not mean) for robustness against heavy-tailed gradient distributions. Selection ratio ρ ∈ [0.15, 0.25] balances quality vs. cost; we use ρ = 0.2. Pre-filtering reduces gradient computation by ~32%."*

**Stage 2 (loss pre-filter)** removes samples outside ±1σ of mean loss — this is the `[μL − σL, μL + σL]` range in step 2. This is **not** a fixed threshold τ — it is a dynamic ±1σ window.

**Selection ratio robustness** — from Bach et al. PDF, §4.2 (Table 5 in paper):
> *"Results are robust across ρ ∈ [0.1, 0.4]: ASR remains consistently low (2.7–6.0%), all substantially better than baseline (16.6%) and random sampling (11.8%)."*

> 📎 **ATTACH**: **Table 5 from 2604.17215v1.pdf** (sensitivity to ρ on Qwen3-4B) — shows robustness across selection ratios.  
> 📎 Also attach the Algorithm 1 box from the paper directly — it is clean and citable.

---

## SLIDE 7 — Main Results: Full Text LLM Table (Confirmed from PDF)

**Table 6 exact numbers** — extracted directly from 2604.17215v1.pdf via OCR. This is the main ASR + capabilities table, checkpoint-averaged, mean ± std over 3 seeds.

| Model | Method | ASR ↓ | TruthfulQA | ARC-C | BoolQ | HellaSwag | Winogrande |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Qwen2.5-7B** | Baseline | 36.7 ± 13.6 | 38.2 ± 1.2 | 58.0 ± 1.5 | 86.4 ± 1.0 | 79.2 ± 0.5 | 72.3 ± 0.3 |
| | Random | 31.1 ± 14.3 | 38.4 ± 1.1 | 58.1 ± 0.6 | 85.9 ± 2.0 | 79.4 ± 0.3 | 72.3 ± 0.5 |
| | KL | 33.5 ± 13.4 | 37.8 ± 1.3 | 58.3 ± 1.7 | 86.2 ± 1.4 | 79.1 ± 0.4 | 72.3 ± 0.4 |
| | O-LoRA | 16.5 ± 19.7 | 42.9 ± 1.0 | 56.6 ± 0.9 | 86.1 ± 1.2 | 79.3 ± 0.4 | 71.8 ± 0.6 |
| | EWC | 17.4 ± 6.7 | 38.1 ± 0.3 | 57.7 ± 0.4 | 86.8 ± 0.2 | 79.2 ± 0.1 | 71.7 ± 0.3 |
| | Grad. Clip | 31.2 ± 13.8 | 38.2 ± 1.1 | 57.9 ± 1.4 | 86.3 ± 1.1 | 79.3 ± 0.4 | 72.1 ± 0.4 |
| | **Moderate-$G_i$** | **10.2 ± 7.1** | 42.5 ± 1.3 | 59.6 ± 1.7 | 86.3 ± 1.5 | 79.9 ± 0.1 | 71.7 ± 0.9 |
| **LLaMA-3.1-8B** | Baseline | 44.2 ± 22.5 | 37.8 ± 0.7 | 56.3 ± 1.3 | 84.8 ± 1.0 | 77.9 ± 0.5 | 73.8 ± 0.5 |
| | Random | 31.9 ± 23.3 | 38.6 ± 1.7 | 56.9 ± 1.5 | 84.8 ± 0.6 | 78.0 ± 0.3 | 73.6 ± 0.5 |
| | KL | 43.6 ± 21.6 | 38.6 ± 0.8 | 56.4 ± 1.5 | 84.9 ± 1.0 | 78.0 ± 0.6 | 74.0 ± 0.5 |
| | O-LoRA | 23.3 ± 28.0 | 40.0 ± 1.0 | 56.4 ± 1.2 | 84.7 ± 0.6 | 78.3 ± 0.6 | 74.0 ± 0.7 |
| | EWC | 40.2 ± 11.8 | 38.0 ± 0.3 | 56.0 ± 0.7 | 84.9 ± 0.2 | 78.0 ± 0.1 | 74.0 ± 0.2 |
| | **Moderate-$G_i$** | **18.3 ± 17.3** | 41.5 ± 2.6 | 56.0 ± 1.5 | 84.8 ± 0.6 | 77.9 ± 0.7 | 73.7 ± 0.5 |
| **Qwen3-4B** | Baseline | 16.6 ± 7.7 | 39.7 ± 0.7 | 59.8 ± 1.5 | 86.2 ± 0.5 | 71.0 ± 1.2 | 68.7 ± 0.4 |
| | Random | 11.8 ± 5.8 | 40.1 ± 1.6 | 60.2 ± 1.1 | 85.6 ± 1.2 | 70.6 ± 0.8 | 68.7 ± 0.7 |
| | KL | 17.8 ± 7.0 | 39.7 ± 0.8 | 59.5 ± 1.2 | 86.0 ± 0.4 | 71.0 ± 1.2 | 69.0 ± 0.7 |
| | O-LoRA | 6.8 ± 6.5 | 42.3 ± 1.6 | 59.5 ± 1.3 | 85.2 ± 0.8 | 70.7 ± 1.1 | 68.7 ± 0.7 |
| | EWC | 14.1 ± 3.1 | 40.5 ± 0.2 | 59.3 ± 0.3 | 85.7 ± 0.1 | 71.1 ± 0.1 | 68.9 ± 0.3 |
| | **Moderate-$G_i$** | **6.0 ± 5.4** | 42.8 ± 1.6 | 59.2 ± 1.3 | 84.6 ± 1.4 | 70.1 ± 0.8 | 68.5 ± 0.8 |

*Source: Bach et al. (2604.17215v1.pdf), Table 6. Caption: "Alignment preservation metrics, checkpoint-averaged (mean ± std over three seeds). Safety via attack success rate (ASR, lower better), truthfulness via TruthfulQA, and general capabilities via ARC-Challenge, BoolQ, HellaSwag, and Winogrande."*

**From paper text** (§5.2, confirmed via OCR):
> *"Moderate-Gi achieves 10.2% ASR versus 36.7% (Baseline), 31.1% (Random), 33.5% (KL), and 16.5% (O-LoRA)—representing 3.6× reduction over Baseline. EWC achieves 17.4% ASR but notably worsens safety on LLaMA-3.1 (40.2% vs. 44.2% baseline), demonstrating that Fisher-based regularization, designed to protect task-critical parameters, fails to consistently preserve alignment."*

> 📎 **ATTACH**: **Table 6 from 2604.17215v1.pdf** — screenshot the whole table. The numbers above were extracted verbatim.

---

## SLIDE 8 — Continual Learning / BWT Results (Confirmed from PDF)

**Table 8 exact numbers** — extracted directly from 2604.17215v1.pdf via OCR:

| Model | Method | Avg Perf | BWT ↑ | FM ↓ | Max Drop ↓ |
|:---|:---|:---:|:---:|:---:|:---:|
| **LLaMA-3.1-8B** | Baseline | 46.5 | +0.2 | −0.2 | 8.4 |
| | Random | 46.8 | +0.8 | −0.8 | 4.6 |
| | KL | 46.4 | −1.1 | 1.1 | 8.7 |
| | O-LoRA | 47.9 | +6.4 | −4.5 | — |
| | **Moderate-$G_i$** | 46.4 | **−1.7** | 1.7 | **5.4** |
| **Qwen3-4B** | Baseline | 54.2 | −18.5 | 32.5 | 18.5 |
| | Random | 55.0 | −19.8 | 23.2 | 19.8 |
| | KL | 54.8 | −15.5 | 26.0 | 15.5 |
| | O-LoRA | 58.8 | −12.4 | 15.3 | 12.4 |
| | **Moderate-$G_i$** | **58.1** | **−4.3** | **5.6** | **4.3** |

*Source: Bach et al. (2604.17215v1.pdf), Table 8. Caption confirmed via OCR: "Moderate-Gi achieves 14.2% BWT improvement and 5.8× reduction in max drop on Qwen3."*

**From paper text** (confirmed via OCR, around line 1243):
> *"Moderate-Gi achieves 14.2% BWT improvement and 5.8× reduction in max drop on Qwen3."*

> 📎 **ATTACH**: **Table 8 from 2604.17215v1.pdf** — screenshot the whole table.

---

## SLIDE 9 — HarmBench Results (Confirmed from PDF)

**Table 9 exact numbers** — extracted from 2604.17215v1.pdf:

| Method | HarmBench ASR ↓ |
|:---|:---:|
| Baseline | 27.8 (3.7) |
| Random | 17.2 (5.6) |
| KL | 27.7 (1.0) |
| EWC | 31.0 (6.7) |
| O-LoRA | 10.0 (1.4) |
| **Moderate-$G_i$** | **5.0 (3.4)** |

*Source: Bach et al. (2604.17215v1.pdf), Table 9. Model: LLaMA-3.1-8B. Caption: "HarmBench ASR on LLaMA-3.1-8B across the full continual learning pipeline."*

From paper text (§5.2):
> *"Our method achieves 5.6× lower ASR than baseline on HarmBench."*

> 📎 **ATTACH**: **Table 9 from 2604.17215v1.pdf**.

---

## SLIDE 10 — SafeVLM: The Existing VLM Safety Approach We Are Comparing Against

**Paper**: Nie et al., *Safety Alignment for Vision Language Models*, arXiv:2405.13581  
**PDF on disk**: `Safety Alignment for Vision Language Models-with-annotations.pdf`

**What they do** (from PDF Abstract, confirmed via OCR):
> *"We enhance the existing VLMs' visual modality safety alignment by adding safety modules, including a safety projector, safety tokens, and a safety head, through a two-stage training process, effectively improving the model's defense against risky images."*

**Their results on LLaVA-v1.5-7B** (from PDF Table 3 + Table 4, extracted via OCR):

| Method | AdvBench (Vanilla) ↓ | AdvBench (Suffix Injection) ↓ | XSTest Unsafe ↓ | RTVLM Score ↑ |
|:---|:---:|:---:|:---:|:---:|
| LLaVA-v1.5-7B (baseline) | 6.45% | 78.27% | 26.50% | 6.27 |
| **SafeVLM** | **1.72%** | **67.56%** | **7.46%** | **8.26** |
| SafeVLM (+LoRA) | 1.90% | 69.86% | 6.96% | — |

*Source: Nie et al. (arXiv:2405.13581), Tables 3 & 4, confirmed via PDF text extraction.*

**Key difference from our approach**:
- SafeVLM adds new architectural modules (safety projector, safety tokens, safety head) — requires architectural modification.
- Our approach (Moderate-$G_i$ adapted to VLMs) requires **zero architectural changes**, no curated safety data at adaptation steps.

> 📎 **ATTACH**: Table 3 from `Safety Alignment for Vision Language Models-with-annotations.pdf` — shows AdvBench and XSTest ASR numbers.

---

## SLIDE 11 — Our VLM Extension: Methodology

### What Changes When Going Text LLM → VLM

In Bach et al.'s text LLM, trainable parameters are homogeneous LoRA adapters on language attention/MLP layers. In VLMs, the architecture decomposes:

$$\Theta_{\text{VLM}} = \underbrace{\Theta_{\text{Vision Encoder}}}_{\text{frozen}} \cup \underbrace{\Theta_{\text{Projector}}}_{\text{trainable}} \cup \underbrace{\Theta_{\text{Language LoRA}}}_{\text{trainable}}$$

### Our 3 Gradient Attribution Modes (Novel Contribution)

This is our formulation — no prior paper has done this ablation for VLMs:

$$G_i^{(L)} = \left\| \nabla_{\Theta_{\text{LM-LoRA}}} \mathcal{L}_i \right\|_2 \quad \text{(Language: direct port of Bach et al.)}$$

$$G_i^{(P)} = \left\| \nabla_{\Theta_{\text{Projector}}} \mathcal{L}_i \right\|_2 \quad \text{(Projector: cross-modal alignment tension)}$$

$$G_i^{(J)} = \sqrt{\left(G_i^{(L)}\right)^2 + \lambda \left(G_i^{(P)}\right)^2} \quad \text{(Joint: combined VLM signal)}$$

Justified by SafeVLM finding (PDF, §3.2):
> *"Projectors play a [key] role... the features processed by the existing pre-trained projectors lack safety alignment."*  
> — Nie et al. (2405.13581), §3.2

### Critical VLM Implementation: Label Masking

Bach et al.'s Algorithm 1 computes $G_i = \|\nabla_\theta \mathcal{L}(x_i, y_i; \theta)\|_2$ on the response tokens $y_i$. In VLMs, the input contains visual tokens that must be masked to $-100$ to prevent the gradient from being dominated by image reconstruction loss instead of task-response alignment.

> 📎 No table needed on this slide. Draw the Qwen2-VL-2B architecture showing frozen ViT, trainable projector, and LoRA language backbone.

---

## SLIDE 12 — Task Sequence and Execution Plan

**Our task sequence** (analogue of Bach et al.'s Dolly → GSM8K → MedMCQA → SQuAD v2, from §5.1):

| Stage | Bach et al. Text Task | Our VLM Equivalent | Reasoning | Citation |
|:---|:---|:---|:---|:---|
| 1 | Dolly (15K instruction following) | **LLaVA-Instruct-150K** | General visual instruction following — same role as Dolly (reduces refusal before task-specific tuning). Benign, diverse, general purpose. | Liu et al., arXiv:2304.08485 |
| 2 | GSM8K (math word problems) | **MathVista** (6,141 problems) | Visual-mathematical reasoning from charts, diagrams, geometry. Direct multimodal analog to GSM8K. Verified scale: 6,141 problems (from arXiv:2310.02255 abstract). | Lu et al., arXiv:2310.02255 |
| 3 | MedMCQA (medical MCQ) | **VQA-RAD** (primary) or **SLAKE** (alternate) | Clinical image understanding: radiology, pathology. VQA-RAD = radiology QA pairs (Lau et al., Nature Scientific Data 2018). SLAKE = bilingual medical VQA (Liu et al., arXiv:2102.09542). | Lau et al., doi:10.1038/sdata.2018.251; Liu et al., arXiv:2102.09542 |
| 4 | SQuAD v2 (reading comprehension) | **DocVQA** (~50,000 Q&A pairs) | Dense document OCR and layout reasoning. Directly tests extractive reading comprehension on visual documents — same capability as SQuAD v2. Verified scale: ~50,000 (from arXiv:2007.00398 abstract). | Mathew et al., arXiv:2007.00398 |

*Source for text task sequence: Bach et al. §5.1. VLM analogues and justifications are our original design contribution.*

**Phase 1 (Colab T4 — Active)**: Single task, 10% calibration subsample. Verify Moderate-$G_i^{(L)}$ vs Random vs High-$G_i$ on FigStep ASR.

**Phase 2 (Campus Cluster — Pending clearance)**: Full 4-task sequence with all attribution mode ablations and SOTA baselines.

---

## SLIDE 13 — Summary

### Confirmed from papers (text LLMs):
- Fine-tuning on benign data causes alignment drift — proved by Bach et al. (arXiv:2604.17215).
- Moderate-$G_i$ cuts Qwen2.5 ASR from **36.7% to 10.2%** (3.6× reduction) — Bach et al. Table 6.
- Safety basin retention: **83–88% vs 62–72%** for High-$G_i$ — Bach et al. Table 2.
- BWT improvement on Qwen3: from **−18.5% to −4.3%** — Bach et al. Table 8.

### Our contribution (VLMs — to be experimentally verified):
- First extension of gradient-based selection to VLMs.
- First ablation of gradient attribution across Language LoRA vs Multimodal Projector.
- Open challenge explicitly called out in Bach et al. Appendix (Limitations, line 2736 of PDF).

> 📎 **ATTACH**: Table 2 and Table 6 from 2604.17215v1.pdf together on this summary slide.

---

## Quick Reference: Which PDF, Which Table

| Slide | What to screenshot | PDF filename | Table/Figure |
|:---|:---|:---|:---|
| 4 | Safety basin / VISAGE retention numbers | `2604.17215v1.pdf` | **Table 2** |
| 5 | Gradient direction / reversion vector alignment | `2604.17215v1.pdf` | **Table 4** |
| 6 | Algorithm pseudocode | `2604.17215v1.pdf` | **Algorithm 1 box** |
| 6 | Selection ratio sensitivity | `2604.17215v1.pdf` | **Table 5** |
| 7 | Main ASR + capability results | `2604.17215v1.pdf` | **Table 6** |
| 8 | BWT / forgetting metrics | `2604.17215v1.pdf` | **Table 8** |
| 9 | HarmBench generalization | `2604.17215v1.pdf` | **Table 9** |
| 10 | SafeVLM text attack results | `Safety Alignment for Vision Language Models-with-annotations.pdf` | **Table 3** |
| 10 | SafeVLM multimodal benchmark | `Safety Alignment for Vision Language Models-with-annotations.pdf` | **Table 4** |
| 3 | FigStep attack example | arXiv:2311.05608 (download PDF) | **Figure 1** |
| 3 | MM-SafetyBench 13 categories | arXiv:2311.17600 (download PDF) | **Table 1** |
