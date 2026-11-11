# Steer2Edit: deep paper study and source-to-code map

Aryaman Singh Dev · 11 November 2026 · primary-paper study for the weight-editing direction.
The pre-specified run plan is in [the reproduction contract](STEER2EDIT_REPRODUCTION_CONTRACT.md).

Companion to the [weight-editing direction](WEIGHT_EDITING_RESEARCH_DIRECTION_2026-11-10.md) and
the [reference dependency audit](REFERENCE_DEPENDENCY_AUDIT.md). It records what was read and
inspected, separates author statements from released-code behaviour and from our deductions, and
specifies one reproducible published result. It authorizes nothing: no GPU run, weight download,
paid judging or release has been performed.

## 0. State separation

| State | Status on 11 November |
| --- | --- |
| Source reading | Paper v4 read: Abstract, §1–§6, Appendices B–F, and the tables of H–Q; v1 read for the version diff. Figures 3, 6, 9 inspected as captions only, not pixel-level. |
| Extraction | All five central equations, both published best safety configurations, and cells from Tables 5, 11, 12, 13 transcribed. |
| Understanding | Three-step derivation, Elastic-Net allocation and budget asymmetry worked through analytically; small worked example below. |
| Implementation inspection | Official repo cloned and pinned; `edit.py`, `extract_directions.py`, `generate_response.py`, `utils.py`, `edit.sh` and the edit-application block of `evaluate.py` read line by line. |
| Empirical validation | CPU only: `tools/steer2edit_edit_math.py`, 11/11 checks on a synthetic fixture. **No model was loaded and no published number was reproduced.** |

## 1. Verified identity and the version problem

| Field | Verified value |
| --- | --- |
| Title | Steer2Edit: From Activation Steering to Component-Level Editing |
| Authors | Chung-En Sun, Ge Yan, Zimo Wang, Tsui-Wei Weng |
| arXiv | 2602.09870; v1 10 Feb 2026, v2 3 Mar 2026, v3 4 Nov 2026, **v4 8 Nov 2026 (current)** |
| Venue | **Accepted to NeurIPS 2026** (arXiv comment field; repo README dates acceptance 2026/09/24) |
| DOI | 10.48550/arXiv.2602.09870 |
| Repository | `Trustworthy-ML-Lab/Steer2Edit`, pinned commit `86382c2f44fdfda2bafe80faf09634e6d729562c`, 2026-09-30, 8 commits total |

**Version correction.** Our brief pins `html/2602.09870v1`; the current version is v4. This is not
cosmetic: v1 carries 26 bibliography entries and Appendices A–G, v4 carries 37 entries and
Appendices A–Q. The equations are **unchanged** between v1 and v4 — the brief's transcription of the
editing rule is correct — but v4 adds the numeric tables a reproduction needs and a vision-language
experiment that changes our novelty position (§7). Work from v4.

**Repository lag.** The pinned commit predates v3/v4 by five weeks and covers only the three main
settings on the original model panel. The v4 appendices added during review — OR-Bench, 70B,
vision-language, diffusion LLM, fine-grained steering baselines, judge swap — have **no released
implementation**, so reproducing Appendix N would be our implementation, not the authors'.

## 2. Research question, claim and mechanism

Activation steering adds a direction to the residual stream at inference. The authors argue this
is doubly wrong: it is *global* (all tokens and components treated alike, though behaviour is
carried by a small heterogeneous subset) and it sits *outside the standard forward pass* (breaking
the fixed computation graphs optimized inference assumes). Their claim: the steering vector is
better used as a **diagnostic signal** saying which components to rewrite, after which the model
runs an ordinary forward pass with no hooks.

Claimed headline (abstract, v4): at matched downstream performance, +17.2% safety, +9.8%
truthfulness, −12.2% reasoning length against the strongest steering baseline.

