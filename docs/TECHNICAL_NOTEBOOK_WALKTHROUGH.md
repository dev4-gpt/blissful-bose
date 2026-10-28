# Technical notebook walkthrough for the advisor

Reviewed 22 October 2026. Read actual saved Drive notebooks as JSON, including code and output structures; no notebook was rerun, changed or interrupted. Raw outputs were not copied into this document. The 14-slide technical deck links to this audit; the maintained scientific narrative is [STATUS_AND_PAPER_PLAN.md](STATUS_AND_PAPER_PLAN.md).

## 1. What evidence should be brought to the meeting?

Bring the paired study contract, exact input/guard protocol, estimator definition, aggregate table, failure/denominator/cap coverage, and source notebook/cell. A collection of notebook screenshots alone cannot distinguish changed prompts, scoring or reused generations. Code cells below use **zero-based notebook indices**, not execution counters.

Read **38 saved Drive notebooks/archives** and **14 local notebooks**. Archives include incomplete attempts and duplicates; these are not 38 independent experiments. Local generated inputs are not substitutes for executed Drive files. Error-free notebook outputs can still contain caught model failures; inspect the saved failure aggregates.

## 2. Technical definitions and analysis actually implemented

- Binary refusal contrast: `Delta(a,b) = mean(R_a - R_b)` on the same jointly valid items. Report raw versus frozen-NC-adjusted definitions separately; missing parses are not negative labels.
- Exact McNemar: let `b` be a-only positives and `c` b-only positives. The implementation uses the two-sided Binomial(b+c, 0.5) tail, capped at 1. This tests paired discordance symmetry, not harm severity or equivalence.
- Historical scenario interval: compute one mean paired difference per represented scenario; `mean(d_s) +/- t_(k-1, .975) * sd(d_s)/sqrt(k)`. With all eight MM scenarios, df=7. Saved `diff` is pooled over valid items, while `t_ci` centers on the equal-scenario mean; missingness can make those targets differ.
- Historical equivalence flag: the 90% scenario interval must lie strictly inside +/-0.10. A degenerate interval from eight all-equal pairs is not accepted as population equivalence. Holm correction is implemented for the declared test families, not blanket justification for every exploratory table.
- GEE grid: `logit Pr(R_iwm=1) = beta0 + betaI*I + beta1*W1 + beta2*W2 + gamma1*I*W1 + gamma2*I*W2`. Binomial family, exchangeable working correlation, **item groups**; default robust covariance. Image log-odds are betaI, betaI+gamma1, betaI+gamma2. These are not percentage-point interactions; scenario t intervals above use a different grouping.
- V6 guard input: actual stimulus plus `reply[:1500]` (characters), with separate NC rules. Qwen3Guard safety Controversial was not equivalent to missing harm under the old mapping. The newer `harm_cx` preserves Controversial as unresolved and `Guard7` receives the full selected response. Thus old and new labels differ in protocol, not merely model/version.
- Matched development: `d_P = r(P_img)-r(P_txt)`, `d_S = r(S_img)-r(S_txt)`, interaction `d_S-d_P`. Chosen crossover requires `d_P<0`, `d_S>=0.15` and positive interaction. Current means are +0.125/+0.375, so the condition fails despite a +0.25 interaction.
- Development/window comparisons use `paired_cx`: average paired differences within each scenario, then average over all eight scenarios; no new population confidence interval is inferred. One item per scenario makes this equal to the paired item mean when coverage is complete.
- Window unit: decode generated IDs `t[0:256]` and `t[0:512]` from **one** generation, verify the full decode against the saved reply, retain EOS/cap evidence, compare prefixes to archived 256-token replies. Thirty-two answers give 64 dependent units; two guards give 128 evaluations.
- Missing-label cell bounds: if k positives and u unresolved among N scheduled, rate is bounded by `[k/N,(k+u)/N]`; contrast bounds subtract opposite endpoints. These are deterministic ambiguity bounds, not confidence intervals or guarantees about annotation error.
- Human/LLM agreement: `kappa=(p_o-p_e)/(1-p_e)`. Harm has observed agreement 41/48, but all-negative B implies the same chance agreement, so kappa=0. Comprehension including UNCERTAIN agrees, but the resolved-only single-class kappa is undefined. Neither annotator is automatically ground truth.

## 3. Notebook-by-notebook explanations and saved output evidence

### v1 — vlm_modality_tradeoff.ipynb

**Design / question.** A/B/C/D, coupling and inference-time activation steering. No training.

