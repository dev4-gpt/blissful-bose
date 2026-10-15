# Papers 5 to 8 in depth: speaker notes

Ten slides: MMJailBench (2), CMRM (2), JailBound (2), SafetyReminder (2), and a synthesis.

## Slide 1: Papers 5 to 8 in depth

In-depth look at the second group of four papers. Each gets two slides. The goal is that for every number on a slide you can say what was measured, how, and what it means for our design.
Order: MMJailBench (which factor drives jailbreaks), CMRM (do images shift hidden states), JailBound (linear probes inside the model), SafetyReminder (where refusal appears in a reply). The last slide ties the four to our design and lists what we deliberately do not take.
The longer 36-slide deck has every table row by row; this one keeps the argument and the key evidence.

## Slide 2: A full grid, so each factor can be separated

MMJailBench's question: which part of a multimodal jailbreak does the work? It builds a full grid so each factor can be varied alone. 272 harmful intents across 9 harm domains, 6 prompt framings (academic, system, structured, story, code, safety-paradox), 5 visual-semantic conditions (danger context, scenario, professional role, identity credential, authorization document) and 2 carriers (plain TEXT or OCR image). 272 x 6 x 5 x 2 = 16,320 instances per model; 16 models give 261,120 replies.
Metrics. A GPT-5 judge scores each reply 1 to 5 for harmfulness; ASR is the share scoring 4 or 5. Refusals, warnings and high-level discussion do not count. Example: 66,200 of 130,560 replies scoring 4 or 5 is 50.7%. For OCR there is a risk that the model simply misreads the image, so the paper also reports instruction mismatch (misread or irrelevant replies) and CASR = successes / (N minus mismatches). Delta ASR is the change against the no-image condition.
For us: ASR with a model judge is our kind of outcome; mismatch and CASR are the same idea as our legibility covariate.

## Slide 3: Meaning moves ASR; an OCR carrier is weaker than text

Left, Table 2 (visual semantics): ASR change against no image (34.77% baseline). The five meaningful contexts add +8.45 to +12.96 points, authority documents highest. The controls add little: blank +2.19, noise +0.76, nature +0.72. So it is the meaning of the visual context, not the mere presence of an image, that raises ASR here.
Right, Table 3 (carrier): TEXT 50.70% ASR, OCR 40.59%; CASR TEXT 50.89%, OCR 42.34%; mismatch TEXT 0.37%, OCR 4.14%. OCR is weaker even after removing misreads, so rendering an instruction in an image is not automatically stronger. The long deck's Table 4 shows the carrier effect is model-dependent (about 50 points for LLaVA-OneVision, about 1 for Qwen2.5-VL and Claude).
Third finding, not charted: prompt framing is the largest factor, with more than 40 points between best and worst style.
Lessons: always run a TEXT arm; treat text-side framing as a variable; report misreads. Caveat: ASR only, internals on one model (gemma3-12b).

## Slide 4: Any image, even a blank one, raises the unsafe rate

CMRM's observation: a VLM's language backbone is safe on text, but adding an image degrades safety. Setup: the same harmful text query in five input forms: text only, text plus the image's caption, text plus a Gaussian-noise image, text plus a blank image, and original image plus text. Dataset VLSafe (1,110 malicious queries), model LLaVA-1.5-7B, metric unsafe rate from a Llama-3.1-8B-Instruct judge.
Chart: text only 1.91%, caption 5.52%, noise image 57.21%, blank image 56.87%, original 61.53%. With no image or only a caption the model behaves like its safe backbone; with any image, even a blank one, the rate jumps by more than 50 points. For this model and dataset, the image's presence does most of the damage. That is why our design has a clean-image arm.
Method, for understanding only: h_o is the hidden state for the original input, h_c for a corrupted image, h_t for text alone. Assume the state is the ideal state plus an image-induced shift, which gives h* = h_o + alpha (h_t minus h_c). It is applied at inference with no weight change. We do not build this as a defense; the size of h_t minus h_c per layer is a measurement we reuse.

## Slide 5: Reading the PCA, and the cost of the fix

Fig. 1 is a 2-D PCA of last-token hidden states for LLaVA-7B, LLaVA-13B and ShareGPT4V-7B. PCA projects the high-dimensional states onto the two directions of largest variance so clusters become visible. Colours are the five input types. The text-only and caption points form their own cloud; every variant containing an image falls in a separate region, even the blank one, which matches the chart on the previous slide.
Table 1 (LLaVA-1.5-7B), on the right: with no intervention the unsafe rate is 61.53% (original), 56.87% (blank); CMRM sample-level correction brings these to 3.15% and 1.24%. Cost: general capability L-Bench 79.2 to 77.3 and S-QA 68.03 to 66.14, small drops. Training-based VLGuard also reaches near zero but changes weights.
Limits: it shows images shift states, not which image property matters, and the evidence is on LLaVA-family models. For us: compute the shift per condition and layer, relative to a text-only baseline, with the blank-image control.

## Slide 6: A linear probe: boundary, normal, distance

