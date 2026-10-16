# Typographic / image-text jailbreak benchmarks: controls and limitations

Evidence tags: VERIFIED = I fetched the arXiv abs and/or HTML page and the fetch tool returned the stated content; SNIPPET = web-search result only; UNVERIFIED = not seen. Caveat: WebFetch summarises pages with a small model, so numbers are second-hand and should be re-checked against the PDF before they go into a paper. Quotes are under 15 words; no harmful content reproduced.

## Paper table

| Paper (arXiv) | Text / template-matched control? | Wrapper separated from modality? | OCR / readability check? | Models; judge | Limitations relevant to us |
|---|---|---|---|---|---|
| MM-SafetyBench 2311.17600 (VERIFIED, abs + HTML) | Yes, a "Text-only" arm (query, no image). Unclear whether it uses the original or the rephrased question. Typo query is rephrased with an extract-from-image instruction. | No. Typo/SD arms change both the image and the wording. VLSBench independently notes its prompts share an "image shows" pattern. | No readability check. Authors concede some "safe" responses come from poor OCR or weak instruction following. | 12 MLLMs (LLaVA, MiniGPT-4, Qwen-VL, ...; LLaVA-1.5 7B/13B detailed). GPT-4 judge, no agreement statistic reported. | Safe-looking responses can be capability failures; no agreement stat; modality confounded with rephrasing. |
| FigStep 2311.05608 (VERIFIED, abs + HTML) | Partial. Ablations say plain-text versions of the same content were much weaker (avg ASR 44.8% text vs 82.5% FigStep, six open LVLMs). Details of wrapper matching not visible to me. | Partly: reports the benign list-continuation prompt matters, but the fixed wrapper is part of the attack, not factored out. | No quantified OCR check; OCR-based defences tested only as defences. | Six open LVLMs (LLaVA, MiniGPT-4, CogVLM, ...); manual labels primary; AI judge gave lower ASR and misjudged some cases. | Small n (50-500); manual judge; judge disagreement; model-version drift. |
| HADES 2403.09792 (VERIFIED, abs + HTML) | Yes: "Text-only" (LLaVA-1.5 ASR 26.13%) vs "Typ image" (65.60%). | No. Typographic prompt swaps keywords for an image pointer; the paper does not say whether the template is matched. Pointer phrasing itself lowered ASR 7.47 pts. | Authors note weak-OCR models misread keywords; retried up to 5 times. | LLaVA-1.5, MiniGPT-v2/4, Gemini Pro Vision, GPT-4V. Beaver-dam-7B judge; humans checked LLaVA-1.5 only. | 750 instructions; judge validated on one model; OCR errors acknowledged but not quantified. |
| VLSBench 2411.19939 (VERIFIED, abs + HTML) | Yes, "w/o vision" and "text + caption" arms, but on its own data, not typographic. | Argues typographic benchmarks leak the harm into the text query (visual safety information leakage, VSIL), so a text-only model can refuse. | No. | 10+ open (LLaVA, Qwen2-VL, InternVL2.5, ...) and GPT-4o, Gemini-1.5, Claude 3.5. GPT-4o judge. | Not a typographic study. Important as a reviewer-cited critique: FigStep/MM-SafetyBench conflate text leakage with modality. |
| SIUO 2406.15279 (VERIFIED, abs + HTML) | No image-only/text-only controls. | N/A (safe image + safe text -> unsafe combination). | No. | 15 LVLMs (GPT-4V/4o, Gemini, LLaVA, Qwen-VL, CogVLM...). GPT-4V judge, 82.44% agreement with humans on safety. | Small (167 human + 102 AI items); GPT-4V judge unreliability. Mostly a contrast case, not a typographic one. |
| HoliSafe 2506.04704 (VERIFIED, abs + HTML, partial) | No text-only or typographic control; FigStep only discussed as covering unsafe-image/safe-text. | No. | No (OCR not mentioned). | 21 VLMs incl. LLaVA-1.5-7B, Qwen2.5-VL, InternVL2.5, Gemma3; Claude/GPT-4o/Gemini-2.0 judges + string match. | Proprietary judges; GPT-4o-generated data; appendix limitation not seen. Cite as taxonomy of image/text safety combinations. |
| MemeSafetyBench 2505.15389 (VERIFIED, abs + HTML partial) | Yes: no-image, typographic, SD, SD+Typo (from MM-SafetyBench) and meme arms, same instructions, 514 samples. Memes: 26.3% refusal vs 54.6% no-image. | Instructions held fixed, but typographic images still come with MM-SafetyBench-style framing; I could not confirm. | No OCR evaluation. | InternVL2.5 (1B-38B), Qwen2.5-VL (3/7/32B), LLaVA-1.5/1.6. WildGuard + gpt-4o-mini (task completion; 0.93 agreement). | English meme culture; closed-LLM dependence. Useful for Qwen2.5-VL typo vs no-image numbers. |
| MMJailBench 2608.25490 (VERIFIED, abs + HTML) | Yes, closest to our design: 272 intents x 6 framings x 5 visual conditions x 2 carriers (TEXT vs OCR-rendered). Overall ASR 50.70% TEXT vs 40.59% OCR. | Yes: framing varied separately; framing is the dominant factor, gap between framings >40 pts; carrier effect model-dependent, rendered text not stronger. | Yes, partial: instruction-mismatch flag (0.37% TEXT vs 4.14% OCR), excluded in conditional ASR. No separate OCR read-back test seen. | 16 models (qwen2.5-vl-7b, internvl3-8b, llava-onevision-1.5, gemma3-12b, gpt-5, claude-sonnet-4.5 ...). GPT-5 judge, QWK 0.97 vs humans. | No limitations section seen. Framings are jailbreak styles (Academic, Story, Code...), not a benign procedural wrapper like ours; no sub-3B models; no LLaVA-1.5; not 304-item MM-SafetyBench items. Posted Aug 2026; check for later versions. |
| Lingua-SafetyBench 2601.22737 (VERIFIED, abs + HTML partial) | No template-matched or text-only control for the image-dominant subset (typographic keyword renderings); text-dominant is a different condition. | No. | None reported; OCR consistency listed as future work. | 11 open VLLMs incl. Qwen2-VL 2B/7B, Qwen2.5-VL 3B/7B. GPT-5.1 + Qwen3Guard, disagreements = uncertain. | Authors admit ASR may reflect weaker capability, not safety. Reuses MM-SafetyBench typographic images, so it inherits the confound. Directly relevant to our two Qwen models. |

