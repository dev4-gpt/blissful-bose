# VLM Safety Proposal: Paper Reading Guide

Use this guide with the numbered IEEE references in the presentation. It is a targeted reading route, not a claim that every paper has been independently reproduced. Read the papers that supply our primary methods/results closely; read attack and benchmark papers for the exact threat model, construction, scoring, and limitations. A result table should only be quoted after checking its caption, model/version, judge, and metric in the paper itself.

**Companion documents:** [Protocol audit](vlm_safety_protocol_audit.md) contains the SOTA map, protocol comparisons, reported-result tables, benchmark cards, and proposed study design. [Methodology comparison](methodology_comparison.md) covers broader continual-learning alternatives, many of which are not direct VLM safety baselines. Slide references are grouped by role, but citation numbers remain global and unchanged.

## The Short Route

Read these seven papers’ method and experiment sections closely before presenting the proposed baseline ladder:

1. **[5] VLGuard:** multimodal safety-SFT baseline and data boundary.
2. **[6] SafeVLM:** architectural safety module; inspect its safety, over-refusal, capability, and ablation results.
3. **[7] SPA-VL:** preference-data construction and how it can support standard DPO.
4. **[8] CMRM:** representation-gap diagnosis and inference-time correction.
5. **[12] ADPO:** direct adversarial preference-alignment prior art and strongest training comparator in this proposal.
6. **[15] VLMGuard-R1:** external reasoning-driven rewriter; understand that target VLM weights remain unchanged.
7. **[16] VSFA:** recent label-free training alternative; compare its data, safety, utility, and over-refusal claims.

Add **[13] Think in Safety** if you plan to discuss reasoning-based alignment as a candidate method. For runtime-method breadth, read [21] GuardAlign, [22] SafeSteer, [23] SafeRI, [24] SafetyReminder, and [25] MMAligner selectively as described below. Do not present all methods as if they were interchangeable training baselines.

## Per-Paper Reading Map

“Main comparison” below means the paper’s own central result table/figure and its caption. Where this guide does not give a table or figure number, that number has not been verified here; use the paper’s section heading and caption rather than guessing. Use the cited version/venue in the bibliography, and check whether a preprint differs from the published version.

