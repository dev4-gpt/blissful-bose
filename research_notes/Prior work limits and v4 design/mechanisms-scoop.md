# Mechanisms, trade-offs and scoop check (as of 2026-10-15)

Status tags: VERIFIED = I opened the arXiv abs page and read the abstract. SNIPPET = seen only in a search-result summary. UNVERIFIED = not checked. "Abstract-only" means full text was not read, so limitations are inferred from the abstract.

## Part 1. Trade-offs and mechanisms

**Headline: no paper I found explicitly tests a zero-sum see-saw (vision safety down by Z, text safety up by Z).** Searches for "see-saw", "zero-sum", "trade-off" returned only modality-gap papers (SNIPPET, search below). The nearest thing is Lee et al. (2410.07571), which claims a conflict between vision-language adaptation and safety tuning. That is a conflict in training objectives, not a measured per-modality exchange. The literature's dominant picture is one-directional: text safety is stronger, and images shift the model away from it.

| Paper (ID, date) | Tag | What it found | Limitations / relevance to our data |
|---|---|---|---|
| CMRM (2410.09047, Oct 2024) | VERIFIED, abstract-only | Adding images shifts representations off the text distribution, degrading inherited safety. Inference-time fix; LLaVA-7B unsafe rate 61.53% to 3.15%. | Headline from one model; no per-modality exchange measured; no 2B/3B Qwen. Supports "image lowers text-side safety", consistent with our -0.02 to -0.06. |
| VLGuard (2402.02207, Feb 2024) | VERIFIED | Vision instruction tuning erases LLM safety; adding a safety dataset restores it with little helpfulness loss. | Reports no safety loss on the other channel, so no see-saw. Not a decomposition of the gap. |
| Chakraborty et al. (2406.02575, May 2024; EMNLP Findings 2024) | VERIFIED | Text-only unlearning cuts ASR below 8% for both text and vision-text attacks. | Direct evidence of positive transfer (text safety up, image safety up), the opposite of a see-saw. Attack sets are ASR-based; no matched-wording control. |
| Lee et al. (2410.07571, Oct 2024) | VERIFIED | VL adaptation degrades safety even with safe data; safety tuning causes over-refusal; "goals conflict". Weight merging helps. | Closest to a trade-off claim, but the trade-off is safety vs helpfulness and adaptation vs safety tuning, not text vs image. |
| TGA (2410.12662, Oct 2024; ICLR 2025) | VERIFIED | Text safety mechanisms fail to transfer through vision-language alignment; hidden states for images differ from text. Text-guided alignment transfers safety without image safety tuning. | Positive transfer framing. Evaluated on older LLaVA-style models. |
| HPA (2511.20158, Nov 2025; rev. Jun 2026) | VERIFIED | Continual visual instruction tuning makes MLLMs less safe and forget tasks. | About continual learning; safety loss is across time, not across modalities. Weak relevance. |
| Arditi et al. (2406.11717, Jun 2024) | VERIFIED | Refusal is mediated by one direction in 13 text chat models. | Text-only models. Does not cover VLMs; transfer to images is an assumption made by later work. |
| MARS (2606.31876, Jun 2026) | VERIFIED | Text refusal directions transfer to image and video, but depend on layer, strength, and cross-modal misalignment, which can push safe inputs toward refusal. | Shared structure across modalities argues against independent channels. Needs activations; our API-style generations cannot test it directly. Over-refusal side-effect relevant to our XSTest-style item. |
| JRS-Rem (2603.17372, Mar 2026) | VERIFIED | Adding an image pushes representations into a state that suppresses refusal; defines a jailbreak direction and removes the shift. | Image presence lowers refusal (the same sign as our small drop in text refusal). Models and scope not read in full. |
| ShiftDC (2502.13095, Feb 2025) | VERIFIED | Images shift activations toward "safe" ("safety perception distortion"); removing the safety-relevant part of the shift restores backbone safety. | Modality as a shift, not a trade. FigStep-style evaluation, no matched-text control (SNIPPET). |
| 2605.18104 (May 2026) | VERIFIED | "Safety Geometry Collapse": multimodal drift reduces separability along the text refusal direction; ReGap corrects it. | Same one-directional picture. No behavioural decomposition. |
| 2608.30750 (Aug 2026; EMNLP 2026 main) | VERIFIED | Text safety is localized (~88 neurons); visual safety is distributed (at least 50 directions vs ~5). SNIPPET: whether the VLM refuses depends mainly on the text query, and a harmful image lowered one model's text refusal from 90.7% to 76.9%. | Supports weakly coupled mechanisms and "adding vision lowers text refusal". Does not test a see-saw. Mechanistic; no wording/OCR control. |

