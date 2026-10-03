# VLM Safety Alignment: Evidence Dossier and End-to-End Research Map

**Snapshot:** 30 September 2026  
**Bibliography:** 29 entries: 28 VLM-related papers and [26], one LLM-only project-history reference. HoliSafe / Safe-VLM is [27]; this sweep adds DAVSP [28] and Pragma-VL [29].  
**Purpose:** connect prior work into an auditable research design. This is a literature-to-experiment system diagram, not a claim that the cited methods have already been combined or reproduced by us.

## What the proposed connection is

There is no single prior-art pipeline that combines all of these papers. They provide different parts of the research apparatus:

1. **Alignment-method papers** tell us what intervention to compare: safety SFT, preference tuning, adversarial preference tuning, label-free neutral-VQA tuning, architecture/guard modules, representation correction, prompt rewriting, and generation-time steering.
2. **Training datasets** tell us what supervision is available and how it is structured: image/question/response examples, chosen/rejected preference pairs, safety labels, or the five joint image-text states.
3. **Attack papers** define attacker access, image/text carriers, optimization budget, and attack families. They are not all benchmarks and are not interchangeable.
4. **Benchmarks** define the behavior to measure: unsafe compliance, benign false refusal, whether the image is actually needed, composition risk, risk-by-modality coverage, or ecological context.
5. **Evaluation protocol** freezes the base model, policy/rubric, data split, preprocessing, decoding, judge, and resource budget so differences can be attributed to the alignment condition.

The proposed end-to-end experiment is therefore: literature evidence → paper protocol audit → scope/threat model → disjoint intent and attack-family split → matched training arms → locked attack and benchmark evaluation → semantic judge plus human audit → safety/utility/grounding/cost analysis → defensible research claim. Papers enter this design by role; they are not all modules of one deployed model. The interactive workflow is [vlm_safety_alignment_end_to_end.html](vlm_safety_alignment_end_to_end.html), and the editable source is [vlm_safety_alignment_end_to_end.workflow.json](vlm_safety_alignment_end_to_end.workflow.json).

## Problem and study question

> For small open VLMs, under a shared evaluation protocol, how do text-only safety tuning, multimodal SFT, multimodal preference alignment, adversarial preference alignment, holistic five-state supervision/visual guards, and selected inference-time defenses compare on held-out visual and cross-modal attacks while preserving benign answerability, grounded image use, and practical cost?

**Primary outcome:** harmful-compliance rate (HCR) by attack family, with uncertainty and judge audit.  
**Required paired outcomes:** false-refusal rate (FRR) on safe near-neighbors; benign answer quality; VQA/OCR and image-grounding checks; training/inference cost.  
**Scope:** first paper is single-turn image+text assistants. Keep multi-turn, privacy, medical-specialist policy, fairness, image perturbation, and internal-boundary probing distinct unless explicitly included in the registered scope.

## End-to-end experimental roles

| Stage | Inputs / source papers | Study artifact | Decision or control |
|---|---|---|---|
| Literature intake | All 28 VLM papers; [26] LLM paper is context only | IEEE bibliography plus source/version ledger | Verify title, venue/version, paper status, and whether it is VLM alignment, attack, benchmark, or adjacent work |
| Protocol audit | Methods [5]–[8], [12], [13], [15]–[16], [21]–[25], [27]; attack/benchmark papers | Per-paper data/method/target/attack/judge/metric/results/limitations row | Never compare raw scores across different models, judges, budgets, or benchmark definitions |
| Freeze threat model | FigStep [1], HADES [3], JailBreakV [4], ADPO [12], PolyJailbreak [19], JailBound [20], factorized MMJailBench [18] | Harm policy; attacker access; fixed query and perturbation budgets; source-intent splits | Hold out attack families and source intents; white-box and black-box tiers remain separate |
| Prepare training arms | VLGuard [5], SafeVLM [6], SPA-VL [7], ADPO [12], Think in Safety [13], VSFA [16], HoliSafe [27], DAVSP [28], Pragma-VL [29] | Reproducible data subsets, preference pairs, labels, train/validation manifests | De-duplicate images/intents and document licenses; equalize or transparently curve data and training budgets |
| Train/compare | Training arms B0–B5, optionally system comparators | Frozen checkpoints/adapters and hashes | Distinguish target-model weight updates from upstream guards and test-time defenses |
| Locked test | MM-SafetyBench [2], VLSBench [9], VSCBench [10], SIUO [11], USB [17], MMJailBench [18], HoliSafe-Bench [27]; attack suite A0–A5 | Per-item model responses and run metadata | Never train/tune on locked test items; report benchmark slices and intent-level N |
| Score and audit | Paper-native judges plus our pre-registered rubric/human adjudication | Semantic HCR/FRR, pair quality, agreement, error audit | String-matched refusal is not a semantic harm judge; validate a stratified subset manually |
| Interpret and report | All candidate conditions | Result tables, intervals, utility, calibration, grounding, latency/compute | State what is supported, what failed, and what is not measured; no universal SOTA claim |

