# Status and paper plan: all versions v1 to v6 (written 2026-10-18)

This is a cross-version analysis. It reads every result folder (v1 to v6, aggregates only; raw replies stay on Drive) and answers three questions: what have we done, what do the data say, and is this a publishable paper. Everything below is **exploratory**: all results were read before the human-audit gate in `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md`, so none of it is confirmatory yet.

## 1. Verdict in five lines

1. **The original claim (a text/vision "see-saw") is not supported.** Across every version the two channels move together, not against each other (section 4).
2. **The finding that has stayed stable from v2 to v6 is a measurement finding:** the large typographic "refusal gap" in MM-SafetyBench is mostly produced by the benchmark's wrapper prompt and, for LLaVA, by image presence, not by the typed text being hard to read or being a different modality in the sense the benchmark claims.
3. We were **not testing randomly**: the headline gap B-C is the same number in v2, v3, v5 and v6 (section 3). Versions v3 to v6 each fixed a measurement flaw found by self-review or red-team, and each fix left the headline intact. That is a good sign.
4. We **have been circling** on one thing: three versions (v4, v5, v6) went into making measurement valid and adding controls, and the central claim has not changed since v3. It is time to freeze the design and move to confirmation.
5. **Publishable?** Yes as a workshop paper by 20 Nov if the human audit and one more model family are done. For ACL 2027 (ARR 4 Jan) it needs a mechanism or mitigation part and 4 to 6 models. Details in section 7.

## 2. The versions, what each did, and how far to trust it

| Ver | What it tested | Models, n | Labeller | What it showed | Trust |
|---|---|---|---|---|---|
| v1 (n5 smoke, n30 full) | Pilot: A LLM text, B VLM text, C typographic image, D blank image; coupling; refusal-direction steering | Qwen2-VL-2B, Qwen2.5-VL-3B; 240 items | Qwen2.5-3B rubric | Gap B-C only 0.20 (different image prompt); text and image refusal positively coupled | Low (judge later found invalid; different stimulus) |
| v2 | Stricter judge, benign twins, random items, E (key phrase as text) | same, 304 items | Qwen2.5-3B rubric | Gap B-C 0.51 (2B), 0.31 (3B); blank image raises refusal; steering restores vision refusal | Medium for the gap, low for labels. **v2 results were unread until today** |
| v3 | Gap decomposition G = P + Cmp + R; read-back of the typed phrase; 5 labellers; judge-free prefix score | same, 304 | keyword, Qwen3Guard, WildGuard, two LLM rubrics | 70 to 100% of G is wrapper/content (B-E), residual image effect about 0; read-back 88 to 93%; two LLM judges are invalid | Medium-high for the gap; decomposition is path-dependent (see section 6) |
| v4 | Factorial wrapper x content x modality, LLaVA, harm, XSTest | smoke only (16 items) | guards | Pipeline test only, superseded by v5 | Not interpretable |
| v5 | v4 plus noun-phrase, bare phrase, font size, interaction, Holm, audit files | + LLaVA-1.5-7B; 304 / 152 | Qwen3Guard, WildGuard, keyword | Wrapper explains most of Qwen's gap; LLaVA gap is image-driven; neutral-image block invalid (guards disagree, kappa 0.00 to 0.09) | Medium; neutral-image block unusable |
| v6 | Stimulus-aware 3-way labels, wrapper grid W0/W1/W2, presence controls, true-size legibility, FigStep replication, noise floor | 3 models; 304 / 152; 200 FigStep items | same three, 3-way | Guards agree (diffs under 0.02); wrapper x modality interaction large; FigStep replicates the wrapper effect | Best so far; still exploratory until the audit |

v4 has no full run; v5 and v6 each also have a smoke copy on Drive.

## 3. What is stable across versions (the evidence that we are not random)

Refusal rate by condition, same 304 items (152 for LLaVA), greedy decoding. A = LLM backbone text, B = VLM plain text, C = typographic image with the benchmark's wrapper, E = key phrase as text with the same wrapper. Selected rows; every labeller is in the data.

| Version / labeller | Model | A | B | C | D (blank) | E | **B - C** |
|---|---|---|---|---|---|---|---|
| v2 rubric | 2B | 0.72 | 0.65 | 0.14 | 0.77 | 0.44 | 0.51 |
| v3 keyword | 2B | 0.72 | 0.65 | 0.12 | 0.77 | 0.20 | 0.54 |
| v3 WildGuard | 2B | 0.72 | 0.65 | 0.13 | 0.77 | 0.16 | 0.52 |
| v6 WildGuard (3-way) | 2B | 0.72 | 0.65 | 0.12 | 0.77 | 0.15 | 0.53 |
| v6 Qwen3Guard (3-way) | 2B | 0.72 | 0.66 | 0.15 | 0.77 | 0.18 | 0.51 |
| v2 rubric | 3B | 0.76 | 0.74 | 0.43 | 0.76 | 0.65 | 0.31 |
| v3 keyword | 3B | 0.77 | 0.74 | 0.43 | 0.76 | 0.49 | 0.31 |
| v6 WildGuard (3-way) | 3B | 0.78 | 0.74 | 0.44 | 0.76 | 0.50 | 0.30 |
| v5 WildGuard | LLaVA-1.5-7B | 0.53 | 0.44 | 0.02 | 0.05 | 0.38 | 0.42 |
| v6 WildGuard (3-way) | LLaVA-1.5-7B | 0.53 | 0.44 | 0.00 | 0.05 | 0.37 | 0.44 |

