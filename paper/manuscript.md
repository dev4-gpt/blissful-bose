# Do Matched Text Controls Explain Typographic Safety Gaps?

*Exploratory manuscript for advisor review — updated October 20, 2026. Author list and venue to be confirmed. Human validation and fresh confirmatory evaluation are pending. This draft reports existing evidence; proposed extensions are not results.*

**Latest evidence update:** the matched Qwen2.5 eight-item crossover was not observed (56 target/96 guard calls). The subsequent response-window study completed 32 target responses and 128 guard evaluations without failures. All paired automated labels remained unchanged; eight full responses hit the 512-token cap and new human review is pending. Original 48-answer human review was partly LLM-assisted; auxiliary GPT-6.1-Sol is not a second human. The maintained result ledger and advisor walkthrough are [status §§17–18](../docs/STATUS_AND_PAPER_PLAN.md). Historical statements below must be read with that update.

## Abstract

Text–image safety comparisons can change the request's wording and content form along with its carrier. We examine what matched text controls and alternative scoring choices reveal about typographic refusal gaps in open vision–language models. Existing exploratory runs cover MM-SafetyBench and FigStep on three checkpoints, supplemented by a separately reported eight-item development pilot. We distinguish refusal, harmful assistance and non-comprehension, preserve model and evaluator failures, and verify the provenance of the latest pilot's cached responses and labels. The pilot's matched text and image responses receive identical item-level refusal and harmfulness labels within each guard, while the guards disagree on harmfulness for two answering responses. This pilot is not a fresh replication and does not establish population equivalence. Human-referenced measurement and generalization remain necessary before substantive claims about explanation or efficient substitution can be made.

## 1. Introduction

When a vision–language model refuses a plain-text request but answers a typographic image, an apparent modality gap can have several explanations. The image may carry different information, the surrounding instruction may change, image presence may affect behavior, or the scoring system may misread the response. A refusal label alone cannot establish whether the model supplied harmful assistance.

Our original motivation was a possible inverse relationship between language and visual safety. The limited exploratory evidence does not support a universal see-saw; it also cannot exclude every trade-off or identify a common causal mechanism. We instead investigate a narrower question: **which apparent typographic differences remain interpretable after matched controls and explicit measurement checks?**

This is an exploratory replication and measurement study, not a claim to invent text controls or discover that multimodal models can fail. Its potential empirical contribution depends on whether audited measurements materially alter a substantive comparison or establish a useful boundary across checkpoints. A result showing little correction is also informative when its precision and scope are reported honestly.

## 2. Closest related work