## Baseline ladder to take to the advisor

| ID | Condition | What it isolates | Prior-art relation |
|---|---|---|---|
| B0 | Native instruction-tuned checkpoint | Starting safety/utility behavior | Same frozen base model for all arms |
| B1 | Text-only safety SFT | Whether language-only safety transfers through image input | Control, not a VLM method claim |
| B2 | Multimodal safety SFT | Effect of image-grounded safe/unsafe supervision | VLGuard-style; compare with SafeVLM’s more architectural intervention |
| B3 | Standard multimodal DPO | Effect of preference objective and chosen/rejected labels | SPA-VL data resource plus standard DPO algorithm |
| B4 | ADPO | Adversarial reference plus adversary-aware preference training | Direct prior art; include if code/model/compute allow a faithful run |
| B5 | HoliSafe/Safe-VLM-style five-state training, with or without its VGM as separate subconditions | Reproduction and transfer at small model scale; data effect versus guard-module effect | Published CVPR 2026 Findings prior art; emphatically not our novel five-state formulation |
| B6, optional | VSFA neutral VQA or one selected inference-time defense | Alternative mechanism/system-level comparison | Keep labels, extra calls, latency, and changed model weights explicit |

Do not collapse B5’s data effect and VGM architecture into one opaque condition. If resources permit, use B5a five-state data-only SFT and B5b the VGM+same-data condition. Only do this if the authors’ training recipe and artifacts can be reproduced; otherwise present these as proposed conditions, not completed experiments.

## Attack and benchmark mapping

| Test cell | Primary source(s) | Why it is in the suite | Controls and outcomes |
|---|---|---|---|
| A0 matched text control (not an attack) | Same source intents as A1/A2 in ordinary text | Establish language-channel safety | Match intent IDs; HCR with same rubric |
| A1 fixed OCR attack | FigStep [1]; optional fixed JailBreakV-28K image-text subset [4] | Test image-carried text robustness | Hold out render templates/fonts; benign OCR controls; HCR by family |
| A2 fixed semantic-visual attack | HADES Typ and black-box +Opt [3] | Separate typography from semantically matched image effects | Keep Typ and +Opt separate; white-box +Adv belongs only in W1 |
| A3 compositional evaluation (not an attack algorithm) | SIUO [11], HoliSafe states [27] | Test whether joint image-text interpretation changes risk | Image-only/text-only/joint conditions; HCR by state |
| A4 attribution/calibration controls | VLSBench [9], VSCBench [10], USB [17], HoliSafe [27] | Test visual dependence and over-refusal | Original/removed/masked/decoy plus safe pairs; grounding and FRR |
| A5 adaptive black-box attack | PolyJailbreak [19] | Test beyond static templates under bounded adaptive search | Equal capped calls; report success-vs-query curve and cost |
| W1 optional white-box image perturbation | VisualAdv/MMPGDBlank in ADPO [12] | Open-weight robustness diagnostic | Separate from deployment black-box suite; fixed perturbation and compute budget |
| W2 optional internal-boundary probing | JailBound [20] | Tests internal safety boundary access, not ordinary user-input robustness | Report as a separate white-box diagnostic, never pool with black-box ASR |

**Recommended benchmark core:** HoliSafe-Bench [27] for the five-state structure; VSCBench [10] for calibration; VLSBench [9] for image-dependence; SIUO [11] for a targeted composition set; one broad vision-relevant slice of USB [17]; plus A0–A5 attack-family reporting. MM-SafetyBench [2] and JailBreakV [4] are useful broader sources, but not substitutes for safe-pair and leakage controls. The exact set and accessible versions must be frozen after checking licenses, data availability, and source-intent overlap.

**Executable protocol companion:** [VLM_ATTACK_PROTOCOL_SPEC.md](VLM_ATTACK_PROTOCOL_SPEC.md) specifies the proposed data lock, threat model, fixed and adaptive run sequence, query caps, judge/human audit, metrics, logging schema, result tables, and go/no-go checks. It explicitly distinguishes paper-native settings from harmonized project choices.

## Paper-by-paper evidence ledger

“Extracted” means a paper-specific result has been transcribed into the project’s tables and tied to that paper’s own metric. “Protocol map” means role and design are summarized, but exact table-by-table values still need an independent source check before they are put on a slide. A paper’s abstract alone is not enough for a result claim.

