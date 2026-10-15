# Cross-modal conflict, 14 slides: speaker notes

Question, literature map, five papers in depth (FigStep, VLSBench, MMJailBench, CMRM, SafetyReminder), gap, design, measurement, mechanism, status, plan.

## Slide 1: Cross-Modal Signal Conflict in Post-Trained Vision-Language Models

This is the short version of the whole project. Ten slides, one storyline: the question, what the eight papers teach us, the gap, the design, how we measure behaviour, how we look inside the model, where we are, and the plan.
Two companion decks hold the detail. 'Deep Dive, Papers 1 to 4' explains every metric and table of FigStep, HADES, SIUO and VLSBench; 'Deep Dive, Papers 5 to 8' does the same for the other four. Use them as backup when someone asks 'what does that number mean'.
Honesty line to say early: this is a proposal. The stimulus generator and runner exist and pass a dry run, but no model has been run, so there are no results of our own in this deck.

## Slide 2: Two channels, one answer

Left to right: the user's text and the image each carry a signal; a frozen VLM turns both into one answer. The answer may be a refusal, an execution of the image's instruction, or only a reading of the image text. The third case is not an attack and must not be counted as one.
Why a conflict is plausible: the language backbone of most open VLMs was safety-aligned on text, while the vision encoder and projector were not (SIUO). Adding an image, even a blank one, shifts hidden states (CMRM, HADES).
Why it is still open: FigStep raised ASR from 44.8% to 82.5% on six open VLMs, yet ADPO's Table 1 reports only 4.5% typographic-jailbreak ASR on Qwen2-VL-7B (22.2% on LLaVA-1.5-7B). So 'can the image win' is known; 'when and why' is not.
Purpose and limits, as the advisor set them: we study how alignment fails, to inform future methods. No defense, no benchmark, no training; weights stay frozen.

## Slide 3: Eight papers audited; five in depth

One slide for all eight papers, so you can truthfully say all eight were audited. The five marked 'in depth' get a slide each next; the other three are one-line mentions.
HADES: typography, then a diffusion image, then adversarial noise; LLaVA-1.5 goes 65.60 to 78.53 to 90.26, GPT-4V 1.73 to 15.07. The last step needs gradients. SIUO: 167 cases where safe image plus safe text still needs care; best model GPT-4V 53.29% safe, LLaVA-1.5-7B 21.56%; we take 'harm without harmful words, so the judge must read meaning'. JailBound: per-layer linear probes; weak in layers 0 to 4, near-perfect deep; its attack ASR is a string match and the attack needs gradients, so we borrow only the layer-wise probing idea.
If asked why those three are not presented: they matter for design details (ablation style, judge, probing) that appear later in the talk, but the argument does not rest on their numbers.

## Slide 4: A harmful list opener as an image, plus a benign prompt

ASR means attack success rate: the share of harmful questions for which the model gave a prohibited (harmful, helpful-to-the-attacker) answer. Worked example: if SafeBench has 500 questions and 420 of them got at least one harmful reply, ASR is 420 / 500 = 84%.
The detail that matters: FigStep sends each question five times and counts the question as a success if ANY of the five replies is harmful. That is a best-of-5 number, higher than a single-shot number. The authors show this themselves: with one repetition, ASR on LLaVA is already 82% but about 60% on MiniGPT4 and CogVLM (Fig. 6a).
Judging was by hand. They also tried an automated judge: it gave lower numbers (for example LLaVA 92% manual vs 72% automated; Table 4) but kept the same ordering, so FigStep still wins. In our own work we will report single-shot ASR, say which judge was used, and audit a sample by hand.

PPL is perplexity. A language model (here GPT-2) reads the model's reply and measures how surprised it is by each next word. Low perplexity means the text is predictable and fluent; high means odd or incoherent. Intuition: 'The cat sat on the mat' has low perplexity, a random word salad has high.
The authors use it as a quality check on the replies. Averaged over the six models, PPL falls from 19.26 (vanilla) to 7.73 (FigStep). They read that as FigStep making the model produce confident, well-formed answers, which supports Intuition 3 (step-by-step lists).
PPL is not a safety score. CogVLM's vanilla PPL is high (30.54) because it often replies 'there is no information in the image' to plain-text questions, which is incoherent for a text-only query but not harmful. Our interpretation: lists also tend to have low perplexity just because list text is formulaic, so a low PPL does not by itself prove the content is more harmful.

