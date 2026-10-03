# Speaker Notes: Safety Alignment for Small Vision-Language Models

**Target duration:** about 20 minutes, 19 core slides plus evidence appendix, references, and three optional attack-protocol slides (35–37).
**Companion:** [`VLM_Safety_Alignment_Research_Proposal_Updated.pptx`](../VLM_Safety_Alignment_Research_Proposal_Updated.pptx)  
**Detailed protocol and benchmark audit:** [`../docs/vlm_safety_protocol_audit.md`](../docs/vlm_safety_protocol_audit.md)  
**Literature snapshot:** 30 September 2026. This revision includes HoliSafe, DAVSP, and Pragma-VL, material recent VLM safety contributions absent from the earlier bibliography; it now has 29 entries (28 VLM-related, plus one LLM-only project-context paper).

The slides present an evidence-based proposal, not completed experimental findings. Attribute all reported claims to their papers; do not imply that cross-paper results are directly comparable. For examples, keep harmful requests abstract and non-operational.

## Slide 1 — Safety Alignment for Small VLMs (0:30)

“This presentation is a reset of the research framing. We are not assuming that the previous LLM continual-gradient method can simply be moved into a vision-language model. Instead, I audited what VLM safety-alignment research is doing now, how it tests its claims, and what study remains valuable for small open models.”

## Slide 2 — The question is not whether images create risk (1:00)

“A vision-language model receives more than a text prompt. The user can put text inside an image, communicate through visual semantics, or distribute meaning across the image and text. The goal is not merely to ask whether an attack works. We need to know which channel produces the failure, whether the model still answers benign requests, and whether the test genuinely requires visual understanding. That leads to our research question: can multimodal alignment improve robustness to held-out attacks in small open models without damaging safe answerability and grounding?”

## Slide 3 — Operationalize safety as three outcomes (1:10)

“I separate three outcomes because one number cannot describe alignment. First is harmful compliance: did the output materially enable the disallowed goal? Second is benign utility: did it still help with an allowed request that may share vocabulary or imagery with a harmful one? Third is grounding: did it interpret the image accurately? A system can look safer because it refuses everything, or because it stops looking at the image. Both would be poor outcomes. We should say ‘alignment’ when describing the training objective and ‘safety’ when describing measured system behavior.”

## Slide 4 — Text alignment does not guarantee multimodal safety (1:10)

“There are four reasons this is a separate research problem. Vision tuning can disturb safety behavior from the language backbone. Visual text can expose an OCR route around text-only safeguards. Joint image-text interpretation can create risk that neither channel expresses alone. And benchmark prompts can accidentally state the risk in text, allowing the model to pass without reading the image. The protocol therefore needs channel ablations, compositional cases, leakage controls, and matched safe examples.”

## Slide 5 — The field has shifted from finding failures to attributing them (1:00)

“The timeline shows how the questions evolved. Early work such as FigStep, HADES, MM-SafetyBench, and JailBreakV established attack channels and datasets. Work in 2025 added preference training, representation-gap explanations, and safety calibration. In 2026, benchmarks like USB and MMJailBench place more emphasis on modality factors and over-refusal; methods include prompt rewriting, label-free visual alignment, and selective decoding interventions. This is a broad, active field, not an empty space waiting for an LLM method to be ported.”

**Context if asked:** This is a representative map, not an exhaustive census or our method. The project itself is a controlled small-model comparison. Publication status matters: USB, VSFA, VLMGuard-R1, HoliSafe, DAVSP, and Pragma-VL are peer-reviewed proceedings; MMJailBench and SafeRI are preprints at this snapshot. HoliSafe's five-state benchmark and visual guard overlap with our earlier matched-data proposal; DAVSP and Pragma-VL also mean that a generic claim to propose a new VLM alignment method is not defensible. The gap must be established from a bounded comparison, transfer test, or measurement design.

## Slide 6 — Current methods intervene at different system layers (1:20)

“This taxonomy is organized by where the intervention acts. Training-time methods change data or objective: SFT, preference optimization, and adversarial DPO. Representation methods act on internal states. Input guards inspect or rewrite the prompt before the target model. Reasoning methods explicitly interpret risk or use threat-image exposure to shape behavior. Decode-time methods alter generation or activate a safety module only on risky trajectories. These are not interchangeable: a preprocessor can improve the system while leaving the target model unchanged, and its latency and failure modes must be counted.”

