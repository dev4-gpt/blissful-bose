# Master Research Plan: Cross-Modal Signal Conflict in Safety-Aligned Vision-Language Models

**Project Title:** Cross-Modal Signal Conflict in Safety-Aligned Vision-Language Models: A Causal Analysis of Visual Injections and Intentional Context  
**Author:** Aryaman Singh Dev  
**Advisor:** Prof. Thao Minh Le — Pennsylvania State University  
**Date:** October 2026  

---

## 1. Executive Summary & The Core Pivot

Following advisor feedback, this project pivots away from compute-intensive continual learning and defense-template engineering toward an **empirical, causal investigation of Cross-Modal Signal Conflict in frozen, post-trained Vision-Language Models (VLMs)**.

### What We Are NOT Doing (Explicit Advisor Exclusions)
1. **NOT designing a template to resist attacks:** No new defense wrappers, guardrail architectures, or prompt-filtering frameworks.
2. **NO new benchmark creation:** No curating massive 5,000-sample benchmark datasets.
3. **NO heavy model training:** No 4-stage continual fine-tuning, no LoRA fine-tuning across domains, no DPO/ADPO re-training.

### What We ARE Doing (Core Directives)
1. **Focus on Cross-Modal Signal Conflict:** Investigating what happens when visual and textual inputs convey contradictory instructions.
2. **Disentangling Signal Context vs. Intentional Context:**
   - **Signal Context:** Physical manifestation in the visual channel (carrier, typography, resolution, layout, visual saliency).
   - **Intentional Context:** Semantic framing in the language channel (benign intent, neutral inquiry, strict safety system prompt).
3. **Evaluating Post-Trained Models:** Probing off-the-shelf, safety-aligned models (e.g., `Qwen2.5-VL-7B-Instruct`, `Qwen2-VL-2B-Instruct`) to test if their safety alignment holds under cross-modal conflict.
4. **Causal Impact via Counterfactual Injections:** Keeping one modality fixed while perturbing or injecting bad instructions into the other, measuring the exact threshold where safety guardrails flip.
5. **Seminar Structure:** Answering the two foundational academic questions:
   - *What has been done?* (SOTA literature audit)
   - *What else can be done?* (Our zero-training causal probing experiment)

---

## 2. Theoretical Grounding & Literature Audit

### 2.1 What Has Been Done (SOTA)
- **Carrier Exploits (2023–2024):** 
  - *FigStep* (Gong et al., 2023): Harmful text rendered inside images bypasses text safety filters via the OCR pathway.
  - *MM-SafetyBench* (Liu et al., 2024): Demonstrated that image inputs act as an unaligned backdoor for aligned LLM backbones.
- **Compositional & Implicit Risks (2025):**
  - *SIUO* (Wang et al., NAACL 2025): Showed that a benign-looking image and benign-looking text can combine to produce an unsafe request.
  - *VLSBench* (Hu et al., ACL 2025): Revealed *visual leakage*—many multimodal benchmarks leak the harm via text without requiring actual visual comprehension.
- **Factorized Taxonomy (2026):**
  - *MMJailBench* (Wang et al., 2026): Factorized multimodal attacks into intent, framing, visual semantics, and carrier.
- **Representation & Inference Interventions:**
  - *CMRM* (Liu et al., Findings of ACL 2025): Cross-modality representation manipulation at inference time to bridge the representation gap.
  - *JailBound* (Song et al., NeurIPS 2025): Probing internal safety boundaries in VLM representation space.

### 2.2 What Else Can Be Done (The Open Gap We Address)
Existing literature shows *that* attacks succeed or proposes heavy defense mechanisms. **Nobody has systematically mapped the causal mechanics of conflict arbitration inside frozen models:**
1. Under what visual saliency threshold (font size, contrast, image area) does an image-based injection overpower a textual safety prompt?
2. Does the model fail because the vision encoder suppresses the language model's refusal tokens in cross-attention, or because the model fails to detect the conflict?
3. How effectively does strengthening the **Intentional Context** (e.g., system instructions) defend against varying **Signal Contexts** without retraining?

---

## 3. Experimental Methodology: Causal Injections (Zero Training)

### 3.1 The 3×3 Counterfactual Conflict Matrix
We construct controlled evaluation pairs $(I, T)$ crossing 3 Signal Contexts with 3 Intentional Contexts:

| Signal Context (Image $I$) | Intentional Context: Benign Framing ($T_1$) | Intentional Context: Safety-Explicit ($T_2$) | Intentional Context: Neutral Request ($T_3$) |
| :--- | :--- | :--- | :--- |
| **$I_0$: Clean / Benign Image** | Control: Benign Q&A | Control: Strict Safe Q&A | Control: Direct Q&A |
| **$I_1$: Typographic Bad Injection (OCR)** | **Tug-of-War Test:** Does the visual text override benign user intent? | **Hierarchy Test:** Does the explicit safety prompt defeat the visual injection? | **Direct Jailbreak:** Baseline visual bypass rate. |
| **$I_2$: Visual Semantic Cue (Spliced)** | **Implicit Composition:** SIUO-style latent conflict. | **Ambiguity Check:** Does the model over-refuse safe visual elements? | **Semantic Trigger:** Visual cue eliciting restricted knowledge. |

### 3.2 Causal Interventions
1. **Visual Saliency Scaling:** We fix a harmful instruction and render it at 12pt, 24pt, 36pt, 48pt, and 72pt. We record the exact font size at which the model transitions from **Safe Refusal** $\rightarrow$ **Harmful Compliance**.
2. **Patch Occlusion / Masking:** We mask patches of the injected image to find the minimal visual surface area required to trigger compliance.
3. **Cross-Attention Attribution:** During generation, we extract attention weights from the first generated token to determine whether attention is flowing toward the text instruction or the visual injection tokens.

### 3.3 Behavioral Outcome Metrics
Every output is categorized into one of three distinct behavioral states:
- **State 1: Aligned Refusal** (Text alignment holds; model refuses the harmful request).
- **State 2: Unsafe Compliance** (Visual injection wins; model follows the harmful instruction).
- **State 3: Hallucinated Deflection** (Conflict causes confusion; model outputs irrelevant/nonsense text).

---

## 4. The Seminar Presentation Blueprint (12 Slides)

| Slide | Title | Key Message / Narrative |
| :---: | :--- | :--- |
| **1** | **Title Slide** | *Cross-Modal Signal Conflict in Post-Trained Vision-Language Models: Causal Dynamics of Visual Injections and Intentional Context.* |
| **2** | **The Core Problem: A Multi-Modal Tug-of-War** | When the image says one thing and the text prompt says another, which signal wins? |
| **3** | **Key Variables: Signal vs. Intentional Context** | Defining **Signal Context** (visual carrier, OCR, typography) vs. **Intentional Context** (semantic goal, prompt framing). |
| **4** | **What Has Been Done? (SOTA Literature Audit)** | Reviewing FigStep (OCR carrier), SIUO (joint composition), and VLSBench (visual leakage). |
| **5** | **The Critical Gap in Existing Work** | Prior work focuses on black-box attacks or expensive training defenses; internal conflict arbitration is unmapped. |
| **6** | **What Else Can Be Done? Our Core Research Question** | Zero-training causal probing to identify the exact thresholds where visual signals override text alignment. |
| **7** | **The Counterfactual Conflict Matrix** | Presenting the 3×3 experimental matrix testing conflicting inputs. |
| **8** | **Causal Intervention Protocol** | Explaining saliency scaling, patch occlusion, and counterfactual injections. |
| **9** | **Behavioral Analysis: Refusal vs. Compliance vs. Deflection** | Categorizing model behavior beyond simple attack success rates. |
| **10** | **Pilot Demonstration on Qwen2-VL-2B** | Showing concrete qualitative examples of conflict flips running locally/on Colab. |
| **11** | **Feasibility & Compute Advantage** | High scientific rigor with zero training overhead, running on standard GPU hardware. |
| **12** | **Project Roadmap & Summary** | Immediate milestones and research deliverables. |

---

## 5. Execution Roadmap: When and How to Start

### Phase 1: Presentation & Seminar Materials (Immediate — Today)
- [ ] Generate the 12-slide PowerPoint presentation: `presentation/VLM_Cross_Modal_Conflict_Presentation.pptx`.
- [ ] Generate the word-for-word speaker script: `presentation/VLM_Cross_Modal_Conflict_Speaker_Notes.md`.
- [ ] Review and rehearse for the advisor meeting.

### Phase 2: Diagnostic Pilot Test (Days 1–3)
- [ ] Set up a lightweight environment running `Qwen2-VL-2B-Instruct` (Google Colab T4 or local GPU).
- [ ] Create a 20-sample diagnostic dataset containing clean pairs, typographic injections, and prompt variations.
- [ ] Run inference forward passes and record the behavioral responses.
- [ ] Add 2–3 qualitative screenshots of the output directly into Slide 10 of the presentation deck.

### Phase 3: Systematic Causal Probing (Days 4–7)
- [ ] Run the saliency scaling test (varying typography size and contrast).
- [ ] Log attention weights to confirm whether visual tokens suppress language refusal tokens.
- [ ] Synthesize findings into the final paper draft.