Assumptions that matter to us, in the authors' framing: a steering vector `v_i` exists in the
space the component writes into; one direction suffices, so a **rank-1** edit is the minimal
sufficient perturbation; and a well-trained component already encodes which inputs are relevant to
`v_i`, so the edit should imitate the component's existing input sensitivity rather than invent a
new one. The method is explicitly agnostic to how `v_i` is obtained.

## 3. Architecture, access and editable surface

Pre-normalization transformer, `L` layers, residual width `d`. Each layer's attention and MLP
blocks write additive updates into the residual stream. Editable components are exactly the linear
maps whose output lands in that stream:

- **Attention:** the output projection `o_proj`. One component per *head*: `W_o ∈ R^{d×d_head}`,
  the head's column block.
- **MLP:** the down projection `down_proj`. One component per *neuron*: a single column
  `w_down,j ∈ R^{d}`, treated as independent.

Required access: full weights, plus forward hooks on `o_proj` and `down_proj` inputs and outputs
during calibration. White-box. No gradients, no optimizer, no backward pass anywhere.

For LLaMA-2-7B-Chat (32 layers, 32 heads, `d_ff` 11008) the candidate set is 32×32 = 1,024
attention heads and 32×11,008 = 352,256 MLP neurons — 353,280 components, each receiving its own
scalar magnitude.

## 4. The five central equations

Original notation on the left, teaching notation and constraints on the right.

**(E1) Steering vector, Eq. (1) / Appendix D.**
`v_ℓ^b = δ̄_{ℓ,pos}^b − δ̄_{ℓ,neg}^b ∈ R^d`
Mean block output over positive-set responses minus the same over negative-set responses, where
each response is first averaged over its own token span. One vector per (layer, block).
Dimension: `d`, the residual width. Sign convention: *points from negative behaviour toward
positive behaviour*. Constraint: `v_i ≠ 0` (Theorem 3.1).

**(E2) Output direction, Theorem 3.1.**
`û_i = v_i / ‖v_i‖₂`
Derived, not chosen: requiring the edit's output shift to have zero projection on every
`z ⊥ v_i` forces `u_i ∈ span{v_i}`. Scale and sign are deferred to `λ_i`.

**(E3) Input direction, Theorem 3.2.**
`k̂_i = W_iᵀ v_i / ‖W_iᵀ v_i‖₂`
Derived by maximizing `|Pearson(Δs_i(h_i), s_i(h_i))|`, where `s_i(h_i) = v_iᵀ W_i h_i` is the
component's semantic alignment score. Dimension: `k̂_i ∈ R^{d_in}`, so `d_head` for a head and
**a scalar ±1 for an MLP neuron**. Requires `W_iᵀ v_i ≠ 0` and `Var(s_i) > 0`.

**(E4) Component importance, Section 3.4.**
`g_i = cos(v_i, W_i μ_i) ∈ [−1, 1]`, with the convention `g_i := 0` if `W_i μ_i = 0`.
`μ_i = E[h_i]` is the mean input activation. The double normalization (by `‖v_i‖` and by
`‖W_i μ_i‖`) is what makes scores comparable across layers of very different output scale. Sign
says reinforce or oppose; magnitude says how strongly.

**(E5) Magnitude, Theorem 3.3.**
`λ_i* = sign(g_i) · max(|g_i| − ρα, 0) / (ρ(1−α))`
The unique maximizer of `gᵀλ − ρ(α‖λ‖₁ + ((1−α)/2)‖λ‖₂²)` with `ρ > 0`, `α ∈ [0,1)`. This is
soft-thresholding: `ρα` is a hard gate below which a component is left alone, and `1/(ρ(1−α))` is
the gain applied to whatever survives. Separate budgets `ρ_attn`, `ρ_mlp`; shared `α`. `α < 1` is
required or the denominator vanishes — the released `edit.py` asserts it.

**Unified rule (Section 3.5):** `ΔW_i = λ_i* û_i k̂_iᵀ`, i.e.
`ΔW_i = sign(g_i)·max(|g_i|−ρα,0)/(ρ(1−α)) · v̂_i k̂_iᵀ`.

