# Ten-Paper Visual Evidence Guide

**Snapshot:** 30 September 2026  
**Deck:** `VLM_Safety_Alignment_10_Paper_Proposal.pptx`, paper-review slides 7–11  
**Purpose:** specify which source figure explains each paper's method or benchmark, which table supports its reported result, and how each item maps to the proposed study.

## How to use this guide

For every paper, the **primary pair** is the recommended figure plus table. The figure explains the contribution; the table anchors the paper-reported evaluation result. A second result plot is listed only when it adds something the table cannot show. On the two-papers-per-slide review slides, do not paste four full-resolution source images: that will make them unreadable. Keep a high-resolution crop of each primary pair in the appendix/evidence dossier, and on the main slide use a single legible crop or a carefully redrawn, citation-labelled miniature with the exact paper/table/figure citation. Never recreate a paper's graphic without checking its original caption and metric definition.

The cited results are each paper's own-protocol results, **not comparable ranks**. Preserve model/checkpoint, benchmark split, judge, denominator, metric direction, and paper version beside every number. Source visual reproductions should retain the paper title/reference and figure/table number; check the venue's reuse terms before publishing or distributing the deck.

## At-a-glance map

| Deck slide | Paper | Primary figure | Primary table | Pipeline role |
|---|---|---|---|---|
| 7 | FigStep [1] | Fig. 2, attack construction | Table 1, mean ASR | Fixed image-text/OCR attack |
| 7 | PolyJailbreak [4] | Fig. 6, adaptive workflow | Table VI, ASR and harmfulness | Adaptive black-box red team |
| 8 | VLSBench [2] | Fig. 1, visual leakage/shortcut alignment | Table 4, alignment comparison | Leak-resistant test + image-dependence controls |
| 8 | USB [3] | Fig. 3, benchmark construction | Table 2, model outcomes | Risk/modality strata + benign over-refusal |
| 9 | VLGuard [5] | Fig. 3, safety/helpfulness behavior | Table 2, baseline and fine-tuning | Multimodal SFT baseline |
| 9 | SPA-VL [6] | Fig. 1, data/preferences construction | Table 2, DPO/PPO results | Preference data + standard DPO comparator |
| 10 | ADPO [7] | Fig. 2, ADPO method | Table 1, safety and utility | Adversarial preference comparator |
| 10 | HoliSafe / Safe-VLM [8] | Fig. 2, VGM/Safe-VLM architecture | Table 3, HoliSafe-Bench results | Five-state coverage + optional guard comparator |
| 11 | DAVSP [9] | Fig. 2, method overview | Table 2, resistance success rate | Frozen-backbone visual intervention |
| 11 | Pragma-VL [10] | Fig. 3, training/arbitration procedure | Table 2, safety/helpfulness | Optional alignment comparator |

## Paper-by-paper attachment recommendations

### 1. FigStep [1] — slide 7

**Attach:** Fig. 2 and Table 1. Fig. 2 is the actual paraphrase → typographic image → incitement-text construction. Table 1 is the source for the reported 82.50% mean FigStep ASR versus 44.80% vanilla-text ASR across the paper's six open VLMs. Table 2 is an ablation, not the source for that headline comparison.

**What to say:** “FigStep tests whether a VLM's text-side refusal still works when the harmful request is carried by text inside an image. On the paper's six-model set, the image-typography condition had a higher mean attack success rate than the direct-text condition. We use it as a fixed OCR/visual-text attack, paired with the same text-only intent and benign OCR controls. It is an older fixed attack, not an estimate for today's models.” The paper's success protocol tries each question five times and counts a success if any try succeeds; state that if discussing the exact percentage.

**Optional:** Fig. 1 for a high-level concept overview; Table 2 only when discussing the ablation. Prefer Fig. 2 when there is room for only one method illustration.

### 2. VLSBench [2] — slide 8

