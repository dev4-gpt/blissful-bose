# Index: modality-safety paper project (VLM refusal gap)

Last updated 2026-10-18 (paper-readiness review, verified novelty corrections and reproducible tables). This lists the files for the "is the typographic refusal gap a wrapper, content, or image effect?" project. Older reading material is listed at the end; unrelated work is excluded.

## 1. Start here (read in this order)

| # | File | What it is | Status |
|---|---|---|---|
| 000 | `AGENTS.md` (repo root) | **Operating brief for an AI agent (Codex)**: mission, rules, repo map, task queue T1 to T8 with acceptance criteria | current (2026-10-18) |
| 00 | `docs/HANDOFF_END_TO_END.md` | **Start here for a new agent or collaborator**: goal, files, how to run/regenerate, results, rules, next steps | current (2026-10-18) |
| 0b | `docs/NOVELTY_AUDIT_AND_PLAN.md` | Primary-source register, FigStep Q2-prime correction, scoped novelty assessment and outstanding searches | current; focused review, not completed systematic T1 |
| 0c | `docs/METHODOLOGY_REVIEW_AND_UPGRADE_PLAN.md` | Expanded review and v7 design audit; companion novelty section 10 brings the inventory to 32 sources and proposes investigating text-led testing; section 8 adds analysis options and call budgets | current; proposals need approval before scientific use |
| 0 | `docs/STATUS_AND_PAPER_PLAN.md` | **Current plain-language end-to-end review**: reproduced results, tested/planned/recent models, human audit, paper structure and execution gates | current (2026-10-18) |
| 1 | `docs/V5_RESULTS_AND_NEXT_STEPS.md` | Historical v5 findings and validity corrections | superseded by v6 and current review for headline results |
| 2 | `docs/PRIOR_WORK_AND_V5_PLAN.md` | Literature position (MMJailBench is the closest paper), reviewer attacks and answers, OpenResearch decision, path to submission | current (second-hand citations: verify) |
| 3 | `research_notes/Project critique and v6 design/` | Red-team review of the whole project and a survey of other approaches (written 2026-10-16) | see folder |
| 4 | `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` | **Pre-specification**: H1-H34, Amendments 1-5, human gate and deviation log; Amendment 5 approved | authoritative; preserve approved hash; additions need an amendment/addendum |
| 5 | `docs/V3_RESULTS_AND_NEXT_STEPS.md` | Results of the 2-model v3 run, and the finding that two LLM-rubric judges were invalid | superseded by v5 for numbers; still the record of the judge failure |
| 6 | `docs/MASTER_PLAN_MODALITY_SAFETY_PAPER.md` | Early master plan: story, venues, ethics, deadlines | partly superseded |
| 7 | `docs/PAPER_ROADMAP_MODALITY_SAFETY.md` | Historical roadmap and venue targets | dates require official re-verification; see current review |
| 8 | `docs/PLAN_MODALITY_SAFETY_TRADEOFF.md` | The original experiment plan and the OpenResearch notes (section 7) | historical |
| 9 | `reports/VLM safety research gaps.md` | Staged literature review and the first proposal (decomposition idea), with a status note after v3 | historical, header note current |

## 2. Notebooks (Colab, one per experiment version)

| File | What it does | Run? |
|---|---|---|
| `notebooks/vlm_modality_tradeoff.ipynb` (v1) | Pilot: conditions A-D, activation steering | yes (n=5 smoke, n=30 full) |
| `notebooks/vlm_modality_tradeoff_v2.ipynb` | Stricter judge, benign twins, random items | yes; aggregates inspected, historical exploratory labels |
| `notebooks/vlm_modality_tradeoff_v3.ipynb` | Decomposition G = P + Cmp + R, read-back, judge ensemble | yes (`v3_final_four_judges/`) |
| `notebooks/vlm_modality_tradeoff_v4.ipynb` | Factorial: wrapper x content x modality, LLaVA, harm, XSTest | smoke only (superseded by v5) |
| `notebooks/vlm_modality_tradeoff_v5.ipynb` | v4 plus noun-phrase, bare phrase, font-size, interaction, Holm, audit files, failure isolation | **full run done** (`v5_full/`) |
| `notebooks/vlm_modality_tradeoff_v6.ipynb` | Stimulus-aware 3-way labelling (re-labels v5 replies), wrapper grid W0/W1/W2, presence controls, true-size legibility, FigStep replication, noise floor, H21-H27 (Amendment 4), 360-row audit | **full run done** (`v6_full/`, exploratory); smoke in `v6_smoke_n16/` |
| `notebooks/vlm_modality_tradeoff_v7.ipynb` | Approved Amendment 5 (H28-H34): eight-checkpoint panel, exact item caches/revisions, B/E/C and wrapper grid, presence/dose, read-back, eight sampling draws, private stratified audit | **implementation under validation**; benign synthetic smoke only by default. No v7 scientific results yet; T4 support must be checked per model |
| `notebooks/vlm_methodology_review.ipynb` | Literature-to-design companion with an executed synthetic example explaining weighted human/autorater auditing | CPU only; no Drive, model downloads, private data or experimental outcome |
| `notebooks/vlm_research_expanded.ipynb` | Approved one-model benign compatibility stage plus expanded analysis of actual frozen v6 aggregates, paired refusal transitions and scoring sensitivity, with editable explanations | Scientific collection remains gated; saved-results analysis is exploratory |
| `notebooks/continual_safety_vlm.ipynb` | Separate earlier project | not part of this one |