Division of labour, which the authors stress and which matters for our improvement: `k̂_i`
captures how alignment *varies across inputs*; `λ_i` depends only on the *average* alignment.
Confusing the two is the standard misreading.

### 4.1 Worked example

One head, `d = 4`, `d_head = 2`, `ρ_attn = 0.18`, `α = 0.8` (published best for llama2-7b).

Let `v = (0, 3, 0, 4)`, so `‖v‖₂ = 5` and `v̂ = (0, 0.6, 0, 0.8)`.
Let `W = [[1,0],[0,1],[0,0],[1,0]]` (4×2) and mean input `μ = (2, 1)`.

- `Wμ = (2, 1, 0, 2)`, `‖Wμ‖₂ = 3`.
- `vᵀWμ = 3·1 + 4·2 = 11`, so `g = 11/(5·3) = 0.7333`.
- Gate: `ρα = 0.144`. Since `|g| > 0.144`, the head is edited.
- `λ = +(0.7333 − 0.144)/(0.18·0.2) = 0.5893/0.036 = 16.37`.
- `Wᵀv = (4, 3)`, `‖·‖₂ = 5`, so `k̂ = (0.8, 0.6)`.
- `ΔW = 16.37 · v̂ k̂ᵀ`: row 2 = `16.37·0.6·(0.8,0.6) = (7.86, 5.89)`,
  row 4 = `16.37·0.8·(0.8,0.6) = (10.48, 7.86)`, rows 1 and 3 zero.

Note the magnitude: `λ = 16.4` against original weights of order 1. The gain
`1/(ρ(1−α)) = 27.8` at this configuration is large, so the edit is not a gentle nudge but a
substantial rewrite of the surviving components. This is why the coarse search discards degenerate
configurations with a 20-prompt sanity check before measuring anything.

### 4.2 Input-to-output path

```
probing prompts (100 malicious + 100 benign)
        │
        ▼  vLLM generation, model's own generation_config (sampled, unseeded)
model-generated responses
        │
        ▼  forward pass with hooks on o_proj / down_proj
   pre-activations  h ──► μ_i   (mean INPUT,  "pre")
   post-activations δ ──► v_i   (mean-diff OUTPUT, "post")
        │
        ▼
   g_i = cos(v_i, W_i μ_i)    k̂_i = W_iᵀv_i/‖·‖    û_i = v_i/‖v_i‖
        │
        ▼  Elastic-Net soft-threshold over the whole component set
   λ_i for 353,280 candidates → sparse surviving subset
        │
        ▼  ΔW_i = λ_i û_i k̂_iᵀ written into o_proj column blocks / down_proj columns
   edited checkpoint saved to disk ──► vLLM loads it ──► ORDINARY forward pass
        │
        ▼
   safety: refusal-keyword match on AdvBench+GCG and AdvBench+ADV-LLM
   utility: accuracy on CommonsenseQA, CodeMMLU, GSM8K
```

## 5. Source-to-code map and resolved discrepancies

Pinned commit `86382c2`. Line numbers are that commit's.

| Paper element | Released code | Verdict |
| --- | --- | --- |
| `û_i = v̂_i` (Thm 3.1) | `edit.py:91-92`, `l2_normalize` on `directions["post"]["direction"]` | Matches |
| `k̂_i` (Thm 3.2) | `edit.py:116-120`, `W_block.T @ vhat`, normalized | Matches |
| `g_i` attention (E4) | `edit.py:109`, `cosine_similarity(vhat, W_block @ x_mean_heads[j])` | Matches, per-head slice of μ |
| `λ_i` (Thm 3.3) | `edit.py:22-29`, exactly the closed form | Matches |
| `ΔW_i = λ û k̂ᵀ` | `evaluate.py:179-180`, `oW.data[:, h0:h1].add_(lam * outer(vhat, khat))` | Matches; orientation confirmed |
| MLP component | `evaluate.py:190`, `dW.data[:, neuron].add_(lam * vhat)` | Matches; `k` is a scalar ±1 folded into λ |

