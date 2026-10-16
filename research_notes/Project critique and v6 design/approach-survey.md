# Approach survey: VLM safety alignment, what has been tried, what a student can add

Date: 2026-10-16. Marks: V = I opened the arXiv abstract page and saw it (abstracts only; WebFetch summarises with a small model, so numbers are second-hand from the abstract). S = search-snippet only. U = unverified / from memory. I read no full PDFs, so per-model numbers inside papers are mostly NOT checked. "Not found" means I did not find it, not that it does not exist.

## 1. Benchmarks and attacks

| Paper | What they did | Headline result | Limitation | Mark |
|---|---|---|---|---|
| MM-SafetyBench 2311.17600 | 13 scenarios, 5,040 text-image pairs; query-relevant images (diffusion + typography) | 12 MLLMs vulnerable even with aligned LLM backbones; a prompting defence proposed | Text rephrased into the image variants differs from plain text (our wrapper confound); per-model numbers not seen | V |
| FigStep 2311.05608 | Harmful instruction rendered as typographic image, benign text wrapper | Avg ASR 82.50% on six open LVLMs (AAAI 2025 oral) | Attack, not controlled decomposition; wrapper text also changes | V |
| HADES 2403.09792 | Images that conceal/amplify harmful intent | ASR 90.26% LLaVA-1.5, 71.60% Gemini Pro Vision | White-box-ish optimised images; ASR depends on judge | V |
| VLSBench 2411.19939 | 2.2k pairs avoiding "visual safety information leakage" (harm already in text) | Hard for LLaVA, Qwen2-VL, GPT-4o; text alignment suffices when leakage exists, multimodal alignment needed otherwise | Explains why text-only safety transfer looks good on leaky benchmarks; directly relevant to our typographic data (harm is in the text) | V |
| SIUO 2406.15279 | Safe image + safe text -> unsafe combination, 9 domains | Substantial failures in GPT-4V, LLaVA | Small, hand-built; no numbers seen | V |
| HoliSafe 2506.04704 | All five safe/unsafe image-text combinations; visual guard module | Existing VLMs show critical gaps | Their gains come from training | V |
| MSTS 2501.10057 | 400 prompts, 40 hazards, 10 languages | Some models "safe" only because they do not understand the prompt; text-only safer than multimodal; classifiers inadequate | Small; comprehension confound is the key lesson | V |
| MOSSBench 2406.17806 | 300 benign queries that trigger over-refusal | Refusal of harmless queries up to 76%; stronger safety tuning tends to mean more oversensitivity (20 MLLMs) | Small | V |
| VLGuard 2402.02207 | Safety instruction-tuning dataset + benchmark | Safety fine-tuning with little helpfulness cost; attack success near zero in many cases | Needs training | V |
| SPA-VL 2406.12030 | 100,788 preference quadruples, 12 VLMs' responses | Aligned models gain harmlessness and helpfulness | Training; automated labels | V |
| MMJailBench 2608.25490 (Aug 2026) | Factorised benchmark: intent x framing x visual semantics x instruction carrier; 16 MLLMs | Framing is dominant variance source; task-relevant images raise susceptibility; rendered text does NOT consistently beat plain text | Closest competitor to our wrapper-vs-modality decomposition; see scoop risk | V |
| DUAL-Bench 2510.10846; USB (ACL 2026); VLSU (ICLR 2026) | Over-refusal / unified / joint-understanding benchmarks | DUAL-Bench: low safe-completion rates incl. Qwen; USB: models struggle with safety vs over-refusal across 22 MLLMs | Snippets only | S |
| Wei et al. 2603.17372 (Mar 2026) | Mechanism + defence, see section 4 | Reports a blank image raises LLaVA-1.5-7B jailbreak success on HADES by 28.13% (snippet) | Blank-image figure not seen on the abstract page | V (paper) / S (blank figure) |

## 2. Defences needing little or no training

