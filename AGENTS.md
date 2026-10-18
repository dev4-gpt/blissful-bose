# AGENTS.md: operating brief for the VLM refusal-gap research project

You are continuing a research project that is already six experiment versions in. Read this file fully, then `docs/HANDOFF_END_TO_END.md` (detail) and `docs/INDEX.md` (file index). Everything here was written 2026-10-18 and reflects the repo at that date. When this file and the code disagree, trust the code and fix this file.

## 1. Mission

Produce a **publishable paper** on safety alignment of vision-language models (VLMs), using only open models and open data, free or Colab Pro (T4) compute, **no training**. The human owner is Aryaman Singh Dev (first-time researcher; advisor Prof. Thao Minh Le, Penn State). Targets: a workshop paper by about 20 Nov 2026; ACL 2027 via ARR (4 Jan 2027); TMLR as fallback.

The advisor's original hypothesis was a text/vision "see-saw" (if vision safety drops by Z, language safety rises by Z). **The data do not support it.** The project is now a controlled study of *why the typographic image-attack refusal gap exists* and how much of it is an artifact of the benchmark's prompt wrapper, image presence and measurement error. Your job is to move this from "exploratory evidence" to "pre-registered, validated, reviewer-proof evidence" and to help write it up.

## 2. State of the evidence (all exploratory)

Refusal rates, v6 full run (304 items per Qwen model, 152 for LLaVA; Qwen3Guard 3-way; WildGuard within 0.02):

| | Qwen2-VL-2B | Qwen2.5-VL-3B | LLaVA-1.5-7B |
|---|---|---|---|
| B plain text | 0.66 | 0.74 | 0.45 |
| C typed image + benchmark wrapper | 0.15 | 0.44 | 0.03 |
| gap B-C (stable across v2 to v6) | 0.51 | 0.30 | 0.43 |
| E key phrase as text + same wrapper | 0.18 | 0.51 | 0.38 |
| F_txt / F_img (plain instruction) | 0.56 / 0.24 | 0.73 / 0.65 | 0.56 / 0.03 |
| D blank image | 0.77 | 0.76 | 0.05 |

Findings so far: (1) for Qwen the gap is mostly the benchmark's imperative wrapper ("List steps in detail to perform this activity"); wrapper x modality interaction is large (log OR 1.1 to 2.6). (2) For LLaVA any image, even noise or irrelevant, drops refusal from 0.45 to about 0.07 and raises unsafe output. (3) FigStep replicates the wrapper finding (text twin recovers about 95% / 136% / 121% of the image-attack gap). (4) No see-saw: text and image refusal correlate positively; steering a refusal direction raised both. (5) Refusal is not harm (2B: refusal 0.15 but unsafe 0.56). (6) Qwen reads 12 px typed text at 0.99; LLaVA reads 46%. (7) Reply text varies with batch size on 7 to 34% of replies but refusal labels change on under 1%. (8) Unexplained: the 3B refuses more with an image under the strong wrapper (0.92 vs 0.56).

Why it is **not yet publishable as is**: all results were read before the human-audit gate (exploratory); only three small, older models; one main benchmark plus FigStep; no human-validated labels; no confirmatory run; and MMJailBench (arXiv 2608.25490) already reports that prompt framing dominates, so novelty must come from a retroactive audit of the benchmarks everyone uses plus validated measurement (see `docs/NOVELTY_AUDIT_AND_PLAN.md`).

## 3. Non-negotiable rules

