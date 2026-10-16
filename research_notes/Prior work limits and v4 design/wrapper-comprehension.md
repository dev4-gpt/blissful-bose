# Wrapper wording, content specificity and comprehension confounds

Status tags: VERIFIED = arXiv abstract/page or HTML opened by me (abstract-level unless stated); SNIPPET = seen only in search results; UNVERIFIED = not opened. Fetches returned abstracts mostly, so "VERIFIED" here means abstract or section text, not full-paper reading. Nothing below is from a full-text read except SORRY-Bench (HTML, first 100k chars).

## Source table

| Source (arXiv) | What it did | NOT controlled | Limitation that matters for us | Status |
|---|---|---|---|---|
| SORRY-Bench 2406.14598 | 440 unsafe prompts, 44 topics; 20 mutations (question, slang, technical terms, role play, persuasion, ciphers, languages) on 50+ LLMs | Mutations are LLM paraphrases, run on a model subset, one temperature; no over-refusal measure | Question form changes refusal by only ~2-13 points; technical terms raise fulfilment 8-19 points; persuasion up to ~60 points on GPT-4o. So wording moves refusal, but "list steps" was not tested. Authors admit garbled cipher outputs are scored as refusal, a direct comprehension-as-safety confound | VERIFIED (HTML, partial) |
| StrongREJECT 2402.10260 | Prompt set plus rubric evaluator; shows prior metrics overstate jailbreaks | Not about wrappers | Jailbreaks that bypass safety often degrade capability. Supports scoring usefulness, not just non-refusal, in our judge | VERIFIED (abstract) |
| XSTest 2308.01263 | 250 safe + 200 unsafe contrast prompts to expose surface-feature refusal | Not multimodal | Justifies a matched benign control set: if the generic wrapper alone triggers or suppresses refusal on benign phrases, wrapper effects are not about harm | VERIFIED (abstract) |
| Mood Matters 2608.05409 | Behavioural and causal mediation on 16 models up to 70B; refusal partly conditioned on syntactic form | Abstract does not state the form-by-form comparison; no VLMs | Closest direct evidence that grammatical mood, independent of content, shifts refusal. Search snippet said imperative gave the highest refusal rate (SNIPPET only). Need full text before citing numbers | VERIFIED (abstract) / SNIPPET (imperative claim) |
| MSTS 2501.10057 | 400 text+image prompts, 40 hazards, open VLMs, 10 languages | Reading ability not measured separately | States some models look safe only because they fail to understand simple prompts, and models were safer with text alone. Our reading-success check (88-93%) is the right response, but it must be per condition | VERIFIED (abstract) |
| MMJailBench 2608.25490 | Factorized benchmark separating intent, framing, visual content, instruction format; 16 models | Single-model mechanism analysis; full text not readable by me | Abstract: prompt framing is the largest source of variation, and rendering instructions as images did not consistently raise susceptibility vs text. Strongest published support for our hypothesis; check whether their image render is comparable | VERIFIED (abstract) |
| Lingua-SafetyBench 2601.22737 | 100,440 image-text pairs, 10 languages, 11 open VLMs, image- vs text-dominant split | Semantic pairing vs typography; reading not isolated | Shows risk source (image vs text) interacts with language; typography-centric prior sets noted as a gap. Not a wrapper test | SNIPPET |
| 2604.25102 (Balakrishnan, Mendapara) | Typographic prompt injection; 12 font sizes, 10 transforms, 4 VLMs incl. Qwen3-VL | Correlational; embedding distance not causal | Explicitly decomposes success into perceptual readability and safety alignment; 6px text gives near-zero ASR on strong models. Supports reporting OCR success as a covariate | VERIFIED (abstract) |
| 2604.12371 (Reading Between the Pixels) | 1,000 SALAD-Bench prompts, 4 VLMs, text vs image attack, fonts 6-28px | One benchmark, 4 models, only one small | GPT-4o text attacks 36% vs image 8%; Claude 47% vs 22%; Qwen3-VL and Mistral similar across modalities. Modality gap is model-dependent; Qwen3-VL-4B shows none | VERIFIED (abstract/page) |
| Azulay et al. (ICML 2026, PMLR v306) | Four visual jailbreaks; visual cipher 40.9% vs text cipher 10.7% on Claude-Haiku-4.5 | Page gives no wrapper or comprehension controls | Cipher vs cipher contrast is a decoding-task difference, not plain text vs plain-text-in-image. No arXiv ID obtained | VERIFIED (page) |
| Text2VLM 2507.20704 | Converts text datasets to typographic-image prompts | Abstract silent on OCR | Reported (SNIPPET) both a refusal drop and that models read typographic input worse than text, plus a drop even among understood prompts | VERIFIED (abstract) / SNIPPET (details) |
| MM-SafetyBench 2311.17600 | 1,680 questions, text / SD / SD+TYPO / TYPO; question rewritten to noun-phrase "steps to / list of" form | Wrapper and rewriting confounded with modality | Source of our wrapper. Its text-only baseline uses the original question, not the rewritten phrase plus wrapper, so the "gap" mixes content form and modality | VERIFIED (abstract); template form SNIPPET |
| FigStep 2311.05608 | Typographic list-completion prompt, 82.5% ASR on 6 LVLMs | Abstract mentions no same-text control | Its prompt asks the model to complete numbered list steps, i.e. the same "list steps" frame. Wrapper could be doing the work | VERIFIED (abstract) |
| Xu et al. 2410.12662 | Toxic images handled worse than same-meaning toxic text; hidden-state shift | Mechanism, not wording | Supports a genuine modality effect exists in some models; our factorial test must show how much remains after wrapper control | SNIPPET |