| Paper | What they did | Headline result | Limitation | Mark |
|---|---|---|---|---|
| ECSO 2403.09572 | Detect unsafe, caption image, answer from text | LLaVA-1.5-7B +37.6% on MM-SafetyBench (SD+OCR), +71.3% VLSafe; utility reported maintained | Typographic images captioned = text restored, so helps mostly because text is recovered; over-refusal cost not stated in abstract | V |
| Safety prompt in MM-SafetyBench | Prompting strategy | "Simple" gain claimed | Details not seen | V (existence) |
| Safety Reminder 2506.15734 | Learnable soft prompt injected during generation | Lower ASR, utility preserved | Needs training of soft tokens; no numbers seen | V |
| Arditi 2406.11717 | Refusal = single direction, text LLMs | 13 chat models up to 72B; ablate to jailbreak, add to induce refusal | Text-only; difference-of-means direction | V |
| MARS 2606.31876 | Text-derived refusal direction applied to MLLMs, re-centering, adaptive strength, first token | Consistent safety gains, utility preserved, five MLLMs | Misalignment pushes benign inputs to refuse; abstract has no numbers; publicly out, so steering novelty is gone | V |
| VLM-Guard 2502.10486 | Project out of space orthogonal to LLM safety direction | Narrows safety gap, no numbers on page | "Work in progress" | V |
| JRS-Rem 2603.17372 | Remove image-induced "jailbreak shift" at inference | Defence while preserving benign tasks (no numbers on page) | Needs white-box access | V |
| Cross-modal textual unlearning 2406.02575 | Unlearn on text only | ASR under 8% (some ~2%) over six datasets; multimodal unlearning no better, up to ~6x compute | Training; VLSBench argues this holds only under visual leakage | V |
| Weight merging 2410.07571 | Merge safety-tuned and multimodal-strong model | Reduces safety loss while keeping helpfulness; vision adaptation erodes safety even with safe data | Needs two checkpoints; no model-family scaling study seen | V |
| HPA 2511.20158 | Continual visual instruction tuning keeping safety via parameter partition | Better safety retention than baselines | Training heavy, no numbers seen | V |
| Safe decoding for VLMs | Not found as a distinct paper in my searches | n/a | n/a | not found |

## 3. Evaluation methodology

| Paper | What they did | Headline result | Limitation | Mark |
|---|---|---|---|---|
| MSTS | Comprehension vs safety | Some "safe" models just do not understand; classifiers inadequate | Small | V |
| MOSSBench / DUAL-Bench / USB | Over-refusal | Refusal on benign up to 76% (MOSS); safety-vs-overrefusal tradeoff (USB, snippet) | Different label schemes | V / S |
| Schwinn et al. "A coin flip for safety" (ICML 2026) | LLM-judge reliability for adversarial robustness | Title only | Text-only; I did not see findings | S |
| Typical practice (JailDAM, SafeCoT, Safety Reminder) | One LLM judge or refusal-string template | n/a | None of the snippets measured judge disagreement | S |
| VLM-specific judge validity study | Not found | Gap: no paper found that compares keyword vs Qwen3Guard vs WildGuard on VLM outputs against human labels | | not found |

## 4. Mechanisms: why images lower safety

| Paper | What they did | Headline result | Limitation | Mark |
|---|---|---|---|---|
| FigStep | Embedding analysis | Attributes success to weak alignment of visual embeddings | Qualitative | V |
| Visual instruction tuning forgets safety 2405.04403 | VLM vs its LLM backbone | All three VLMs more jailbreakable than backbones; "forgetting effect" | Models not named on page; snippet says a blank image added to adversarial input raised harmful outputs | V / S |
| 2410.07571 | Adaptation weights | Safety-related layers affected | See above | V |
| VLM-Guard | Modality gap | Image/text separation blurs harm boundary | No numbers | V |
| Wei et al. 2603.17372 | Representations | Models still recognise harm; images shift state toward a "jailbreak" state, separable from refusal | Needs read-through for models/data | V |
| 2026 visual-replacement paper (cited in search result) | Logit lens | Refusal activation suppressed in late layers | Could not identify id | S |
| MMJailBench | Single open model internals | Representation patterns linked to vulnerability | One model | V |

## 5. Is there a text-vs-vision safety trade-off?

| Evidence | Reading | Mark |
|---|---|---|
| 2410.07571: adaptation and safety tuning "pull in different directions" | Training-time conflict, not a zero-sum between modalities at inference | V |
| 2406.02575: text-only unlearning also fixes vision attacks; multimodal adds nothing | Evidence AGAINST a see-saw (positive transfer) | V |
| VLSBench: text alignment enough when text leaks harm | Same, with caveat | V |
| 2405.04403: vision tuning lowers backbone safety | Vision-vs-text safety lost, but it is erosion, not a see-saw | V |
| MOSSBench / USB: stronger safety, more over-refusal | Real safety vs helpfulness trade-off, a different axis | V / S |
| Zero-sum text-vs-vision see-saw | Not found anywhere; our data also do not support it | not found |

## 6. Ranked study ideas (T4, hours to days)

