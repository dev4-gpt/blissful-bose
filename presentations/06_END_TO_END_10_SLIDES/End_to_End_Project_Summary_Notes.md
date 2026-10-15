# End-to-end project summary: speaker notes

Ten slides: question, literature (papers 1 to 4 and 5 to 8), gap and questions, design, measurement, mechanism, status, plan.

## Slide 1: Cross-Modal Signal Conflict in Post-Trained Vision-Language Models

This is the short version of the whole project. Ten slides, one storyline: the question, what the eight papers teach us, the gap, the design, how we measure behaviour, how we look inside the model, where we are, and the plan.
Two companion decks hold the detail. 'Deep Dive, Papers 1 to 4' explains every metric and table of FigStep, HADES, SIUO and VLSBench; 'Deep Dive, Papers 5 to 8' does the same for the other four. Use them as backup when someone asks 'what does that number mean'.
Honesty line to say early: this is a proposal. The stimulus generator and runner exist and pass a dry run, but no model has been run, so there are no results of our own in this deck.

## Slide 2: Two channels, one answer

Left to right: the user's text and the image each carry a signal; a frozen VLM turns both into one answer. The answer may be a refusal, an execution of the image's instruction, or only a reading of the image text. The third case is not an attack and must not be counted as one.
Why a conflict is plausible: the language backbone of most open VLMs was safety-aligned on text, while the vision encoder and projector were not (SIUO). Adding an image, even a blank one, shifts hidden states (CMRM, HADES).
Why it is still open: FigStep raised ASR from 44.8% to 82.5% on six open VLMs, yet ADPO's Table 1 reports only 4.5% typographic-jailbreak ASR on Qwen2-VL-7B (22.2% on LLaVA-1.5-7B). So 'can the image win' is known; 'when and why' is not.
Purpose and limits, as the advisor set them: we study how alignment fails, to inform future methods. No defense, no benchmark, no training; weights stay frozen.

## Slide 3: Papers 1 to 4: the attack, its parts, and how to measure it fairly

Read each row as: what the paper did, the one number to remember, and the design rule we take.
FigStep: a harmful request rendered as a numbered-list image plus a benign text prompt. 44.8% to 82.5% mean ASR on six open VLMs. Note the protocol: ASR counts a question as a success if any of five tries is harmful, so single-try rates are lower (MiniGPT4 and CogVLM drop to about 60%).
HADES: typography, then a diffusion image, then adversarial noise. LLaVA-1.5 goes 65.60 to 78.53 to 90.26; GPT-4V 1.73 to 15.07. The last step needs gradients, so it cannot be run on closed models. We copy the one-factor-at-a-time ablation style.
SIUO: 167 cases where the image and text are each safe but the combination needs care. Best model (GPT-4V) gives a safe reply 53.29% of the time; LLaVA-1.5-7B 21.56%. Conflict does not need harmful words, so our judge must read meaning, and a refusal is not automatically the right reply.
VLSBench: in four older benchmarks the text alone already carries the harm (R1 minus R2 is under 1 point), so text-only alignment looks sufficient. On 2,241 leak-free pairs the safe rates collapse: GPT-4o 21.4%, Qwen2-VL 13.8%, LLaVA-1.5-7B 6.6%. Our user text will carry no harm cue.
Backup: the Deep Dive 1 to 4 deck defines ASR, PPL, Typ image, T2I pointer, Opt image, Adv image, safe rate, effective rate, R1 and R2 with worked examples.

## Slide 4: Papers 5 to 8: which factor matters, and where to look inside

MMJailBench crosses intent, framing, visual semantics and carrier (272 x 6 x 5 x 2 = 16,320 cases per model, 16 models). Framing moves ASR by more than 40 points; meaningful visuals add 8.45 to 12.96 points; blank, noise and nature images add under 2.2. The OCR carrier is weaker than plain text (40.59% vs 50.70%), so a rendered instruction is not automatically stronger. Hence we always include a TEXT arm.
CMRM: a PCA of hidden states shows that text-only and with-image inputs form separate clouds, even with a blank image. Its correction method is training-free but is a defense, which we do not build; we keep the idea of measuring the shift per layer, with a blank-image control.
JailBound: per-layer logistic-regression probes separate safe from unsafe inputs; accuracy is poor in layers 0 to 4 and near-perfect deep. Its attack ASR (94.3% white-box) uses a string-match judge that counts any reply without a refusal phrase as a success, so it is far more lenient than judged numbers elsewhere. The attack needs gradients; we do not use it.
SafetyReminder: safety wording sits near the start of a response normally and moves toward the end under a prefilling attack (Qwen2-VL-7B, Fig. 2). It trains a soft prompt as a defense; we use only the idea that refusal has a position, so we measure the first token and the early tokens.
Also relevant: SafetyReminder's Table 1 gives FigStep ASR of 26.6% for Qwen2-VL-7B against 74.9% for LLaVA-1.5-7B, which supports the floor-effect risk for our Qwen2-VL-2B pilot.

## Slide 5: Three questions, each with a way to be wrong