**Method-family detail:**
- **Data and objective:** VLGuard uses multimodal safety-instruction tuning; SafeVLM adds a safety projector/tokens/head; SPA-VL supplies chosen/rejected multimodal preference pairs; ADPO explicitly trains with adversarial preferences. VSFA uses neutral VQA around threat-related images; DAVSP optimizes a padded visual safety prompt with activation-space supervision; Pragma-VL combines risk-aware cold-start SFT with query-dependent safety/helpfulness reward weighting.
- **Representation and activation:** CMRM diagnoses and corrects cross-modal representation mismatch at inference; MMAligner calibrates unsafe multimodal representations toward a refusal region. These intervene at a different layer from preference training.
- **Input and reasoning:** VLMGuard-R1 uses an upstream reasoning-guided rewriter; GuardAlign combines unsafe-region detection and attention calibration. Think in Safety studies safety reasoning, with additional token cost and possible reasoning leakage.
- **Generation-time controls:** SafetyReminder uses a safety reminder/soft-prompt intervention; SafeSteer changes decoding; SafeRI proposes a streaming recognizer with gated LoRA activation. Treat SafeRI as a preprint at the snapshot date. These runtime approaches are not direct apples-to-apples training baselines.

**Comparison rule:** Label each result as model-intrinsic training or a system-level defense. Record changed target weights, extra models, trainable parameters, additional tokens/calls, latency, and whether the intervention runs on every request. See audit Sections 2–3; for continual-learning alternatives and trade-offs, see [methodology_comparison.md](../docs/methodology_comparison.md), especially its taxonomy and comparison tables.

## Slide 7 — Training-time papers are not interchangeable (1:20)

“VLGuard gives us a multimodal safety-SFT baseline; SafeVLM adds architectural safety modules. SPA-VL is a preference dataset and route to DPO, while ADPO is direct adversarial preference-alignment prior art. VSFA trains on neutral VQA around threat images without safety labels. HoliSafe adds five-state training/evaluation coverage and Safe-VLM adds an integrated visual guard. DAVSP instead optimizes a padded visual safety prompt against activation-space harmfulness signals; Pragma-VL combines risk-aware SFT with a reward model that dynamically arbitrates safety and helpfulness by query. These are distinct published approaches, not pieces of a method we can claim to have invented.”

**What the comparison means:** Separate safety data + SFT, standard DPO, adversarial DPO, architectural safety modules, holistic five-state training/guarding, activation-space visual prompting, query-dependent safety/helpfulness arbitration, and label-free neutral-VQA training. ADPO reports white-box VisualAdv/MMPGDBlank and black-box MultiTrust tests; SPA-VL is data, not an attack; SafeVLM and Safe-VLM/VGM are architectural methods, not plain SFT. Full protocols and caveats are in audit Section 3 and Addenda A.2–A.8.

## Slide 8 — Runtime defenses change the system boundary (1:00)

“CMRM and MMAligner are representation interventions. VLMGuard-R1 adds an upstream reasoning-based rewriting component. SafetyReminder and SafeSteer work at the prompt or decoding level; SafeRI is a very recent preprint proposing a token-level recognizer and gated LoRA. A fair comparison must state whether the target model weights changed, whether a second model was added, whether the method operates every token, and how latency and trigger mistakes affect safe examples. These distinctions matter especially for small deployment.”

**Newer methods to keep in the account:** GuardAlign is an input/internal hybrid (unsafe-region detection plus attention calibration), not simply a prompt filter. Think in Safety is a reasoning/data approach. SafeSteer is decoding-level intervention; SafeRI is a September 2026 arXiv preprint and must be labeled as emerging. These additions belong in the related-work/methodology comparison even when the 20-minute narrative cannot give each a full slide. See audit Section 2 and [methodology_comparison.md](../docs/methodology_comparison.md).

## Slide 9 — Separate attack procedures from benchmark controls (1:00)

“We corrected an important category error: FigStep and HADES are attack constructions; PolyJailbreak is adaptive; JailBreakV is a collection of attack instances. SIUO, VLSBench, USB, and safe-neighbor sets are evaluation resources or controls, not attack algorithms. HADES Typ, black-box +Opt, and white-box +Adv also represent distinct threat models. The appendix now specifies how we would freeze and run them.”

## Slide 10 — Benchmarks answer different questions (1:30)

