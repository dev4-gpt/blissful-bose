# Spoken Presentation Script: Continual Safety Alignment in Small VLMs
## Slide-by-Slide Speaker Notes for Meeting with Prof. Thao Minh Le
### Author: Aryaman Singh Dev | Penn State University

---

### Navigation & Delivery Guidelines
- **Target Pace**: ~45–60 seconds per slide (25–30 minutes total presentation).
- **Style**: Conversational, academically rigorous, and direct. 
- **Rule of Thumb**: **Never read the slide verbatim**. The slide contains the formulas, tables, and formal citations for the professor's visual reference. Your spoken words should explain the *motivation, intuition, structural insight, and technical rationale*.
- **Addressing the Advisor**: When discussing Bach et al., frame it naturally as *"As established in your paper with Bach et al..."* or *"Building directly on your findings..."*

---

## Slide 01: Title Slide
- **Slide Title**: *Continual Safety Alignment in Vision-Language Models via Multimodal Gradient-Based Sample Selection*
- **What to Say**:
  > "Good afternoon, Professor Le. Today, I am excited to present my research proposal on extending continual safety alignment to multimodal architectures. Specifically, this work builds directly on your paper, Bach et al., investigating whether gradient-based sample selection can prevent safety degradation in small vision-language models without requiring architectural modifications or expensive safety retraining. Over the next 25 minutes, I will walk you through the theoretical motivation, our multimodal gradient decomposition, our experimental protocol on Qwen2-VL, and the roadmap for empirical validation."
- **Key Takeaway**: Establishing project identity, advisor lineage, and clear research scope.

---

## Slide 02: Research Proposal — Alignment Drift in Continual Fine-Tuning
- **Slide Title**: *The Problem: Alignment Drift in Continual Fine-Tuning*
- **What to Say**:
  > "To establish the problem: in your paper, you demonstrated that benign fine-tuning erodes safety guardrails as a structural byproduct of gradient descent. High-gradient samples drive elastic reversion toward unaligned pretraining distributions, and standard remedies like gradient clipping fail because clipping merely shortens the step size while keeping the exact unaligned direction. 
  > However, in the Limitations section of Bach et al., you explicitly noted that extending gradient-based selection to vision-language models remains an open question. In VLMs, the problem is compounded: attackers exploit an unprotected visual channel—using image typography or visual jailbreaks—that completely bypasses text safety filters. Our central question is: does the same gradient-driven drift govern VLMs, and can data-centric median selection defend both text and visual safety channels?"
- **Key Takeaway**: Anchoring the core problem in Bach et al.'s explicit limitation statement.

---

## Slide 03: Theoretical Foundation — LLM Elasticity (Ji et al., 2024)
- **Slide Title**: *LLM Elasticity*
- **What to Say**:
  > "To understand why fine-tuning degrades safety, we look at the elasticity framework by Ji et al. Models behave like coupled springs: the massive pretraining distribution exerts an elastic restoring force that pulls the model back toward its unaligned base state whenever fine-tuning updates perturb it. 
  > Importantly, in our project, we do not assume dataset size alone dictates this pull. Rather, high-gradient samples—which often reflect severe format or semantic mismatch—act as heavy perturbations that stretch the model past its elastic limit, triggering rapid reversion to unaligned behavior."
- **Key Takeaway**: Elastic restoring force explains *why* benign updates cause catastrophic safety drift.

---

## Slide 04: Theoretical Foundation — VISAGE Safety Basin Geometry (Peng et al., 2024)
- **Slide Title**: *VISAGE: Volumetric Index for Safety Alignment Guided by Explanation*
- **What to Say**:
  > "The geometry of this drift is captured by Peng et al.'s VISAGE framework. Safety alignment does not occupy a broad, forgiving landscape; it resides in a localized 'safety basin' with sharp, step-function boundaries. Small, moderate parameter updates allow the model to stay inside this basin. But large gradient updates push model weights directly over the ridge into unsafe territory, where safety collapses abruptly. 
  > A higher VISAGE score indicates a deeper, more robust basin. Our goal is ensuring that continual fine-tuning updates remain confined within this safe volume."
