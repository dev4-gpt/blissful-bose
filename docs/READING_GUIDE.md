# Reading Guide: Which File Answers Which Question
## Continual Safety Alignment in Small VLMs — Navigation Map

> ✅ = verified from PDF OCR (trust numbers) | ⚠️ = structurally correct, cross-check numbers against PRESENTATION_CITED_WRITEUP.md

---

## 1. Results of the Original Paper (Bach et al.)

| What you need | File | Section | Trust |
|:---|:---|:---|:---|
| Core claim: benign FT breaks safety | PRESENTATION_CITED_WRITEUP.md | SLIDE 2 | ✅ |
| Algorithm (3-stage exact pseudocode) | PRESENTATION_CITED_WRITEUP.md | SLIDE 6 | ✅ |
| ASR results — 3 models, all methods | PRESENTATION_CITED_WRITEUP.md | SLIDE 7 (Table 6) | ✅ |
| Safety basin / VISAGE retention | PRESENTATION_CITED_WRITEUP.md | SLIDE 4 (Table 2) | ✅ |
| BWT / catastrophic forgetting results | PRESENTATION_CITED_WRITEUP.md | SLIDE 8 (Table 8) | ✅ |
| HarmBench generalization | PRESENTATION_CITED_WRITEUP.md | SLIDE 9 (Table 9) | ✅ |
| Format-mismatch mechanism | PRESENTATION_CITED_WRITEUP.md | SLIDE 5 (Table 4) | ✅ |
| Deep math derivation | docs/gradient_strategy_dossier.md | §1–§3 | ⚠️ |
| Step-by-step Bach procedure | docs/master_research_formulation.md | PART 1 (Steps 1–6) | ⚠️ |

---

## 2. VLM Strategy — Method, Eval, Datasets

| What you need | File | Section | Trust |
|:---|:---|:---|:---|
| VLM architecture decomposition | PRESENTATION_CITED_WRITEUP.md | SLIDE 11 | ✅ |
| 3 gradient attribution modes (G_i^L, G_i^P, G_i^J) | PRESENTATION_CITED_WRITEUP.md | SLIDE 11 | ✅ |
| Label masking requirement | PRESENTATION_CITED_WRITEUP.md | SLIDE 11 | ✅ |
| Task sequence: LLaVA→MathVista→VQA-RAD→DocVQA | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 | ✅ |
| All evaluation benchmarks | PRESENTATION_CITED_WRITEUP.md | SLIDE 3 | ✅ |
| Phase 1 Colab + Phase 2 Cluster plan | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 | ✅ |
| PyTorch implementation: micro-batch backward | docs/reproducibility_blueprint.md | §1.1–§1.3 | ✅ |
| vLLM for eval at scale | docs/reproducibility_blueprint.md | §2 | ⚠️ |
| Full VLM step-by-step adaptation | docs/master_research_formulation.md | PART 2 | ⚠️ |

---

## 3. SOTA — What's Already Been Done At This Problem

| What you need | File | Section | Trust |
|:---|:---|:---|:---|
| SafeVLM — existing VLM safety approach | PRESENTATION_CITED_WRITEUP.md | SLIDE 10 (numbers from PDF) | ✅ |
| All 6 method families with tradeoffs | docs/methodology_comparison.md | All sections | ⚠️ |
| 20+ paper survey | docs/sota_landscape_survey.md | Pillars 1–6 | ⚠️ |
| Which prior methods are drop-in usable | docs/master_research_formulation.md | PART 3 (Categories A, B, C) | ⚠️ |
| Grand comparison table | docs/methodology_comparison.md | "The Grand Comparison Table" | ⚠️ |

---

## 4. Research Challenges (VLM-Specific)

| Challenge | File | Section |
|:---|:---|:---|
| Label masking (visual tokens inflate gradients) | docs/master_research_formulation.md | PART 4, Challenge 1 |
| Which parameter group drives multimodal drift | docs/master_research_formulation.md | PART 4, Challenge 2 |
| VRAM constraints for per-sample backward passes | docs/master_research_formulation.md | PART 4, Challenge 3 |
| Cross-modal jailbreaks (no text-only equivalent) | docs/master_research_formulation.md | PART 4, Challenge 4 |
| Over-refusal on benign visual inputs | docs/master_research_formulation.md | PART 4, Challenge 5 |
| Compute gating (Phase 1 vs Phase 2) | docs/master_research_formulation.md | PART 4, Challenge 6 |
| Open engineering questions | docs/reproducibility_blueprint.md | §3, OPEN 1–5 |