**Attach:** Fig. 1 and Table 4. Fig. 1 illustrates visual safety-information leakage (VSIL): a text query may reveal unsafe intent, letting textual alignment appear effective without genuine visual reasoning. Table 4—not Fig. 1—is the quantitative comparison: for LLaVA-1.5-7B, multimodal SFT total safety is 21.26%, multimodal DPO 27.01%, text SFT 13.99%, and text DPO 13.99%. “Total safety” sums refusal and warning in the paper's rubric; it is not ASR.

**What to say:** “VLSBench asks whether the image is actually necessary to determine the risk. It removes the shortcut where the prompt itself announces the harmful intent. The table shows that, on this leakless test, the listed multimodal tuning conditions score above the text-only conditions for this checkpoint. We will therefore report original-image and image-removed/masked/decoy controls separately. This result is specific to the paper's test and scoring rubric.”

**Optional:** Fig. 2 for concrete leakage examples, but label those as examples of leakage in prior-style benchmark pairs, not examples of the leakless VLSBench construction. Keep the main table caption visible.

### 3. USB [3] — slide 8

**Attach:** Fig. 3 and Table 2. Fig. 3 shows the benchmark/data-synthesis and evaluation framework. Table 2 reports the model results by risk/modality state; for the exact row shown in the short deck, the paper's model string is **Claude-Sonnet4**, with total SR 91.16% and RR 18.30 ± 0.75. The authors define SR on harmful inputs as the fraction receiving a safe response and RR on harmless inputs as the fraction incorrectly refused. Thus higher SR and lower **benign-input** RR are desirable. Do not write simply “lower refusal is better” without that benign qualifier.

**What to say:** “USB contributes coverage and measurement, not an alignment algorithm. It crosses 61 risk categories with four image/text risk states and reports harmful-input safety separately from over-refusal on harmless inputs. That separation is why our results table must show harmful compliance and benign false refusal side by side. This benchmark is broad MLLM evidence; our study should prespecify the relevant VLM strata rather than pool every cell.”

**Optional:** Fig. 5 is the actual safety-versus-benign-over-refusal plot. Fig. 2 is the risk taxonomy. Fig. 1 is not the trade-off plot. Do not substitute Table 1 dataset difficulty scores for Table 2 model safety results.

### 4. PolyJailbreak [4] — slide 7

**Attach:** Fig. 6 and Table VI. Fig. 6 is correctly the adaptive attack workflow: model discovery, attack initialization, then an RL-based optimization loop. Table VI reports the paper's eight-target comparison; PolyJailbreak averages 83.34% ASR and 3.976/5 harmfulness score, with ASR and severity kept as separate metrics. The paper lists GPT-4.1 among its target models; preserve exact table spellings/model versions. Its maximum of 15 optimization steps is paper-specific, not a universal total API-call budget.

**What to say:** “Unlike FigStep's fixed transformation, PolyJailbreak learns from black-box feedback and changes text/image strategies during optimization. Its table reports both whether the attack succeeded and how harmful the response was. For our protocol, we will preserve this as a separate adaptive tier, show success versus query/step curves, and log target calls separately from auxiliary agent, judge, and image-generation calls.”

**Optional:** Fig. 7 to show cumulative ASR across five optimization steps against baselines; this is a result curve, while Fig. 6 is the method diagram. If explaining adaptive cost, the curve is more helpful than Fig. 6 alone.

### 5. VLGuard [5] — slide 9

**Attach:** Fig. 3 and Table 2. Fig. 3 visualizes the safety/helpfulness trade-off across fine-tuning choices. Table 2 is the main quantitative comparison; crop only the exact baseline/post-hoc/mixed rows and the column headings needed for the claim. In the LLaVA-v1.5-7B comparison, baseline FigStep is 72.62% ASR, post-hoc 0.23%, and mixed tuning 0.90%. Preserve the other benchmark columns when making any helpfulness or safe-input claim; those values are not interchangeable with ASR.

**What to say:** “VLGuard is a practical multimodal safety-SFT baseline. It shows that fine-tuning can sharply change harmful-response rates, while the safe/helpfulness conditions reveal why safety alone is not enough. We use it to define an image-conditioned SFT arm and retain ordinary helpfulness data, then measure false refusal on matched benign neighbors.”

