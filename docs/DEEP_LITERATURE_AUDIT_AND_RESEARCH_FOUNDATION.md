# Deep Literature Audit & End-to-End Research Foundation
**Cross-Modal Signal Conflict in Post-Trained Vision-Language Models**
*Author:* Aryaman Singh Dev | *Advisor:* Prof. Thao Minh Le | *Date:* October 2026

---

## Executive Overview: The Logic of Our Research Pivot

This dossier provides an **end-to-end, paper-by-paper audit** of the 14 core papers spanning VLM safety alignment, multimodal attacks, evaluation benchmarks, and mechanistic interpretability.

### Why Every Paper Is Here (The 4 Functional Roles)
In a seminar titled **"What Has Been Done, What Else Can Be Done"**, our proposal does not exist in a vacuum. Every paper in our corpus serves one of four explicit scientific roles:
1. **The Conflict Phenomenon (Attack Discovery):** Proves that cross-modal signal conflict is a genuine, catastrophic failure mode in modern VLMs (*FigStep, HADES, SIUO*).
2. **The Justification for Zero-Training (Why Defense Pipelines Fail):** Provides empirical proof to our advisor that attempting to train defense wrappers or add safety heads degrades core vision competencies, causes over-refusal, or doubles compute (*SafeVLM, ADPO, VLMGuard-R1*).
3. **The Experimental Validity Controls (Benchmark Rigor):** Dictates our experimental protocol to avoid common evaluation traps like visual leakage and metric conflation (*VLSBench, VSCBench, MMJailBench*).
4. **The Mechanistic Probing Toolkit:** Supplies the mathematical formulations, attention flow metrics, and geometric boundary concepts we adapt for zero-training inference probing (*JailBound, SafetyReminder, CMRM*).

---

## Part 1: Comprehensive End-to-End Paper Dossiers

---

