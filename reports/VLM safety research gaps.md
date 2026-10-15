# VLM safety: research gaps and the proposal we should test

**Date:** 2026-10-14 · Author: Aryaman Singh Dev · Advisor: Prof. Thao Minh Le (PSU)
**How this was produced:** six parallel literature scouts (attacks and benchmarks, mechanisms, defenses, evaluation validity, 2026 frontier, your own corpus), then four checkers (two prior-art checks, a design/feasibility spec, a simulated ACL review panel). Findings are saved in the Ruflo memory namespace `vlm-safety-paper`.
**Reading guide:** *verified* = I checked it myself; *agent-reported* = a subagent opened the source (usually an LLM-summarised read, not line by line); *unverified* = seen only in a snippet or inferred. I verified only two things myself: MARS (arXiv 2606.31876) exists and shows text-derived refusal directions transfer to images, and the pilot judge failure (90 of 125 Qwen2-VL-2B image-condition "refusals" contain no refusal phrase).

> **Status update, 2026-10-15 (after the v3 run).** Exploratory v3 results (`docs/V3_RESULTS_AND_NEXT_STEPS.md`) support the headline direction but not all of the predictions below. The typographic gap is real (G = 0.29-0.54) and **most of it is prompt wording or content, not the image channel** (P is 70-100% of G; the residual image effect is about 0 for Qwen2-VL-2B and 6-8 points for Qwen2.5-VL-3B). The comprehension story did **not** materialise (read-back 88-93%, Cmp = 0-2 points, so P2 is refuted) and the residual routing term R is small (P3 mostly refuted). The multi-judge spread (P4) is uninformative because the two LLM-rubric judges were invalid (they label 84-90% of replies REFUSE); two independent guard models agree with the keyword rule. Next experiment: `notebooks/vlm_modality_tradeoff_v4.ipynb`, pre-specified in the analysis plan (Amendment 2, H10-H15), which splits the wrapper from the content, adds a non-Qwen model, harmfulness and XSTest over-refusal.

## 1. Bottom line

1. **What we are not doing:** replicating published steering results. Steering transfer from text to images is already published (MARS, JRS-Rem, a 2026 cross-architecture audit that includes Qwen2-VL-2B with random-direction controls). It becomes an appendix.
2. **What five of six scouts independently flagged:** the apparent weakness of the typographic-image channel in small VLMs may be partly a *measurement and comprehension artifact*: the prompt wording differs, the model may not be able to read the rendered text, and small judges mislabel the replies. Several papers raise this (Lingua-SafetyBench, Azulay et al., MSTS, 2604.25102) but none, as far as the checkers found, measures it per item on sub-4B open VLMs.
3. **Proposed paper:** a measurement-led study that *decomposes* the typographic refusal gap into a prompt-format effect, a comprehension (read-back) failure, and a residual routing failure, with a multi-judge, human-validated, three-way label. Item-level coupling of text and image refusal is supporting evidence. A probe conditioned on non-refusals is a stretch goal.
4. **Realistic venue today:** a workshop paper first, then ARR or TMLR depending on the evidence. The simulated reviewers would reject the current plan from the ACL main conference; they judged a narrow, pre-specified measurement paper plausible for Findings or a workshop if specific fixes are made (section 7).

## 2. The field in one page

| Area | Established | Contested or open |
|---|---|---|
| Image weakens refusal | Adding vision lowers refusal relative to the backbone (CMRM 2410.09047, VLGuard, Learning-to-See, Lee et al. 2410.07571, TGA 2410.12662) | Size of the gap depends on model, OCR route and judge: Lingua finds typography > pure vision; Cisco finds image ASR about equal to text for Qwen3-VL-4B; MMJailBench finds rendered text does not consistently beat text |
| Mechanism | A shared refusal direction exists across text and image (Arditi 2406.11717; MARS; a 2026 audit finds positive cosine in 15 of 15 cells); text safety is concentrated, visual safety diffuse (2608.30750) | Three competing accounts of *why*: mean shift toward "safe" (ShiftDC), loss of separability (2605.18104), high raw projection with no discrimination (MARS, unverified reading). Never compared head to head on one model |
| Defenses | Text-only unlearning transfers to image attacks (2406.02575); caption fallback (ECSO) works; weight merging and replay mixes help | Over-refusal is the main cost (VLGuard XSTest acceptance 91 to 42); safety is lost under benign fine-tuning (HPA); most defenses are evaluated in-distribution with LLM judges |
| Evaluation | Judges collapse under distribution shift (Coin Flip 2603.06594, Know Thy Judge); keyword matching is biased (StrongREJECT, XSTest); open VLMs show 28.5% "safe by accident" replies that are misunderstanding, not refusal (MSTS) | No validated judge protocol for the image channel; refusal, harm and comprehension are conflated |
| Frontier (2026) | Crowded: inference-time defenses, reasoning-VLM safety, typographic attacks on big models, direction transfer | Under-explored: sub-4B open VLMs, capability-controlled comparisons, per-scenario coupling |

