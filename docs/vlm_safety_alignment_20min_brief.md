# VLM Safety Alignment: 20-Minute Research Brief

## Talk Thesis

Safety-aligned VLMs inherit text-model safety mechanisms, but visual inputs create a second attack channel. Existing VLM safety work mostly improves initial alignment, adds inference-time guardrails, or benchmarks jailbreaks. The open research gap is continual safety alignment: preserving multimodal safety while the VLM is sequentially fine-tuned on benign vision-language tasks.

Our proposed angle is to extend Bach et al. (ACL Findings 2026), *Continual Safety Alignment via Gradient-Based Sample Selection*, from text LLMs to small VLMs. Their core finding is that fine-tuning samples are not equally dangerous: high-gradient samples cause greater safety degradation, while moderate-gradient samples preserve alignment with competitive task learning. The VLM version asks whether the same gradient signal predicts safety drift when gradients are split across the language backbone, vision-language projector, and joint multimodal path.

## Problem Formulation

Given an initially aligned VLM with parameters theta_0, train it sequentially on benign multimodal datasets D_1 ... D_T while preserving:

- task utility on each new vision-language task;
- prior-task retention across the sequence;
- multimodal safety under image-text jailbreaks;
- text-only safety inherited from the underlying LLM;
- low false-refusal rate on benign but sensitive visual inputs.

The central question:

Can per-sample multimodal gradient statistics identify benign fine-tuning examples that are likely to push a VLM out of its safety region?

## Why This Is Not Already Solved

Text continual safety alignment is not enough because VLMs introduce:

- image-channel attacks, such as harmful instructions rendered as typography;
- cross-modal composition failures, where safe image + safe text can jointly produce unsafe output;
- representation shifts caused by visual inputs that prevent text-learned refusal boundaries from activating;
- modality gaps, where unsafe visual concepts are recognized but not treated as unsafe;
- parameter attribution ambiguity: safety drift may live in the LLM backbone, projector, visual adapter, or their interaction.

## Foundational Papers

| Paper | What it gives us | How to position it |
| --- | --- | --- |
| Bach et al., 2026, *Continual Safety Alignment via Gradient-Based Sample Selection*, arXiv:2604.17215 | Text-only method: high-gradient samples worsen safety drift; moderate-gradient samples preserve alignment without curated safety data. | Primary method to extend. |
| Peng et al., 2024, *Navigating the Safety Landscape*, arXiv:2405.17374 | Safety basin and VISAGE: safety can collapse sharply outside a local parameter region. | The geometry explaining why fine-tuning can be dangerous. |
| Ji et al., 2024/2025, *Language Models Resist Alignment*, arXiv:2406.06144 | Elasticity: aligned models tend to revert toward pretrained behavior under fine-tuning. | The mechanism explaining why benign fine-tuning can undo alignment. |

## State-of-the-Art VLM Safety Alignment Papers