Table 1, row by row. Each model has two rows: Vanilla (the plain harmful question) and FigStep. Columns: ASR (higher is worse for safety, hence the up arrow) and PPL (lower arrow).
Read the Average rows: ASR 44.80% to 82.50%, a rise of 37.7 points. PPL 19.26 to 7.73.
Three patterns. (1) The vanilla column tracks the language model's alignment: MiniGPT4-Llama-2-Chat is 23.80% because Llama-2-Chat is strongly aligned, MiniGPT4-Vicuna-13B is 83.40% because Vicuna is weakly aligned. (2) FigStep lifts every model, most where alignment was strong: MiniGPT4-Llama-2-Chat 23.80 to 82.60 (+58.8). CogVLM goes 8.20 to 87.00 (+78.8) but CogVLM's low vanilla number is partly because it often does not understand the text-only question; it is not strong safety. (3) The gain is smallest where the model was already unsafe: MiniGPT4-Vicuna-13B 83.40 to 85.20 (+1.8), a ceiling effect.
So the message is: text-side alignment does not carry over to the image path.

## Slide 5: The harm was leaking through the text

R1, R2 and R1 minus R2, step by step. Take N image-text pairs. A judge labels each pair twice: once with image and text together, once with the text alone. R1 is the share of pairs the judge calls unsafe when it sees image and text. R2 is the share of pairs that are unsafe with image and text AND whose text alone gets the same unsafe label. R1 minus R2 is therefore the share of pairs that are unsafe only when the image is included: harm that requires the image.
Worked example with 10 pairs (table on the slide): 6 pairs unsafe with the image and also unsafe from the text; 1 pair unsafe with the image but safe from the text alone; 3 pairs safe. R1 = 7/10 = 70%. R2 = 6/10 = 60%. R1 minus R2 = 10%, the one pair that truly needs the image.
Why it matters. A benchmark meant to test cross-modal safety should have a large R1 minus R2. If it is near 0, nearly all its harm is visible in the text. Note that R1 and R2 describe the dataset as judged by LlamaGuard3-11B-Vision, not the behaviour of any VLM.

Table 3 as a chart: total safety rate (refusal + warning) on VLSBench. Gemini-1.5-pro is highest at 49.78%; Llama-3.2-11B-Vision 26.29%; GPT-4o 21.43% (refusal 5.21, warning 16.22); Qwen2-VL-7B 13.77% (refusal 1.11, warning 12.66); LLaVA-v1.5-7B only 6.60% (refusal 0, warning 6.60). The challenge holds from 2B to 78B parameters. Stronger reasoning does not necessarily help: the reasoning model QVQ-72B-Preview reaches 23.20%.
Two further results. Table 4: now that leakage is gone, text-only alignment lags multimodal alignment: on LLaVA-v1.5-7B textual SFT reaches 13.99% against 21.26% for multimodal SFT and 27.01% for multimodal DPO; on Qwen2-VL-7B 67.42% against 78.39%. Fig. 7: simply adding a safety instruction to the prompt lifts LLaVA-v1.5-7B from 6.6% to 44.5% and LLaVA-Mistral from 11.19% to 56.8% on a 500-sample subset. Table 5 on 200 samples: Qwen2-VL-7B refuses 19.5% with no vision input but 1.0% with the image, and caption-instead-of-image restores some safety (22.5%).

## Slide 6: Meaning moves ASR; an OCR carrier is weaker than text

Left, Table 2 (visual semantics): ASR change against no image (34.77% baseline). The five meaningful contexts add +8.45 to +12.96 points, authority documents highest. The controls add little: blank +2.19, noise +0.76, nature +0.72. So it is the meaning of the visual context, not the mere presence of an image, that raises ASR here.
Right, Table 3 (carrier): TEXT 50.70% ASR, OCR 40.59%; CASR TEXT 50.89%, OCR 42.34%; mismatch TEXT 0.37%, OCR 4.14%. OCR is weaker even after removing misreads, so rendering an instruction in an image is not automatically stronger. The long deck's Table 4 shows the carrier effect is model-dependent (about 50 points for LLaVA-OneVision, about 1 for Qwen2.5-VL and Claude).
Third finding, not charted: prompt framing is the largest factor, with more than 40 points between best and worst style.
Lessons: always run a TEXT arm; treat text-side framing as a variable; report misreads. Caveat: ASR only, internals on one model (gemma3-12b).

## Slide 7: Any image, even a blank one, raises the unsafe rate

