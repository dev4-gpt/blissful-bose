# Speaker Notes: Safety Alignment for Small Vision-Language Models

**Target duration:** about 20 minutes, 18 core slides plus evidence appendix and references.  
**Companion:** [`VLM_Safety_Alignment_Research_Proposal_Updated.pptx`](../VLM_Safety_Alignment_Research_Proposal_Updated.pptx)  
**Detailed protocol and benchmark audit:** [`../docs/vlm_safety_protocol_audit.md`](../docs/vlm_safety_protocol_audit.md)  
**Literature snapshot:** 30 September 2026.

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

**Context if asked:** The literature is not one linear leaderboard. It spans (i) attack construction, (ii) safety datasets and preference alignment, (iii) explanations of why safety degrades across modalities, (iv) training-time and inference-time defenses, and (v) evaluation validity and calibration. In the audit, see Section 2 for the family map and timeline; Section 3 for paper-level protocols. The 2026 entries are not all equivalent in maturity: USB, VSFA, and VLMGuard-R1 are peer-reviewed proceedings, while MMJailBench and SafeRI are preprints in this snapshot.

## Slide 6 — Current methods intervene at different system layers (1:20)

“This taxonomy is organized by where the intervention acts. Training-time methods change data or objective: SFT, preference optimization, and adversarial DPO. Representation methods act on internal states. Input guards inspect or rewrite the prompt before the target model. Reasoning methods explicitly interpret risk or use threat-image exposure to shape behavior. Decode-time methods alter generation or activate a safety module only on risky trajectories. These are not interchangeable: a preprocessor can improve the system while leaving the target model unchanged, and its latency and failure modes must be counted.”

**Method-family detail:**
- **Data and objective:** VLGuard uses multimodal safety-instruction tuning; SafeVLM adds a safety projector/tokens/head; SPA-VL supplies chosen/rejected multimodal preference pairs; ADPO explicitly trains with adversarial preferences. VSFA is a different training hypothesis: neutral VQA examples around threat-related images, without explicit safety labels.
- **Representation and activation:** CMRM diagnoses and corrects cross-modal representation mismatch at inference; MMAligner calibrates unsafe multimodal representations toward a refusal region. These intervene at a different layer from preference training.
- **Input and reasoning:** VLMGuard-R1 uses an upstream reasoning-guided rewriter; GuardAlign combines unsafe-region detection and attention calibration. Think in Safety studies safety reasoning, with additional token cost and possible reasoning leakage.
- **Generation-time controls:** SafetyReminder uses a safety reminder/soft-prompt intervention; SafeSteer changes decoding; SafeRI proposes a streaming recognizer with gated LoRA activation. Treat SafeRI as a preprint at the snapshot date. These runtime approaches are not direct apples-to-apples training baselines.

**Comparison rule:** Label each result as model-intrinsic training or a system-level defense. Record changed target weights, extra models, trainable parameters, additional tokens/calls, latency, and whether the intervention runs on every request. See audit Sections 2–3; for continual-learning alternatives and trade-offs, see [methodology_comparison.md](../docs/methodology_comparison.md), especially its taxonomy and comparison tables.

## Slide 7 — Training-time papers are not interchangeable (1:20)

“VLGuard gives us a natural multimodal safety-SFT baseline; SafeVLM adds an architectural safety module. SPA-VL contributes preference examples across multiple safety domains, so it is a data resource and a route to DPO. ADPO is especially important: it is already a direct adversarial preference-alignment method, combining an adversarially trained reference model with an adversary-aware preference objective. VSFA, published at ACL 2026, offers a different hypothesis: neutral VQA around threat-related images may induce caution without explicit safety labels. We must include or at least discuss it before proposing a training novelty.”

**What the comparison means:** These methods change different things. Separate (1) safety data plus ordinary SFT, (2) preference data plus standard DPO, (3) adversarial preference optimization, (4) architectural safety components, and (5) label-free/neutral-VQA training. ADPO is the clearest direct adversarial-training comparator; it reports white-box VisualAdv and MMPGDBlank plus black-box MultiTrust subsets and a HarmBench classifier, alongside utility tests. SPA-VL is primarily a preference dataset/resource, not an attack algorithm. VSFA is a newer peer-reviewed, label-free alignment alternative. SafeVLM's safety module is architectural and should not be described as plain SFT. Full protocols and caveats are in audit Section 3 and Addendum A.2–A.4.

## Slide 8 — Runtime defenses change the system boundary (1:00)