| Ref. | Paper / role in our system | Data/setup and reported evaluation to understand | Audit status in project; next exact read |
|---|---|---|---|
| [1] FigStep | Typographic image-carried attack | Image-rendered text, paired prompt; inspect target panel, ASR judge, transfer and benign OCR controls | Protocol map; verify paper’s main ASR table, model versions and attack construction |
| [2] MM-SafetyBench | Broad synthetic benchmark and attack channels | 5,040 image-text pairs, 13 risk scenarios; SD/OCR/combined styles; examine split and scoring | Dataset scale documented; extract exact per-channel/model results and defense protocol |
| [3] HADES | Semantic visual attack | Crafted images paired with harmful intent; headline reported ASR 90.26% LLaVA-1.5 and 71.60% Gemini Pro Vision in the original setup | Protocol summary; verify table, judge, attack image construction, and target versions |
| [4] JailBreakV-28K | Attack collection/benchmark, not one attack algorithm | 28K cases from 2K source prompts, including text-transfer and image-based variants; examine attack types, source split, model panel | Scale summary documented; verify paper table and deduplication/split details |
| [5] VLGuard | Multimodal safety dataset and SFT baseline | Safe/unsafe image-grounded data, safety SFT, post-hoc/mixed tuning, visual and advanced black-/white-box tests | Core method role mapped; exact dataset counts, table values, judge and training budget need full table pass |
| [6] SafeVLM | Safety projector/tokens/head architecture | LLaVA-v1.5-7B; RTVLM/risk-set GPT scores, text attacks, safe instruction pass rate, general VLM capability | Detailed Tables 1–5 transcribed in audit A.2; metrics remain paper-specific and attack table is text-centric |
| [7] SPA-VL | Preference dataset plus DPO experiments | 100,788 question/image/chosen/rejected records; six domains, 13 categories, 53 subcategories; inspect annotation and DPO sample size | Dataset schema and selected Table 7 results mapped; verify Tables 7–8, preference annotation quality, and train/test intent overlap |
| [8] CMRM | Representation-shift diagnosis and inference-time correction | Compares text-only and multimodal safety; calibrated representations; safety and utility tests | Protocol map and selected Table 1 values are cited in audit; verify all model/set definitions and exact metric direction |
| [9] VLSBench | Leakage-controlled benchmark | About 2,241 cases; asks whether the visual evidence is needed rather than leaked in text | Role/scale mapped; read construction, leakage controls, main table and judge details |
| [10] VSCBench | Safe/unsafe calibration benchmark | 3,600 paired cases; 11 VLMs; under-safety and over-safety | Role/scale mapped; extract pair scoring, exact metrics and per-model results |
| [11] SIUO | Safe inputs / unsafe joint-output composition benchmark | Targeted cross-modal cases; audit total examples, domain counts, generation and multiple-choice variants | **Count discrepancy to resolve:** project notes say 167; HoliSafe Table 1 labels 269. Read the SIUO primary paper and distinguish core split from expanded/all samples before quoting. |
| [12] ADPO | Adversarial preference alignment; direct training prior art | LoRA; adversarial reference + adversary-aware DPO; VisualAdv/MMPGDBlank and MultiTrust; HarmBench classifier; MMStar/OCRBench/MM-Vet/LLaVABench utility | Main Tables 1–2 and key settings transcribed in audit A.4; inspect appendices and attack budgets before implementation |
| [13] Think in Safety | Safety reasoning/data for multimodal reasoning models | Read training data/pipeline, five evaluation families, MSSBench/SIUO sampling and reasoning costs | Role mapped; extract exact dataset schema, table values, judge and latency/token costs |
| [14] MemeSafetyBench | Ecological real-meme benchmark | 50,430 examples; strong class imbalance reported (46,599 harmful / 3,831 benign); study contextual/multi-turn protocol | Scale/imbalance mapped; verify label process and per-class results before selecting a test slice |
| [15] VLMGuard-R1 | External reasoning-driven prompt rewriter | Rewriter trained on roughly 10K image/instruction examples; six target VLMs; safety/helpfulness, benchmark transfer, refusal-string DSR, latency | Selected Tables 1 and supplement values transcribed in audit A.3; verify version consistency with arXiv draft and current proceedings |
| [16] VSFA | Label-free alignment with neutral VQA over threat-related imagery | Four main VLMs; FigStep, MM-SafetyBench, SPA-VL; GPT-4o ASR/Constructive Score, MM-Vet and refusal outcomes | Tables 1–2 inspected; exact training-set scale, image sourcing, budget and ablations should be recorded before baseline decision |
| [17] USB | Unified broad safety benchmark | 61 risk categories × four modality interactions; 22 MLLMs; vulnerability and over-refusal | Coverage summary documented; read sample counts, aggregation, judge, and vision-specific extraction rule |
| [18] MMJailBench | Factorized benchmark (preprint) | 272 intents × 6 frames × 5 visual semantics × 2 carriers (16,320 configurations); 16 models; judge threshold and CASR | Factor design/result summary documented; verify exact lightweight/full protocol and preprint artifact version |
| [19] PolyJailbreak | Adaptive black-box cross-modal attack | Search/agent feedback, attacker queries, transfer and target interaction | Attack role mapped; exact algorithm, query budget, prompts, and evaluated versions remain to be checked in primary source |
| [20] JailBound | Internal-boundary white-box attack | Probes/crosses internal safety boundary; white/black-box transfer is a separate threat model | Role mapped; verify access assumptions, boundary definition and success metrics |
| [21] GuardAlign | Training-free test-time detection + attention calibration | Six models; unsafe-response reductions on SPA-VL and VQAv2 utility result reported in ICLR abstract | Abstract-level numbers only; extract main table, exact benchmark slice, detector false positives and runtime |
| [22] SafeSteer | Decoding-time discriminator/steering | Iterative decoding correction and alignment vector; reports up to 33.40% safety improvement | Abstract-level result only; inspect tables, attacks (FigStep/MMSafety/SPA-VL/ImgJP/GCG/BAP), model panel and overhead |
| [23] SafeRI | Token-level recognizer + gated LoRA (preprint) | SPA-VL-derived training; five safety and three general benchmarks; GPT-oss judge in current draft | Table summary present in prior source audit; re-check version/date, metrics (some reported as safe response rate), and runtime before claiming SOTA |
| [24] SafetyReminder | Inference-time reminder / soft-prompt training | Two VLMs; multiple safety benchmarks and image/prompt attacks; report ASR and utility | Published AAAI 2026; prior extracted average ASR values need rechecking against Table 1 and attack setup |
| [25] MMAligner | Representation calibration (preprint) | Unsafe multimodal representation moved toward refusal region; paper reports high refusal and low utility degradation | Abstract-level only; verify paper’s metric definition, benchmark panel, calibration/over-refusal, and artifacts |
| [26] Bach et al. | Historical LLM-only project approach | Continual safety alignment/gradient-based selection; not VLM data or evidence | Context only. Do not port its results or call it a VLM baseline. |
| [27] HoliSafe / Safe-VLM | Five-state safety dataset + benchmark + integrated VGM | 6,689 images/14,246 pairs; 10,215 training pairs; 1,796 images/4,031 test Q&A; 7 categories/18 subcategories; multi-judge ASR/RR and VGM classification | Detailed method, Table 3 and Table 4 selected results, judge protocol, and dataset split transcribed in audit A.6; check current CVPR Findings version, licenses, and source-data overlap |
| [28] DAVSP | Training-time visual safety prompt with activation-space alignment | Builds a harmfulness direction using 470 rejected malicious + 470 benign VLGuard examples; trains padding-based visual prompt on 600 MM-SafetyBench harmful + 100 MM-Vet benign samples; evaluates LLaVA-1.5-13B and Qwen2-VL-7B | Full AAAI paper checked §§3–5.6 and Tables 1–6. Table 2: FigStep RSR 84.20% (LLaVA-13B), 99.20% (Qwen2-VL-7B); MM-SafetyBench SD+TYPO 98.72%, 99.12%. Table 1 shows corresponding utility: LLaVA MM-Vet total 39.07, MME 1602, LLaVA-Bench 63.6; Qwen MM-Vet 61.61, MME 2146, LLaVA-Bench 75.2. Not directly comparable to other papers' judges/protocols. Reproduction details and adversarial-example analysis are in the extended version. |
| [29] Pragma-VL | End-to-end safety/helpfulness arbitration training method (ICLR 2026) | Cold-start SFT uses risk-aware visual-encoder clustering and interleaved risk descriptions/high-quality data; synergistic reward model uses query-dependent dynamic weights | Official ICLR abstract checked; it reports 5–20% gains over baselines on most multimodal safety benchmarks while retaining math/knowledge capability. Full paper, exact tables, evaluation setup, ablations, and cost not yet audited; read before quoting results or selecting as a baseline. |

## Readiness and evidence-quality rule

Detailed paper-specific numerical extracts currently expanded most deeply are SafeVLM [6], ADPO [12], VLMGuard-R1 [15], HoliSafe [27], and DAVSP [28]. Pragma-VL [29] is in the SOTA map based on official proceedings metadata/abstract; its full tables remain to be audited. The remaining references are not forgotten; the ledger above names what each is, where it enters the system, and what source work remains. Before the deck is called final, close the remaining primary-source checks for the method baselines, attacks, benchmarks, datasets, evaluator definitions, exact results, and artifacts. Each slide number should point to the source’s table/figure and metric definition, not merely its abstract.

Never pool author-reported values into one leaderboard. For every result store: checkpoint/revision, data split, number of unique source intents/images, attack access/budget, preprocessing and decode settings, judge/rubric/threshold, metric direction, uncertainty, utility outcome, and compute. Mark inaccessible or unverified values as “not checked,” never inferred.