| Ref. | Paper and role | Read in the paper | Inspect in particular | What it contributes to our pipeline |
|---|---|---|---|---|
| [1] | FigStep; image-text attack | Attack construction, experimental setup, main evaluation, limitations | Typographic-image examples and ASR comparison; note the target model versions | Canonical OCR/image-carrier attack, not a general-purpose safety benchmark |
| [2] | MM-SafetyBench; benchmark/attack suite | Dataset construction and risk/channel taxonomy, evaluation protocol, model comparison | Construction examples and per-channel results; verify the dataset release/version | Broad synthetic test set; use slices and controls, not as the whole evaluation |
| [3] | HADES; semantic visual attack | Attack design, attacker access, experimental setup, main results, limitations | Crafted-image examples and model-specific ASR table | Visual-semantic attack family distinct from OCR attacks |
| [4] | JailBreakV-28K; attack collection/benchmark | Source-intent collection, text/image attack generation, split and evaluation | Dataset statistics and results by attack type | Broad attack source; split/deduplicate by original intent to prevent leakage |
| [5] | VLGuard; training data + safety SFT | Safety-data construction, fine-tuning setup, safety and utility evaluation, limitations | Main safety/utility comparison and any train/test overlap controls | B2 multimodal safety-SFT baseline and a data resource |
| [6] | SafeVLM; safety architecture | Method’s two-stage training and module design; experiments and ablations | Tables 1–5, especially Table 3 (text attack/safe-instruction trade-off) and Table 4 (capability) | Architectural comparator; evidence for reporting false refusal and utility separately |
| [7] | SPA-VL; preference dataset | Preference-data collection/annotation, taxonomy, quality checks, preference-tuning experiments | Dataset scale/domain breakdown and main preference-alignment comparisons | Data source for a standard DPO baseline; not itself an attack algorithm |
| [8] | CMRM; inference-time representation correction | Section 3 method and Sections 4.1–4.4 experiments; Appendix A.3 for hidden-state effects | Figure 1 is a representation-separation diagnostic, not a full pipeline diagram; Table 1 is the main safety/utility comparison | Mechanistic comparator; motivates text/image controls and explicit inference-time system boundary |
| [9] | VLSBench; leakage-controlled benchmark | Benchmark construction, leakage control, evaluation design and limitations | Main comparison and image/text leakage or ablation conditions | Checks whether safety decisions require image evidence |
| [10] | VSCBench; calibration benchmark | Paired safe/unsafe case design, metrics, evaluation and limitations | Pair-level results for under-safety and over-safety | Benign near-neighbor and false-refusal evaluation |
| [11] | SIUO; compositional benchmark | “Safe inputs, unsafe output” construction, domains, scoring, generation/MC protocols | Dataset size/domain breakdown and main model results | Small, targeted test for interaction risk; do not misrepresent its scale |
| [12] | ADPO; adversarial preference alignment | Sections 3–4.5; Appendix A for settings and Appendix B for added experiments | Figure 2 pipeline; Table 1 safety/utility; Figure 5 alpha ablation; Table 2 training time; Appendix hyperparameters | B4 direct adversarial-alignment comparator. Track its model size, white/black-box access, utility loss, and training cost |
| [13] | Think in Safety; reasoning/data method | Method and training-data construction, evaluation protocol, main results and ablations | Safety reasoning pipeline and appendix’s MSSBench sampling details | Reasoning-based related work; include as a baseline only if resources and scope support it |
| [14] | MemeSafetyBench; ecological benchmark | Data collection/labeling, class distribution, evaluation and limitations | Class balance and per-class model results | Optional ecological slice; report balanced/class-specific metrics |
| [15] | VLMGuard-R1; external prompt rewriter | Section 2 Method; Sections 3.1–3.6; Appendix A.2–A.3 | Figures 1–2 system/data pipeline; Tables 1–5 results/ablations; Table 6 refusal-string DSR caveat; Tables 8–9 latency/scaling | System-level guard comparator, not target-model fine-tuning; count rewriter calls and latency |
| [16] | VSFA; label-free training | Method and data construction; Sections 4.3–4.4 for modality ablation and mechanistic analysis; limitations | Figure 1 method/data construction; Table 1 safety and Constructive Score across four VLMs; Table 2 over-refusal/MM-Vet; Figure 2 image/text/mixed-data ablation | Recent training alternative; prevents an overbroad novelty claim about safety data or label efficiency. Check the synthetic-data scale and model/checkpoint details before comparing results |
| [17] | USB; unified safety benchmark | Risk/modality taxonomy, dataset construction, scoring, model panel and results | Risk-by-modality coverage and benign over-refusal results | Broad evaluation source; select a preregistered VLM-relevant slice |
| [18] | MMJailBench; factorized benchmark (preprint) | Factor definitions, configurations, judges, full/lightweight protocols and results | Factor ablations and evaluation-mode comparison; verify preprint/code version | Design precedent for attributing intent, framing, visual semantics, and carrier effects |
| [19] | PolyJailbreak; adaptive black-box attack | Attack/search procedure, attacker feedback, query budget, target interactions and evaluation | Attack algorithm diagram, budget controls, transfer/results and limitations | Held-out adaptive evaluation only; never put its generated attacks in training or validation |
| [20] | JailBound; internal-boundary attack | Safety-boundary probing/crossing method, access requirements, white/black-box transfer evaluation | Boundary construction and main success/transfer results | Optional white-box diagnostic; separate from ordinary black-box visual jailbreaks |
| [21] | GuardAlign; test-time defense | Method/system boundary, unsafe-region detection and attention calibration, experiments and ablations | Main safety and utility table; identify exact test slice behind “up to” claims | Inference-time comparator; account for detector/calibration errors and runtime |
| [22] | SafeSteer; decoding-level defense | Steering/decoding mechanism, trigger/activation, evaluation, ablations and cost | Main safety/utility comparisons; distinguish decoding intervention from training | Runtime method landscape; check the exact ACL version because similarly named drafts exist |
| [23] | SafeRI; token-level intervention (preprint) | Recognizer and gated-LoRA method, trigger policy, evaluation, ablations and limitations | Main safety/utility results and runtime overhead; confirm version/date | Emerging selective-generation comparator; label as preprint, not settled SOTA |
| [24] | SafetyReminder; inference-time reminder | Reminder construction/injection point, attack evaluation, utility, ablations and limitations | Mechanism diagram and main attack/utility table | Prompt/representation-level inference defense, distinct from weight alignment |
| [25] | MMAligner; representation calibration (preprint) | Calibration objective, intervention point, evaluation, ablations and limitations | Main safety/utility comparisons and any calibration analysis | Representation-based inference comparator; verify code and preprint status before reproducing |
| [26] | Bach et al.; LLM-only project history | Read only if explaining the origin of the old project: method, task sequence, and limitations | Original LLM results and assumptions; do not transfer its numbers to VLMs | Context for why the project changed direction, not VLM evidence or a VLM baseline |

## How to Read the Evidence

For any reported result, record the exact base checkpoint/version, processor/chat template, training data and split, attacker access and budget, dataset slice, decoding settings, judge/threshold, metric direction, and uncertainty. Keep safety, helpfulness, false refusal, grounding, and cost as separate outcomes. A source-paper score is not a prediction of our result and is not comparable to another paper’s score unless the protocols are harmonized.

For the proposed experiment, map papers to components rather than making one large leaderboard:

| Proposed component | Primary reading |
|---|---|
| Native/text-only/SFT/DPO baseline ladder | [5], [6], [7], [12] |
| Direct adversarial-alignment comparator | [12] |
| Alternative label-free training mechanism | [16] |
| Representation/inference comparators | [8], [21], [22], [24], [25]; [23] as emerging work |
| External prompt-rewriting system baseline | [15] |
| OCR, semantic, adaptive, and internal attack families | [1], [3], [4], [19], [20] |
| Broad, compositional, leakage, calibration, and ecological test sets | [2], [9]–[11], [14], [17], [18] |

The **protocol audit is the synthesis and navigation document**, not a substitute for checking primary papers before quoting exact claims. You do not need to read every related-work citation in the audit. Deep-read the seven core methods above; then follow this table for every attack, benchmark, or numeric claim that appears in the talk. Optional alternatives in [methodology_comparison.md](methodology_comparison.md) are outside the presentation’s core numbered bibliography unless we explicitly promote them to a baseline.