Additional 2025-26 papers with typographic vs text comparisons:

| Paper | Finding relevant to us |
|---|---|
| Why Does Weak-OOD Help? 2511.08367 (VERIFIED, HTML partial) | Has Vanilla-Text (blank image + plain query) vs Vanilla-Typo (fixed "fulfill the request in the image" prompt), but prompts differ, so the gap cannot be attributed to modality. Typo ASR higher on RedTeam-2K, mixed on HarmBench. Qwen2.5-VL-7B, InternVL2.5-8B, GPT-4o/4.1, Gemini 2.5 Pro; GPT-4o judge. |
| Do VLMs Share Safety Neurons Across Modalities? 2608.30750 (VERIFIED, HTML) | Neutral procedural template ("The image shows a scene of an activity..."), rendered harmful text gives 61-100% refusal vs 10-93% for natural images; attributes this to OCR reactivating the text safety pathway. No plain-text-under-same-template arm reported. 10 VLMs incl. Qwen2.5-VL, Qwen3-VL; GPT-4o judge plus keyword metric. Notes Qwen2.5-VL-7B refusal 90.7% -> 76.9% with a harmful image. Very close to our wrapper framing; must read in full. |
| Text2VLM 2507.20704 (SNIPPET only; PDF did not decode) | Claims adding an image lowers refusal and VLMs handle typographic prompts worse than text, attributed to weak OCR. Details UNVERIFIED. |
| One Perturbation, Two Failure Modes 2604.25102 (SNIPPET) | Font size matters: 6px reduces ASR, rises by 10px. Supports a legibility confound. |
| Seen but Not Refused (GitHub Aurnawr/VLM-Interp) (SNIPPET, not peer reviewed) | Reports LLaVA-1.5-7B never genuinely refused typographic images while Qwen2.5-VL-7B refused 98%. Useful for the LLaVA-1.5 expectation; not citable as a paper. |
| Beyond Text 2510.20223, Implicit Jailbreak 2505.16446, VERA-V 2510.17759 (SNIPPET) | Typographic/FigStep used as attack pipelines; I could not confirm any wrapper ablation. |