CMRM's observation: a VLM's language backbone is safe on text, but adding an image degrades safety. Setup: the same harmful text query in five input forms: text only, text plus the image's caption, text plus a Gaussian-noise image, text plus a blank image, and original image plus text. Dataset VLSafe (1,110 malicious queries), model LLaVA-1.5-7B, metric unsafe rate from a Llama-3.1-8B-Instruct judge.
Chart: text only 1.91%, caption 5.52%, noise image 57.21%, blank image 56.87%, original 61.53%. With no image or only a caption the model behaves like its safe backbone; with any image, even a blank one, the rate jumps by more than 50 points. For this model and dataset, the image's presence does most of the damage. That is why our design has a clean-image arm.
Method, for understanding only: h_o is the hidden state for the original input, h_c for a corrupted image, h_t for text alone. Assume the state is the ideal state plus an image-induced shift, which gives h* = h_o + alpha (h_t minus h_c). It is applied at inference with no weight change. We do not build this as a defense; the size of h_t minus h_c per layer is a measurement we reuse.

## Slide 8: Qwen2-VL refuses early, and the model gap is large

SafetyReminder's observation: a jailbroken VLM often starts to comply and only adds 'this is illegal' at the end. Terms: a safety token is a refusal or warning word ('sorry', 'illegal', 'cannot'); its relative position is where it falls in the reply, 0 at the start and 1 at the end; a prefilling attack forces the reply to begin with an affirmative opening such as 'Sure, here is'.
Fig. 2 plots the density of safety tokens by position, for a harmful dataset and for a prefilling attack. For LLaVA-1.5-7B both curves peak near the end. For Qwen2-VL-7B the plain harmful prompts put safety tokens near the start (the model refuses early) and the prefilling attack moves them to the end. Reading: safety wording clusters at the two ends and is largely absent in the middle, and an attack pushes it to the end.
For us: Qwen2-VL is our model family and it refuses early when not attacked, which supports measuring the first token and the first few tokens rather than only the final answer. Earlier drafts attributed an attention result and a 'first five tokens' rule to this paper; neither is in it.

Table 1, ASR (%) on six test sets. LLaVA-1.5-7B with no defense: FigStep 74.9, MMSafety 58.2, SPA-VL 45.6, ImgJP 86.6, GCG 94.0, BAP 97.0, average 76.1. Qwen2-VL-7B no defense: 26.6, 13.2, 1.5, 97.4, 79.0, 82.0, average 50.0. Self-Reminder (a prompt-only defense) helps partly; their trained soft prompt (SAPT) brings the averages to 5.0 and 4.7.
Two readings for us. First, the attack gap between models: FigStep gets 74.9% on LLaVA but 26.6% on Qwen2-VL-7B, which supports the floor-effect risk for our Qwen2-VL-2B pilot, though the 2B model has not been measured. Second, Table 2 reports the cost side: utility on MM-Vet (LLaVA 27.9 to 28.0, Qwen 52.3 to 52.6) and the refusal rate on benign questions (2.3 to 3.7, and 3.7 to 4.1), while another defense, BlueSuffix, cuts Qwen2-VL's capability to 13.4 and lifts refusals to 35.8%. The lesson is to report safety and over-refusal together.
The safety-awareness classifier (SVD plus a linear classifier on the last-token hidden state, over 256 harmful and 256 benign text prompts from the Arditi et al. set) parallels our planned refusal direction; we would use a difference of means per layer. We do not use SAPT, which is trained.

## Slide 9: Three questions, each with a way to be wrong

The papers each change one thing and mostly report ASR. What we have not seen in these eight is a study that, on the same inputs in one frozen model, varies how visible the image instruction is, varies how strong the text-side system instruction is, and looks at the refusal signal inside the model.
Caution on novelty: related sweeps exist (font size, opacity and position of typographic distractors; typographic prompt injection; a 12-font-size study). They are on the to-read list because I have only seen abstracts. Their question is distraction or injection success, not safety arbitration with a graded system role and internals, but that needs checking against the full papers.
The three questions. H1: once the image text is legible, execution rises with visibility; the shape of the curve is the finding. H2: stronger system-role instructions lower execution but do not remove it at high visibility. H3: in conflict cases the hidden state projects less onto the refusal direction than the text-only baseline from mid-depth onward, and first-token refusal probability predicts the final behaviour. Each has a stated way to be wrong; there are no numeric thresholds because we have no data yet.

## Slide 10: Four arms, two factors, controlled visibility