Observations:

- The headline gap B-C is 0.51 to 0.54 for the 2B, 0.30 to 0.31 for the 3B and 0.42 to 0.44 for LLaVA, regardless of version or labeller. A and B barely move, so VLM training costs only 0.05 to 0.06 of text refusal.
- The simple keyword rule tracks WildGuard within about 0.04 in every cell. Refusal can be measured cheaply; the hard part is "did the model answer the question it was given" (NOT_COMPREHEND), which v6 handles.
- Reply text changes with batch size on 7 to 34% of replies, but the refusal label changes on under 1%. The refusal labels are robust to that noise.
- The judge-free prefix score (v3: log-likelihood of a refusal opening) points the same way: 2B B = 0.87 vs C = -4.14; 3B B = 3.64 vs C = -0.93. The gap does not depend on any labeller.

## 4. What the data say about the original hypothesis (see-saw)

- **Coupling is positive, not negative.** Item-level phi between text and image refusal is 0.24 to 0.54, and scenario-level Spearman is 0.73 to 0.90 (v1 and v2, both models, p between 0.002 and 0.04). Scenarios that a model refuses in text, it also tends to refuse in the image.
- **Across models, the better-aligned model is better in both channels:** 3B beats 2B on text refusal (0.74 vs 0.66) and on image refusal (0.44 vs 0.15). LLaVA is weaker on both (0.45 and 0.03). With three points this is a direction, not a test.
- **Steering test (v2, 2B only):** adding a refusal direction at layer 16 raises vision refusal from 0.125 to 0.77 at strength 0.5, while text refusal goes from 0.58 to 0.80. A random direction does nothing. Both channels respond together, not oppositely. The cost is over-refusal on benign text, 0.375 at strength 0.5 (n = 24, so rough).
- Conclusion for the advisor: raising safety in one channel does not lower it in the other. The better story is "the channels are tied together by one refusal mechanism, and the benchmark's wrapper plus image presence distort how much of it each channel shows."

## 5. The main findings in detail (v6, three labellers agree)

Qwen3Guard 3-way refusal; WildGuard gives the same picture within 0.02.

| Finding | 2B | 3B | LLaVA |
|---|---|---|---|
| Wrapper effect B - G_full (text, benchmark wrapper vs plain) | 0.32 | 0.19 | -0.05 |
| Image effect, plain wrapper (F_txt - F_img) | 0.32 | 0.07 | 0.53 |
| Image effect, mid wrapper | 0.03 | -0.13 | 0.37 |
| Image effect, strong wrapper (G_full - W2_img) | 0.06 | -0.37 | 0.49 |
| Plain text vs irrelevant image (B - B_noise / B_nat / B_irr) | 0.00 / 0.07 / 0.03 | -0.05 / -0.06 / -0.06 | 0.38 / 0.37 / 0.39 |
| Blank image alone (B - D) | -0.11 | -0.02 | 0.40 |
| Over-refusal on benign text (Bben) | 0.17 | 0.19 | 0.04 |

1. **Wrapper:** For the Qwen models, the benchmark's imperative "list steps" wrapper lowers refusal by 0.19 to 0.32 even when the content is typed text. The wrapper x modality interaction is large and significant (log odds ratio 1.1 to 2.6, p below 1e-12 for both Qwen models).
2. **Qwen image effect depends on the wrapper:** for the 2B it is real only under the plain instruction (0.32) and vanishes under stronger wrappers; for the 3B the image is neutral under plain and actually safer under the strong wrapper.
3. **LLaVA is a different mechanism:** any image, even random noise or an irrelevant photo, drops refusal from 0.45 to about 0.07, while unsafe-output rates rise to 0.7 or more (0.39 for plain text). The "typographic" effect there is image presence, and the typed content hardly matters.
4. **FigStep (second benchmark, 200 items) replicates the wrapper finding:** the text twin of FigStep's own wrapper recovers about 95% (2B), 136% (3B) and 121% (LLaVA) of the image-attack gap. For LLaVA this differs from MM-SafetyBench, where image presence drives it: worth explaining in the paper.
5. **Refusal and harm are different:** the 2B under the benchmark wrapper has refusal 0.15 and unsafe rate 0.56; the 3B under the strong wrapper refuses 0.92 and is unsafe 0.02.
6. **Legibility is not the story:** Qwen reads typed phrases at 12 px nearly perfectly (read-back 0.99); LLaVA reads only 46% at 12 px and 86% at 20 px.

## 6. Caveats and what is NOT established

