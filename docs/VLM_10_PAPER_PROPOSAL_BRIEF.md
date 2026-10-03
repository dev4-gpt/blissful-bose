# Focused VLM Safety Alignment Proposal: Literature-to-Protocol Brief

**Literature snapshot:** 30 September 2026  
**Scope:** a focused proposal grounded in ten representative papers, not a completed systematic review. The larger evidence dossier and full-paper checklist remain the broader audit of record.

## 1. Problem formulation

Vision-language models (VLMs) must interpret an image and a text instruction jointly. Safety failures can arise from text-only intent, text embedded in an image, harmful visual semantics, or the interaction of individually innocuous modalities. A refusal-only metric is insufficient: an always-refusing model can appear safe while failing benign users, and a model can pass a safety test without actually grounding its decision in the image.

**Research question:** For a fixed open-weight VLM and a controlled multimodal data budget, which safety-alignment intervention most improves resistance to held-out visual and cross-modal attacks while preserving benign answerability, image grounding, and general task capability?

**Unit of evaluation:** a source intent paired with an image, text prompt, and controlled transformations. Splits must be made by source intent before attack variants are generated, preventing near-duplicate prompt/image variants from leaking across train and test.

## 2. What the focused literature establishes

| Evidence role | Representative papers | What they establish for our design | What they do not establish |
|---|---|---|---|
| Safety SFT and data | VLGuard | Multimodal safety instruction tuning is a practical baseline; preserve helpful data and measure false refusal. | That one small safety dataset generalizes to adaptive or unseen visual attacks. |
| Preference alignment | SPA-VL, ADPO | Preference pairs are a distinct resource; ADPO directly studies adversarially aware preference training. | A common leaderboard across different models, data, judges, and threat models. |
| Integrated visual guard | HoliSafe / Safe-VLM | Five safety input/outcome states and a visual guard are already prior art. | That a five-state taxonomy alone captures adaptive, leakless, or cross-model generalization. |
| Visual prompt intervention | DAVSP | A prompt/activation intervention can be evaluated alongside weight updates. | That its reported RSR is directly comparable to other papers' ASR or safety rate. |
| Arbitration objective | Pragma-VL | Recent work explicitly balances safety and helpfulness in training. | Direct comparability until exact metrics, model recipes, and judges are harmonized. |
| Fixed attack | FigStep | Image-carried typography/OCR is a reproducible jailbreak channel. | Comprehensive coverage of semantic images, compositional risk, or adaptive attackers. |
| Leakage-aware evaluation | VLSBench | Safety scores can overstate visual robustness when test text leaks the unsafe intent. | A complete safety evaluation by itself; must be combined with other attack families. |
| Broad benchmark | USB | Risk coverage can be organized across many categories and modality combinations, with over-refusal tracked. | A single stable causal estimate unless source intent, split, and judge are controlled. |
| Adaptive attack | PolyJailbreak | Black-box cross-modal attacks can adapt to targets; query budget is part of the threat model. | A static ASR directly comparable with fixed attacks or attacks run at different budgets. |

## 3. Proposed hypothesis and falsifiable predictions

**Primary hypothesis H1:** Multimodal safety alignment trained with image-conditioned safety evidence will reduce harmful-compliance rate on intent-held-out visual/cross-modal attacks more than text-only safety tuning at a matched training budget.

**Trade-off hypothesis H2:** Adversarial preference alignment (ADPO-style) will further reduce attack success on attack families represented during training, but may show smaller gains on held-out attack mechanisms; therefore family-held-out testing is essential.

**Grounding hypothesis H3:** Leakless and image-removal/decoy controls will reveal a gap between benchmark performance that can be achieved from text alone and genuine image-grounded safety behavior.

These are proposals, not findings. Pre-register primary endpoint, evaluation set, judge, and exclusion rules before running the experiment.

## 4. End-to-end experimental system design

