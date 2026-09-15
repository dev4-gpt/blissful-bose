---
name: vlm-gradient-safety
description: >
  Enables rigorous, zero-hallucination analysis of research and code in the domain
  of VLM safety alignment and gradient-based sample selection. Every empirical claim
  MUST cite its source paper and section. No numbers may be invented or extrapolated.
  Use this skill for any task involving reading, writing, or implementing research
  on continual safety alignment, multimodal jailbreaks, or gradient-based data selection.
---

# VLM Safety Alignment & Gradient Sample Selection Skill

## PRIME DIRECTIVE: Zero Hallucination, Zero Fabrication

This skill operates under a strict **grounded-only** policy. Before using any number, claim, or result:

1. **Name the source paper** (author, year, arXiv ID or venue).
2. **Name the section or table** where the result appears.
3. **Quote the number verbatim** — do not round, extrapolate, or estimate.
4. **If you cannot find the source, say so explicitly.** Write: "[Source not verified — do not cite]".

Violation of this policy is worse than admitting ignorance. A wrong citation in a paper destroys credibility.

---

## Verified Paper Registry

| Short Name | Full Title | Venue / arXiv ID | Key Contribution |
|:---|:---|:---|:---|
| Bach et al. (2026) | Continual Safety Alignment via Gradient-Based Sample Selection | ACL 2026 / arXiv:2604.17215 | Gradient-based sample selection for text LLM continual alignment |
| Peng et al. (2024) | Navigating the Safety Landscape: Measuring Risks in Finetuning LLMs | NeurIPS 2024 / arXiv:2405.17374 | Safety Basin geometry; VISAGE metric |
| Ji et al. (2024) | Language Models Resist Alignment: Evidence From Data Compression | arXiv:2406.06144 | Elasticity framework; elastic reversion force |
| SafeVLM / Liu et al. (2024) | Safety Alignment for Vision Language Models | arXiv:2405.13581 | Safety projector + safety tokens + safety head |
| VLMGuard-R1 (2026) | VLMGuard-R1: Proactive Safety Alignment for VLMs via Reasoning-Driven Prompt Optimization | ACL 2026 / arXiv:2504.12661 | Model-agnostic input-stage guardrail |
| FigStep (2023) | FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts | arXiv:2311.05608 | Typographic jailbreak; 82.50% avg ASR on 6 open-source LVLMs |
| MM-SafetyBench (2023) | MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal LLMs | arXiv:2311.17600 | 13 scenarios, 5,040 text-image pairs |
| HarmBench (2024) | HarmBench: A Standardized Evaluation Framework for Automated Red Teaming | arXiv:2402.04249 | 18 red teaming methods, 33 target LLMs |
| POPE (2023) | Evaluating Object Hallucination in Large Vision-Language Models | arXiv:2305.10355 | Polling-based hallucination eval (Random/Popular/Adversarial) |

WRONG ID ON RECORD: arXiv:2406.14856 resolves to a Parkinson's disease detection paper.
Correct Safety Basin ID: arXiv:2405.17374 (Peng et al., NeurIPS 2024).

---

## Phase 1: Domain Scoping Before Touching Any Paper

### 1.1 Multi-Modal Gradient Mechanics
- Identify which parameters are trained (vision encoder typically frozen; projector and LM backbone trainable).
- Check whether label masking is applied to visual tokens (labels = -100 for vision spans).
- Note image resolution — it affects gradient norm magnitude and VRAM requirements.

### 1.2 Alignment Degradation Metrics — Confirm Before Citing
- ASR: Which attack set? Which judge model?
- VISAGE: Scale? Number of perturbation directions?
- TruthfulQA: Which version, shot count?
- BWT/FM: How many tasks? What task sequence?

### 1.3 Data-Centric Boundary Definitions — Never Conflate These
- Moderate-Gi: fraction rho CLOSEST TO MEDIAN gradient norm
- Low-Gi: strictly bottom rho by gradient norm
- High-Gi: strictly top rho by gradient norm
- Random: uniform random subset at ratio rho

