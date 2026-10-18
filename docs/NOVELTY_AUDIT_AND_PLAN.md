# Novelty audit and "unstoppable" plan (2026-10-18)

Purpose: say what we have actually done, check each claim against **verified** prior work (this supersedes the second-hand literature in `docs/PRIOR_WORK_AND_V5_PLAN.md`), and decide which ideas are new enough to carry a paper. Method: about 14 web searches and 7 page fetches on 2026-10-18. Most reads are **abstract-level**; only MMJailBench was read through its HTML full text. "Not found" below means "not found in this search", not "does not exist".

## 1. What we did (one paragraph)

Six experiment versions on MM-SafetyBench (plus FigStep in v6), three small open VLMs (Qwen2-VL-2B, Qwen2.5-VL-3B, LLaVA-1.5-7B), no training. The typographic refusal gap (plain text minus typed-text image) is 0.51 / 0.30 / 0.43 and is stable across versions and labellers. Controlled grids show it is mostly a **prompt-wrapper effect** for Qwen and an **image-presence effect** for LLaVA; text and image refusal move together (no see-saw). Details and numbers: `docs/STATUS_AND_PAPER_PLAN.md`.

## 2. Verified prior art, claim by claim

| Our claim | Closest verified work | How much it overlaps | What is left for us |
|---|---|---|---|
| The typographic gap is mostly framing, not the image | **MMJailBench** (arXiv 2608.25490): 272 intents x 6 framings x 5 visual semantics x 2 carriers (TEXT vs OCR), 16 models; "prompt framing is the dominant source of variation"; rendered (OCR) instructions are **not** more harmful than direct text on average (ASR 40.6% vs 50.7%) | **High.** The headline direction is already published, on a new benchmark | Their paper builds a *new* benchmark. We would show the same confound inside the **two benchmarks the field already cites** (MM-SafetyBench, FigStep) by adding the wrapper-matched text twin. I found no paper doing that. FigStep's own paper credits the effect to visual-embedding misalignment and treats its wrapper as part of the attack |
| Any image, even irrelevant, lowers refusal in LLaVA | Liu et al. (2410.09047, ACL Findings 2025) and Yang et al. (2505.24208): blank or irrelevant images make LLaVA-class models answer harmful prompts they refuse in text; both give a **modality-gap** explanation and a fix | **High** for LLaVA | MMJailBench's own blank/noise/nature controls change ASR by **under 2.2 points on average** across 16 modern models, so presence effects are model-specific. Our LLaVA-1.5 drop (0.45 to about 0.07) vs Qwen (about 0) is a clean, controlled contrast, but the mechanism (why LLaVA?) is open |
| Refusal-direction steering restores image refusal | **MARS** (2606.31876): text-derived refusal directions transfer to images, 5 MLLMs, training-free; also CMRM (2410.09047), TGA (ICLR 2025), textual unlearning (2406.02575), SRT (2609.02082, EMNLP Findings 2026) | **Very high.** This area is saturated | Do not lead with steering. Use it only as a supporting analysis |
| Text/vision "see-saw" is not supported | No paper found that tests a text-vs-vision **trade-off** as a hypothesis; the literature talks about a safety "gap" and "transfer" | **Low** (good for novelty), but evidence is thin: 3 models, 2 benchmarks | A negative result needs breadth (10+ models) to be credible |
| Judges and guards mislabel non-answers as refusals | MMJailBench: GPT-5 judge validated against human experts (QWK 0.97). MUSE, ADVERSA, TVD-Conflict: judge disagreement concentrates at refusal vs non-answer boundaries. SpeechJBB uses a "deflected" class. I found **no VLM-specific study** of refusal vs non-answer | **Medium** | Our stimulus-aware 3-way labelling and the audit showing Qwen3Guard over-counts refusals (kappa 0.70 vs 0.79 to 0.82 for others, against one annotator) |
| Reading ability (legibility) matters | Balakrishnan et al. (2604.12371, ICLR 2026 workshop): font size 6px near-zero ASR; embedding distance correlates with ASR; text attacks beat image attacks on GPT-4o and Claude | **Medium** | Our true-size legibility (12/20/38 px) shows Qwen reads at 12 px but LLaVA does not; comprehension and safety are confounded for weak models |

Overall: **the individual findings are each partly known.** Taken together, the new part is a *controlled, retroactive audit of the benchmarks everyone uses*, plus an honest measurement-validity analysis. That is a respectable evaluation paper, not a discovery paper.

## 3. Ideas that look unquestioned (to be verified before we commit)

Each was not found in my searches. I mark novelty confidence honestly.