**D1 — `μ_i` is not the input-distribution mean.** Paper §3.4 defines `μ_i = E[h_i]`.
`edit.py:97-100` uses `0.5·(pos_mean + neg_mean)`, the unweighted midpoint of the two
*probing-set* means. These agree only when the sets are equally sized and weighted. The released
safety pipeline uses 100 + 100, so they coincide there by construction, not by definition. **Any
VLM adaptation with unequal pair counts silently changes the estimator.** Carried into
`tools/steer2edit_edit_math.py:mu_from_directions`.

**D2 — probing data is MaliciousInstruct, not AdvBench.** Appendix D states "we construct steering
vectors using the ADVBench dataset". The code reads `data/MaliciousInstruct.txt` (100 lines) for
harmful probes and `data/benign_instructions.jsonl` (100 Alpaca instructions) for benign. AdvBench
(`harmful_behaviors.csv`, 520 rows) is used only for **evaluation**. The code's behaviour is
*better* than the paper's description — it gives clean probe/evaluation separation — but the paper
text as written is wrong, and a reader following the paper would introduce calibration/evaluation
overlap. Treat the code as authoritative.

**D3 — no refusal selection or filtering exists.** Appendix D states the positive set "consists of
refusal responses to harmful prompts". `generate_response.py:186-200` takes
`batch_result.outputs[0].text.strip()` for every prompt and writes it, with **no judge, no keyword
filter and no selection step**. The positive set is thus "whatever LLaMA-2-7B-Chat said given a
malicious instruction under a safety system prompt" — overwhelmingly refusals for this model, so the
description holds approximately *by construction*, not by enforcement. This is the most important
inherited assumption for us: it is exactly what fails on a weaker-aligned model or a VLM under an
image-carried attack, where many responses to harmful probes are compliances that would pollute the
positive set and partly invert the direction.

**D4 — the negative set shares the harmful prompt.** `extract_directions.py:88-90` takes
`questions` from the *positive* (malicious) file, and line 199 calls
`collect_embeddings(questions, neg_traces)`, pairing each **malicious question** with an **Alpaca
response**. The contrast is not "harmful prompt + refusal vs benign prompt + help" but *prompt held
fixed, response style swapped* — defensible and arguably stronger, yet contradicting Appendix D. It
is the recipe to copy if we want the method rather than the prose.

**D5 — the token span is next-token aligned, and boundary-fragile.** `span_mean_per_layer` averages
positions `[start-1, end-1)` where `start = len(tok(prompt))`, `end = len(tok(prompt+response))`.
Under next-token semantics the activation at `t` produces token `t+1`, so this span is exactly the
positions whose outputs are the response tokens: deliberate, not an off-by-one bug. But
`full_str = base_str + t` is re-tokenized from scratch, so merges across the prompt/response
boundary can shift `start`. The code warns only when `end <= start`.

**D6 — probe generation is not reproducible.** `make_params` copies `temperature`, `top_k`, `top_p`
from the model's own `generation_config` — sampling, not greedy, for LLaMA-2-7b-chat — and
`SamplingParams` is built **without a seed**; `np.random.seed(20)`/`torch.manual_seed(20)` do not
control vLLM's sampler. Re-running step 1 yields different probes and different directions, so our
run identity must store the generated responses themselves, not merely the seed.

**D7 — precision.** Everything runs in `torch.bfloat16`: model load, span means, cosine scores and
the update, which `evaluate.py:175-176` casts to the weight dtype before `add_`. bfloat16 carries 8
mantissa bits, so a cosine compared against a gate of 0.144 is computed at roughly three decimal
digits. Our CPU suite found identical component selection between fp32 and bf16 on a synthetic
fixture (Jaccard 1.000) — reassuring, but not evidence at 353,280 real components near the gate.