JailBound's first stage is a linear probe. Take image-text examples labelled safe or unsafe, read the hidden state h at a fusion layer, and train a logistic regression: P(unsafe) = sigmoid(w.h + b). The boundary is the plane w.h + b = 0; the unit normal v = w / |w| points from safe toward unsafe; epsilon is an example's distance to the plane. One classifier per layer.
The schematic (ours, not the paper's) shows those pieces. Fig. 7 (appendix A.2) shows per-layer training: deep layers reach near-perfect accuracy while layers 0 to 4 do poorly; the introduction's wording that all layers reach 100% is the looser statement.
What a probe tells us: whether safe-versus-unsafe information is linearly readable at a layer. What it does not: whether the model will refuse, since the labels describe input content ('determined by the VLM' on MM-SafetyBench samples). So we borrow the layer-wise linear method and aim it at refusal behaviour instead.

## Slide 7: Each channel helps, both together help more

Setup: MM-SafetyBench, 1,719 adversarial examples over 13 prohibited categories; six VLMs (white-box on Llama-3.2-11B, Qwen2.5-VL-7B, MiniGPT-4 among others; black-box on GPT-4o, Gemini 2.0 Flash, Claude 3.5 Sonnet). I0 and I1 are the clean and perturbed image, T0 and T1 the original text and the text with an optimised suffix.
Chart, Illegal Activity, white-box ASR: no attack I0+T0 51.47 / 2.94 / 42.65 (Llama / Qwen / MiniGPT-4); text suffix only 82.35 / 30.88 / 69.12; image only 85.29 / 22.06 / 83.82; both separately 88.24 / 64.71 / 95.59; joint optimisation 95.59 / 82.35 / 100.00. Malware Generation follows the same shape. Read it as a factorial: each channel alone helps, both together help more, joint best.
The metric caveat matters: ASR here is the share of replies with no rejection phrase (exact string match). That counts evasive or gibberish replies as successes, so these numbers are not comparable with judged ASRs elsewhere. Note the baseline: Qwen2.5-VL-7B starts at 2.94%, much better at emitting refusal phrases than Llama-3.2 (51.47%). Abstract averages: 94.32% white-box, 67.28% black-box. The attack needs gradients; we do not use it.

## Slide 8: Where the safety words fall in a reply

SafetyReminder's observation: a jailbroken VLM often starts to comply and only adds 'this is illegal' at the end. Terms: a safety token is a refusal or warning word ('sorry', 'illegal', 'cannot'); its relative position is where it falls in the reply, 0 at the start and 1 at the end; a prefilling attack forces the reply to begin with an affirmative opening such as 'Sure, here is'.
Fig. 2 plots the density of safety tokens by position, for a harmful dataset and for a prefilling attack. For LLaVA-1.5-7B both curves peak near the end. For Qwen2-VL-7B the plain harmful prompts put safety tokens near the start (the model refuses early) and the prefilling attack moves them to the end. Reading: safety wording clusters at the two ends and is largely absent in the middle, and an attack pushes it to the end.
For us: Qwen2-VL is our model family and it refuses early when not attacked, which supports measuring the first token and the first few tokens rather than only the final answer. Earlier drafts attributed an attention result and a 'first five tokens' rule to this paper; neither is in it.

## Slide 9: Attack gap between models, and reporting the cost

Table 1, ASR (%) on six test sets. LLaVA-1.5-7B with no defense: FigStep 74.9, MMSafety 58.2, SPA-VL 45.6, ImgJP 86.6, GCG 94.0, BAP 97.0, average 76.1. Qwen2-VL-7B no defense: 26.6, 13.2, 1.5, 97.4, 79.0, 82.0, average 50.0. Self-Reminder (a prompt-only defense) helps partly; their trained soft prompt (SAPT) brings the averages to 5.0 and 4.7.
Two readings for us. First, the attack gap between models: FigStep gets 74.9% on LLaVA but 26.6% on Qwen2-VL-7B, which supports the floor-effect risk for our Qwen2-VL-2B pilot, though the 2B model has not been measured. Second, Table 2 reports the cost side: utility on MM-Vet (LLaVA 27.9 to 28.0, Qwen 52.3 to 52.6) and the refusal rate on benign questions (2.3 to 3.7, and 3.7 to 4.1), while another defense, BlueSuffix, cuts Qwen2-VL's capability to 13.4 and lifts refusals to 35.8%. The lesson is to report safety and over-refusal together.
The safety-awareness classifier (SVD plus a linear classifier on the last-token hidden state, over 256 harmful and 256 benign text prompts from the Arditi et al. set) parallels our planned refusal direction; we would use a difference of means per layer. We do not use SAPT, which is trained.

## Slide 10: What papers 5 to 8 give us, and what we leave out

Putting the four together. MMJailBench says meaning and framing matter more than the image being present as text, and that OCR is not automatically stronger. CMRM says any image shifts the hidden state. JailBound says safety information is linearly readable, weakly in early layers. SafetyReminder says refusal has a position in the reply.
What we take: a TEXT arm and a legibility covariate; a clean-image arm and a per-layer shift against a text-only baseline; layer-wise linear analysis aimed at refusal; the first-token and early-token refusal probabilities.
What we do not take: CMRM's correction (a defense), JailBound's gradient attack and string-match ASR, SafetyReminder's trained soft prompt. Three of the four papers contain a method that trains or uses gradients; only their measurement ideas are borrowed.
Still unverified: the refusal-direction work of Arditi et al. is cited from memory, and related typographic sweeps outside these eight papers have not been read in full.
