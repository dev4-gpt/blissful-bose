# VLM Safety Alignment: Verified 10-Paper Analysis and Reading Checklist

**Evidence snapshot:** 30 September 2026  
**Scope:** a focused, primary-source audit of the ten papers used in the short proposal deck. This is not a systematic review of every VLM safety paper and does not replace the broader evidence dossier.

## What this document is

The paper analyses and selected numeric transcriptions below have been checked against the linked primary papers/proceedings. This is meant to give you a reliable first explanation of what each paper did and how it informs the research design. Each paper's audit now has exactly three explicit study questions, each followed immediately by a separate answer: the reading-route objective, a method/protocol question, and an evidence/interpretation question. Before presenting a number, open its cited table/figure and confirm its caption and metric direction. In particular, paper versions and judges matter.

The ten papers have different roles. Some introduce a benchmark, some an attack, some training data or a tuning method, and some an inference-time or architectural defense. They were not tested on one common dataset or under a shared protocol. **Do not rank their headline numbers against each other, claim that the proposed pipeline is already validated, or imply that all ten methods should be stacked.**

The focused deck now has paper-by-paper evidence on slides 7–11, a representative attack-family coverage matrix on slide 12, and the datasets/benchmarks summary on slide 13. The final proposed study diagram is on slide 19 of [VLM_Safety_Alignment_10_Paper_Proposal.pptx](../VLM_Safety_Alignment_10_Paper_Proposal.pptx). The attack runbook remains [VLM_ATTACK_PROTOCOL_SPEC.md](VLM_ATTACK_PROTOCOL_SPEC.md). This focused guide does not replace or modify the larger evidence dossier or long presentation.

## How the short proposal uses the papers

The short deck is not only a literature summary. It proposes an **end-to-end comparative research pipeline**: curate and label image-text safety data; split by source intent before creating variants; compare a small set of distinct alignment arms; test them with fixed and adaptive attacks plus leak-resistant benchmark slices and benign controls; then report safety, false refusal, helpfulness, grounding, capability, and cost. Slides 7–11 establish what the cited papers contribute; slides 12–18 specify attacks, benchmarks, baselines, and evaluation; slide 19 is the synthesis diagram; slides 20–22 cover protocol and execution. This is a proposed study design, not a completed implementation or a pipeline already validated by the ten papers.

## The proposed research in one paragraph

Study whether safety alignment trained with image-conditioned evidence is more robust than language-only safety tuning when unsafe intent is carried by text, image text, visual semantics, or their combination, while preserving helpful responses to benign near-neighbors. Use one pinned open-weight VLM, a source-intent split made before generating attack variants, matched training budgets, distinct training arms, fixed and adaptive attacks, benchmark/image-dependence controls, and separate safety, false-refusal, utility, grounding, and cost outcomes. This question is motivated by prior work; it is not itself a finding.

## Reading route

Read in this order to build the argument from evaluation failure, to attack, to alignment options, to the end-to-end proposal. For each paper, check the exact sections and tables listed under its entry. No need to read every citation in each reference list on the first pass; do read each main method, experimental setup, main results, limitation/discussion, and any appendix that defines its scoring or attack procedure.

| Order | Paper | Read and inspect | What you should be able to explain |
|---|---|---|---|
| 1 | FigStep | §§4–6.5; Figs. 1–2; Tables 1–2; App. A, C, D | Why an image-carried instruction can bypass text-only alignment; exact benchmark, attack construction, and success rule. |
| 2 | VLSBench | §§2–4; Fig. 1; Tables 1–6; appendices defining construction/judges | Visual safety information leakage, why it invalidates some tests, and why warning/refusal and image-dependence must be separated. |
| 3 | USB | benchmark construction and taxonomy; modality definitions; Tables 1–3; judge/metric appendix | How a broad risk taxonomy is crossed with modality conditions, and why safety and benign over-refusal are joint outcomes. |
| 4 | PolyJailbreak | threat model; strategy primitives and algorithm; evaluation setup; Table VI; ablations | How an adaptive black-box attack differs from fixed FigStep, its model set and budget, and why ASR and harmfulness score are distinct. |
| 5 | VLGuard | §3; §4; Table 2; Figs. 2–3; Appendix C.4 and helpfulness results | How a small multimodal safety dataset is turned into an SFT baseline, and the safety/helpfulness trade-off. |
| 6 | SPA-VL | dataset construction; §3.1; §4.1–4.2; Table 1–3; Fig. 3; App. D and G | What a preference record contains, what DPO/PPO do, the evaluated datasets, and an important taxonomy-count inconsistency. |
| 7 | ADPO | §§3–4.4; Figs. 1–3; Tables 1–2; App. A–B | How adversarial image/latent perturbations enter preference training, and which robustness gains trade off with utility/compute. |
| 8 | HoliSafe / Safe-VLM | §§2.1–2.2; §3; §§4.1–4.5; Tables 1–5 and 7; App. B, C.1–C.3 | The five image/text safety states, benchmark construction, visual guard, judge variation, and overlap with our proposal. |
| 9 | DAVSP | §§3–5.6; Figs. 1–2; Tables 1–6; supplement | How a trainable visual safety prompt is optimized while the base VLM is frozen, its measured resistance, and capability costs. |
| 10 | Pragma-VL | §§3–4; Figs. 1–4; Tables 1–4; appendices on data/reward/evaluation | How its staged risk-aware alignment and context-aware reward arbitration work, and how it reports safety/helpfulness/capability. |

## Paper-by-paper audit

### 1. FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts

**Citation:** Y. Gong et al., “FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts,” arXiv:2311.05608, version 3, 2025. [Paper](https://arxiv.org/abs/2311.05608).

- **Role in the field:** early, simple, black-box visual-text jailbreak and a useful fixed baseline. It is an attack plus its SafeBench evaluation set, not a safety-alignment training method.
- **Method/protocol:** paraphrase a prohibited request as a list-like instruction, render it as text in an image, then pair it with benign incitement text. The attacker has query access only; the paper uses one-turn queries. SafeBench has 500 manually reviewed questions across ten topics; SafeBench-Tiny samples five per topic (50 total). Paper experiments include six open-weight VLMs and separate closed-model case studies.
- **Results to know:** Table 1 reports mean ASR **82.50%** for FigStep versus **44.80%** for direct/vanilla harmful text across the paper’s six-model evaluation. These are historical checkpoints and the paper’s own prompt/judge/protocol, not a forecast for current VLMs. The later small-set numbers are from a different subset and must not be swapped into this comparison.
- **Interpretation and limitation:** demonstrates the visual-text pathway is not covered by language-only refusal. The result does not isolate OCR capability from policy behavior unless paired with image ablation and benign OCR controls; it also does not test current models or adaptive attackers.
- **Use in our pipeline:** fixed typography attack tier; matched text-only control, benign OCR cases, held-out rendering styles, and an image-removal/decoy control.
- **Read:** §§4–6.5, especially §5.2 and §6.1–6.4; inspect Fig. 1 (concept) and Fig. 2 (construction), Table 1 (main ASR comparison), Table 2 (ablation of design choices on SafeBench-Tiny), and App. C/D (SafeBench and setup). Figure 1 is an explanatory overview; Figure 2 is the more useful attack-method diagram.
**Paper audit: three questions and answers**

1. **Question:** Why can an image-carried instruction bypass text-only alignment, and what benchmark and success rule does FigStep use?
   **Answer:** The harmful instruction is rendered into image typography, so it reaches the model through the visual pathway rather than only through the text channel. SafeBench contains 500 manually reviewed questions across ten topics; SafeBench-Tiny is a 50-question subset. The paper's success rule tries each question five times and counts it successful if any attempt succeeds. This is a fixed attack and a paper-specific evaluation, not a universal rate.
2. **Question:** What is FigStep’s threat model, and what are its three construction stages?
   **Answer:** It assumes black-box, one-turn access: the attacker can submit inputs and observe outputs but does not use model weights or gradients. The stages are (1) paraphrase the unsafe request as a list-like instruction, (2) render that instruction as text in an image, and (3) pair the image with neutral/inciting text.
3. **Question:** What does Table 1’s 82.50% versus 44.80% comparison establish, and what does it not establish?
   **Answer:** These are the paper's mean ASRs for FigStep image typography versus direct/vanilla harmful text across six open models under its own protocol. The comparison supports the claim that image-carried text can expose a safety weakness. It does not establish a current-model ASR, isolate OCR as the only cause without image-dependence controls, or compare FigStep with adaptive attacks.

### 2. VLSBench: Unveiling Visual Leakage in Multimodal Safety

**Citation:** X. Hu, D. Liu, H. Li, X. Huang, and J. Shao, “VLSBench: Unveiling Visual Leakage in Multimodal Safety,” in *Proc. ACL*, 2025, pp. 8285–8316, doi: 10.18653/v1/2025.acl-long.405. [Paper](https://aclanthology.org/2025.acl-long.405/).

- **Role in the field:** evaluation-validity paper and benchmark. Its central issue is visual safety information leakage (VSIL): the text may disclose the unsafe intent so the model can answer without using the image.
- **Data/protocol:** 2,241 image-text samples and 1,957 images, organized into six categories and 19 subcategories. Evaluates a range of MLLMs and compares textual and multimodal safety alignment. GPT-4o is used for model-response assessment in the paper’s protocol; follow the paper’s prompts and sample conditions when reproducing.
- **Results to know:** Table 4 reports LLaVA-1.5-7B **total safety rate** (refusal + warning) of 21.26% after multimodal SFT, 27.01% after multimodal DPO, 13.99% after textual SFT, and 13.99% after textual DPO. Table 4’s component columns are Refusal, Warning, Total. These are safety rates, **not ASR**; higher total means more safe/warning responses under this rubric. Figure 1 is the visual-leakage motivation, not the source of these alignment values.
- **Interpretation and limitation:** the work argues that textual alignment can look stronger on leaky tests than on tests requiring visual evidence. A high “safety rate” can include warning responses as well as outright refusal, so it is not equivalent to a strict refusal rate or attack success rate.
- **Use in our pipeline:** require image-dependence controls: original image, removed/masked image, and matched decoy where valid; stratify image-essential vs text-leaking cases.
- **Read:** §§2–4 and the table/figure captions; Fig. 1; Tables 1–6, especially Table 4 for alignment comparison and the image/text controls. Use the paper’s actual figure numbering, not the later safety-prompt Figure 7.
**Paper audit: three questions and answers**

1. **Question:** What is visual safety information leakage (VSIL), and why can it invalidate a multimodal safety test?
   **Answer:** VSIL occurs when the text prompt itself discloses the safety-relevant harmful intent. A model may then refuse from text alone, even if it ignores the image, making the test appear to demonstrate visual safety when it does not establish image-conditioned safety.
2. **Question:** What does image ablation test, and what can it not prove on its own?
   **Answer:** Comparing the original image with a removed/masked image or a carefully matched decoy tests whether the response changes when visual evidence is removed. It is an image-dependence/attribution control; by itself it does not prove causality, since the manipulation may change more than the relevant evidence.
3. **Question:** Why are Table 4’s 21.26% and 27.01% not ASR values?
   **Answer:** They are total safety rates (refusal plus warning) for multimodal SFT and DPO on LLaVA-1.5-7B; the textual SFT/DPO entries are 13.99% each. The paper counts warnings as safe under that rubric. These rates therefore cannot be read as attack success or refusal-only rates.

### 3. USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models

**Citation:** B. Zheng et al., “USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models,” in *Proc. ACL*, 2026, pp. 21184–21211, doi: 10.18653/v1/2026.acl-long.970. [Paper](https://aclanthology.org/2026.acl-long.970/).

- **Role in the field:** broad evaluation framework that measures both vulnerability and over-refusal; it is not an alignment method or one attack algorithm.
- **Data/protocol:** the paper crosses 61 risk categories with four image/text risk states (RIRT, RIST, SIRT, SIST), yielding 244 risk-modality intersections. It reports USB-Base (13,175 samples) and USB-Hard (3,785); evaluates 22 MLLMs. Keep the paper’s definitions of the four abbreviations and of benign control subsets beside any reused results.
- **Results to know:** in Table 2, the paper's exact model label is **Claude-Sonnet4**, reported at SR **91.16%** and RR **18.30% ± 0.75**. The authors define SR on harmful inputs as the rate of safe responses and RR on harmless inputs as the rate of refusals (benign over-refusal). Thus higher SR and lower **benign-input RR** are desirable together. Table 1 also has dataset/difficulty results; do not quote those as the model leaderboard or reverse the metric direction without checking the table caption.
- **Interpretation and limitation:** USB’s contribution is coverage and joint diagnosis, not proof that one score summarizes alignment. Its MLLM scope is broader than a VLM-only study; select the relevant image/text slices and preserve per-stratum results.
- **Use in our pipeline:** benchmark strata and safe-input controls; report ASR/safety and benign RR separately by risk-modality cell.
- **Read:** dataset construction/taxonomy and modality definitions; Figures 2–3; Tables 1–3; judge and scoring appendix. Figure 1 in this paper is not an over-refusal-versus-safety plot; rely on the correct caption.
**Paper audit: three questions and answers**

1. **Question:** How does USB structure its risk/modality coverage, and what is the difference between dataset difficulty and a model safety result?
   **Answer:** USB crosses 61 risk categories with four image/text risk states: RIRT (risky image/risky text), RIST (risky image/safe text), SIRT (safe image/risky text), and SIST (safe image/safe text), yielding 244 intersections. USB-Base has 13,175 samples and USB-Hard 3,785. Table 1's dataset/difficulty analysis characterizes evaluation resources; it is not the model leaderboard. Table 2 reports model outcomes.
2. **Question:** What do Safety Rate (SR) and Refusal Rate (RR) measure, and on which inputs is RR calculated?
   **Answer:** SR measures safe responses to harmful inputs. RR measures refusals on harmless inputs, so it is a benign-input over-refusal measure. In Table 2, the exact model label Claude-Sonnet4 has SR 91.16% and RR 18.30% ± 0.75.
3. **Question:** Why is low RR not sufficient evidence of alignment?
   **Answer:** A low benign-input RR means fewer safe requests are incorrectly refused, but says nothing by itself about harmful requests. A model could have low RR while complying with harmful inputs. Read benign-input RR alongside harmful-input SR and preserve results by risk/modality stratum; higher SR and lower benign-input RR are jointly desirable.

### 4. PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs

**Citation:** X. Wang, B. Li, Z. Shao, A. Liu, and S. Ji, “PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs,” arXiv:2510.17277, 2025. [Paper](https://arxiv.org/abs/2510.17277). Check the arXiv version against the final bibliographic record before a formal reference-list freeze.

- **Role in the field:** adaptive black-box attack. It is a red-team method, not a benchmark or defensive alignment method.
- **Method/protocol:** builds reusable atomic cross-modal strategy primitives, then uses a multi-agent/reinforcement-learning loop to adapt prompts and images against a target. Table VI tests eight targets: four closed (GPT-4o, GPT-4.1, Gemini-2.5-Flash 0520, Claude-3.7-Sonnet 20250219) and four open (LLaVA-1.5-7B, LLaVA-1.6-7B, Llama-3.2-Vision-11B, Qwen2.5-VL-7B). The paper states a maximum **15 optimization steps**; do not relabel that as a total-call budget unless counting all attack-agent, judge, and image-generation calls separately.
- **Results to know:** Table VI reports average ASR **83.34%** and harmfulness score **3.976/5** for PolyJailbreak over its eight-model testbed. It uses a GPT-4o harmfulness judge; ASR and severity score are separate outcomes. This is the paper’s experiment, not a directly comparable result to FigStep’s six-model average.
- **Interpretation and limitation:** its adaptive attacker is more expensive and more model-dependent than fixed attacks. The reported optimization budget is not a common apples-to-apples query count across APIs and auxiliary agents; preserve target calls and total pipeline calls in our own logs.
- **Use in our pipeline:** separate adaptive red-team tier with equal target-call cap across training arms, success-vs-query curves, frozen target versions, and disclosed auxiliary model/API costs.
- **Read:** threat model, method/algorithm and atomic strategy primitives, experiment setup, Table VI, query/optimization budget, judge description, and ablations. Figure 6 is the adaptive workflow; Figure 7 is the cumulative-ASR optimization curve.
**Paper audit: three questions and answers**

1. **Question:** How does PolyJailbreak’s adaptive black-box loop differ from fixed FigStep?
   **Answer:** FigStep applies a fixed rendering recipe. PolyJailbreak profiles a target, selects and combines reusable text/image/prompt-amplification strategies, observes target and judge feedback, then iteratively updates its strategy through a multi-agent/RL-based loop. It is an adaptive attacker, not a defense.
2. **Question:** What target set and optimization budget does the paper report, and why is that not the same as a total API-call budget?
   **Answer:** Table VI tests eight targets: GPT-4o, GPT-4.1, Gemini-2.5-Flash 0520, Claude-3.7-Sonnet 20250219, LLaVA-1.5-7B, LLaVA-1.6-7B, Llama-3.2-Vision-11B, and Qwen2.5-VL-7B. The paper states at most 15 optimization steps. That is not automatically the total number of target, attack-agent, judge, or image-generation calls; those must be counted separately in a new experiment.
3. **Question:** How should Table VI’s ASR and harmfulness score be interpreted?
   **Answer:** Table VI reports average ASR 83.34% and harmfulness score 3.976/5 over its eight-model testbed, using a GPT-4o harmfulness judge. ASR measures the fraction of prompts judged successful/harmful; the 0–5 score measures severity. They are distinct outcomes and should not be collapsed or compared directly with FigStep's six-model mean.

### 5. VLGuard: Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models

**Citation:** Y. Zong, O. Bohdal, T. Yu, Y. Yang, and T. Hospedales, “Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models,” in *Proc. ICML*, PMLR, vol. 235, 2024, pp. 62867–62891. [Paper](https://arxiv.org/abs/2402.02207).

- **Role in the field:** multimodal safety data plus SFT baseline. It is an important low-cost alignment precedent, not an adaptive attack.
- **Data/method:** 2,000 training images (977 harmful, 1,023 safe), about 3,000 image-instruction-response pairs; 1,000 test images divided into Safe-Safe, Safe-Unsafe, and Unsafe conditions. The study compares post-hoc and mixed fine-tuning and emphasizes adding ordinary helpfulness data to avoid exaggerated safety.
- **Results to know:** Table 2, LLaVA-v1.5-7B baseline row: AdvBench vanilla 6.45% ASR, suffix 78.27%; XSTest unsafe 26.50%, safe 91.20%; VLGuard Safe-Safe 90.40%, Safe-Unsafe 18.82%, Unsafe 87.46%; FigStep 72.62%. The Post-hoc row reports 0.00, 13.08, 6.00, 80.80, 0.00, 18.96, 0.90, and 0.23 in those same ordered columns. The arrows in the table indicate intended direction: ASRs/unsafe conditions down, safe/helpfulness conditions up. Do not conflate the benign refusal/accuracy columns with attack rates.
- **Interpretation and limitation:** safety fine-tuning sharply lowers several unsafe-condition scores, but the safe-condition column can collapse in some variants; the paper’s central point is the safety/helpfulness balance. Its attack suite mixes text and image tests and is not a contemporary adaptive-attack audit.
- **Use in our pipeline:** minimum multimodal SFT baseline, paired with a matched helpfulness mixture; reproduce the same base checkpoint and report safe-neighbor performance.
- **Read:** §3 data construction and split; §4 and Table 2; Figure 3; Appendix C.4 and helpfulness results. Figure 1’s motivation is useful in a presentation; Table 2 is the essential quantitative evidence.
**Paper audit: three questions and answers**

1. **Question:** What data and tuning comparison make VLGuard a useful multimodal SFT baseline?
   **Answer:** VLGuard constructs about 3,000 image-instruction-response pairs from 2,000 training images (977 harmful, 1,023 safe), and evaluates on 1,000 test images across Safe-Safe, Safe-Unsafe, and Unsafe conditions. It compares post-hoc and mixed fine-tuning and emphasizes adding ordinary helpfulness data to reduce exaggerated safety.
2. **Question:** How should the main Table 2 columns be read, and why is low harmful ASR alone insufficient?
   **Answer:** AdvBench Vanilla/Suffix, XSTest Unsafe, VLGuard Safe-Unsafe, VLGuard Unsafe, and FigStep are harmfulness/attack-rate columns where lower is safer. XSTest Safe and VLGuard Safe-Safe are benign/helpfulness indicators where higher is better. The baseline LLaVA-v1.5-7B FigStep ASR is 72.62%; post-hoc tuning reports 0.23%. That reduction alone does not establish good overall behavior if safe requests are refused or helpfulness falls.
3. **Question:** What does the safe/helpfulness data mixture contribute to the result?
   **Answer:** The paper's key claim is that safety tuning can reduce harmful responses, while mixing in ordinary helpfulness data can limit exaggerated safety and preserve performance on benign requests. Utility and safety must be read together, including the benign columns and the paper's separate response-quality/VQA evaluation.

### 6. SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision Language Models

**Citation:** Y. Zhang et al., “SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision Language Models,” in *Proc. IEEE/CVF CVPR*, 2025, pp. 19867–19878. [Paper](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision_Language_CVPR_2025_paper.html) | [arXiv:2406.12030](https://arxiv.org/abs/2406.12030).

- **Role in the field:** preference dataset and alignment experiments. The paper evaluates DPO and PPO; **DPO is the training objective/algorithm, not the dataset**. In plain language, DPO updates a policy to prefer the chosen answer over the rejected answer relative to a reference policy, without requiring a separately trained reward model in the basic formulation.
- **Data/method:** each preference record is `(question, image, chosen response, rejected response)`. The paper reports 100,788 samples, from 12 open- and closed-source response models. The split is 93,258 train, 7,000 validation, 265 HarmEval, 265 HelpEval. Important audit note: the abstract says 6 domains/13 categories/53 subcategories, while §3.1 says 6 primary domains/15 secondary categories/53 tertiary categories. Cite the counts with this discrepancy disclosed or use the consistent 6-domain/53-subcategory description until clarified from the camera-ready source.
- **Results to know:** Table 2 reports LLaVA+SPA-VL-DPO MM-SafetyBench ASR of 0.00 (text-only), 0.60 (SD), 0.60 (Typo), 1.19 (SD+Typo), 0.60 average; AdvBench vanilla/suffix 0.00/0.00; HarmEval USR/score 0/0. The table’s SPA-VL-PPO row is 0.60/0/0/1.19/0.45; 0.19/2.12; 0/0. These are percentages/scores according to separate column definitions; HarmEval columns must be read with their actual header and denominator. The paper reports these trained LLaVA models against its own baseline suite, not as a direct comparison to ADPO or HoliSafe.
- **Interpretation and limitation:** demonstrates multimodal preference data can support DPO/PPO and evaluates safety plus helpfulness. Its training recipe, preference generation and split/source overlap need auditing before reusing it; table results do not establish generalization to a held-out adaptive attacker.
- **Use in our pipeline:** preference-data provenance and standard DPO comparator; ensure no test-intent overlap and document the chosen/rejected construction.
- **Read:** dataset construction and §3.1; §4.1–4.2 and Table 2; Figure 3 for data scaling; Appendix D/G for recipes, preference quality, and examples. Figure 1 is a high-level illustration; use the actual record example to explain what preference data looks like.
**Paper audit: three questions and answers**

1. **Question:** What is one SPA-VL preference record, and what do “chosen” and “rejected” mean?
   **Answer:** A record is `(question, image, chosen response, rejected response)`: two responses to the same visual question are paired, with the preferred safer/more helpful response labeled chosen and the less-preferred response labeled rejected. The dataset reports 100,788 samples from 12 response models, split into 93,258 train, 7,000 validation, 265 HarmEval, and 265 HelpEval examples.
2. **Question:** How do DPO and PPO differ, and what evidence does Table 2 provide?
   **Answer:** Basic DPO updates a policy to prefer chosen over rejected relative to a reference policy, without a separately trained reward model. PPO is an on-policy policy-optimization method using a reward signal/model; it is not another name for SPA-VL. Table 2 evaluates trained models on MM-SafetyBench, AdvBench, and HarmEval. Each column has its own metric and denominator, so report its entries by column rather than combining them into one score.
3. **Question:** What is the paper’s category-count inconsistency, and how should it be reported?
   **Answer:** The abstract says 6 domains, 13 categories, and 53 subcategories; §3.1 says 6 primary domains, 15 secondary categories, and 53 tertiary categories. State the mismatch explicitly rather than silently choosing 13 or 15; both descriptions agree on six top-level domains and 53 lowest-level categories.

### 7. Adversary-Aware DPO: Enhancing Safety Alignment in Vision Language Models via Adversarial Training

**Citation:** F. Weng et al., “Adversary-Aware DPO: Enhancing Safety Alignment in Vision Language Models via Adversarial Training,” in *Findings of EMNLP*, 2025, pp. 13644–13657, doi: 10.18653/v1/2025.findings-emnlp.735. [Paper](https://aclanthology.org/2025.findings-emnlp.735/).

- **Role in the field:** direct precedent for adversarially robust multimodal preference alignment. This means we should position any proposal as controlled replication/extension/transfer study, not as the first adversarial VLM alignment method.
- **Method/data:** constructs 200 harmful image-text training pairs (80 HarmBench-mm, 40 HarmBench-AT text prompts with blank images, 80 typographic/Stable-Diffusion images based on HarmBench-AT); safe response preferences are trained with an adversarial reference model and an adversary-aware DPO loss, using image-space or latent perturbations. It also samples 500 LLaVA-Instruct-150K examples for utility alignment. Tests five model families using LoRA.
- **Results to know:** Table 1, LLaVA-1.5-7B attack ASRs in column order VisualAdv / MMPGDBlank / MultiTrust typographic / multimodal / crossmodal: base **64.5/84.0/22.2/55.1/42.0**; standard DPO **12.0/33.0/0.7/8.8/9.6**; ADPO **5.0/0.5/0.0/0.0/0.2**. Utility on MMStar/OCRBench/MM-Vet/LLaVA-Bench: base **32.7/202/29.9/59.5**; DPO **33.9/198/28.9/54.4**; ADPO **33.7/184/24.2/48.2**. Lower attack ASR is better; utility scores are not one shared unit and some decrease under ADPO. Table 2 compares training time per iteration; inspect it before making any efficiency claim.
- **Interpretation and limitation:** the results are strong on the evaluated attacks, including white-box optimized-image attacks, but utility shifts and training cost are material. Robustness on those attacks does not by itself prove transfer to held-out attack generation or modern API models.
- **Use in our pipeline:** adversarial-preference comparator and training-attack precedent; reserve independent attack families/templates for test, and count perturbation optimization/compute.
- **Read:** §§3–4.4; Fig. 2 method, Fig. 3 safety-utility tradeoff, Table 1, Table 2, Appendix A–B. Figure 1 is the motivating comparison; Figure 2 explains the training method.
**Paper audit: three questions and answers**

1. **Question:** What is the difference among AR-DPO, AT-DPO, and ADPO?
   **Answer:** AR-DPO uses the adversarially trained reference model without the adversary-aware DPO loss. AT-DPO uses the adversary-aware loss with an ordinary reference model. ADPO combines both components.
2. **Question:** What safety result does Table 1 report, and what should be said about utility?
   **Answer:** On LLaVA-1.5-7B, Table 1 reports lower ASR for ADPO than standard DPO across the listed attacks. Utility is not uniformly unchanged: for example, MM-Vet is 24.2 for ADPO versus 29.9 for the base model, and OCRBench is 184 versus 202. These are separate task-specific metrics, not one shared utility scale.
3. **Question:** What does the paper establish about robustness and cost, and what remains unestablished?
   **Answer:** It supports improved robustness on the attacks tested, including optimized-image attacks, while showing utility trade-offs; Table 2 gives training-time-per-iteration comparisons that must be interpreted with hardware and setup. It does not establish free, universal, or held-out adaptive-attack robustness. A new study should reserve independent test attacks and account for perturbation optimization and compute.

### 8. HoliSafe / Safe-VLM: Holistic Safety Benchmarking and Modeling with Safety Meta Token for Vision-Language Model

**Citation:** Y. Lee et al., “HoliSafe: Holistic Safety Benchmarking and Modeling with Safety Meta Token for Vision-Language Model,” in *Proc. IEEE/CVF CVPR Findings*, 2026, pp. 5989–5998. [CVPR paper](https://openaccess.thecvf.com/content/CVPR2026/html/Lee_HoliSafe_Holistic_Safety_Benchmarking_and_Modeling_with_Safety_Meta_Token_for_Vision-Language_Model_CVPR_2026_paper.html) | [arXiv:2506.04704](https://arxiv.org/abs/2506.04704).

- **Role in the field:** both safety data/benchmark and an integrated visual safety architecture. This is close prior art for several parts of our intended pipeline.
- **Data/method:** 14,246 image-instruction-response pairs; 10,215 train examples and 4,031 HoliSafe-Bench questions on 1,796 images; seven high-level categories and 18 subcategories. Its five cases are unsafe image/unsafe text, unsafe image/safe text, safe image/unsafe text, safe image + safe text leading to unsafe output, and safe image + safe text leading to safe output. Safe-VLM uses a learnable safety meta token and safety head / Visual Guard Module (VGM) to classify image harmfulness while the model generates a response; training combines classification and next-token objectives. The paper evaluates 21 VLMs.
- **Results to know:** Table 3 is the benchmark’s ASR table, with four unsafe-condition rates, mASR, and benign refusal rate (RR); judge columns differ. In the revised arXiv version, Safe-LLaVA-7B’s Table 3 row is **8.8% mASR / 1.3% RR under Claude-3.5-Sonnet; 15.3% mASR under GPT-4o; 15.8% under Gemini-2.0; 15.4% under string matching**. These are judge-dependent cells; check the camera-ready table/version before formal use. Do not substitute the 12.3% result from another model/table. The paper’s Table 7 ablation reports (2-layer VGM, hidden ratio 0.5) 15.4 mASR and 0.3% string-match RR; adding non-refusal data moves the tradeoff from 10.4/1.0 at 0 data, to 15.4/0.3 at 10K, to 19.2/0.1 at 15K. These are specifically ablation cells, not the Table 3 headline.
- **Interpretation and limitation:** the five-state framing is not a novel contribution for our proposal if we adopt it; cite HoliSafe and say we will use/adapt its coverage. Judge choice changes measured ASR; safe refusal and harm rates must be reported together. The paper’s data includes images curated from training sets of prior datasets, so overlap checks are essential for any combined evaluation.
- **Use in our pipeline:** coverage template and one possible method comparator; compare its guard only if checkpoint/code/data and compute are feasible. Do not stack it with all other methods by default.
- **Read:** §§2.1–2.2 and Tables 1–2; §3/Fig. 2 for safety-token/VGM architecture; §§4.1–4.5 and Tables 3–5; Table 7 ablation; Appendix B/C.1–C.3 for training and judges. Table 3 is not interchangeable with Table 7.
**Paper audit: three questions and answers**

1. **Question:** What are HoliSafe’s five image/text safety cases, and which are benign-safe versus compositional-risk?
   **Answer:** The cases are unsafe image + unsafe text; unsafe image + safe text; safe image + unsafe text; safe image + safe text that nevertheless leads to unsafe output; and safe image + safe text leading to safe output. The last is the benign-safe control. The safe-image/safe-text → unsafe-output case is compositional risk, not a benign control, and should be handled safely.
2. **Question:** What does Safe-VLM add, and how does its benchmark organize evidence?
   **Answer:** Safe-VLM uses a learnable safety meta token and safety head/Visual Guard Module to classify image harmfulness while generating a response, combining classification and next-token objectives. HoliSafe provides 14,246 image-instruction-response pairs and a 4,031-question benchmark over five cases. Table 3 reports judge-dependent rates across unsafe cases, mASR, and benign refusal rate.
3. **Question:** How should a Table 3 mASR result be cited and interpreted?
   **Answer:** State the model, judge, metric, and paper version because judge choice changes the result. In the cited revised arXiv version, Safe-LLaVA-7B reports 8.8% mASR/1.3% RR under Claude-3.5-Sonnet and 15.3% mASR under GPT-4o. These are Table 3 headline cells; do not substitute the separate Table 7 ablation values or omit the judge.

### 9. DAVSP: Safety Alignment for Large Vision-Language Models via Deep Aligned Visual Safety Prompt

**Citation:** Y. Zhang, J. Li, L. Cai, and G. Li, “DAVSP: Safety Alignment for Large Vision-Language Models via Deep Aligned Visual Safety Prompt,” in *Proc. AAAI*, vol. 40, no. 44, 2026, pp. 38111–38119, doi: 10.1609/aaai.v40i44.41149. [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/41149) | [arXiv:2506.09353](https://arxiv.org/abs/2506.09353).

- **Role in the field:** visual-input-side alignment/defense comparator, not a preference-data method. It optimizes a trainable visual safety prompt and activation-level alignment while leaving the base LVLM frozen, then applies a padding/border prompt at inference with a textual safety prompt.
- **Method/protocol:** tested on LLaVA-1.5-13B and Qwen2-VL-7B-Instruct. Evaluation includes MM-SafetyBench (in-distribution), FigStep (out-of-distribution), and utility measures including MM-Vet, MME, and LLaVA-Bench; the paper reports Resist Success Rate (RSR), not ASR. It uses its own image/prompt construction and result protocol.
- **Results to know:** Table 2 reports DAVSP RSR on FigStep of **84.20%** for LLaVA-1.5-13B and **99.20%** for Qwen2-VL-7B-Instruct. On MM-SafetyBench SD+TYPO, the values are **98.72%** and **99.12%**. Table 3/ablation evidence shows for LLaVA that removing Deep Alignment drops FigStep RSR from 84.20% to 67.00%; removing the visual safety prompt gives 76.20%. Table 1 reports capability measures; do not label Table 2’s RSR as attack success rate. High RSR is better under the paper’s definition.
- **Interpretation and limitation:** the results show strong resistance under these test conditions, not universal robustness. Report utility too: on LLaVA, the DAVSP row in the capability table reports MM-Vet 63.6, MME total 1602, and LLaVA-Bench 63.6; those values are comparable only within the same evaluation setup. Transferability to another processor, resolution, or model must be tested.
- **Use in our pipeline:** a distinct inference-time visual-prompt comparator if implementation and training artifacts are available; evaluate it as its own arm and measure latency/utility.
- **Read:** §§3–4 for prompt/activation method and deployment; §5.1–5.6; Figs. 1–2; Tables 1–6 and supplement. Figure 2 is the method overview; Table 2 is the RSR evidence; the ablation table explains which components drive it.
**Paper audit: three questions and answers**

1. **Question:** What does DAVSP change, and how does that distinguish it from full-model SFT/DPO?
   **Answer:** It freezes the LVLM weights and optimizes a trainable visual safety prompt/padding using activation-space alignment and output supervision. At inference, the visual border prompt is applied with a textual safety prompt. The intervention is on the visual input/prompt path, not a full-model weight update.
2. **Question:** What are RSR and ASR, and which direction is favorable?
   **Answer:** RSR is the proportion of malicious queries the model successfully resists (higher is better); ASR is the proportion of attacks that succeed (lower is better). They are complements only if the examples and success rubric match, so do not assume cross-paper values sum to 100%.
3. **Question:** What do the reported results show, and what are their limits for our pipeline?
   **Answer:** Table 2 reports FigStep RSR of 84.20% for LLaVA-1.5-13B and 99.20% for Qwen2-VL-7B-Instruct; on MM-SafetyBench SD+TYPO it reports 98.72% and 99.12%. These show resistance under the paper's protocol, not universal robustness. Compare capability, latency, and deployment costs, and test transfer across processors, resolutions, and attack variants.

### 10. Pragma-VL: Towards a Pragmatic Arbitration of Safety and Helpfulness in MLLMs

**Citation:** M. Wen, K. Yang, X. Chen, J. Zhang, D. Han, S. Cui, and Y. Xu, “Pragma-VL: Towards a Pragmatic Arbitration of Safety and Helpfulness in MLLMs,” in *Proc. ICLR*, 2026. [ICLR paper](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4054556fcaa934b0bf76da52cf4f92cb-Abstract-Conference.html) | [arXiv:2603.13292](https://arxiv.org/abs/2603.13292).

- **Role in the field:** recent training-time safety/helpfulness arbitration method. It is not an attack and not merely a safety dataset.
- **Method/protocol:** two-stage design: a risk-aware visual pre-alignment/cold-start stage with risk descriptions and normal samples, then a context-aware reward process that separately represents helpfulness and harmlessness and uses risk-dependent arbitration to optimize the policy with GRPO. Evaluated on Qwen2.5-VL-7B and LLaVA-1.5-7B. Table 2 includes BeaverTails-V, SPA-VL, MM-SafetyBench, SIUO, and MSSBench; Table 3 covers general capability.
- **Results to know:** Table 2, Qwen2.5-VL-7B Pragma-VL: BeaverTails-V Help/Harmless win rates **62.65/67.91%**; SPA-VL Help/Harmless **87.17/87.92%**; MM-SafetyBench ASR **31.66%**; SIUO effective/safety **95.21/63.47%**; MSSBench effective/safety **99.66/55.89%**. The base Qwen row gives MM-SafetyBench ASR 48.75%, SIUO effective/safety 92.17/38.78%, MSSBench effective/safety 98.48/36.53%. Table 3 Pragma Qwen results include VQAv2 84.20% (base 83.60%) and MathVista 67.20% (base 67.80%). These are task-specific results from the paper’s own training/test setup, not a cross-paper leaderboard.
- **Interpretation and limitation:** improvements in safety/helpfulness benchmarks do not mean every capability metric rises; see Table 3. It is a substantial multi-stage training pipeline, so data access, training compute, reward/judge construction, and recipe fidelity are feasibility gates. Do not use unsupported claims about reward variance/instability as a limitation.
- **Use in our pipeline:** strongest recent training-method comparator among this selected set if feasible; otherwise it informs the design rationale without becoming a required baseline. Do not combine it with ADPO, HoliSafe, and DAVSP as one compound intervention.
- **Read:** method sections and Figs. 1–4; Table 2 (safety/helpfulness), Table 3 (general ability), Table 4 (ablation); appendices for datasets, reward construction, and evaluation details. Figure 2 gives the overall framework; Figure 3/algorithm details help explain the training stages.
**Paper audit: three questions and answers**

1. **Question:** What are Pragma-VL’s two stages, and how does context-dependent reward arbitration work?
   **Answer:** Stage 1 performs risk-aware visual pre-alignment/cold start with risk descriptions and normal examples. Stage 2 represents helpfulness and harmlessness separately, uses query-dependent weights to arbitrate which should dominate in context, and optimizes the policy with GRPO. The reported training used 16 A100 GPUs, a material feasibility constraint.
2. **Question:** How should the distinct Table 2 metric families be read?
   **Answer:** BeaverTails-V and SPA-VL Help/Harmless columns are judge-based win rates; MM-SafetyBench reports ASR (lower is better); SIUO and MSSBench report Effective and Safety rates (higher is better, with effectiveness penalizing blanket refusals). They are separate measures, not one aggregate score.
3. **Question:** What do the results and capability evaluation establish, and what do they not establish?
   **Answer:** On Qwen2.5-VL-7B, Pragma-VL reports task-specific safety/helpfulness and capability results under its own setup; for example, Table 2 reports MM-SafetyBench ASR 31.66%, and Table 3 reports VQAv2 84.20% and MathVista 67.20%. Table 3 must be read with task-native metrics, and not every capability improves. These results do not form a cross-paper leaderboard or remove feasibility concerns around data, reward construction, compute, and recipe fidelity.

## Evidence comparison: only compare within the original paper

| Paper | Primary evidence to cite | Metric / direction | Why it is not directly comparable across papers |
|---|---|---|---|
| FigStep | Table 1: 82.50% FigStep vs 44.80% vanilla mean | ASR, lower is safer | Different historical model set, attack/query and judge protocol. |
| VLSBench | Table 4 LLaVA-1.5-7B: MM-SFT 21.26%; MM-DPO 27.01%; textual SFT/DPO 13.99% total | Refusal + warning safety rate, higher | Warning/refusal mix; leaky-benchmark controls and sample set differ. |
| USB | Table 2 Claude-Sonnet4 SR 91.16%, benign-input RR 18.30% | SR higher; benign-input false refusal lower | Broad risk-modality matrix, distinct scoring and model versions. |
| PolyJailbreak | Table VI average 83.34% ASR, HS 3.976/5 | ASR and harm severity, both lower is safer | Adaptive attack, eight targets, auxiliary agents, distinct call accounting. |
| VLGuard | Table 2 LLaVA baseline and post-hoc columns | ASRs down; safe/helpful condition should remain high | Distinct benchmarks/conditions; column semantics must be retained. |
| SPA-VL | Table 2 LLaVA+SPA-VL-DPO average MM-SafetyBench ASR 0.60%; AdvBench 0/0 | ASR, lower | Own dataset/training and test suite; potential train/evaluation overlap matters. |
| ADPO | Table 1 LLaVA base vs DPO vs ADPO, five safety columns and four utility metrics | ASR lower; individual capability metric higher | White-box attack suite and distinct utility units; compute differs. |
| HoliSafe | Table 3 judge-specific mASR; Table 7 component/data ablation | mASR and RR lower | Judge-dependent; do not substitute an ablation value for main table. |
| DAVSP | Table 2: FigStep RSR 84.20% / 99.20%; SD+TYPO 98.72% / 99.12% | RSR higher is better | Resistance metric, models and prompt deployment differ. |
| Pragma-VL | Table 2 safety/helpfulness rows; Table 3 capability | Several metrics, mixed directions | Win rate, ASR, effective/safety rates, and QA accuracy are not one scale. |

## Synthesis: what these ten papers jointly say

1. **The problem is real and modality-specific.** FigStep and PolyJailbreak show that moving or composing an unsafe request across text/image channels can bypass defenses; HoliSafe formalizes image/text safety combinations.
2. **Evaluation design changes the conclusion.** VLSBench’s leakage analysis means an unsafe intent in visible text can make an image-safety score misleading. USB’s modality/risk matrix and benign refusal reporting argue for disaggregated outcomes, not a single ASR.
3. **Alignment options already exist.** VLGuard provides multimodal safety SFT; SPA-VL supplies preference pairs and compares DPO/PPO; ADPO adds explicit adversarial training; HoliSafe adds an integrated visual safety head; DAVSP optimizes a visual prompt; Pragma-VL learns a safety/helpfulness arbitration. Therefore, a defensible gap is **controlled comparison and held-out transfer under shared data, attack, and evaluation conditions**, not “no one has aligned VLMs” or “we are first to use adversarial alignment.”
4. **A safety score alone is inadequate.** A model may reduce unsafe answers by refusing benign requests. Measure harmful compliance, benign false refusals, safe-answer quality, visual dependence, general capability, and cost separately.
5. **The ten papers do not establish one state-of-the-art winner.** Checkpoint, benchmark, judge, attack access, data overlap, and metric differ. Say “paper-reported result on its own protocol,” not “best VLM safety model” unless a controlled common evaluation supports that claim.

## Final recommended system design

The proposed diagram uses the following flow. It is a **research protocol**, not a method already demonstrated by these papers:

```text
PAPERS / DATA SOURCES
VLGuard + SPA-VL + HoliSafe + USB taxonomy + VLSBench controls
                              |
                              v
CURATE + LABEL
image, text, joint intent, risk class, safe counterpart, source/license
                              |
                              v
SPLIT BY SOURCE INTENT (before rendering, image synthesis, paraphrase, or attack)
train / validation / locked test; deduplicate images, intents, and attack templates
                   /                          \
                  v                            v
         TRAINING ARMS                  LOCKED EVALUATION SET
         B0 native checkpoint            benign and harmful pairs
         B1 text-only safety SFT           fixed: FigStep-style typography
         B2 multimodal safety SFT          adaptive: PolyJailbreak-style
         B3 standard multimodal DPO        benchmark strata: VLSBench/USB/HoliSafe
         B4 ADPO-style (if reproducible)  attribution: image removed/masked/decoy
         B5 ONE feasible comparator               |
                  \                              /
                   v                            v
               SAME PINNED MODEL FAMILY + SHARED INFERENCE SETTINGS
                              |
                              v
                BLIND SCORING + HUMAN AUDIT SAMPLE
                              |
                              v
 harmful compliance / ASR by family | benign false refusal + answer quality
 image dependence / grounding | general capability | latency, calls, compute
                              |
                              v
               PAIRED INTENT-LEVEL ANALYSIS + UNCERTAINTY
```

**Key design choices:**

- The dataset split happens before any derived image or attack rendering; all variants of one source intent stay in one split.
- Training arms are independent. The practical core is native baseline, text-only SFT, multimodal SFT, and standard DPO; add ADPO and one recent comparator only after reproduction/compute checks. Do not stack every paper’s intervention.
- Attack algorithms (FigStep, PolyJailbreak) are separate from benchmark suites (VLSBench, USB, HoliSafe) and from causal controls (image ablation, safe near-neighbors).
- The attack runbook’s proposed budget is not a paper-native setting. In particular, PolyJailbreak’s 15 optimization steps are its paper setting; any extra discovery calls or a shared cap must be called our protocol choice.
- Report stratified outcomes and confidence intervals grouped by source intent; never merge warning rate, refusal rate, safety rate, ASR, RSR, helpfulness win rate, and capability scores into one unlabeled number.

## Short oral-preparation check

Before presenting, make sure you can answer these without reading a slide:

- What is the research question, and what would count as evidence against the hypothesis?
- What is visual safety information leakage, and how does image ablation test it?
- What is the difference between an attack, a benchmark, an alignment dataset, and an alignment method?
- What is a SPA-VL preference pair, and what does DPO optimize?
- Why must harmful compliance and benign false refusal be measured together?
- Which methods are actually in the proposed baseline ladder, and which are optional comparators?
- Why can none of these published headline scores be ranked as a common leaderboard?
- What exact paper/table/version/judge supports every numeric value in the presentation?

## References in topic order

**Attacks and evaluation:** [1] FigStep; [2] VLSBench; [3] USB; [4] PolyJailbreak.  
**Training data and alignment:** [5] VLGuard; [6] SPA-VL; [7] ADPO.  
**Recent model/defense comparators:** [8] HoliSafe; [9] DAVSP; [10] Pragma-VL.

For the complete bibliographic entries, venue/version details, citations, and remaining papers, see [VLM_VERIFIED_PAPER_CHECKLIST.md](VLM_VERIFIED_PAPER_CHECKLIST.md) and [VLM_PAPER_EVIDENCE_DOSSIER.md](VLM_PAPER_EVIDENCE_DOSSIER.md).