**D8 — persistence writes a full checkpoint per configuration.** `evaluate.py:281-309` loads the
base model, applies edits in place, then `save_pretrained`s into a fresh `TemporaryDirectory` for
vLLM to load, cleaned at exit. So the original checkpoint is never mutated (good), save/reload
fidelity is exercised by the pipeline itself (good), and each evaluated configuration writes
roughly 13 GB to local disk (a real budget item). The compact `.pt` pack holds only (λ, k̂, v̂).

**D9 — `edit.py` meta omits fields its own docstring promises** (`hidden_size`, `num_heads`,
`head_dim`); `evaluate.py:161-163` falls back to the model config, so it works. Latent fragility if
the pack is read by anything trusting the docstring.

**D10 — checkpoints are unpinned.** `MODEL_MAP` holds bare repo IDs
(`meta-llama/Llama-2-7b-chat-hf`, `mistralai/Mistral-7B-Instruct-v0.2`) with no `revision`. We pin
a commit SHA ourselves and record it as our addition.

### 5.1 Degenerate-input handling, as released

Inspected before proposing any repair, per the owner's instruction.

- `l2_normalize` adds `eps = 1e-12` to the norm, so a zero `v` returns a zero vector **silently**
  rather than raising, though Theorem 3.1 assumes `v ≠ 0`.
- `g` uses `F.cosine_similarity` (default `eps = 1e-8`), which returns 0 when `W_i μ_i = 0`,
  matching Theorem 3.3's stated convention `g_i := 0`.
- Attention: `if k_norm == 0.0: continue` — the component is skipped.
- MLP: mask `(lambdas != 0) & (k_scalars != 0)`.
- `ρ ≤ 0` returns all-zero λ; `edit.sh` uses `-1.0` as the "do not edit this block" sentinel and
  explicitly skips the `(-1, -1)` combination.

Our verdict: the released handling is **safe but silent**. Every degenerate case yields "no edit"
rather than an error, so a calibration failure that zeroes a direction is indistinguishable from a
legitimately unedited component. For the VLM adaptation this is a genuine hazard, and it is the one
place where we should add instrumentation rather than change behaviour.

### 5.2 An analytic consequence the paper does not state

Figure 6's caption reports that safety edits are "concentrated in a small subset of attention
heads, predominantly in later layers. MLP neurons receive near-zero coefficients." The chosen
budgets largely force this:

| Configuration | gate `ρ_attn·α` | gate `ρ_mlp·α` | gain attn | gain mlp |
| --- | ---: | ---: | ---: | ---: |
| llama2-7b safety (README best) | 0.144 | 0.440 | 27.78 | 9.09 |
| mistral-7b safety (README best) | 0.315 | 0.413 | 9.52 | 7.27 |
| Qwen2.5-VL-7B (Table 13 best) | 0.150 | 0.250 | 6.67 | 4.00 |

At the llama2 best configuration an MLP neuron needs `|cos| > 0.440` to receive any edit while an
attention head needs only `> 0.144` — a 3.05× stricter gate — and surviving attention heads are
additionally amplified 3.06× more. **The attention-dominance finding is therefore partly an
artifact of the budget asymmetry, not purely evidence about where safety is implemented.** Our CPU
fixture reproduces the pattern qualitatively (3 of 8 heads edited, 0 of 96 neurons at the same
configuration), though a synthetic fixture is weak evidence. A per-component-type normalization of
`g` before thresholding is a cheap, concrete candidate improvement that this observation motivates
directly.

A further structural point, verified in the suite: for an MLP neuron `d_in = 1`, so
`cos(v, W_j·μ_j) = sign(μ_j)·cos(v, W_j)`. The **magnitude** of the mean activation cannot affect
`|g|` for MLP neurons at all — it only sets the sign. Attention heads, with `d_head`-wide inputs,
do get magnitude-weighted scores. The two component families are thus scored by structurally
different quantities under one shared `α`.

## 6. Data, metrics and what the numbers mean

**Calibration (probing).** 100 MaliciousInstruct prompts + 100 Alpaca benign instructions, one
sampled response each, at most 1024 new tokens. No filtering (D3). No overlap with evaluation (D2).

