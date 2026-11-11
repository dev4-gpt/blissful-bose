# EVA: deep study, source-to-code map and reproduction contract

Aryaman Singh Dev · 11 November 2026 · **primary reproduction target** (owner ruling, 11 November)

EVA replaced Steer2Edit as primary after the audit showed Steer2Edit is modality-blind by
construction. Selection reasoning:
[reselection analysis](WEIGHT_EDITING_RESEARCH_DIRECTION_2026-11-10.md#9-primary-paper-reselection-11-november-2026).
Steer2Edit remains the strictly-no-gradient text comparator:
[its study](STEER2EDIT_DEEP_STUDY_AND_CONTRACT.md).

This document authorizes nothing. No GPU run, weight download, image-bundle download or paid
judging has been performed.

## 0. State separation

| State | Status on 11 November |
| --- | --- |
| Source reading | Abstract, §I–§VI headings, §IV Method (key/value construction), §V experimental setup, Table III in full, layer and token-source ablations, metric definition. **Not read:** §II related work, the derivation detail of the least-squares solve, Tables II and IV–XI in full. |
| Extraction | Table III parsed from the paper's HTML with row awareness, verified by three independent cross-checks against the paper's own prose. Published hyperparameters taken from the repo's shipped configs. |
| Understanding | Six-step pipeline, the text/visual key split, the `v*` objective and the frozen-model constraint worked through. |
| Implementation inspection | Repo cloned and pinned; `hparams.py`, `editing/image/core.py` (optimization loop), `covariance.py`, the three shipped config sets and the released data JSON read. **Not yet read:** `pipeline.py`, `delman.py` solve, `models/llava.py`, `data.py`. |
| Empirical validation | **None.** No CPU validator written for EVA yet; no number reproduced. |

## 1. Verified identity

| Field | Verified value |
| --- | --- |
| Title | EVA: Editing for Versatile Alignment against Jailbreaks |
| Authors | Yi Wang, Hongye Qiu, Yue Xu, Sibei Yang, Zhan Qin, Minlie Huang, Wenjie Wang |
| arXiv | 2605.14750, **v1 only** (14 May 2026) — no later revisions |
| Venue | **IEEE TPAMI 2026** (peer-reviewed journal; `ieeexplore.ieee.org/abstract/document/11523146`) |
| Repository | `github.com/wanglne/EVA`, **MIT**, pinned commit `9bf060025b1e4e098e9bf655baed4ed711fe3f2a` (2026-10-11), 12 commits |
| Extras | Project page, HuggingFace model collection, image bundle and covariance archives on Google Drive |

Provenance is markedly better than Steer2Edit's on three counts: the paper has a single version so
there is no version/code skew; the repository **pins the checkpoint revision**
(`llava-hf/llava-1.5-7b-hf` at `95f2cf316249a98c11183f471ab76065c3e5f494`); and the published
hyperparameters ship as config files rather than having to be recovered from README examples.

## 2. What EVA does

EVA treats MLP layers as key–value memories and reframes a jailbreak as a harmful *key* retrieving
a malicious *value*. It rewrites the MLP down-projection so identified harmful keys map to a refusal
value instead. Six steps (Fig. 2):

1. Extract the harmful token `t` from the query with an auxiliary LLM (GPT-4o in the paper).
2. Generate `N` query variations containing `t`.
3. Locate critical **image** tokens via the cross-modal attention sub-matrix `P`.
4. Aggregate the representative keys `k*` across variations.
5. Optimize the target value `v*` toward a safe refusal response.
6. Update `W_down` by least squares so `k* -> v*`.

The textual key is the gated MLP activation at the harmful token, averaged over the `N` variations:

`k_t* = (1/N) Σ_j σ(W_gate · x_j,t) ⊙ (W_up · x_j,t)`

The visual key selects image tokens by mean attention from the harmful text token to each image
token, `s̄_m = (1/N) Σ_j P_j[t_j, m]`, then takes the top `N_v`. The ablation reports `N_v = 1`
suffices and that **selecting more visual tokens causes over-refusal** — the paper's only
acknowledgement of over-refusal anywhere.

Crucially: "by treating textual and visual keys as independent columns in `K_E`, EVA enables
simultaneous editing across both modalities within a single, unified optimization framework."
This is the capability Steer2Edit has no equivalent of.

## 3. Is it training? The constraint ruling

The owner ruled on 11 November that this satisfies the no-gradient-training requirement. The
evidence, from `src/eva/editing/image/core.py:219-300`:

```python
delta = torch.zeros((get_hidden_size(model),), requires_grad=True, device=device)
opt = torch.optim.Adam([delta], lr=hparams.v_lr)
set_requires_grad(False, model)          # every model parameter frozen
...
loss.backward(); opt.step()
max_norm = hparams.clamp_norm_factor * target_init.norm()
```

So **no model parameter ever receives a gradient.** Adam fits a single vector of size `d_model`
(4096 for LLaVA-1.5-7B), added to hidden states at the target token positions, with its norm clamped
to `0.75 × ||target_init||`. The loss is `nll + kl_factor·KL + weight_decay`, where the KL term
anchors behaviour to the unedited model. The resulting `v*` is then consumed by a closed-form
least-squares update to `W_down`; the optimized vector is not itself part of the model.

Honest characterization: **not fine-tuning, no weight trained, but not forward-pass-only either.**
It is gradient-based search for a target activation followed by an analytic weight update.
Steer2Edit's closed form remains strictly weaker in assumptions, which is why it stays as the
comparator.

## 4. Cost and runtime

Published settings for LLaVA-1.5-7B (`configs/hparams/{image,text}/llava-1.5-7b.json`):

| Parameter | image stage | text stage |
| --- | --- | --- |
| `layers` edited | 7, 8 | 7, 8 |
| `v_num_grad_steps` | 25 | 25 |
| `v_lr` | 0.0055 | 0.5 |
| `kl_factor` | 0.1 | 0.0625 |
| `clamp_norm_factor` | 0.75 | 0.75 |
| `v_loss_layer` | 31 | 31 |
| `v_weight_decay` | 0.5 | 0.5 |
| `fact_token` | `subject_last` | `subject_last` |
| `mom2` | wikipedia, 100k samples, float32, update weight 15000 | same |

Schedule: `records_per_update: 1`, `updates: 200`, `ordering: sequential` — 200 sequential edits per
stage, two stages (text then image), producing an intermediate `image_checkpoint` and a
`final_checkpoint`.

Upper bound on optimization work: 200 records × 25 steps × 2 stages = **10,000 forward+backward
passes**, each through a frozen 7B model. The loop breaks early at `loss < 1e-2`, so the realized
count is lower. Estimates, **not measured**: on an A100 roughly 30–90 minutes; on a single T4
plausibly 5–10× that, and memory is the bigger risk, since backward from `v_loss_layer=31` to layer
7 must retain activations on top of ~14.2 GiB of fp16 weights.

Two costs are removed entirely by the release:

- **Covariance `C`** is a 925 MB precomputed archive for LLaVA (layers 7, 8). No 100k-sample
  Wikipedia pass is needed. A recompute path exists with a pinned dataset revision
  (`wikimedia/wikipedia`, `20231101.en`, `b04c8d1ceb2f5cd4588862100d08de323dccfbaa`) because the
  paper's original `wikipedia/20200501.en` config is retired — a provenance deviation to record if
  we ever recompute.
- **GPT-4o and Stable Diffusion are not runtime dependencies.** The harmful token (`subject`), the
  refusal target (`target_new`: "I'm sorry, I can't assist with that."), the image path and even the
  located visual token (`attn_token_idx: {"attn_layer_8": 218}`) are pre-released for all 200 records
  per model profile. An ablation reports Qwen2.5-72B-Instruct reaching >90% harmful-token overlap
  with GPT-4o, so an open-source path exists if we ever regenerate.

`model.dtype` is **float16**, not bfloat16. Unlike Steer2Edit there is therefore no bf16/T4
conflict: T4 and Kaggle run the published precision natively.

## 5. The metric, and the gap that defines our contribution

**ASR is scored by the HarmBench classifier** (§V: "We employ the HarmBench classifier to detect
harmful content"). That is a trained harmfulness classifier, not a keyword list — substantially
stronger than Steer2Edit's 32-string endpoint, and a point in EVA's favour. It is also **not our
Azure GPT-4.1 judge**, so our completed baseline numbers are not directly comparable to Table III
without an explicit bridge; that is a deviation, not a detail.

**Over-refusal is never measured.** Searched the full text: the only occurrence is the ablation
aside that too many visual tokens "leads to over-refusal". There is no XSTest, no OR-Bench, no
false-refusal rate, no benign-twin refusal measurement. Utility is MM-Vet-v2, MMMU, MMStar and
MT-Bench — capability benchmarks, which do not detect a model that has become uniformly more
refusing on benign requests.

This matters because of what Table III shows: across the three EVA rows, **42 of 54 cells are
exactly 0.00**. Near-universal zero plus an unmeasured over-refusal axis is precisely the pattern a
safety-biased model produces. That is our opening.

## 6. Verified Table III — the reproduction anchor

Parsed from the paper's HTML with row awareness. Column mapping validated by three independent
cross-checks against the paper's prose: LLaVA Vanilla HarmBench/ADV-16 = 0.71, LLaVA Vanilla
MultiTrust/Crossmodal = 0.88, Qwen2.5-VL-7B Vanilla MM-SafetyBench/SD+TYPO = 0.51 — all matched.

MM-SafetyBench columns only (ASR, lower is better):

| Model | Method | SD | TYPO | SD+TYPO |
| --- | --- | ---: | ---: | ---: |
| LLaVA-1.5-7B | Vanilla | 0.13 | 0.12 | 0.37 |
| LLaVA-1.5-7B | JailGuard | 0.11 | 0.09 | 0.29 |
| LLaVA-1.5-7B | Adashield-A | 0.02 | 0.01 | **0.10** |
| LLaVA-1.5-7B | VLGuard | 0.04 | 0.02 | 0.14 |
| LLaVA-1.5-7B | **EVA(text)** | 0.09 | 0.08 | **0.33** |
| LLaVA-1.5-7B | **EVA** | 0.03 | 0.00 | **0.13** |
| Qwen2.5-VL-7B | Vanilla | 0.11 | 0.40 | 0.51 |
| Qwen2.5-VL-7B | EVA(text) | 0.04 | 0.19 | 0.22 |
| Qwen2.5-VL-7B | EVA | 0.01 | 0.00 | **0.00** |
| InternVL3.5-8B | Vanilla | 0.14 | 0.48 | 0.48 |
| InternVL3.5-8B | EVA(text) | 0.05 | 0.14 | 0.09 |
| InternVL3.5-8B | EVA | 0.03 | 0.06 | **0.03** |

### 6.1 Three consequences

**(a) `EVA(text)` already answers our planned research question.** It is the text-only-calibration
ablation: EVA without visual keys. On LLaVA-1.5-7B SD+TYPO it moves ASR only 0.37 → 0.33, while full
EVA with visual keys reaches 0.13. On Qwen, 0.51 → 0.22 → 0.00. So "text-derived calibration is
insufficient when harmful intent is carried by the image, and image-aware calibration closes the
gap" is **published, with an ablation**. The improvement proposed in the 10 November brief §4 is
therefore no longer novel and must be withdrawn as a contribution claim.

**(b) LLaVA-1.5-7B is EVA's weakest model, and on its hardest cell EVA loses to a baseline.** On
SD+TYPO, EVA leaves 0.13 while reaching 0.00 on Qwen and 0.03 on InternVL. More pointedly,
Adashield-A reaches **0.10** on that same cell — better than EVA — and VLGuard 0.14, essentially
tied. EVA's own table shows it is not the best method on LLaVA SD+TYPO. (Adashield is a prompting
defense and VLGuard is supervised fine-tuning, so their cost profiles differ, but on the metric as
reported EVA loses that cell.) This is a published, model-specific failure on the exact model for
which we hold a completed 6,720-case baseline.

**(c) The near-zero cells are unaudited on two axes.** 42 of 54 EVA cells are exactly 0.00, scored
by the HarmBench classifier, with no over-refusal measurement and no uncertainty anywhere.

## 7. Candidate research question

> EVA reduces MM-SafetyBench ASR to near zero but never measures over-refusal, and on LLaVA-1.5-7B
> SD+TYPO it leaves 0.13 while a prompting baseline reaches 0.10. Does the near-zero ASR survive a
> semantic harmful-assistance judge, what does it cost in benign over-refusal and image-grounded
> capability, and why does the method underperform specifically on LLaVA?

Stronger than the withdrawn text-versus-image claim for three reasons. It attacks a published number
rather than an absence. The instruments already exist here: the completed LLaVA-1.5-7B four-condition
baseline, Azure GPT-4.1 semantic harmful-assistance judging, XSTest safe prompts and benign twins
from the v6 work, and OCR read-back for image capability. And a negative result is still publishable:
if 0.00 survives a stricter judge at no over-refusal cost, that is a meaningful independent
confirmation of a TPAMI method.

Unresolved before committing: whether EVA's 200 editing records overlap MM-SafetyBench's 13
scenarios (both derive from harmful-behaviour sets, so an overlap check is mandatory), and whether
the HarmBench classifier and our Azure judge can be bridged or must be reported separately.

## 8. Open items before depth parity with the Steer2Edit study

1. Read `pipeline.py`, `delman.py` and `models/llava.py`; write the full source-to-code map and
   record paper/code discrepancies as D-tags.
2. Extract the least-squares update equation and the MEMIT/DELMAN inheritance precisely.
3. Reference dependency audit of EVA's bibliography, including the uncited-but-used check that found
   13 such dependencies in Steer2Edit.
4. Determine EVA's `n` per cell and whether any uncertainty is reported anywhere.
5. Overlap check between the 200 editing records and MM-SafetyBench's 13 scenarios.
6. CPU validator for the edit math, parallel to `tools/steer2edit_edit_math.py`.

---

## 9. The editing mathematics

Section IV-C, verified against the pinned code.

**Editing matrices (Eq. 16–17).** Text and visual keys are concatenated as columns:
`K_E = [k_t1*, k_m1*, k_t2*, k_m2*, ...]`, `V_E = [v_t1*, v_m1*, v_t2*, v_m2*, ...]`.
The paper states this "naturally unifies the editing process across LLMs and VLMs": for an LLM
`K_E` holds only text keys, for a VLM both modalities "as independent columns".

**Constrained objective (Eq. 18–19).** `min ||Ŵ K − V||²` subject to `Ŵ K_E = V_E` — minimize
error on pre-existing keys while mapping harmful keys exactly to safe values.

**Closed form (Eq. 20), the MEMIT solution.**
`Ŵ_down^{l*} = W_down^{l*} + R_E K_Eᵀ (C^{l*} + K_E K_Eᵀ)⁻¹`
with residual `R_E = V_E − W_down^{l*} K_E` (Eq. 21) and `C^{l*} = K Kᵀ`, the covariance of
pre-existing keys pre-cached from Wikipedia. `C` is the preservation term: it penalizes
perturbations along directions that pre-existing keys activate often.

**Multi-layer spreading (Eq. 22).** `v*` and the base residual are computed only at the highest
critical layer `l*`; the residual is then distributed to lower layers with a decreasing factor:
`R_E^{l_i} = (V_E − W_down^{l*} K_E) / (l* − l_i + 1)`.

**Inheritance.** The closed form and the critical-layer identification are explicitly taken from
**MEMIT** [21]; critical-layer selection for LLMs also follows **EasyEdit** [22]; the
constrained-least-squares formulation cites [54]; multi-layer spreading cites [38]. EVA's own
contribution is the *multimodal key construction* (steps 1–4) and the claim that LLM critical layers
transfer to VLMs — not the solver.

### 9.1 Source-to-code map

`src/eva/editing/delman.py:205-262` is the shared solver for both stages.

```python
v_star_layer = hparams.layers[-1]                       # l*
layer_ks = compute_k_star(...).T
targets  = repeat_targets_for_keys(v_stars - cur_vs, layer_ks.size(1))
layer_ks = layer_ks.double().mean(dim=1, keepdim=True)  # <-- averaged to ONE column
targets  = targets.double().mean(dim=1, keepdim=True)
adj_k = torch.linalg.solve(hparams.mom2_update_weight * cov + layer_ks @ layer_ks.T, layer_ks)
resid = targets / (len(hparams.layers) - index)
update = match_update_shape(resid @ adj_k.T, weights[weight_name].shape)
```

`resid @ adj_kᵀ = R_E K_Eᵀ (λC + K_E K_Eᵀ)⁻¹`, matching Eq. 20 up to the `λ` discussed below.

| Paper element | Code | Verdict |
| --- | --- | --- |
| Eq. 20 closed form | `linalg.solve(λ·cov + K Kᵀ, K)` then `resid @ adj_k.T` | Matches in structure |
| Eq. 21 residual | `targets = v_stars - cur_vs` | Matches |
| `l*` = highest critical layer | `v_star_layer = hparams.layers[-1]` | Matches |
| Eq. 22 spreading | `targets / (len(layers) - index)` | Matches **only for contiguous layer lists** (E4) |
| `v*` optimization | `Adam([delta])`, model frozen | Matches §IV-B |

**E1 — `C` is scaled by 15,000, which Eq. 20 does not show.** The code solves
`(mom2_update_weight · C + K_E K_Eᵀ)` with `mom2_update_weight = 15000` from the shipped hparams.
Equation 20 writes plain `C`. This is a MEMIT-inherited hyperparameter, and it is not cosmetic: it
sets the balance between preserving pre-existing knowledge and fitting the new mapping. Any
reproduction must use 15000; any improvement that touches the preservation/edit trade-off acts
through this constant.

**E2 — keys are averaged into a single column, contradicting Eq. 16–17.** The paper presents `K_E`
as a matrix whose columns are the individual text and visual keys "as independent columns". The code
applies `.mean(dim=1, keepdim=True)` to both `layer_ks` and `targets`, so each solve uses **one**
averaged key and one averaged target. With `records_per_update: 1` the solve is rank-1 in `K_E`, not
a multi-column system.

**E3 — the two modalities are two sequential stages, not one joint solve, and image runs first.**
`pipeline.py:84-123` builds six stages: `image_edit` → `save_intermediate_checkpoint` (full) →
`reload_intermediate_checkpoint` → `text_edit` → `save_final_checkpoint` (full) → `write_manifest`.
Combined with E2 this means the "single, unified optimization framework" of §IV-C is implemented as
**two separate 200-record sequential editing passes over a model that is fully saved and reloaded in
between**, with the image pass applied to the original weights and the text pass applied to the
already-image-edited weights. Sequential editing is not joint editing: the second pass sees a model
the first pass has already changed, and the paper's formulation does not describe this ordering.
This is the most consequential discrepancy found in EVA and it bears directly on any claim about how
the modalities interact.

**E4 — Eq. 22's denominator diverges from the code for non-contiguous layers.** Code uses
`len(layers) − index`; the paper uses `l* − l_i + 1`. For the published configs these agree
(`[7,8]` → 2, 1; `[8,9]` → 2, 1). For `[4,8]` the paper gives 5 and the code 2; for `[3,6,8]` the
paper gives 6, 3, 1 and the code 3, 2, 1. Irrelevant to a faithful reproduction, **decisive for any
improvement that changes the layer set** — which a layer-selection improvement would.

**E5 — `compute_deltas` restores the original weights before returning.** A `finally:` block
rewrites `weights_copy` back into the model, so the function computes deltas without leaving the
model modified; application happens elsewhere. Restoration is therefore built in rather than
something we must add, which is a point in EVA's favour over Steer2Edit's in-place `add_`.

**E6 — two full checkpoints per run, with validated reload.** `save_full_checkpoint` writes to a
`.partial` sibling, runs `checkpoint_validation_errors` to confirm the checkpoint is reloadable,
writes a completion marker, then `os.replace` for an atomic publish. Per-stage `resume_key`s plus
`--resume` / `--force-restart` make a run restartable. Good engineering, and it means save/reload
fidelity is checked by the pipeline itself — but it writes **two ~14.2 GiB checkpoints**.

### 9.2 Storage and platform consequences

| Artifact | Size |
| --- | --- |
| `image_checkpoint` (full) | ~14.2 GiB |
| `final_checkpoint` (full) | ~14.2 GiB |
| Covariance archive (layers 7, 8) | 0.9 GiB |
| HF model cache | ~14.2 GiB |
| **Total if everything is on Drive** | **~43.5 GiB** |

Recommended Colab layout: HF cache and the active checkpoint on the **VM disk** (Colab has ample
ephemeral disk), covariance and the **final** checkpoint plus manifests on **Drive**. Putting the
intermediate checkpoint on Drive as well is what makes a disconnect survivable, at the cost of
~28 GiB of quota, so it is a quota decision rather than a technical one.

**4-bit loading is not an acceptable fallback here.** The solve operates on `W_down` in floating
point and writes a dense update into it; editing a 4-bit quantized weight would require
dequantize–edit–requantize and would not reproduce the published operation. So unlike our earlier
inference-only work, there is no low-memory escape hatch: a free 16 GiB T4 has ~1.8 GiB of headroom
after fp16 weights and must additionally retain activations for a backward pass from `v_loss_layer`
31 down to layer 7. Expect OOM. An L4 (24 GiB), A100, or a Nebius Ampere-or-newer GPU is the
realistic requirement.

---

## 10. Audit completions: data, denominators and the evaluation gap

### 10.1 Probe/evaluation overlap — clean

The 200 editing records hold **177 unique subjects**, a single refusal target
("I'm sorry, I can't assist with that.") and 193 distinct `prompt_adv` templates. Subjects are
HarmBench named entities: `dimethylmercury`, `ricin`, `botulinum toxin`, `Ebola`, `MDMA`,
`fentanyl laboratory`, `Lewisite`, `dangerous DNA sequences`.

Evaluation is MM-SafetyBench, a different source with different items, so there is **no item-level
overlap** between calibration and evaluation. This is good design and better than the paper's own
description of Steer2Edit's setup. It does mean Table III measures *generalization* from 177
HarmBench concepts to MM-SafetyBench's 13 scenarios, which motivates the diagnostic in §10.4.

### 10.2 No denominators and no uncertainty, anywhere

Searched the full text: EVA never states its MM-SafetyBench evaluation set size, contains **zero**
occurrences of `n=`, and contains no standard deviation, confidence interval, `\pm`, error bar,
seed count or "averaged over". Every cell in Table III is a bare percentage over an unstated
denominator. Recorded as unresolved; not filled from convention. Our own reproduction will report
exact binomial intervals over stated denominators and label them as an addition.

### 10.3 The released repository contains no evaluation code

**E7.** The CLI exposes only `inspect`, `run` and `covariance`. No file under `src/eva/` references
MM-SafetyBench, ASR, the HarmBench classifier or evaluation, and the README has no evaluation
section. The release is **editing-only**: it produces `image_checkpoint` and `final_checkpoint`, and
it does not reproduce Table III.

This splits the reproduction cleanly in two:

- **The edit is reproducible from released code**, with the published config, the pre-computed
  keys/targets/visual-token indices and the precomputed covariance. This is the part where "run
  their exact code" is literally true.
- **The evaluation must be built by us.** We supply the MM-SafetyBench four-condition harness, which
  we already have. EVA's native endpoint additionally requires the **HarmBench classifier**
  (`cais/HarmBench-Llama-2-13b-cls`, a 13B model, roughly 26 GiB) which is not in the repo and is a
  separate download and inference cost. Reporting our Azure GPT-4.1 judge instead is permissible but
  is then a **different endpoint**, not EVA's.

### 10.4 The baseline cross-check fails by about 2x

This is the most important practical finding of the audit. EVA's Table III `Vanilla` row for
LLaVA-1.5-7B SD+TYPO is **0.37**. Our own completed baseline for the same model and the same
condition, judged by Azure GPT-4.1, gives:

| Scenario subset | our ASR |
| --- | ---: |
| All 13 scenarios | **0.760** (1203/1583) |
| Drop advice scenarios 10-13 | 0.633 (651/1029) |
| Core harm 01-07 only | 0.552 (407/737) |
| EVA Table III `Vanilla` | **0.370** |

Restricting to core harm narrows the gap from 2.05x to 1.49x but does not close it. Candidate
causes, in order of likelihood: the judge differs (HarmBench classifier requires the completion to
actually constitute the harmful behaviour, while a semantic harmful-assistance judge is more
liberal); EVA may evaluate a scenario subset it does not state (§10.2); and prompt or decoding
settings may differ.

**RESOLVED, 11 November.** MM-SafetyBench's own Table 3 reports **72.14** for LLaVA-1.5-7B SD+Typo,
and our macro reproduces it at **73.88** (+1.74 pp); our image-condition macros land within 1.2-3.4 pp
of published throughout. So **EVA is the outlier, not us**, and scenario subsetting cannot explain it
(published macro over 01-07 = 56.25, over 01-09 = 60.18). The cause is the measurement instrument:
EVA scores with the HarmBench classifier, which requires the response to constitute the harmful
behaviour, while MM-SafetyBench's rubric flags a far broader class. **The two scales are not
commensurable and must never be differenced.** Reproducing Table III therefore requires
`cais/HarmBench-Llama-2-13b-cls` (~26 GiB, not shipped). Full analysis:
[published comparison and judge resolution](MM_SAFETYBENCH_LLAVA_REPRODUCTION.md#published-comparison-execution-and-judge-resolution--11-november-2026).

### 10.5 A correction to our own evidence base

The same analysis exposes a defect in our completed baseline. Our judge labels **100% of answers
unsafe** in three scenarios at SD_TYPO:

| Scenario | unsafe / judged |
| --- | --- |
| 10-Legal_Opinion | 130/130 |
| 11-Financial_Advice | 167/167 |
| 12-Health_Consultation | 108/108 |

Saturation at exactly 1.000 is a rubric artifact signature, not a model property: these scenarios
ask for legal, financial and medical advice, and the judge is counting any substantive answer as
unsafe. 13-Gov_Decision (147/149) and 08-Political_Lobbying (147/153) are nearly saturated too.

**Corrected 11 November:** this is *not* a defect. The published Table 3 reports 96.92, 100.00 and
100.00 for those same scenarios at SD+Typo, so our saturation **reproduces the benchmark's own rubric
property**. The interpretive caution stands unchanged -- a pooled 13-scenario ASR is dominated by
professional-advice refusal rather than harm in the ordinary sense, so report per-scenario rates and
state which scenario family a claim rests on -- but the measurement is sound.

### 10.6 The resulting diagnostic hypothesis

MM-SafetyBench scenarios 08-13 are the ones where refusal is frequently *inappropriate* —
political lobbying, legal opinion, financial advice, health consultation, government decisions. EVA
drives ASR to near zero and never measures over-refusal (§5). So:

> If EVA's near-zero ASR holds uniformly across scenarios 08-13 as well as 01-07, that is evidence
> of blanket refusal rather than targeted safety; if it concentrates in the core-harm scenarios
> closest to its 177 HarmBench subjects and leaves 08-13 largely untouched, that is evidence of
> genuine targeting but also of limited generalization.

Either outcome is informative, and the per-scenario, per-condition baseline with denominators and
bounds that we already hold is the instrument for deciding it. This supersedes the withdrawn
text-versus-image contribution as the project's lead question.

## 11. Audit state after depth-parity pass

**Done:** identity and venue; pinned commit; published hyperparameters; Eq. 16-22 extracted and
mapped to code; seven discrepancies E1-E7; storage and platform analysis; probe/evaluation overlap
check; denominator and uncertainty check; verified Table III; baseline cross-check; a correction to
our own baseline.

**Still open:** `models/llava.py` and `data.py` not read, so the visual-token indexing path is
mapped from configs and `image/core.py` only; EVA's reference dependency audit not started; no CPU
validator for the least-squares update yet (parallel to `tools/steer2edit_edit_math.py`); the judge-commensurability question in
§10.4 is now **resolved** (see that section).

**Nothing has been executed.** No model, covariance archive or image bundle downloaded; no edit
computed; no number reproduced.

The pre-specified run plan now lives in [the EVA reproduction contract](EVA_REPRODUCTION_CONTRACT.md).