---

## 5. Adversarial Attacks for Alignment Testing

| Attack | File | Section | Citation |
|:---|:---|:---|:---|
| MM-SafetyBench: 5,040 pairs, 13 scenarios | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 row 1 | arXiv:2311.17600 |
| FigStep: typographic visual jailbreak | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 row 2 | arXiv:2311.05608 |
| JailBreakV-28K: 28K samples, 16 scenarios | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 row 3 | arXiv:2404.03027 |
| HarmBench text slice (VLM language decoder) | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 row 4 | arXiv:2402.04249 |
| Threat model and attack taxonomy | docs/master_research_formulation.md | PART 5 (A, B, C) | — |
| Attack verification status | docs/gradient_strategy_dossier.md | §6 | — |

---

## 6. Baselines for the Research

| Baseline | File | Section |
|:---|:---|:---|
| Full FT, Random, KL-Reg, O-LoRA, EWC, Grad.Clip | PRESENTATION_CITED_WRITEUP.md | SLIDE 7 (Table 6 verified numbers) |
| SafeVLM (architectural VLM safety method) | PRESENTATION_CITED_WRITEUP.md | SLIDE 10 |
| All 6 families with honest tradeoffs | docs/methodology_comparison.md | "Grand Comparison Table" |
| Which to include Phase 1 vs Phase 2 | docs/master_research_formulation.md | VLM-Step 4 |
| Layered inclusion strategy | docs/methodology_comparison.md | "Layered Strategy Over 3 Phases" |

---

## 7. Benchmarks

| Benchmark | File | Section | Citation |
|:---|:---|:---|:---|
| MM-SafetyBench (5,040 / 13 scenarios) | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 | arXiv:2311.17600 |
| FigStep | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 | arXiv:2311.05608 |
| JailBreakV-28K | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 | arXiv:2404.03027 |
| HarmBench (text slice) | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 1 | arXiv:2402.04249 |
| MMHal-Bench (hallucination primary) | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 2 | arXiv:2309.14525 |
| POPE (hallucination secondary) | PRESENTATION_CITED_WRITEUP.md | SLIDE 3, Battery 2 | arXiv:2305.10355 |
| LLaVA-Instruct-150K (task 1) | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 | arXiv:2304.08485 |
| MathVista 6,141 problems (task 2) | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 | arXiv:2310.02255 |
| VQA-RAD / SLAKE (task 3) | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 | doi:10.1038/sdata.2018.251 |
| DocVQA ~50K (task 4) | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 | arXiv:2007.00398 |
| Extra: RTVLM, XSTest | docs/sota_landscape_survey.md | Pillar 6 | — |

---

## 8. Suggested Procedure / Methodology

| What you need | File | Section |
|:---|:---|:---|
| Complete VLM procedure (6 steps from Bach et al.) | docs/master_research_formulation.md | PART 2 (VLM-Steps 1–6) |
| Engineering implementation (code level) | docs/reproducibility_blueprint.md | §1–§2 |
| Phase 1 Colab + Phase 2 cluster execution | PRESENTATION_CITED_WRITEUP.md | SLIDE 12 |
| Layered baseline inclusion over time | docs/methodology_comparison.md | "Layered Strategy" |
| Research novelty vs prior work | docs/sota_landscape_survey.md | "Three-Line Novel Contribution Summary" |

---

## Recommended Reading Order

**30 minutes before PPT:**
→ `docs/PRESENTATION_CITED_WRITEUP.md` top to bottom — everything verified

**2 hours to understand full research:**
1. `PRESENTATION_CITED_WRITEUP.md` — verified PPT content
2. `docs/master_research_formulation.md` PART 4 + PART 5 — challenges + attacks
3. `docs/methodology_comparison.md` — all SOTA baselines
4. `docs/reproducibility_blueprint.md` §3 — open questions

**Before running the experiment:**
1. `docs/reproducibility_blueprint.md` §1–§2 — implementation
2. `PRESENTATION_CITED_WRITEUP.md` SLIDE 12 — Phase 1 plan