“The benchmark choices are complementary. USB gives broad risk-by-modality coverage; VSCBench measures safe/unsafe calibration; VLSBench tests whether the image matters; SIUO targets safe inputs that become risky jointly; HoliSafe covers five image/text safety states. MMJailBench factorizes intent, framing, visual semantics, and carrier, but is a preprint at this snapshot.”

**Selection logic:** Use a broad benchmark for coverage, paired safe/unsafe cases for calibration, a leakage-controlled set for visual dependence, and a targeted composition set for interaction risk. MM-SafetyBench and JailBreakV are useful attack-suite sources but are not substitutes for safe-neighbor evaluation. MemeSafetyBench adds ecological real-meme cases but has marked class imbalance; report balanced/class-specific metrics. Capability and hallucination diagnostics should be reported separately from harmful-compliance benchmarks. Do not average unlike measures into one score. Dataset sizes, examples, roles, and caveats are in audit Section 5 and Addendum B.1.

## Slide 11 — Protocol audit: ADPO is a useful reproduction template (1:10)

“ADPO is a good example of what a useful protocol description looks like. It names its model panel and LoRA approach; it tests two optimization-based attacks and the typographic, multimodal, and cross-modal portions of MultiTrust; it uses the HarmBench classifier to label harmful responses; and it measures utility on four visual benchmarks. It also compares against SFT, standard DPO, a training-free defense, and direct adversarial training, plus component ablations. The result is not just a claimed safety gain: the paper also reports utility trade-offs. Our protocol audit asks the same questions for every paper.”

**Audit checklist applied across papers:** What is the intervention and system boundary? Which base checkpoints, processors, and chat templates? What training data and split? Which attack families and attacker access/query budget? What judge, rubric, and human validation? Which benign utility tests? What ablations and compute? The protocol audit table records these for direct alignment methods; a separate attack-paper table records attack construction and access. Do not treat a number as reproducible if model version, judge, or decoding details are missing. See audit Section 3 and its “Attack-paper protocol audit.”

## Slide 12 — The defensible gap is a controlled small-model study (1:00)

“We should not claim that no one has aligned VLMs or that no one has trained against adversarial attacks. Those claims are disproven by work such as ADPO, SPA-VL, and recent label-free approaches. The more careful gap is a controlled small-model comparison: does alignment transfer across unseen visual carriers, does it preserve calibration, and what is the compute cost? Our contribution can be a reproducible answer rather than an overclaimed new defense.”

**Positioning guardrail:** Existing work already covers multimodal SFT, preference data, adversarial preference alignment, representation correction, prompt rewriting, label-free training, safety reasoning, and generation-time interventions. Novelty should therefore be framed around a controlled small/open-model evaluation, held-out attack-family generalization, safe-neighbor calibration, visual-grounding controls, or resource-aware comparisons only if the experiment actually tests those claims. The audit's Sections 2, 3, 7, and Addendum C.4–C.5 lay out the field and limits on defensible claims.

## Slide 13 — Proposed study protocol (1:00)

“This is a proposed workflow, not a recipe copied from one paper. The papers connect by role: training papers define B1–B5 candidates, attack papers define threat families, and benchmark papers define coverage and controls. They are not all combined into one defense. HoliSafe already contributes five-way image/text safety data, evaluation, and a visual-guard architecture, so we cannot call that training-data structure our novel idea. We should compare an available, reproduced HoliSafe-style condition against text-only SFT, ordinary multimodal SFT, and preference/adversarial baselines under a common small-model protocol. Then hold out attack families and intents, and report harmful compliance, safe false refusal, visual utility, judge agreement, and cost. This is a research question and controlled comparison, not an established result.”

**What the relationship among papers means:** The synthesis is a *division of experimental labor*, not a claim that the papers form a single pipeline: alignment methods are candidate interventions; attack papers specify attacker capabilities and input carriers; benchmarks test different safety/utility constructs; evaluator papers and metrics govern measurement validity. The proposed connection is that these components can be compared under shared checkpoints, splits, judging, and budgets. Whether any method generalizes is what the experiment tests.

**HoliSafe correction:** Its CVPR 2026 Findings paper reports 4,031 benchmark Q&A pairs over 1,796 images, all five combinations (UIUT, UIST, SIUT, SIST→U, SIST→S), training on 10,215 instruction-response pairs, and SafeLLaVA/Safe-VLM variants with a visual guard module. This substantially overlaps the prior B5 idea. Its source-paper results and protocol are now listed in the evidence dossier; do not describe B5 as a novel data formulation.

## Slide 14 — Three falsifiable hypotheses (1:10)

