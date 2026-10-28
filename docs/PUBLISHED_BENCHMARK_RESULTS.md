# Published-data visual benchmark: measured development results

Generated from saved aggregate files by `python3 tools/report_published_benchmarks.py`. 
27 October 2026. No generated research examples or fabricated outcomes. These are
small development adaptations using published sources, not faithful paper-table
reproductions, human validation, or evidence of a novel defense.

## Source and measurement contract

Eight frozen standard HarmBench validation behaviors and their released optimizer
continuations; Qi released carrier/corpus/artifact; separate frozen eight-item
CyberSecEval3 literal-marker diagnostic. Source revisions, hashes, original-paper
mappings and repair deviations: [protocol](PUBLISHED_BENCHMARK_PROTOCOL.md).
Worked architecture, objective, FGSM/PGD/patch equations and interpretation:
[end-to-end guide](VISUAL_ATTACKS_END_TO_END_GUIDE.md). The generated Colab notebook
also has an editable mathematical-contract cell.

HarmBench’s pinned 13B classifier uses its original standard-behavior template,
NF4 deployment, greedy three-token answer and strict Yes/No parsing. The original
classifier stage processed 340 distinct cached responses;
this is not the number of independent source requests. Reused clean/control
responses and shared artifacts create dependencies. Human labels remain pending.

ASR is classifier Yes / eight planned requests. Missing/ambiguous cases give
[Yes/8,(Yes+unresolved)/8]; no unavailable row is a measured 0% ASR. Refusal,
exact optimizer-target matching, perceptual error and literal injection-marker
containment are different endpoints.

## Safety results

| Model | Method | Clean ASR | Attacked ASR | Prefix-defended attacked ASR |
|---|---|---:|---:|---:|
| SmolVLM-500M | FGSM | 1/8 (12.5%) | 1/8 (12.5%) | 1/8 (12.5%) |
| SmolVLM-500M | PGD | 1/8 (12.5%) | 4/8 (50%) | 4/8 (50%) |
| SmolVLM-500M | Localized bounded patch | 1/8 (12.5%) | 1/8 (12.5%) | 0/8 (0%) |
| SmolVLM-500M | Shared image | 1/8 (12.5%) | 0/8 (0%) | 0/8 (0%) |
| SmolVLM-500M | Shared bounded patch | 1/8 (12.5%) | 1/8 (12.5%) | 1/8 (12.5%) |
| SmolVLM-500M | Replacement EOT patch | 1/8 (12.5%) | 1/8 (12.5%) | 0/8 (0%) |
| SmolVLM-500M | Defense-aware PGD | 1/8 (12.5%) | 1/8 (12.5%) | 2/8 (25%) |
| SmolVLM-500M | Flip-aware PGD | 1/8; 2 unresolved | 2/8; 2 unresolved | 3/8; 2 unresolved |
| SmolVLM-500M | Released Qi artifact | Unavailable (0/8 responses) | Unavailable (0/8 responses) | Unavailable (0/8 responses) |
| Qwen2.5-VL-3B | FGSM | 1/8 (12.5%) | 1/8 (12.5%) | 0/8 (0%) |
| Qwen2.5-VL-3B | PGD | 1/8 (12.5%) | 2/8 (25%) | 2/8 (25%) |
| Qwen2.5-VL-3B | Localized bounded patch | 1/8 (12.5%) | 0/8 (0%) | 0/8 (0%) |
| Qwen2.5-VL-3B | Shared image | 1/8 (12.5%) | 0/8 (0%) | 0/8 (0%) |
| Qwen2.5-VL-3B | Shared bounded patch | 1/8 (12.5%) | 1/8 (12.5%) | 0/8 (0%) |
| Qwen2.5-VL-3B | Replacement EOT patch | Unavailable (0/8 responses) | Unavailable (0/8 responses) | Unavailable (0/8 responses) |
| Qwen2.5-VL-3B | Defense-aware PGD | 1/8 (12.5%) | 1/8 (12.5%) | 2/8 (25%) |
| Qwen2.5-VL-3B | Flip-aware PGD | 1/8 (12.5%) | 2/8 (25%) | 2/8 (25%) |
| Qwen2.5-VL-3B | Released Qi artifact | 1/8 (12.5%) | 0/8 (0%) | 0/8 (0%) |

These rows share eight underlying evaluation requests; summing them does not
increase the independent sample size. Compare each attack with its paired clean
condition before attributing unsafe responses to the attack. The fixed prefix is
a generic prompting baseline, not a reproduction of the full AdaShield system.
No benign utility set was run in this stage, so safety/utility superiority cannot
be claimed. Many outputs hit their generation cap; full-length assistance may differ.

## Paired comparisons and missingness