**Implementation / estimator.** `analyse`, `boot_diff`, `mcnemar_exact`, `run_steering`. A is a different backbone model; B/C changes stimulus form and framing. Historical labels are not interchangeable with v6.

**Observed result / limit.** The tested simple see-saw is unsupported; steering can raise both channels and benign refusal.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_modality_tradeoff.ipynb>). Local source: [vlm_modality_tradeoff.ipynb](../notebooks/vlm_modality_tradeoff.ipynb). Aggregate: [`v1_full_n30/results.json`](../v1_full_n30/results.json).

**Saved inspection:** 9/9 code cells have execution counters; 28 saved output blocks; 0 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 4: `load_split`, `to_img`; 6: `_kw`, `free`, `VLM`, `LLM`; 8: `safe`, `run_cached`; 10: `string_refusal`, `judge_all`, `labels_for`; 12: `wilson`, `mcnemar_exact`, `boot_diff`, `analyse`; 15: `run_steering`; 18: configuration/execution/export.

**Notebook SHA256:** `7ea7c00312b36d84371f22831486835897f61f5fdfe1ac1365d9ab23768898ac`.

### v2 — vlm_modality_tradeoff_v2.ipynb

**Design / question.** Add phrase-text E, benign prompts, random items, random-direction steering control and clustered resampling.

**Implementation / estimator.** `boot_diff_cluster`, `intents_for`, `run_steering`; retain the actual cache/label version. Baseline versus text twin is not a pure wording contrast.

**Observed result / limit.** Qwen2 steering strength 0.5: harmful text/image refusal 80.0%/76.7%; benign text 37.5%; not a deployable safety mitigation.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_modality_tradeoff_v2.ipynb>). Local source: [vlm_modality_tradeoff_v2.ipynb](../notebooks/vlm_modality_tradeoff_v2.ipynb). Aggregate: [`v2_run/results.json`](../v2_run/results.json).

**Saved inspection:** 10/10 code cells have execution counters; 114 saved output blocks; 0 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 4: `load_split`, `to_img`; 6: `_kw`, `free`, `VLM`, `LLM`; 8: `safe`, `run_cached`; 10: `string_refusal`, `judge_all`, `labels_for`, `intents_for`; 12: `wilson`, `mcnemar_exact`, `boot_diff`, `boot_diff_cluster`, `analyse`; 15: `run_steering`; 18: configuration/execution/export; 19: configuration/execution/export.

**Notebook SHA256:** `59d50dc94f0a8620e13aa0bee6be1a5e38df565c108c30508aaeb708fb426f3a`.

### v3 — vlm_modality_tradeoff_v3.ipynb

**Design / question.** Multiple judges, readback and a telescoping decomposition of the refusal gap.

**Implementation / estimator.** `judge_qwen3guard`, `judge_wildguard`, `decompose`, `cluster_boot`, `coupling`. Algebraic components depend on the chosen path; they are not uniquely identified causal mechanisms.

**Observed result / limit.** Invalid early rubric judges were retired; report guard-specific results rather than a pooled consensus.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_modality_tradeoff_v3.ipynb>). Local source: [vlm_modality_tradeoff_v3.ipynb](../notebooks/vlm_modality_tradeoff_v3.ipynb). Aggregate: [`v3_final_four_judges/results.json`](../v3_final_four_judges/results.json).

**Saved inspection:** 11/11 code cells have execution counters; 108 saved output blocks; 0 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 3: configuration/execution/export; 5: `load_split`, `to_img`, `norm_text`, `lev`, `cer`, `content_recall`, `to_text_prompt`, `string_refusal`; 7: `_kw`, `free`, `safe`, `VLM`, `LLM`, `run_cached`; 9: configuration/execution/export; 11: `sanity`, `score_readback`; 13: configuration/execution/export; 14: `parse_rubric`, `parse_legacy`, `judge_qwen_chat`, `judge_qwen3guard`, `judge_wildguard`; 16: `refuse_arrays`, `keyword_arrays`, `decompose`, `cluster_boot`, `ci`, `analyse_decomposition`, `coupling`, `run_analysis`; 18: configuration/execution/export.

**Notebook SHA256:** `22519e22cd11fffa79cfba468805c322f01c5d596f7a384872f93dc559db6964`.

### v4 — vlm_modality_tradeoff_v4.ipynb

**Design / question.** Introduce a larger wrapper/content/carrier grid, LLaVA, presence and harmfulness.