**Optional:** Fig. 1 for the motivating safety degradation after VLM tuning; Appendix Table 13 if making a specific additional helpfulness claim. Do not claim utility is preserved from the FigStep column alone.

### 6. SPA-VL [6] — slide 9

**Attach:** Fig. 1 and Table 2. Fig. 1 is the dataset-construction workflow and shows the easy question, hard question, and hard statement paths into preference construction. Table 2 reports results for DPO/PPO on MM-SafetyBench, AdvBench, and HarmEval. For the row quoted in the current deck, SPA-VL-DPO reports MM-SafetyBench average ASR 0.60%, AdvBench vanilla/suffix 0.00%/0.00% under the authors' setup. Table 1 is the more useful alternative if the slide needs split/category and data-statistics evidence instead of an outcome table.

**What to say:** “SPA-VL contributes preference data: for each image/question, a chosen response is paired with a rejected response. DPO is the optimization method that teaches the model to prefer the chosen answer; it is not the name of the dataset. The paper reports low attack rates on its test suite after training, but these numbers do not establish transfer to a held-out adaptive attack. In our design it informs preference-data provenance and a standard DPO comparator.”

**Important source note:** the abstract says 13 categories, while §3.1 states 15 secondary categories; do not silently normalize the mismatch. It is precisely **13 versus 15 secondary categories** (with 53 subcategories/tertiary categories also stated).

### 7. ADPO [7] — slide 10

**Attach:** Fig. 2 and Table 1. Fig. 2 presents the ADPO training procedure. Table 1 is the main safety/utility results table; crop the base and ADPO rows across the five named attack columns, retaining headings. For LLaVA-1.5-7B, the reported base → ADPO ASRs are 64.5→5.0 (VisualAdv), 84.0→0.5 (MMPGDBlank), 22.2→0.0 (MultiTrust Typographic), 55.1→0.0 (Multimodal), and 42.0→0.2 (Crossmodal), all percent. Do not omit the separate utility columns if claiming utility is maintained.

**What to say:** “ADPO is direct prior art for adversarially aware multimodal preference alignment. It changes the preference-training process to account for adversarial distortions and reports substantially lower ASR on its tested attacks. Its table also reports general capability, and those values can move; we should not summarize the result as ‘safety improved for free.’ We would include this comparator only if its recipe and attack assumptions are reproducible.”

**Optional:** Fig. 1 for the motivating failure under white-box attacks; Fig. 3 for the safety/utility trade-off; Table 2 for training-time comparison.

### 8. HoliSafe / Safe-VLM [8] — slide 10

**Attach:** Fig. 2 and Table 3. Fig. 2 is the Safe-VLM/Visual Guard Module architecture. Table 3 is the primary HoliSafe-Bench result and varies by judge. In the cited arXiv version, Safe-LLaVA-7B reports 8.8% mASR and 1.3% RR under Claude-3.5, and 15.3% mASR under GPT-4o. Keep judge and version attached; do not swap in an ablation value or a different judge's score.

**What to say:** “HoliSafe fills five image/text safety states, including safe-looking inputs that can yield unsafe outputs, and Safe-VLM adds a visual safety classification path alongside generation. The result is judge-dependent, which is a useful reminder to report evaluator sensitivity. In our study, the five-state framing can inform coverage; the VGM is an optional separate comparator, not something to stack automatically with every training method.”

**Optional:** Table 1 for why the benchmark's five-state coverage differs from earlier resources; Table 7 for ablation only. Fig. 1 is qualitative output comparison, not the architecture or a five-state taxonomy diagram.

### 9. DAVSP [9] — slide 11

**Attach:** Fig. 2 and Table 2. Fig. 2 gives the method overview: learned visual safety prompt plus deep alignment while freezing the base model. Table 2 reports resistance success rate (RSR), not ASR. The cited values are FigStep 84.20% for LLaVA-1.5-13B and 99.20% for Qwen2-VL-7B; MM-SafetyBench SD+TYPO 98.72% and 99.12%, respectively. Higher RSR means greater resistance in the paper's definition.