## Answers

**(1) Has anyone measured wrapper vs content vs modality?** I found no paper that does the full three-way factorial. Nearest partial attempts: MMJailBench (2608.25490) crosses prompt framing x carrier (TEXT vs rendered) and finds framing dominates and rendered text is not systematically stronger, which is consistent with our "wrapper removes most of the gap" result. FigStep's ablation (benign list prompt matters; plain-text version much weaker) is suggestive but not a clean factorial. 2511.08367 explicitly has unmatched prompts, so it confounds. 2608.30750 uses a fixed neutral template but lacks the matched plain-text arm. MemeSafetyBench varies image type with fixed instructions but not wrapper. This is a negative-search claim: I did not read every 2025-26 paper, so state it as "to our knowledge" and re-search before submission.

**(2) Known confounds to control.**
- Prompt wrapper: wording differs between text and image arms (MM-SafetyBench rephrasing, HADES pointer, FigStep list continuation, 2511.08367 fixed prompt). Hold wrapper constant across modality (our plan).
- Content leakage: harm in the text query lets the LLM refuse regardless of image (VLSBench VSIL).
- Readability/OCR: weak OCR can masquerade as "safe" (MM-SafetyBench, HADES, Lingua); font size matters (2604.25102); keep read-back rate and report conditional ASR excluding mismatches as MMJailBench does.
- Capability vs safety: low ASR from non-compliance or incoherence; need harmfulness labels, not only refusal.
- Judge: single judge/keyword refusal metrics (2608.30750 relies on one judge); judge agreement stats absent in MM-SafetyBench; use two judges with human spot-check.
- Intent selection: 2608.30750 selected intents with high text-only refusal consensus, so results hold only in a refusal-active regime.
- Over-refusal: image presence can make models stricter regardless of content (Qwen3-VL-2B per snippet); include blank-image and benign-content arms and XSTest.
- Model scale/family: Qwen vs LLaVA behave oppositely (SNIPPET); effect direction is model-dependent (MMJailBench Table 4).
- Dataset reuse: Lingua and MemeSafetyBench inherit MM-SafetyBench items, so findings are not independent.

**(3) Must cite and compare.** MM-SafetyBench (2311.17600) and FigStep (2311.05608) as the effects being decomposed; MMJailBench (2608.25490) as closest prior (cite and differentiate: benign procedural wrapper, content-matched text, sub-3B and LLaVA-1.5 models); VLSBench (2411.19939) for the leakage critique; HADES (2403.09792) for its text-only vs typographic numbers on LLaVA-1.5; MemeSafetyBench (2505.15389) for Qwen2.5-VL typographic vs no-image refusal; 2608.30750 (neutral-template, OCR-reactivates-text-safety hypothesis, Qwen2.5-VL); Lingua-SafetyBench (2601.22737) for Qwen2-VL/2.5-VL ASR on the same typographic images; 2511.08367 as an example of unmatched Text vs Typo. SIUO and HoliSafe are context only (different threat: combinations, not typography). Text2VLM only after verifying the PDF.

## Sources
- https://arxiv.org/abs/2311.17600 ; https://arxiv.org/html/2311.17600
- https://arxiv.org/abs/2311.05608 ; https://arxiv.org/html/2311.05608v3
- https://arxiv.org/abs/2403.09792 ; https://arxiv.org/html/2403.09792v3
- https://arxiv.org/abs/2411.19939 ; https://arxiv.org/html/2411.19939
- https://arxiv.org/abs/2406.15279 ; https://arxiv.org/html/2406.15279v2
- https://arxiv.org/abs/2506.04704 ; https://arxiv.org/html/2506.04704v5
- https://arxiv.org/abs/2505.15389 ; https://arxiv.org/html/2505.15389
- https://arxiv.org/abs/2608.25490 ; https://arxiv.org/html/2608.25490
- https://arxiv.org/abs/2601.22737 ; https://arxiv.org/html/2601.22737v1
- https://arxiv.org/html/2511.08367 ; https://arxiv.org/html/2608.30750v1
- SNIPPET only: https://arxiv.org/pdf/2507.20704 , https://arxiv.org/pdf/2604.25102 , https://github.com/Aurnawr/VLM-Interp , https://arxiv.org/html/2510.20223v1