1. **Wrapper-matched control as a drop-in evaluation standard, applied retroactively** (confidence in novelty: medium-high). Add the text twin with the identical wrapper to MM-SafetyBench, FigStep and two more benchmarks, across 8 to 10 modern VLMs, and report how much of each published "image-attack" number survives. Reviewers like benchmark-hygiene results that change how people report numbers.
2. **Model-zoo natural experiment for the see-saw** (medium-high). Without training, run 10+ open VLMs and their text backbones; estimate coupling of text-channel and image-channel refusal across models with covariates (backbone family, parameter count, image tokens, connector type). That tests the trade-off claim at population level instead of with 2 models.
3. **Forecastability: predict image-attack success from the text twin** (high, unverified). If the text twin with the same wrapper predicts image-condition refusal (cross-model R-squared), image benchmarks add little beyond a text probe. A clean, falsifiable, cheap result that nobody seems to have tested.
4. **Image-token dose-response for the LLaVA presence effect** (medium). Vary image size, token count, and whether the image comes before or after the text. Prior work blames "the modality gap" in pretraining; a dose-response would test attention dilution vs mere presence. Needs LLaVA-class models only.
5. **Capability-adjusted refusal** (medium). Report refusal among replies that show comprehension, alongside raw refusal, so "safe because it could not read" is separated from "safe because it refused". Directly addresses the NOT_COMPREHEND confound.
6. **Images that make models safer** (medium, exploratory). Qwen2.5-VL-3B refuses more under the strong wrapper with an image than with text (0.92 vs 0.56). Nothing in the literature I found predicts this; it needs a mechanism check before it can be claimed.
7. **Refusal stability under sampling** (low-medium). Greedy decoding hides variance; a "refuses in k of 8 samples" metric is cheap and reviewers will ask for it.

## 4. What to add so reviewers cannot stop it (priority order)

1. **Match MMJailBench's open-weight model set** where it fits a T4: Qwen2.5-VL-7B, InternVL3-8B, Gemma3-12B (4-bit), LLaVA-OneVision, plus our three. Without modern models the "older small models" objection is fatal; with them our numbers are comparable to the closest paper.
2. **Finish the human audit** (the 129 borderline rows first) and recompute labeller sensitivity and specificity with Rogan-Gladen, as the plan states. MMJailBench validates its judge against human experts; we must too.
3. **Run ideas 1, 2 and 3 above** as the pre-registered core. Write them as Amendment 5 **before** the run, on fresh items not yet read.
4. **Add ideas 4 and 5 as secondary analyses** (cheap).
5. **Keep steering out of the headline.** It is saturated; use it as a one-paragraph supporting result with the over-refusal cost.
6. **Positioning sentence:** "We do not propose a new attack or benchmark; we show how much of the published typographic image-attack effect is carried by the prompt wrapper and image presence, and give a control that makes numbers comparable."

## 5. Risks to novelty and how to handle them

- **MMJailBench already says "framing dominates".** Cite it prominently, position ours as complementary (retroactive audit of existing benchmarks plus cross-model forecastability), and avoid claiming the discovery of the framing effect.
- **"Your guards are weaker than GPT-5."** Open-models-only is a stated constraint; mitigate with human audit, two guards, the keyword rule and their agreement.
- **"Small samples."** 8 scenario clusters limit sign tests; use item-level GEE and scenario-level intervals, and extend items per scenario where Colab time allows.
- **My search was shallow.** Before drafting, run a systematic search (arXiv, Semantic Scholar, ACL Anthology) for each of the 7 ideas, read MMJailBench, FigStep and MM-SafetyBench fully, and check VLSBench, USB, HoliSafe and DUAL-Bench for overlap.

## 6. Proposed next steps (no code written yet)

1. Systematic novelty search for ideas 1 to 3 (about half a day).
2. Human audit of borderline rows (you), while the next run is prepared.
3. Write Amendment 5: models, benchmarks, forecasting test, fresh items, endpoints.
4. v7 notebook (frozen v6 design plus new models, two more benchmarks, token dose-response, sampling): run in blocks, each cached.
5. Confirmatory run, analysis, paper draft. Target: workshop deadline about 20 Nov; ARR 4 Jan for the longer version.

## Sources

- MMJailBench: A Factorized Benchmark for Disentangling Multimodal Jailbreak Vulnerabilities, arXiv 2608.25490 (https://arxiv.org/abs/2608.25490; HTML read in full).
- Unraveling and Mitigating Safety Alignment Degradation of Vision-Language Models, arXiv 2410.09047.
- Bootstrapping LLM Robustness for VLM Safety via Reducing the Pretraining Modality Gap, arXiv 2505.24208 (abstract).
- Harnessing Textual Refusal Directions for Multimodal Safety (MARS), arXiv 2606.31876 (abstract).
- Transfer Safety Awareness for Cross-Modal Safety Drift in MLLMs, arXiv 2609.02082 (abstract).
- Cross-Modal Safety Alignment: Is Textual Unlearning All You Need?, arXiv 2406.02575; Cross-Modal Safety Mechanism Transfer in LVLMs (ICLR 2025); Security tensors, arXiv 2507.20994.
- Reading Between the Pixels, arXiv 2604.12371 (abstract); Text is All You Need for VLM Jailbreaking, arXiv 2602.00420 (abstract).
- FigStep (AAAI 2025, arXiv 2311.05608), MM-SafetyBench, Text2VLM (arXiv 2507.20704), VLSBench, USB, VLSU, DUAL-Bench (search results only).
- Judge reliability: MUSE (arXiv 2603.02482), ADVERSA (2603.10068), TVD-Conflict (NeurIPS 2026), SpeechJBB (2606.06037) (search snippets only).