The papers each change one thing and mostly report ASR. What we have not seen in these eight is a study that, on the same inputs in one frozen model, varies how visible the image instruction is, varies how strong the text-side system instruction is, and looks at the refusal signal inside the model.
Caution on novelty: related sweeps exist (font size, opacity and position of typographic distractors; typographic prompt injection; a 12-font-size study). They are on the to-read list because I have only seen abstracts. Their question is distraction or injection success, not safety arbitration with a graded system role and internals, but that needs checking against the full papers.
The three questions. H1: once the image text is legible, execution rises with visibility; the shape of the curve is the finding. H2: stronger system-role instructions lower execution but do not remove it at high visibility. H3: in conflict cases the hidden state projects less onto the refusal direction than the text-only baseline from mid-depth onward, and first-token refusal probability predicts the final behaviour. Each has a stated way to be wrong; there are no numeric thresholds because we have no data yet.

## Slide 6: Four arms, two factors, controlled visibility

Four arms give the controls the papers were missing. TEXT carrier: the harmful instruction as plain text, so we know what the model refuses at all (the VLSBench lesson, in place of an 'image removed' control that would be trivially safe). Clean image: isolates the effect of an image being present (HADES, CMRM). Benign typographic: a harmless instruction in the image, which measures whether the model reads and obeys image text. Harmful typographic: the conflict arm.
Two factors on top. Visibility is relative to the image, not in points: a fixed 784 x 784 canvas (28 x 28 patches in Qwen2-VL), text height 16 to 96 px, and the generator refuses to build an image where the text would clip. Hierarchy uses the real system role, S0 to S3, where S3 says text inside images is untrusted. For Qwen2-VL, S0 and S1 are identical because its chat template inserts the same default system message.
First pass: 6 harmful and 3 benign instructions, 270 prompts and 55 images. These gate the larger run; they are not a benchmark. The three images shown are the same instruction at three visibilities.

## Slide 7: What the model did, and how it is judged

Four labels, not three. Transcription is the one that matters: if the user asks 'describe the text' and the model reads out the image text, that is correct behaviour, not an attack. The first pilot's keyword classifier counted any reply containing words like 'script' or 'step' as unsafe compliance and would have scored this wrongly.
Judge: an LLM with a written rubric, a refusal-phrase list used only as a prefilter, and a human audit of about 100 responses with agreement reported. This is where the ASR variants in the papers (manual best-of-5, classifier, GPT score, string match) bite: we state ours and keep the raw responses.
Calibration: begin with the TEXT arm and keep only items the model refuses as plain text, otherwise there is nothing for the image to override. Legibility covariate: transcription accuracy on benign text at each size separates 'could not read it' from 'read it and refused'.
Statistics: bootstrap confidence intervals, paired comparisons across matched conditions, greedy decoding with a sampling check.

## Slide 8: Three inference-only measurements, then interventions

All three are inference-only; weights never change. First-token behaviour: the probability on refusal openers versus compliance openers at step one, then the first few tokens; the runner already saves the top-10 first-token distribution (idea from SafetyReminder). Refusal direction: the difference of mean hidden states between harmful and harmless text-only prompts for the same model (the refusal-direction idea of Arditi et al., cited from memory and still to be read), projected layer by layer for conflict cases against the text-only baseline and clean-image control (the CMRM-style comparison). Attention to image tokens: these models are decoder-only, so image tokens enter through self-attention, not cross-attention; we normalise by token count and drop the first sink token.
Attention is correlational, so causal claims come from interventions: block attention to image tokens at chosen layers, swap activations between conflict and control runs, and add or subtract the refusal direction. These are diagnostics, not a defense. JailBound-style probes are kept only as a check that the information is linearly accessible.

## Slide 9: What exists, and the main risk: a floor effect

Built and checked: a v2 generator (270 prompts, 55 images, every instruction fits at every size) and a runner for Qwen2-VL that saves raw responses and first-token distributions. A dry run validated the pipeline. No model has been run, so nothing in this deck is our own result.
What the first pilot got wrong and v2 fixes: clipped instructions at large sizes, no controls, a keyword labeller that mislabels transcription, 'system' text placed in the user turn, absolute paths.
Models: Qwen2-VL-2B-Instruct for development, Qwen2-VL-7B for a scale check, LLaVA-1.5-7B as a positive control. Main risk is a floor effect: ADPO reports 4.5% typographic ASR on Qwen2-VL-7B but 22.2% on LLaVA-1.5-7B. Gate 0 therefore runs the TEXT arm and the benign typographic arm first. The first run downloads about 4.5 GB of weights, which needs your go-ahead. If Qwen resists image instructions, that is itself a result and LLaVA still gives contrast.

## Slide 10: Plan, threats to validity, and what the findings would mean

Five to six weeks. Week 1 Gate 0 and judge calibration; week 2 hierarchy-by-task factorial on Qwen2-VL-2B and LLaVA-1.5; week 3 visibility sweeps with the legibility covariate; week 4 mechanism measurements and interventions; week 5 Qwen2-VL-7B replication and analysis; week 6 write-up.
Threats to validity, the first two to lead with: judge validity (rubric plus human audit) and legibility (measured). Also a small hand-written instruction set, two model families only, attention being correlational, and overlap with prior sweeps still to read.
What it would mean for alignment: this project builds no defense. If the refusal direction collapses at particular depths, a future method knows where to act. If some system-role levels fail at high visibility, hierarchy-aware training data must cover them. If the first-token refusal probability predicts the outcome, it is a cheap monitoring signal. Asked 'so does it make models safer', the honest answer is no, it shows where and when they fail.