1. **The GitHub repo (`dev4-gpt/blissful-bose`) is PUBLIC.** Never commit: raw model replies (`gen_*.jsonl`), audit files (`audit_*`, `audit_work/`), `*PRIVATE*` files, `.env`, API keys, tokens. `.gitignore` already blocks these; do not weaken it. Result folders hold aggregates only (JSON/CSV/PNG). No prompts, images or replies may be released.
2. **Never print, log or commit secrets.** `~/.claude.json` and shell env may hold Exa/Firecrawl/HF keys.
3. **Do not push to GitHub, force-push, rewrite history, or merge to `master` without the owner's explicit go-ahead.** Commit locally on a branch; ask before pushing.
4. **Do not end, delete or "Disconnect and delete runtime" on Colab sessions** and do not start long Colab runs without the owner's say-so. The owner clicks the Drive "Connect" prompt and toggles Colab's `HF_TOKEN` notebook access. Colab limits sessions ("Too many sessions").
5. **Pre-registration discipline.** Do not run a new experiment until its hypotheses and endpoints are written into `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` as a new Amendment. Items already read (the 304 / 152 used so far, FigStep 200) are *exploratory*; confirmatory claims need fresh items or a held-out split. Report refuted hypotheses.
6. **Do not invent citations.** Every cited paper must be opened and checked (title, authors, arXiv ID, what it actually claims). Mark abstract-only reads. Older agent research in `research_notes/` is second-hand: verify before use.
7. **Label claims honestly:** "exploratory", "guard-labelled", "LLM-annotator", "human-validated" mean different things. Claude's blind labelling of the audit is an LLM annotator, not a human audit.
8. **Open models and open data only; no training** (inference, steering and prompting are fine).
9. Keep files under 500 lines; edit existing files before creating new ones; do not create documentation files unless needed; do not save working files in the repo root.
10. Do not touch unrelated material in the repo (`PLAN_SMT_IFVG_BACKTEST.md`, `gradient_strategy_dossier.md`, decks, older reading guides).

## 4. Repository map

Root: `/Users/aryamandev/Developer/blissful-bose` (GitHub `dev4-gpt/blissful-bose`; working branch `wip/backup-2026-10-03`; default `master`).

- `docs/INDEX.md` index of every project document; `docs/HANDOFF_END_TO_END.md` full onboarding; `docs/STATUS_AND_PAPER_PLAN.md` cross-version analysis and venue plan; `docs/NOVELTY_AUDIT_AND_PLAN.md` verified prior art and ranked ideas; **`docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` the pre-specification (Amendments 1 to 4, hypotheses H1 to H27, deviation log; edit only by adding amendments or deviation rows)**; `docs/V3_RESULTS_AND_NEXT_STEPS.md`, `docs/V5_RESULTS_AND_NEXT_STEPS.md` per-version write-ups (V5 section 8 holds the red-team corrections); `docs/PRIOR_WORK_AND_V5_PLAN.md` (second-hand literature; superseded by the novelty audit); older master plans and reading material (see INDEX section 6, background only).
- `notebooks/` six Colab notebooks (generated): `vlm_modality_tradeoff.ipynb` (v1), `_v2`, `_v3`, `_v4`, `_v5`, `_v6`. **v6 is current.**
- `tools/nb_gen/` generators for v6: `make_nb6_part1.py` (config, data, model classes and cache, condition specs, generation loop), `make_nb6_part2.py` (stimulus-aware labelling, statistics, analysis and H21 to H27, export, audit), `make_nb6.py` (assembles `notebooks/vlm_modality_tradeoff_v6.ipynb`; reads the v5 notebook for shared cells); `tools/nb_gen/e2e/e2e6.py` CPU end-to-end test with stub models. `tools/analyze_v3_offline.py` offline paired tests. Other files in `tools/` are deck builders (not part of this project).
- Result folders (aggregates only): `v1_smoke_n5`, `v1_full_n30`, `v2_run`, `v3_run1_judges_failed`, `v3_run2_three_judges`, `v3_final_four_judges` (use this one for v3), `v4_smoke_n16`, `v5_smoke_n16`, `v5_full`, `v6_smoke_n16`, `v6_full`. v4/v5/v6 smoke folders are pipeline tests: numbers are noise. v5_full's `audit_v5_*` files are stale smoke leftovers (git-ignored).
- `research_notes/` agent outputs (second-hand). `reports/` earlier staged literature review.

