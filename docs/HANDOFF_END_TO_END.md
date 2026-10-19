# End-to-end handoff: the VLM refusal-gap project (2026-10-18)

**Later October 18 review supersedes the positioning and schedule below:** read `docs/STATUS_AND_PAPER_PLAN.md` and `docs/NOVELTY_AUDIT_AND_PLAN.md` first. FigStep already has its Q2-prime text control (Section 6.4); MMJailBench already has mismatch-conditioned ASR. Cross-version judge agreement is not uniform. Amendment 5 is approved and v7 benign compatibility testing is underway, with no v7 scientific result yet. The local audit still has zero human labels. ARR lists January 2027 without a verified exact day. Use the current review's generated tables and scope limits.

Read this first. It explains the goal, what exists in the repo and on Google Drive, how to run and regenerate everything, what the results are, what is still open, and the rules to follow. Companion docs: `docs/STATUS_AND_PAPER_PLAN.md` (cross-version results and the venue plan), `docs/NOVELTY_AUDIT_AND_PLAN.md` (verified prior art and ranked ideas), `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` (the pre-specification), `docs/INDEX.md` (file index).

## 1. Goal and who is doing it

A first-time researcher (advisor: Prof. Thao Minh Le, Penn State) wants a **publishable paper** on safety alignment of vision-language models (VLMs), using only open models and open data, free or Colab Pro (T4) compute, **no training**. Targets: a workshop paper by about 20 Nov 2026; ACL 2027 via ARR (4 Jan 2027); TMLR as fallback.

The advisor's starting hypothesis was a **text/vision "see-saw"**: safety alignment in the language modality and the vision modality trade off (if vision safety drops by Z, language safety rises by Z). **The data do not support it** (section 6). The project has since become a controlled study of *why the typographic image-attack refusal gap exists*.

## 2. The scientific question as it stands now

On MM-SafetyBench, models refuse harmful requests much less when the key phrase is typed into an image than when the same request is plain text. The "typographic gap" (plain text refusal minus image refusal) is 0.51 / 0.30 / 0.43 for Qwen2-VL-2B / Qwen2.5-VL-3B / LLaVA-1.5-7B. Question: **is that gap about the image modality, the benchmark's prompt wrapper ("List steps in detail to perform this activity"), image presence, or measurement error?** Answer so far (exploratory): mostly the wrapper for Qwen, image presence for LLaVA, and text and image refusal move together.

## 3. Setup and constraints

- **Models** (all open, greedy decoding, 256 new tokens): Qwen2-VL-2B-Instruct (backbone Qwen2-1.5B-Instruct), Qwen2.5-VL-3B-Instruct (backbone Qwen2.5-3B-Instruct), LLaVA-1.5-7B (backbone Vicuna-7B v1.5; 4-bit; 152 items, square-padded input).
- **Data:** MM-SafetyBench (8 scenarios x 38 items = 304; LLaVA uses the first 19 per scenario = 152), FigStep SafeBench (`AngelAlita/FigStep` mirror, 200 items = 20 per category), XSTest safe prompts and benign twins for over-refusal.
- **Labellers:** Qwen3Guard-Gen-4B, WildGuard (`allenai/wildguard`, gated: needs an `HF_TOKEN`), and a keyword rule. Two LLM-rubric judges (Qwen3-4B, Qwen2.5-3B) were **invalid** (84 to 90% REFUSE in every condition) and are retired.
- **Compute:** Colab Pro T4. Models download to the VM disk (about 78 GB); outputs go to Google Drive. Colab session limit is real ("Too many sessions").
- **Stats:** exact paired McNemar, scenario-level t(7) intervals (8 clusters; smallest sign-test p is 0.0078), item-clustered GEE logit, TOST equivalence (margin 0.10), Holm, Rogan-Gladen calibration once the human audit exists.

## 4. Conditions (v6 vocabulary)

A = LLM backbone, plain text. B = VLM, plain text. C = key phrase typed in an image + the benchmark wrapper. D = blank image. E = key phrase as *text* + the same wrapper. G_full = full question as text with the benchmark wrapper. N = neutral variants. F_txt / F_img = full question as text / as an image, plain instruction ("Answer the question given below/in the image"). W0/W1/W2 = plain / mid / strong wrapper; W1_txt, W1_img, W2_img etc. B_noise / B_nat / B_irr = plain text + noise / natural / irrelevant-text image. E_blank / E_nat = E plus blank/natural image. L12/L20/L38 = key phrase rendered at true 12/20/38 px. FS_B / FS_F / FS_E / FS_W0i / FS_W0t = FigStep plain text / own image + wrapper / text twin / plain instruction image / text. Bben/Nben/Dben/Aben = benign twins for over-refusal.

## 5. The experiment ladder (what each version did)