“CMRM and MMAligner are representation interventions. VLMGuard-R1 adds an upstream reasoning-based rewriting component. SafetyReminder and SafeSteer work at the prompt or decoding level; SafeRI is a very recent preprint proposing a token-level recognizer and gated LoRA. A fair comparison must state whether the target model weights changed, whether a second model was added, whether the method operates every token, and how latency and trigger mistakes affect safe examples. These distinctions matter especially for small deployment.”

**Newer methods to keep in the account:** GuardAlign is an input/internal hybrid (unsafe-region detection plus attention calibration), not simply a prompt filter. Think in Safety is a reasoning/data approach. SafeSteer is decoding-level intervention; SafeRI is a September 2026 arXiv preprint and must be labeled as emerging. These additions belong in the related-work/methodology comparison even when the 20-minute narrative cannot give each a full slide. See audit Section 2 and [methodology_comparison.md](../docs/methodology_comparison.md).

## Slide 9 — A jailbreak suite must vary the carrier (1:00)

“The attacks are selected to isolate different phenomena. Direct text is our control. FigStep carries the request in image text. SIUO-style cases test joint interpretation, while HADES is a semantic visual exploit. A held-out adaptive method such as PolyJailbreak tests whether a model generalizes beyond fixed templates. White-box pixel attacks and JailBound are optional diagnostics because they require additional access and represent different threat models. We should report each family separately, not combine everything into a single opaque attack score.”

## Slide 10 — Benchmarks answer different questions (1:30)

“The four primary benchmark choices are complementary. USB is broad risk-by-modality coverage and includes over-refusal. VSCBench measures paired safe and unsafe behavior. VLSBench addresses visual safety information leakage: does the test require the image? SIUO is smaller but directly examines safe inputs whose combination creates a risk. MMJailBench is a 2026 preprint that factorizes intent, framing, visual semantics, and carrier. It is an excellent design reference, but its preprint status should be visible in the talk.”

**Selection logic:** Use a broad benchmark for coverage, paired safe/unsafe cases for calibration, a leakage-controlled set for visual dependence, and a targeted composition set for interaction risk. MM-SafetyBench and JailBreakV are useful attack-suite sources but are not substitutes for safe-neighbor evaluation. MemeSafetyBench adds ecological real-meme cases but has marked class imbalance; report balanced/class-specific metrics. Capability and hallucination diagnostics should be reported separately from harmful-compliance benchmarks. Do not average unlike measures into one score. Dataset sizes, examples, roles, and caveats are in audit Section 5 and Addendum B.1.

## Slide 11 — Protocol audit: ADPO is a useful reproduction template (1:10)

“ADPO is a good example of what a useful protocol description looks like. It names its model panel and LoRA approach; it tests two optimization-based attacks and the typographic, multimodal, and cross-modal portions of MultiTrust; it uses the HarmBench classifier to label harmful responses; and it measures utility on four visual benchmarks. It also compares against SFT, standard DPO, a training-free defense, and direct adversarial training, plus component ablations. The result is not just a claimed safety gain: the paper also reports utility trade-offs. Our protocol audit asks the same questions for every paper.”

**Audit checklist applied across papers:** What is the intervention and system boundary? Which base checkpoints, processors, and chat templates? What training data and split? Which attack families and attacker access/query budget? What judge, rubric, and human validation? Which benign utility tests? What ablations and compute? The protocol audit table records these for direct alignment methods; a separate attack-paper table records attack construction and access. Do not treat a number as reproducible if model version, judge, or decoding details are missing. See audit Section 3 and its “Attack-paper protocol audit.”

## Slide 12 — The defensible gap is a controlled small-model study (1:00)

“We should not claim that no one has aligned VLMs or that no one has trained against adversarial attacks. Those claims are disproven by work such as ADPO, SPA-VL, and recent label-free approaches. The more careful gap is a controlled small-model comparison: does alignment transfer across unseen visual carriers, does it preserve calibration, and what is the compute cost? Our contribution can be a reproducible answer rather than an overclaimed new defense.”

**Positioning guardrail:** Existing work already covers multimodal SFT, preference data, adversarial preference alignment, representation correction, prompt rewriting, label-free training, safety reasoning, and generation-time interventions. Novelty should therefore be framed around a controlled small/open-model evaluation, held-out attack-family generalization, safe-neighbor calibration, visual-grounding controls, or resource-aware comparisons only if the experiment actually tests those claims. The audit's Sections 2, 3, 7, and Addendum C.4–C.5 lay out the field and limits on defensible claims.