**Implementation / estimator.** `generation_cache_context`, `gen_cond`, `contrast`, `unsafe_arr`. Saved notebook is a smoke run, not the full factorial scientific dataset.

**Observed result / limit.** Engineering/control-flow evidence only; do not interpret small smoke percentages as substantive findings.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_modality_tradeoff_v4_smoke.ipynb>). Local source: [vlm_modality_tradeoff_v4.ipynb](../notebooks/vlm_modality_tradeoff_v4.ipynb). Aggregate: [`v4_smoke_n16/results_v4.json`](../v4_smoke_n16/results_v4.json).

**Saved inspection:** 11/11 code cells have execution counters; 66 saved output blocks; 0 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 3: configuration/execution/export; 5: `load_split`, `to_img`, `norm_text`, `lev`, `cer`, `content_recall`, `to_text_prompt`, `string_refusal`, `model_idx`; 7: `_kw`, `free`, `safe`, `VLM`, `LLM`, `sha256_json`, `_image_hash`, `generation_cache_context`, `run_cached`; 9: configuration/execution/export; 11: `sanity`, `score_readback`, `score_readback_full`, `gen_cond`; 13: `judge_qwen3guard`, `judge_wildguard`; 15: `exact_p`, `contrast`, `decompose`; 17: `refuse_arr`, `unsafe_arr`, `_g`, `_both`, `_h14`, `_h15`; 19: configuration/execution/export.

**Notebook SHA256:** `5e6c56d1cd50a434c080b6c0943f6c4aafbe3bcbcd1189cc4ea0932de9b5fe22`.

### v5 — vlm_modality_tradeoff_v5.ipynb

**Design / question.** Full exploratory grid, font treatment, judge disagreement, Holm checks and private audit export.

**Implementation / estimator.** `run_pair`, `judge_qwen3guard`, `judge_wildguard`, `holm`. Neutral-input judging used the wrong target context; preprocessing upscaled intended small-font images.

**Observed result / limit.** Preserve v5 outcomes, but use the corrected v6 context/preprocessing for the maintained interpretation.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_modality_tradeoff_v5.ipynb>). Local source: [vlm_modality_tradeoff_v5.ipynb](../notebooks/vlm_modality_tradeoff_v5.ipynb). Aggregate: [`v5_full/results_v5.json`](../v5_full/results_v5.json).

**Saved inspection:** 14/14 code cells have execution counters; 167 saved output blocks; 0 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 3: `purge_hf_cache`; 5: `load_split`, `to_img`, `norm_text`, `lev`, `cer`, `content_recall`, `to_text_prompt`, `string_refusal`, `model_idx`; 7: `_kw`, `free`, `safe`, `VLM`, `LLM`, `sha256_json`, `_image_hash`, `generation_cache_context`, `run_cached`; 9: configuration/execution/export; 11: configuration/execution/export; 13: `sanity`, `score_readback`, `score_readback_full`, `gen_cond`, `run_pair`; 15: `judge_qwen3guard`, `judge_wildguard`; 17: `exact_p`, `contrast`, `decompose`; 19: `refuse_arr`, `unsafe_arr`, `_g`, `_both`, `_h14`, `_h15`; 21: `holm`, `mean_ci`, `_c`, `_h20`; 23: configuration/execution/export; 25: configuration/execution/export.

**Notebook SHA256:** `88bcabd31216e467495932e30ca5aaeb5337405f7896d07a0c312468bd1330b4`.

### v6 — vlm_modality_tradeoff_v6.ipynb

**Design / question.** Stimulus-aware relabeling; true 12/20/38-pixel rendering; presence, FigStep and batch comparison.

**Implementation / estimator.** Saved cells 15/17/19 define guards, statistics and result checks (zero-based). `contrast` uses jointly finite pairs; `gee_grid` uses exchangeable binomial GEE grouped by item. Guards slice replies to 1,500 characters.

**Observed result / limit.** Historical Qwen3Guard B/E/C refusal: Qwen2 66.1/18.4/15.1%; Qwen2.5 74.3/51.0/44.1%; LLaVA 45.4/37.5/2.6%. H21 false, H22 split, H23 true, H24 false, H25 true, H26 inconclusive, H27 false.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_modality_tradeoff_v6.ipynb>). Local source: [vlm_modality_tradeoff_v6.ipynb](../notebooks/vlm_modality_tradeoff_v6.ipynb). Aggregate: [`v6_full/results_v6.json`](../v6_full/results_v6.json).

