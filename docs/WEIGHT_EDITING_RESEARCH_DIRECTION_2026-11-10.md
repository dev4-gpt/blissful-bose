# Research direction — safer VLM answers through weight editing

Aryaman Singh Dev · Working research brief · 10 November 2026

> **Correction banner, 11 November 2026.** This brief was written against arXiv `2602.09870v1`.
> The current version is **v4** (8 November 2026), accepted to NeurIPS 2026, and it **supersedes
> two factual premises below**: that the published safety experiments are text-only, and that
> applying Steer2Edit to a VLM is an unpublished adaptation. See §8 at the end of this file and
> [the deep study](STEER2EDIT_DEEP_STUDY_AND_CONTRACT.md) for the verified replacement. The
> equations transcribed in §2 are **unchanged** in v4 and remain correct.

## 1. The owner's goal and the starting evidence

Develop a method that changes a small part of a pretrained vision-language model's stored weights using forward-pass calibration and a mathematical update. The edited checkpoint should produce less harmful assistance and appropriately refuse harmful requests while preserving useful answers to benign requests. Evaluate image understanding and answer quality as well as safety.

The owner requires no gradient training or fine-tuning. Calibration, computing activations, selecting settings and solving a matrix equation still consume data and compute. Loading an inference adapter connects a checkpoint to our runner. It does not itself align the checkpoint.

The completed MM-SafetyBench panel supplies the baseline. Each model processed 1,680 questions across 13 scenarios and four conditions, giving 6,720 planned cases. The recorded judge is Azure GPT-4.1 version 2025-04-14.

| Model | Nonempty answers | Empty outcomes | Safety labels | Refusal labels |
| --- | ---: | ---: | ---: | ---: |
| Qwen2.5-VL-3B | 6,720 | 0 | 6,549 | 6,603 |
| LLaVA-1.5-7B | 6,720 | 0 | 6,414 | 6,478 |
| InstructBLIP Vicuna-7B | 5,922 | 798 | 5,773 | 5,782 |

Six judging passes completed. Azure filtered some requests, and the empty outputs remain unresolved for safety and refusal. These differences require denominator and coverage reporting. Qwen2.5 and the updated judge are documented adaptations. [Completed archive and aggregate results](MM_SAFETYBENCH_ARCHIVE.md)

The professor's suggested strategy is to study one paper deeply, recover its method and resources, reproduce a specific result, diagnose a limitation, and test one targeted improvement. The first milestone is a verified reproduction and a clearly evidenced failure on one target, with additional models reserved for later transfer validation.

<!-- pagebreak -->

## 2. Recommended primary paper — Steer2Edit

