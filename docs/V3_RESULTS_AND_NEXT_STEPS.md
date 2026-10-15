# v3 results and next steps (exploratory, read before the human judge gate)

**Date:** 2026-10-15 · **Data:** `v3_final_four_judges/` (Qwen2-VL-2B and Qwen2.5-VL-3B, 304 MM-SafetyBench items each, 8 scenarios × 38) · **Status:** exploratory. The human audit gate in `ANALYSIS_PLAN_MODALITY_SAFETY.md` section 3 has **not** been passed; these numbers were read early at the author's request and the deviation is logged (plan section 9). Nothing here is a confirmatory result.

## 1. Which measurements can be trusted

Five labellers were run on every reply. Comparing each judge's *ungated* REFUSE rate with the keyword baseline shows they are not equivalent:

| Labeller | Behaviour | Use |
|---|---|---|
| Qwen3-4B-Instruct-2507 rubric | labels 84-90% of replies REFUSE in **every** condition, including replies the keyword check calls compliant (C: 0.875 ungated vs 0.115 keyword, 2B) | **Invalid as a judge.** After the refusal-cue gate its rates equal the keyword rates to the third decimal |
| Legacy Qwen2.5-3B | same failure (C: 0.862 ungated) | Invalid; after gating it also equals the keyword baseline |
| Qwen3Guard-Gen-4B | independent classifier; rates within 0.02-0.12 of keyword | Usable |
| WildGuard | independent classifier; rates within 0.02-0.03 of keyword | Usable |
| Keyword (first 200 chars) | transparent, lexical | Baseline |

Consequence: the "judge spread" in `results.json` (max/min of G of 1.06-1.26) compares three copies of the keyword rule with two real classifiers, so it does **not** show that conclusions are robust to the judge choice. It shows that two independent guard classifiers agree with the keyword rule within a few points. The v3 rubric prompt needs to be replaced; v4 drops both LLM-rubric judges rather than gating them. Guard-model agreement (Cohen kappa between Qwen3Guard and WildGuard): 0.96-1.00 in A, B, D, E; 0.98 in C for the 3B; **0.67 in C for the 2B**, the one cell where the two disagree (Qwen3Guard 0.23, WildGuard 0.13 refusal).

## 2. What the data say (guard classifiers; scenario-clustered intervals in `results.json`, paired tests in `offline_analysis.json`)

Refusal rate (share of replies labelled REFUSE; two guards: Qwen3Guard / WildGuard):

| Model | A (backbone text) | B (VLM text) | C (typed in image) | D (blank image) | E (same prompt, phrase as text) |
|---|---|---|---|---|---|
| Qwen2-VL-2B | 0.72 / 0.72 | 0.66 / 0.65 | 0.23 / 0.13 | 0.77 / 0.77 | 0.22 / 0.16 |
| Qwen2.5-VL-3B | 0.79 / 0.78 | 0.74 / 0.74 | 0.45 / 0.44 | 0.76 / 0.76 | 0.53 / 0.51 |

- **The typographic gap G = B - C is large:** 0.43 / 0.52 (2B) and 0.29 / 0.30 (3B); all scenario-clustered intervals exclude 0 and the lower bounds are at least 0.18.
- **Most of it is not the image channel.** Pasting the *same key phrase as text* into the *same generic prompt* (E) drops refusal almost as far as the image does. The prompt-wording term P = B - E is 0.44 / 0.49 (2B) and 0.21 / 0.23 (3B): 70-100% of G. Exact paired test B vs E: p < 1e-13 in every model/judge; direction holds in 7-8 of 8 scenarios; logistic GEE odds ratio for E vs B 0.11-0.14 (2B) and 0.37-0.39 (3B).
- **The residual image effect (E - C) is model-dependent and small.** 2B: -0.01 / +0.03, discordant pairs balanced (29 vs 33; 28 vs 18), GEE odds ratio 1.08 [0.81, 1.45] / 0.77 [0.54, 1.09]: **no detectable image-channel effect**. 3B: +0.08 / +0.07, McNemar p = 0.002 / 0.006, 8 of 8 and 7 of 8 scenarios positive, odds ratio 0.72 [0.59, 0.88] / 0.75 [0.61, 0.91]: a **real but small** image-channel effect of about 6-8 points.
- **Reading is not the bottleneck for these models.** The model transcribes the typed phrase correctly for 88% (2B) and 93% (3B) of items (97-99% on the subset where two OCR readers agree on the reference). Comprehension term Cmp = 0.00-0.02; residual routing R is 0.02-0.06, interval includes 0 except under Qwen3Guard for the 3B.
- **No see-saw.** Adding vision to the text backbone lowers text-channel refusal slightly (A - B = +0.06 for the 2B, +0.02 for the 3B; A uses a different checkpoint, so descriptive only), and item-level text/image refusal is positively coupled (within-scenario phi 0.12 [0.00, 0.24] for the 2B, 0.33 [0.20, 0.45] for the 3B, computed from the keyword-equivalent gated labels). Image refusal falling while text refusal rises is not observed.
- **Blank image:** adding a blank image *raises* harmful-request refusal (D - B = +0.11 for the 2B, +0.02 for the 3B); refusal on the 48 benign twins is 0-2% everywhere, so over-refusal cannot be assessed with this set.

