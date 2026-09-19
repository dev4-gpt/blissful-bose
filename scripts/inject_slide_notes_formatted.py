import os
from pptx import Presentation
from pptx.util import Pt

NOTES_DICT = {
    1: {
        "title": "Slide 1: Title Slide",
        "onscreen": [
            "Title: Continual Safety Alignment in Vision-Language Models via Multimodal Gradient-Based Sample Selection",
            "Subtitle: Extending Continual Safety Alignment (Bach et al., 2026) to Multimodal Architectures",
            "Metadata: Researcher: Aryaman Singh Dev | Advisor: Prof. Thao Minh Le | Penn State University"
        ],
        "script": "Good afternoon, Professor Le. Today, I am excited to present my research proposal on extending continual safety alignment to multimodal architectures. Specifically, this work builds directly on your paper, Bach et al., investigating whether gradient-based sample selection can prevent safety degradation in small vision-language models without requiring architectural modifications or expensive safety retraining. Over the next 25 minutes, I will walk you through the theoretical motivation, our multimodal gradient decomposition, our experimental protocol on Qwen2-VL, and the roadmap for empirical validation.",
        "qa": "Q: Why extend this to VLMs specifically?\nA: In the Limitations section of Bach et al., you explicitly noted that extending gradient-based selection to VLMs remains an open question. In VLMs, the visual channel introduces an entirely new, unaligned attack surface where image typography and visual jailbreaks bypass text safety filters completely.",
        "transition": "Let's begin by reviewing the core alignment drift problem established in your paper and how it manifests in multimodal models."
    },
    2: {
        "title": "Slide 2: Alignment Drift in Continual Fine-Tuning",
        "onscreen": [
            "1. Confirmed in Text LLMs (Bach et al., 2026): Benign fine-tuning erodes guardrails; high gradients drive elastic reversion; gradient clipping fails (ASR ~31% at clip=0.5).",
            "2. Research Question for VLMs: Does the same mechanism govern VLMs? Attackers bypass text guardrails via visual channels (Nie et al., 2024)."
        ],
        "script": "To establish the problem: in your paper with Bach et al., you demonstrated that benign fine-tuning erodes safety guardrails as a structural byproduct of gradient descent. High-gradient samples drive elastic reversion toward unaligned pretraining distributions. Crucially, standard remedies like gradient clipping fail because clipping merely shortens the step size while keeping the exact unaligned direction. In your Limitations section, you noted that extending gradient-based selection to VLMs is an open question. In VLMs, the problem is compounded: attackers exploit an unprotected visual channel—using image typography or visual jailbreaks—that completely bypasses text safety filters. Our central question is: does the same gradient-driven drift govern VLMs, and can data-centric median selection defend both text and visual safety channels?",
        "qa": "Q: Why not just use gradient clipping instead of sample selection?\nA: As demonstrated in Bach et al. Table 6, gradient clipping rescales ||g|| <= c, but preserves the exact direction of the update vector. If a sample's gradient points straight out of the safety basin, clipping simply takes smaller steps in that harmful direction—leaving ASR at ~31% even at aggressive clipping (c=0.5). Median selection removes the destabilizing samples entirely.",
        "transition": "To understand the physical mechanics behind this drift, we look at the elasticity framework."
    },
    3: {
        "title": "Slide 3: LLM Elasticity (Ji et al., 2024)",
        "onscreen": [
            "LLM Elasticity: Models act like coupled springs; massive pretraining distributions exert elastic restoring forces.",
            "Key Project Premise: Dataset size alone does not determine update direction; high-gradient samples act as heavy perturbations."
        ],
        "script": "To understand why fine-tuning degrades safety, we ground our work in the elasticity framework by Ji et al. Neural models act like coupled physical springs: pretraining establishes an elastic restoring force that pulls the model back toward its base, unaligned state when perturbed. Importantly, this project does not assume dataset size alone dictates this pull. Rather, high-gradient samples—which often reflect severe format or semantic mismatch—act as massive perturbations that stretch the model past its elastic limit, triggering rapid reversion to unaligned behavior.",
        "qa": "Q: How does elasticity apply across modalities?\nA: In VLMs, the restoring force exists in both the language backbone and the vision-language projector. Cross-modal tension stretches the projector weights, causing rapid forgetting of aligned refusal boundaries.",
        "transition": "Next, we examine the geometric shape of this safety boundary using VISAGE."
    },
    4: {
        "title": "Slide 4: VISAGE Safety Basin Geometry (Peng et al., 2024)",
        "onscreen": [
            "VISAGE: Volumetric Index for Safety Alignment Guided by Explanation.",
            "Safety Basin Geometry: Flat safety basin with sharp step-function collapse boundaries.",
            "1D vs 2D Rankings: Rankings are perfectly consistent (Llama 3 > Llama 2 > Mistral > Vicuna); 1D is a faster, computationally efficient metric."
        ],
        "script": "The geometry of this drift is formalized by Peng et al.'s VISAGE framework. Safety alignment does not occupy a broad, forgiving valley; it resides in a localized 'safety basin' with sharp, step-function boundaries. Moderate parameter updates allow the model to stay inside this basin. But large gradient updates push model weights directly over the ridge into unsafe territory, where safety collapses abruptly. A higher VISAGE score indicates a deeper, more robust basin. Furthermore, Peng et al. showed that 1D VISAGE rankings perfectly preserve 2D rankings, providing a computationally efficient metric to track safety basin retention during fine-tuning.",
        "qa": "Q: Why use 1D VISAGE instead of 2D?\nA: 1D VISAGE captures the exact same model safety ranking as 2D (Llama 3 > Llama 2 > Mistral > Vicuna) at a fraction of the compute cost, making it practical for tracking drift across continual training stages.",
        "transition": "Now let us examine how we translate the text evaluation suite of Bach et al. to the multimodal domain."
    },
    5: {
        "title": "Slide 5: Benchmark Suite: 1-to-1 Mapping",
        "onscreen": [
            "Safety / ASR: AdvBench, HarmBench -> MM-SafetyBench, FigStep, JailBreakV-28K.",
            "Truthfulness / Hallucination: TruthfulQA -> MMHal-Bench (open-ended), POPE (object probing).",
            "Downstream Task Sequence: Dolly, GSM8K, MedMCQA, SQuAD v2 -> LLaVA-Instruct-150K, MathVista, SLAKE/VQA-RAD, DocVQA."
        ],
        "script": "To evaluate this rigorously, we cannot rely on standard text benchmarks alone. On this slide, I have established a strict one-to-one mapping from every text evaluation in Bach et al. to its multimodal equivalent. For safety, AdvBench and HarmBench map to MM-SafetyBench, FigStep—which renders toxic text directly onto images—and JailBreakV-28K. For truthfulness, TruthfulQA maps to MMHal-Bench for open-ended hallucination and POPE for object probing. And for downstream tasks, Dolly, GSM8K, MedMCQA, and SQuAD map directly to LLaVA-Instruct, MathVista, SLAKE, and DocVQA. This ensures our evaluation mirrors the depth of the original text study.",
        "qa": "Q: Why both MMHal-Bench and POPE?\nA: They are complementary: MMHal-Bench measures open-ended generative hallucination severity, while POPE evaluates targeted binary object existence to isolate perceptual hallucination.",
        "transition": "Let us take a closer look at the attack surface that makes VLM evaluation uniquely challenging."
    },
    6: {
        "title": "Slide 6: Attack Surface & Multi-Channel Evaluation",
        "onscreen": [
            "Attack Surface Table (6 rows): Text channel, Image-text rendering (FigStep), Visual semantic content (MM-SafetyBench), Optimization transfer, Cross-modal conflict, Typographic distortion.",
            "Multi-channel reporting: Disaggregated ASR (ASR-text, ASR-visual, ASR-cross, aggregate)."
        ],
        "script": "A critical insight in VLMs is that reporting a single aggregate Attack Success Rate is dangerous and misleading. A model could maintain a 2% text ASR while its visual ASR collapses to 70%. As shown in this table, we decompose attacks across six distinct surfaces: raw text channels, OCR rendering, visual semantic content, optimization transfer, cross-modal conflicts, and typographic distortions. In our evaluation, we explicitly report separate metrics for ASR-text, ASR-visual, and ASR-cross to detect modality-specific alignment collapse.",
        "qa": "Q: What is cross-modal conflict?\nA: An attack where the image and text prompt are individually benign or ambiguous, but their cross-modal combination forms a harmful instruction that bypasses unimodal safety filters.",
        "transition": "Next, let's examine how prior works have attempted to defend VLMs, specifically SafeVLM."
    },
    7: {
        "title": "Slide 7: Related Multimodal Safety Approach — SafeVLM (Nie et al., 2024)",
        "onscreen": [
            "SafeVLM Architectural Approach: Adds Safety Projector, Safety Tokens, and Safety Head.",
            "Limitations: Requires complex 2-stage training, alters inference topology, and adds latency."
        ],
        "script": "To contextualize our contribution against state-of-the-art multimodal safety, we examine SafeVLM by Nie et al. SafeVLM addresses VLM vulnerability through an architectural approach. As shown in their paper, they freeze the base VLM and add three dedicated modules: a parallel Safety Projector, trainable Safety Tokens, and a multi-class Safety Head. This requires a complex two-stage training pipeline and permanently alters the model's inference topology. While effective, it represents an architectural defense, which motivated our search for a purely data-centric solution.",
        "qa": "Q: How does our approach differ from SafeVLM?\nA: SafeVLM changes the model architecture and adds runtime inference latency. Our approach is purely data-centric: we curate benign training data so standard fine-tuning naturally preserves safety, with zero architectural modifications and zero runtime overhead.",
        "transition": "Let's examine the empirical trade-offs reported in SafeVLM's results."
    },
    8: {
        "title": "Slide 8: SafeVLM Empirical Results & Over-Refusal Trade-offs (Tables 3 & 4)",
        "onscreen": [
            "Empirical evidence: Pretrained projector transmits visual features without safety alignment.",
            "LLaVA-v1.5-7B Results: AdvBench Vanilla ASR 6.45% -> 1.72%; Suffix Injection 78.27% -> 67.56%.",
            "Over-refusal Trade-off: XSTest Unsafe Rate dropped from 26.50% to 7.46% (safe instruction refusal risk); RTVLM 6.27 -> 8.26."
        ],
        "script": "Looking at SafeVLM's reported numbers in Tables 3 and 4, two key findings emerge. First, SafeVLM provides empirical proof that pre-trained visual projectors lack safety alignment—explaining why visual inputs easily jailbreak models. Second, their defense comes with substantial trade-offs: on XSTest, their safe instruction accuracy drops by over 14%, indicating severe over-refusal and false alarms. Furthermore, their custom safety head adds computational overhead during every inference step. Our data-centric hypothesis is that by filtering training samples at the gradient level, we can achieve competitive safety retention with zero architectural changes, zero latency penalty, and lower over-refusal.",
        "qa": "Q: Is over-refusal really a critical issue?\nA: Yes. A model that refuses benign requests (like asking how to slice an apple) has zero utility. We optimize the Pareto frontier of low ASR and high benign task utility.",
        "transition": "Now, let us enter our core methodology: how we decompose VLM gradients mathematically."
    },
    9: {
        "title": "Slide 9: VLM Extension: Parameter Formalization",
        "onscreen": [
            "Continual sequence of T multimodal tasks: visual inputs, text instructions, target responses.",
            "Parameter decomposition: Theta_train = (Theta_LoRA, Theta_projector).",
            "Frozen components: Vision encoder (ViT) and base language model."
        ],
        "script": "Now, let us turn to our core methodology. We formalize continual safety alignment across a sequence of T multimodal tasks, where each task contains visual inputs, text instructions, and target responses. In a VLM, the parameter space is decomposed into three distinct components: the vision encoder weights, the vision-language projector weights, and the language backbone weights. Under parameter-efficient fine-tuning, the vision encoder and base language model remain frozen, and optimization is restricted strictly to the language LoRA adapters and the cross-modal projector. Our goal is minimizing task loss while constraining the updated parameters within the multimodal safety basin.",
        "qa": "Q: Why freeze the vision encoder?\nA: Freezing the ViT preserves foundational visual representations, avoids representation collapse, and makes training computationally feasible on consumer/campus hardware.",
        "transition": "Why can't we simply take the full model gradient as was done in text LLMs? Slide 10 explains the dilemma."
    },
    10: {
        "title": "Slide 10: The Multimodal Dilemma: Why Naive Gradients Fail",
        "onscreen": [
            "Full-model backpropagation issue: ViT spatial pixel variance & hundreds of image patch tokens swamp the gradient norm.",
            "Decoupling parameter groups: Isolate alignment tension from visual reconstruction noise.",
            "Q&A Table: Loss tokens (assistant response only), ignored positions (image, prompt, system, padding)."
        ],
        "script": "The immediate challenge when extending Bach et al. to VLMs is that computing a naive gradient norm across the entire model fails. If you backpropagate through all parameters, the Vision Transformer contains high spatial pixel variance and hundreds of image patch tokens. This visual noise completely swamps the gradient norm. A sample could receive an enormous gradient simply because the image had high visual contrast or complex texture, rather than because it strained the model's alignment. We must decouple parameter groups.",
        "qa": "Q: What tokens generate the loss in our setup?\nA: Assistant-response tokens only. All image patch tokens and prompt tokens are masked to -100. G_i measures the sensitivity of trainable parameters strictly to the target response.",
        "transition": "Slide 11 breaks down the dual origins of gradient tension in VLMs."
    },
    11: {
        "title": "Slide 11: Disentangling Modality Tension",
        "onscreen": [
            "Format Mismatch vs. Visual Cross-Attention.",
            "Text LLM tension: Driven primarily by output format mismatch (short categorical vs verbose).",
            "VLM dual tension: 1. Format mismatch in text decoder; 2. Visual grounding conflict in connector."
        ],
        "script": "In text LLMs, high-gradient samples were primarily caused by output format mismatch—such as short categorical targets colliding with verbose conversational safety pretraining. In VLMs, high gradients arise from two fundamentally distinct sources: format mismatch in the text decoder, and visual grounding conflict in the connector, where dense visual tokens collide with language priors. To study this, we must track and attribute gradients separately across modalities.",
        "qa": "Q: How do you separate these two sources of tension?\nA: By computing gradients separately for language LoRA parameters (G_i^{(L)}) and projector parameters (G_i^{(P)}), as shown on the next slides.",
        "transition": "Let's look at the exact mathematical loss function and PyTorch masking rule on Slide 12."
    },
    12: {
        "title": "Slide 12: Strict Response-Only Label Masking (label = -100)",
        "onscreen": [
            "Loss Formula: L_i(I_i, x_i, y_i) = - sum_{t=1}^{T_y} log P(y_{i,t} | I_i, x_i, y_{i,<t}).",
            "PyTorch Masking: label = -100 for all image patch tokens, system prompts, user queries, and padding.",
            "Guaranteed Behavior: Gradients backpropagate strictly from response tokens; zero visual reconstruction loss."
        ],
        "script": "This brings us to a foundational technical requirement: strict label masking. As shown in the formula, our per-sample loss is calculated strictly over the assistant target response tokens, y_i. In PyTorch, we mask all non-target positions to -100: all image patch tokens, system instructions, user prompts, and padding tokens. Because cross-entropy loss ignores -100 positions, gradients backpropagate strictly from response tokens conditioned on the multimodal prefix. This guarantees that G_i measures the parameter change needed to generate the answer, completely preventing visual reconstruction loss from corrupting our selection.",
        "qa": "Q: Does label masking remove image reconstruction loss?\nA: Yes! There is zero reconstruction loss. Gradients backpropagate only from the supervised text tokens, so G_i strictly reflects response difficulty given the visual context.",
        "transition": "With response-only loss defined, Slide 13 introduces our 3 novel gradient attribution modes."
    },
    13: {
        "title": "Slide 13: Proposed Gradient Attribution Modes",
        "onscreen": [
            "Mode 1: Language-LoRA only: G_i^{(L)} = ||nabla_{Theta_LoRA} L_i||_2 (decoder formatting priors).",
            "Mode 2: Projector-only: G_i^{(P)} = ||nabla_{Theta_projector} L_i||_2 (cross-modal feature warping).",
            "Mode 3: Joint Multimodal Tension: G_i^{(J)} = sqrt((G_i^{(L)})^2 + lambda^2 (G_i^{(P)})^2)."
        ],
        "script": "With response-only loss established, we formulate our core scientific ablation: three distinct gradient attribution modes. First, Language-LoRA only, G_i^{(L)}, which isolates whether drift is driven by conversational response priors in the decoder. Second, Projector-only, G_i^{(P)}, which isolates cross-modal feature warping in the visual bridge. Third, Joint Multimodal Attribution, G_i^{(J)}, which combines both signals using a balancing scalar lambda. This ablation directly answers whether safety drift originates in the language backbone or the vision connector.",
        "qa": "Q: Which mode do you hypothesize will perform best?\nA: We hypothesize that Joint Attribution (G_i^{(J)}) will outperform unimodal modes because multimodal jailbreaks exploit both linguistic decoding and visual feature transmission.",
        "transition": "How do we balance language LoRA and projector gradients without parameter count bias? Slide 14 shows our solution."
    },
    14: {
        "title": "Slide 14: Balancing Scalar lambda & Median-Normalized Formulation",
        "onscreen": [
            "Balancing Scalar lambda formulation.",
            "Scale-invariant, median-normalized formula: G_i^{(J)} = sqrt((G_i^{(L)} / median(G^{(L)}))^2 + (G_i^{(P)} / median(G^{(P)}))^2).",
            "Eliminates parameter-count dominance: Both modules contribute equally to tension ranking."
        ],
        "script": "When combining language and projector gradients into G_i^{(J)}, a naive sum would allow the language LoRA adapters to dominate simply because they contain more parameters. To solve this, we propose a scale-invariant, median-normalized formulation, shown at the bottom of the slide. By dividing each module's gradient norm by its own empirical median across the dataset before squaring and summing, both the language decoder and the vision projector contribute equally to the joint tension metric.",
        "qa": "Q: Why use median normalization rather than mean or standard deviation?\nA: Gradients are heavy-tailed and contain extreme outliers. The empirical median is robust to outliers, ensuring stable scaling across diverse batches.",
        "transition": "Slide 15 shows the comprehensive per-sample diagnostics we log during this selection pass."
    },
    15: {
        "title": "Slide 15: VLM-Specific Diagnostic Logging",
        "onscreen": [
            "Per-sample diagnostics table: Target token count, prompt length, image token count, native image resolution, mean response loss, individual module gradients (G_i^{(L)}, G_i^{(P)})."
        ],
        "script": "To ensure our selection is methodologically sound, we log a comprehensive set of per-sample diagnostics during the selection pass: target token count, prompt length, image token count, native image resolution, mean response loss, and individual module gradients. This provides full observability and allows us to rule out potential confounders.",
        "qa": "Q: Why log image resolution?\nA: Higher resolution produces more image tokens in dynamic resolution architectures (like Qwen2-VL), which could affect cross-attention computation. Logging resolution allows us to verify whether gradient magnitude correlates with image complexity.",
        "transition": "Slide 16 addresses another potential confounder: response token length."
    },
    16: {
        "title": "Slide 16: Length Normalization & L2 Norm Foundations",
        "onscreen": [
            "Length normalization: G_tilde_i = G_i / sqrt(N_tokens).",
            "Observation: Longer benign answers naturally accumulate higher gradient norms across token loss steps.",
            "Random walk property: L2 norm of sum of N independent steps scales with sqrt(N)."
        ],
        "script": "Slide 16 details our length normalization mechanism. In auto-regressive generation, longer responses naturally accumulate higher gradient norms simply because you are summing across more token loss steps. A 300-word benign explanation could easily exhibit a larger gradient than a 2-word unsafe response. We implement length normalization by dividing the joint norm by the square root of the target token count. We will use this in sensitivity analysis to verify that our median selection captures semantic tension rather than verbosity.",
        "qa": "Q: Why sqrt(N) instead of N?\nA: Gradient vectors across tokens are approximately orthogonal random variables under stochastic gradient descent; the L2 norm of the sum of N independent steps scales with sqrt(N), following standard random walk theory.",
        "transition": "Slide 17 shows how these gradient scores translate into sample selection buckets."
    },
    17: {
        "title": "Slide 17: Total Norm vs. Selection Buckets",
        "onscreen": [
            "3-stage selection pipeline: 1. Loss pre-filter [mu_L +/- sigma_L]; 2. 20% closest to median gradient norm.",
            "Comparison buckets: Low-G_i, Moderate-G_i (median), High-G_i, Random 20%, Full Fine-Tuning."
        ],
        "script": "If we only tracked a single total norm, we would have no diagnostic visibility into which mechanism caused an outlier—whether it was a formatting clash, an ambiguous image, or an unusually long answer. As in Bach et al., our selection pipeline does not simply pick the lowest gradients. We first apply a loss pre-filter to eliminate noisy outliers, and then select the 20% of samples closest to the median gradient norm, comparing them against Low-G_i, High-G_i, Random, and Full fine-tuning.",
        "qa": "Q: Why select Moderate-G_i (median) rather than Low-G_i?\nA: Low-G_i samples represent trivial, low-information examples that the model already knows; training on Low-G_i preserves safety but stalls downstream task adaptation. Moderate-G_i strikes the optimal Pareto trade-off: sufficient gradient signal for new task acquisition while avoiding the extreme-gradient outliers that breach safety basins.",
        "transition": "Now let us move to our experimental roadmap: the 4-stage continual task sequence on Slide 18."
    },
    18: {
        "title": "Slide 18: Execution Plan: 4-Stage Continual Task Sequence",
        "onscreen": [
            "Stage 1: LLaVA-Instruct-150K (general visual instruction).",
            "Stage 2: MathVista (visual math reasoning).",
            "Stage 3: SLAKE (14k training) / VQA-RAD (held-out medical evaluation).",
            "Stage 4: DocVQA (dense document OCR)."
        ],
        "script": "On Slide 18, we outline our continual training sequence. We proceed through four diverse stages: general visual instruction following on LLaVA-150K; visual math reasoning on MathVista; clinical image understanding on SLAKE; and dense document OCR on DocVQA. Crucially, for clinical VQA, we use SLAKE's 14,000 samples for training, and preserve VQA-RAD as an untouched, out-of-domain benchmark to test true generalization. For MathVista, we strictly separate the training split from held-out evaluation.",
        "qa": "Q: Why separate SLAKE and VQA-RAD?\nA: Using SLAKE for training and VQA-RAD exclusively for evaluation ensures that our medical domain evaluation measures true zero-shot cross-dataset generalization rather than memorized dataset artifacts.",
        "transition": "Slide 19 details our pragmatic compute strategy: moving from a Colab pilot to the PSU cluster."
    },
    19: {
        "title": "Slide 19: Implementation Plan: Two-Phase Roadmap",
        "onscreen": [
            "Phase 1: Rapid pilot on Google Colab T4 GPU (Qwen2-VL-2B in 4-bit QLoRA, 1,000 samples). Tests core hypothesis on FigStep & MM-SafetyBench.",
            "Phase 2: Scale to PSU Campus Cluster across 3 seeds on full 4-task sequence, complete benchmark suite, and attribution ablations."
        ],
        "script": "Our experimental roadmap is divided into two pragmatic phases. Phase 1 is a rapid pilot on Google Colab using a single T4 GPU. We use Qwen2-VL-2B in 4-bit QLoRA on a 1,000-sample subset of LLaVA-Instruct. This pilot will quickly test our core hypothesis: does High-G_i induce higher visual ASR than Moderate-G_i on FigStep and MM-SafetyBench? Once validated, Phase 2 scales to the PSU Campus Cluster across 3 random seeds, running the full 4-task sequence, complete benchmark suite, and full attribution ablation.",
        "qa": "Q: What is the exact deliverable of Phase 1?\nA: A 2x2 matrix: Moderate vs High G_i evaluated on FigStep and MM-SafetyBench. If High-G_i causes significantly higher ASR than Moderate-G_i, the core hypothesis is confirmed before running large cluster jobs.",
        "transition": "Slide 20 outlines our model choice, LoRA setup, and concrete success criteria."
    },
    20: {
        "title": "Slide 20: Practical Setup & Hyperparameters",
        "onscreen": [
            "Model: Qwen2-VL-2B-Instruct (matches Qwen2.5/Qwen3 base lineage of Bach et al.).",
            "LoRA: Language backbone q, k, v, o, gate, up, down (r=16, alpha=32).",
            "Success Criteria: Moderate-G_i preserves lower ASR than Full/Random while matching task accuracy."
        ],
        "script": "For model selection, Qwen2-VL-2B-Instruct is ideal: it belongs to the exact Qwen architectural family analyzed in Bach et al., ensuring theoretical continuity while fitting into consumer hardware. We target all attention projections and MLP layers in the language backbone with rank 16 and alpha 32. Our success criterion in Phase 1 is confirming that Moderate-G_i preserves lower ASR than standard or random fine-tuning while matching downstream task accuracy.",
        "qa": "Q: Why Qwen2-VL-2B instead of LLaVA-1.5-7B?\nA: Qwen2-VL has native dynamic resolution, a modern vision architecture, strong multilingual/multimodal benchmarks, and matches the Qwen2.5/Qwen3 base lineage used in Bach et al.",
        "transition": "Next, let us examine how we evaluate multimodal safety accurately, starting with Slide 21."
    },
    21: {
        "title": "Slide 21: Safety Judges for VLMs: The Visual Blindspot",
        "onscreen": [
            "Limitations of text-only judges: Cannot see images; cannot detect FigStep image-rendered attacks.",
            "Solution: Judge model evaluates generated response against the intended harmful query embedded in the prompt/image, not just raw text prompt.",
            "Artifact logging: Preserve image, intended instruction, VLM response, judge decision, OCR verification."
        ],
        "script": "Evaluating safety in VLMs introduces a major dilemma: text-only judges like Llama-Guard are blind to images. In a FigStep attack, the harmful instruction is rendered visually inside the image while the text prompt is completely benign. If a text judge only inspects the prompt and answer, it cannot determine whether the model obeyed a harmful visual directive. Therefore, for visual jailbreaks, our judge must evaluate the generated response against the intended harmful instruction embedded in the image, rather than the raw text prompt alone.",
        "qa": "Q: Are you using an automated VLM judge or text judge?\nA: We use a text judge (Llama-Guard-3 / GPT-4o-mini), but we explicitly feed it the decoded reference harmful instruction from the image metadata, not just the benign prompt.",
        "transition": "Slide 22 shows the structured evaluation record schema that enables this."
    },
    22: {
        "title": "Slide 22: Structured Record Schema for Evaluators",
        "onscreen": [
            "Schema: attack_category, image, decoded_or_reference_harmful_instruction, text_prompt, vlm_response, judge_label.",
            "Stratified manual audit: Fixed sample to verify automated labels across attack categories."
        ],
        "script": "To implement this cleanly, we feed our automated evaluator a standardized record containing: the attack category, the image, the decoded reference harmful instruction, the prompt, and the VLM's response. We then supplement automated evaluation with a stratified manual audit across attack categories to empirically calibrate judge accuracy.",
        "qa": "Q: How many samples will you manually audit?\nA: A fixed stratified sample of 100 responses per attack category (500 total), measuring Cohen's Kappa between the automated judge and human annotators.",
        "transition": "Slide 23 details our two-stage evaluation protocol and over-refusal monitoring."
    },
    23: {
        "title": "Slide 23: Two-Stage Safety Evaluation Protocol",
        "onscreen": [
            "Stage 1: Automatic judge for refusal/compliance; store raw responses.",
            "Refusal Quality: Pair safety with capability; Safety-Utility tradeoff = (Low ASR, High TaskScore).",
            "Stage 2: Manual audit for partial compliance, recognition, and hallucination."
        ],
        "script": "Slide 23 summarizes our two-stage safety evaluation. Stage 1 executes automated classification of refusal versus compliance, logging raw text responses for every attack. Importantly, we pair safety with utility: a model that refuses every visual question has low ASR but zero utility. We report the complete Pareto frontier: Low ASR paired with High Task Score. Stage 2 executes manual spot-checks to inspect partial compliance and visual hallucinations.",
        "qa": "Q: What constitutes partial compliance?\nA: When a model gives a generic refusal but still provides actionable preliminary steps (e.g., 'I cannot give the recipe, but here are the ingredients'). Our manual audit specifically checks for this.",
        "transition": "Slide 24 formalizes our threat model and attack surface taxonomy."
    },
    24: {
        "title": "Slide 24: Threat Model & Attack Surface Breakdown",
        "onscreen": [
            "Threat Model: Test-time adversary providing malicious multimodal inputs without modifying weights.",
            "Input attack vectors: Harmful text, harmful image instruction, benign text + malicious image, benign image + harmful text, typography/screenshots, jailbreak multimodal prompts.",
            "Separation: Isolate visual vs textual channels to detect modality-specific alignment collapse."
        ],
        "script": "Slide 24 formalizes our threat model. We assume a test-time adversary who provides malicious multimodal inputs without modifying model weights. The table systematically decomposes the attack matrix: text-only prompts test decoder safety; text rendered in images tests the visual OCR bypass; harmful images test visual semantic safety; benign images with harmful prompts test distraction; and joint ambiguous pairs test multimodal synergy.",
        "qa": "Q: Do you consider adversarial perturbation attacks (e.g. PGD on pixels)?\nA: While continuous gradient perturbations exist, jailbreaks using semantic image rendering (FigStep) and real-world malicious imagery are far more prevalent and realistic in deployment.",
        "transition": "Slide 25 provides our multi-dimensional observability scorecard."
    },
    25: {
        "title": "Slide 25: Comprehensive Observability Checklist",
        "onscreen": [
            "6 Core Dimensions: Multimodal safety, Refusal quality / over-refusal, Truthfulness & hallucination (MMHal-Bench, POPE), Downstream task accuracy, VLM safety basin retention (VISAGE), Computational cost."
        ],
        "script": "Slide 25 provides our multi-dimensional observability checklist. Beyond text and visual ASR, we track benign over-refusal on clean visual questions, open-ended hallucination via MMHal-Bench, object hallucination via POPE, task accuracy across all 4 stages, volumetric safety basin retention, and computational training cost.",
        "qa": "Q: How will you measure safety basin retention?\nA: By perturbing the trained LoRA and projector weights with Gaussian noise and tracking how rapidly multimodal ASR increases.",
        "transition": "Slide 26 introduces the mathematical formalization of our continual learning metrics."
    },
    26: {
        "title": "Slide 26: Continual Learning Dynamics: Formal Metrics",
        "onscreen": [
            "Task performance matrix: R_{t,k} (performance on task k after training on task t).",
            "Backward Transfer: BWT = (1 / (T-1)) sum_{i=1}^{T-1} (R_{T,i} - R_{i,i}).",
            "Forgetting Measure: FM_k = max_{l in {1...T-1}} R_{l,k} - R_{T,k}.",
            "Pairwise Task Interference: I_{j -> k} = R_{j,k} - R_{j-1,k}."
        ],
        "script": "On Slide 26, we formalize our continual learning metrics. We maintain the complete task performance matrix, R_{t,k}, tracking performance on past tasks after training on each new task. From this matrix, we compute Backward Transfer to quantify retention, Forgetting Measure to capture peak-to-final accuracy drops, and pairwise Task Interference, I_{j -> k}, which isolates exactly how learning task j alters performance on earlier task k.",
        "qa": "Q: Why measure pairwise task interference?\nA: BWT only gives an aggregate average. Pairwise interference reveals if specific task transitions—such as moving from math diagrams to clinical scans—are particularly destructive to safety.",
        "transition": "Slide 27 presents our full mechanism diagnostics table."
    },
    27: {
        "title": "Slide 27: VLM Specific Mechanism Diagnostics",
        "onscreen": [
            "Diagnostics Table (9 rows): Language gradient G_i^{(L)}, Projector gradient G_i^{(P)}, Joint gradient G_i^{(J)}, Loss L_i, Target token length N_tokens, Prompt length, Image token count, Image resolution, Parameter displacement ||theta_t - theta_0||_2."
        ],
        "script": "Slide 27 presents our diagnostics table. For every experiment, we record language LoRA drift, projector drift, joint norms, token lengths, image resolution, and parameter distance from the aligned checkpoint theta_0. This allows us to map sample selection directly to weight trajectory shifts in parameter space.",
        "qa": "Q: What does parameter displacement tell us?\nA: It directly tests Ji et al.'s elasticity theory: if Moderate-G_i remains closer to theta_0 while achieving high task performance, it proves that safety retention is achieved by minimizing unnecessary weight displacement.",
        "transition": "Slide 28 presents our 13-condition experimental control grid."
    },
    28: {
        "title": "Slide 28: VLM Control Conditions & Baselines Grid",
        "onscreen": [
            "13 Conditions: Aligned theta_0, Standard full fine-tuning, Random 20%, Low-G_i 20%, Moderate-G_i 20% (LM-LoRA), Moderate-G_i 20% (Projector), Moderate-G_i 20% (Joint), High-G_i 20%, Length-norm Moderate-G_i, Gradient Clipping, EWC, Replay with safety data, Full + Safety Co-training."
        ],
        "script": "Slide 28 is our experimental control grid, spanning 13 conditions. Every condition answers a distinct scientific question: Aligned theta_0 sets the ceiling; Standard Fine-Tuning measures unconstrained drift; Random 20% controls for sample count; Low and High-G_i test the extreme ends of the spectrum; Gradient Clipping tests whether magnitude control suffices; EWC tests generic forgetting regularizers; and our three attribution modes isolate the modality responsible for drift.",
        "qa": "Q: Why is Random 20% an essential baseline?\nA: Because if Moderate 20% outperforms Full Fine-Tuning, a reviewer might claim it's simply because training on fewer samples causes less drift. Comparing Moderate 20% directly against Random 20% proves the benefit is driven by gradient selection, not sample budget.",
        "transition": "Slide 29 provides the unified evaluation matrix."
    },
    29: {
        "title": "Slide 29: Complete Evaluation Matrix",
        "onscreen": [
            "Unified Matrix: Maps 7 dimensions (Multimodal safety, Refusal quality, Robustness, Hallucination, Task performance, Continual learning, Compute efficiency) to metrics and exact measurement tools."
        ],
        "script": "Slide 29 provides our complete evaluation scorecard, mapping every metric—from multi-channel ASR to judge/manual agreement and GPU wall-clock training efficiency—to its precise measurement methodology.",
        "qa": "Q: What is your primary headline metric?\nA: The Pareto frontier of Average Continual ASR (lower is better) versus Average Downstream Accuracy (higher is better) across the 4 stages.",
        "transition": "Finally, Slide 30 synthesizes our proposal into 6 fundamental research questions."
    },
    30: {
        "title": "Slide 30: Summary & 6 Core Research Questions",
        "onscreen": [
            "Text LLM findings vs VLM Open Questions.",
            "6 Research Questions: RQ1 (Multi-channel safety), RQ2 (LoRA vs Projector attribution), RQ3 (Forgetting without overhead), RQ4 (Data-centric vs SafeVLM), RQ5 (Safety basin collapse), RQ6 (Confounder invariance)."
        ],
        "script": "To summarize: in text LLMs, we know high-gradient samples drive elastic reversion out of safety basins, and median filtering preserves alignment without extra safety data. In this research, we are answering six fundamental questions: Does multimodal gradient selection protect both text and visual jailbreaks? Does tension concentrate in the language LoRA weights or the cross-modal projector? Can we eliminate forgetting with zero architectural overhead? Can data-centric filtering match architectural defenses like SafeVLM without inference penalties? Does high-gradient selection cause safety basin collapse in VLMs? And do these improvements hold after strictly controlling for target length and image token density?",
        "qa": "Q: Which of these 6 RQs is the most novel?\nA: RQ2 (LoRA vs Projector attribution) and RQ4 (Data-centric filtering vs Architectural defenses like SafeVLM). No prior work has investigated gradient attribution across multimodal components for safety retention.",
        "transition": "Slide 31 lists our core academic references."
    },
    31: {
        "title": "Slide 31: References",
        "onscreen": [
            "Primary foundations: Bach et al. (arXiv:2604.17215), Ji et al. (arXiv:2406.06144), Peng et al. (arXiv:2405.17374).",
            "Multimodal SOTA & Benchmarks: MM-SafetyBench, FigStep, SaLORA, LARF, EWC, VLGuard, LLaVA, MathVista."
        ],
        "script": "Finally, our theoretical and empirical foundations are anchored in Bach et al. (2026), Ji et al.'s elasticity theory, Peng et al.'s VISAGE safety basins, and standard multimodal benchmarks including MM-SafetyBench, FigStep, and MathVista. Thank you, Professor Le. I welcome your feedback, guidance, and questions on our proposed methodology.",
        "qa": "Q: Where do we start on Monday?\nA: With the Phase 1 Colab T4 prototype: running the 1,000-sample gradient pass on Qwen2-VL-2B to verify the gradient distribution and test Moderate vs High G_i on FigStep.",
        "transition": "End of presentation. Open floor for advisor Q&A."
    }
}