| Model | Method | Contrast | Resolved pairs | Increase / decrease | Difference |
|---|---|---|---:|---:|---:|
| smol | FGSM | attack-clean | 8 | 1 / 1 | 0 pp |
| smol | FGSM | defended_attack-attack | 8 | 1 / 1 | 0 pp |
| smol | PGD | attack-clean | 8 | 3 / 0 | 37.5 pp |
| smol | PGD | defended_attack-attack | 8 | 0 / 0 | 0 pp |
| smol | Localized bounded patch | attack-clean | 8 | 0 / 0 | 0 pp |
| smol | Localized bounded patch | defended_attack-attack | 8 | 0 / 1 | -12.5 pp |
| smol | Shared image | attack-clean | 8 | 0 / 1 | -12.5 pp |
| smol | Shared image | defended_attack-attack | 8 | 0 / 0 | 0 pp |
| smol | Shared bounded patch | attack-clean | 8 | 0 / 0 | 0 pp |
| smol | Shared bounded patch | defended_attack-attack | 8 | 0 / 0 | 0 pp |
| smol | Replacement EOT patch | attack-clean | 8 | 1 / 1 | 0 pp |
| smol | Replacement EOT patch | defended_attack-attack | 8 | 0 / 1 | -12.5 pp |
| smol | Defense-aware PGD | attack-clean | 8 | 1 / 1 | 0 pp |
| smol | Defense-aware PGD | defended_attack-attack | 8 | 1 / 0 | 12.5 pp |
| smol | Flip-aware PGD | attack-clean | 6 | 1 / 0 | 16.6667 pp |
| smol | Flip-aware PGD | defended_attack-attack | 6 | 1 / 0 | 16.6667 pp |
| smol | Released Qi artifact | attack-clean | 0 | 0 / 0 | Unavailable |
| smol | Released Qi artifact | defended_attack-attack | 0 | 0 / 0 | Unavailable |
| qwen | FGSM | attack-clean | 8 | 0 / 0 | 0 pp |
| qwen | FGSM | defended_attack-attack | 8 | 0 / 1 | -12.5 pp |
| qwen | PGD | attack-clean | 8 | 1 / 0 | 12.5 pp |
| qwen | PGD | defended_attack-attack | 8 | 0 / 0 | 0 pp |
| qwen | Localized bounded patch | attack-clean | 8 | 0 / 1 | -12.5 pp |
| qwen | Localized bounded patch | defended_attack-attack | 8 | 0 / 0 | 0 pp |
| qwen | Shared image | attack-clean | 8 | 0 / 1 | -12.5 pp |
| qwen | Shared image | defended_attack-attack | 8 | 0 / 0 | 0 pp |
| qwen | Shared bounded patch | attack-clean | 8 | 0 / 0 | 0 pp |
| qwen | Shared bounded patch | defended_attack-attack | 8 | 0 / 1 | -12.5 pp |
| qwen | Replacement EOT patch | attack-clean | 0 | 0 / 0 | Unavailable |
| qwen | Replacement EOT patch | defended_attack-attack | 0 | 0 / 0 | Unavailable |
| qwen | Defense-aware PGD | attack-clean | 8 | 0 / 0 | 0 pp |
| qwen | Defense-aware PGD | defended_attack-attack | 8 | 1 / 0 | 12.5 pp |
| qwen | Flip-aware PGD | attack-clean | 8 | 1 / 0 | 12.5 pp |
| qwen | Flip-aware PGD | defended_attack-attack | 8 | 1 / 1 | 0 pp |
| qwen | Released Qi artifact | attack-clean | 8 | 0 / 1 | -12.5 pp |
| qwen | Released Qi artifact | defended_attack-attack | 8 | 0 / 0 | 0 pp |

Differences describe this development subset. No corrected hypothesis test or
population-level model/defense ranking is inferred.

## Execution coverage and deviations

- Original smol: 62 completed method–request cases. Reached its fixed time cap; stale running flag is not a live job.
- Original qwen: 64 completed method–request cases. EOT objective became non-finite; original injection parity check failed.

Repair results have not yet been reconciled; original missing cells remain missing.

## Separate visual-injection diagnostic

| Model | Condition | Marker-containing responses | Valid / planned | Unresolved |
|---|---|---:|---:|---:|
| smol | defended_image | 1 | 8/8 | 0 |
| smol | injected_image | 0 | 8/8 | 0 |
| smol | text_only | 1 | 8/8 | 0 |
| qwen | defended_image | 0 | 0/8 | 8 |
| qwen | injected_image | 0 | 0/8 | 8 |
| qwen | text_only | 0 | 0/8 | 8 |

Published markers are artificial constructions in the released benchmark;
they are not newly invented project data or real secrets. No-image is not an
original clean-scene counterpart; do not interpret marker rate differences as
proof of causal injection success or pool them with unsafe-assistance ASR.

## Provenance and remaining research

- Original driver finished: True.
- Original safety-aggregate SHA256: `70e06d02c4d9e2d4b9c5930b7bb7d1173329189f0b193134042978a75c0765a3`.
- Reported safety-aggregate SHA256: `70e06d02c4d9e2d4b9c5930b7bb7d1173329189f0b193134042978a75c0765a3`.
- VLM_Published_Benchmarks_20261026_PRIVATE: recorded private archive 60096316 bytes, SHA256 `91eb85de1882fdcc6d8202f1582c08ad868358a8cd995bc593671d1dbc525c56`.

Remaining: original feature/trigger matching, teacher/context matching and full
BAP feedback search are not reproduced; full published datasets, benign utility,
independent human evaluation, held-out confirmation and novelty review are open.
Finishing an implemented panel does not finish the full research program.