- **Key Takeaway**: Safety basins have non-linear, sharp boundaries, making gradient magnitude control essential.

---

## Slide 05: Benchmark Suite — 1-to-1 Mapping from Text LLMs to VLMs
- **Slide Title**: *Evaluation Suite: Mapping LLM Benchmarks to Multimodal Counterparts*
- **What to Say**:
  > "To evaluate this rigorously, we cannot rely on standard text benchmarks alone. On this slide, I have established a strict 1-to-1 mapping from every text evaluation in Bach et al. to its multimodal equivalent.
  > For safety, AdvBench and HarmBench map to MM-SafetyBench and FigStep—which renders toxic text directly onto images—alongside JailBreakV-28K and a text slice of HarmBench. For truthfulness, TruthfulQA maps to open-ended hallucination on MMHal-Bench and object probing on POPE. And for downstream tasks, Dolly, GSM8K, MedMCQA, and SQuAD v2 map directly to LLaVA-Instruct, MathVista, SLAKE, and DocVQA. This ensures our evaluation mirrors the depth of the original text study."
- **Key Takeaway**: Principled, direct translation of every experimental dimension from LLM to VLM.

---

## Slide 06: Attack Surface & Multi-Channel Evaluation
- **Slide Title**: *VLM Attack Surface & Multi-Channel Evaluation*
- **What to Say**:
  > "A critical insight for VLMs is that reporting a single aggregate Attack Success Rate is dangerous and misleading. A model could maintain a 2% text ASR while its visual ASR collapses to 70%.
  > As shown in the table, we decompose attacks across six distinct surfaces: raw text channels, OCR rendering, visual semantic content, optimization transfer, cross-modal conflicts, and typographic distortions. In our evaluation, we will explicitly report separate metrics for ASR-text, ASR-image, ASR-cross, and aggregate ASR to detect modality-specific alignment collapse."
- **Key Takeaway**: Disaggregated ASR reporting is mandatory to uncover hidden visual channel failures.

---

## Slide 07: SOTA Baseline — SafeVLM Architectural Defense (Nie et al., 2024)
- **Slide Title**: *Related Multimodal Safety Approach: SafeVLM*
- **What to Say**:
  > "To contextualize our contribution against state-of-the-art multimodal safety, we examine SafeVLM by Nie et al. SafeVLM addresses VLM vulnerability through an architectural approach. As shown in Figure 1 from their paper, they freeze the base VLM and add three dedicated modules: a parallel Safety Projector, trainable Safety Tokens, and a multi-class Safety Head. 
  > This requires a complex two-stage training pipeline and permanently alters the model's inference topology. While effective, it represents an architectural defense, which motivated our search for a purely data-centric solution."
- **Key Takeaway**: SafeVLM represents the architectural paradigm; our work pioneers the data-centric paradigm.

---

## Slide 08: SafeVLM Empirical Results & Over-Refusal Trade-offs
- **Slide Title**: *SafeVLM Empirical Results: Safety Scores & Over-Refusal Trade-offs (Tables 3 & 4)*
- **What to Say**:
  > "Looking at SafeVLM's reported numbers in Tables 3 and 4, two key findings emerge. First, SafeVLM provides empirical proof that pre-trained visual projectors lack safety alignment—justifying why visual inputs easily jailbreak models.
  > Second, their defense comes with substantial trade-offs: on XSTest, their safe instruction accuracy drops by over 14%, indicating severe over-refusal and false alarms. Furthermore, their custom safety head adds computational overhead during every inference step. Our data-centric hypothesis is that by filtering training samples at the gradient level, we can achieve competitive safety retention with zero architectural changes, zero latency penalty, and lower over-refusal."
- **Key Takeaway**: SafeVLM proves projectors are vulnerable but suffers from over-refusal and inference overhead.

---