Relation to our work: SAME = repeat of what we did; EXT = extension; DIFF = different pattern.

| # | Study | Question and design | Effort | Novelty | Scoop risk | Makes it a paper if | Type |
|---|---|---|---|---|---|---|---|
| 1 | Image-presence effect (a) | Does any image (blank, noise, irrelevant natural, task-irrelevant text image) lower refusal for plain harmful text? 3 models x ~5 image conditions, matched benign set for over-refusal | 2-3 days | Partial (2603.17372 and 2405.04403 report blank-image effects in snippet; no dose-response or family comparison found) | Medium-high | Effect is large, LLaVA-specific vs Qwen-specific, and graded by image type; persists after controlling labeller | EXT (our LLaVA finding) |
| 2 | Cross-benchmark wrapper-vs-modality decomposition (b) | Replicate on FigStep SafeBench-style data and a second image-text set; text-in-wrapper vs plain vs image conditions | 3-4 days | Partial (MMJailBench says framing dominates, which agrees with our result) | High (MMJailBench Aug 2026) | Decomposition replicates across benchmarks and gives a reusable recipe for subtracting wrapper effect | SAME |
| 3 | Judge-validity component (d) | Hand-label ~300 outputs; compare keyword, Qwen3Guard, WildGuard, refusal vs harm; report how conclusions flip | 2-3 days (labelling time) | Partial to clear (no VLM-specific judge comparison found) | Low-medium | Rankings of models/conditions change depending on judge, with kappa vs human | EXT |
| 4 | Safety reminder / caption-first with over-refusal cost (c) | System reminder, ECSO-style caption-first, and both; measure harmful-refusal gain vs benign refusal on MOSSBench-like and matched benign sets | 3-4 days | Partial (ECSO exists; cost accounting and wrapper-controlled comparison less covered) | Medium | Cost-benefit curves show where gains are just over-refusal | DIFF |
| 5 | Steering with proper controls (e) | Text-derived refusal direction (Arditi/MARS style), compare with random direction, norm-matched control, benign-set refusal and a capability check | 4-6 days | Low-partial (MARS 2606.31876 exists) | High | Show gains vanish or are over-refusal under controls | DIFF |
| 6 | Scaling within a family (f) | Same Qwen2.5-VL 3B/7B (and 2B/7B Qwen2-VL, maybe 32B if 4-bit) on 1-3 conditions | 2-3 days | Partial-clear (I found no scaling study of this decomposition) | Low-medium | Wrapper vs image effect varies non-monotonically with size | EXT |
| 7 | Comprehension control (MSTS-style) | Separate "refuses" from "understands" by adding an OCR/comprehension probe per item | 2 days | Partial | Medium | Refusal gap shrinks once non-readers are excluded | EXT |
| 8 | Backbone vs VLM gap | Compare VLM refusal to its LLM backbone on same text (LLaVA vs Vicuna, Qwen2-VL vs Qwen2) to measure inherited-safety loss | 2 days | Partial (2405.04403) | Medium | Gap quantified per model and image condition | DIFF |
| 9 | Layer-wise refusal-direction projection of images | Measure projection onto text-derived refusal direction for text, typographic, blank images | 3-4 days | Partial (2603.17372, VLM-Guard) | High | Blank image shifts projection in LLaVA but not Qwen | DIFF |
| 10 | Image-position / resolution ablations | Does text size, font, resolution change refusal | 2 days | Partial-clear | Low | Monotone effect on legibility | EXT |

Notes: "Same as what we did" is only #2. Items 1, 3, 6, 7, 10 extend; 4, 5, 8, 9 are new patterns. Honest caveat: a text-vs-vision see-saw is not supported by what I found or by the user's data, so frame it as a negative or null result.

## Summary

The literature already shows that images lower safety, that framing and prompt content dominate (MMJailBench, Aug 2026), that text-only safety transfers, and that refusal-direction steering helps (MARS). I found no paper supporting a text-vs-vision zero-sum, so that framing should be dropped. The least-covered gap I found is judge validity for VLM safety, with no VLM-specific judge comparison against human labels. The second is a graded image-presence study with matched benign controls, since only snippet-level blank-image results exist. My top three are: (1) the judge-validity study folded into everything else, (2) the image-presence dose-response across Qwen and LLaVA with over-refusal controls, and (3) the cross-benchmark wrapper decomposition with a scaling arm, accepting MMJailBench scoop risk by running it first. Steering and reminder studies are worth including only as controlled secondary analyses.