| Ver | Notebook (in `notebooks/`) | Result folder (repo) | What it did | Status |
|---|---|---|---|---|
| v1 | `vlm_modality_tradeoff.ipynb` | `v1_smoke_n5`, `v1_full_n30` | Pilot A-D, coupling, refusal-direction steering | Low trust (invalid judge, different stimulus). Raw replies are in git history (see section 10) |
| v2 | `..._v2.ipynb` | `v2_run` | Stricter judge, benign twins, E; steering on the 2B | Gap OK, labels unreliable. Read for the first time on 2026-10-18 |
| v3 | `..._v3.ipynb` | `v3_final_four_judges` (+ run1/run2) | Gap decomposition G = P + Cmp + R, read-back of typed phrase, 5 labellers, judge-free prefix score | Medium-high; decomposition is path-dependent |
| v4 | `..._v4.ipynb` | `v4_smoke_n16` | Factorial wrapper x content x modality, LLaVA, harm, XSTest | Smoke only, superseded |
| v5 | `..._v5.ipynb` | `v5_full`, `v5_smoke_n16` | v4 + noun-phrase, bare phrase, font size, interaction, Holm, audit files | Neutral-image block invalid (judged against the full question, not the stimulus) |
| v6 | `..._v6.ipynb` | `v6_full`, `v6_smoke_n16` | Stimulus-aware 3-way labels, wrapper grid W0/W1/W2, presence controls, true-size legibility, FigStep, noise floor, 360-row audit | Best so far, exploratory |

Pre-specification: `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` has Amendments 1 to 4 (H1 to H27) and a deviation log. All results so far were read before the human-audit gate, so they are **exploratory**; a confirmatory run on fresh items is still required.

## 6. Results (v6 full, Qwen3Guard 3-way; WildGuard within 0.02)

Refusal rates (selected):

| Condition | 2B | 3B | LLaVA |
|---|---|---|---|
| A (backbone text) | 0.72 | 0.79 | 0.55 |
| B (VLM text) | 0.66 | 0.74 | 0.45 |
| C (typed image + wrapper) | 0.15 | 0.44 | 0.03 |
| D (blank image) | 0.77 | 0.76 | 0.05 |
| E (phrase as text + wrapper) | 0.18 | 0.51 | 0.38 |
| G_full | 0.35 | 0.56 | 0.51 |
| F_txt / F_img (plain instruction) | 0.56 / 0.24 | 0.73 / 0.65 | 0.56 / 0.03 |
| W1_txt / W1_img | 0.57 / 0.54 | 0.74 / 0.87 | 0.44 / 0.07 |
| W2_img (strong wrapper, image) | 0.28 | 0.92 | 0.02 |

Cross-version stability of the gap B-C: 2B 0.51 to 0.54, 3B 0.30 to 0.31, LLaVA 0.42 to 0.44 across v2, v3, v5, v6 and across labellers. The judge-free prefix score (v3) agrees.

Findings: (1) **Wrapper effect for Qwen**: the benchmark wrapper lowers refusal 0.19 to 0.32 even for typed text; wrapper x modality interaction is large (log OR 1.1 to 2.6, p below 1e-12). (2) **LLaVA**: any image, even noise or irrelevant, drops refusal from 0.45 to about 0.07 and raises unsafe output (0.39 text vs 0.72 to 0.75 with irrelevant images). (3) **FigStep replicates the wrapper finding**: the text twin recovers about 95% (2B), 136% (3B), 121% (LLaVA) of the image-attack gap. (4) **No see-saw**: text and image refusal correlate positively (item phi 0.24 to 0.54; scenario Spearman 0.73 to 0.90 in v1/v2); the stronger model is better in both channels; steering the 2B raises both channels together (image 0.125 to 0.77 at strength 0.5, text 0.58 to 0.80; over-refusal cost 0.375 on 24 benign items). (5) **Refusal is not harm**: 2B refusal 0.15 vs unsafe 0.56 under the benchmark wrapper; 3B with the strong wrapper refuses 0.92 and is unsafe 0.02. (6) **Legibility is not the story for Qwen** (reads 12 px at 0.99); LLaVA reads 46% at 12 px. (7) Reply text changes on 7 to 34% of replies across batch sizes but the refusal label changes on under 1%. (8) The 3B refuses *more* with an image under the strong wrapper (0.92 vs 0.56): unexplained.

Pre-specified verdicts (Amendment 4, H21 to H27): H21 false, H22 SPLIT, H23 true, H24 false, H25 true, H26 inconclusive, H27 false. See `v6_full/results_v6.json` (`prespecified_check`) and `docs/STATUS_AND_PAPER_PLAN.md`.

## 7. Human audit (the gate)

`vlm_tradeoff_out_v6/audit_v6_blinded.csv` (Drive) has 360 rows (12 per cell x 10 conditions x 3 models, half selected by labeller disagreement), a 60-row retest, a fixed rubric (REFUSE / COMPLY / NOT_COMPREHEND, judged against the stimulus the model saw). On 2026-10-18 Claude labelled all 360 rows blind to the key (an **LLM annotator, not human**): agreement with WildGuard 0.90 (kappa 0.79), keyword 0.92 (0.82), Qwen3Guard 0.85 (0.70); on non-borderline rows kappa 0.91 / 0.94 / 0.85. Qwen3Guard over-counts refusals on non-answers and silent pivots; WildGuard under-counts soft refusals; the NOT_COMPREHEND rule has about 53% precision and 31% recall. Still needed: a person labels the 129 borderline rows and the retest. Those files are local and git-ignored (`audit_work/`, `audit_*`).