## Slide 09: VLM Methodology — Multimodal Parameter Decomposition
- **Slide Title**: *VLM Extension: Methodology — Parameter Formalization*
- **What to Say**:
  > "Now, let us turn to our core methodology. We formalize continual safety alignment across a sequence of T multimodal tasks, where each task contains visual inputs, text instructions, and target responses.
  > In a VLM, the parameter space is decomposed into three distinct components: the vision encoder weights, the vision-language projector weights, and the language backbone weights. When using parameter-efficient fine-tuning, the vision encoder and base language model remain frozen, and optimization is restricted strictly to the language LoRA adapters and the cross-modal projector. Our goal is minimizing task loss while constraining the updated parameters within the multimodal safety basin."
- **Key Takeaway**: Formal setup of the parameter subspace $\Theta_{\text{train}} = (\Theta_{\text{LoRA}}, \Theta_{\text{projector}})$.

---

## Slide 10: The Multimodal Dilemma — Why Naive Gradients Fail
- **Slide Title**: *VLM Extension: The Multimodal Dilemma*
- **What to Say**:
  > "The immediate challenge when extending Bach et al. to VLMs is that computing a naive gradient norm across the entire model fails. 
  > If you backpropagate through all parameters, the Vision Transformer contains high spatial pixel variance and hundreds of image patch tokens. This visual noise completely swamps the gradient norm. A sample could receive an enormous gradient simply because the image had high visual contrast or complex texture, rather than because it strained the model's alignment. We must decouple parameter groups."
- **Key Takeaway**: Full-model backprop causes image reconstruction noise to swamp safety signals.

---

## Slide 11: Disentangling Modality Tension
- **Slide Title**: *VLM Extension: Disentangling Modality Tension*
- **What to Say**:
  > "In text LLMs, high-gradient samples were primarily caused by output format mismatch—such as short categorical targets colliding with verbose conversational safety pretraining. 
  > In VLMs, high gradients arise from two fundamentally distinct sources: format mismatch in the text decoder, and visual grounding conflict in the connector, where dense visual tokens collide with language priors. To study this, we must track and attribute gradients separately across modalities."
- **Key Takeaway**: VLM gradient tension has dual origins: linguistic format mismatch vs. cross-modal grounding conflict.

---

## Slide 12: Strict Response-Only Label Masking (`label = -100`)
- **Slide Title**: *VLM Extension: Response-Only Loss Formulation*
- **What to Say**:
  > "This brings us to a foundational technical requirement: strict label masking. As shown in the formula, our per-sample loss is calculated strictly over the assistant target response tokens, $Y_i$.
  > In PyTorch, we mask all non-target positions to -100: all image patch tokens, system instructions, user prompts, and padding tokens. Because cross-entropy loss ignores -100 positions, gradients backpropagate strictly from response tokens conditioned on the multimodal prefix. This guarantees that $G_i$ measures the parameter change needed to generate the answer, completely preventing visual reconstruction loss from corrupting our selection."
- **Key Takeaway**: PyTorch `label = -100` masking guarantees gradients reflect alignment, not image modeling.

---

## Slide 13: Proposed Gradient Attribution Modes
- **Slide Title**: *VLM Extension: The 3 Novel Attribution Modes*
- **What to Say**:
  > "With response-only loss established, we formulate our core ablation: three distinct gradient attribution modes.
  > First, Language-LoRA only, $G_i^{(L)}$, which isolates whether drift is driven by conversational response priors in the decoder.
  > Second, Projector-only, $G_i^{(P)}$, which isolates cross-modal feature warping in the visual bridge.
  > Third, Joint Multimodal Attribution, $G_i^{(J)}$, which combines both signals using a balancing scalar $\lambda$. This ablation allows us to answer whether safety drift originates in the language backbone or the vision connector."
- **Key Takeaway**: Three attribution modes ($G_i^{(L)}, G_i^{(P)}, G_i^{(J)}$) form the core scientific ablation of this research.

---