Other relevant Part 1 hits (not in the requested list):
- MMAligner 2608.05909 (Aug 2026; CCS 2026), VERIFIED: MLLMs refuse unsafe text but comply with semantically equivalent multimodal input. Equivalent-input comparison, but the abstract does not separate comprehension from refusal and names no models. Partial relevance.
- 2609.02082 (Sep 2026; EMNLP Findings 2026), VERIFIED: benign text plus an image conveying harm gets refused far less; fix is representation transfer. Cross-modal drift, not a see-saw.
- V-DEAL 2607.21151 (Jul 2026), VERIFIED: video; rules out perception failure (over 81% recognition) before measuring refusal. A methodological analogue of our comprehension gate, in video.
- Qu et al. USENIX Security 2025 (SNIPPET): open VLMs recognise unsafe concepts yet judge images safe more often than text.

**Takeaway for the advisor's framing:** the published picture supports a text-to-image safety gap (text stronger), and some papers show images mildly lowering text-side refusal. None shows text safety rising when vision safety falls. Our item-level positive coupling (phi 0.12 and 0.33) and small negative effect of adding vision fit the shared-structure view (MARS, TGA, Chakraborty). I found no paper that estimates item-level coupling between text and image refusal. That is a possible small contribution but "nothing found" is not proof.

## Part 2. Scoop check

Date window: arXiv 2609.* to 2610.* (to 2026-10-15), plus earlier papers that bear on the design. Planned claim: decompose the typographic refusal gap into wrapper, content, comprehension and residual modality effects.

### The six specified IDs (all opened, VERIFIED)

| ID | Title (short) | Date | What it is | Overlap |
|---|---|---|---|---|
| 2609.26174 | The Uncontrolled Variable: VL refusal is conditioned on the image-attachment interface | v1 12 Aug 2026; v2 25 Sep 2026 | Attaching even a blank or unreadable image raises refusal on borderline benign prompts, depends on canvas colour and pixel count, reverses across checkpoints, and persists when told to ignore the image; lowers ASR on harmful prompts. | **Partial.** Closest to our "wrapper" and "residual modality" terms and to over-refusal for images. No typographic payload, no comprehension/OCR gate, no decomposition. Must be cited. Its finding (image attachment itself shifts refusal) is a competing explanation for our small text-refusal drop. |
| 2609.31403 | Sorry Robot, Happy Human: VLMs read only one of two legible typographic layers | 25 Sep 2026 | DecoyBench, 300 images with overlapping outlined and shaded text; six closed models; reading, not safety. | **None** on safety. Mild relevance to OCR/readability. |
| 2603.08497 | Reading is not Seeing: the typography gap in VLMs | 9 Mar 2026 | VLMs read text accurately but poorly perceive font style/size; 15 models. | **None** (not safety). |
| 2607.27910 | Cross-architecture audit of direction-based inference-time defences in VLMs | 30 Jul 2026 (v2 23 Aug) | Benchmarks five direction-subtraction defences on 15 configs; image-conditioning shift partly overlaps a text refusal direction. | **None** for the decomposition; Part 1 relevance (shared geometry). |
| 2603.17372 | JRS-Rem | 18 Mar 2026 | See Part 1. | **None** (defence). |
| 2609.18860 | Decodable but Misrouted: readout gap for harmful meme detection | 16 Sep 2026 (v2 29 Sep) | SAEs, probes and interventions on harmful meme detection; evidence often present internally but not routed to output. | **None** (detection, not refusal gap), though the "knows but does not act" idea resembles our comprehension vs refusal split. |

### Other candidates found