## 3. Candidate hypotheses, ranked

| # | Hypothesis | Prior-art verdict (agent-reported) | Cost | Rank |
|---|---|---|---|---|
| H-A | The typographic gap decomposes into prompt-format + read-back failure + residual routing failure; the residual is smaller than reported | Pieces exist (MMJailBench, Azulay, MSTS); per-item read-back conditioning on sub-4B open VLMs with a prompt-matched control appears open | Inference only | 1 (headline) |
| H-B | A multi-judge, three-way (refuse / comply / did-not-comprehend), human-validated protocol changes conclusions versus a single small judge | Concept exists (Azulay, MSTS); applying it to the standard typographic channel with an independent read-back score appears open | Inference + one evening of labels | 2 (co-headline) |
| H-C | Item-level text-image refusal coupling remains positive within scenario after controlling for item difficulty | Least occupied: no item-level coupling found (caveat: search absence only) | Offline stats on saved labels | 3 (supporting) |
| H-D | Harmfulness stays linearly decodable from image-prompt states on non-refused items (probe) | Partly done: an unpublished repo and JRS-Rem make the argument; text-trained probe transfer conditioned on non-refusals in sub-4B Qwen-VL not found | ~1 h CPU on cached states, needs controls | 4 (stretch) |
| H-E | Per-layer divergence plus real activation patching text-run to image-run | Partly done, high scoop risk | GPU hours | Not recommended as lead |
| H-F | Scenario-matched recentering fixes steering over-refusal at 2-3B | Direct extension of MARS; high scoop risk | Moderate | Appendix or future work |
| H-G | Flip probability between text and image is non-monotonic in the text refusal margin (mid-margin items are most fragile) | Analogy to Bach et al.; novelty unchecked | Cheap once margin metric works | Exploratory |
| H-H | Replay-light safety retention under benign LoRA tuning | Needs training, outside the advisor's exclusions | LoRA hours | Out of scope |

## 4. Recommended proposal

**Working title:** "Is the typed-text image channel really less safe? Decomposing the refusal gap in small open VLMs." (Retitle to "refusal gap" per the review panel, since refusal is not safety.)

**Research question.** In small open VLMs, how much of the lower refusal rate for harmful requests rendered as typed text in an image is explained by (i) prompt wording, (ii) the model failing to read the text, versus (iii) a real failure to turn recognised harm into refusal?

**Contributions (honest wording from the novelty check):** a per-item, read-back-conditioned decomposition of the standard typographic channel (FigStep / MM-SafetyBench TYPO) in sub-4B open VLMs, combining a prompt-matched text control, an independent transcription score and a refuse / comply / did-not-comprehend label; a multi-judge sensitivity analysis showing which conclusions depend on the judge; item-level coupling within scenario. Avoid "first" and "novel decomposition".