**Saved inspection:** 13/13 code cells have execution counters; 78 saved output blocks; 1 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 3: `purge_hf_cache`; 5: `load_split`, `to_img`, `norm_text`, `lev`, `cer`, `content_recall`, `to_text_prompt`, `string_refusal`, `model_idx`; 7: `_kw`, `free`, `safe`, `VLM`, `LLM`, `sha256_json`, `_image_hash`, `generation_cache_context`, `_read_records`; 9: configuration/execution/export; 11: `add_spec`, `wrap_q`, `stimulus`; 13: `score_readback`, `score_readback_full`, `gen_cond`, `run_pair`; 15: `nonanswer`, `Qwen3GuardJ`, `WildGuardJ`; 17: `exact_p`, `contrast`, `kappa`, `holm`, `gee_grid`, `rogan_gladen`; 19: `_guard`, `arr`, `have`, `clus`, `clus_fs`, `both`, `rate`, `_h22`, `_h24`; 21: configuration/execution/export; 23: configuration/execution/export.

**Notebook SHA256:** `b1a99abf8f1196f41e3c29e966f98e7c9ef5b2098adec259bad7e50f33d89dda`.

### v7 — vlm_modality_tradeoff_v7.ipynb

**Design / question.** Eight-checkpoint benign compatibility, native adapters, exact identity caches, split/gate checks, sampling and image dose/order machinery.

**Implementation / estimator.** `Model7`, `Guard7`, `cached7`, `paired7`, `forecast7`, `human_gate7`. Implemented arms are not all executed scientific outcomes. Inspect individual preserved attempts.

**Observed result / limit.** Three completed benign checks, two partial, three failed before response; no eight-model scientific or fresh-confirmatory result.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/v7_completed_runs/vlm_modality_tradeoff_v7.ipynb>). Local source: [vlm_modality_tradeoff_v7.ipynb](../notebooks/vlm_modality_tradeoff_v7.ipynb). Associated results are described in the maintained status; no single pooled aggregate is implied.

**Saved inspection:** 11/11 code cells have execution counters; 57 saved output blocks; 1 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 3: `digest7`, `atomic7`, `norm7`, `image_hash7`, `cached7`, `text_image7`, `smoke_items7`, `conditions7`, `historical_ids7`; 4: `ValidLogits7`, `cuda_fatal7`, `Model7`, `Guard7`, `environment7`; 5: `norm_text`, `lev`, `content_recall`, `string_refusal`, `nonanswer`; 7: `budget7`, `purge7`; 9: `human_gate7`; 11: configuration/execution/export; 13: configuration/execution/export; 15: configuration/execution/export; 17: configuration/execution/export.

**Notebook SHA256:** `f519fa1262b86fddb7b0eaeaa5d3ca3c2077457b58250f5fb676dae3c0ad2b28`.

### expanded — vlm_research_expanded.ipynb

**Design / question.** Compatibility/development runner plus no-inference historical paired-transition and scoring-sensitivity analysis.

**Implementation / estimator.** `analyze_saved`, `paired_counts`, `transition_readout`, `sensitivity_readout`. Reconstruct refusal tables only when saved discordances and paired margins agree; never reconstruct joint harm from separate marginals.

**Observed result / limit.** Qwen2 E/C example: 31 text-only refusals, 21 image-only, n=304; net 3.3 pp versus 17.1% changing label. This is reused historical evidence.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_research_expanded.ipynb>). Local source: [vlm_research_expanded.ipynb](../notebooks/vlm_research_expanded.ipynb). Associated results are described in the maintained status; no single pooled aggregate is implied.

**Saved inspection:** 16/16 code cells have execution counters; 70 saved output blocks; 12 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 2: configuration/execution/export; 3: configuration/execution/export; 4: `digest7`, `atomic7`, `norm7`, `image_hash7`, `cached7`, `text_image7`, `smoke_items7`, `conditions7`, `historical_ids7`; 5: `ValidLogits7`, `cuda_fatal7`, `Model7`, `Guard7`, `environment7`; 6: `norm_text`, `lev`, `content_recall`, `string_refusal`, `nonanswer`; 8: `budget7`, `purge7`; 11: `human_gate7`; 14: configuration/execution/export; 17: configuration/execution/export; 20: configuration/execution/export; 23: configuration/execution/export; 25: `run_readout7`; 28: `number`, `count`, `paired_counts`, `missing_bounds`, `analyze_saved`, `markdown_table`, `transition_readout`, `sensitivity_readout`, `make_figure`; 29: configuration/execution/export; 31: configuration/execution/export; 33: configuration/execution/export.