I did not find usable pages for: an Azulay arXiv ID, Lingua full text, MMJailBench body text.

## Answer 1: best existing evidence that wrapper wording, not modality, drives drops

1. MMJailBench 2608.25490 (abstract): framing is the largest variance source and image-rendered instructions did not consistently beat text. Best single source; verify in the body.
2. Mood Matters 2608.05409: refusal partially depends on syntactic form independent of content in text-only LLMs, so a wrapper effect is plausible without any image.
3. SORRY-Bench: wording mutations alone move fulfilment by 2-65 points.
4. 2604.12371: Qwen3-VL-4B and Mistral showed similar success text vs image, so a large modality gap is not universal; and GPT-4o/Claude gaps coexist with readability effects.
5. MM-SafetyBench/FigStep design: the image condition changes content form and wrapper together. No source I found runs the full wrapper x content x modality factorial, so our test would fill a gap (UNVERIFIED claim of novelty; check 2025-2026 work again before asserting).

## Answer 2: recommended wrappers and controls

- Wrappers: (a) generic imperative as used now; (b) neutral descriptive, e.g. "Here is a phrase: <X>. What is this phrase about?" kept free of "steps", "list", "perform"; (c) neutral question, "What does the following say?" plus a separate answer-the-content variant; (d) no wrapper (bare phrase) as floor.
- Content: full question; key phrase; and a third, paraphrased-to-noun-phrase full content so MM-SafetyBench's rewrite is separated from phrase truncation.
- Identical strings in both modalities: same wrapper text typed in the prompt, only the content moves into the image. Keep a fixed instruction channel (text) for all conditions, plus an "image-wrapper" arm for completeness.
- Matched benign controls (XSTest-style): benign phrases through every cell, to show the wrapper does not itself cause refusals or compliance.
- Comprehension: per-cell transcription/OCR check using the same model, and a "describe what is being asked" probe; analyse refusal only on read-correctly items, and report both.
- Judge: score refusal, compliance and "off-topic or misunderstood" as separate classes (MSTS, StrongREJECT lessons); report StrongREJECT-style usefulness.
- Stats: paired by item, interaction term wrapper x modality, bootstrap CIs; fixed decoding with several seeds (SORRY-Bench flagged single-temperature).
- Non-Qwen model: pick one where 2604.12371-type modality gap is known (GPT-4o-like) and one without, if feasible.

## Answer 3: remaining confounds

- Out-of-context phrase: a key phrase alone is ungrammatical, so the model may treat it as a topic rather than a request. Control with a bare-phrase arm and a benign-phrase arm.
- Length and token position: the image carries tokens (image tokens vs few text tokens) and the harmful content moves from prompt end/middle to the vision span. Match text length by padding with neutral text; vary order (image before/after text).
- Font, resolution, contrast, line wrapping: legibility differs between short phrase and long question images (2604.25102 shows font effects). Fix one rendering, test two sizes.
- OCR success is not comprehension: reading text correctly does not imply grasping intent (MSTS). Use an explicit meaning probe.
- Qwen-specific system prompt and chat template differences between text and image inputs.
- Dataset contamination and MM-SafetyBench category differences (some categories are not refusable by design, e.g. legal/financial advice).
- Judge bias on short or off-topic replies; validate with human-labelled sample.
- Wrapper semantic content "perform this activity" implies a harmful task even for the phrase; neutral wrappers may swing the effect the other way, so report both directions.

## Sources
- arXiv 2406.14598, 2402.10260, 2308.01263, 2501.10057, 2608.25490, 2601.22737, 2604.25102, 2604.12371, 2507.20704, 2311.17600, 2311.05608, 2410.12662, 2608.05409
- Azulay et al., "Jailbreaking Vision-Language Models Through the Visual Modality", https://proceedings.mlr.press/v306/azulay26a.html (no arXiv ID found)
- Also seen in search only (not opened): 2601.17911, 2510.01259