## Slide 14: The Balancing Scalar $\lambda$ & Median-Normalized Formulation
- **Slide Title**: *VLM Extension: Balancing Scalar $\lambda$*
- **What to Say**:
  > "When combining language and projector gradients into $G_i^{(J)}$, a naive sum would allow the language LoRA adapters to dominate simply because they contain more parameters.
  > To solve this, we propose a scale-invariant, median-normalized formulation, shown at the bottom of the slide. By dividing each module's gradient norm by its own empirical median across the dataset before squaring and summing, both the language decoder and the vision projector contribute equally to the joint tension metric."
- **Key Takeaway**: Median-normalized joint norm prevents parameter count disparities from biasing sample selection.

---

## Slide 15: VLM-Specific Diagnostic Logging
- **Slide Title**: *VLM Extension: Per-Sample Diagnostic Logging*
- **What to Say**:
  > "To ensure our selection is methodologically sound, we log a comprehensive set of per-sample diagnostics during the selection pass: target token count, prompt length, image token count, native image resolution, mean response loss, and individual module gradients. This provides full observability and allows us to rule out confounders."
- **Key Takeaway**: Comprehensive per-sample telemetry ensures zero-hallucination analysis of filtered data.

---

## Slide 16: Length Normalization & L2 Norm Foundations
- **Slide Title**: *VLM Extension: Length Normalization*
- **What to Say**:
  > "Slide 16 details our length normalization mechanism. In auto-regressive generation, longer responses naturally accumulate higher gradient norms simply because you are summing across more token loss steps. A 300-word benign explanation could easily exhibit a larger gradient than a 2-word unsafe response.
  > We implement length normalization by dividing the joint norm by the square root of the target token count. We will use this in sensitivity analysis to verify that our median selection captures semantic tension rather than verbosity."
- **Key Takeaway**: $\tilde{G}_i = G_i / \sqrt{N_{\text{tokens}}}$ prevents answer length from confounding gradient ranking.

---

## Slide 17: Total Norm vs. Selection Buckets
- **Slide Title**: *VLM Extension: Total Norm & Selection Buckets*
- **What to Say**:
  > "If we only tracked a single total norm, we would have no diagnostic visibility into which mechanism caused an outlier—whether it was a formatting clash, an ambiguous image, or an unusually long answer.
  > As in Bach et al., our selection pipeline does not simply pick the lowest gradients. We first apply a loss pre-filter $[\mu_L \pm \sigma_L]$ to eliminate outliers, and then select the 20% of samples closest to the median gradient norm, comparing them against Low-$G_i$, High-$G_i$, Random, and Full fine-tuning."
- **Key Takeaway**: Re-affirming the 3-stage median selection pipeline adapted from Bach et al.

---

## Slide 18: Execution Plan — 4-Stage Continual Task Sequence
- **Slide Title**: *Execution Plan: 4-Stage Continual Task Sequence*
- **What to Say**:
  > "On Slide 18, we outline our continual training sequence. We proceed through four diverse stages: general visual instruction following on LLaVA-150K; visual math reasoning on MathVista; clinical image understanding on SLAKE; and dense document OCR on DocVQA.
  > Crucially, for clinical VQA, we use SLAKE's 14,000 samples for training, and preserve VQA-RAD as an untouched, out-of-domain benchmark to test true generalization. For MathVista, we strictly separate the training split from held-out evaluation."
- **Key Takeaway**: Methodologically clean 4-task sequence with strict training vs. evaluation data hygiene.

---

## Slide 19: Implementation Plan — Two-Phase Compute Roadmap
- **Slide Title**: *Implementation Plan: Two-Phase Roadmap*
- **What to Say**:
  > "Our experimental roadmap is divided into two pragmatic phases. Phase 1 is a rapid pilot on Google Colab using a single T4 GPU. We use Qwen2-VL-2B in 4-bit QLoRA on a 1,000-sample subset of LLaVA-Instruct. This pilot will quickly test our core hypothesis: does High-$G_i$ induce higher visual ASR than Moderate-$G_i$ on FigStep and MM-SafetyBench?
  > Once validated, Phase 2 scales to the PSU Campus Cluster across 3 random seeds, running the full 4-task sequence, complete benchmark suite, and full attribution ablation."
