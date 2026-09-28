# Vision-Language Model Safety Alignment: Research Review and Study Proposal

**Prepared:** 2026-09-26
**Purpose:** Establish the VLM safety-alignment landscape independently of the earlier LLM continual-gradient proposal, then derive a tractable research problem, evaluation plan, and presentation structure.

## Executive Summary

VLM safety research is not one method race. Public work spans multimodal safety fine-tuning and preference optimization, adversarially robust alignment, representation and decoding interventions, input-side guardrails, reasoning-based safety, and increasingly diagnostic evaluation benchmarks. Results across papers are not directly rankable because models, attack sets, judges, and utility measures differ.

The most defensible project direction is to study **cross-modal safety calibration and generalization**: can a VLM learn to respond safely to harmful intent expressed through different combinations of image and text, while remaining helpful on closely matched benign cases and robust to attack families withheld during training? This direction is motivated by existing work, but its novelty must be checked against the newest papers and implemented baselines before being claimed. The project should not assume gradient sample selection is suitable or central.

## 1. Scope and Evidence Standard

This review covers public VLM/MLLM work on harmful-content safety and jailbreak robustness, with emphasis on papers and benchmarks available by September 26, 2026. “Alignment” is used here in the operational sense of producing policy-consistent safe/helpful behavior, especially refusing assistance that would facilitate harm. That is narrower than a full account of value alignment, privacy, bias, truthfulness, or deployment governance.

Evidence grades used below:

- **High:** primary paper or official conference page inspected; claim is stated in its abstract or paper text.
- **Medium:** primary paper identified and its headline method is clear, but details such as settings, comparisons, or reported outcomes need a full-paper audit before a formal presentation.
- **Open:** plausible research implication or proposed study design, not an established empirical result.

The field map below is a synthesis based on **where an intervention acts**. It is not a canonical taxonomy, and some methods belong to multiple categories. “SOTA” should mean recent strong work within a specified task and evaluation protocol, not a universal ranking.

## 2. What the Field Is Studying

### 2.1 Training-time safety alignment