**Notebook SHA256:** `b27f575dddf1db0d591c76ab6d5127ea7621cb2875b02d469c733a84ee61895b`.

### pilot — vlm_development_pilot.ipynb

**Design / question.** Eight seen OCR-verified MM items, Qwen2-VL-2B, B/E/C plus separate readback.

**Implementation / estimator.** Exact dataset/source/response/label hashes checked by `summarize_development_pilot.py`. Eight items are purposive development coverage, not a population sample.

**Observed result / limit.** 32 responses and 72 automated label records; no failures. E/C refusal and harmfulness labels match within each guard. Sixteen of 24 answering calls hit 256 tokens.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/v7_completed_runs/2026-10-19_123518_Qwen2_CORE8_DEVELOPMENT_COMPLETED/completed_notebook.ipynb>). Local source: [vlm_development_pilot.ipynb](../notebooks/vlm_development_pilot.ipynb). Aggregate: [`v7_development_core8/pilot_summary.json`](../v7_development_core8/pilot_summary.json).

**Saved inspection:** 16/16 code cells have execution counters; 70 saved output blocks; 9 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 2: configuration/execution/export; 3: configuration/execution/export; 4: `digest7`, `atomic7`, `norm7`, `image_hash7`, `cached7`, `text_image7`, `smoke_items7`, `conditions7`, `historical_ids7`; 5: `ValidLogits7`, `cuda_fatal7`, `Model7`, `Guard7`, `environment7`; 6: `norm_text`, `lev`, `content_recall`, `string_refusal`, `nonanswer`; 8: `budget7`, `purge7`; 11: `human_gate7`; 14: configuration/execution/export; 17: configuration/execution/export; 20: configuration/execution/export; 23: configuration/execution/export; 25: `run_readout7`; 28: `number`, `count`, `paired_counts`, `missing_bounds`, `analyze_saved`, `markdown_table`, `transition_readout`, `sensitivity_readout`, `make_figure`; 29: configuration/execution/export; 31: configuration/execution/export; 33: configuration/execution/export.

**Notebook SHA256:** `6b9a2d8b2c0693fb82c4d34e633149a097f895d8e315fcefaf358777610f6f66`.

### crossover — vlm_crossover_development.ipynb

**Design / question.** Pinned Qwen2.5-VL-3B FP16 greedy batch-one; eight seen full questions; 2 wrappers × 2 carriers plus 2 blank arms and readback.

**Implementation / estimator.** `specs_cx`, `select_cx`, `paired_cx`, `summarize_cx`. OCR eligibility then fixed-seed selection; raw refusal is the primary diagnostic. The new steps wording differs from the legacy v6 pair.

**Observed result / limit.** 56 target/96 guard calls; no failures. Plain text/image 4/8 vs 5/8; steps 5/8 vs 8/8. No crossover; 17 of 48 answering responses capped; readback 8/8.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_crossover_development.ipynb>). Local source: [vlm_crossover_development.ipynb](../notebooks/vlm_crossover_development.ipynb). Aggregate: [`v7_crossover_core8/results_crossover.json`](../v7_crossover_core8/results_crossover.json).

**Saved inspection:** 9/9 code cells have execution counters; 68 saved output blocks; 4 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 4: `digest7`, `atomic7`, `norm7`, `image_hash7`, `cached7`, `text_image7`, `smoke_items7`, `conditions7`, `historical_ids7`; 5: `ValidLogits7`, `cuda_fatal7`, `Model7`, `Guard7`, `environment7`; 6: `norm_text`, `lev`, `content_recall`, `string_refusal`, `nonanswer`; 7: `specs_cx`, `select_cx`, `harm_cx`, `cell_cx`, `paired_cx`, `summarize_cx`, `tier_cx`, `CrossoverRun`; 9: `snapshot_cx`; 12: configuration/execution/export; 14: configuration/execution/export.

**Notebook SHA256:** `078de2a577826b427a7f98953d82a5dd99804acefd4fbde611eb5eb3495023a0`.

### human_validation — vlm_next_stage_human_validation.ipynb

**Design / question.** CPU reading notebook plus optional original 48-answer private review/import analysis.

**Implementation / estimator.** `package`, `review`, `outcomes`, `agreement`, `analyze`. Package IDs, source hashes, duplicate/missing labels and reference kind are checked; labels are not automatically adjudicated.