```text
Source intents + licensed image pool
        |
        +--> safety / benign-near-neighbor annotation
        |        +--> image-text state labels (safe/unsafe by modality and outcome)
        |        +--> preference pairs only for preference-training arm
        |
        +--> intent-level split BEFORE attack transforms
                 train / validation / locked test
                          |
           +--------------+-------------------+
           |              |                   |
       Native base    Text-only SFT      VLM alignment arms
                                          VLGuard-style SFT
                                          standard DPO
                                          ADPO-style DPO (if reproducible)
                                          optional HoliSafe/DAVSP comparator
           |              |                   |
           +--------------+-------------------+
                          |
             locked attack/evaluation suite
       FigStep OCR | semantic visual | cross-modal
       VLSBench leakless | USB selected strata
       PolyJailbreak adaptive (separate budgeted tier)
                          |
         safety + helpfulness + grounding + cost
       harmful compliance / false refusal / answer quality
       image ablations / capability / latency / training compute
                          |
             paired analysis, CIs, failure taxonomy
```

The diagram is a proposed comparison design, not a combined model that any paper has already validated. Train and inference interventions should remain separate experimental arms; do not pool their results into one leaderboard.

## 5. Attack suite and test protocol

| Tier | Test family | Role | Minimum control |
|---|---|---|---|
| Fixed, reproducible | FigStep typography/OCR | Image-carried harmful text and prompt interaction | Same intent as text-only; benign OCR and font/layout holdout |
| Semantic visual | Harmful scene/object/action images from a fixed benchmark slice | Tests meaning beyond OCR | Image-only, text-only, and matched safe visual near-neighbor |
| Cross-modal/compositional | Safe Inputs but Unsafe Output (SIUO-style) cases | Tests risk emerging only from joint interpretation | Each modality alone plus joint input; document benchmark version/count |
| Leakage-aware | VLSBench | Requires visual evidence instead of explicit unsafe words | Original image, removed/masked image, and decoy image |
| Broad coverage | Prespecified USB strata | Risk category and modality coverage | Report Base/Hard and each modality separately; include RR/false refusal |
| Adaptive red team | PolyJailbreak | Target-adaptive black-box stress test | Fixed query budget, repeated seeds, success-versus-query curve; never mix with static ASR |

**Primary attack endpoint:** harmful-compliance rate on a locked intent-held-out test. Report by attack family and modality, not only a pooled number. For adaptive attacks report success as a function of queries. Do not treat refusal string matching alone as semantic safety.

## 6. Baseline ladder

1. **Native VLM:** untouched target checkpoint; establishes inherited behavior.
2. **Text-only safety SFT:** isolates improvement from ordinary language safety tuning.
3. **Multimodal safety SFT:** VLGuard-style image-conditioned instruction tuning with benign/helpfulness data retained.
4. **Standard multimodal DPO:** preferred/rejected responses with a fixed preference dataset; distinguishes the effect of preference optimization from adversarial training.
5. **ADPO-style adversarial DPO:** include only if code, threat assumptions, and model recipe can be faithfully reproduced.
6. **One recent method comparator:** choose HoliSafe/Safe-VLM, DAVSP, or Pragma-VL according to compatible model, released artifacts, compute, and evaluation; do not promise all three before feasibility checks.

Use the same base checkpoint, train/validation/test intents, inference settings, and judge across arms where possible. Report data and compute budget. Inference-time defenses (e.g. external guards or prompt interventions) are system comparators and must report extra calls, latency, and guard false positives separately.

## 7. Metrics and analysis

- **Safety:** semantic harmful-compliance rate / attack success rate, with judge and rubric disclosed; human-audit a stratified sample and judge disagreements.
- **Calibration:** benign false-refusal rate and safe-request answer quality on matched safe near-neighbors.
- **Grounding:** performance with original, removed, masked, and decoy images; report whether the answer depends on relevant visual evidence.
- **Capability:** a fixed general VQA/OCR suite, reported separately from safety.
- **System cost:** training data/tokens/compute; inference latency, extra model calls, and memory if intervention adds them.
- **Statistics:** per-item paired comparisons, confidence intervals, run/seed counts, and breakdowns by category, modality, attack family, and model. Avoid a cross-paper “SOTA” rank unless the protocols are harmonized.