| Paper | Method type | Key contribution | Gap for our work |
| --- | --- | --- | --- |
| Zong et al., 2024, *Safety Fine-Tuning at (Almost) No Cost / VLGuard*, arXiv:2402.02207 | Safety dataset + SFT | Builds VLGuard and shows multimodal safety fine-tuning can reduce attacks with small utility cost. | Requires curated safety data; not a continual benign fine-tuning preservation method. |
| Liu et al., 2024, *Safety Alignment for Vision Language Models / SafeVLM*, arXiv:2405.13581 | Architecture + safety modules | Adds safety projector, safety tokens, safety head with two-stage training; reports RTVLM safety score 8.26 on LLaVA-v1.5. | Architectural intervention; not data-centric continual adaptation. |
| Zhang et al., 2024/2025, *SPA-VL*, arXiv:2406.12030 | Preference alignment dataset | 100,788 safety preference quadruples across 6 domains, 13 categories, 53 subcategories. | Large-scale initial alignment data; does not solve later safety drift. |
| Liu et al., 2024/2025, *Unraveling and Mitigating Safety Alignment Degradation of VLMs*, arXiv:2410.09047 | Inference-time representation correction | CMRM shifts multimodal hidden states closer to text-safe representations; reports LLaVA-7B unsafe rate dropping from 61.53% to 5.41% / 3.15% on VLSafe. | Inference-time correction; does not protect the training process. |
| Chen et al., 2025/2026, *VLMGuard-R1*, arXiv:2504.12661 | Prompt rewriting guardrail | Reasoning-driven prompt optimization without changing target VLM parameters; reports 43.59% average safety increase on SIUO. | External input-stage defense; not intrinsic safety preservation during fine-tuning. |
| Tang et al., 2025/2026, *SafetyReminder*, arXiv:2506.15734 / AAAI 2026 | Soft prompt defense | Reactivates delayed safety awareness during generation using learned soft prompts. | Generation-time mitigation; not a sample-selection or continual-learning method. |
| Zhang et al., 2026, *MMAligner*, arXiv:2608.05909 | Representation calibration | Calibrates unsafe multimodal representations into the refusal region; reports 99% refusal rate with <2% utility degradation. | Strong SOTA defense baseline, but still calibration/fine-tuning rather than continual sample selection. |
| Lou et al., 2025, *Think in Safety*, arXiv:2505.06538 / EMNLP 2025 | Safety reasoning dataset | Studies multimodal reasoning models and trains with safety-oriented thought processes. | Important for reasoning VLMs; orthogonal to gradient-based continual preservation. |

## Attack Papers to Use in Evaluation

| Attack / benchmark | What it tests | Why include it |
| --- | --- | --- |
| FigStep, arXiv:2311.05608 | Converts prohibited text instructions into typographic images; reports 82.50% average ASR on six open-source LVLMs. | Cleanest demonstration of image-channel jailbreak. |
| HADES, arXiv:2403.09792 | Uses crafted images to hide/amplify malicious intent; reports 90.26% ASR on LLaVA-1.5 and 71.60% on Gemini Pro Vision. | Tests visual vulnerability beyond typography. |
| JailBreakV-28K, arXiv:2404.03027 | 28,000 cases: 20,000 text-based jailbreak prompts + 8,000 image-based jailbreak inputs. | Broad transfer benchmark across text and image attack families. |
| Multi-Modal Linkage, arXiv:2412.00473 | Splits malicious intent across modalities via encryption/decryption style linkage. | Strong newer black-box attack against frontier VLMs. |
| PolyJailbreak, arXiv:2510.17277 | Cross-modal black-box jailbreak optimization. | Useful stretch attack if time permits. |

Use these at a high level in slides. Do not show operational harmful instructions; show attack structure, ASR, and failure mode.

## Benchmarks

Primary safety benchmarks:

- MM-SafetyBench, arXiv:2311.17600: 13 scenarios, 5,040 text-image pairs; evaluates image-based manipulations against aligned MLLMs.
- JailBreakV-28K, arXiv:2404.03027: broad multimodal jailbreak robustness.
- FigStep dataset, arXiv:2311.05608: typographic visual jailbreak stress test.
- VLGuard, arXiv:2402.02207: safety fine-tuning dataset and evaluation suite.
- SIUO, arXiv:2406.15279: safe inputs but unsafe output, across 9 safety domains.
- MSSBench, arXiv:2410.06172: situational safety, 1,820 language query-image pairs.
- MMJ-Bench, arXiv:2408.08464: unified evaluation of VLM jailbreak attacks and defenses.
- MMJailBench, arXiv:2608.25490: newer factorized benchmark that separates harmful intent, visual semantics, instruction carrier, and prompt framing.
- UnsafeConcepts / SaferVLM, USENIX Security 2025: 75 unsafe concepts and 1.5K images for visual/text modality-gap analysis.

Utility benchmarks:

- MMBench or MME for general multimodal ability.
- ScienceQA or MathVista for visual reasoning.
- DocVQA / TextVQA for OCR-heavy ability.
- POPE for object hallucination.
- Text-only AdvBench / HarmBench to confirm the VLM still preserves inherited LLM safety.