## Slide 13 — Three falsifiable hypotheses (1:10)

“H1 tests whether matched multimodal alignment beats the unmodified model and text-only safety tuning on held-out attacks while preserving benign utility. H2 tests whether gains on seen patterns overstate robustness by comparing them with attack families held out entirely. H3 is exploratory: we ask whether a text-versus-image safety gap explains variation across small models beyond parameter count. The suggested margins shown here are design proposals, not established standards; choose them with the advisor and preregister them before test runs.”

## Slide 14 — Final attack suite (1:20)

“The six required cells are the minimum suite: direct text, image-carried text, joint-context risk, a leakage-controlled test, benign matched pairs, and one adaptive held-out attack. That gives coverage over baseline safety, OCR, compositional reasoning, benchmark validity, over-refusal, and generalization. If compute and model access permit, add one fixed-budget white-box perturbation and optionally a representation-boundary diagnostic. Keep those results separate from the deployment-realistic black-box tests.”

## Slide 15 — Compare methods on the same model and same budget (1:20)

“The baseline sequence is designed to make each comparison interpretable. B0 is the native checkpoint. B1 asks how far text safety transfers. B2 is multimodal SFT. B3 is standard preference alignment. B4 is ADPO, if we can reproduce it or use a compatible release. B5 is our proposed matched cross-modal condition. As current candidates, compare Qwen3-VL 2B and 4B within a family, and use SmolVLM2 2.2B only as an external replication. The exact model revisions, processors, and chat templates must be frozen at experiment start. Use the same base model, preprocessing, data size or a transparent data-size curve, tuning policy, and held-out evaluation.”

## Slide 16 — Report safety, utility, calibration, and cost together (1:10)

“The primary safety outcome is harmful-compliance rate by family, with confidence intervals. The benign side includes refusal rate and answer quality. Utility includes a compact VQA/OCR set before and after alignment. We also compare text-only, image-only, and joint-input behavior to quantify the modality gap. Evaluation reliability matters: use a blind classifier, validate a stratified subset with human review, and publish judge disagreement. Finally, measure training and runtime cost, especially if adding a guard model or reasoning step.”

## Slide 17 — What we expect to contribute (1:40)

“The project should produce four things: a protocol that identifies the attack carrier; a small-model comparison that tests held-out generalization and safe near-neighbors; a paper-by-paper audit of threat model, benchmark, judge, and utility; and an empirical answer about whether additional multimodal alignment helps beyond text-only tuning. The immediate next steps are to freeze model checkpoints and the harm rubric, reproduce the simplest baselines first, validate the evaluator, and only then run the held-out attacks. That order protects us from spending the whole project debugging a novel method before we know whether the measurement works.”

## Slide 18 — Primary literature and source conventions (as needed)

"The bracketed citations on each slide point to the IEEE-style numbered bibliography at the end. We deliberately distinguish peer-reviewed proceedings from arXiv preprints, and we keep each paper’s reported score attached to its own model and evaluation protocol. The audit is the synthesis; the linked VLM_PAPER_READING_GUIDE.md maps every numbered reference to the sections, figures, and tables to inspect in the original paper."

## Evidence appendix (slides 19–27; use for questions, not in the 20-minute run)

These slides are backup material. Present only the table relevant to a question. The values are transcribed from each paper and are **not a common leaderboard**: the datasets, target versions, judges, decoding, and metric definitions differ.

### Slide 19 — Attachment audit

“I reviewed the files attached to the project. The two SafeVLM PDFs are copies of one paper. The VLMGuard-R1 PDF is an earlier arXiv version of the later Findings ACL paper. The gradient-selection paper and its write-up address language-only models, so they are project history and not VLM result evidence. The old presentation also is not an academic source. That leaves two unique direct VLM-safety papers among the local attachments; the wider literature review adds the other published studies.”

### Slide 20 — SafeVLM results

“SafeVLM reports a rise in GPT-judged RTVLM average from 6.39 for LLaVA to 8.18 or 8.26 for its two variants. Its separate risk-set average also rises. This is evidence for its own method and test setup, not a cross-paper rank. The capability scores move in different directions: MMBench and SEEDBench rise, while MME perception and aggregate MME fall. Keep those metrics visible rather than hiding the trade-off in a composite.”

### Slide 21 — SafeVLM over-refusal warning

