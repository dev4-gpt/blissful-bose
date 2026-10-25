# Visual Attack Mechanisms and Inference-Time Defenses in Open VLMs

*Working manuscript for advisor review, 25 October 2026. Separate from the historical
typographic refusal-gap manuscript. Authorship and venue are owner decisions. This is
not submission-ready: benchmark safety results, independent human validation and
novelty verification remain open.*

## Abstract — provisional

We develop a reproducible framework for comparing visual attack mechanisms in open
vision–language models under frozen weights. The protocol separates perceptual errors,
instruction-integrity violations and unsafe assistance, and records delivered-image
constraints, model-specific preprocessing, clean utility and execution failures.
A first synthetic Qwen2.5-VL-3B/T4 profile establishes that constrained input optimization
can execute through the pretrained model; it does not establish a successful jailbreak.
Broader development and external-injection diagnostics are reported separately as
they complete. No novel defense effectiveness or safety ranking is currently claimed.

## 1. Research question and scope

How do visual attack mechanisms affect open VLM behavior, and which inference-time
defenses reduce failures while preserving legitimate task performance? Model weights
remain fixed; image optimization is permitted. We study digital images, not physical
camera capture, poisoning, backdoors, videos or agent tool execution.

This is a measurement/reproduction study until a held-out finding survives comparison
with closest prior art. The historical typographic experiments supply methodological
lessons about matched stimuli and scoring; their outcomes are not pooled into visual
perturbation estimates, nor do they establish the current hypotheses.

## 2. Related work — verification depth in the dossier