## 8. Main research challenges surfaced by these papers

1. **Evaluation leakage and attribution:** unsafe text can reveal the answer without image understanding; use VLSBench-like neutralized prompts and image ablations.
2. **Attack-family generalization:** static OCR success does not imply semantic/adaptive robustness; keep a family out of training and validation.
3. **Safety-helpfulness trade-off:** refusal rates can reward blanket refusal; include safe near-neighbors and task quality.
4. **Metric incompatibility:** ASR, RSR, safety rate, judge scores, and benchmark-native scores have different directions and denominators; never compare raw values without a protocol table.
5. **Data contamination and near duplicates:** split by source intent and image provenance before deriving adversarial variants.
6. **Judge validity:** different LLM judges disagree; disclose rubric/version and audit human-labeled examples.
7. **Reproducibility and access:** commercial models, unavailable training data, adaptive query budgets, and evolving paper versions constrain fair reproduction.
8. **Benchmark scope:** broad categories can still miss compositional, multi-turn, demographic, language, and real-world contexts.

## 9. How to present this honestly

Say: “This is a focused proposal grounded in ten selected papers spanning attacks, evaluation validity, safety data, and alignment interventions. We synthesize them into a proposed end-to-end research pipeline: curated and decontaminated data, intent-level splits, separate alignment arms, locked attack and benchmark evaluation, then safety/helpfulness/grounding/cost analysis. The pipeline is our research design, not a system already implemented or validated by the literature. The ten papers use different setups, so their headline scores are not a shared leaderboard.”

For a numeric result, put the **paper citation, table/figure number, model, benchmark, metric name/direction, and evaluator** on the slide or in the speaker note. Use the exact paper-reported value. Never substitute the checklist's selected cells for reading the caption and protocol yourself.

## 10. References (IEEE-style short entries)

[1] Y. Gong *et al*., “FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts,” arXiv:2311.05608, 2023; AAAI 2025 (Oral).  
[2] X. Hu, D. Liu, H. Li, X. Huang, and J. Shao, “VLSBench: Unveiling Visual Leakage in Multimodal Safety,” in *Proc. ACL*, 2025, pp. 8285–8316, doi: 10.18653/v1/2025.acl-long.405.  
[3] B. Zheng *et al*., “USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models,” in *Proc. ACL*, 2026, pp. 21184–21211, doi: 10.18653/v1/2026.acl-long.970.  
[4] X. Wang et al., “PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs,” *IEEE Trans. Dependable Secure Comput.*, 2026, doi: 10.1109/TDSC.2026.3707228.  
[5] Y. Zong, O. Bohdal, T. Yu, Y. Yang, and T. Hospedales, “Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models,” in *Proc. ICML*, PMLR, vol. 235, 2024.  
[6] Y. Zhang *et al*., “SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision Language Models,” in *Proc. IEEE/CVF CVPR*, 2025, pp. 19867–19878.  
[7] F. Weng et al., “Adversary-Aware DPO: Enhancing Safety Alignment in Vision Language Models via Adversarial Training,” in *Findings of EMNLP*, 2025, pp. 13644–13657.  
[8] Y. Lee *et al*., “HoliSafe: Holistic Safety Benchmarking and Modeling with Safety Meta Token for Vision-Language Model,” in *Proc. IEEE/CVF CVPR Findings*, 2026, pp. 5989–5998.  
[9] Y. Zhang, J. Li, L. Cai, and G. Li, “DAVSP: Safety Alignment for Large Vision-Language Models via Deep Aligned Visual Safety Prompt,” in *Proc. AAAI*, vol. 40, no. 44, 2026, pp. 38111–38119, doi: 10.1609/aaai.v40i44.41149.  
[10] M. Wen, K. Yang, X. Chen, J. Zhang, D. Han, S. Cui, and Y. Xu, “Pragma-VL: Towards a Pragmatic Arbitration of Safety and Helpfulness in MLLMs,” in *Proc. ICLR*, 2026.
