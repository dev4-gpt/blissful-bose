# Completed MM-SafetyBench reproduction archive

Saved on 10 November 2026. This archive covers the three-model generation and Azure GPT-4.1 evaluation completed on 8 November. The subsequent weight-editing literature and proposed experiments are maintained separately.

## Completed coverage

Each model processed 1,680 questions across 13 scenarios and four conditions, giving 6,720 planned cases. The conditions are TEXT, SD, TYPO and SD_TYPO. Qwen2.5-VL-3B is a checkpoint adaptation. The judge is GPT-4.1 version 2025-04-14, which differs from the historical GPT-4 judge in the original paper.

| Model | Nonempty answers | Empty outcomes | Safety labels | Safety filtered | Refusal labels | Refusal filtered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-VL-3B | 6,720 | 0 | 6,549 | 171 | 6,603 | 117 |
| LLaVA-1.5-7B | 6,720 | 0 | 6,414 | 306 | 6,478 | 242 |
| InstructBLIP Vicuna-7B | 5,922 | 798 | 5,773 | 149 | 5,782 | 140 |

All six metric passes finished. An empty generation remains unresolved for both metrics. A filtered judge request remains unresolved for its metric. Refusal and harmful assistance are independent labels. The tables report judged denominators, all-planned bounds and scenario macro rates. Bounds express missingness sensitivity. Full and released-tiny cohorts overlap, with the latter using the authors' 168 IDs and 672 cases per model.

## Notebook navigation

These four files preserve the code from the completed-run snapshots. Public exports clear outputs, attachments and session/account metadata. The private originals retain their code and outputs.

| Completed run | Public source notebook |
| --- | --- |
| LLaVA-1.5-7B, all four conditions | [LLaVA notebook](../notebooks/completed_mm_safetybench/llava_7b.ipynb) |
| InstructBLIP, all four conditions including empty outcomes | [InstructBLIP notebook](../notebooks/completed_mm_safetybench/instructblip.ipynb) |
| Qwen2.5-VL-3B, 1,680 text-only cases | [Qwen text notebook](../notebooks/completed_mm_safetybench/qwen25_text.ipynb) |
| Qwen2.5-VL-3B, 5,040 image cases | [Qwen image notebook](../notebooks/completed_mm_safetybench/qwen25_images.ipynb) |

Qwen's completed study used separate image and text notebooks. Its image notebook executes the frozen worker, archived in [the matching source file](../tools/nb_gen/mm_safetybench_full_release.py). A fresh runtime requires that file at the upload path requested by the notebook, or the preserved worker in Drive. The text notebook requires the archived image run for identity checks. The LLaVA and InstructBLIP notebooks embed their worker source and mount the user's Drive. These are historical source archives, with dependencies on their recorded paths and configurations. Exporting them does not rerun inference.

Earlier notebooks under `notebooks/mm_safetybench_*` retain the preflight, model inventory and generation-development history. IDEFICS, original Qwen-VL and MiniGPT-4 notebook availability does not establish completed answers or judgments for those models. The completed panel is the three models in the table above.

## Results and evaluation code

- [Scenario and condition results](../reports/mm_safetybench_asr_rr_by_scenario.csv) contain 312 rows across three models, full/tiny cohorts, 13 scenarios and four conditions.
- [Condition results](../reports/mm_safetybench_asr_rr_by_condition.csv) contain 24 model/cohort/condition rows, pooled and macro rates, coverage and bounds.
- [Archive manifest](../reports/mm_safetybench_archive_manifest.json) records completed counts, dataset identity, checksums and private-backup verification.
- [Generation and scoring protocol](MM_SAFETYBENCH_LLAVA_REPRODUCTION.md) records checkpoint, prompt-mapping, decoding and evaluator differences and the dated execution history.
- [Azure service integration](../tools/nb_gen/mm_safetybench_azure_pilot.py), [resumable judging](../tools/nb_gen/mm_safetybench_azure_batch.py), [ASR/RR continuation](../tools/nb_gen/mm_safetybench_complete_metrics.py) and [metric reporting](../tools/nb_gen/mm_safetybench_metric_report.py) preserve the evaluation implementation. The five judging source files match the completed private evaluation snapshot.
- [Public export utility](../tools/prepare_mm_reproduction_archive.py) verifies the private snapshot and regenerates the output-cleared notebooks and aggregate CSVs without model or API calls.

The workflow ledger reports USD 28.716136 in cost/reservations within the approved USD 40 ceiling. This is workflow accounting. Azure's final invoice is separate. Human validation remains pending, and exact historical reproduction is not established.

## Data and complete private evidence

The benchmark is available through the [authors' pinned release](https://github.com/isXinLiu/MM-SafetyBench/tree/b80eedea3db312c09ded2082813390f68e750ef3). It links the processed questions and separate image archive. Reuse the exact released fields and image files recorded by the run identities. No new dataset creation is required for these existing runs.

The college Drive retains the source archives, images, raw model answers, per-answer GPT-4.1 records, frozen run configurations, full notebooks with outputs and dated snapshots. The [private results folder](https://drive.google.com/drive/u/2/folders/1b3CX7RKTOOKsUvZTRBGx0yQk7x-_V6ek) requires the owner's account. It has not been made public.

The final snapshot is `Runs/Snapshots_PRIVATE/all_three_ASR_RR_complete_20261109T034959Z_PRIVATE/`. Its 48 recorded files passed SHA-256 verification, covering the six judge ledgers, aggregate reports, frozen evaluation code, cost records and protocol. Its manifest references three completed generation snapshots, which also passed their file checksums. Those generation snapshots include both Qwen notebooks. These checks establish file integrity against the saved manifests.

Per-case prompts, images, model answers and individual judgments remain in that private evidence store under the project's standing publication rules. GitHub contains runnable source, public benchmark pointers, aggregate results and checksums for the saved evidence.

## Verification

The existing CPU judging suite passed 23 tests, and the portable generation suite passed 13 tests. They cover coverage, resumption, configuration checks, missing/empty outcomes, export and separate metric accounting. The tests use fixtures and mocked calls. The recorded completed runs supply the empirical evidence.

```bash
python3 tools/nb_gen/e2e/test_mm_judge.py
python3 tools/nb_gen/e2e/test_mm_portable.py
python3 tools/prepare_mm_reproduction_archive.py --runs /path/to/private/Runs
```