**Observed result / limit.** Saved preparation execution is not evidence that the full v6 human gate passed. Original assisted A versus auxiliary GPT-6.1-Sol comparison is descriptive; the new 64-unit review is distinct.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_next_stage_human_validation_2026-10-19_154115.ipynb>). Local source: [vlm_next_stage_human_validation.ipynb](../notebooks/vlm_next_stage_human_validation.ipynb). Associated results are described in the maintained status; no single pooled aggregate is implied.

**Saved inspection:** 7/7 code cells have execution counters; 7 saved output blocks; 6 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 3: configuration/execution/export; 7: `read`, `sha`, `write`, `package`, `review`, `binary`, `agreement`, `rate`, `outcomes`; 8: configuration/execution/export; 10: configuration/execution/export; 13: configuration/execution/export; 15: configuration/execution/export.

**Notebook SHA256:** `86a53b9e829dd4481daaaaf090c973ecd9b8a30f3441896f9e01530c4621a28d`.

### window — vlm_window_study.ipynb

**Design / question.** 32 up-to-512-token generations from the same eight items and four core arms; derive prefix256/full512 from generated IDs.

**Implementation / estimator.** `window_views`, `window_summary`, `WindowRun`. Verify token decode/EOS and original prefix; `Guard7` uses full selected reply without the old character slice. 64 units share 32 responses.

**Observed result / limit.** 32 target, 64 units, 128 guard labels; zero failures/missing labels; zero prefix drift. No guard-label changes or crossover; eight full cap hits. New human review pending; broader diagnostic unresolved.

**Read the notebook:** [saved Drive copy](</Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive/Colab Notebooks/vlm_window_study.ipynb>). Local source: [vlm_window_study.ipynb](../notebooks/vlm_window_study.ipynb). Aggregate: [`v7_window_core8/results_window.json`](../v7_window_core8/results_window.json).

**Saved inspection:** 8/8 code cells have execution counters; 54 saved output blocks; 9 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: False. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 1: configuration/execution/export; 2: configuration/execution/export; 4: configuration/execution/export; 7: configuration/execution/export; 10: configuration/execution/export; 12: configuration/execution/export; 14: configuration/execution/export; 17: configuration/execution/export.

**Notebook SHA256:** `3e59a236747d20a53067090dd020c871e8eecd696310682949bda2e0fd74ee9e`.

### companion — vlm_project_companion.ipynb

**Design / question.** Portable hash-checked allowlisted cross-version snapshot, source map, tables and figures.

**Implementation / estimator.** `make_unified_nb.collect`, `execute_cpu`; reads saved aggregates and inspects code syntax, never executes experiment bodies. Local refreshed copy is newer than earlier Drive companion snapshots.

**Observed result / limit.** CPU presentation/reproduction only, zero target/guard calls. This is the best reading entry point, not an additional experiment.

**Read the notebook:** [current local CPU notebook](</Users/aryamandev/Developer/blissful-bose/notebooks/vlm_project_companion.ipynb>). Associated results are described in the maintained status; no single pooled aggregate is implied.

**Saved inspection:** 26/26 code cells have execution counters; 46 saved output blocks; 22 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 2: `digest_companion`, `show_rows`; 4: configuration/execution/export; 7: configuration/execution/export; 11: configuration/execution/export; 14: configuration/execution/export; 17: configuration/execution/export; 20: configuration/execution/export; 23: configuration/execution/export; 26: configuration/execution/export; 29: configuration/execution/export; 32: configuration/execution/export; 35: configuration/execution/export; 38: configuration/execution/export; 41: configuration/execution/export; 45: configuration/execution/export; 48: configuration/execution/export; 51: configuration/execution/export; 54: configuration/execution/export; 57: configuration/execution/export; 59: configuration/execution/export; 62: configuration/execution/export; 64: configuration/execution/export; 67: configuration/execution/export; 70: configuration/execution/export; 73: configuration/execution/export; 78: configuration/execution/export.

**Notebook SHA256:** `99fc0c4f190c7e6d692dad8ee865cd6ebc21de72f42faf56a751c45681a5950f`.

### methodology — vlm_methodology_review.ipynb

**Design / question.** Literature-to-design explanation with a synthetic weighted human/autorater estimation example.

**Implementation / estimator.** Synthetic numeric illustration; statistical assumptions and design weights are teaching material, not observed calibration of our runs.

**Observed result / limit.** No model downloads, no human-validation result and no new empirical VLM finding.