| ID | Date | What it did | Closeness |
|---|---|---|---|
| 2610.07009 "Which Image Property Carries the Jailbreak?" | 4 Oct 2026 | Controlled dissection of image-to-text jailbreaks on 313 StrongREJECT prompts with a constant instruction; benign-image and size-matched controls; Qwen3-VL-8B ablation (about 0.12 ASR drop from removing relatedness). VERIFIED abstract-only. | **Partial.** Same spirit (attribute the gap to image properties with controls) but it does not name typographic payloads, text-matched controls, OCR/comprehension, or a refusal-gap decomposition; judge is an automated rubric. Read full text before submission. |
| 2609.36121 "Render Before Reading" | 28 Sep 2026 | Models follow instructions delivered as images less than as text (prompt injection); defence renders untrusted text as images. VERIFIED. | **Partial, different task.** Prompt injection rather than refusal; shows a modality gap in the opposite direction. Cite for the wording-vs-modality ambiguity. |
| 2609.00232 VeriOCRBench | 31 Aug 2026 | OCR task verification with over-refusal controls. VERIFIED. | **None** (not safety); related to OCR plus over-refusal. |
| 2604.12371 "Reading Between the Pixels" | 14 Apr 2026 | Typographic attacks on SALAD-Bench; text attacks beat image attacks for GPT-4o and Claude; Qwen3-VL-4B similar across modalities; embedding distance predicts ASR. VERIFIED. | **Partial.** Has a text-vs-image comparison and font-size sweep; no wrapper/content/comprehension decomposition; mostly frontier models. Pre-window. |
| 2604.25102 | 28 Apr 2026 | Embedding-guided typographic perturbations improve readability and reduce refusals. VERIFIED. | **Partial** on readability vs refusal. Pre-window. |
| 2602.00420 Text-DJ | 31 Jan 2026 | OCR-based grid jailbreak. VERIFIED. | **None** for decomposition. |
| 2605.00583 | 1 May 2026 (ICML 2026) | Visual-channel jailbreaks; visual cipher 40.9% vs 10.7% textual on Claude-Haiku-4.5. VERIFIED abstract. | **Partial** (matched text vs image cipher), frontier models, attack-focused. |
| 2605.07250 "Hard to Read, Easy to Jailbreak" | May 2026 | Visual degradation; uses transcribe-then-assess prompting and a pure OCR prompt. SNIPPET only. | **Partial** on OCR/read-back; UNVERIFIED beyond snippet. |
| 2608.05909 MMAligner | 6 Aug 2026 | Text vs semantically equivalent multimodal gap; defence. VERIFIED. | **Partial**, no decomposition. |
| 2510.10846 DUAL-Bench | Oct 2025 | Over-refusal and safe completion across 18 VLMs. VERIFIED title via search; abstract SNIPPET. | **Partial** on image over-refusal. Pre-window. |
| Omni-SafetyBench 2508.07173 | Aug 2025 | Argues misunderstanding can masquerade as safety. SNIPPET. | **Partial** on the misunderstanding-vs-refusal idea. |
| MSTS 2501.10057 | Jan 2025 | Paired with/without-image test suite; model-dependent gap. SNIPPET. | **Partial.** |

### Verdict on novelty (qualified)
No paper found that decomposes the typographic refusal gap into wrapper, content, comprehension and residual modality terms on small open VLMs. The closest are 2609.26174 (image-attachment effect on refusal), 2610.07009 (controlled image-property dissection), 2604.12371 (text vs typographic image comparison) and MMAligner 2608.05909 (equivalent text vs multimodal). Each covers one slice. **Rating: partial overlap, not scooped.** Residual risk: search engines index arXiv unevenly, I saw abstracts only, and the 2610.* window is thin because only two weeks of papers exist.

### Queries tried
1. typographic image jailbreak vision-language models decomposition wrapper content comprehension refusal gap
2. arXiv 2609 typographic attack small VLM refusal text-matched control OCR read-back
3. vision-language model misunderstanding versus refusal typographic image safety comprehension failure MM-SafetyBench
4. XSTest over-refusal multimodal images benchmark vision-language 2026 (nothing found: no image version of XSTest; DUAL-Bench is closest)
5. modality safety see-saw trade-off text image safety vision-language models zero-sum (nothing found for see-saw)
6. "typographic" jailbreak VLM text-only control same wording image vs text refusal rate difference attribution
7. is the image the problem? safety gap ... text-rendered-as-image versus plain text same prompt confound
8. arXiv 2610 vision-language safety typographic jailbreak refusal decomposition image channel controlled (nothing new)
9. Qwen2-VL-2B Qwen2.5-VL-3B safety refusal typography MM-SafetyBench ... (no 2B/3B-specific results found)
10. VLM safety evaluation "read back" OR transcription check ...
11. text and image safety positively correlated ... item-level coupling (nothing found on item-level coupling)
Not searched: OpenReview and workshop pages directly, alphaxiv listings.

## Sources
https://arxiv.org/abs/2609.26174, /2609.31403, /2603.08497, /2607.27910, /2603.17372, /2609.18860, /2410.09047, /2402.02207, /2406.02575, /2410.07571, /2410.12662, /2511.20158, /2406.11717, /2606.31876, /2502.13095, /2605.18104, /2608.30750, /2610.07009, /2609.36121, /2609.02082, /2609.00232, /2608.05909, /2607.21151, /2604.12371, /2604.25102, /2605.00583, /2602.00420 (all arxiv.org/abs/...). Others from search snippets: arxiv.org/abs/2510.10846, 2605.07250, 2508.07173, 2501.10057.