| Work | Method and finding | What it establishes / does not establish |
|---|---|---|
| [VLGuard, Zong et al. (2024)](https://arxiv.org/abs/2402.02207) | Curates multimodal safe instruction-following data; reports that safety data can be mixed into VLM instruction tuning or used for post-hoc safety tuning, reducing jailbreak success with limited helpfulness cost. | Shows that the training mixture matters and provides a data/training baseline. It is not an evaluation-only benchmark and does not by itself solve generalization to unseen adaptive attacks. **High** |
| [SafeVLM, Liu et al. (2024)](https://arxiv.org/abs/2405.13581) | Adds a safety projector, safety tokens, and a safety head in a two-stage training design. | Architectural and training intervention aimed at risky visual inputs. Compare on matched data and benchmarks rather than relying on its standalone reported score. **High** |
| [SPA-VL, Zhang et al. (CVPR 2025)](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision_Language_CVPR_2025_paper.html) | Provides a large multimodal preference dataset for safety alignment and studies preference optimization such as DPO/PPO. | Makes preference-based multimodal safety training a central baseline family. Dataset scale does not imply robustness to attack families outside its construction. **High** |
| [Adversary-Aware DPO (ADPO), Weng et al. (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.735/) | Integrates adversarial training into DPO; creates preference pairs under adversarial distortions and an adversarially trained reference model. The paper targets robustness to white-box perturbations and reports improvements in safety and utility over its baselines. | Direct evidence that “adversarially robust VLM alignment” is already an active method line. A new project cannot claim simply to be the first to combine VLM safety alignment with adversarial training. **High** |
| [Think in Safety, Lou et al. (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.261/) | Evaluates 13 multimodal reasoning models across five benchmarks and trains with safety-oriented reasoning data. Reports that safety behavior differs between jailbreak-robustness and safety-awareness benchmarks. | Reasoning models need evaluation beyond standard short-answer VLMs; safety reasoning is a distinct training direction, not a synonym for all VLM alignment. **High** |
| [Gulati & Raval (2026), harmful fine-tuning study](https://arxiv.org/abs/2602.16931) | Studies safety erosion when VLMs are fine-tuned on harmful data and compares multimodal and text-only evaluation. | Relevant to harmful-data fine-tuning, but it is not the same setting as benign task adaptation. Do not use it alone to justify a benign-fine-tuning project. **Medium** |

### 2.2 Representation, decoding, and model-internal defenses

| Work | Intervention | What to take from it |
|---|---|---|
| [CMRM, Liu et al. (Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.186/) | Inference-time cross-modality representation manipulation. The paper attributes safety degradation to a representation gap between multimodal inputs and the text distribution where the LLM backbone learned safety. | Establishes a representation-based explanation and a training-free inference intervention. Its reported reduction on LLaVA-7B is paper-specific, not a common benchmark ranking. **High** |
| [SafetyReminder (AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40607) | Learns soft prompt tokens and injects them during generation to activate safety earlier, motivated by “delayed safety awareness.” | A generation-time intervention with a small learned component; evaluate its inference overhead and response quality as well as refusal. **High** |
| [MMAligner (2026 preprint)](https://arxiv.org/abs/2608.05909) | Calibrates unsafe multimodal representations toward an existing refusal region, with preservation objectives for benign inputs. Its abstract reports a 99% average refusal rate and under 2% utility degradation on its selected evaluations. | Recent and directly relevant. Treat headline values as author-reported and not comparable to other papers without reproducing the common evaluation. It is a strong method to inspect for mechanism, data, and code availability. **Medium** |
| [JRS-Rem (2026 preprint)](https://arxiv.org/abs/2603.17372) | Identifies a jailbreak-related representation shift and removes that shift at inference time. | Further evidence that internal-state interventions remain active; read alongside MMAligner and CMRM rather than treating any one as settled consensus. **Medium** |
| [HiddenDetect (ACL 2025)](https://aclanthology.org/2025.acl-long.724/) | Uses hidden-state patterns to detect multimodal jailbreaks. | Detection is distinct from alignment: it may be a guardrail component, but its output must be evaluated for false alarms and attack transfer. **Medium** |

### 2.3 Input-side guardrails and prompt handling

- [VLMGuard-R1 (2025 preprint)](https://arxiv.org/abs/2504.12661) uses a reasoning-guided rewriter to inspect image-text interactions and rewrite user inputs without changing the target VLM’s parameters. Its paper reports improvements across three benchmarks and five VLMs. It is best categorized as an external input-side defense, not intrinsic parameter alignment. **High**
- Guardrails can be complementary to model training, but comparisons must include their added latency, errors introduced by rewriting, and behavior on safe inputs. The system-level combination should be reported separately from the target model’s intrinsic behavior. **Open recommendation**

### 2.4 Broader evaluation and safety dimensions

The public literature increasingly distinguishes jailbreak resistance from safety awareness, false refusal, contextual safety, visual leakage, and privacy. These are related but not interchangeable outcomes.

## 3. Problem Formulation

### 3.1 General problem

Given a vision-language model with image and text inputs, align its responses so that it:

1. recognizes harmful intent expressed in text, images, or their combination;
2. refuses or safely redirects requests where assistance would facilitate harm;
3. remains helpful on benign requests, including safe cases visually or linguistically similar to harmful ones; and
4. retains this behavior under transformations and adversarial inputs not seen during alignment.

Let an input be \(x=(I,T,C)\), where \(I\) is image content, \(T\) is text, and \(C\) is conversational context. Let \(y\) be the model response. The target is not simply to maximize refusal. It is to minimize unsafe assistance and excessive refusal jointly, subject to preserving useful visual-language capability:

\[
\min_{\theta}\; \lambda_h R_{harm}(\theta) + \lambda_o R_{overrefusal}(\theta)
 + \lambda_u L_{utility}(\theta) + \lambda_a R_{attack}(\theta),
\]

where the terms must be operationalized using held-out data and declared judges. This is a conceptual objective, not a claim that the papers share one common formula.

### 3.2 Recommended research question

**Can safety alignment built from controlled image-text counterfactuals improve cross-modal and held-out jailbreak robustness while preserving helpfulness on matched benign inputs?**

This narrows the broad goal into a testable question. Each underlying scenario would have matched variants in which the harmful or benign intent is conveyed by text, image text, image semantics, or the image-text combination. Training would use only designated attack families; testing would hold out attack families, prompt framings, and semantic intents where feasible.

### 3.3 Why this direction is worth testing

- Existing training methods include safety SFT/preference data (VLGuard, SPA-VL), adversarial preference training (ADPO), and safety reasoning data (Think in Safety).
- Existing defenses include internal representation correction/calibration (CMRM, MMAligner), generation-time soft prompts (SafetyReminder), and input rewriting (VLMGuard-R1).
- Newer evaluations expose weaknesses in a single aggregate attack-success metric: visual leakage (VLSBench), under- versus over-refusal (VSCBench), factor confounding (MMJailBench), naturalistic memes (MemeSafetyBench), and multi-turn context (MTMCS-Bench).
- **Open synthesis:** the project’s defensible contribution would be a controlled alignment/evaluation study of safety transfer across content carriers and held-out attack families, with calibration and utility measured together. Whether no prior work already does this combination must be checked by paper-level review and citation chaining before asserting novelty.

## 4. Research Challenges

| Challenge | Evidence / why it matters | Design implication |
|---|---|---|
| Cross-modal intent composition | SIUO studies cases where individual modalities appear safe but the combination implies an unsafe request. | Use paired or factorial image/text conditions; do not evaluate only text-in-image attacks. |
| Visual leakage in benchmarks | [VLSBench](https://aclanthology.org/2025.acl-long.405/) identifies cases where text already reveals the risky image content, allowing text-only refusal to score as multimodal safety. | Include visual-leakage checks and require that the image actually carries necessary information. |
| Under-refusal versus over-refusal | [VSCBench](https://aclanthology.org/2025.findings-acl.158/) pairs visually/textually similar safe and unsafe cases and finds both failure types. | Report safe-case helpfulness/false-refusal alongside harmful compliance. |
| Attack and prompt confounding | [MMJailBench](https://arxiv.org/abs/2608.25490) factorizes harmful intent, visual semantics, carrier, and framing; it reports substantial model-dependent effects. | Separate factors and split train/test by attack family and intent, not random rows alone. |
| Ecological validity | [MemeSafetyBench](https://aclanthology.org/2025.emnlp-main.1555/) uses real memes and reports higher vulnerability than synthetic/typographic images in its experiments. | Include realistic visual inputs, while documenting licenses, annotation quality, and cultural/language scope. |
| Multi-turn safety drift | [MTMCS-Bench (ACL 2026)](https://aclanthology.org/2026.findings-acl.96/) evaluates escalation and context switching in image-grounded dialogues. | Decide whether the target is single-turn alignment or conversational safety; do not generalize single-turn results to the latter. |
| Reasoning-model behavior | Think in Safety finds different safety patterns across benchmark types and reasoning settings. | Report model family and reasoning mode; avoid mixing reasoning and non-reasoning VLMs as if identical. |
| Judge reliability | Automated judges can be sensitive to refusal wording, image understanding, and response detail. Benchmark papers use differing evaluators. | Validate a sample with human ratings; publish prompts, judge version, agreement, and adjudication rules. |
| Utility measurement | A defense can appear safe by refusing everything. | Include standard visual QA/reasoning scores and safe near-neighbor prompts. |
| Reproducibility and access | Some baselines use proprietary models, closed APIs, or unavailable training artifacts. | Make an open-weight model the main result; label closed-model tests as supplementary and report version/date. |

## 5. Adversarial Attack Plan

### 5.1 Attack families to cover

| Family | Representative work | What it probes | Role in the study |
|---|---|---|---|
| Typographic image instruction | [FigStep](https://arxiv.org/abs/2311.05608) | Safety behavior when harmful instruction text is rendered into an image. | Core visual-carrier stress test. |
| Crafted semantic visual context | [HADES](https://arxiv.org/abs/2403.09792) | Harmful intent distributed between image semantics and text. | Core cross-modal visual-context test. |
| Transfer attacks and image-based jailbreaks | [JailBreakV-28K](https://arxiv.org/abs/2404.03027) | Mix of transferred text jailbreaks and multimodal image attacks. | Broad coverage; use a documented subset if full execution is too costly. |
| Cross-modal linkage | [Multi-Modal Linkage](https://arxiv.org/abs/2412.00473) | Components of intent linked across text and image. | Test compositional and obfuscated cross-modal understanding. |
| Adaptive black-box attack | [PolyJailbreak](https://arxiv.org/abs/2510.17277) | Automatically adapts attack inputs to a target model. | Held-out/adaptive robustness test; follow the paper’s safe handling protocol. |
| White-box perturbation | [ADPO paper’s MMPGD-style evaluation](https://aclanthology.org/2025.findings-emnlp.735/) | Model-aware visual perturbation attacks. | Include if model access, compute, and attack implementation permit; do not treat as interchangeable with semantic jailbreaks. |
| Controlled factor combinations | [MMJailBench](https://arxiv.org/abs/2608.25490) | Varies prompt framing, instruction carrier, visual semantics, and intent under controlled settings. | Strong diagnostic set for factor attribution and held-out splits. |
| Realistic meme inputs | [MemeSafetyBench](https://aclanthology.org/2025.emnlp-main.1555/) | Safety on naturally occurring meme images and single-/multi-turn interactions. | Ecological-validity check, not a substitute for controlled attacks. |

Attack papers and benchmarks are different artifact types even when they overlap: an attack is a procedure for constructing adversarial inputs; a benchmark is a dataset/protocol for measuring model behavior. FigStep is an attack method with associated cases; JailBreakV-28K and MMJ-Bench are primarily evaluation resources; MMJailBench is a factorized evaluation suite.

### 5.2 Recommended minimum suite

For a tractable initial study, use:

1. **MMJailBench lightweight configuration** for controlled factor analysis and attack-family coverage.
2. **FigStep** for image-text rendering.
3. **HADES or Multi-Modal Linkage** for image/text compositional stress (prefer one initially to reduce overlap).
4. **One adaptive attack**, such as PolyJailbreak, kept out of alignment training.
5. **Matched benign counterparts** from VSCBench or a carefully constructed safe set.
6. **VLSBench checks** to confirm risky visual information is not trivially stated in text.

Add JailBreakV-28K or OmniSafeBench-MM for broader coverage if compute and licensing permit. Avoid claiming that any static suite proves robustness against all attacks.

### 5.3 Scoring protocol

- Primary safety: harmful-compliance rate / attack success rate, with a fixed response threshold and declared judge.
- Calibration: false-refusal rate on benign matched inputs; helpfulness/answer quality on those inputs.
- Capability: one or two task-appropriate visual QA/reasoning benchmarks before and after alignment.
- Robustness: disaggregate by risk category, carrier, attack family, prompt framing, and model.
- Reliability: report per-example evaluator instructions, sampling parameters, judge model/version, confidence intervals, and a human-audited subset.
- Comparability: run all candidate methods on the same checkpoint, data split, attacks, decoding configuration, and judge. Do not compare reported ASRs across papers as if they were controlled head-to-head results.

## 6. Benchmark Selection

| Benchmark | Primary use | Recommendation |
|---|---|---|
| [MM-SafetyBench](https://arxiv.org/abs/2311.17600) | Broad image-text safety and jailbreak cases; 13 scenarios and 5,040 pairs in the original paper. | Useful baseline coverage, but audit for visual leakage and benchmark overlap. |
| [SIUO](https://aclanthology.org/2025.findings-naacl.198/) | Safe modalities whose combination can imply unsafe outputs; nine safety domains. | Use for compositional cross-modal safety. |
| [VSCBench](https://aclanthology.org/2025.findings-acl.158/) | 3,600 image-text pairs for both under- and over-safety calibration. | Strong choice for safety/helpfulness trade-off. |
| [VLSBench](https://aclanthology.org/2025.acl-long.405/) | 2.2K image-text pairs designed to reduce visual safety information leakage. | Important validity check for claims of visual safety. |
| [MMJ-Bench](https://ojs.aaai.org/index.php/AAAI/article/view/34983) | Unified comparison of jailbreak attacks and defenses with utility evaluation. | Useful shared protocol and baseline source. |
| [MMJailBench (2026)](https://arxiv.org/abs/2608.25490) | Factorized jailbreak variables and configurable evaluation. | Most relevant recent diagnostic benchmark; inspect split and judge details. |
| [USB (ACL 2026)](https://aclanthology.org/2026.acl-long.970/) | Unified safety evaluation across 61 risk categories and four modality interactions; integrates harmful-input and benign-input over-refusal assessment. | Strong recent broad evaluation candidate. Select its vision-relevant slices and inspect whether the full benchmark matches our model/input scope. |
| [OmniSafeBench-MM (2025 preprint)](https://arxiv.org/abs/2512.06589) | Unified toolbox with multiple attacks, defenses, risk domains, and metrics. | Promising broad evaluation infrastructure; verify reproducibility and overlap before adopting. |
| [MemeSafetyBench (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1555/) | 50,430 meme-image / harmful-or-benign instruction instances; naturalistic safety evaluation. | Useful ecological-validity add-on; note its dataset is imbalanced toward harmful cases. |
| [MTMCS-Bench (ACL 2026)](https://aclanthology.org/2026.findings-acl.96/) | More than 30K multimodal/unimodal multi-turn examples for escalation and context-switch safety. | Include only if multi-turn interaction is within the study scope. |
| [PII-VisBench (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.501/) | 4,000 probes of image-grounded PII safety across subject visibility levels. | Privacy-specific; do not blend its results into harmful-instruction ASR. |
| [MSSBench](https://arxiv.org/abs/2410.06172) | Situational safety with image and language context. | Consider for context-dependent harms; inspect exact task format before selecting. |

### Recommended core benchmark package

For an initial research project, use **USB’s vision-relevant slices + VLSBench + either MMJailBench (lightweight) or VSCBench**. Add **SIUO** if the central claim concerns intent composition. USB offers breadth and joint over-refusal evaluation; VLSBench addresses whether risk really comes from the image; MMJailBench isolates attack factors, while VSCBench gives matched safety/benign calibration cases. Use a held-out adaptive attack for external robustness. This package is a recommendation to validate for access, licensing, overlap, and compute, not a claim that these are universally “the best” benchmarks.

## 7. Baselines and Comparisons

### 7.1 Minimum fair baseline set

| Baseline | Purpose |
|---|---|
| Original instruction-tuned VLM, no extra safety training | Starting-point safety and utility. |
| Standard safety SFT with VLGuard-style data | Supervised multimodal safety baseline. |
| Preference alignment with SPA-VL-style preferences / standard DPO | Preference-training baseline. |
| ADPO | Closest existing adversarial preference alignment comparator; especially relevant if our method uses adversarial training. |
| One inference-time defense (CMRM or MMAligner) | Representation calibration comparison. Select based on available code and compatible model architecture. |
| VLMGuard-R1 or another input guardrail | External guardrail/system-level comparison; report latency and errors separately. |
| SafetyReminder | Generation-time comparison if implementation and model compatibility are available. |
| Proposed method | Controlled cross-modal counterfactual alignment; exact objective to be finalized after baseline feasibility audit. |

Do not include every published defense in the core experiment. First reproduce a small, methodologically diverse set. Add SafeVLM or Think in Safety where the model type and compute make a fair comparison possible.

### 7.2 Candidate proposed training recipe (hypothesis)

Construct **matched safe/unsafe pairs** from an underlying scenario and vary the carrier: (a) direct text, (b) text rendered in an image, (c) semantic visual evidence, and (d) joint image-text context. Train a VLM on safe responses/refusals using a preference or contrastive objective, and preserve matched benign requests as explicit non-refusal examples. Keep attack families, prompt framings, and preferably intent templates held out for evaluation.

This is a proposal, not an existing proven method. ADPO already studies adversarial preference alignment; the differentiating claim would need to be **factorized cross-modal counterfactual supervision plus held-out transfer and calibrated helpfulness**, not “we are the first to use adversarial DPO for VLM safety.” The most important first experiment may be a controlled comparison of SFT, standard DPO, ADPO, and the proposed data construction under identical evaluation.

## 8. Main Research Hypotheses and Ablations

**H1 (transfer):** Training with counterfactual pairs spanning text and image carriers improves safety on held-out carriers/attack families more than same-size unimodal safety data.

**H2 (calibration):** Matched benign examples reduce false refusals relative to safety-only refusal training at similar harmful-compliance rates.

**H3 (factor importance):** Joint image-text composition and prompt framing explain failures not captured by typography-only tests.
**H4 (trade-off):** A measured safety gain can be achieved without material regression on the chosen visual QA task; define the acceptable bound before running experiments.

These are testable claims, not expected outcomes. Report null results and failures to transfer as valid findings.

## 9. 20-Minute Presentation Structure

1. **Motivation and scope (2 min):** why vision changes safety; define operational safety behavior.
2. **Problem evidence (3 min):** VLGuard/CMRM and a visual failure example; distinguish initial alignment from robustness.
3. **Field map (4 min):** training alignment, representation/decoding defenses, input guardrails, reasoning safety.
4. **Evaluation gap (4 min):** attacks versus benchmarks; visual leakage, over-refusal, compositional and adaptive attacks.
5. **Research challenges (2 min):** data validity, generalization, judge reliability, safety-utility trade-off.
6. **Proposed problem and hypotheses (3 min):** controlled cross-modal counterfactual alignment with held-out attacks.
7. **Study design and baselines (2 min):** model, core benchmark package, method comparisons, metrics.

Suggested title: **“Safety Alignment for Vision-Language Models: Methods, Evaluation Gaps, and a Study of Cross-Modal Robustness.”**

## 10. What We Can and Cannot Claim Yet

**Supported by the reviewed literature:** VLM safety is studied with safety data/SFT, preference methods, adversarially robust training, representation interventions, runtime guardrails, and reasoning-oriented tuning. Benchmarks now test more than basic refusal, including composition, visual leakage, calibration, realistic images, adaptive attacks, privacy, and multi-turn context.

**Not supported yet:** that one method is the overall state of the art; that the proposed cross-modal pair-training idea is novel; that a listed benchmark exhaustively tests safety; that reported attack-success rates from separate papers are comparable; or that a single successful benchmark run establishes robust alignment.

**Next literature audit before final proposal:** read complete method/experiment sections for ADPO, MMAligner, SafetyReminder, VLMGuard-R1, MMJailBench, OmniSafeBench-MM, VSCBench, and VLSBench; inspect released code and licenses; chase citation chains for 2026 safety-alignment work; verify whether counterfactual carrier-matched preference training has already been studied.

## References

The linked primary sources are embedded in the tables above. Additional core sources:

- [FigStep (2023)](https://arxiv.org/abs/2311.05608)
- [MM-SafetyBench (2023/2024)](https://arxiv.org/abs/2311.17600)
- [JailBreakV-28K (2024)](https://arxiv.org/abs/2404.03027)
- [HADES (2024)](https://arxiv.org/abs/2403.09792)
- [Multi-Modal Linkage (2024; ACL 2025 proceedings)](https://arxiv.org/abs/2412.00473)
- [PolyJailbreak (2025 preprint)](https://arxiv.org/abs/2510.17277)
- [MMJ-Bench (AAAI 2025)](https://ojs.aaai.org/index.php/AAAI/article/view/34983)
- [OmniSafeBench-MM (2025 preprint)](https://arxiv.org/abs/2512.06589)