**Read the notebook:** [current local CPU notebook](</Users/aryamandev/Developer/blissful-bose/notebooks/vlm_methodology_review.ipynb>). Associated results are described in the maintained status; no single pooled aggregate is implied.

**Saved inspection:** 1/1 code cells have execution counters; 1 saved output blocks; 7 interpretation-related Markdown cells. Uncaught error types: none. Executed archive source equals current local code: True. A mismatch is a provenance distinction, not evidence of failed results.

**Cell map (zero-based):** 7: `stratified_difference`, `synthetic_demo`.

**Notebook SHA256:** `f037de33600d569bc1e2a9ee91e97f45dec760d864859985e19f2152f5cca632`.

## 4. Saved Drive archive inventory

This is an output-preservation inventory, not a claim that every stage succeeded. `Counter cells` counts execution metadata; some snapshots retain outputs after counters were reset. Late export snapshots can contain the completed preceding run but not their own export-cell output.

| Saved Drive notebook | Counter cells | Output blocks | Uncaught errors |
|---|---:|---:|---|
| `Colab Notebooks/v7_completed_runs/2026-10-18_1722_Qwen25VL7B_COMPLETED.ipynb` | 12/12 | 28 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_000215_InternVL3_2B_COMPLETED_WITH_FAILURES.ipynb` | 16/16 | 29 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_001353_SmolVLM2_COMPLETED_PARTIAL.ipynb` | 16/16 | 31 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_010159_OneVision_COMPLETED_WITH_FAILURES.ipynb` | 16/16 | 36 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_011617_InternVL3_8B_COMPLETED_WITH_FAILURES.ipynb` | 16/16 | 35 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_0140_PANEL_REVIEWED_FINAL.ipynb` | 16/16 | 35 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_015734_development_core8_DATA_PREFLIGHT_FAILED.ipynb` | 8/16 | 6 | ValueError |
| `Colab Notebooks/v7_completed_runs/2026-10-19_0211_development_core8_PREFLIGHT_RETRY.ipynb` | 8/16 | 4 | ValueError |
| `Colab Notebooks/v7_completed_runs/2026-10-19_103835_development_DRIVE_MOUNT_FAILED.ipynb` | 6/16 | 2 | ValueError |
| `Colab Notebooks/v7_completed_runs/2026-10-19_104600_development_MOUNT_FAILED_LOCAL_FALLBACK.ipynb` | 6/16 | 2 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_123518_Qwen2_CORE8_DEVELOPMENT_COMPLETED/completed_notebook.ipynb` | 16/16 | 70 | none |
| `Colab Notebooks/v7_completed_runs/2026-10-19_123518_Qwen2_CORE8_DEVELOPMENT_COMPLETED/reviewed_notebook.ipynb` | 16/16 | 70 | none |
| `Colab Notebooks/v7_completed_runs/vlm_modality_tradeoff_v7.ipynb` | 11/11 | 57 | none |
| `Colab Notebooks/v7_completed_runs/vlm_modality_tradeoff_v7_explained_2026-10-18_1658_MOUNT_FAILED.ipynb` | 0/12 | 2 | ValueError |
| `Colab Notebooks/v7_completed_runs/vlm_modality_tradeoff_v7_smoke_Qwen2VL2B_2026-10-18_1554_COMPLETED.ipynb` | 0/11 | 11 | none |
| `Colab Notebooks/v7_completed_runs/vlm_modality_tradeoff_v7_smoke_stage2_2026-10-18_1641_COMPLETED_PARTIAL.ipynb` | 0/11 | 57 | none |
| `Colab Notebooks/vlm_crossover_development.ipynb` | 9/9 | 68 | none |
| `Colab Notebooks/vlm_modality_tradeoff.ipynb` | 9/9 | 28 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v2.ipynb` | 10/10 | 114 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v3.ipynb` | 11/11 | 108 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v4_smoke.ipynb` | 11/11 | 66 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v5.ipynb` | 14/14 | 167 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v5_smoke.ipynb` | 14/14 | 71 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v6.ipynb` | 13/13 | 78 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v6_smoke.ipynb` | 13/13 | 107 | none |
| `Colab Notebooks/vlm_modality_tradeoff_v7_explained_Qwen25VL7B_2026-10-18.ipynb` | 12/12 | 28 | none |
| `Colab Notebooks/vlm_next_stage_human_validation_2026-10-19_154115.ipynb` | 7/7 | 7 | none |
| `Colab Notebooks/vlm_research_expanded.ipynb` | 16/16 | 70 | none |
| `Colab Notebooks/vlm_window_study.ipynb` | 8/8 | 54 | none |
| `vlm_tradeoff_analysis/deeper_measurement_2026-10-19_010506/vlm_deeper_measurement_analysis_EXECUTED.ipynb` | 6/6 | 8 | none |
| `vlm_tradeoff_out_v7/development/crossover_3b_20261019T174000Z/snapshots/20261019T175513_833444Z/completed_notebook.ipynb` | 7/9 | 21 | none |
| `vlm_tradeoff_out_v7/development/crossover_3b_20261019T174000Z/snapshots/20261019T181322_164968Z/completed_notebook.ipynb` | 7/9 | 62 | none |
| `vlm_tradeoff_out_v7/development/crossover_3b_20261019T174000Z/snapshots/20261019T181322_692305Z/completed_notebook.ipynb` | 7/9 | 66 | none |
| `vlm_tradeoff_out_v7/development/crossover_3b_20261019T174000Z/snapshots/20261019T181323_358733Z/completed_notebook.ipynb` | 8/9 | 66 | none |
| `vlm_tradeoff_out_v7/development/window_3b_20261020_v1/snapshots/20261020T171216_094186Z/notebook_with_outputs.ipynb` | 5/8 | 8 | none |
| `vlm_tradeoff_out_v7/development/window_3b_20261020_v1/snapshots/20261020T171934_824105Z/notebook_with_outputs.ipynb` | 5/8 | 24 | none |
| `vlm_tradeoff_out_v7/development/window_3b_20261020_v1/snapshots/20261020T173209_151061Z/notebook_with_outputs.ipynb` | 5/8 | 49 | none |
| `vlm_tradeoff_out_v7/development/window_3b_20261020_v1/snapshots/20261020T173210_988698Z/notebook_with_outputs.ipynb` | 7/8 | 53 | none |