**Safety evaluation.** AdvBench harmful behaviours, each wrapped by one of two attacks:

- **GCG** (Zou et al. 2023b): released as `data/gcg_results/{model}/adv_suffix_{0-9…90-99}.csv`,
  10 files × 10 rows = **100 behaviours**, columns `prompt, adv, response`.
- **ADV-LLM** (Sun et al. 2025a): released as
  `data/advllm/advbench/{greedy,group_beam_search_50}/*.pkl`.

**Both attacks are pre-computed and released for `llama2-7b` and `mistral-7b`. No attacker needs
to be trained or run.** This is the decisive feasibility finding for the native reproduction.

**The native safety endpoint is keyword refusal matching.** `utils.py:REFUSAL_SIGNAL` is a
32-string list with very permissive entries — `"cannot"`, `"I must"`, `"I understand"`, `"Hello!"`,
`"unethical"`, `"As an"` — so "I understand your question, here is how to…" scores as a refusal. It
measures *refusal-shaped text*, not withheld assistance. Preserve it exactly; our semantic
harmful-assistance ASR is a **separate measurement**, never a substitute.

**Utility**, from `DATASET_MAP`: `skrishna/gsm8k_only_answer` (test), `tau/commonsense_qa`
(validation), `Fsoft-AIC/CodeMMLU` config `code_completion` (test). Reported as the unweighted mean
of three accuracies.

**Missingness and denominators.** The paper reports percentages with no denominators, intervals or
uncertainty anywhere in the safety setting. Tables 8, 12, 13 are annotated "n=10" and Table 10
"n=3"; **the paper never defines `n`**, it is not resolvable from the text, and the code for those
appendices was never released. Recorded as unresolved, not filled from convention.

**Selected exact published results** (v4, transcribed):

| Anchor | Value |
| --- | --- |
| Table 5, LLaMA-2-7B-Chat, Steer2Edit | Avg Safety **88.15**; GCG 95.10; ADV-LLM 81.20; Avg Utility 28.00 (CSQA 45.01, CodeMMLU 20.06, GSM8K 18.93) |
| Table 11, LLaMA-2-7B-Chat | Original 49.9 safety / 60.1 over-refusal; Steer2Edit **88.1 / 66.4** |
| Table 13, Qwen2.5-VL-7B-Instruct | Original 73.9 safety / 76.6 utility; Steer2Edit (ρa .3, ρm .5, α .5) **98.2 / 76.0** |
| Table 12, LLaMA-2-70B-Chat | Original 66.6 safety; Steer2Edit 97.0, utility 51.8 → 35.7 |
| README best configs | llama2-7b ρa 0.18, ρm 0.55, α 0.8; mistral-7b ρa 0.42, ρm 0.55, α 0.75 |

Table 5's 88.15 and Table 11's 88.1 are independent cross-checks of the same quantity and they
agree. That makes **LLaMA-2-7B-Chat average safety ≈ 88.1** the most strongly corroborated single
number in the paper, and our reproduction target.

## 7. Observability, limitations and our novelty position

**What is observable.** Only: the token sequences the edited model emits; the keyword metric over
them; task accuracies; and internally, the λ distribution over components. The claim that the edit
"redistributes behavioural influence" across heads is an *interpretation* of where non-zero λ land.
A non-zero λ on a head shows the optimization assigned it budget given `g`; it does not show that
the head implements refusal. Causality would need component-removal and shuffled-direction
controls, which the paper runs for design choices (Appendix G ablations over `k`, `g`, `λ` variants)
but not as a mechanistic claim about safety localization.

**Author-acknowledged limits.** Rank-1 per component by construction; `α < 1` required;
hyperparameters need a held-out grid search; some settings leave one block entirely unedited; and a
broader-impact note that editing could in principle be inverted to reduce safety.