**Design (from the design spec):**
- **Conditions per item:** A LLM text, B VLM plain text, C typed-in-image + generic prompt, D blank image, E generic prompt with the *same key phrase as text*, benign twins.
- **Fix before v2 results are trusted:** the current v2 condition E embeds the *full* question while C shows only the rendered key phrase, so E can carry more information than a perfect reader gets from C and will inflate (E - C). Build E from the key phrase (extract it by two-OCR agreement with CER <= 0.1, or hand-transcribe about 300 short phrases) and treat the current E as a different condition. Also cap image resolution identically in every condition.
- **Read-back:** same image, prompt "Transcribe the text written in this image exactly...", greedy, 48 tokens; normalised character error rate; *verified read* = CER <= 0.10 and >= 90% content words (sensitivity at 0.25). Store only flags, CER and a salted hash, never the transcription in outputs.
- **Decomposition (exact):** G = S_B - S_C = P + Cmp + R with P = S_B - S_E (prompt), Cmp = (1 - w)(S_E|unread - S_C|unread) (comprehension), R = w(S_E|read - S_C|read) (residual routing), w = share of verified reads. Report shares only if the bootstrap lower bound of G exceeds 0.05; otherwise report percentage points. Include phrase length as a covariate, because read-back is confounded with difficulty.
- **Judges:** Qwen3Guard-Gen-4B, WildGuard (cross-family, gated auto-approve, 4-bit), Qwen3-4B-Instruct-2507 with the three-label rubric, plus the legacy Qwen2.5-3B as a baseline; compare with a keyword baseline. Judge-free check: teacher-forced prefix-level refusal score (a first-token margin is unreliable because "I" starts both refusals and compliance).
- **Statistics:** scenario-clustered paired bootstrap with t(7) critical values, a mixed-effects logistic model with an item random effect and a modality fixed effect for coupling, Holm correction across the primary family.
- **Models:** Qwen2-VL-2B, Qwen2.5-VL-3B, plus LLaVA-1.5-7B in 4-bit (note its 336 px resize hurts legibility, which is itself informative) and ideally Qwen2.5-VL-7B in 4-bit, so "differs by model" can be tested beyond two Qwen models.
- **Compute:** about 45-100 minutes of generation per small model per full matrix on a T4, 3-6 minutes of read-back, about 5 minutes of probe features (estimates, to be measured on a 16-item run first).

**Pre-specified predictions** (to be added to the analysis plan as an amendment before v2 results are read):
- **P1:** B - C >= 0.15 with an interval excluding 0 in both Qwen models (refuted if either interval includes 0).
- **P2:** the comprehension term Cmp is at least 40% of G for the 2B model and at most 25% for the 3B model (refuted if the ordering reverses or both are within 10 points of each other).
- **P3:** the residual routing term R is positive with an interval excluding 0 in both (if R's interval includes 0 in both, the paper's message becomes "the gap is a comprehension and wording artifact").
- **P4:** the multi-judge spread of the image-condition gap exceeds a factor of 1.5, and the judge-by-channel interaction is positive.
- **P5:** within-scenario item coupling stays positive after the mixed-effects item effect (refuted if the modality-by-item coefficient is within noise of zero).
- **P6 (stretch):** a text-trained probe achieves AUROC >= 0.75 on image prompts among non-refused items, and exceeds the shuffled-label, bag-of-words and benign-typographic controls.

**Decision rule:** all outcomes publish: gap survives conditioning -> "the image channel is genuinely weaker beyond wording and reading"; gap shrinks to wording and reading -> "most apparent image weakness is an artifact"; no coupling beyond item difficulty -> report as a negative result and revisit the see-saw question.

## 5. What we cut and why

- **Steering** is an appendix (published; scoop risk; needs random-direction control).
- **Probe (H-D)** is optional; the review panel recommends omitting it from a 4-page paper, and it would need a post-hoc entry in the deviation log.
- **Per-layer patching (H-E)** is future work.
- **Four claims in four pages** is not credible; keep claims 1 and 2 with 3 as support.

## 6. Housekeeping found by the scouts

1. `docs/DEEP_LITERATURE_AUDIT_AND_RESEARCH_FOUNDATION.md` cites SIUO as arXiv 2410.01275 with GPT-4V 68.2% and LLaVA-1.5 45.7%. The SIUO PDF gives GPT-4V 53.29% and LLaVA-1.5-7B 21.56%, and the correct ID is 2406.15279 (agent-reported).
2. Three PDFs in `presentation/paper_pdfs/` are the wrong papers (safetyreminder.pdf, siuo.pdf, vlsbench.pdf); use the `_acl` and `_aaai` versions (agent-reported).
3. Do not commit `Big Data Lab Cluster User Guide 2.pdf` (agent-reported to contain a shared password).
4. "ACL 2026" for Bach et al. is unverified; the file is an arXiv preprint.
5. The statement that eight MM-SafetyBench scenarios are "clearly harmful" was chosen by name; verify in the original paper.
6. Two unrelated papers are both named "ReGap"; cite carefully.