“H1 tests whether existing multimodal conditions, including a HoliSafe-style five-state comparator, outperform the native checkpoint and text-only tuning on held-out attacks while preserving benign utility. H2 compares seen and held-out attack families. H3 is exploratory: does a text-versus-image safety gap explain variation across small models beyond parameter count? The contribution is the controlled comparison and transfer test, not inventing five-state data. Margins are design proposals that need preregistration.”

## Slide 15 — Proposed test matrix: attacks, attribution controls, safe pairs (1:20)

“A0 is a matched text control, not an attack. A1 is the fixed FigStep typographic image. A2 is HADES +Opt, a black-box semantic-image condition. A3 uses SIUO/HoliSafe to evaluate compositional risk, not to claim a new attack. A4 pairs VLSBench image ablations with safe-neighbor calibration. A5 is adaptive PolyJailbreak. We report each as its own row. White-box HADES +Adv, ADPO perturbations, and JailBound remain optional, separate diagnostics.”

## Slide 16 — Compare methods on the same model and same budget (1:20)

“B0 is the native checkpoint; B1 text-only SFT; B2 multimodal SFT; B3 standard DPO; B4 ADPO if reproducible; B5 a HoliSafe-style five-state/Safe-VLM comparator, separating data-only from VGM if possible. B5 is prior art, not our claimed invention. Freeze exact model revisions, processors, templates, training budget, and held-out evaluation before running.”

## Slide 17 — Report safety, utility, calibration, and cost together (1:10)

“The primary safety outcome is harmful-compliance rate by family, with confidence intervals. The benign side includes refusal rate and answer quality. Utility includes a compact VQA/OCR set before and after alignment. We also compare text-only, image-only, and joint-input behavior to quantify the modality gap. Evaluation reliability matters: use a blind classifier, validate a stratified subset with human review, and publish judge disagreement. Finally, measure training and runtime cost, especially if adding a guard model or reasoning step.”

## Slide 18 — What we expect to contribute (1:40)

“The project should produce four things: a protocol that identifies the attack carrier; a small-model comparison that tests held-out generalization and safe near-neighbors; a paper-by-paper audit of threat model, benchmark, judge, and utility; and an empirical answer about whether additional multimodal alignment helps beyond text-only tuning. The immediate next steps are to freeze model checkpoints and the harm rubric, reproduce the simplest baselines first, validate the evaluator, and only then run the held-out attacks. That order protects us from spending the whole project debugging a novel method before we know whether the measurement works.”

## Slide 19 — Primary literature and source conventions (as needed)

"The bracketed citations point to the IEEE bibliography. The guide and evidence dossier map every paper’s role and reading targets, and clearly mark which exact result tables have been transcribed versus still needing source verification. We distinguish published proceedings from preprints and tie each result to its own protocol."

## Evidence appendix (slides 20–29; use for questions, not in the 20-minute run)

These slides are backup material. Present only the table relevant to a question. The values are transcribed from each paper and are **not a common leaderboard**: the datasets, target versions, judges, decoding, and metric definitions differ.

### Slide 20 — Attachment audit

“I reviewed the files attached to the project. The two SafeVLM PDFs are copies of one paper. The VLMGuard-R1 PDF is an earlier arXiv version of the later Findings ACL paper. The gradient-selection paper and its write-up address language-only models, so they are project history and not VLM result evidence. The old presentation also is not an academic source. That leaves two unique direct VLM-safety papers among the local attachments; the wider literature review adds the other published studies.”

### Slide 21 — SafeVLM results

“SafeVLM reports a rise in GPT-judged RTVLM average from 6.39 for LLaVA to 8.18 or 8.26 for its two variants. Its separate risk-set average also rises. This is evidence for its own method and test setup, not a cross-paper rank. The capability scores move in different directions: MMBench and SEEDBench rise, while MME perception and aggregate MME fall. Keep those metrics visible rather than hiding the trade-off in a composite.”

### Slide 22 — SafeVLM over-refusal warning

“The attack table is text-only: AdvBench vanilla and suffix prompts, plus XSTest safe and unsafe instructions. SafeVLM lowers unsafe compliance, but its safe-instruction pass rate falls from 91.20% to about 77–78%. That is a meaningful calibration cost. It is also why our experiment needs visual safe near-neighbors and false-refusal reporting. This table does not establish visual-jailbreak robustness.”

### Slide 23 — VLMGuard-R1 selected results