**Our separately identified concerns.** (i) No uncertainty anywhere in the safety setting, and an
undefined `n` on every appendix table. (ii) The native safety metric is permissive keyword
matching, so "88.1% safety" is an upper bound on withheld assistance. (iii) Table 5's best-safety
configuration costs enormous utility — average utility 28.00, GSM8K 18.93 — so "matched downstream
performance" in the abstract refers to selected points on a trade-off curve, not to this row; the
headline and this table must never be quoted together as if one implied the other. (iv) The budget
asymmetry partly manufactures the attention-dominance result (§5.2). (v) Probe generation is
unseeded (D6). (vi) Paper and code disagree on the probing dataset and on refusal selection
(D2, D3). (vii) The utility, truthfulness and over-refusal benchmarks are used with **no
bibliography entries at all** (see the reference audit).

**Novelty position, corrected.** Our brief, written from v1, states that the published safety
experiments are text-only and that applying the method to a VLM is "a separate adaptation" whose
"performance and novelty remain open". **v4 Appendix N supersedes the first half of that.** The
authors apply Steer2Edit to Qwen2.5-VL-7B-Instruct by editing the LLM backbone with the same
pipeline, and report 98.2% safety at preserved utility (Table 13). "Steer2Edit works on a VLM" is
therefore published, and our brief's framing must be narrowed.

What Appendix N does **not** do, in its own words: "Safety and utility are evaluated on
**text-only benchmarks** to measure whether edits to the language backbone preserve general
capabilities." The directions are text-derived, the attacks are text suffixes, no image is involved
at any point, and the vision encoder is explicitly untouched. The open question is therefore
narrower and sharper than the brief states, and it is still open:

> Do text-derived directions and component importance scores select the right components when the
> harmful intent is carried by the **image** rather than the text — and does calibration with
> matched text/image pairs fix component selection at comparable harmful-assistance ASR and
> retained image-grounded utility?

This is a better research question than the brief's, because the authors have now supplied the
text-only VLM baseline we would otherwise have had to establish ourselves, and because our
completed MM-SafetyBench panel supplies exactly the image-carried conditions (TEXT / SD / TYPO /
SD_TYPO) that Appendix N omits. The novelty claim must be stated against Appendix N, not against v1.

## 8. Ten answered study questions

1. **Why must `u_i` be collinear with `v_i`?** Semantic invariance demands `zᵀΔW h = 0` for every
   input and every `z ⊥ v_i`; a rank-1 map's output lies in `span{u_i}`, so any part of `u_i` off
   `v_i` leaks into an orthogonal direction. Independent of `k_i` and `λ_i`, so it is solved first.
2. **Why `k̂_i = W_iᵀv_i` rather than something learned?** It maximizes the absolute Pearson
   correlation between the induced alignment shift and the component's intrinsic alignment score,
   so the edit fires on the inputs the component already uses — reusing its own input sensitivity
   instead of inventing a trigger.
3. **`k_i` versus `λ_i`?** `k_i` is input-conditional (how the effect varies across inputs); `λ_i`
   is one number from the *average* alignment (how much the component is reinforced or suppressed).
4. **Why normalize `g_i` twice?** Raw `E[s_i]` scales with both `‖v_i‖` and the component's output
   magnitude, which differ by orders of magnitude across layers; dividing by both gives a cosine in
   `[−1,1]`, so one global `(ρ, α)` applies to every component.
5. **What does `α` control?** Gate and gain jointly — gate `ρα`, gain `1/(ρ(1−α))`. Raising `α` at
   fixed `ρ` makes the edit sparser *and* amplifies each survivor; the two cannot be tuned
   independently in this parameterization, which is a design limitation.
6. **Why can `λ_i` be negative?** `sign(g_i)` is preserved, so a component whose output
   consistently opposes the refusal direction is suppressed. Edits both add and remove influence.
7. **Inference cost?** None. `W' = W + ΔW` is stored, so the forward pass is unchanged and standard
   batched or parallel inference applies — the central practical advantage over hooks.