Steer2Edit, by Chung-En Sun, Ge Yan, Zimo Wang and Tsui-Wei Weng, derives component-level weight updates from activation directions. It provides the closest algorithmic starting point for the owner's requirement of persistent edits without gradient fitting. The recommendation remains subject to source/code audit and the owner's selection. [Versioned paper](https://arxiv.org/html/2602.09870v1) · [Author project](https://lilywenglab.github.io/Steer2Edit/)

Its core update is:

```text
W′ᵢ = Wᵢ + ΔWᵢ
ΔWᵢ = λᵢ ûᵢ k̂ᵢᵀ
ûᵢ = vᵢ / ‖vᵢ‖₂
k̂ᵢ = Wᵢᵀvᵢ / ‖Wᵢᵀvᵢ‖₂
gᵢ = cos(vᵢ, Wᵢμᵢ)
λᵢ = sign(gᵢ) max(|gᵢ| − ρα, 0) / [ρ(1 − α)]
```

Here i indexes an editable attention or MLP component. Wᵢ maps its input to the residual stream. The vector vᵢ is a steering direction in that output space. The unit vector ûᵢ selects the output direction, and k̂ᵢ selects which input features activate the edit. The mean input μᵢ determines the alignment score gᵢ. The magnitude λᵢ can have either sign. The sparsity parameter satisfies 0 ≤ α < 1, and ρ > 0 controls regularization. The direction normalizations require nonzero norms. Attention and MLP components use separate budgets in the experiments. The ordinary forward pass then uses the saved W′. [Sections 3.1–3.5](https://arxiv.org/html/2602.09870v1#S3)

The official repository contains generation, direction extraction, activation means, editing and evaluation commands. Its probing data include attack prompts and benign Alpaca examples. Audit dataset membership and model-generated refusal selection before reusing these data. [Official resources](https://github.com/Trustworthy-ML-Lab/Steer2Edit)

The published safety experiments use LLaMA-2-7B-Chat and Mistral-7B-Instruct-v0.2, text jailbreaks and downstream text-task accuracy. Their main safety endpoint is refusal. A VLM/MM-SafetyBench experiment is an adaptation. Our evaluation adds semantic harmful-assistance labels, empty-output tracking, benign over-refusal and image-dependent utility. [Section 4.2.1 and Appendices B–F](https://arxiv.org/html/2602.09870v1#S4)

<!-- pagebreak -->

## 3. How the other new papers fit

These methods supply mechanisms and comparators. The immediate project has one primary reproduction target. Additional methods enter experiments when needed to distinguish the proposed improvement.

| Paper | Intervention and source evidence | Role and material boundary |
| --- | --- | --- |
| MARS | Text refusal directions, neutral-image centering, a positive gate and adaptive activation strength. MM-SafetyBench appears in Appendix A. | Runtime steering comparator. Its published model panel differs from our three checkpoints. [Paper](https://arxiv.org/html/2606.31876v2) |
| ShiftDC | Projects the visual-versus-caption activation difference onto a safety axis, then subtracts that component. Tests MM-SafetyBench. | Helps diagnose which part of an image-induced shift matters. Its attack metric uses refusal keywords, requiring separate interpretation from GPT-labeled harmful assistance. [Paper](https://arxiv.org/html/2502.13095v1) |
| CMRM | Uses text-only and corrupted-image hidden states for dataset-level or per-item corrections. Tests VLSafe and modified JailbreakLLMs. | Earlier representation-calibration method. The subtraction convention requires clarification against its own earlier equations. An author implementation was not located in the scoped review. [Paper](https://arxiv.org/html/2410.09047v1) |
| ECSO | Checks the initial answer, then uses a query-aware caption and text-only regeneration if flagged. Tests MM-SafetyBench. | External comparison for safety gains obtained through extra inference. Optional SFT experiments are a separate preparation track. [Paper](https://arxiv.org/html/2403.09572v4) |
| EVA | Optimizes internal safe target values, then edits decoder weights using a preservation-aware solve. Tests VLMs on MM-SafetyBench. | Closest direct VLM weight-editing precedent. Its target optimization falls outside a strict forward-pass-only preparation. [Paper](https://arxiv.org/html/2605.14750v1) |
| Unsafe Weights Manipulation | Scores safe/unsafe activation differences and rescales selected weights. Primarily studies contrastive encoders and includes a LLaVA vision-encoder captioning test. | Additional no-training weight-edit baseline. Editing the vision encoder alone cannot change text-only inference that never uses that encoder. Its captioning endpoints differ from benchmark jailbreak ASR. [Paper](https://arxiv.org/html/2503.11742v2) |

MARS, ShiftDC and CMRM modify runtime activations. ECSO changes the inference procedure. Steer2Edit, EVA and UWM persist changes in weights. These mechanisms offer distinct explanations for safer-looking outputs, so evaluate the final delivered answer and preserved capability in each case.

<!-- pagebreak -->

## 4. Candidate research question and novelty test

Does a text-derived Steer2Edit update select appropriate components when harmful intent is carried through an image? If a reproducible failure appears, can calibration with matched text and image forms improve component selection at comparable harmful-assistance ASR and retained utility?

This is a proposed evidence gap. A simple transfer to a new checkpoint or a combination of existing components has unestablished novelty. First compare the failure against EVA, UWM and existing multimodal steering research. Identify precisely which setting or mechanism the closest work already handles.

| Claim under consideration | What is already established | Evidence our paper would need |
| --- | --- | --- |
| Store steering effects in weights | Steer2Edit already derives component-level updates. | A specific multimodal failure and a reproducible improvement beyond its unmodified rule. |
| Improve VLM safety with weight edits | EVA and UWM already do this in their respective settings. | Matched comparison explaining the value of our calibration or selection change. |
| Use text to improve visual safety | MARS and related calibration methods already study transfer. | Demonstrated benefit from the proposed persistent edit and analysis of when transfer succeeds or fails. |
| Increase refusal | Existing methods already optimize or report refusal. | Lower semantic harmful assistance, preserved benign answers and stable visual capability, including failure coverage. |

One candidate test changes only calibration and component scoring. Compare the released text-only recipe, a pooled text/image recipe and a paired recipe with matched data volume and edit budget. A shuffled-pair control tests whether pairing contributes beyond extra data. Actual equations depend on the observed failure and source audit, so this brief makes no performance prediction.

The prior working study also described a benign-pair penalty in an analytic projection edit. Keep that as an alternative design to assess against Steer2Edit and preservation-based editing literature. Avoid fitting both approaches to the same final test and selecting the winner afterward.

Useful failure outcomes include a method that improves refusal keywords but preserves harmful assistance, an edit that destroys OCR, and a calibration direction that fails under a held-out carrier. A strong paper can explain a consequential negative finding if its controls establish what fails and why the measurements matter.

<!-- pagebreak -->

## 5. Focused execution sequence

| Stage | Work | Reviewable completion evidence |
| --- | --- | --- |
| Study | Read Steer2Edit end to end, verify official implementation and complete its direct reference inventory. Trace critical direction-extraction and evaluation dependencies. | Equations with every symbol defined, code-path map, dataset/test inventory, source-specific numerical results and unresolved settings. |
| Native reproduction | Use one supported original checkpoint and one prespecified safety experiment. Freeze release revision, data splits, probing response selection and settings search. | Same native metric, saved outputs, a result comparison and all deviations. Checkpoint access and compute feasibility are established before launch. |
| VLM diagnosis | Select one target after the native check. LLaVA-1.5-7B has a completed baseline and shared lineage with several VLM comparisons. | Unmodified edit versus unchanged inference, four-condition routing and a measured limitation. Archived baseline reuse requires matching identities. |
| Improvement | Alter one component justified by that limitation. | Candidate specification, matched original-method control, parameter/data budget and component ablations. |
| Confirmation | Freeze the method and test unexamined items after overlap checks. | Paired uncertainty, benign utility, image capability, coverage and independently reviewed judgments. Add a second model only for the final transfer question. |

Before changing weights, test disabled-intervention parity, exact edit scope and reversible restoration. Verify that saving and reloading the edited checkpoint preserves the intended outputs. Record base and edited model fingerprints, calibration IDs, direction tensors, component choices, coefficients and settings. Keep each configuration in a separate resumable run identity.

The written hypothesis and primary endpoint precede the scientific run. New GPU and paid judging execution need the owner's applicable authorization. The old judging budget covered the completed baseline. Changed weights produce new answers requiring new judgments.

## 6. What we must measure

Harmful-assistance ASR and refusal are separate outcomes. Report each numerator and its judged denominator. On benign requests, measure over-refusal and correctness/useful assistance. On image-dependent tasks, measure OCR, visual question answering or another source-defined capability endpoint. Also record empty/truncated outputs, failed calls, unresolved judgments, editing cost, inference latency and memory.

The released four conditions preserve benchmark coverage. Their text wording can differ, so additional matched controls are required to attribute a difference to image presence or carrier. Group all variants of one question together in calibration and evaluation splits. Treat previously inspected MM-SafetyBench outcomes as exploratory for the new-method decision.

<!-- pagebreak -->

## 7. Reading order, resources and present status

Begin with Steer2Edit Sections 2–3 for the mechanism, Section 4.2.1 for the safety experiment, Appendix B for probing data, Appendix C for settings search, and Appendices D–F for trade-offs and component ablations. Then follow the official safety pipeline in its README. The original experiments, a port to our VLM and our eventual improvement need their own provenance records.

| Resource | Purpose |
| --- | --- |
| [Steer2Edit paper](https://arxiv.org/html/2602.09870v1) and [official repository](https://github.com/Trustworthy-ML-Lab/Steer2Edit) | Primary recommended reproduction and extension target. Full implementation execution and exact checkpoint/resource audit remain pending. |
| [EVA paper](https://arxiv.org/html/2605.14750v1) and [official repository](https://github.com/wanglne/EVA) | Closest VLM safety editing comparison and evaluation precedent. |
| [UWM paper](https://arxiv.org/html/2503.11742v2) and [official repository](https://github.com/Moreno98/UWM) | Forward-pass calibration and selective stored-weight manipulation. |
| [MARS code](https://github.com/Moreno98/MARS) and [ShiftDC code](https://github.com/Renovamen/ShiftDC) | Inspected runtime-hook and reference-activation implementations. |
| [ECSO project](https://gyhdog99.github.io/projects/ecso/) and [official repository](https://github.com/gyhdog99/ECSO) | Query-aware captioning, self-checking and text-regeneration comparison. |
| [Independent paper studies](TRAINING_FREE_SAFETY_RESEARCH.md) | Deeper four-method review, equations, selected native tables, limitations and dependency boundaries. |
| [Source coverage](../reports/training_free_source_coverage.csv) and [reference inventory](../reports/training_free_reference_dependencies.csv) | Current nine-paper extraction and reading register. New weight-edit roots still require the complete standing dependency audit. |

The completed empirical work in this brief is the three-model MM-SafetyBench baseline. Runtime-intervention primitives have CPU tests. No new paper has been empirically reproduced in this next stage, and no weight-edited VLM has been evaluated. The focused recommendation is Steer2Edit, with one initial VLM and one improvement chosen after diagnosis. The method's novelty, benefit and feasibility remain open.

The reproduction archive was pushed first, as requested. This new-paper brief is kept separate from that GitHub commit.

<!-- pagebreak -->

## 8. Verified corrections, 11 November 2026

Source audit completed against the versioned paper and the pinned repository. Full detail in
[the deep study](STEER2EDIT_DEEP_STUDY_AND_CONTRACT.md) and
[the reproduction contract](STEER2EDIT_REPRODUCTION_CONTRACT.md). Three items in §2 and §4 above
change; everything else in this brief stands.

**C1. Version and status.** The paper has four versions: v1 10 Feb 2026, v2 3 Mar 2026, v3 4 Nov
2026, v4 8 Nov 2026. It is **accepted to NeurIPS 2026**. v1 has 26 bibliography entries and
Appendices A–G; v4 has 37 and Appendices A–Q. The repository is pinned at
`86382c2f44fdfda2bafe80faf09634e6d729562c` (30 Sep 2026), which **predates v3/v4**, so the
appendices added during review have no released implementation. The editing equations are identical
in v1 and v4, so §2's transcription needs no change.

**C2. The text-only premise is superseded.** §2 states "The published safety experiments concern
text LLMs... A VLM/MM-SafetyBench experiment is an adaptation. Its performance and novelty remain
open." v4 **Appendix N, Table 13** applies Steer2Edit to **Qwen2.5-VL-7B-Instruct** by editing the
LLM backbone with the same pipeline, reporting 98.2% safety against 73.9% unedited at preserved
utility (76.0 vs 76.6), at ρ_attn 0.3, ρ_mlp 0.5, α 0.5. v4 also adds a 70B result (Table 12), a
diffusion-LLM result (Table 14) and an OR-Bench over-refusal table (Table 11).

So "Steer2Edit can be applied to a VLM" is now published and may no longer be claimed as our
contribution. What Appendix N does **not** do, in its own words, is test images: "Safety and
utility are evaluated on **text-only benchmarks**." The directions are text-derived, the attacks
are text suffixes, no image enters the pipeline, and the vision encoder is explicitly untouched.

**C3. The research question narrows, and survives.** §4's question should be restated as:

> Do text-derived directions and component importance scores select the right components when the
> harmful intent is carried by the **image** rather than the text, and does calibration with
> matched text/image pairs fix component selection at comparable harmful-assistance ASR and
> retained image-grounded utility?

This is a better position than the brief's, for three reasons. The authors have supplied the
text-only VLM baseline we would otherwise have had to establish. Our completed MM-SafetyBench panel
already covers exactly the image-carried conditions (TEXT / SD / TYPO / SD_TYPO) Appendix N omits.
And the novelty claim is now stated against a specific published table rather than against an
absence. The novelty comparison against EVA, UWM and multimodal steering in §4 above still stands
and still has to be run.

**C4. Two inherited assumptions that the brief could not have known.** Both come from reading the
released code rather than the paper, and both bear directly on the VLM adaptation.

- The positive set is **not filtered for refusals**, despite Appendix D saying it consists of
  refusal responses. `generate_response.py` keeps the first sampled response to every prompt with no
  judge and no selection. This is approximately true for LLaMA-2-7B-Chat under a safety system
  prompt, and it is exactly the assumption that breaks when a VLM complies with image-carried
  attacks: compliances would enter the positive set and partly invert the direction. Our adaptation
  must decide and record a selection rule rather than inherit silence.
- The probing contrast holds the **prompt fixed and swaps the response**: `extract_directions.py`
  pairs each malicious question with an Alpaca response. The paper describes different prompts.
  Copying the paper's prose rather than the code would produce a different direction.

**C5. A limitation we can target.** At the published llama2 configuration the Elastic-Net gate is
`ρ_attn·α = 0.144` for attention heads and `ρ_mlp·α = 0.440` for MLP neurons — a 3.05× stricter gate
— with surviving heads amplified 3.06× more. The paper's finding that "MLP neurons receive near-zero
coefficients" (Figure 6) is therefore **partly produced by the budget asymmetry**, not purely by
where safety lives. Additionally, because an MLP neuron has a one-dimensional input, the magnitude
of its mean activation cannot affect `|g|` at all, only its sign, so the two component families are
scored by structurally different quantities under one shared `α`. Per-component-type normalization
of `g` before thresholding is a cheap, well-motivated candidate improvement, and it is independent
of the multimodal question, so it can be tested on the native setting first.

**C6. Feasibility.** Both jailbreak attacks are **pre-released** — GCG suffixes for 100 AdvBench
behaviours and ADV-LLM suffixes, for both `llama2-7b` and `mistral-7b`. No attacker needs to be
trained or run. The native endpoint is a 32-string keyword list in `utils.py`, not a judge, so the
native reproduction needs **no paid judging**. Probing is 100 + 100 prompts. The main costs are the
gated LLaMA-2-7B-Chat download, GPU inference, and ~13 GB of local disk per evaluated configuration
because each edit is materialized as a full checkpoint copy.

**C7. Scope question: one paper deeply, or all seven reproduced.** The owner asked on 11 November to
reproduce "each and every paper". That conflicts with the professor's recommendation recorded in §1
and with this brief's own single-paper strategy, so it is a decision rather than an assumption.

The two are reconcilable if they are sequenced rather than run in parallel, because the comparators
are not all needed for the same claim:

| Priority | Paper | Why, and what it costs |
| --- | --- | --- |
| 1 | **Steer2Edit** native, text LLM | The primary target. Attacks pre-released, endpoint is a keyword list, so no paid judging. Contract written. |
| 2 | **Steer2Edit** MM-SafetyBench four conditions | Our actual research question. Reuses the completed LLaVA baseline if identities match. Needs new judging. |
| 3 | **EVA** (2605.14750) | **Required** for the novelty claim: the closest VLM weight-editing precedent on MM-SafetyBench. Without it we cannot say our edit differs from established work. |
| 4 | **UWM** (2503.11742) | Required second weight-edit comparator; note it edits the vision encoder, so its endpoints differ from benchmark ASR. |
| 5 | MARS, ShiftDC | Runtime-steering comparators. Useful for the trade-off story, not load-bearing for a weight-editing novelty claim. |
| 6 | CMRM, ECSO | Background comparators; CMRM has no located author implementation, ECSO changes the inference procedure rather than the weights. |

Items 1-4 are the defensible programme: they are what a reviewer needs to accept a novelty claim
about persistent multimodal safety edits. Items 5-6 are optional and should not delay 1-4. Attempting
all seven at once would multiply the judging cost, which is the binding constraint, and would leave
none of them reproduced to the standard already set by the MM-SafetyBench panel. Recommendation:
commit to 1-4 in order, and treat 5-6 as reading plus selective re-analysis unless a specific claim
requires their numbers.

<!-- pagebreak -->

## 9. Primary-paper reselection, 11 November 2026

The owner challenged the Steer2Edit selection: the goal is VLM safety through weight editing, and
the audit established that Steer2Edit never puts an image in its pipeline. The master prompt
requires that an incompatibility be named exactly before a replacement is proposed. This section
does that, then compares candidates against the owner's stated requirements.

### 9.1 The exact conflict

Steer2Edit's safety setting is text jailbreaks (GCG, ADV-LLM suffixes) on text LLMs. Its one
vision-language result, v4 Appendix N, edits the LLM backbone of Qwen2.5-VL-7B-Instruct and then,
in the authors' words, evaluates "safety and utility ... on **text-only benchmarks**". The vision
encoder is untouched, the directions are text-derived, and no image is present at calibration or at
evaluation. It therefore cannot, as published, answer any question about harmful intent carried by
an image, and it reports no MM-SafetyBench result of any kind.

That is the conflict: **the method is modality-blind by construction, while the project's goal is
modality-specific.** Using it as the primary paper would mean reproducing a text result and then
inventing the multimodal part ourselves — which is research, but it is not "reproduce a published
experiment, diagnose its limitation, improve one component."

### 9.2 Requirement matrix

Owner requirements are from §1 of this brief. Verified 11 November against the versioned papers and
the released code; "~" marks a partial or conditional satisfaction.

| Requirement | Steer2Edit (2602.09870v4) | EVA (2605.14750, TPAMI 2026) |
| --- | --- | --- |
| Persistent update to stored weights | yes, rank-1 on `o_proj`/`down_proj` | yes, least-squares update to `W_down` |
| No gradient training or fine-tuning | **yes, strictly** — closed form, zero backprop | **~** weights frozen (`set_requires_grad(False, model)`); Adam optimizes one d-dim vector `v*`, then a closed-form solve |
| Native vision-language method | ~ backbone only, appendix | **yes**, designed for VLMs |
| Images present in calibration | **no** | **yes** — Stable-Diffusion images plus OCR/typography images; visual keys located by cross-modal attention |
| MM-SafetyBench SD / TYPO / SD+TYPO reported | **no** | **yes**, Table III columns |
| Model overlap with our completed baseline | no (LLaMA-2-7B, Mistral) | **yes — LLaVA-1.5-7B exactly** |
| Harmful-assistance endpoint | keyword refusal list only | ASR, plus utility on MM-Vet-v2, MMMU, MMStar |
| Over-refusal measured | ~ OR-Bench added in v3/v4 | utility benchmarks, not a dedicated over-refusal set |
| Code and data released | code yes, but commit predates the v3/v4 appendices | **yes** — MIT, pip-installable, 200 records with fixed visual-token indices, image bundle, HF model collection |
| Expensive steps pre-computed | attacks pre-released | harmful token (`subject`), refusal target and `attn_token_idx` all pre-released per model |
| Platform feasibility | 7B text model | LLaVA-1.5-7B, comparable size |

EVA wins decisively on the five requirements that define the project (native VLM, images in
calibration, MM-SafetyBench conditions, baseline model overlap, released multimodal artifacts).
Steer2Edit wins on exactly one: strict absence of any gradient.

### 9.3 The one decision this turns on

EVA's step 5 optimizes a target value `v*`. The released code
(`src/eva/editing/image/core.py:219-297`) creates `delta = torch.zeros(hidden_size,
requires_grad=True)`, calls `set_requires_grad(False, model)`, runs `torch.optim.Adam([delta])` and
`loss.backward()`. **No model parameter receives a gradient**; backpropagation passes through a
frozen model to fit one vector of size `d`, and the weight change itself is a closed-form
least-squares solve.

So EVA is not fine-tuning and does not train the model. It is also not strictly forward-pass-only.
Whether that satisfies "without gradient training or fine-tuning" is the owner's ruling, and it is
the only thing standing between EVA and selection. The brief's §1 already allows that "calibration,
activation collection, settings selection and mathematical fitting still require data and compute",
which reads as permitting it.

### 9.4 Recommendation

Make **EVA** the primary reproduction target and keep **Steer2Edit** as the text-LLM mechanism
comparator. Nothing done so far is wasted: Steer2Edit is the strictly-no-gradient baseline that any
claim about needing `v*` optimization must beat, the completed audit is itself a contribution
(ten paper/code discrepancies, the budget-asymmetry result), and its native reproduction is cheap
because both attacks are pre-released and the endpoint needs no paid judging.

Proposed reproduction target for EVA, pending the ruling and an audit of the same depth already
applied to Steer2Edit: **Table III, LLaVA-1.5-7B, the SD / TYPO / SD+TYPO columns**, against the
`Vanilla` row we can cross-check with our own completed baseline.

The headline to scrutinize is that EVA reports ASR **0.00 in 14 of 18 cells** of Table III.
Near-universal zero is exactly the pattern that a permissive ASR metric or blanket refusal
produces, and the baselines AdaShield-A and VLGuard report many 0.00 cells too. Our completed
semantic harmful-assistance judging, over-refusal measurement and image-grounded capability checks
are the natural test of whether 0.00 survives a stricter endpoint and at what capability cost.
That is a sharper and more defensible paper than transferring a text-only method to images.

### 9.5 Candidates checked and set aside

Searched 11 November for closer-fit 2026 work on persistent VLM safety weight edits. Nothing
displaced EVA. GuardAlign (2602.24027) is training-free but explicitly "keeps parameters
unchanged", so it is not weight editing. 2603.27240 repairs activations via a causal-subspace
intervention rather than storing a weight change. SafeNexus (2607.28969) steers. UWM (2503.11742)
edits the vision encoder, whose endpoints are captioning rather than benchmark ASR, and an encoder
edit cannot change text-only inference; its role stays a second weight-edit comparator. These
identities come from abstracts and the existing nine-paper register, not from full reads, so they
remain provisional.
