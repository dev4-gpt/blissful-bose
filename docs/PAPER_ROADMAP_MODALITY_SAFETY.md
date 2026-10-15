# Roadmap: From a Notebook to a Publishable Paper

**Date:** 2026-10-14 · Companion to `PLAN_MODALITY_SAFETY_TRADEOFF.md` (the experiment) and `notebooks/vlm_modality_tradeoff.ipynb` (the code).
**Status of claims:** deadlines below were read from search results on 2026-10-14; confirm each on the official site before planning around it. Anything marked *unverified* I could not confirm.

## 1. What a research paper needs (and why one notebook is not enough)

A notebook answers one question. A paper needs a **claim**, **evidence for it that survives scrutiny**, and a **place in the literature**:

| Part | What reviewers look for | Where we are |
|---|---|---|
| Problem and claim | One sentence that could be false | Draft: "Text and vision safety are [coupled / traded off / independent] in open VLMs" (the data must pick) |
| Related work | You know what exists and say exactly what is new | Started (section 2) |
| Method | Someone else can redo it | Notebook, seeded, cached |
| Baselines and reproduction | You can recover published numbers before extending them | **Not done** (section 3) |
| Experiments | Enough models, seeds and data that the claim is not an accident | 2 small model pairs, ~240 items: pilot scale only |
| Analysis | Why, not only what; failure cases; ablations | Steering test and blank-image control are the start |
| Limitations and ethics | Honest threats to validity; safe handling of harmful content | Section 7 |

Typical conference paper: 8 pages plus references and appendix, a fixed LaTeX template, anonymous submission, peer review with a rebuttal.

## 2. What has already been done (prior work map)

First pass from search summaries. Reading each paper properly is the next step; the "gap" column is my reading, not a verified claim.