## 7. What the simulated reviewers would reject (and the cheapest fix)

1. **Two Qwen models cannot support "model-size dependent".** Add a non-Qwen family and a larger Qwen, or say "differs between the two models".
2. **Item difficulty explains coupling; OCR conditioning is selection-biased.** Mixed-effects model; report stratified and pooled estimates.
3. **The judge story is a straw man** (our pilot judge was a 3B model). Compare against keyword and guard-model baselines; two human labelers on at least 120 shared rows, or report self-consistency with CIs and state it as a limitation.
4. **Probe claim is post-hoc and uncontrolled.** Drop it or add controls and log the deviation.
5. **Refusal is not safety.** Retitle; sensitivity analysis dropping partly benign scenarios; harmfulness check on about 100 compliant outputs.
6. **Novelty against MARS and eight related papers.** One table: prior work by control (prompt-matched, OCR, three-way label, benign twins, item-level coupling).
- Also: say "pre-specified before v2" (v1 was seen); ~37 items per scenario with 8 clusters makes cluster intervals unstable.

## 8. Ethics and Responsible NLP items (from the review panel; verify against the current ARR checklist)

Mandatory Limitations (Qwen-heavy, small judges, single labeler, typographic images only, English only); risks and dual-use (no jailbreak prompts or images released, redacted or aggregate examples only); annotator statement (who labeled, exposure to harmful content, wellbeing mitigation, consent); licences (MM-SafetyBench CC-BY-NC, model licences); compute, seeds and decoding; AI-assistance disclosure; kappa with confidence intervals.

## 9. Timeline and venue

| Dates | Work |
|---|---|
| Oct 15-17 | Amend analysis plan; fix condition E using the key phrase; add read-back and the multi-judge ensemble to the notebook; read v1/v2 judge gate only |
| Oct 18-Nov 5 | Hand-label the audit sample; run the fixed matrix on 2B, 3B and a third family; mixed-effects analysis |
| By Nov 20 | Workshop version (AAAI-27 Deployable AI, 4 pages, non-archival; none is dedicated to VLM safety) if gates pass |
| Nov 21-Dec 20 | Confirmatory run (>=100 items per scenario where data allow, >=4 models, max_new_tokens >= 256), draft |
| Jan 4, 2027 | ARR submission for ACL 2027, or TMLR depending on evidence |

## 10. Re-checks before any submission

Re-run arXiv searches for October 2026 onward (typographic, OCR, read-back, misunderstanding, small VLM, refusal direction); read the full bodies of 2609.26174, 2609.31403, 2603.08497, 2607.27910, 2603.17372 and 2609.18860; check whether the "Seen but Not Refused" repository links a paper; read FigStep's text-baseline construction; confirm the MM-SafetyBench image types used.

## 11. Source list (opened by agents unless marked)

MARS 2606.31876 (also verified by lead); CMRM 2410.09047; 2505.24208; ShiftDC 2502.13095; 2605.18104; CR-VLM 2602.07013; 2608.30750; TGA 2410.12662; VLM-Guard 2502.10486; 2605.00583; 2607.27910; 2608.18628; 2603.25035; 2609.18860 (abstract); Arditi 2406.11717 (abstract); MM-SafetyBench 2311.17600; FigStep 2311.05608; HADES 2403.09792; VLSBench 2411.19939; SIUO 2406.15279; HoliSafe 2506.04704; MemeSafetyBench 2505.15389; 2507.11155; 2604.12371; 2604.25102; 2605.07250; 2601.22737; MMJailBench 2608.25490; Text2VLM 2507.20704; MSTS 2501.10057; VLGuard 2402.02207; SPA-VL 2406.12030; 2406.02575; ECSO 2403.09572; Lee et al. 2410.07571; NullSteer 2603.22094; HPA 2511.20158; VLMGuard-R1 2504.12661; Coin Flip 2603.06594; SORRY-Bench 2406.14598; StrongREJECT 2402.10260; XSTest 2308.01263; 2411.08410; 2605.05427; Know Thy Judge 2503.04474; Miller 2411.00640; MOSSBench 2406.17806; DUAL-Bench 2510.10846; EchoSafe 2603.15800; JRS-Rem 2603.17372; 2602.16931; SafeThink 2602.11096; Bach et al. 2604.17215 (local PDF).