def inject_all_formatted_notes():
    prs = Presentation('Presentation1.pptx')
    assert len(prs.slides) == 31, f"Expected 31 slides, found {len(prs.slides)}"
    
    for slide_idx, data in NOTES_DICT.items():
        slide = prs.slides[slide_idx - 1]
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.clear()
        
        # 1. Slide Title Header
        p_title = tf.paragraphs[0]
        p_title.text = f"=== {data['title']} ==="
        p_title.font.bold = True
        p_title.font.size = Pt(14)
        
        # 2. What's on the Slide (Context reminder)
        p_ctx_hdr = tf.add_paragraph()
        p_ctx_hdr.text = "\n[WHAT PROF. LE SEES ON SCREEN]:"
        p_ctx_hdr.font.bold = True
        p_ctx_hdr.font.size = Pt(11)
        
        for item in data['onscreen']:
            p_item = tf.add_paragraph()
            p_item.text = f"• {item}"
            p_item.font.size = Pt(10)
        
        # 3. Spoken Script
        p_script_hdr = tf.add_paragraph()
        p_script_hdr.text = "\n[SPOKEN SCRIPT - READ ALOUD]:"
        p_script_hdr.font.bold = True
        p_script_hdr.font.size = Pt(12)
        
        p_script = tf.add_paragraph()
        p_script.text = f"\"{data['script']}\""
        p_script.font.size = Pt(11)
        
        # 4. Anticipated Q&A Defense
        p_qa_hdr = tf.add_paragraph()
        p_qa_hdr.text = "\n[ANTICIPATED QUESTION & DEFENSE]:"
        p_qa_hdr.font.bold = True
        p_qa_hdr.font.size = Pt(11)
        
        p_qa = tf.add_paragraph()
        p_qa.text = data['qa']
        p_qa.font.size = Pt(10)
        
        # 5. Transition Cue
        p_trans_hdr = tf.add_paragraph()
        p_trans_hdr.text = "\n[TRANSITION TO NEXT SLIDE]:"
        p_trans_hdr.font.bold = True
        p_trans_hdr.font.size = Pt(11)
        
        p_trans = tf.add_paragraph()
        p_trans.text = data['transition']
        p_trans.font.size = Pt(10)
        
        print(f"Formatted and injected notes for Slide {slide_idx}")
        
    prs.save('Presentation1.pptx')
    print("\n[SUCCESS] Successfully saved all 31 formatted slide notes directly into Presentation1.pptx!")

if __name__ == '__main__':
    inject_all_formatted_notes()