| Theme | Papers | What they show | Gap relative to our question |
|---|---|---|---|
| Adding vision erodes safety | [Learning to See but Forgetting to Follow](https://arxiv.org/pdf/2405.04403); [VLGuard](https://arxiv.org/pdf/2402.02207); [VL adaptation impact](https://arxiv.org/pdf/2410.07571) | Visual instruction tuning raises attack success even on text prompts | Measure text *loss*; do not ask whether vision-channel safety moves the opposite way |
| Representation/modality gap | [Safety Alignment Degradation](https://arxiv.org/pdf/2410.09047) (ACL Findings 2025); [Bootstrapping LLM Robustness for VLM Safety](https://www.arxiv.org/pdf/2505.24208) | Image inputs shift hidden states away from text; gap correlates inversely with safety | Correlation across models; per-item coupling between channels not tested |
| Text safety does not transfer | [Cross-Modal Safety Mechanism Transfer](https://arxiv.org/pdf/2410.12662) (ICLR 2025) | Text-trained refusal fails on images; text-guided alignment fixes it | Offers a fix; we ask whether a *text-derived* direction transfers at inference, without retraining |
| Fine-tuning generalizes across modality | [Emergent misalignment in VLMs](https://arxiv.org/abs/2602.16931) (Feb 2026) | Narrow harmful tuning spreads across tasks and modalities; multimodal evals show more misalignment than text-only | Supports shared circuitry (H_shared) |
| Perception distortion | [Safety Perception Distortion](https://papers.nips.cc/paper_files/paper/2025/file/a627b9468c319c13a70b7c2fb8df65a3-Paper-Conference.pdf) (NeurIPS 2025) | Multimodal inputs can shift activations toward a *safer*-looking direction | Contradicts "vision is simply weaker"; needs reconciling |
| Training-free fixes | [Risk Awareness Injection](https://arxiv.org/html/2602.03402v2) (2026) | Visual tokens dilute risk signals; modulating them cuts attack success | Utility trade-off, not modality trade-off |
| Over-refusal | [Visual Self-Fulfilling Alignment](https://papers.cool/arxiv/2603.08486) (Mar 2026) | Lowers attack success while reducing over-refusal | Reported trade-offs are safety vs helpfulness |
| Benchmarks | MM-SafetyBench, FigStep, VLGuard, HoliSafe-Bench, VLSBench, SIUO (see `PROJECT_PLAN_CROSS_BENCHMARK_EVALUATION.md`) | Different image/text safety states and judges | Numbers not comparable across papers |

**What I did not find:** a paper that tests text-vs-vision safety as an explicit zero-sum/Pareto trade-off (a 2026 search returned none). Absence of search results is not proof none exists. This is a possible gap, but it needs a systematic search (Google Scholar, arXiv, Semantic Scholar, ACL Anthology) before any "first" claim.

## 3. What we must reproduce and retest

Reproducing published numbers shows our pipeline is trustworthy.

1. **One headline result per theme, with original code where public:**
   - VLGuard / Learning-to-See: VLM vs its LLM backbone on text-only harmful prompts (our conditions A vs B).
   - MM-SafetyBench: text-only vs typographic attack success on LLaVA-1.5, once with their judge protocol as a check.
   - Safety Alignment Degradation: the inference-time fix on LLaVA, if code is available *(unverified)*.
2. **Acceptance rule:** same *ordering* and direction of effect within CIs; do not expect identical percentages (different judges). If the ordering fails, find out why before extending.
3. **Retest under one protocol:** same judge, decoding and prompts across all models (the harmonized-evaluation idea in `PROJECT_PLAN_CROSS_BENCHMARK_EVALUATION.md`).
4. **Scale the pilot:** 5–8 model pairs from different families (Qwen2/2.5-VL, LLaVA-1.5, InternVL, Phi-3.5-vision; Gemma-3 if the licence allows), at least 500 items per condition, judge audits, bootstrap CIs.

## 4. Where a novel contribution could come from

Ranked by how defensible they are with free compute and no training:

1. **Channel coupling as a measured quantity.** First systematic per-item and per-scenario estimate of how text refusal and vision refusal covary across many open VLMs, with a blank-image control separating "image present" from "content in the image". Either outcome (coupled, traded off, independent) is publishable if the evidence is solid.
2. **Cross-modal transfer of a text-derived refusal direction** (steering). Does a direction learned only from text move vision-channel refusal? Layer sweep, direction-quality checks, over-refusal cost. Inference-only, so it fits the no-training rule.
3. **Reconciling conflicting reports:** the perception-distortion paper (multimodal looks safer) vs the degradation papers (multimodal is less safe). Our four-condition design can show when each holds (typographic vs natural images, blank vs content).
4. **Benchmark-comparability study:** same models, one protocol, several benchmarks, showing which conclusions flip with benchmark or judge. Lower novelty, high practical value.

Pick one as the **primary claim** and make the rest supporting analysis. One clear claim beats four half-claims.

## 5. Where to publish

Today is 2026-10-14. From search results:

| Venue | Status | Source |
|---|---|---|
| ICLR 2027 | Abstract Sep 18, paper Sep 25, 2026 AoE: **missed** | [ICLR 2027 call](https://iclr.cc/Conferences/2027/CallForPapers) |
| ARR October cycle (NAACL/COLING 2027) | Deadline Oct 12, 2026: **missed** | [ARR dates](https://aclrollingreview.org/dates) |
| **ARR January cycle, for ACL 2027** | Deadline **Jan 4, 2027** AoE; commitment date TBA | [ACL 2027 calls](https://2027.aclweb.org/calls/main/) |
| CVPR 2027 | Registration Nov 10, paper **Nov 16, 2026**, supplementary Nov 23; decisions Feb 25, 2027 | [CVPR 2027 call](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) |

Interpretation:

- **CVPR Nov 16 is 33 days away.** Realistic only for a narrow, finished result; I would not target it from a notebook that has not yet produced real numbers.
- **ARR January 4, 2027 (ACL 2027)** is the best-fit main-track target: about 12 weeks, enough to reproduce, scale, run the steering analysis and write.
- **Workshops** (safety / trustworthy multimodal AI workshops at ICLR, CVPR, ACL, NeurIPS) take 4–8 page papers on earlier or rolling deadlines and are a good first publication. I did not find a specific list this session. *(Unverified that suitable 2027 workshops have open deadlines.)*
- **ICML 2027** is likely around late January 2027 *(unverified)*.
- **arXiv:** post a preprint once the draft is stable. New arXiv authors may need an endorsement, which your advisor can usually give *(check current arXiv policy)*.

## 6. Timeline (target: ACL 2027 via ARR Jan 4, 2027)

| Weeks | Work | Output |
|---|---|---|
| Oct 14–20 | Finish smoke test; first pilot numbers (2 pairs, 240 items); advisor meeting on the claim | `results.json`, claim v0 |
| Oct 21–Nov 10 | Systematic literature search; reproduce 2–3 published results; fix protocol | Related-work table, reproduction report |
| Nov 11–Dec 8 | Scale to 5–8 model pairs, ≥500 items; judge audits; steering layer sweep | Main results, figures |
| Dec 9–Dec 23 | Ablations, failure analysis, ethics and limitations; first full draft | Draft 1 for advisor |
| Dec 24–Jan 3 | Revise, internal review, template compliance, anonymization | Submission-ready PDF |
| Jan 4 | Submit via ARR | Submitted |

Slack is thin. If reproduction slips, submit to a workshop and aim the full paper at the next cycle.

## 7. Ethics and responsible handling

Common practice in this area (from searched examples; verify against each venue's checklist): disclose findings to affected vendors before publication where applicable, withhold or redact the most dangerous prompts and outputs, state a release plan for code and data, and include a dual-use discussion and a Limitations section. NeurIPS requires conformity with its [Code of Ethics](https://neurips.cc/public/EthicsGuidelines); ACL's Responsible NLP Checklist asks about risks and limitations.

For us: only released benchmarks and open models; no new attack prompts published; harmful outputs shown only redacted or summarized; the steering direction (a refusal-*removal* risk if reversed) discussed as dual-use; datasets are CC-BY-NC, fine for research, say so.

## 8. Things only your advisor can settle

- Authorship order, PSU affiliation and any student-submission rules.
- Workshop first, or a main-track attempt.
- Preferred benchmark, or a route to a vendor safety team.
- Whether no-training activation steering counts as within the "no heavy training" rule.

## 9. Next actions

1. Finish the Colab smoke test and read the first results.
2. Run the literature search: the "text-vs-vision trade-off" claim, plus workshops with open 2027 deadlines; read the ten core papers in full.
3. Meet the advisor with the claim options (section 4), the venue plan (section 5) and the pilot numbers.
