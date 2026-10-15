# Plan: Is VLM Safety a Text/Vision See-Saw? A No-Training Test on Open Models

**Date:** 2026-10-14 · **Author:** Aryaman Singh Dev · **Advisor:** Prof. Thao Minh Le (PSU)
**Compute:** free GPU, Kaggle (T4 x2 / P100) preferred, Colab T4 also works · **Code:** `notebooks/vlm_modality_tradeoff.ipynb`
**Constraints (from the advisor, see `vlm_cross_modal_conflict_plan.md`):** frozen models, no training, no new benchmark, no new defense. Open-source models and data only.

## 1. The question, stated so it can be falsified

The working reading of the professor: "language at X, vision at Y; vision drops by Z, language rises by Z." As hypotheses:

- **H_seesaw (zero-sum):** across channels, ΔS_text ≈ −ΔS_vision. Safety is a conserved budget the model moves between modalities.
- **H_shared (what the literature mostly says):** both channels route through the *same* refusal mechanism in the LLM backbone, so they move **together**, and vision is usually the weaker channel.
- **H_independent:** the channels do not predict each other.

The published evidence points toward H_shared plus a modality gap, not a see-saw. If we only look for a see-saw and find the opposite, that is still a clean result, but we should say so in advance rather than bend the data.

What the sources I found say (secondary reads of abstracts and search summaries; read the papers before citing a number):