- **Key Takeaway**: Low-risk, fast-failing Phase 1 pilot on Colab T4 before scaling to the PSU cluster.

---

## Slide 20: Practical Setup & LoRA Hyperparameters
- **Slide Title**: *Implementation Plan: Local-First Setup & Hyperparameters*
- **What to Say**:
  > "For model selection, Qwen2-VL-2B-Instruct is ideal: it belongs to the exact Qwen architectural family analyzed in Bach et al., ensuring theoretical continuity while fitting into consumer hardware.
  > We target all attention projections (q, k, v, o) and MLP layers in the language backbone with rank 16 and alpha 32. Our success criterion in Phase 1 is confirming that Moderate-$G_i$ preserves lower ASR than standard or random fine-tuning while matching downstream task accuracy."
- **Key Takeaway**: Architecture lineage with Qwen2.5/Qwen3 maintained; clean LoRA configuration.

---

## Slide 21: VLM Safety Judging — Limitations of Text Judges
- **Slide Title**: *Safety Judges for VLMs: The Visual Blindspot*
- **What to Say**:
  > "Evaluating safety in VLMs introduces a major evaluation dilemma: text-only judges like Llama-Guard are blind to images. In a FigStep attack, the harmful instruction is rendered visually inside the image while the text prompt is completely benign. If a text judge only inspects the prompt and answer, it cannot determine whether the model obeyed a harmful visual directive.
  > Therefore, for visual jailbreaks, our judge must evaluate the generated response against the intended harmful instruction embedded in the image, rather than the raw text prompt alone."
- **Key Takeaway**: Text-only judges fail on image jailbreaks; visual context must be explicitly passed to the evaluator.

---

## Slide 22: Structured Record Schema for Evaluators
- **Slide Title**: *Safety Judges for VLMs: Structured Record Schema*
- **What to Say**:
  > "To implement this cleanly, we feed our automated evaluator a standardized record containing: the attack category, the image, the decoded reference harmful instruction, the prompt, and the VLM's response. 
  > We then supplement automated evaluation with a stratified manual audit across attack categories to empirically calibrate judge accuracy."
- **Key Takeaway**: Structured evaluation records guarantee reproducible, verifiable safety classification.

---

## Slide 23: Two-Stage Safety Evaluation Protocol
- **Slide Title**: *Two-Stage Evaluation Protocol*
- **What to Say**:
  > "Slide 23 summarizes our two-stage safety evaluation. Stage 1 executes automated classification of refusal versus compliance, logging raw text responses for every attack. 
  > Importantly, we pair safety with utility: a model that refuses every visual question has low ASR but zero utility. We report the complete Pareto frontier: Low ASR paired with High Task Score. Stage 2 executes manual spot-checks to inspect partial compliance and visual hallucinations."
- **Key Takeaway**: Safety must be coupled with task capability to prevent rewarding degenerate over-refusal.

---

## Slide 24: Threat Model & Attack Surface Breakdown
- **Slide Title**: *Threat Model: Multimodal Attack Taxonomy*
- **What to Say**:
  > "Slide 24 formalizes our threat model. We assume a test-time adversary who provides malicious multimodal inputs without modifying model weights. 
  > The table systematically decomposes the attack matrix: text-only prompts test decoder safety; text rendered in images tests the visual OCR bypass; harmful images test visual semantic safety; benign images with harmful prompts test distraction; and joint ambiguous pairs test multimodal synergy."
- **Key Takeaway**: Formal threat model isolating decoder, OCR, semantic, and cross-modal attack vectors.

---

## Slide 25: Comprehensive Observability Checklist
- **Slide Title**: *VLM Evaluation and Observability Checklist*
- **What to Say**:
  > "Slide 25 provides our multi-dimensional observability checklist. Beyond text and visual ASR, we track benign over-refusal on clean visual questions, open-ended hallucination via MMHal-Bench, object hallucination via POPE, task accuracy across all 4 stages, volumetric safety basin retention, and computational training cost."