“VLMGuard-R1 is a trained upstream rewriter. It sees image and prompt, rewrites the prompt, and calls the target model with the original image. The downstream VLM weights are not what the method aligns. Several GPT-4o safety and helpfulness cells improve, but Qwen2-VL helpfulness on SIUO falls from 60.24 to 53.61. That counterexample is important: improvements are not guaranteed on every cell. Also count the rewriter’s compute, calls, and latency.”

### Slide 24 — VLMGuard-R1 DSR caveat

“The supplementary defense-success-rate table favors VLMGuard-R1, but DSR here detects a set of refusal strings. It is not interchangeable with a semantic judgment that the answer materially enables harm. A model can score well by refusing formulaically. Read DSR beside the GPT-4o safety/helpfulness evaluation, and in our work audit refusal quality and false refusals directly.”

### Slide 25 — ADPO results

“ADPO is direct prior art for adversarial safety alignment, so our novelty cannot be that nobody has trained against VLM attacks. The selected rows show sizeable attack-rate drops for LLaVA and Qwen2-VL under the authors’ VisualAdv, MMPGDBlank, and MultiTrust test subsets. Utility scores also move, with some decreases. The correct conclusion is that ADPO works strongly in its reported protocol and deserves reproduction or comparison; it is not proof of universal robustness.”

### Slide 26 — Benchmark cards

“Each benchmark has a distinct job. MM-SafetyBench provides broad synthetic risk scenarios and image-carrier variants. SIUO targets composition but is only 167 examples. VLSBench controls leakage to test whether the image matters. VSCBench pairs under-safety with over-safety. USB has broad risk-by-modality coverage, while MMJailBench factorizes input attributes and is a preprint at this literature snapshot. Select slices based on the research question and preserve their original metrics.”

### Slide 27 — Proposed test cells

“This is our experiment design, not a paper’s result. A0 anchors text-only safety; A1 tests OCR-carried requests; A2 tests joint image-text composition; A3 checks leakage and grounding; A4 tests safe counterpart requests; A5 is an adaptive held-out evaluation with a fixed query budget. We separate optional white-box pixel attacks and internal boundary probing from the black-box deployment suite. The prompts, intents, templates, and budgets must be split and logged before running.”

### Slide 28 — Reporting standard

“For every method, report what was trained, on what data, and at what cost; the attacker’s access and query budget; the safety judge and its audit; per-family harmful compliance with uncertainty; benign false refusal and useful answer quality; capability before and after; and runtime costs. This allows readers to tell whether a method improves safety, refuses more broadly, ignores the image, or merely changes the system boundary.”

**Appendix sources:** SafeVLM, https://arxiv.org/abs/2405.13581; VLMGuard-R1, https://aclanthology.org/2026.findings-acl.1986/; ADPO, https://aclanthology.org/2025.findings-emnlp.735/; benchmark sources are linked in the protocol audit.

### Slide 29 — HoliSafe data and results

“HoliSafe is important for two separate reasons. Its benchmark covers five image/text states, including cases where individually safe image and text produce an unsafe joint request. Safe-VLM couples instruction tuning with a Visual Guard Module that classifies visual harmfulness. In Table 3, SafeLLaVA-7B’s mean ASR is 8.8% under the Claude judge versus 79.1% for LLaVA-v1.5-7B; safe-pair RR is 1.3% versus 1.6%. GPT-4o, Gemini, and string-match columns produce different absolute values, so keep the judge visible. Table 4 compares VLSBench, MM-SafetyBench, HarmEval, and SIUO. Our lesson is not ‘we invented five-way data’; it is to compare this prior art at small scale and test transfer under a shared, held-out protocol.”

**Dataset/method facts:** 6,689 total images and 14,246 pairs; 10,215 training pairs; 4,031 test QA pairs over 1,796 images. The authors report a two-linear-layer VGM over pooled visual tokens and joint safety-classification/next-token objectives. Check paper §§2–4, Tables 1 and 3–5, and Appendix D.1–D.2. Cite [27].

### Slide 30 — Training, data, and project-context references

“This page groups the training and data-alignment papers: VLGuard, SafeVLM, SPA-VL, ADPO, Think in Safety, VSFA, HoliSafe, DAVSP, and Pragma-VL. References 28 and 29 are especially important recent peer-reviewed methods: DAVSP optimizes a padded visual safety prompt using activation-space supervision; Pragma-VL trains safety/helpfulness arbitration using risk-aware SFT and query-dependent reward weighting. Reference 26 is included only as project-history context; it is LLM-only, not VLM evidence.”