| Finding | Source |
|---|---|
| Attaching a vision encoder weakens refusal even when the backbone was well aligned; cause is a representation shift between image+text and text-only inputs | [Unraveling and Mitigating Safety Alignment Degradation of VLMs](https://arxiv.org/pdf/2410.09047) (ACL Findings 2025) |
| Text safety does not transfer to images because image hidden states drift from text hidden states at the layers that trigger refusal | [Cross-Modal Safety Mechanism Transfer in LVLMs](https://arxiv.org/pdf/2410.12662) (ICLR 2025) |
| Visual instruction tuning damages the backbone's guardrails, on text-only prompts too | [Learning to See but Forgetting to Follow](https://arxiv.org/pdf/2405.04403) |
| VLLMs show higher attack success than their base LLMs on *text* harmful prompts; text-only safety data does not fix vision-language benchmarks | [VLGuard: Safety Fine-Tuning at (Almost) No Cost](https://arxiv.org/pdf/2402.02207) |
| Adapting an LLM to a VLM reduces safety even with safe data; text-only safety tuning is insufficient | [How Does Vision-Language Adaptation Impact Safety?](https://arxiv.org/pdf/2410.07571) |
| Modality gap is inversely correlated with safety and is introduced in pretraining | [arXiv 2505.24208](https://www.arxiv.org/pdf/2505.24208) |
| Counter-evidence: multimodal inputs can shift activations toward a *safer*-looking direction, so VLMs overestimate the safety of harmful inputs | [Understanding and Rectifying Safety Perception Distortion in VLMs](https://papers.nips.cc/paper_files/paper/2025/file/a627b9468c319c13a70b7c2fb8df65a3-Paper-Conference.pdf) (NeurIPS 2025) |
| Safety-only tuning causes over-refusal; adding ~5k helpfulness examples restores balance | VLGuard (above) |

**Where a real trade-off does show up:** safety versus helpfulness (over-refusal), not text versus vision. The design measures that too, so "one goes up, the other goes down" is tested where it most plausibly holds.

## 2. What we measure

For each harmful request we build four matched inputs (same item id, same intent):

| Cond. | Model | Input | Tells us |
|---|---|---|---|
| A | LLM backbone (e.g. Qwen2-1.5B-Instruct) | harmful question, text | backbone text safety |
| B | VLM (e.g. Qwen2-VL-2B-Instruct) | same question, no image | text safety *after* vision was added |
| C | VLM | typographic image holding the harmful phrase + generic prompt | vision-channel safety |
| D | VLM | same question + blank image | effect of "an image is present" alone |

Safety S = refusal rate (judge-labelled); higher is safer.

| Quantity | Definition | Reads as |
|---|---|---|
| Z_text | S(A) − S(B), paired bootstrap CI, exact McNemar | cost to text safety of adding vision |
| Modality gap | S(B) − S(C) | vision channel weaker than text channel |
| Blank-image effect | S(B) − S(D) | is the gap just "an image is there"? |
| Coupling | item-level phi(B,C); per-scenario Spearman(S_text, S_vision) | **negative = see-saw, positive = shared, ~0 = independent** |
| Over-refusal | refusal rate on 24 benign prompts, incl. safe-but-scary wording | the cost side of any safety gain |

## 3. Experiments

- **E1 Modality gap (A–D).** Descriptive. Produces Z_text, gap and blank-image effect per model pair.
- **E2 Coupling.** Same outputs. Item-level and scenario-level correlation between text and vision refusal. A correlation alone cannot prove zero-sum, hence E3.
- **E3 Causal steering (inference-only).** Learn a difference-of-means refusal direction from **text** prompts on held-out ids, add `c × direction` to the residual stream at 60% depth, sweep c ∈ {0, 0.5, 1, 2}. Record refusal on harmful text, harmful typographic image, and benign text.
  - Vision refusal ↑ with c: text-derived safety transfers → anti-see-saw.
  - Vision refusal ↓ while text ↑: genuine see-saw.
  - Benign refusal ↑: safety bought with over-refusal.
- **E4 (optional).** Third pair `llava-hf/llava-1.5-7b-hf` vs `lmsys/vicuna-7b-v1.5` in 4-bit (LLaVA is the family most prior work used).
- **E5 (optional).** Reuse the 6-instruction font-size pilot in `data/pilot_v2/` for illustration only; too few instructions for statistics.

## 4. Open-source assets

| Asset | ID | Notes |
|---|---|---|
| Data | `PKU-Alignment/MM-SafetyBench` | ungated, CC-BY-NC-4.0; splits `Text_only`, `TYPO` (also `SD`, `SD_TYPO`). Checked: `id` aligns across splits in `Illegal_Activitiy` (97 rows each); the notebook asserts this for every scenario |
| Scenarios used | Illegal_Activitiy, HateSpeech, Malware_Generation, Physical_Harm, EconomicHarm, Fraud, Sex, Privacy_Violence | the 8 clearly harmful ones. The five advice/political scenarios are excluded because refusal is not clearly correct there (my judgement from the names; confirm in the MM-SafetyBench paper) |
| Pair 1 | `Qwen/Qwen2-VL-2B-Instruct` ↔ `Qwen/Qwen2-1.5B-Instruct` | fits a T4 easily; backbone relation from memory, confirm in the model card |
| Pair 2 | `Qwen/Qwen2.5-VL-3B-Instruct` ↔ `Qwen/Qwen2.5-3B-Instruct` | same caveat |
| Pair 3 (opt.) | `llava-hf/llava-1.5-7b-hf` ↔ `lmsys/vicuna-7b-v1.5` | needs `LOAD_4BIT=True` |
| Judge | `Qwen/Qwen2.5-3B-Instruct` (REFUSAL / COMPLIANCE / OTHER) | open; a string-match baseline is logged beside it |

Model IDs were not all verified against the Hub this session; the notebook fails loudly on a bad ID.

## 5. Procedure

1. Open the notebook in Colab, runtime = T4 GPU. Run install and config cells.
2. Smoke test: `N_PER_SCENARIO = 5`, one pair, `DO_STEERING = False`. Read the printed first responses for each condition.
3. Full run: `N_PER_SCENARIO = 30` (240 items per condition), both Qwen pairs, steering on pair 1.
4. Everything caches to Google Drive; a disconnect resumes from the cached files.
5. Download `bundle.zip` (results.json, three figures, raw generations and labels).

Rough T4 time (estimate, not measured): 2B pair 30–45 min, 3B pair 45–60 min, steering about 20 min.

## 6. Validity checks (required before any number is quoted)

- **Judge audit:** hand-label 50 random items; report judge-vs-human agreement beside every rate.
- **OTHER rate per condition.** In C the model may only read the image aloud, which is neither refusal nor harmful compliance. Report REFUSAL, COMPLIANCE and OTHER separately.
- **Prompt confound.** C uses a different text prompt than B (the MM-SafetyBench rewrite), so part of the gap is OCR/format. D controls for "image present" but not for the rewrite. State this limit.
- **Small n.** About 240 items and 2–3 model pairs. Model-level correlation from 2–3 points is meaningless; only item- and scenario-level coupling is interpretable. Wilson CIs everywhere.
- **Crude steering direction** (difference of means, one layer, 24 benign prompts). A null transfer could mean a poor direction; sweep layers as a robustness check if time allows.
- **Licence:** CC-BY-NC is fine for research and a seminar.

## 7. Using alphaXiv OpenResearch

[alphaXiv/OpenResearch](https://github.com/alphaXiv/OpenResearch) (MIT) is a local-first harness and workspace that turns an existing coding agent (Claude Code, Codex, OpenCode, Cursor, Antigravity) into a research agent. It logs every experiment to a local SQL database, grounds literature work in alphaXiv, bioRxiv and PubMed, and can dispatch jobs to local, SSH, Slurm, Kubernetes, Modal, Ray or Hugging Face Jobs compute. This comes from its README via fetch; I did not install it.

- **It is not a model, benchmark or safety tool.** It cannot replace the experiments above; it wraps an agent that would run them.
- **Colab is not a listed backend**, so the free-compute path stays notebook-first. SSH needs a machine you control; HF Jobs is paid.
- **Useful parts:** an experiment ledger (code, logs, results per run, handy for a reproducibility appendix), literature grounding through alphaXiv, agent skills for hypothesis→run→write-up loops.
- **Risks:** young project; the CLI installs via an unsigned `curl | sh`; it sends opt-out analytics (`orx telemetry off`); I found no public extension API docs.
- **Recommendation:** do not make it a dependency for this deliverable. Optionally install the desktop app after the Colab run works and use it as the experiment log and literature aid.

## 8. Deliverables and schedule

| When | Deliverable |
|---|---|
| Day 1 | Colab smoke test (5 items per scenario); fix any model-ID or template issue |
| Day 2 | Full E1 + E2 on both Qwen pairs; judge audit |
| Day 3 | E3 steering; optional LLaVA pair |
| Day 4 | Figures from `results.json`, 8–10 slide deck, speaker notes |

**Slides (planned):** problem and hypothesis; what the literature already says; design (A–D matrix); E1 bars with CIs; E2 coupling scatter; E3 steering curves incl. over-refusal; verdict on H_seesaw / H_shared / H_independent; threats to validity; next steps.

## 9. Open questions for the advisor

1. Is the target claim "safety is zero-sum across modalities" or the weaker "vision is the weak channel"? The data speaks to both, but slide 1 framing differs.
2. Is no-training activation steering acceptable under the "no heavy model training" rule? It adds no weights and does no fine-tuning.
3. Is MM-SafetyBench (typographic channel only) enough, or should gated HoliSafe-Bench (five image/text safety states) be added, as in `PROJECT_PLAN_CROSS_BENCHMARK_EVALUATION.md`?
