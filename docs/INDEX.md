# Index: modality-safety paper project (VLM refusal gap)

Last updated 2026-10-16 (v6 notebook built). This lists every file that belongs to the "is the typographic refusal gap a wrapper, content, or image effect?" project, in the order you would read them. Older paper-reading material is listed at the end; unrelated work in the repo (`PLAN_SMT_IFVG_BACKTEST.md`, `gradient_strategy_dossier.md`) is not part of this project.

## 1. Start here (read in this order)

| # | File | What it is | Status |
|---|---|---|---|
| 000 | `AGENTS.md` (repo root) | **Operating brief for an AI agent (Codex)**: mission, rules, repo map, task queue T1 to T8 with acceptance criteria | current (2026-10-18) |
| 00 | `docs/HANDOFF_END_TO_END.md` | **Start here for a new agent or collaborator**: goal, files, how to run/regenerate, results, rules, next steps | current (2026-10-18) |
| 0b | `docs/NOVELTY_AUDIT_AND_PLAN.md` | **Verified prior-art check** (MMJailBench etc.), ranked novel ideas, what to add so reviewers cannot stop it | current (2026-10-18); abstract-level reads, search was shallow |
| 0 | `docs/STATUS_AND_PAPER_PLAN.md` | **Cross-version analysis v1 to v6**: what is stable, see-saw verdict, publishability and a dated plan | current (2026-10-18) |
| 1 | `docs/V5_RESULTS_AND_NEXT_STEPS.md` | Full results of the latest run (3 models, 16 conditions), what is valid, what is broken, hypothesis scorecard | current |
| 2 | `docs/PRIOR_WORK_AND_V5_PLAN.md` | Literature position (MMJailBench is the closest paper), reviewer attacks and answers, OpenResearch decision, path to submission | current (second-hand citations: verify) |
| 3 | `research_notes/Project critique and v6 design/` | Red-team review of the whole project and a survey of other approaches (written 2026-10-16) | see folder |
| 4 | `docs/ANALYSIS_PLAN_MODALITY_SAFETY.md` | **Pre-specification**: measurements, judge gate, hypotheses H1-H20, Amendments 1-3, deviation log | authoritative; edit only via the deviation log |
| 5 | `docs/V3_RESULTS_AND_NEXT_STEPS.md` | Results of the 2-model v3 run, and the finding that two LLM-rubric judges were invalid | superseded by v5 for numbers; still the record of the judge failure |
| 6 | `docs/MASTER_PLAN_MODALITY_SAFETY_PAPER.md` | Early master plan: story, venues, ethics, deadlines | partly superseded |
| 7 | `docs/PAPER_ROADMAP_MODALITY_SAFETY.md` | Paper roadmap and venue/deadline table | still useful for dates |
| 8 | `docs/PLAN_MODALITY_SAFETY_TRADEOFF.md` | The original experiment plan and the OpenResearch notes (section 7) | historical |
| 9 | `reports/VLM safety research gaps.md` | Staged literature review and the first proposal (decomposition idea), with a status note after v3 | historical, header note current |

## 2. Notebooks (Colab, one per experiment version)

| File | What it does | Run? |
|---|---|---|
| `notebooks/vlm_modality_tradeoff.ipynb` (v1) | Pilot: conditions A-D, activation steering | yes (n=5 smoke, n=30 full) |
| `notebooks/vlm_modality_tradeoff_v2.ipynb` | Stricter judge, benign twins, random items | yes (results in `v2_run/`, **unread**) |
| `notebooks/vlm_modality_tradeoff_v3.ipynb` | Decomposition G = P + Cmp + R, read-back, judge ensemble | yes (`v3_final_four_judges/`) |
| `notebooks/vlm_modality_tradeoff_v4.ipynb` | Factorial: wrapper x content x modality, LLaVA, harm, XSTest | smoke only (superseded by v5) |
| `notebooks/vlm_modality_tradeoff_v5.ipynb` | v4 plus noun-phrase, bare phrase, font-size, interaction, Holm, audit files, failure isolation | **full run done** (`v5_full/`) |
| `notebooks/vlm_modality_tradeoff_v6.ipynb` | Stimulus-aware 3-way labelling (re-labels v5 replies), wrapper grid W0/W1/W2, presence controls, true-size legibility, FigStep replication, noise floor, H21-H27 (Amendment 4), 360-row audit | **full run done** (`v6_full/`, exploratory); smoke in `v6_smoke_n16/` |
| `notebooks/continual_safety_vlm.ipynb` | Separate earlier project | not part of this one |

## 3. Result folders (aggregates only; raw replies are never committed)

| Folder | Contents |
|---|---|
| `v1_smoke_n5/`, `v1_full_n30/` | v1 pilot (committed earlier; contain raw replies from the first commit: see housekeeping) |
| `v2_run/` | v2 run, **results not read yet** (raw `gen_*` files are git-ignored) |
| `v3_run1_judges_failed/`, `v3_run2_three_judges/`, `v3_final_four_judges/` | v3 passes; `v3_final_four_judges/` is the one to use (+ `offline_analysis.json`) |
| `v4_smoke_n16/`, `v5_smoke_n16/` | 16-item pipeline tests: **numbers are noise** |
| `v6_smoke_n16/`, `v6_full/` | v6 aggregates (`results_v6.json`, `v6_contrasts.csv`, figure). `v6_full` is the full run, exploratory until the human audit; the 360-row audit is on Drive (`vlm_tradeoff_out_v6/`) |
| `v5_full/` | The full v5 run. `results_v5.json`, `v5_contrasts.csv`, `fig_v5_contrasts.png`, label files. The four `audit_v5_*` files in it are stale smoke leftovers (git-ignored): the real 240-row audit is on Drive (`vlm_tradeoff_out_v5/`) |

## 4. Code and tools

| File | Purpose |
|---|---|
| `tools/analyze_v3_offline.py` | Offline paired tests (exact McNemar, sign test, logistic GEE) on saved labels, no GPU |
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
4. v2 results unread; the 240-row human audit is not done; no commit since `cef563c` except what you choose to commit next.