“The attack table is text-only: AdvBench vanilla and suffix prompts, plus XSTest safe and unsafe instructions. SafeVLM lowers unsafe compliance, but its safe-instruction pass rate falls from 91.20% to about 77–78%. That is a meaningful calibration cost. It is also why our experiment needs visual safe near-neighbors and false-refusal reporting. This table does not establish visual-jailbreak robustness.”

### Slide 22 — VLMGuard-R1 selected results

“VLMGuard-R1 is a trained upstream rewriter. It sees image and prompt, rewrites the prompt, and calls the target model with the original image. The downstream VLM weights are not what the method aligns. Several GPT-4o safety and helpfulness cells improve, but Qwen2-VL helpfulness on SIUO falls from 60.24 to 53.61. That counterexample is important: improvements are not guaranteed on every cell. Also count the rewriter’s compute, calls, and latency.”

### Slide 23 — VLMGuard-R1 DSR caveat

“The supplementary defense-success-rate table favors VLMGuard-R1, but DSR here detects a set of refusal strings. It is not interchangeable with a semantic judgment that the answer materially enables harm. A model can score well by refusing formulaically. Read DSR beside the GPT-4o safety/helpfulness evaluation, and in our work audit refusal quality and false refusals directly.”

### Slide 24 — ADPO results

“ADPO is direct prior art for adversarial safety alignment, so our novelty cannot be that nobody has trained against VLM attacks. The selected rows show sizeable attack-rate drops for LLaVA and Qwen2-VL under the authors’ VisualAdv, MMPGDBlank, and MultiTrust test subsets. Utility scores also move, with some decreases. The correct conclusion is that ADPO works strongly in its reported protocol and deserves reproduction or comparison; it is not proof of universal robustness.”

### Slide 25 — Benchmark cards

“Each benchmark has a distinct job. MM-SafetyBench provides broad synthetic risk scenarios and image-carrier variants. SIUO targets composition but is only 167 examples. VLSBench controls leakage to test whether the image matters. VSCBench pairs under-safety with over-safety. USB has broad risk-by-modality coverage, while MMJailBench factorizes input attributes and is a preprint at this literature snapshot. Select slices based on the research question and preserve their original metrics.”

### Slide 26 — Proposed test cells

“This is our experiment design, not a paper’s result. A0 anchors text-only safety; A1 tests OCR-carried requests; A2 tests joint image-text composition; A3 checks leakage and grounding; A4 tests safe counterpart requests; A5 is an adaptive held-out evaluation with a fixed query budget. We separate optional white-box pixel attacks and internal boundary probing from the black-box deployment suite. The prompts, intents, templates, and budgets must be split and logged before running.”

### Slide 27 — Reporting standard

“For every method, report what was trained, on what data, and at what cost; the attacker’s access and query budget; the safety judge and its audit; per-family harmful compliance with uncertainty; benign false refusal and useful answer quality; capability before and after; and runtime costs. This allows readers to tell whether a method improves safety, refuses more broadly, ignores the image, or merely changes the system boundary.”

**Appendix sources:** SafeVLM, https://arxiv.org/abs/2405.13581; VLMGuard-R1, https://aclanthology.org/2026.findings-acl.1986/; ADPO, https://aclanthology.org/2025.findings-emnlp.735/; benchmark sources are linked in the protocol audit.

### Slide 28 — Training, data, and project-context references

"This page groups the training and data-alignment papers: VLGuard, SafeVLM, SPA-VL, ADPO, Think in Safety, and VSFA. Reference 26 is included only as project-history context; it is LLM-only, not VLM evidence. Citation numbers remain the same as on the slides."

### Slide 29 — Inference and runtime defense references

“This page groups representation correction, reasoning-driven prompt rewriting, test-time alignment, decoding interventions, and token-level selective defenses. It mixes peer-reviewed papers and preprints, so preserve the publication-status labels.”

### Slide 30 — Attack and red-teaming references

“This page groups the image-carrier, visual-semantic, benchmark-collection, adaptive black-box, and internal-boundary attack work. These papers define different attacker capabilities; do not treat their scores as one comparable leaderboard.”

### Slide 31 — Benchmark and dataset references

“This page groups the broad safety, leakage, calibration, compositional, ecological, and risk-by-modality evaluations. SPA-VL and VLGuard are listed on the training page because their primary role here is alignment data/method; they also appear as resources in the benchmark audit. Use the protocol audit for the detailed dataset cards and caveats.”

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