Four arms give the controls the papers were missing. TEXT carrier: the harmful instruction as plain text, so we know what the model refuses at all (the VLSBench lesson, in place of an 'image removed' control that would be trivially safe). Clean image: isolates the effect of an image being present (HADES, CMRM). Benign typographic: a harmless instruction in the image, which measures whether the model reads and obeys image text. Harmful typographic: the conflict arm.
Two factors on top. Visibility is relative to the image, not in points: a fixed 784 x 784 canvas (28 x 28 patches in Qwen2-VL), text height 16 to 96 px, and the generator refuses to build an image where the text would clip. Hierarchy uses the real system role, S0 to S3, where S3 says text inside images is untrusted. For Qwen2-VL, S0 and S1 are identical because its chat template inserts the same default system message.
First pass: 6 harmful and 3 benign instructions, 270 prompts and 55 images. These gate the larger run; they are not a benchmark. The three images shown are the same instruction at three visibilities.

## Slide 11: What the model did, and how it is judged

Four labels, not three. Transcription is the one that matters: if the user asks 'describe the text' and the model reads out the image text, that is correct behaviour, not an attack. The first pilot's keyword classifier counted any reply containing words like 'script' or 'step' as unsafe compliance and would have scored this wrongly.
Judge: an LLM with a written rubric, a refusal-phrase list used only as a prefilter, and a human audit of about 100 responses with agreement reported. This is where the ASR variants in the papers (manual best-of-5, classifier, GPT score, string match) bite: we state ours and keep the raw responses.
Calibration: begin with the TEXT arm and keep only items the model refuses as plain text, otherwise there is nothing for the image to override. Legibility covariate: transcription accuracy on benign text at each size separates 'could not read it' from 'read it and refused'.
Statistics: bootstrap confidence intervals, paired comparisons across matched conditions, greedy decoding with a sampling check.

## Slide 12: Three inference-only measurements, then interventions

All three are inference-only; weights never change. First-token behaviour: the probability on refusal openers versus compliance openers at step one, then the first few tokens; the runner already saves the top-10 first-token distribution (idea from SafetyReminder). Refusal direction: the difference of mean hidden states between harmful and harmless text-only prompts for the same model (the refusal-direction idea of Arditi et al., cited from memory and still to be read), projected layer by layer for conflict cases against the text-only baseline and clean-image control (the CMRM-style comparison). Attention to image tokens: these models are decoder-only, so image tokens enter through self-attention, not cross-attention; we normalise by token count and drop the first sink token.
Attention is correlational, so causal claims come from interventions: block attention to image tokens at chosen layers, swap activations between conflict and control runs, and add or subtract the refusal direction. These are diagnostics, not a defense. JailBound-style probes are kept only as a check that the information is linearly accessible.

## Slide 13: What exists, and the main risk: a floor effect

Built and checked: a v2 generator (270 prompts, 55 images, every instruction fits at every size) and a runner for Qwen2-VL that saves raw responses and first-token distributions. A dry run validated the pipeline. No model has been run, so nothing in this deck is our own result.
What the first pilot got wrong and v2 fixes: clipped instructions at large sizes, no controls, a keyword labeller that mislabels transcription, 'system' text placed in the user turn, absolute paths.
Models: Qwen2-VL-2B-Instruct for development, Qwen2-VL-7B for a scale check, LLaVA-1.5-7B as a positive control. Main risk is a floor effect: ADPO reports 4.5% typographic ASR on Qwen2-VL-7B but 22.2% on LLaVA-1.5-7B. Gate 0 therefore runs the TEXT arm and the benign typographic arm first. The first run downloads about 4.5 GB of weights, which needs your go-ahead. If Qwen resists image instructions, that is itself a result and LLaVA still gives contrast.

## Slide 14: Plan, threats to validity, and what the findings would mean

Five to six weeks. Week 1 Gate 0 and judge calibration; week 2 hierarchy-by-task factorial on Qwen2-VL-2B and LLaVA-1.5; week 3 visibility sweeps with the legibility covariate; week 4 mechanism measurements and interventions; week 5 Qwen2-VL-7B replication and analysis; week 6 write-up.
Threats to validity, the first two to lead with: judge validity (rubric plus human audit) and legibility (measured). Also a small hand-written instruction set, two model families only, attention being correlational, and overlap with prior sweeps still to read.
What it would mean for alignment: this project builds no defense. If the refusal direction collapses at particular depths, a future method knows where to act. If some system-role levels fail at high visibility, hierarchy-aware training data must cover them. If the first-token refusal probability predicts the outcome, it is a cheap monitoring signal. Asked 'so does it make models safer', the honest answer is no, it shows where and when they fail.