### Slide 31 — Inference and runtime defense references

“This page groups representation correction, reasoning-driven prompt rewriting, test-time alignment, decoding interventions, and token-level selective defenses. It mixes peer-reviewed papers and preprints, so preserve the publication-status labels.”

### Slide 32 — Attack and red-teaming references

“This page groups the image-carrier, visual-semantic, benchmark-collection, adaptive black-box, and internal-boundary attack work. These papers define different attacker capabilities; do not treat their scores as one comparable leaderboard.”

### Slide 33 — Benchmark and dataset references

"This page groups the broad safety, leakage, calibration, compositional, ecological, and risk-by-modality evaluations. HoliSafe belongs here as both a five-combination benchmark and a training resource; its method is cross-listed on the training page. SPA-VL and VLGuard are also resources in the benchmark audit. Use the protocol audit for the detailed dataset cards and caveats."

### Slide 34 — Recent alignment method references

“DAVSP and Pragma-VL are direct peer-reviewed alignment-method papers added in this literature pass. DAVSP uses a padded visual prompt trained with activation-space supervision; Pragma-VL uses risk-aware cold-start training and query-dependent reward weighting to arbitrate safety and helpfulness. They are distinct methods with different training and deployment assumptions. Read both before proposing a method claim; exact Pragma-VL paper results still need full table-level extraction in our audit.”

### Slide 35 — Attack protocol: freeze cases before querying targets

“This appendix is the operational version of the attack plan. We first create an intent ledger and split by source intent before any rendering or image transformation. Then we lock one fixed text control, FigStep images, and HADES black-box +Opt artifacts. Image removal, masking, decoys, image-only/text-only variants, and safe near-neighbors are attribution or calibration controls. The proposed deterministic setting and 256-token cap are our harmonization choices, not settings attributed to each source paper. HADES +Adv requires white-box access and must not be reported with black-box outcomes.”

### Slide 36 — Adaptive protocol and success adjudication

“For each source intent and target, our proposed PolyJailbreak budget is up to five discovery calls plus fifteen optimization calls, twenty target calls total, stopping after the first adjudicated success for the primary endpoint. The paper’s T_max=15 refers to optimization steps; our extra discovery allowance is a proposal, not its native setting. We retain all call logs and show success against query count. A frozen semantic judge is blinded to alignment arm, ambiguous cases are human-adjudicated, and uncertainty is bootstrapped over source intents. False refusal, grounding, capability, latency, and cost remain separate outcomes.”

### Slide 37 — Protocol gate: qualify the experiment before launch

“Before test, pin and hash benchmark versions, licenses, image artifacts, splits, target checkpoint, processor, chat template, decoding, judge, and rubric. Verify HADES artifact availability and PolyJailbreak’s final-paper/code details; pilot only on development intents. Lock the evaluator after reliability checks, then use the test set once. Keep static attacks, adaptive attacks, compositional benchmarks, leakage controls, safe pairs, and optional white-box diagnostics in separate result tables. This is a preregistration-ready plan, not an experiment we have already run.”

## Likely questions and concise answers

**Is the novelty just extending an LLM method to VLMs?**  
No. The proposed study is grounded in VLM-specific threats and compares existing multimodal alignment families. The prior LLM method is not assumed to transfer.

**Why not use only MM-SafetyBench?**  
It is useful broad coverage, but a single benchmark cannot distinguish image reading, prompt leakage, cross-modal composition, adaptive generalization, and over-refusal. We add targeted controls.

**Why include attacks and benign cases together?**  
Because refusal-only optimization can look safe while destroying helpfulness. Safety and utility must be measured jointly.

**Is ADPO already the answer?**  
It is a strong directly relevant baseline, not proof of universal robustness. It uses specific models, attacks, training, and evaluation choices; the proposed study asks about small-model transfer under a common held-out protocol.

**What if we cannot reproduce ADPO?**  
Report that limitation, retain B0–B3, and use a published compatible checkpoint only if its base model, license, and protocol match. Do not label an unreproduced paper number as our result.

**Why include SafeRI?**  
It is a September 2026 preprint that signals current direction toward selective token-level intervention. Mention it as emerging work, not established peer-reviewed SOTA.

**What is the minimum viable experiment?**  
One model family at two sizes, B0–B3, the A0–A5 suite, a validated evaluator, and cost reporting. Add methods only after this core protocol works.