## 5. What is already explained, what was corrected, and what not to claim

Existing explanations are in the saved expanded/pilot/crossover/window notebooks, the local unified companion and status sections 3, 10 and 15–18. Some Drive text cells still say prepared/untested even though later outputs completed. Read the outputs and manifests before quoting those headings. This audit adds current technical interpretation alongside the source links; immutable executed notebooks are not rewritten.

- The old v6 grid observes a reversal under legacy inputs; the new matched grid did not. They differ in wrapper wording, selected items, generation batch and label protocol. This is not an exact same-protocol replication or a contradiction to erase.
- The 1,500-character guard window is verified directly in the saved v6 code. It is an additional historical limitation, not proof that it caused any result. The newer window study has no such hidden character slice. Do not treat this code difference as a new observed response-length finding.
- A historical paired E/C net gap of 10/304 = 3.3 pp coexists with (31+21)/304 = 17.1% changed refusal labels. Counts come from jointly valid paired margins/discordances, not separate harm rates.
- Original 48-answer labels are development material. A received LLM help; B is auxiliary GPT-6.1-Sol, user-confirmed, exact backend/settings unknown. Seven harm disputes remain unresolved. The new 64-unit human pass and delayed repeat are pending.
- Broad text controls, framing, attachment effects and judge limitations have close prior work. See [the verified novelty register](NOVELTY_AUDIT_AND_PLAN.md#13-response-window-measurement-review--2026-10-20), including sections/method reading depth. A concrete paired consequence plus untouched validation is needed before a novel contribution claim.

## 6. Professor-facing answers

**What is the unit of analysis?** Historical item-condition responses, paired by item; GEE clusters repeated conditions by item. Scenario intervals aggregate within scenario. Window pairs share one generation; do not call them independent samples.

**What is causal here?** Controlled input comparisons within a checkpoint, subject to serialization/content/measurement limitations. No internal mechanism is established by correlation, readback, interaction or steering alone.

**What has actually been resolved?** Wrong-stimulus scoring, font treatment, exact cache/source identity, coverage and failure preservation, and evidence navigation. Label validity, scientific novelty and fresh generalization are not resolved by these fixes.

**Which notebook should be run next?** None for generation. Finish the existing 64-unit private review and >=24-hour delayed repeat; analyze exact paired human/guard outcomes, then decide whether a new approved validation is justified.

**Should we attach every notebook’s exploratory analysis?** Attach this source-and-cell walkthrough and the unified companion. Present one coherent design/result table, not a pooled average across notebook versions. Keep original archives available for questions; private replies/annotations must not be attached to a public presentation.