## Baselines

Minimum baseline set:

- full fine-tuning on each multimodal task;
- random 20% selection;
- low-gradient 20%;
- high-gradient 20%;
- moderate-gradient language-backbone only;
- moderate-gradient projector only;
- moderate-gradient joint gradient;
- KL regularization to original aligned model;
- EWC or Fisher regularization;
- VLGuard mixed safety data;
- CMRM / MMAligner as inference-time or representation-calibration comparison.

Optional if resources allow:

- SafeVLM-style safety head/module;
- VLMGuard-R1 prompt rewriting;
- SafetyReminder soft-prompt defense;
- replay/memory baseline with a small safety buffer.

## Proposed Research Contribution

The clean contribution is not "we invented VLM safety." It is:

1. First data-centric continual safety alignment study for small VLMs using per-sample multimodal gradient selection.
2. First attribution analysis separating language-backbone, projector, and joint gradient signals for safety drift.
3. A controlled evaluation of whether text-only safety-basin/elasticity ideas transfer to multimodal models.
4. A practical baseline recipe for preserving VLM safety during benign downstream fine-tuning without requiring additional curated safety data.

## Experimental Design

Model:

- Qwen2-VL-2B-Instruct or LLaVA-v1.5-7B as the primary open VLM.
- Keep vision encoder frozen if following common VLM fine-tuning setups; train LoRA adapters and/or projector.

Task sequence:

- general visual instruction following: LLaVA-Instruct or similar;
- visual reasoning: ScienceQA or MathVista;
- medical visual QA: VQA-RAD or SLAKE;
- document/OCR: DocVQA or TextVQA.

Metrics:

- ASR on MM-SafetyBench, FigStep, JailBreakV-28K;
- refusal rate on harmful multimodal inputs;
- false refusal rate on benign sensitive images/prompts;
- task accuracy for each downstream dataset;
- BWT / forgetting measure across task sequence;
- VISAGE-style safety-basin retention if computationally feasible;
- gradient attribution: correlation between per-sample G_i and post-training safety degradation.

## Research Challenges

- Per-sample gradients are expensive with images; use loss pre-filtering and micro-batched single-sample backward passes.
- Visual-token labels must be masked, otherwise gradient norms measure image-token complexity rather than response-learning pressure.
- Safety judges are noisy; pair automatic judging with a small manual audit.
- High-gradient samples may be format mismatches, not harmful content; avoid claiming they are adversarial unless shown.
- VLM attacks vary by modality and judge; one benchmark is not enough.
- Over-refusal matters: a safer model that refuses benign medical, legal, art, or identity-related images is not aligned.
- Projector-only vs language-only gradients may identify different failure modes; this is the central ablation.

## 20-Minute Slide Plan

1. Title and one-sentence thesis.
2. Problem: benign fine-tuning can break safety.
3. Why VLMs are harder: image channel and cross-modal composition.
4. Foundation: elasticity and safety basin.
5. Bach et al. method: moderate-gradient sample selection.
6. Evidence from text LLMs: why high-G_i is dangerous and moderate-G_i is the target.
7. VLM SOTA map: safety fine-tuning, preference alignment, inference-time defenses, prompt rewriting, representation calibration.
8. Gap: none directly solve continual benign VLM fine-tuning without extra safety data.
9. Proposed formulation and hypotheses.
10. Method: loss pre-filter, per-sample multimodal G_i, median selection.
11. VLM-specific ablation: language vs projector vs joint gradients.
12. Attack suite: FigStep, HADES, JailBreakV-28K, MM-SafetyBench.
13. Benchmarks and metrics: safety, utility, false refusal, forgetting.
14. Baselines.
15. Expected outcomes and what would falsify the hypothesis.
16. Research challenges and risk controls.
17. Timeline / implementation plan.
18. Takeaway: preserve safety during adaptation, not only after deployment.

## One-Slide Takeaway

Existing VLM safety papers mostly answer: "How do we make a VLM safer now?"

This project asks: "After it is safe, how do we keep it safe while it keeps learning?"