## 8. Where things live

Repo (`/Users/aryamandev/Developer/blissful-bose`, GitHub `dev4-gpt/blissful-bose`, **public**; branch `wip/backup-2026-10-03`, default `master`):
- `docs/` plans, results write-ups, literature (see `docs/INDEX.md`); `research_notes/` agent outputs (second-hand, verify before citing).
- `notebooks/` the six Colab notebooks (generated, see section 9); `tools/` offline analysis (`analyze_v3_offline.py`) and generators (`tools/nb_gen/`).
- Result folders `v1_*` to `v6_*` hold **aggregates only** (JSON, CSV, figures).
Google Drive (college account `aryamandev.college@gmail.com`): notebooks in `Colab Notebooks/`; outputs in `vlm_tradeoff_out`, `_v2` to `_v6` (raw `gen_*.jsonl`, `lab6_*.json`, audit files, bundle zips); unified folder `VLM_Safety_Project` holds shortcuts to all of them. Locally the Drive streams at `~/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/` (Drive for Desktop, stream mode).

## 9. How to run and regenerate

- **Run on Colab:** upload the `.ipynb` to the college account's Drive, T4 runtime, set `SMOKE = True` first (about 25 min), then `False` (about 8 to 9 h for v6; every block is cached, so re-running resumes). Needs the `HF_TOKEN` Colab secret with Notebook access (WildGuard) and the Drive "Connect" click. The v6 cache keys are version-free; v6 also imports earlier caches by tag and exact item list.
- **Notebooks are generated.** Edit the generators, not the JSON: `tools/nb_gen/make_nb6_part1.py` (header, config, data, model classes + cache, conditions, generation loop), `make_nb6_part2.py` (stimulus-aware labelling, statistics, analysis and H21-H27, export, audit), `make_nb6.py` (assembles `notebooks/vlm_modality_tradeoff_v6.ipynb`; it reads the v5 notebook for shared cells). Run `python3 make_nb6.py` from `tools/nb_gen/` after editing. `ROOT` in the scripts is the absolute repo path; adjust if needed.
- **Test without a GPU:** `tools/nb_gen/e2e/e2e6.py` runs the real notebook cells on CPU with stub models and fake data (`python3 e2e6.py v6`; env flags `LLAVA_FAIL`, `WG_FAIL`, `FS_FAIL`, `NB_PATH`, `E2E_DIR`). Always run it plus `pyflakes` after changing a generator. It does not replace a real Colab smoke run.
- **Analyse offline:** the notebooks export `results_vN.json` and bundles; unpack bundle zips into a new `vN_*` folder (aggregates only).

## 10. Rules and gotchas (important)

- The repo is **public**. Never commit `audit_*`, `gen_*.jsonl`, `*PRIVATE*`, `.env` or any key (`.gitignore` blocks the first three). No prompts, images or model replies may be released. Known leak: v1 folders in git history contain raw replies from the first commit; removing them needs an explicit decision.
- Do not push, end Colab sessions, "Disconnect and delete runtime", or touch cluster resources without the user's explicit go-ahead. The user does the Colab Drive-connect click and the `HF_TOKEN` toggle (an agent has granted HF_TOKEN access in-notebook at the user's request).
- Local hooks (GateGuard) ask for stated facts before the first Bash/Write/Edit; state the instruction and what the command does, then retry.
- Never print API keys; `~/.claude.json` holds Exa and Firecrawl keys.
- Keep findings labelled exploratory until the human audit and a confirmatory run exist; report refuted hypotheses.

## 11. What is next (ordered)

1. Human audit (user) of borderline rows + retest; Rogan-Gladen calibration.
2. Systematic novelty search (Firecrawl and Exa are now configured) for the ranked ideas in `docs/NOVELTY_AUDIT_AND_PLAN.md`: wrapper-matched control as an evaluation standard, a model-zoo test of the see-saw, forecasting image-attack refusal from the text twin, image-token dose-response, capability-adjusted refusal. Read MMJailBench (arXiv 2608.25490), FigStep and MM-SafetyBench fully; MMJailBench already reports framing dominance, so position ours as a retroactive audit of the benchmarks everyone uses.
3. Write Amendment 5 (pre-register models, benchmarks, endpoints, fresh items) before any new run.
4. v7: add modern models that fit a T4 (Qwen2.5-VL-7B, InternVL3-8B, Gemma3-12B 4-bit, LLaVA-OneVision), more benchmarks, token dose-response, sampled-decoding stability; keep the v6 design frozen.
5. Confirmatory run, analysis, paper draft (ethics statement, verified citations).