- v3's decomposition shares depend on path order (Cmp + R = E - C identity), "no effect" claims need equivalence tests, and v5's neutral-image block was invalid because replies were judged against the full harmful question rather than the stimulus (fixed in v6; v6 H26 on re-labelled v5 replies is inconclusive because the labels are near-constant).
- No human audit yet (360 rows in `vlm_tradeoff_out_v6/audit_v6_blinded.csv`, 60-row retest, rubric fixed). Until it is done every label-based number is "guard-labelled", not validated.
- Only three small, older models (Qwen2-VL-2B, Qwen2.5-VL-3B, LLaVA-1.5-7B) and two benchmarks (MM-SafetyBench, FigStep). No 7B+ modern VLM (Qwen2.5-VL-7B is wired but off), no non-Qwen non-LLaVA family.
- Greedy decoding only; English only; 8 scenario clusters (smallest possible sign-test p is 0.0078).
- No confirmatory run: every hypothesis was set after reading earlier data (see the deviation log).
- No mitigation beyond the v2 steering result on one model.
- Prior work position: MMJailBench (second-hand abstract) is the closest paper and found that framing dominates. Our added value is the controlled grid, the presence controls, the FigStep replication and the labeller-validity analysis. Citations need verification before submission.

## 7. Is this publishable, and where

**Honest read:** a clean, well-controlled measurement paper with a strong negative result on the see-saw and a corrected account of the typographic gap. That is a respectable workshop or Findings paper. For a main-conference slot at ACL/EMNLP it needs something reviewers read as "more than a careful re-analysis": a mechanism or an actionable fix, and breadth in models.

| Target | Deadline | What it needs on top of today |
|---|---|---|
| Workshop on multimodal / trustworthy AI | about 20 Nov 2026 | Human audit (360 rows, plus 1-day retest), a third model family, a fresh-items confirmatory rerun of the 6 key contrasts, 4 to 6 page write-up |
| ACL 2027 via ARR | 4 Jan 2027 | All of the above plus 4 to 6 models including a 7B+ modern VLM, a mechanism/mitigation section, a recommended matched-control protocol for benchmark authors |
| TMLR (fallback) | rolling | Same as ACL, longer; stronger on rigour than novelty, which suits this paper |

**Proposed title direction:** "Is the typographic gap in VLM safety benchmarks about the image? Wrapper, presence and measurement controls." Contribution list: (1) a matched-control protocol (text twin with the same wrapper, irrelevant-image control, stimulus-aware labelling); (2) evidence that the gap is mostly wrapper for Qwen and image presence for LLaVA; (3) no see-saw; (4) a labeller-validity analysis showing rubric LLM judges and non-stimulus-aware guards give misleading refusal rates.

## 8. Remaining work, in order

1. **Human audit** of `audit_v6_blinded.csv` (about 4 to 6 hours). **Update 2026-10-18:** Claude labelled all 360 rows blind to the key as an LLM annotator (local, git-ignored, `audit_work/`). It agrees with WildGuard at 0.90 (kappa 0.79) and the keyword rule at 0.92 (kappa 0.82), but Qwen3Guard only at 0.85 (kappa 0.70); on the 231 rows Claude did not flag as borderline, kappa is 0.91 (WildGuard), 0.94 (keyword) and 0.85 (Qwen3Guard). The NOT_COMPREHEND rule has about 53% precision and 31% recall. That is a second annotator, **not** a human audit: a person still has to label at least the 129 borderline rows before the paper can say "human-validated". Retest 60 rows one day later. Then Rogan-Gladen calibration of each labeller from the audit. This is the gate for everything.
2. **v7 run (about 10 to 12 h on Colab):** add a third family (SmolVLM2, InternVL or Gemma-3 are candidates, none tested) and turn on Qwen2.5-VL-7B (flag exists, off). Keep the v6 design frozen.
3. **Mechanism/mitigation (cheap, no training):** extend the v2 steering to the 3B and the third family, plus a refusal-direction comparison between text and image inputs, to ground the "one shared mechanism" claim. Report over-refusal cost.
4. **Confirmatory run:** fresh item draw (not the 304 already read), the 6 pre-specified contrasts, written into an Amendment 5 before it runs.
5. **Sampling robustness:** a small temperature-sampled rerun with several seeds for the main contrasts.
6. **Writing:** paper skeleton, figures in the style of `fig_v6_contrasts.png`, ethics statement (no prompts, images or replies released), verified citations.

Rough schedule to hit 20 Nov: audit this week; v7 and mechanism the next week; confirmatory run and write-up in the following two weeks. It is tight but possible if the audit starts now.

## 9. Housekeeping that still matters

- Do not commit `audit_*`, `gen_*.jsonl` or `*PRIVATE*` (repo is public; `.gitignore` already blocks them).
- v1 folders in the public history contain raw replies from the first commit; removing them from history needs an explicit decision.
- v5's "stale smoke audit" files in `v5_full/` are leftovers; the real 240-row v5 audit is on Drive.
- Unified Drive folder `VLM_Safety_Project` holds shortcuts to all 19 project items (notebooks, result folders, bundles); nothing is shared with any other account yet.