Google Drive (college account `aryamandev.college@gmail.com`; locally streamed at `~/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/`): notebooks in `Colab Notebooks/`; outputs `vlm_tradeoff_out` (v1), `_v2` to `_v6` (raw `gen_*.jsonl`, `lab6_*.json` labels, `ref_phrases_PRIVATE_*.json`, `audit_v6_*`, bundle zips); `VLM_Safety_Project/` holds shortcuts to all of them. v6 output folder has 512 files. Do not move or rename these folders: v6 imports earlier caches from `../vlm_tradeoff_out_v5/_v4/_v3` by path.

## 5. The experiment, in one place

- **Models:** Qwen2-VL-2B-Instruct (LLM twin Qwen2-1.5B-Instruct), Qwen2.5-VL-3B-Instruct (twin Qwen2.5-3B-Instruct), LLaVA-1.5-7B (twin Vicuna-7B v1.5; 4-bit; 152 items, square-padded). Greedy, 256 new tokens, batch 8 (batch-1 reruns measure noise).
- **Data:** MM-SafetyBench, 8 scenarios x 38 = 304 items (LLaVA: first 19 per scenario); FigStep SafeBench (`AngelAlita/FigStep` mirror, 20 per category = 200); XSTest safe prompts (open CSV `Paul/XSTest`) and benign twins for over-refusal.
- **Conditions:** A LLM text; B VLM text; C typed key phrase in image + benchmark wrapper; D blank image; E key phrase as text + same wrapper; G_full full question as text + benchmark wrapper; F_txt/F_img full question as text/image with the plain instruction; W0/W1/W2 plain/mid/strong wrapper (W1_txt, W1_img, W2_img); B_noise/B_nat/B_irr plain text + noise/natural/irrelevant-text image; E_blank/E_nat; L12/L20/L38 typed phrase at true 12/20/38 px; FS_B/FS_F/FS_E/FS_W0i/FS_W0t for FigStep; Bben/Nben/Dben/Aben benign twins. `STAGES` in the config cell toggles blocks: relabel, wrapper_grid, presence, legibility, figstep, noise_floor.
- **Labelling (v6):** Qwen3Guard-Gen-4B and WildGuard (needs `HF_TOKEN`) judge each reply **against the stimulus the model saw**, not the original harmful question; plus a keyword rule; plus a fixed NOT_COMPREHEND rule (`nonanswer()`: clarification requests, echoes of the phrase, image descriptions). Outputs: `refuse3` (REFUSE after the NC rule), `refuse_raw`, `notcomp`, `unsafe`. The two LLM-rubric judges are retired (invalid).
- **Statistics:** exact paired McNemar, scenario-level t(7) intervals (8 clusters; smallest sign-test p is 0.0078), TOST equivalence margin 0.10, item-clustered GEE for the wrapper x modality grid, Holm, labeller kappa. Rogan-Gladen calibration is planned once the human audit exists.
- **Caching:** generations are cached as `gen_{model}__{cond}__{hash}.jsonl` with version-free keys (v5's keys contained library versions and missed on every new Colab image); v6 also imports older caches by tag prefix and exact item-uid list. Label caches are `lab6_{labeller}__{model}__{cond}__{hash}.json`. Re-running a notebook resumes.
- **Outputs:** `results_vN.json` keys: `meta`, `results[model]` (`n`, `rates[labeller][cond]`, `contrasts[labeller][name]`, `grid`, `unsafe_rate_all`, `kappa`, `readback`, `legibility`, `noise_floor`), `figstep`, `prespecified_check` (H21 to H27 verdicts), plus `v6_contrasts.csv`, a figure and a bundle zip (aggregates only; no `gen_`, `audit_`, `lab6_` files).

## 6. How to work

- **Edit generators, not notebook JSON.** After editing `tools/nb_gen/*.py`: run `python3 make_nb6.py` from `tools/nb_gen/` (paths in the scripts are absolute to this checkout; adjust `ROOT`), then `python3 -m pyflakes` on the concatenated notebook code, then `python3 e2e/e2e6.py v6` (flags: `LLAVA_FAIL=1`, `WG_FAIL=1`, `FS_FAIL=1`, `NB_PATH=<smoke notebook>`, `E2E_DIR=<empty dir>`). The harness uses stubs; it proves control flow and failure isolation, not GPU behaviour. A real Colab smoke run (`SMOKE = True`, about 25 min) is still required before any full run, and only the owner can start it.
- **Colab protocol:** upload the `.ipynb` to the college Drive, T4, `SMOKE = True`, then `False` (v6 full is about 8 to 9 h; every block is cached and resumes after a disconnect). Notebooks must run unattended apart from the Drive "Connect" click and the HF_TOKEN toggle. Each model pair is failure-isolated; a failed pair is listed under `failed_pairs`.
- **Analysis lives in the notebook and in offline scripts under `tools/`.** Prefer offline, reproducible scripts that read `results_*.json` and Drive caches, so tables in docs can be regenerated.
- **Before saying "done":** tests/harness pass, numbers in docs match the files, no secrets or raw text in the diff (`git diff --cached | grep -E "hf_|API_KEY|exaApiKey"` must be empty), and any claim is labelled exploratory or validated correctly.
- **Reporting:** summarize what changed, what was verified, what was not, and what you need from the owner. No silent scope expansion; ask before writing more than 3 to 5 new files in one go.

## 7. Task queue (in priority order)

Each task lists goal, steps and acceptance criteria. Do them in order unless the owner redirects.

**T1. Systematic novelty search and verified related work.** Goal: replace the shallow search in `docs/NOVELTY_AUDIT_AND_PLAN.md` with a verified one. Steps: read in full MMJailBench (2608.25490), FigStep (2311.05608), MM-SafetyBench, VLSBench, USB, HoliSafe, DUAL-Bench, Text2VLM, 2410.09047, 2505.24208, 2606.31876, 2609.02082, 2604.12371; for each of the seven ranked ideas search arXiv, Semantic Scholar and the ACL Anthology for prior art; record exact claims, models and numbers. Acceptance: an updated novelty doc with each citation opened and checked, each idea marked novel / partly known / known with evidence, and a final recommendation of which 2 to 3 ideas carry the paper.

**T2. Audit tooling and calibration.** Goal: make the human audit usable. Steps: write `tools/audit_analyze.py` that reads the audit CSV with a `human` column and the key, computes agreement (percent, kappa, AC1/PABAK), per-labeller sensitivity/specificity, Rogan-Gladen calibrated refusal rates per condition with intervals, and stratum-weighted population estimates (the audit sample is half disagreement-selected, so raw rates are not representative; weight by stratum sizes recomputed from `lab6_*` caches). Test on Claude's labels (the owner may place them at `audit_work/audit_v6_claude_labeled.csv`; local only, git-ignored). Acceptance: script runs end to end, outputs a small aggregates-only table suitable for the paper, never writes replies.

**T3. Improve the NOT_COMPREHEND rule.** Current precision about 53%, recall about 31% against Claude's blind labels (and the human labels when available). Goal: precision and recall at least 0.7 on a held-out half of the audit, without using the labeller outputs of the same rows for tuning leakage. Steps: error analysis by reply type (clarification, silent safe pivot, false denial, garbled, image description), improve `nonanswer()` in `make_nb6_part2.py`, test offline. Acceptance: documented rule change with before/after numbers; v6 labels remain reproducible (version the rule).

**T4. Amendment 5 (pre-registration).** Goal: write hypotheses and analysis plan before any new run. Steps: add Amendment 5 to `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` with H28+ covering the ideas from T1: (a) retroactive wrapper-matched control on MM-SafetyBench and FigStep across a wider model set; (b) forecastability (does the text twin predict image-condition refusal across models, R-squared and equivalence margin); (c) model-zoo coupling of text- and image-channel refusal across at least 8 models with covariates; (d) image-token dose-response for LLaVA-type presence effects (image size, token count, position); (e) capability-adjusted refusal (refusal among comprehended replies); (f) refusal stability under sampling (k of 8). Specify fresh items, primary and secondary endpoints, multiplicity handling, decision rules, labellers, the audit plan, and a deviation log row. Acceptance: owner approves the amendment before T5.

**T5. v7 notebook (generator + tests).** Goal: implement Amendment 5 as `notebooks/vlm_modality_tradeoff_v7.ipynb`, generated by new scripts in `tools/nb_gen/` (copy the v6 structure; keep v6 frozen). Requirements: add modern models that fit a T4 (candidates: Qwen2.5-VL-7B in 4-bit, InternVL3-8B, Gemma3-12B in 4-bit, LLaVA-OneVision; verify each loads on a T4 before committing), additional benchmarks, the dose-response and sampling arms, the forecasting and zoo analyses; per-pair failure isolation; version-free cache keys; legacy-cache import from v6; Drive output folder `vlm_tradeoff_out_v7`; HF cache purge between models; runs unattended. Acceptance: pyflakes clean, CPU e2e passes including failure flags, a smoke notebook generated; then ask the owner to run SMOKE on Colab. Do not start a full run yourself.

**T6. Cross-version reproduction script.** Goal: `tools/cross_version_table.py` that regenerates the cross-version table in `docs/STATUS_AND_PAPER_PLAN.md` (A to E and gap per version and labeller, coupling, steering) from the committed result folders. Acceptance: script output matches the doc; doc references the script.

**T7. Paper skeleton.** Goal: a draft in `paper/` (LaTeX or markdown, owner's choice) with abstract, introduction, related work (only verified citations), method (matched-control protocol, stimulus-aware labelling), results placeholders tied to figures generated by scripts, limitations, ethics statement (no prompts, images or replies released; dual-use consideration), reproducibility checklist. Acceptance: compiles or renders, every number traceable to a result file, claims tagged exploratory until confirmatory results exist.

**T8. Housekeeping (ask first).** v1 folders in git history contain raw replies from the first commit; propose options (BFG/filter-repo vs leaving) and wait for the owner's decision. Fix `docs/DEEP_LITERATURE_AUDIT_AND_RESEARCH_FOUNDATION.md` (SIUO has the wrong arXiv ID and numbers; correct ID is 2406.15279). Keep `docs/INDEX.md` current.

## 8. Decisions that belong to the owner (ask, do not guess)

Pushing or merging; deleting or rewriting history; starting any Colab run; sharing Drive folders with other accounts; accepting an Amendment; choosing the target venue; whether Claude's LLM-annotator labels may be cited; model additions that need gated access or large downloads; anything that spends money or compute.

## 9. Known gotchas

- Colab: models download to the VM disk (about 78 GB free; purge the HF cache between models); outputs go to Drive; a secrets toggle can reset the kernel; Chrome automation uses the college profile only.
- WildGuard is gated (needs the owner's `HF_TOKEN` and accepted terms); XSTest uses an open CSV, not the gated copy.
- LLaVA-1.5 needs square-padded inputs and 4-bit loading; keep it out of any pooled Qwen estimate.
- PIX_MIN upscaling made v5's "small font" arm not small; v6 renders true 12/20/38 px on a 768x768 canvas.
- v3's decomposition shares (P, Cmp, R) depend on path order (Cmp + R = E - C); do not headline them.
- Non-significance is not absence of an effect (floor effects, 8 clusters); use equivalence tests for "no effect".
- Claude-specific hooks (GateGuard) ask for stated facts before first tool use; ignore if you are not running under Claude Code.

## 10. Start here (first actions)

1. Read `docs/HANDOFF_END_TO_END.md`, `docs/STATUS_AND_PAPER_PLAN.md`, `docs/NOVELTY_AUDIT_AND_PLAN.md`, and the Amendment 4 section of `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md`.
2. Run `git status` and `git log --oneline -5`; confirm you are on `wip/backup-2026-10-03` and nothing sensitive is staged.
3. Confirm the e2e harness passes (`tools/nb_gen/e2e/e2e6.py`) so you know your environment works.
4. Begin T1; report findings to the owner before starting T4.