## 3. Result folders (aggregates only; raw replies are never committed)

| Folder | Contents |
|---|---|
| `v1_smoke_n5/`, `v1_full_n30/` | v1 pilot (committed earlier; contain raw replies from the first commit: see housekeeping) |
| `v2_run/` | v2 aggregates inspected; historical exploratory evidence (raw `gen_*` files are git-ignored) |
| `v3_run1_judges_failed/`, `v3_run2_three_judges/`, `v3_final_four_judges/` | v3 passes; `v3_final_four_judges/` is the one to use (+ `offline_analysis.json`) |
| `v4_smoke_n16/`, `v5_smoke_n16/` | 16-item pipeline tests: **numbers are noise** |
| `v6_smoke_n16/`, `v6_full/` | v6 aggregates (`results_v6.json`, `v6_contrasts.csv`, figure). `v6_full` is the full run, exploratory until the human audit; the 360-row audit is on Drive (`vlm_tradeoff_out_v6/`) |
| `v5_full/` | The full v5 run. `results_v5.json`, `v5_contrasts.csv`, `fig_v5_contrasts.png`, label files. The four `audit_v5_*` files in it are stale smoke leftovers (git-ignored): the real 240-row audit is on Drive (`vlm_tradeoff_out_v5/`) |

## 4. Code and tools

| File | Purpose |
|---|---|
| `tools/analyze_v3_offline.py` | Offline paired tests (exact McNemar, sign test, logistic GEE) on saved labels, no GPU |
| `tools/cross_version_table.py` | Reproduces v1/v2/v3/v5/v6 aggregate tables, coupling and steering; checks marked tables in current review; optional PNG/SVG plot; never exports nested response samples |
| `tools/nb_gen/make_nb7.py` | Generates the self-contained v7 notebook from approved plan, frozen v6 NC helpers and the two v7 modules; embeds plan/code hashes |
| `tools/vlm_audit_estimation.py` | Separate finite-population stratified difference-estimator prototype; numeric inputs only, explicit design/reference, variance and deterministic bounds, no unvalidated confidence interval |
| `tools/vlm_saved_analysis.py`, `tools/nb_gen/make_research_extension_nb.py` | Validate paired refusal tables and compute descriptive rule/guard sensitivity from frozen v6 aggregates; generate a combined notebook or an executable CPU analysis-only variant, with separate measurement JSON and editable explanations; no raw-cache access |
| `tools/nb_gen/vlm7_explanations.py` | Plain-English guide and editable text cell after each results block, aggregate-only automatic readout and post-run interpretation template; embedded by the generator |
| `tools/vlm7_core.py` | Exact atomic caches, pinned data/source verification plus OCR, development/reserved partition, paired and forecast analyses, private weighted-audit sample |
| `tools/vlm7_models.py` | Native Transformers adapters, FP16/NF4, actual image-token/order checks, guard parsing and resource measurements; no remote model code |
| `tools/nb_gen/e2e/e2e7.py` | CPU notebook-cell and failure tests; run with `python3 tools/nb_gen/e2e/e2e7.py`; stubs do not establish T4 compatibility |
| `tools/build_modality_safety_deck.py` | Builds `presentation/Modality_Safety_Pilot_Deck.pptx` from the v1 results |
| `presentation/Modality_Safety_Pilot_Deck.pptx` | The 13-slide pilot deck (v1 numbers, labelled pilot) |

## 5. Research notes (agent outputs, second-hand, verify before citing)

`research_notes/VLM safety research gaps/` (six scouts, stage-2/3 checks) and `research_notes/Prior work limits and v4 design/` (typo-attacks, wrapper-comprehension, judges-metrics, mechanisms-scoop, openresearch-eval).

## 6. Older paper-reading material (background, not the experiment)

`docs/DEEP_LITERATURE_AUDIT_AND_RESEARCH_FOUNDATION.md` (known errors: SIUO ID and numbers), `MASTER_PAPER_BY_PAPER_DEEP_DIVE_AND_PROPOSAL_VERIFICATION.md`, `MASTER_RESEARCH_COMPENDIUM.md`, `VLM_10_PAPER_*`, `VLM_PAPER_*`, `VLM_VERIFIED_PAPER_CHECKLIST.md`, `READING_GUIDE.md`, `PRESENTATION_CITED_WRITEUP.md`, `SPEAKER_SCRIPT_31_SLIDES.md`, `vlm_*` briefs, `methodology_comparison.md`, `sota_landscape_survey.md`, `reproducibility_blueprint.md`, `lit_review/`.

## 7. Housekeeping still open

1. The v1 folders in the public repo contain raw model replies (`gen_*.jsonl`); removing them from history needs an explicit decision.
2. `docs/DEEP_LITERATURE_AUDIT...` cites SIUO with the wrong arXiv ID and numbers (correct: 2406.15279).
3. Three PDFs in `presentation/paper_pdfs/` are the wrong papers; do not commit `Big Data Lab Cluster User Guide 2.pdf`.
4. The current 360-row audit still needs human labels and a next-day retest. V2 aggregates have been reviewed; no new commit or push was made during this review.