**What to say:** “DAVSP is a visual-side intervention rather than ordinary full-model SFT or DPO: it learns a safety prompt/activation-space adjustment while leaving the base model frozen. Its result uses RSR, so we must not compare it numerically with another paper's ASR. We map it to an optional intervention arm and measure its added inference cost and general capability.”

**Optional:** Fig. 1 contrasts conventional perturbation with DAVSP; Table 1 or Table 4 for capability/ablation, if those claims are discussed.

### 10. Pragma-VL [10] — slide 11

**Attach:** Fig. 3 and Table 2. Fig. 3 explains the staged training and context-aware arbitration process. Table 2 reports the safety/helpfulness outcomes; for Qwen2.5-VL-7B, the deck's cited MM-SafetyBench ASR is 31.66% vs. 48.75% for the base model, and the SIUO effectiveness/safety rates are 95.21%/63.47% vs. 92.17%/38.78%. Keep metric names and directions with every value. Table 3 is needed if claiming general VQA/math capability is retained.

**What to say:** “Pragma-VL treats safe behavior as a context-sensitive decision rather than maximizing refusals. Its training combines visual risk perception with a reward model that balances safety and helpfulness according to the query. The results are encouraging on the paper's own suite, but the metrics differ by benchmark. We treat it as a possible comparator only after checking released data/code, compute, and compatibility with the selected base model.”

**Optional:** Fig. 1 to introduce the risk-blind/over-refusal failure modes; Fig. 2 if it better fits your narration of data/reward construction; Table 3 only for capability results.

## Check of the Gemini audit suggestions

| Suggestion | Primary-source check | Action for our materials |
|---|---|---|
| “Claude Sonnet 4 does not exist.” | Incorrect. USB Table 2 uses the exact string `Claude-Sonnet4`; it reports SR 91.16% and RR 18.30 ± 0.75. The paper defines RR on harmless inputs. | Keep the paper's exact model label and explicitly call RR benign-input over-refusal. |
| “GPT-4.1 in PolyJailbreak is likely a typo.” | Incorrect. PolyJailbreak names GPT-4.1 among its four closed-source test targets and has a GPT-4.1 result column in Table VI. | Keep GPT-4.1 exactly as printed in the paper. |
| “VLSBench's 21.26/27.01 result belongs to Fig. 1, not Table 4.” | Incorrect for the exact numeric cells. Fig. 1 illustrates shortcut alignment/VSIL; Table 4 is captioned as the alignment-method comparison and contains the listed numbers. | Retain Table 4 for the values; use Fig. 1 to explain why the benchmark is needed. |
| “Lower refusal rate should be qualified as benign.” | Correct and important. USB RR counts refusals on harmless queries. | Use “benign-input false-refusal rate” every time; SR is evaluated on harmful queries. |
| “SPA-VL discrepancy needs exact counts.” | Correct. The abstract says 13 categories; §3.1 says 15 secondary categories; both state 53 lower-level categories. | State the precise 13-vs-15 discrepancy and identify the two locations. |

## Pipeline-design additions worth keeping

1. **Deduplication and contamination audit:** the existing system diagram already calls for intent/image deduplication and splits before derived prompts or attacks. Operationalize this in the protocol: exact hashes and perceptual hashes for images; image-embedding nearest-neighbor review (e.g., CLIP); exact/near-duplicate text plus semantic-intent similarity review; human adjudication for borderline matches. Include generated/rendered variants. Set thresholds on development data, not the locked test. Similarity tools are screens, not proof of no leakage.
2. **Separate weight updates from inference wrappers:** conceptually, compare intrinsic weight-updating arms separately from add-on inference components. Do not full-factor every combination by default. A feasible design is the core training comparison first, then a small pre-registered wrapper ablation on the native and best aligned checkpoints. DAVSP is a learned visual prompt/activation intervention; Safe-VLM's auxiliary visual safety head is an architectural add-on. Measure latency and extra calls for wrapper arms.
3. **Isolate text-only versus multimodal SFT:** use the same source intents, risk/benign distribution, split, examples-per-intent, and optimization budget. In the text-only arm, provide the same text but no image; do not use a blank image by default, because that introduces an image-conditioned training artifact. If a model interface requires an image tensor, document and separately validate the placeholder control. Keep helpfulness examples matched.
4. **Make adaptive-attack cost visible:** report target-model queries and success-vs-query curves, plus separate auxiliary-agent, judge, and image-generation calls, tokens, wall time, and monetary cost where available. Keep PolyJailbreak's optimization-step count distinct from the total system-call budget. Cost-efficiency complements ASR; it does not replace fixed-budget ASR.