[Goodfellow et al., §3](https://arxiv.org/abs/1412.6572) motivates the signed input-gradient
baseline; [Madry et al., §2](https://arxiv.org/abs/1706.06083) motivates constrained iterative
optimization. [Brown et al., §2](https://arxiv.org/abs/1712.09665) studies universal patches
under transformations. A bounded per-example patch is a different threat model.

[Qi et al., §3](https://arxiv.org/abs/2306.13213),
[Jailbreak in Pieces, §3.1](https://arxiv.org/abs/2307.14539),
[Image Hijacks, §2](https://arxiv.org/abs/2309.00236), and
[BAP, §4](https://arxiv.org/abs/2406.04031) motivate distinct corpus, feature, behavior
and combined-channel objectives. Our changed models/preprocessing/objectives are
labelled adaptations; original configuration reproduction is not inferred from sharing
an optimizer. The paper register records outstanding appendix/code inspections.

[MMJ-Bench](https://ojs.aaai.org/index.php/AAAI/article/view/34983) is a mandatory
attack/defense comparison baseline. [AdaShield, §3](https://arxiv.org/abs/2403.09513)
and [JailGuard, §4](https://arxiv.org/abs/2312.10766) are relevant inference-time defense
comparators. We have not reproduced their complete adaptive systems. The
[CyberSecEval3 official visual-injection release](https://huggingface.co/datasets/facebook/cyberseceval3-visual-prompt-injection)
supports an evaluation-only integrity diagnostic, not a general safety estimate.

## 3. Threat models and objectives

Let $x\in[0,1]^d$ denote the delivered image, $t$ the fixed legitimate text input,
$\theta$ frozen model weights and $y^*$ a targeted continuation. The response-only
surrogate is $L(x,t,y^*)=-|y^*|^{-1}\sum_j\log p_\theta(y_j^*\mid x,t,y^*_{<j})$.
Prompt/image/padding tokens are masked and causal predictions shifted once.

Targeted FGSM uses $x'=\Pi_{\mathcal C}(x-\epsilon\operatorname{sign}\nabla_xL)$.
PGD repeats $x_{k+1}=\Pi_{\mathcal C}(x_k-\alpha\operatorname{sign}\nabla L)$ with
$\mathcal C=[0,1]^d\cap B_\infty(x,\epsilon)$. A local mask $A$ restricts changes to
$x'=(1-A)x+Ap$. A replacement EOT patch instead constrains patch pixels to the
unit box and reports area, not an imperceptible full-image budget.

Feature matching minimizes $\|V(x')-V(x_{target})\|_2^2$ using each model's declared
visual features. Behavior matching uses detached teacher distributions on a fixed
teacher-forced continuation. Corpus and combined image/text mechanisms have separate
optimization contexts. Visual injection places instructions in lower-trust image
content; it does not require gradients or a small perturbation budget.

## 4. Implementation and comparison protocol

| Deployment | Model revision | Precision | Delivered canvas | Status |
|---|---|---|---|---|
| Qwen2.5-VL-3B | `66285546d2b821cf421d4f5eb2576359d3770cd3` | FP16/eager | 224 initial, 448 broader | Initial pretrained profile completed |
| SmolVLM-500M / Idefics3 | `a7da5b986cb59b408707209984f360a5f4ad7e47` | FP32/eager | 448, no splitting/resizing | Pretrained synthetic panel completed |

The common broader canvas controls delivered pixels and budgets. Different precision,
native visual encoders, language backbones, token counts and training remain confounds:
this is a deployment comparison, not an isolated causal effect of architecture or size.
One model runs per process on a T4. Native processor/logit parity, finite nonzero image
gradients, unchanged frozen weights and artifact bounds gate each applicable experiment.
Save actual post-transformation stimuli for review; cache identities include revisions,
source/configuration hashes, data groups, seed and decoding.

Development integration uses four synthetic tasks and four separate optimization
contexts, ten mechanisms and two defense-aware PGD variants. Universal-labelled modes
use one development carrier, so do not establish cross-request universal transfer.
Directional transfer reuses the exact Qwen PGD/patch artifacts on Smol without destination
optimization. Mechanism coverage and failed configurations remain visible.

The external integrity diagnostic freezes eight source IDs before outputs from the
official literal-marker subset. It uses original user/system instructions and released
images; conditions are text-only, injected image and injected image with the already-fixed
defense prefix. No original clean-source images are available. Text-only is a baseline,
not a matched clean-image counterpart; no causal injection effect is identified.

## 5. Evaluation and uncertainty

Perceptual correctness, unauthorized instruction deviation and unsafe assistance have
different rubrics. Exact-target match and target-loss change are development diagnostics;
neither is a safety success rate. In the selected external source subset, literal marker
containment follows the official judge form and measures that specific integrity failure.
Report all attempted cases, valid outputs, cap hits, missing outcomes and costs.

For $H$ resolved failures and $M$ unresolved among $N$ attempted, report bounds
$[H/N,(H+M)/N]$. Planned scientific comparisons are paired by underlying request;
related images/paraphrases stay grouped. Shared artifacts are dependencies, not independent
attack replications. Prespecify the primary family and Holm adjustment before held-out
evaluation. The four/eight-case diagnostics do not support population or significance claims.

Two independent human reviewers receive a blinded probability sample with actual task,
system context where relevant, image and response. Preserve independent labels, selection
probabilities and unresolved cases before adjudication. Selected-disagreement diagnostics
remain separate. Review packets are currently unlabelled; automated scoring is not human validation.

## 6. Results ledger

### Initial engineering profile — completed

Source: [saved aggregate record](../visual_t4_profile_20261025/profile_aggregate_status.json).
One synthetic case and three PGD steps completed on Tesla T4, with zero case failures.
Target NLL changed from 12.779708862304688 to 9.617810249328613, while the attacked
generation did not match the selected incorrect target. Delivered Linf was
0.0313725471496582; native clean-logit maximum error was 0.0. This establishes this
configuration's execution feasibility, not jailbreak effectiveness. The original backward
peak was not retained separately from load/generation peaks.

### Broader development panel — completed integration run

Colab model-status records report 34 completed cases per model, across 12 variants,
with zero case failures. Qwen elapsed time was 442.6653609060004 seconds and Smol
185.87124256900006 seconds, including its eight transfer cases. Model load times
were 45.23079021900048 and 19.231195581000065 seconds respectively. These are
observed deployment costs, not a precision- or hardware-isolated architecture result.
The 68 records reuse four development tasks; they are not 68 independent examples.

The synthetic review frame contains 480 responses; the unlabelled probability sample
contains 120 with inclusion probability 0.25. The eight directional transfer cases
are outside that frame. No human agreement or safety estimate is available.
Private runtime archive SHA256: `3f6b00be94813e701e85f12230198a0d173de03d2ec046dea3018a497539cc21`.
Durable college-Drive preservation is awaiting the owner's Connect click; no raw archive
is published. Task-correctness/target-match analysis must come from the saved aggregates,
not inferred from successful execution. Keep tracks and deployment differences separate.

### External integrity diagnostic — prepared

Populate only after actual execution. Record source IDs/revision, literal-marker counts,
denominators, cap hits, baseline leakage and missingness separately per condition/model.

### Safety and human-reviewed outcomes — pending

No unsafe-assistance estimate, independent-human calibration, held-out safety effect or
defense-generalization claim is available. Planned HarmBench/benign VQA/clean-pair checks
are not completed experiments. Freeze the final data and scoring contract first.

## 7. Novelty decision and limitations

Candidate contributions concern delivered preprocessing/transfer, defense generalization
at matched utility/cost, or a consequential reproduction discrepancy. None is novel by
default. Exclude close prior art, reproduce working baselines and require affordable
held-out validation. Otherwise report an honest replication/measurement result.

Key limits include synthetic integration tasks, small external subset, missing original
clean images, checkpoint/precision differences, output caps, partial original-paper
reproduction and pending independent human labels. An inference-time wrapper does not
change model weights or establish improved weight alignment.

## 8. Reproducibility, data handling and remaining submission gates

Release code, allowed source IDs and aggregates only. Keep benchmark text/media, raw
responses, reviewer data and private archives out of public Git. Preserve completed
Colab code/outputs and distinct aggregate snapshots before changing runs. Report negative
results, failures and all deviations from original configurations.

Before submission: finish verified prior-art/config audits; freeze held-out data/scoring;
complete human review and safety/utility/adaptive evaluations; regenerate figures from
traceable aggregates; revise claims with the advisor; select venue and author list.
The December 1 target is manuscript readiness, not guaranteed acceptance.