8. **How is an MLP neuron rank-1 if it is one column?** Its input dimension is 1, so `k̂` can only
   be `±1` and the update degenerates to adding `±λ v̂` to that column; the code folds the sign into λ.
9. **Why 353,280 candidates but few edits?** Soft-thresholding requires `|g_i| > ρα`, and cosines
   between a mean-difference direction and a component's mean output are small for most components.
10. **Could a high refusal rate mean blanket refusal?** Yes, and the native metric cannot tell them
    apart — which is why Appendix L was added in v3/v4: at matched ~66% over-refusal Steer2Edit
    reports 88.1% against steering's ~65.7%. But over-refusal still *rises* from 60.1% to 66.4%, so
    the edit is not free of blanket caution.

## 9. Released, missing and unrecoverable

| Resource | Status |
| --- | --- |
| Editing, direction-extraction, generation and evaluation code for 3 settings | Released |
| GCG + ADV-LLM adversarial prompts for llama2-7b, mistral-7b | Released — no attacker run needed |
| MaliciousInstruct (100) + Alpaca benign (100) probes | Released |
| Published best configurations | Recoverable from README `visualize_edit.py` invocations only |
| Refined grid ranges | Table 2 (v4) |
| Appendix L / M / N / O / P / Q implementations | **Not released**; repo predates those versions |
| Probe responses used for the published directions | **Not released**; unseeded sampling (D6) makes them unrecoverable |
| Checkpoint revisions | **Not pinned** anywhere |
| Meaning of `n` in Tables 8/10/12/13 | **Undefined** in the paper |
| Per-config raw outputs, λ tensors, direction tensors | Not released |

The native reproduction contract that this study specifies lives in
[the reproduction contract](STEER2EDIT_REPRODUCTION_CONTRACT.md).

## 10. Validation performed on CPU

`tools/steer2edit_edit_math.py` is a reference transcription of the released arithmetic plus a
validation suite. **11/11 checks pass** on a synthetic single-layer fixture (hidden 64, 8 heads,
intermediate 96) at the published llama2 configuration:

component shapes and orientation (`k̂ ∈ R^{d_head}`, unit norm); rank-1 change per edited head
(max `s₂/s₁ = 4.15e-08`); disabled-edit parity at `ρ = −1` (zero factors, bitwise-identical
weights); only intended weights modified (5 heads and 96 neurons untouched); finite arithmetic
(max |λ| = 2.15); exact restoration (max residual 1.49e-08 in float32); deterministic edit
construction across rebuilds; zero-norm steering vector handled without exception; zero mean
activation handled per the `g := 0` convention; bf16-versus-fp32 selection agreement (Jaccard
1.000, observational); and the structural result that MLP `|g|` is independent of `‖μ‖`.

One caution found while building this: `torch.linalg.matrix_rank(Δ, tol=1e-8)` reports rank 5–8 for
a mathematically rank-1 `Δ`, because that tolerance is **absolute** and float32 rounding noise sits
above it. A rank check on these edits must compare `s₂/s₁`.

Not yet validated, because it needs the real model: `save_pretrained` round-trip fidelity at 7B
scale, the behaviour of the 20-prompt degeneracy screen, and component-selection stability in
bfloat16 across 353,280 real components near the gate.

## 11. Execution state and next action

**Verified:** paper identity, four versions, NeurIPS acceptance, repository commit, all five
equations against code, both published best configurations, the pre-release of both attacks, ten
paper/code discrepancies, the undefined `n`, the missing benchmark citations, 11 CPU checks.

**Uncertain:** whether the 125-configuration grid re-finds ρa 0.18 / ρm 0.55 / α 0.8; whether bf16
selection is stable at real scale; what `n=10` denotes; how much attention dominance survives
per-type normalization.

**Execution state:** preparation and CPU validation complete — no model loaded, no weights
downloaded, no published number reproduced, nothing pushed. **Next action:** owner approval for the
reproduction-contract scope, specifically gated LLaMA-2-7B-Chat access and the GPU/disk budget for arm (a).