[FigStep, §6.4](https://arxiv.org/html/2311.05608v3#S6.SS4) already evaluates an all-text control. [MMJailBench, §§3–5](https://arxiv.org/html/2608.25490v1) factorizes multimodal attacks and accounts for instruction mismatch. Our matched controls are replications/adaptations, not new inventions.

[MSTS, §§3.4 and 4.5–4.6](https://arxiv.org/html/2501.10057) combines text equivalents, human response analysis and automated-evaluator assessment. [ELITE, §§3.1 and 5–6](https://arxiv.org/html/2502.04757v3) distinguishes harmful outputs from harmless descriptions and evaluates agreement with people. We therefore require a contribution beyond adding another human audit.

[VLSU, §2](https://arxiv.org/html/2510.18214) studies joint image–text safety and borderline content; [MOSSBench, §§3–5](https://arxiv.org/html/2406.17806v1) evaluates visual over-refusal. These studies motivate retaining benign usefulness and treating typography as a limited scope rather than general visual safety.

If we later investigate efficient evaluation, [tinyBenchmarks](https://arxiv.org/html/2402.14992v2), [FAQ, §3](https://arxiv.org/html/2601.20251v3), [active statistical inference](https://proceedings.mlr.press/v235/zrnic24a.html), and [robust active sampling](https://arxiv.org/html/2511.08991v1) are essential comparators. This draft does not claim a new estimator or a demonstrated efficiency gain.

The detailed primary-source reading register, including limitations of theorem transfer and proposed directions outside typography, is in [the novelty audit, §11](../docs/NOVELTY_AUDIT_AND_PLAN.md).

## 3. Study design and evidence separation

### 3.1 Evidence cohorts

| Cohort | Purpose | How it may be used |
| --- | --- | --- |
| v1–v5 historical runs | Development, judge failures and design refinement | Traceable historical context; cached reruns are not independent replications |
| v6 full run | Main existing exploratory scientific evidence | Guard-specific comparisons on the saved item sets; no human-validation claim |
| v7 eight-checkpoint benign checks | Engineering compatibility | Report complete/partial/failed coverage; never treat as safety outcomes |
| v7 Qwen2 core-eight development pilot | End-to-end data, inference and labeling feasibility | Separate descriptive table; previously seen items, one item per scenario |
| Human review | Pending | Separate label version and weighted estimates only after annotation and design verification |
| Fresh confirmatory evaluation | Not collected | Locked until the human, historical-exclusion and measured-budget gates pass |

### 3.2 Conditions and attribution

B is the original plain-text question. E is the benchmark payload represented as text with its matched wrapper; C presents that payload in the benchmark image with the wrapper. E/C is a useful matched benchmark contrast, but it does not establish universal semantic equivalence between carriers. B/E additionally changes content form, so it is not a pure wording intervention. Wording attribution requires the full-question factorial grid.

Blank, noise and irrelevant-image controls address image presence. Separate readback addresses transcription under a separate task; it does not demonstrate comprehension during the answering call. Preserve processor revisions, image ordering, effective token grids and unsupported conditions.

### 3.3 Generation and measurement

The development pilot uses Qwen2-VL-2B, batch one, greedy decoding, and a 256-new-token cap. It evaluates B/E/C and a separate image readback for each of eight previously seen development items. Qwen3Guard and WildGuard label the actual presented stimulus and response; the frozen keyword and NC rules remain separately identified. The readbacks are not safety-judged.

Original model outputs and automated labels are preserved. Human review adds a distinct label version. Any scoring change developed using annotations must be evaluated on untouched grouped human labels; tuning rows cannot also validate the change. Human-only and corrected population estimates require verified sampling weights, including agreement strata. Reference disagreement and adjudication should be reported rather than treating a single person's label as infallible.

### 3.4 Analysis and uncertainty

Historical analyses use the approved contrasts and their saved scenario/item structure. The new pilot is reported descriptively: its eight purposively selected, previously seen items do not support a population-equivalence claim. Original degenerate interval/verdict fields are archived unchanged and explicitly not endorsed in the reviewed summary. Formal changes to inference, endpoints or sampling require an addendum before confirmatory adoption.

Separate exact paired tables are constructed for refusal, harmfulness and NC. They use complete matched item responses and retain missingness. Do not reconstruct a joint harmfulness table from marginal rates or treat the two guards as independent replications. Distributional claims about repeated responses require repeated completions, which this pilot does not provide.

## 4. Existing results

### 4.1 Historical evidence

The complete cross-version and guard-specific tables are generated by `python3 tools/cross_version_table.py --check-doc docs/STATUS_AND_PAPER_PLAN.md`. The v6 source is [results_v6.json](../v6_full/results_v6.json); descriptive reanalysis is in `tools/vlm_saved_analysis.py`.

One illustrative frozen v6 comparison, Qwen2-VL-2B under Qwen3Guard's NC-adjusted E/C refusal measure, has 304 valid pairs: 31 refuse only in text and 21 only in images. The net is 10/304 while 52/304 pairs change label. Opposing changes therefore cancel partly in the average. These are refusal outcomes from observed historical completions, not evidence of hidden harmful image responses or a stable internal policy change. Source: [the verified analysis and caveats](../docs/NOVELTY_AUDIT_AND_PLAN.md#10-october-19-decision-evaluate-the-limits-of-text-led-safety-testing).

### 4.2 Completed development pilot

Source: [pilot_summary.json](../v7_development_core8/pilot_summary.json), with exact counts in [pilot_rates.csv](../v7_development_core8/pilot_rates.csv). These aggregates were verified against the private manifest, generation checkpoints and stimulus/response-specific label caches. The original Colab notebook with outputs and original aggregate export is separately preserved on college Drive.

| Guard | Condition | Refusal / valid | Harmful assistance / valid |
| --- | --- | --- | --- |
| Qwen3Guard | B | 5/8 | 3/8 |
| Qwen3Guard | E | 0/8 | 7/8 |
| Qwen3Guard | C | 0/8 | 7/8 |
| WildGuard | B | 5/8 | 3/8 |
| WildGuard | E | 0/8 | 8/8 |
| WildGuard | C | 0/8 | 8/8 |

The run saves 32 target responses, including eight readbacks, and 72 automated label records, with zero recorded failures. Each guard assigns identical item-level E/C refusal and harmfulness labels. This pilot therefore provides no observed E/C harmfulness discordance; it does not confirm a hidden-image-failure hypothesis. The guards disagree on harmfulness for two of the 24 answering responses and agree on refusal for all 24. That agreement is not human validation.

Readback succeeds by the frozen rule for all eight images. However, 16 of the 24 answering calls reach the 256-token cap: three in B, six in E and seven in C. A cap hit identifies a response-window limitation, not proof that missing text would change its safety label. No unsafe label is available from the keyword rule.

This development result must not be pooled with v6, described as a fresh replication, or used to claim equivalence because no observed E/C differences occurred. The original export's zero-width E/C intervals and equivalence flag are unsuitable for that conclusion. The pilot supports execution feasibility and a bounded descriptive matched-control observation.

### 4.3 Engineering coverage

The approved panel's benign attempts yielded three complete Qwen checks, partial LLaVA-1.5 and SmolVLM2 checks, and three first-generation numerical failures. Failed image ordering and numerical configurations remain visible. These counts describe engineering attempts, not safety rankings. See [the saved status record](../docs/STATUS_AND_PAPER_PLAN.md#2-what-has-actually-been-tried).

## 5. What remains unmeasured

Human-only rates, audit-weighted label corrections, fresh paired effects, and architecture-held-out predictive performance remain pending. No claim of publication readiness, calibrated risk control, a new safety mechanism, or efficient replacement follows from the current evidence.

A possible future question is whether text-led testing can reduce evaluation cost while bounding missed harmful image responses. It requires full paired reference outcomes to validate the policy, a random audit of purportedly low-risk cases, and a matched-cost random baseline. A policy can estimate an average accurately while missing particular failures; these are separate objectives. This is a proposal requiring a frozen addendum, not an experiment performed here.

An output-protocol boundary is also possible, but [Visual Grounding Safety, §2](https://arxiv.org/html/2610.05637v1) already studies VQA versus grounding. Any successor must isolate a distinct interaction, preserve refusal affordances, and score capability/format failures separately. We do not add grounding, new models, or new benchmarks in this draft.

## 6. Limitations, ethics and reproducibility

All scientific results remain exploratory and guard-labelled. Historical outcomes informed the design. Related checkpoints are not independent architectures; observed compatibility limits the achieved panel. Benchmark wrappers, data mirrors, comprehension, rendering, quantization, output caps and judge parsing constrain interpretation. Human audits may change labels and conclusions.

The project uses open models/data and inference without training. Public artifacts contain reconstruction code, exact settings, numeric aggregates and figures where available. Raw prompts, images, replies and audits remain private. Safety evaluation can have dual-use implications; the paper does not release attack payloads or harmful replies. Human annotation procedures must allow ambiguous judgments, disagreement and the option to skip sensitive material.

Reproduce the new descriptive summary with `python3 tools/summarize_development_pilot.py --source <private-run-folder> --output v7_development_core8`; run `python3 tools/nb_gen/e2e/e2e_development_summary.py` for corruption/missingness checks. This script makes no model calls. Private source access is necessary for full cache verification; public aggregates reproduce the displayed table, not an independent audit of unavailable raw records. The approved analysis-plan hash remains unchanged.

## 7. Conclusion — provisional

The existing evidence motivates testing the interpretation of typographic safety gaps under matched controls and human-referenced measurement. The completed pilot shows agreement between its matched text and image outcomes under each guard and provides a useful negative development observation. Whether the broader measurement study or a cost-constrained extension supports a substantial paper remains an open empirical question.