---

## Phase 2: Systematic Research Dissection

### 2.1 Gradient Selection Taxonomy

| Category | Definition | Example |
|:---|:---|:---|
| Gradient Filtering | Drops samples based on gradient magnitude before optimizer step | Bach et al. Moderate-Gi |
| Gradient Projection | Projects gradient onto a subspace | OGD (Orthogonal Gradient Descent) |
| Gradient Clipping | Scales gradient magnitude; does NOT change direction or remove samples | clip_grad_norm_ |
| Gradient Regularization | Adds a penalty term to loss (KL, EWC Fisher) | EWC, KL-reg |

HARD RULE: These are distinct mechanisms. Do not conflate them.
Bach et al. Appendix explicitly proves gradient clipping is insufficient because it preserves gradient DIRECTION.

### 2.2 What High-Gradient Samples Actually Are
Source: Bach et al. Appendix E.1 (Sample Audit)
High-gradient samples are predominantly FORMAT MISMATCHES — short-answer tasks where the aligned
model's verbose output distribution diverges from terse targets. They are NOT content-based outliers
and NOT adversarial examples in the traditional sense. Do NOT describe them as "adversarial."

### 2.3 VLM-Specific Checks
For any VLM paper, verify:
- Does it test multimodal attacks, or only text jailbreaks?
- Does it distinguish visual-encoder-channel vs. language-decoder-channel vulnerabilities?
- Does it measure false positive rate (over-refusal on benign images)?
- Is the vision encoder frozen during fine-tuning?

---

## Phase 3: Behavioral Constraints (Hard Rules)

1. Do not speculate on accuracy or safety metrics. If a VLM result is not yet measured,
   write: "[Not yet measured — open research question]"
2. Do not conflate gradient filtering with gradient projection.
3. Do not state that high-gradient samples are "adversarial" — cite Bach et al. App. E.1.
4. Do not invent benchmark scores.
5. Never cite arXiv:2406.14856 as the safety basin paper. Correct ID: arXiv:2405.17374.
6. Always distinguish training cost (~51% overhead per Bach et al.) from inference cost (unchanged).

---

## Quick Reference: Verified Numbers (Bach et al., ACL 2026)

Source for all numbers: Continual_Safety_Alignment.md (in-repo) and arXiv:2604.17215

| Metric | Model | Strategy | Value |
|:---|:---|:---|:---|
| AdvBench ASR | Qwen2.5-7B | Baseline full FT | 36.7% |
| AdvBench ASR | Qwen2.5-7B | Moderate-Gi | 10.2% |
| AdvBench ASR | Qwen2.5-7B | Random | 31.1% |
| HarmBench ASR | (unspecified) | Baseline | 27.8% |
| HarmBench ASR | (unspecified) | Moderate-Gi | 5.0% |
| HarmBench ASR | (unspecified) | EWC | 31.0% |
| HarmBench ASR | (unspecified) | LoRA-based | 10.0% |
| AdvBench ASR | LLaMA-3.1-8B | Baseline | 44.2% |
| AdvBench ASR | LLaMA-3.1-8B | Moderate-Gi | 18.3% |
| VISAGE Retention | Qwen2.5-7B | Moderate-Gi | 83.4% (65.5 vs 78.5 base) |
| VISAGE Retention | LLaMA-3.1-8B | Moderate-Gi | 87.6% (59.3 vs 67.7 base) |
| BWT | Qwen3-4B | Baseline | -18.5% |
| BWT | Qwen3-4B | Moderate-Gi | -4.3% |
| Training Overhead | Any | Moderate-Gi | ~51% |
| FigStep avg ASR | 6 open-source LVLMs | Black-box | 82.50% |
| MM-SafetyBench | Dataset size | — | 13 scenarios, 5,040 pairs |
| SafeVLM RTVLM | LLaVA-v1.5-7B+LoRA | SafeVLM | 8.26 (vs 6.39 base, 7.92 GPT-4V) |