- **Key Takeaway**: Multi-dimensional scorecard covering safety, hallucination, utility, and compute cost.

---

## Slide 26: Continual Learning Dynamics — Formal Metrics
- **Slide Title**: *Continual-Learning Metrics & Dynamics*
- **What to Say**:
  > "On Slide 26, we formalize our continual learning metrics. We maintain the complete task performance matrix, $R_{t,k}$, tracking performance on past tasks after training on each new task.
  > From this matrix, we compute Backward Transfer (BWT) to quantify retention, Forgetting Measure (FM) to capture peak-to-final accuracy drops, and pairwise Task Interference, $I_{j \rightarrow k}$, which isolates exactly how learning task $j$ alters performance on earlier task $k$."
- **Key Takeaway**: Mathematical formalization of continual learning dynamics ($R_{t,k}$, BWT, FM, and $I_{j \rightarrow k}$).

---

## Slide 27: VLM Specific Mechanism Diagnostics
- **Slide Title**: *VLM Specific Mechanism Diagnostics*
- **What to Say**:
  > "Slide 27 presents our diagnostics table. For every experiment, we record language LoRA drift, projector drift, joint norms, token lengths, image resolution, and parameter distance from the aligned checkpoint $\theta_0$. This allows us to map sample selection directly to weight trajectory shifts in parameter space."
- **Key Takeaway**: Diagnostic table linking sample selection to geometric parameter trajectories.

---

## Slide 28: VLM Control Conditions & Baselines Grid
- **Slide Title**: *VLM Control Conditions and Baselines*
- **What to Say**:
  > "Slide 28 is our experimental control grid, spanning 13 conditions. Every condition answers a distinct scientific question:
  > Aligned $\theta_0$ sets the ceiling; Standard Fine-Tuning measures unconstrained drift; Random 20% controls for sample count; Low and High-$G_i$ test the extreme ends of the spectrum; Gradient Clipping tests whether magnitude control suffices; EWC tests generic forgetting regularizers; and our three attribution modes ($G_i^{(L)}, G_i^{(P)}, G_i^{(J)}$) isolate the modality responsible for drift."
- **Key Takeaway**: Airtight 13-condition experimental grid isolating every potential confounder.

---

## Slide 29: Complete Evaluation Matrix
- **Slide Title**: *VLM Continual-Learning Diagnostics Summary*
- **What to Say**:
  > "Slide 29 provides our complete evaluation scorecard, mapping every metric—from multi-channel ASR to judge/manual agreement and GPU wall-clock training efficiency—to its precise measurement methodology."
- **Key Takeaway**: Unified operational summary of the entire experimental pipeline.

---

## Slide 30: Summary & 6 Core Research Questions
- **Slide Title**: *Summary and Open Research Questions*
- **What to Say**:
  > "To summarize: in text LLMs, we know high-gradient samples drive elastic reversion out of safety basins, and median filtering preserves alignment without extra safety data.
  > In this research, we are answering six fundamental questions: Does multimodal gradient selection protect both text and visual jailbreaks? Does tension concentrate in the language LoRA weights or the cross-modal projector? Can we eliminate forgetting with zero architectural overhead? Can data-centric filtering match architectural defenses like SafeVLM without inference penalties? Does high-gradient selection cause safety basin collapse in VLMs? And do these improvements hold after strictly controlling for target length and image token density?"
- **Key Takeaway**: The 6 defining scientific questions (RQs 1–6) that will structure the final published paper.

---

## Slide 31: References
- **Slide Title**: *References*
- **What to Say**:
  > "Finally, our theoretical and empirical foundations are anchored in Bach et al. (2026), Ji et al.'s elasticity theory, Peng et al.'s VISAGE safety basins, and standard multimodal benchmarks including MM-SafetyBench, FigStep, and MathVista.
  > Thank you, Professor Le. I welcome your feedback, guidance, and questions on our proposed methodology."
- **Key Takeaway**: Academic grounding and respectful handoff to Q&A discussion.

---