## Does the system diagram explain everything?

It explains the **end-to-end logic at a useful proposal level**: data provenance → labels and intent-level split → separate alignment arms → locked attacks/benchmarks and attribution controls → multidimensional scoring. It is good as the synthesis slide, not as a substitute for the rest of the deck or a runbook.

It does not encode the full dataset schema, concrete dedup thresholds, matched text-only/multimodal training controls, exact benchmark versions and sample counts, attack implementation parameters, query/cost accounting, judge rubric/human audit, statistical analysis plan, or feasibility/compute gates. Keep those in the protocol slide, the speaker notes, and the runbook. The diagram already includes deduplication at a conceptual level; an explicit “near-duplicate/source-intent audit” label can be added if the slide has room, but the exact CLIP or text-similarity implementation belongs in the written protocol.

The speaker notes for slide 19 should make clear that the pipeline is a proposed study design synthesized from prior work—not an end-to-end system already demonstrated by these ten papers. A small, orthogonal wrapper ablation can be a follow-on; it is not required to make the primary text-only versus multimodal alignment comparison valid.

## References

[1] Y. Gong *et al*., “FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts,” arXiv:2311.05608. [Paper](https://arxiv.org/abs/2311.05608).  
[2] X. Hu *et al*., “VLSBench: Unveiling Visual Leakage in Multimodal Safety,” in *Proc. ACL*, 2025, pp. 8285–8316. [Paper](https://aclanthology.org/2025.acl-long.405/).  
[3] B. Zheng *et al*., “USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models,” in *Proc. ACL*, 2026, pp. 21184–21211. [Paper](https://aclanthology.org/2026.acl-long.970/).  
[4] X. Wang *et al*., “PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs,” arXiv:2510.17277; published version in *IEEE Trans. Dependable Secure Comput.*, 2026. [arXiv paper](https://arxiv.org/abs/2510.17277).  
[5] Y. Zong *et al*., “Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models,” in *Proc. ICML*, PMLR, vol. 235, 2024, pp. 62867–62891. [Paper](https://arxiv.org/abs/2402.02207).  
[6] Y. Zhang *et al*., “SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision Language Models,” in *Proc. IEEE/CVF CVPR*, 2025, pp. 19867–19878. [Paper](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision_Language_CVPR_2025_paper.html).  
[7] F. Weng *et al*., “Adversary-Aware DPO: Enhancing Safety Alignment in Vision Language Models via Adversarial Training,” in *Findings of EMNLP*, 2025, pp. 13644–13657. [Paper](https://aclanthology.org/2025.findings-emnlp.735/).  
[8] Y. Lee *et al*., “HoliSafe: Holistic Safety Benchmarking and Modeling with Safety Meta Token for Vision-Language Model,” in *Proc. IEEE/CVF CVPR Findings*, 2026. [Paper](https://arxiv.org/abs/2506.04704).  
[9] Y. Zhang *et al*., “DAVSP: Safety Alignment for Large Vision-Language Models via Deep Aligned Visual Safety Prompt,” in *Proc. AAAI*, vol. 40, no. 44, 2026, pp. 38111–38119. [Paper](https://ojs.aaai.org/index.php/AAAI/article/view/41149).  
[10] M. Wen *et al*., “Pragma-VL: Towards a Pragmatic Arbitration of Safety and Helpfulness in MLLMs,” in *Proc. ICLR*, 2026. [Paper](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4054556fcaa934b0bf76da52cf4f92cb-Abstract-Conference.html).