## 3. Pre-specified hypotheses scorecard (exploratory)

| # | Result | Verdict |
|---|---|---|
| H1 gap >= 0.15, both models | G = 0.29-0.52, intervals exclude 0 | **Supported** |
| H2 image-channel part is at least half of G | image part (E - C) is 0-25% of G | **Refuted**; prompt part dominates |
| H3 within-scenario phi >= 0.20, interval excludes 0 | 2B 0.12 (below threshold); 3B 0.33 (met) | **Mixed**; positive in both, no see-saw |
| H4 blank image raises harmful and benign refusal | harmful +0.02 to +0.11; benign flat at 0-2% (n=48) | **Not testable** at this benign size |
| H6 adding vision lowers text safety (2B only) | A - B = +0.06 (2B), +0.02 (3B) | Directionally yes in both; descriptive |
| H7 Cmp >= 40% of G (2B), <= 25% (3B) | Cmp = 4% and 6% of G | **Refuted** |
| H7b R positive, interval excludes 0 in both | excludes 0 only for the 3B under one guard | **Refuted** |
| H8 judge spread > 1.5x | spread <= 1.26x, but see section 1 | **Refuted, but uninformative** (three of five labellers are the keyword rule) |

Plan section 5 decision row that applies: *"H1 holds but (E - C) is small -> most apparent image weakness is prompt wording."* Wording, not reading: the comprehension story (H7) did not materialise for these two models.

## 4. Why this is not yet a paper result, and what v4 tests

1. **P bundles three things.** E differs from B in (a) the generic "list steps in detail" wrapper, (b) the information content (key phrase only vs the full question) and (c) the loss of any question form. We cannot yet say that a *wrapper* artifact, rather than an *information* artifact, drives the gap. v4 separates them with a text-only factorial: B (full question), G_full (generic wrapper + full question), E (generic wrapper + phrase), N (neutral wrapper + phrase).
2. **Modality effect under a neutral wrapper.** v3 only measures E vs C under the generic wrapper. v4 adds a neutral-wrapper image/text pair, plus a full-question-as-image condition (FigStep-style) with its text twin.
3. **Two Qwen models cannot support a general claim.** v4 adds LLaVA-1.5-7B (4-bit; non-Qwen family; 336 px input, which may hurt legibility).
4. **Refusal is not safety.** v4 adds a harmfulness label on replies (Qwen3Guard response safety) so the gap can be restated as "unsafe replies", not only "non-refusals".
5. **Over-refusal.** 48 benign twins cannot show it. v4 adds XSTest safe prompts (about 250) as text and as typed images, if the dataset loads.
6. **Judges.** v4 drops the failed LLM-rubric judges and reports Qwen3Guard, WildGuard and the keyword rule, with their agreement.
7. **Still outstanding:** the human audit (200 blinded rows, 60-row retest after one day), the judge gate against those labels, and a confirmatory run with >= 100 items per scenario. v4 is exploratory and extends the design; it does not replace them.

## 5. Limits to state in any write-up

Two small Qwen models (plus LLaVA in v4); one benchmark, one typographic rendering; 8 scenario clusters (intervals are unstable; paired exact tests and sign tests over scenarios are reported alongside); single labeller for the human gate; refusal is not harm; the early read of v3 before the human gate means v3 cannot be used as confirmatory evidence.