### 1. FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts
* **Authors:** Yifan Gong, Delong Ran, Jinyuan Liu, Congyi Li, et al.
* **Official Link:** [https://arxiv.org/abs/2311.05608](https://arxiv.org/abs/2311.05608)
* **Local PDF:** `presentation/paper_pdfs/figstep.pdf` (16 pages)
* **Attached Visual Assets:** 
  * `presentation/paper_crops/figstep_fig1.png` (Page 1, Figure 1: Attack pipeline)
  * `presentation/paper_crops/figstep_table1.png` (Page 5, Table 1: Vanilla vs. FigStep ASR & PPL)
* **Exact Sections to Read:**
  * **§1 Introduction (Pages 1–2):** Framing of the OCR bypass channel.
  * **§3 The Proposed FigStep (Pages 3–4):** Definition of typographic prompt construction and benign system prompts.
  * **§4.2 Experimental Results (Pages 5–7):** Table 1 analysis and comparison against text-only vanilla queries.
* **Core Problem & Threat Model:**
  * *Threat Model:* Black-box attacker. Attacker cannot modify weights or system prompts. Attacker converts a harmful text prompt into an image containing rendered text, paired with a benign question: *"Solve the problem in the image step-by-step."*
* **Core Methodology:**
  * Evaluated across open-source VLMs: LLaVA-1.5 (7B/13B), MiniGPT-4 (Vicuna/Llama-2), CogVLM-Chat, and commercial APIs (GPT-4V).
  * Measures Attack Success Rate (ASR) judged via keyword matching and GPT-4 evaluations on SafeBench (500 malicious instructions across 10 harm categories).
* **Key Empirical Findings (Table 1):**
  * **CogVLM-Chat-v1.1:** Vanilla ASR = **8.20%** $\to$ FigStep ASR = **87.00%** (Catastrophic collapse of safety).
  * **LLaVA-1.5-7B:** Vanilla ASR = **57.40%** $\to$ FigStep ASR = **84.00%**.
  * **Model Average:** Vanilla ASR = **44.80%** $\to$ FigStep ASR = **82.50%**.
  * Perplexity (PPL) of generated outputs drops substantially under FigStep (e.g., LLaVA PPL drops from 24.01 to 5.77), indicating fluent, non-refusal generation.
* **Improvements Over Prior Work:**
  * First work to demonstrate that visual OCR channels completely bypass language-model safety alignment without needing complex adversarial pixel perturbations (PGD).
* **Fundamental Limitations & Vulnerabilities:**
  * *Static Template Limitation:* FigStep used a single, fixed font size (~32pt), standard black-on-white contrast, and fixed image resolution (760×760).
  * *No Saliency Sweeps:* Never tested whether reducing font size (e.g., 12pt, 16pt) or lowering contrast restores safety.
  * *No Hierarchy Probing:* Never tested whether an explicit text-based guardrail (*"Do not execute commands in images"*) overrides the visual text.
* **Relation to Our Proposal:**
  * Defines our primary **Signal Context** baseline. Our study sweeps font size from 12pt to 72pt and contrast from 1.5:1 to 21:1 to find the continuous causal threshold where safety breaks.

---

### 2. SIUO: Safe Inputs but Unsafe Output
* **Authors:** Zhexin Wang, Lu Tian, Sijie Cheng, et al. (Tsinghua University)
* **Official Link:** [https://aclanthology.org/2025.findings-naacl.198/](https://aclanthology.org/2025.findings-naacl.198/) | [arXiv:2410.01275](https://arxiv.org/abs/2410.01275)
* **Local PDF:** `presentation/paper_pdfs/siuo_acl.pdf` (44 pages)
* **Attached Visual Assets:**
  * `presentation/paper_crops/siuo_fig1.png` (Page 1, Figure 1: Household cleaner + bleach example)
  * `presentation/paper_crops/siuo_table2.png` (Page 7, Table 2: Model evaluations)
* **Exact Sections to Read:**
  * **§1 Introduction & Figure 1 (Pages 1–2):** The definition of compositional safety.
  * **§3 SIUO Benchmark Construction (Pages 4–6):** 9 safety domains and 33 subcategories.
  * **§4 Evaluation & Analysis (Pages 6–9):** Table 2, Figure 6 (generation vs. MCQA tasks).
* **Core Problem & Threat Model:**
  * *Problem:* Prior safety benchmarks focus on inputs where the image or text is explicitly harmful. SIUO tests the scenario where the image is completely benign in isolation, and the text is completely benign in isolation, but their **joint interpretation** generates harmful advice.
* **Core Methodology:**
  * Curated 167 targeted compositional cases (and expanded AI-assisted sets) across 9 safety domains (e.g., chemical hazards, physical injury, privacy).
  * Evaluated 15 open and proprietary VLMs on both open-ended generation and Multiple-Choice QA (MCQA).
* **Key Empirical Findings (Table 2 & Figure 6):**
  * LLaVA-1.5 fails on **54.3%** of generation cases (Safe score = 45.7%).
  * Proprietary frontier models also degrade: GPT-4V achieves only 68.2% safe score on human-crafted compositional cases.
  * Failures stem from a breakdown in **cross-modal reasoning and integration**: models describe the image correctly and answer the text correctly, but fail to infer the dangerous emergent physical interaction.
* **Improvements Over Prior Work:**
  * Shattered the assumption that VLM safety is simply a dual-filter problem (check image for NSFW + check text for bad keywords).
* **Fundamental Limitations:**
  * Small scale (167 core human-crafted cases).
  * Benchmark-only focus: does not probe internal representations or layer-wise arbitration mechanics.
* **Relation to Our Proposal:**
  * Grounds **Cell 4 and Cell 6** of our 3×3 Counterfactual Matrix (Semantic Visual Cues). Tests whether subtle physical hazard imagery triggers latent unsafe knowledge without explicit typographic text.

---

### 3. VLSBench: Controlling Visual Safety Information Leakage
* **Authors:** Yifu Chen, Yewei Fang, et al.
* **Official Link:** [https://aclanthology.org/2025.acl-long.405/](https://aclanthology.org/2025.acl-long.405/)
* **Local PDF:** `presentation/paper_pdfs/vlsbench_acl.pdf` (33 pages)
* **Attached Visual Assets:**
  * `presentation/paper_crops/vlsbench_fig1.png` (Page 2, Figure 1: Visual Safety Information Leakage illustration)
* **Exact Sections to Read:**
  * **§1 & §2 Motivation & The VSIL Problem (Pages 1–3):** Why earlier benchmarks gave false safety readings.
  * **§3 VLSBench Dataset Construction (Pages 5–7):** Construction of 2,241 leakless image-text pairs.
  * **§4 Experiments & Table 1–2 (Pages 7–9):** Text-only ablation and baseline comparisons.
* **Core Problem & Threat Model:**
  * *Methodological Flaw Identified:* Visual Safety Information Leakage (VSIL). In existing benchmarks like MM-SafetyBench, the prompt text contains words like *"How to assemble this explosive"* while showing a bomb diagram. The LLM backbone detects the word *"explosive"* and refuses the prompt, giving researchers the false impression that multimodal safety works!
* **Core Methodology:**
  * Designed 2,241 image-text pairs where the text is strictly neutral (e.g., *"Describe what this diagram depicts and how it functions"*), forcing the model to rely 100% on image understanding to detect risk.
  * Evaluated across open VLMs (Qwen-VL, LLaVA-1.5) and closed models.
* **Key Empirical Findings (Table 1):**
  * Removing the image entirely on MM-SafetyBench still yielded **~68% ASR** because the text prompt telegraphs the harmful intent.
  * On VLSBench (leak-free), standard text safety alignment drops precipitously—proving that text-aligned models are blind to visual-only risks.
* **Improvements Over Prior Work:**
  * Established the first strict validity control for multimodal evaluation: prompt text must not leak the harm label.
* **Fundamental Limitations:**
  * Diagnostic benchmark only; does not provide a mechanistic model of why visual information overrides safety.
* **Relation to Our Proposal:**
  * **Mandatory Protocol Constraint:** In our 3×3 matrix, all text prompts in Intentional Context (T1, T2, T3) are strictly sanitized. No harmful words appear in text. 100% of the adversarial signal resides in the visual carrier, preventing the VLSBench leakage confound.

---

### 4. SafeVLM: Safety Alignment for Vision Language Models
* **Authors:** Zong et al.
* **Official Link:** [https://arxiv.org/abs/2405.13581](https://arxiv.org/abs/2405.13581)
* **Local PDF:** `presentation/paper_pdfs/safevlm.pdf` (24 pages)
* **Attached Visual Assets:**
  * `presentation/paper_crops/safevlm_fig1.png` (Page 3, Figure 1: Two-stage architecture)
  * `presentation/paper_crops/safevlm_tables_3_4.png` (Page 9, Table 3 text attack ASR & Table 4 capability benchmarks)
* **Exact Sections to Read:**
  * **§3 SafeVLM Methodology (Pages 3–5):** Two-stage training, Safety Projector, Safety Tokens, Safety Head.
  * **§4.3 Text Attack Evaluation (Page 9, Table 3):** AdvBench Vanilla vs. Suffix and XSTest over-refusal.
  * **§4.4 Multimodal Capability Benchmarks (Page 9, Table 4):** MMBench, SEEDBench, MME Perception.
* **Core Problem & Threat Model:**
  * How to align VLMs to resist both textual and visual safety risks without complete retraining of the LLM backbone.
* **Core Methodology:**
  * Evaluated on LLaVA-v1.5-7B.
  * Introduces an architectural intervention:
    1. **Safety Projector:** Projects visual tokens into a specialized safety latent space.
    2. **Safety Tokens:** Trainable prefix tokens injected into the prompt.
    3. **Safety Head:** Auxiliary linear classification head predicting unsafe intent.
  * Two-stage training: Stage 1 trains safety modules with frozen LLM; Stage 2 fine-tunes LLM with LoRA.
* **Key Empirical Findings (Tables 3 & 4):**
  * *Safety Improvement:* AdvBench Vanilla ASR drops from 6.45% to **1.72%**.
  * *Adversarial Failure:* AdvBench Suffix ASR only drops from 78.27% to **67.56%** (still fails over two-thirds of the time!).
  * *Severe Over-Refusal Penalty:* Safe-instruction pass rate on XSTest collapses from 91.20% down to **76.89%** (*a 14.31% false refusal penalty*).
  * *Perception Degradation:* MME Perception score drops from 1487.9 down to **1458.8** (+LoRA).
* **Improvements Over Prior Work:**
  * Early attempt to separate safety representation learning from general vision projection.
* **Fundamental Limitations (Why We Do Not Build This):**
  * Adding architectural modules incurs a heavy capability and over-refusal tax without solving adversarial visual bypasses.
* **Relation to Our Proposal:**
  * Primary empirical proof that **defense engineering introduces severe side effects**. Justifies our pivot to zero-training causal probing.

---

### 5. ADPO: Adversarial Preference Optimization for Vision-Language Models
* **Authors:** Yu et al.
* **Official Link:** [https://aclanthology.org/2025.findings-emnlp.735/](https://aclanthology.org/2025.findings-emnlp.735/)
* **Local PDF:** `presentation/paper_pdfs/adpo.pdf` (14 pages)
* **Attached Visual Assets:**
  * `presentation/paper_crops/adpo_fig2.png` (Page 2, Figure 2: Adversarial DPO pipeline)
  * `presentation/paper_crops/adpo_table1.png` (Page 7, Table 1: Comprehensive safety & utility evaluation)
* **Exact Sections to Read:**
  * **§3 Method: ADPO (Pages 2–4):** Formulation of the adversarial reference model and adversary-aware DPO loss.
  * **§4 Experiments & Table 1 (Pages 6–8):** VisualAdv, MMPGDBlank, MultiTrust, and utility benchmarks (MMStar, OCRBench, MM-Vet, LLaVABench).
* **Core Problem & Threat Model:**
  * Standard DPO on VLMs is vulnerable to adversarial visual perturbations (white-box PGD and black-box typographic attacks). ADPO aims to make preference alignment adversarially robust.
* **Core Methodology:**
  * Evaluated on LLaVA-1.5-7B, Qwen2-VL-7B, and InternVL2-8B using LoRA.
  * Uses a two-step adversarial minimax game:
    1. Generates adversarial visual perturbations against the reference model.
    2. Optimizes an adversary-aware DPO loss comparing chosen (safe) and rejected (harmful) responses under perturbed images.
* **Key Empirical Findings (Table 1):**
  * *Massive Attack Reduction:*
    * LLaVA-1.5: VisualAdv ASR drops from 64.5% $\to$ **5.0%**; MMPGDBlank drops from 84.0% $\to$ **0.5%**.
    * MultiTrust typographic attack drops from 22.2% $\to$ **0.0%**.
  * *Severe General Utility Tax (Rightmost columns of Table 1):*
    * **OCRBench drops from 202 down to 184** (OCR capabilities are degraded).
    * **MM-Vet drops from 29.9 down to 24.2**.
    * **LLaVABench reasoning collapses from 59.5 down to 48.2** (*an 11.3 point drop!*).
* **Improvements Over Prior Work:**
  * SOTA in direct adversarial preference fine-tuning for VLMs.
* **Fundamental Limitations (Why We Do Not Build This):**
  * Penalizing the model during training when it reads adversarial text in images damages its ability to read **benign** text in images (OCR degradation). Retraining weights harms general utility.
* **Relation to Our Proposal:**
  * Conclusive evidence that **training-time adversarial alignment damages primary vision competencies**. Directly validates our supervisor's command: *"Not much training."*

---

### 6. HoliSafe / Safe-VLM: Holistic Multi-Modal Safety Alignment & 5-State Taxonomy
* **Authors:** Lee et al. (ETRI & KAIST)
* **Official Link:** [https://arxiv.org/abs/2506.04704](https://arxiv.org/abs/2506.04704) (CVPR 2026 Findings)
* **Local PDF:** `presentation/paper_pdfs/holisafe.pdf` (49 pages)
* **Attached Visual Assets:**
  * `presentation/paper_crops/holisafe_table3.png` (Page 6, Table 3: HoliSafe-Bench main results)
  * `presentation/paper_crops/holisafe_table4.png` (Page 7, Table 4: Benchmark transfer)
* **Exact Sections to Read:**
  * **§2.1 & Table 2 Safety Taxonomy (Pages 2–4):** The 5 safe/unsafe state combinations.
  * **§3 Safe-VLM Architecture (Pages 4–5):** Visual Guard Module (VGM) classifier.
  * **§4.2 & Table 3 Benchmark Results (Pages 6–7):** Multi-judge evaluation (Claude, GPT-4o, Gemini).
* **Core Problem & Threat Model:**
  * Previous datasets only tested Safe Image + Safe Text or Unsafe Image + Unsafe Text. Real-world deployments face all permutations of safe and unsafe modalities.
* **Core Methodology:**
  * Curated 6,689 images and 14,246 instruction pairs spanning **5 safety states**:
    1. Unsafe Image + Unsafe Text $\to$ Unsafe
    2. Unsafe Image + Safe Text $\to$ Unsafe
    3. Safe Image + Unsafe Text $\to$ Unsafe
    4. Safe Image + Safe Text $\to$ Unsafe (Joint compositional risk)
    5. Safe Image + Safe Text $\to$ Safe / Helpful
  * Built Safe-VLM: Adds a Visual Guard Module (VGM) that pools visual tokens into an MLP classifier, trained jointly with next-token loss on 8×A100 GPUs.
* **Key Empirical Findings (Table 3):**
  * SafeLLaVA-7B reduces Claude-judged mean ASR from 79.1% (LLaVA-1.5) down to **8.8%**, while keeping safe-pair refusal rate at **1.3%**.
  * Outperforms standard SFT (VLGuard = 39.9% ASR) and standard DPO (SPA-VL = 40.5% ASR).
* **Improvements Over Prior Work:**
  * First work to systematically map and train on the complete 5-state multimodal risk matrix.
* **Fundamental Limitations:**
  * Relies heavily on synthetic GPT-4o supervision (potential data contamination).
  * Focuses on training a new architecture rather than understanding why base post-trained models fail to arbitrate conflict.
* **Relation to Our Proposal:**
  * Validates the structure of our **3×3 Counterfactual Matrix**. HoliSafe proved that multimodal safety must be analyzed across state combinations; we adapt this into a zero-training causal probing suite.

---

### 7. VLMGuard-R1: Proactive Safety Alignment via Reasoning-Driven Prompt Optimization
* **Authors:** Xu et al.
* **Official Link:** [https://aclanthology.org/2026.findings-acl.1986/](https://aclanthology.org/2026.findings-acl.1986/) | [arXiv:2504.12661](https://arxiv.org/abs/2504.12661)
* **Local PDF:** `presentation/paper_pdfs/vlmguard.pdf` (19 pages)
* **Attached Visual Assets:**
  * `presentation/paper_crops/vlmguard_fig1.png` (Page 2, Figure 1: External prompt rewriter framework)
  * `presentation/paper_crops/vlmguard_table1.png` (Page 6, Table 1: Safety vs. Helpfulness on 5 VLMs)
* **Exact Sections to Read:**
  * **§1 & §2 Introduction & Framework (Pages 1–3):** System-level defense boundary.
  * **§4.1 Main Results & Table 1 (Pages 5–7):** Performance on VLGuard-Unsafe, SIUO, MM-SafetyBench.
* **Core Problem & Threat Model:**
  * How to protect arbitrary downstream VLMs without modifying their weights or requiring fine-tuning access.
* **Core Methodology:**
  * Trains an external 7B model (Qwen2-VL-7B) as a **prompt rewriter**.
  * The rewriter inspects the user text and image, detects potential safety bypasses via chain-of-thought reasoning, and rewrites the prompt into a sanitized form before forwarding it to the target VLM.
* **Key Empirical Findings (Table 1):**
  * Safety scores improve across models (e.g., LLaVA-1.5 on VLGuard-Unsafe: 3.71 $\to$ 6.70).
  * **Helpfulness Trade-off:** On SIUO compositional risk, Qwen2-VL-7B helpfulness **drops from 60.24% down to 53.61%**.
  * Refusal-string defense success rate (DSR) is only 56.1% overall.
* **Improvements Over Prior Work:**
  * Eliminates the need to fine-tune downstream models; provides reasoning-guided input sanitization.
* **Fundamental Limitations:**
  * System-level overhead: Doubles latency and GPU memory requirements by adding a second 7B model forward pass.
  * Input rewrites can over-sanitize complex queries, reducing user utility.
* **Relation to Our Proposal:**
  * Demonstrates that **external guard wrappers suffer from helpfulness degradation and latency bloat**. Justifies our focus on probing the intrinsic arbitration mechanics of the target model itself.

---

### 8. CMRM: Cross-Modality Representation Manipulation
* **Authors:** Sun et al.
* **Official Link:** [https://aclanthology.org/2025.findings-acl.186/](https://aclanthology.org/2025.findings-acl.186/)
* **Local PDF:** `presentation/paper_pdfs/cmrm.pdf` (14 pages)
* **Exact Sections to Read:**
  * **§1 & §2 Modality Representation Gap (Pages 1–4):** Hidden state divergence between text and vision.
  * **§3 CMRM Algorithm (Pages 4–5):** Extraction of the representation shifting vector.
  * **§4 Evaluation & Table 1 (Pages 6–8):** Layer sensitivity and safety/utility trade-offs.
* **Core Problem & Threat Model:**
  * Diagnoses the mathematical root cause of why VLMs fail to transfer text alignment to images: **the modality representation gap**.
* **Core Methodology:**
  * Evaluated on LLaVA-1.5, InstructBLIP, and mPLUG-Owl2.
  * Analyzes hidden states in the LLM residual stream. Finds that unsafe image-text inputs cluster in an unaligned representation subspace distinct from unsafe text-only inputs.
  * Extracts an inference-time **shifting vector** $\Delta v$ that shifts unsafe multimodal representations into the aligned refusal region without modifying model weights.
* **Key Empirical Findings (Table 1 & Figure 1):**
  * Visualizes that text safety alignment fails because visual tokens pull hidden states away from the refusal manifold.
  * Applying CMRM shifting vectors at intermediate decoder layers reduces unsafe rates significantly (reported 61.53% $\to$ 3.15% in their setup) while retaining benign utility.
* **Improvements Over Prior Work:**
  * First paper to provide geometric representation-space proof of the multimodal alignment gap.
* **Fundamental Limitations:**
  * Requires identifying optimal steering layers and threshold hyperparameter $\alpha$ per model family; can induce over-refusals if shifted too aggressively.
* **Relation to Our Proposal:**
  * Foundation for our **Mechanistic Attribution (Slide 15)**. Proves that cross-modal conflict occurs as a physical vector displacement in hidden representation space.

---

### 9. JailBound: Probing and Crossing the Multimodal Safety Boundary
* **Authors:** Song et al. (NeurIPS 2025)
* **Official Link:** [https://arxiv.org/abs/2505.19610](https://arxiv.org/abs/2505.19610)
* **Local PDF:** `presentation/paper_pdfs/jailbound.pdf` (21 pages)
* **Exact Sections to Read:**
  * **§1 & §3 Safety Boundary Probing (Pages 1–5):** Mathematical formulation of the linear decision boundary.
  * **§4 Experiments & Table 3–4 (Pages 6–9):** White-box and black-box boundary crossing evaluations.
* **Core Problem & Threat Model:**
  * White-box and black-box representation probing. How do jailbreaks manipulate internal representations to cross the model's safety threshold?
* **Core Methodology:**
  * Formulates safety as a geometric classification boundary in the hidden residual stream.
  * Evaluates 6 VLMs (LLaVA-1.5, LLaVA-NeXT, Qwen2.5-VL-7B, MiniGPT-4).
  * Uses a two-stage approach:
    1. **Safety Boundary Probing:** Uses linear probes on intermediate layer activations to locate the hyperplane separating safe refusal from compliance.
    2. **Boundary Crossing:** Optimizes image and text inputs with gradient guidance to push hidden states across the boundary with minimal perturbation.
* **Key Empirical Findings (Tables 3 & 4):**
  * Achieves **94.32%** average white-box ASR and **67.28%** black-box transfer ASR.
  * Demonstrates that safety decisions are not finalized in layer 1; representations traverse a multi-layer trajectory where visual tokens gradually pull the state across the decision boundary.
* **Improvements Over Prior Work:**
  * Transitions from heuristic prompt hacking to a mathematically grounded geometric boundary theory of VLM safety.
* **Fundamental Limitations:**
  * Focuses on weaponizing the boundary to craft attacks rather than mapping how natural variations in visual carrier saliency influence boundary crossing.
* **Relation to Our Proposal:**
  * Supplies our **Layer-Wise Safety Bifurcation Protocol (Slide 15)**. We train linear probes on safe activations to identify the refusal direction vector, then track conflict-cell hidden state trajectories to find the exact layer where visual injections breach the boundary.

---

### 10. SafetyReminder: Remedying Delayed Safety Awareness in VLMs
* **Authors:** Tang et al. (AAAI 2026)
* **Official Link:** [https://ojs.aaai.org/index.php/AAAI/article/view/40607](https://ojs.aaai.org/index.php/AAAI/article/view/40607)
* **Core Problem:**
  * Why do VLMs comply with visual attacks when their LLM backbone knows how to refuse?
* **Key Finding — "Delayed Safety Awareness":**
  * In text-only LLMs, safety awareness triggers on token 0 (the model immediately outputs *"I cannot..."*).
  * In VLMs, visual tokens dominate the cross-attention matrix during the first few decoding steps. The model commits to generating the initial tokens of compliance (e.g., *"Step 1:..."*) **before the language safety heads have an opportunity to steer the logits toward refusal**. Once the first compliance tokens are generated, autoregressive momentum forces the model to complete the harmful response!
* **Relation to Our Proposal:**
  * Directly motivates our **Cross-Attention Attribution Metric (Slide 15)**:
    $$\text{AttnRatio} = \frac{\sum_{i \in \text{Vision}} A_{t,i}}{\sum_{j \in \text{Prompt}} A_{t,j}}$$
    We extract cross-attention weights over the first 10 generated tokens to test whether visual injection tokens causally monopolize attention mass on token zero.

---

### 11. MMJailBench: A Factorized Benchmark for Multimodal Jailbreak Attribution
* **Authors:** Wang et al. (arXiv:2608.25490, Aug 2026 preprint)
* **Official Link:** [https://arxiv.org/abs/2608.25490](https://arxiv.org/abs/2608.25490)
* **Local PDF:** `presentation/paper_pdfs/mmjailbench.pdf` (16 pages)
* **Exact Sections to Read:**
  * **§1 & §2 Motivation & Factor Decomposition (Pages 1–3):** Deconstruction of multimodal jailbreak mechanisms.
  * **§4 Evaluation across 16 Models (Pages 5–8):** Table 1 (Per-model ASR) & Table 3 (Carrier analysis: TEXT vs. OCR).
* **Core Problem:**
  * Prior benchmarks blend multiple attack variables together, making it impossible to know *why* an attack succeeded.
* **Core Methodology:**
  * Factorizes multimodal inputs into 4 orthogonal dimensions:
    1. **Harmful Intent** (272 intents across 9 risk categories)
    2. **Prompt Framing** (6 conversational frames: neutral, roleplay, hypothetical, etc.)
    3. **Visual Semantics** (5 visual contexts: benign, misleading, relevant, etc.)
    4. **Instruction Carrier** (Text-carried vs. Image-carried OCR)
  * Evaluated across 16 open and closed VLMs.
* **Key Empirical Findings (Table 3):**
  * OCR carrier bypass increases ASR across virtually all models, but the vulnerability is heavily conditioned by prompt framing.
  * Shows that visual tokens and text framing interact multiplicatively rather than additively.
* **Relation to Our Proposal:**
  * Theoretical foundation for our **Signal Context vs. Intentional Context** deconstruction. We adopt their factorization logic and turn it into a controlled counterfactual matrix.

---

### 12. VSCBench: Visual Safety Calibration & Over-Refusal
* **Authors:** Li et al. (Findings of ACL 2025)
* **Official Link:** [https://aclanthology.org/2025.findings-acl.158/](https://aclanthology.org/2025.findings-acl.158/)
* **Local PDF:** `presentation/paper_pdfs/vscbench.pdf` (14 pages)
* **Core Problem:**
  * Evaluating safety solely via ASR rewards "blanket refusal" models that refuse benign questions.
* **Methodology & Findings:**
  * 3,600 paired image/text cases evaluating 11 VLMs.
  * Measures both **under-safety** (answering disallowed queries) and **over-safety** (refusing benign queries with superficially sensitive images).
  * Found that existing safety-aligned models suffer from severe miscalibration, rejecting safe educational or descriptive requests.
* **Relation to Our Proposal:**
  * Supplies the protocol for **Control B and Cell 5** in our matrix. Ensures our behavioral scoring captures both false compliance and false refusal.

---

### 13. PolyJailbreak: Adaptive Black-Box Multi-Agent Visual Search
* **Authors:** Xie et al. (arXiv:2510.17277)
* **Official Link:** [https://arxiv.org/abs/2510.17277](https://arxiv.org/abs/2510.17277)
* **Core Problem:**
  * Static jailbreak templates (like FigStep) are easily memorized or filtered. What happens when an attacker adaptively optimizes multimodal strategies?
* **Methodology & Findings:**
  * Uses a multi-agent reinforcement learning search framework over atomic visual and textual perturbation primitives.
  * Achieved >95% ASR on commercial MLLMs by adaptively finding the weakest cross-modal combination under a fixed query budget.
* **Relation to Our Proposal:**
  * Serves as our **Tier 7 Held-Out Adaptive Attack**. Tests whether the saliency thresholds we discover under static sweeps generalize to dynamic, search-optimized visual attacks.

---

### 14. HADES: Visual-Semantic Concealment and Amplification
* **Authors:** Li et al. (ECCV 2024)
* **Official Link:** [https://arxiv.org/abs/2403.09792](https://arxiv.org/abs/2403.09792)
* **Core Problem:**
  * Unlike FigStep (which renders words into pixels), HADES hides harmful intent inside natural visual semantics and object juxtapositions.
* **Key Findings:**
  * Achieved 90.26% ASR on LLaVA-1.5 and 71.60% on Gemini Pro Vision using semantic image manipulation.
* **Relation to Our Proposal:**
  * Defines our **I2: Semantic Visual Cue** condition in the 3×3 matrix, proving that cross-modal conflict occurs at both the syntactic (OCR) and semantic (scene understanding) levels.

---

## Part 2: Moving Beyond Base Tests to the Full Testing Battery

Our research proposal does not merely re-run FigStep. We synthesize all 14 audited papers into an **exhaustive 7-tier testing battery** that interrogates the entire lifecycle of cross-modal signal conflict:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    THE FULL CAUSAL TESTING BATTERY                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 1: Physical Saliency Sweeps (Extending FigStep & MMJailBench)              │
│   • Font size (12pt → 72pt), contrast (1.5:1 → 21:1), spatial coverage (%)     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 2: Semantic Composition Probing (Extending SIUO & HADES)                  │
│   • Innocuous images + benign prompts with emergent hazard combinations         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 3: Visual Leakage & Grounding Controls (Enforcing VLSBench Protocol)      │
│   • Strict text sanitization: 0% harm in text; 100% harm in visual carrier     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 4: Instruction Hierarchy Stress Testing (Intentional Context Levels)      │
│   • Neutral (L0) → Implicit (L1) → Explicit Untrusted (L2) → Strict System (L3)│
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 5: Paired Calibration & Over-Refusal Checks (VSCBench Protocol)           │
│   • Matched benign counterfactuals for every harm category (Control A, B, C)   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 6: Mechanistic Probing & Layer Bifurcation (JailBound & SafetyReminder)   │
│   • Cross-attention ratio (AttnRatio) on tokens 0–10                           │
│   • Residual stream linear probing to locate exact layer bifurcation point     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Tier 7: Held-Out Adaptive Search Validation (PolyJailbreak Protocol)           │
│   • Bounded black-box query sweeps to verify out-of-distribution robustness    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: Quick Reading Guide for Advisor Meetings

When preparing for discussions with Prof. Thao Minh Le, use this targeted reading map:

| If Discussing... | Open This File | Look at These Exact Pages | What to Point Out |
| :--- | :--- | :---: | :--- |
| **Why OCR breaks models** | `figstep.pdf` | **P1 (Fig 1), P5 (Table 1)** | CogVLM jumps from 8.2% to 87.0% ASR; text-only filters fail. |
| **Why defense pipelines fail** | `safevlm.pdf`<br>`adpo.pdf` | **P9 (Tables 3-4)**<br>**P7 (Table 1)** | SafeVLM safe-pass drops 14.3%; ADPO LLaVABench drops 11.3 pts and OCRBench drops from 202 to 184. |
| **Why prompt rewrites fail** | `vlmguard.pdf` | **P6 (Table 1)** | Qwen2-VL SIUO helpfulness drops from 60.2% to 53.6%; doubles compute. |
| **Compositional danger** | `siuo_acl.pdf` | **P1 (Fig 1), P7 (Table 2)** | Clean image + clean text = dangerous chemical reaction. |
| **Why benchmarks cheat** | `vlsbench_acl.pdf` | **P2 (Fig 1), P3 (Table 1)** | Removing the image still gives ~68% ASR because text leaked the harm. |
| **How we probe mechanisms** | `jailbound.pdf`<br>`cmrm.pdf` | **P2 (Fig 1), P5 (Fig 2)**<br>**P3 (Fig 1)** | Hidden states cross a geometric boundary; visual tokens pull representations away from refusal subspace. |

---
*Dossier preserved in repo:* `/Users/aryamandev/Developer/blissful-bose/docs/DEEP_LITERATURE_AUDIT_AND_RESEARCH_FOUNDATION.md`
