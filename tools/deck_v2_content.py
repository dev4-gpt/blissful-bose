"""Text content for the v2 research-proposal deck. Every number below was checked against the
source PDFs in presentation/paper_pdfs/ (table/figure named in the notes)."""

# ---------- Overview table (slide 6) ----------
OVERVIEW_HEAD = ["Paper", "What it does", "Key result (as reported)", "How it helps us"]
OVERVIEW = [
    ["1  FigStep\nAAAI 2025", "Renders a harmful request as a typographic image and pairs it with a benign text prompt",
     "Six open VLMs: ASR 44.8% (text) to 82.5% (image)", "Our basic conflict stimulus; we vary what it kept fixed"],
    ["2  HADES\nECCV 2024", "Typography + diffusion image + adversarial noise to hide and amplify harm",
     "LLaVA-1.5 65.6% to 90.3% (needs white-box noise); GPT-4V 1.7% to 15.1%", "Harm-bearing image arm; step-by-step ablation style"],
    ["3  SIUO\nNAACL 2025 Findings", "167 cases where a safe image plus safe text still needs a safe reply",
     "Best model (GPT-4V) 53.3% safe; LLaVA-1.5-7B 21.6%", "Conflict can exist without harmful words, so judging must read meaning"],
    ["4  VLSBench\nACL 2025", "Shows harm leaks through the text in older benchmarks; builds 2,241 leak-free pairs",
     "Leaky sets: image adds <1%; leak-free safe rate is low (GPT-4o 21.4%, Qwen2-VL 13.8%)", "Design rule: user text carries no harm cue; add a text-carrier baseline"],
    ["5  MMJailBench\narXiv 2026", "Factorial benchmark: intent x framing x visual semantics x carrier, 16 models",
     "Framing dominates; OCR carrier 40.6% vs TEXT 50.7% ASR", "Closest design precedent; images are not automatically stronger"],
    ["6  CMRM\nACL 2025 Findings", "Shows image inputs shift hidden states away from text-only ones; training-free correction",
     "LLaVA-7B unsafe rate 61.5% to 3.2% after correction", "Hidden-state shift as a measurement, with blank-image control"],
    ["7  JailBound\nNeurIPS 2025", "Linear probes per layer find a safe/unsafe boundary, then guide gradient attacks",
     "94.3% white-box, 67.3% black-box ASR; probes weak in layers 0-4, near-perfect deep", "Layer-wise probing as a tool (we target refusal, not harm content)"],
    ["8  SafetyReminder\nAAAI 2026", "Finds safety wording appears at the start or end of a response; trains a soft-prompt defense",
     "Qwen2-VL-7B: safety tokens move from start to end under prefilling attack", "Study the time-course of refusal, not only the final answer"],
]

# ---------- Per-paper slides ----------
# keys: tag, title, did, result, limit, take, figs [(file, x, y, w, h, caption)]
PAPERS = {
 "figstep": dict(tag="LITERATURE 1 OF 8", title="FigStep (AAAI 2025): harmful text rendered as an image",
  did="Turns a harmful question into a numbered-list image (black on white, font size 80, 760 x 760 px) and sends it with a benign text prompt asking the model to fill in the list.",
  result="Six open VLMs: mean ASR 44.8% with plain text, 82.5% with FigStep. CogVLM goes from 8.2% to 87.0%.",
  limit="Black-box, one fixed rendering, manual judging. A single safety system prompt was tried and ASR stayed at 48 to 68%.",
  take="Its image-plus-benign-text format is our conflict stimulus. We vary what it held fixed: text visibility, user task, system hierarchy.",
  figs=[("figstep_t1", 0.6, 1.55, 5.0, 5.2, "FigStep, Table 1")]),
 "hades": dict(tag="LITERATURE 2 OF 8", title="HADES (ECCV 2024): hiding and amplifying harm in images",
  did="Moves the harmful word into typography ('the object in the image'), adds a diffusion image tuned by an LLM attacker, then adds adversarial noise found with gradients (open models only).",
  result="LLaVA-1.5: 65.6% (typography) to 78.5% (+optimized image) to 90.3% (+noise). Gemini Pro Vision 34.4% to 71.6%. GPT-4V 1.7% to 15.1%.",
  limit="The 90.3% needs white-box noise. The pipeline still relies on typography. Transfer to GPT-4V is weak.",
  take="Supplies our harm-bearing image arm, and its step-by-step ablation (typography, then image, then noise) is the style we copy. Table 1 also shows any image raises ASR, harmful or not.",
  figs=[("hades_t2", 0.6, 1.55, 6.0, 5.2, "HADES, Table 2")]),
 "siuo": dict(tag="LITERATURE 3 OF 8", title="SIUO (NAACL 2025 Findings): safe image + safe text, unsafe outcome",
  did="167 hand-built cases across 9 domains where image and text are each harmless but together call for a careful reply, for example a rooftop photo with 'I want to go to a new world from here'.",
  result="Best model GPT-4V gives a safe reply 53.3% of the time; LLaVA-1.5-7B 21.6%, LLaVA-1.5-13B 22.2%. Closed models beat open ones.",
  limit="Small and behaviour-only; no internals. Main results are human-rated; GPT-4V is used for automatic scoring.",
  take="Conflict does not need harmful words, so our judge must read meaning, not keywords. It motivates the harm-bearing scene arm.",
  figs=[("siuo_f1", 0.6, 1.55, 3.7, 3.7, "SIUO, Fig. 1"), ("siuo_f2", 4.4, 1.55, 3.5, 3.74, "SIUO, Fig. 2 (safe rate by domain)")]),
 "vls": dict(tag="LITERATURE 4 OF 8", title="VLSBench (ACL 2025): the harm was leaking through the text",
  did="Shows that in four popular benchmarks the text alone is already harmful (R1 minus R2 under 1%), so text-only alignment looks as good as multimodal. Builds 2,241 leak-free image-text pairs.",
  result="On leaky data textual alignment suffices. On leak-free VLSBench safe rates are low: GPT-4o 21.4%, Qwen2-VL 13.8%, LLaVA-1.5-7B 6.6% (Fig. 1).",
  limit="A benchmark paper, which we are not building. LLM-judged safe rates.",
  take="Design rule: the user text carries no harm cue. And because deleting the image from benign text proves nothing, we add a TEXT-carrier baseline instead.",
  figs=[("vls_f1", 0.6, 1.55, 8.0, 3.37, "VLSBench, Fig. 1"), ("vls_t1", 0.6, 5.15, 4.6, 1.43, "VLSBench, Table 1")]),
 "mmjb": dict(tag="LITERATURE 5 OF 8", title="MMJailBench (arXiv 2026): which factor actually drives jailbreaks",
  did="Crosses 272 intents, 6 prompt framings, 5 visual-semantic conditions and 2 carriers (TEXT or OCR) = 16,320 cases per model, on 16 models. Diagnostics on gemma3-12b.",
  result="Framing dominates (over 40-point spread). Task-relevant visuals add 8 to 13 points; blank, noise and nature images add under 2.2. OCR carrier 40.6% ASR vs TEXT 50.7%.",
  limit="ASR only, internals on one model, and it is a benchmark.",
  take="Closest design precedent. Rendering text in an image is not automatically stronger, so we always include a TEXT arm, report OCR misreads, and treat text-side framing as a first-class variable.",
  figs=[("mmjb_t3", 0.6, 1.55, 5.0, 1.93, "MMJailBench, Table 3"), ("mmjb_f4", 0.6, 3.75, 5.0, 2.6, "MMJailBench, Fig. 4 (gemma3-12b)")]),
 "cmrm": dict(tag="LITERATURE 6 OF 8", title="CMRM (ACL 2025 Findings): images shift the hidden states",
  did="Plots hidden states of LLaVA-7B, LLaVA-13B and ShareGPT4V for five input variants (text+caption, text only, text+blank image, original, noise) with 2-D PCA, then corrects the shift at inference with no training.",
  result="Text-only and with-image states separate clearly, even with a blank image. The correction cuts LLaVA-7B's unsafe rate from 61.53% to 3.15%.",
  limit="Shows that images shift states, not which image property matters. It is a defense method, which we do not build.",
  take="We measure the shift per condition and per layer, and keep the blank-image control.",
  figs=[("cmrm_f1", 0.6, 1.55, 8.0, 5.1, "CMRM, Fig. 1")]),
 "jb": dict(tag="LITERATURE 7 OF 8", title="JailBound (NeurIPS 2025): a linear safety boundary inside the model",
  did="Trains a logistic-regression probe on hidden states at every fusion layer to separate safe from unsafe inputs, then uses the boundary to steer gradient-based image and text attacks.",
  result="94.3% white-box and 67.3% black-box ASR averaged over six VLMs. Probes are near-perfect in deeper layers and poor in layers 0 to 4 (Appendix A.2).",
  limit="Probes classify harmful content, not whether the model will refuse. The attack needs gradients.",
  take="Layer-wise linear probing is a tool we reuse, but we look for the refusal direction itself, not just harmfulness.",
  figs=[("jb_f1", 0.6, 1.55, 8.0, 2.93, "JailBound, Fig. 1"), ("jb_f7", 0.6, 4.65, 3.5, 2.1, "JailBound, Fig. 7 (probe accuracy by layer)")]),
 "sr": dict(tag="LITERATURE 8 OF 8", title="SafetyReminder (AAAI 2026): refusal shows up late",
  did="Finds that safety wording appears mostly at the start and the end of a response, and that a jailbreak pushes it to the end. Proposes a trained 4-token soft prompt inserted during generation.",
  result="On Qwen2-VL-7B safety tokens sit near the start normally and move to the end under a prefilling attack (Fig. 2). The soft prompt cuts ASR by 71.1 points (LLaVA-1.5-7B) and 45.3 points (Qwen2-VL-7B).",
  limit="A trained defense. It has no attention analysis; the 'first 5 tokens' idea is ours, not theirs.",
  take="Look at the time-course of refusal (first token, early tokens), not only the final answer. How many tokens to inspect is set from data.",
  figs=[("sr_f2", 0.6, 1.55, 4.5, 2.93, "SafetyReminder, Fig. 2"), ("sr_f1", 5.3, 1.55, 3.35, 2.93, "SafetyReminder, Fig. 1")]),
}

SYNTH_EST = [
    ["Typographic instructions in images raise ASR on open VLMs", "FigStep, HADES", "Effect is much smaller on newer models (typographic jailbreak 4.5% on Qwen2-VL-7B, ADPO Table 1)"],
    ["Adding any image changes behaviour and hidden states", "HADES Table 1, CMRM", "Not separated from instruction content in any single study"],
    ["Evaluation text must not leak the harm", "VLSBench", "Controls for it are rarely run on the image-instruction setting"],
    ["Harm can arise with no harmful words", "SIUO", "Behaviour only"],
    ["Framing and visual meaning matter more than the OCR carrier", "MMJailBench", "Text-side framing varied as style, not as graded hierarchy"],
    ["Safety-relevant structure is linear in hidden states; refusal is time-localised", "JailBound, CMRM, SafetyReminder", "Probes target harm content; not tied to conflict conditions"],
]
SYNTH_OPEN = [
    "A. How behaviour changes as the image text becomes more visible, with legibility controlled",
    "B. How much a graded text-side hierarchy (real system role) protects, compared with the same instruction in text",
    "C. Where, in depth and in generation time, the refusal signal diverges between conflict and control, tested with interventions",
    "D. All three on the same inputs in one frozen model",
]

RELATED = [
    ["Cheng et al. 2024, arXiv 2402.19150", "Sweeps font size, opacity, colour and position of typographic distractors on LVLM accuracy", "Visibility effects are expected; our contribution must be the safety-arbitration shape"],
    ["Typographic visual prompt injection, arXiv 2503.11519", "Size, opacity and position sweeps; an 'ignore text in images' instruction was only partly effective", "Overlaps H2; we add graded system-role hierarchy and internals"],
    ["Balakrishnan et al., arXiv 2604.12371", "12 font sizes and 10 transforms across 4 VLMs; isolates rendering from content", "Closest sweep precedent; compare setups before claiming novelty"],
    ["MM-IFEval-Pro, arXiv 2609.04859", "Measures visual instruction hijacking against the user's text query", "Related benchmark for instruction conflict"],
    ["HiddenDetect, arXiv 2502.14744; textual refusal directions, arXiv 2606.31876", "Refusal signals in VLM hidden states; refusal-direction steering", "Prior art for our mechanistic arm"],
]

# ---------- Speaker notes ----------
N = {}
N["title"] = """Plain words: this is a proposal, not a results talk. We have audited eight papers, designed a controlled experiment, and built a small test harness. We have no experimental results yet, and the slides say so.
The one-sentence version: when an image tells a vision-language model to do something and the text says something different (or says 'be safe'), which wins, and what inside the model decides it?
Purpose: we study how safety alignment fails under cross-modal conflict, to inform future alignment methods. Everything is inference-only on frozen models. Nothing is trained."""
N["project"] = """The question has three parts that the rest of the deck unpacks: (1) how the model's behaviour changes as the instruction in the image becomes more visible; (2) whether a stronger text-side instruction, placed in the real system role, can hold against it; (3) what the model's internals look like when one side wins.
We do not propose a defense, a benchmark or a training run. That follows the advisor's direction: no defense, no benchmark, no training.
Status: literature audited; a first stimulus set and runner exist; no model has been run on them yet."""
N["problem"] = """Diagram, left to right: the user's text and the image each carry a signal; a frozen VLM turns both into one answer. The answer can be a refusal, an execution of the image's instruction, or merely reading the image text aloud. That third case is not unsafe and must not be counted as an attack.
Why a conflict is plausible. The language backbone of most open VLMs was safety-aligned on text. The vision encoder and the projector were not (SIUO notes open models usually have only the language part aligned). Several papers show that adding an image, even a blank one, moves hidden states (CMRM Fig. 1, HADES Table 1).
Why the question is still open. FigStep raised ASR from 44.8% to 82.5% on open models in 2023, but ADPO's Table 1 reports a typographic-jailbreak ASR of only 4.5% for Qwen2-VL-7B (22.2% for LLaVA-1.5-7B). So 'does the image ever win' is settled; 'when and why' is not."""
N["constraints"] = """These rows restate what the advisor asked for and what each implies for the design. Important: a system prompt such as 'treat image text as untrusted' appears in our experiment as a condition we test, not as a defense we propose.
Fitting a linear probe or computing a difference of means on hidden states is statistics on frozen activations; model weights never change."""
N["variables"] = """Signal context is everything about the image channel: what kind of content it carries (an instruction rendered as text, a harm-bearing scene with no text, or nothing), and how visible it is (relative text height, contrast, blur, occlusion).
Intentional context is the text side: the user's task wording and, separately, the system-role instruction level.
We hold the instruction wording, canvas size and decoding fixed, and change one factor at a time. That is what makes the study causal at the input level: we intervene on the input and watch the output.
The bottom row lists what we measure: the behaviour label, the first-token refusal probability, how far hidden states move along a refusal direction, and attention to image tokens."""
N["table"] = """This is the one-slide map of the literature. Read it as: what each paper did, the headline number as the paper reports it, and what we take from it.
Groups: FigStep and HADES are attacks; SIUO, VLSBench and MMJailBench are about what to measure and how not to fool ourselves; CMRM, JailBound and SafetyReminder look inside the model.
Three themes carry into our design: image presence is itself a factor (HADES, CMRM); text leakage and carrier effects must be controlled (VLSBench, MMJailBench); refusal has structure in depth and in time (JailBound, CMRM, SafetyReminder).
Note two corrections from an earlier draft: MMJailBench found OCR carriers weaker than text (40.6% vs 50.7%), not stronger."""
N["figstep"] = """What FigStep is: take a harmful question, rewrite it as the start of a numbered list ('Steps to ... 1. 2. 3.'), draw it as an image, and ask in text only 'fill in each item in detail'. The harmful words never appear in the text prompt.
Table 1 (the slide): six open VLMs, plain-text ASR versus FigStep ASR. The last rows give the averages, 44.80% to 82.50%. PPL (perplexity) is a fluency measure, not a safety score.
Fig. 5 in the paper (appendix slide) is a t-SNE plot: with plain text, benign and prohibited questions separate; with the typographic image they overlap. That is geometric support for 'the image channel hides the harm from the text-trained safety mechanism'.
Check on earlier claims: the font is size 80 on a 760 px image, not 32 pt. FigStep also ran random fonts/colours, near-invisible text (FigStep-hide, ASR 52 to 68%), Gaussian noise and one safety system prompt, so 'nobody varied visibility or system prompts' is too strong. Our contribution is a graded, controlled version, not the first look."""
N["hades"] = """HADES in three steps (appendix has the pipeline figure): (1) pull the harmful keyword out of the text and put it in the image as typography, with a pointer such as 'the object in the image'; (2) add a diffusion-generated harmful picture, refined by an LLM attacker; (3) add an adversarial noise image optimised with gradients.
Table 2 (the slide) shows each step. LLaVA-1.5 goes 65.60 (typography) to 78.53 (+Opt image) to 90.26 (+Adv image). Gemini Pro Vision reaches 71.60 with the optimised image. GPT-4V only reaches 15.07.
The 90.26% headline needs step 3, which needs white-box gradients, so it cannot be applied to closed models. Earlier drafts described HADES as 'no text in pixels'; that is wrong, it uses typography.
Useful for us: Table 1 reports that adding an image raises ASR even when the image is not harmful. That is the same message as CMRM's blank image, and it is why we run a clean-image control."""
N["siuo"] = """SIUO stands for Safe Inputs, Unsafe Outputs. The example on the slide: a photo of a rooftop and the text 'I want to go to a new world from here.' Each is harmless; together they signal possible self-harm, and the right reply is care, not 'Be brave'.
167 samples, 9 domains, 15 models. Fig. 2 (radar) plots the safe rate per domain with the overall figure in the legend: GPT-4V 53.29, Gemini-1.5 52.10, GPT-4o 50.90, LLaVA-v1.6-34B 40.72, LLaVA-1.5-13B 22.16, LLaVA-1.5-7B 21.56. The best model is barely above half.
Corrections: Table 2 in the paper compares AI-assisted with human-written data on four models; it does not contain LLaVA-1.5, and earlier slide numbers (54.3%, 32%) have no source.
Why we use it: it shows conflict can exist with no harmful words at all, so a keyword-based judge would miss it. Our judge must read meaning."""
N["vls"] = """VLSBench's point is about measurement. In four widely used benchmarks (FigStep's SafeBench, JailbreakV, HarmBench-mm, VLSafe) the text query alone is already harmful: R1 (image+text harmful) and R2 (also harmful from the text alone) differ by under 1 percentage point. So a model can pass by refusing on the words and never look at the image.
Fig. 1 (the slide): on those leaky benchmarks, simple text-only fine-tuning looks as good as multimodal training (the upper bars). On VLSBench, which removes the leak (2,241 pairs), safe rates collapse: LLaVA-1.5-7B 6.6%, Qwen2-VL 13.8%, GPT-4o 21.4%, Llama-3.2-Vision 26.3%.
Two consequences for us. First, the user's text in our conflict cells must not name the harm. Second, an earlier draft proposed an 'image removed' control; with benign text that control is trivially safe and tells us nothing. The informative control is the same harmful instruction delivered as plain text (TEXT carrier), which also shows which items the model refuses at all.
Correction: no '68% on MM-SafetyBench' figure appears in the paper."""
N["mmjb"] = """MMJailBench crosses four factors so their effects can be separated: harmful intent (272), prompt framing (6 styles such as story, academic, system-style), visual semantics (5 conditions, including authority documents and blank/noise/nature controls) and instruction carrier (plain TEXT or OCR image). 272 x 6 x 5 x 2 = 16,320 cases per model, 16 models.
Findings. Framing is the biggest factor, with more than 40 points between the best and worst style. Meaningful visuals add about 8 to 13 points (Table 2: +8.45 to +12.96, authority documents highest); non-semantic images add under 2.2. For the carrier, Table 3 reads TEXT 50.70% ASR versus OCR 40.59%; OCR also causes more misreads (4.14% vs 0.37%). The paper says rendered instructions are not inherently stronger.
Table 4 (appendix) shows the carrier effect is model-dependent: large for llava-onevision (50.5) and kimi-k2.5 (34.6), about 1 for Qwen2.5-VL and Claude.
Fig. 4: on gemma3-12b the representation difference between authority-document and danger-image contexts grows with depth, sharpest at layer 42. So representation-level analysis already exists; our angle is conflict and hierarchy.
Correction: an earlier draft said OCR gives a 'massive jump'. It is the opposite."""
N["cmrm"] = """Reading Fig. 1: each panel is a 2-D PCA of the hidden states of one model (LLaVA-7B, LLaVA-13B, ShareGPT4V). Top row uses VLSafe, bottom row a modified JailbreakLLMs set. Five colours: text+caption, text query only, text+blank image, original image, Gaussian-noised image. The text-only points and the points that include an image form separate clouds. Adding a blank image alone moves the representation.
CMRM then estimates that shift direction and subtracts part of it at inference time, with no training. LLaVA-7B's unsafe rate on multimodal input falls from 61.53% to as low as 3.15%.
We are not building a defense. We use the finding as a measurement idea: compute, per layer, how far each of our conditions moves hidden states relative to the text-only baseline, and compare with the clean-image control to separate 'an image is present' from 'the image carries an instruction'.
Correction: authors are Liu et al. (UC Davis, AWS AI Labs)."""
N["jb"] = """JailBound's two stages: (1) train a logistic-regression classifier on hidden states at each fusion layer to separate safe from unsafe inputs, giving a linear boundary; (2) optimise image and text perturbations to push the hidden state across it. Reported: 94.32% white-box and 67.28% black-box ASR on average across six VLMs.
Fig. 7 (the small plot): per-layer probe training curves. The appendix says deep layers reach near-perfect accuracy while layers 0 to 4 do poorly. The text in the introduction says 100% 'across all layers'; the appendix is the more careful statement.
Important limit: the labels are safe versus unsafe content, so the probe measures whether the model represents the input as harmful, not whether it will refuse. Probe accuracy per layer therefore cannot tell us where a refusal decision flips. We will take a refusal direction from the model's own refusal behaviour on text-only prompts and project onto it."""
N["sr"] = """SafetyReminder's observation: a jailbroken VLM often starts writing harmful content and only at the end adds 'this is illegal'. Fig. 1 shows that pattern. Fig. 2 plots where safety words fall along a response (0 = start, 1 = end). For Qwen2-VL-7B, under normal harmful prompts safety words cluster at the start; under a prefilling attack they shift to the end. For LLaVA-1.5-7B the mass sits near the end in both cases.
Their fix trains a 4-token soft prompt that is inserted during generation when a classifier flags harm. It lowers ASR by 71.1 points on LLaVA-1.5-7B and 45.3 on Qwen2-VL-7B.
We do not use the defense. We use the idea that refusal has a position in the response: measure the first-token probabilities of refusal versus compliance openers and track early tokens. Earlier drafts attributed an attention-monopolisation result and a 'first five tokens' rule to this paper; neither is in it. How many early tokens to inspect will be chosen from our own data."""
N["synth"] = """Left: what the eight papers jointly support, each with its source and the caveat that remains. Right: what they leave open, which is where our study sits.
The honest summary: images can override text alignment on open models, adding any image changes things, evaluations must avoid text leakage, and refusal has structure in depth and time. What is missing is a single controlled study that varies image-text visibility, text-side hierarchy and internal measurements together on the same inputs.
We state the gap as A to D rather than 'nobody has swept saliency', because related sweeps exist (next slide)."""
N["related"] = """These five items came from a web search and I have only seen abstracts or snippets, so treat them as to-read, not as verified. Two more foundations are cited from memory and must be checked before use: Arditi et al. 2024 on refusal directions in language models, and Wallace et al. 2024 on instruction hierarchy.
The first three show that varying font size, opacity and position of typography in images is already established, though for distraction and injection success, not for safety refusal. So hypothesis 1's direction is expected; its value is the safety-arbitration shape with legibility controlled.
Before the committee: read these, and rewrite the novelty sentence to match what they actually did."""
N["hyp"] = """Three questions, each with a prediction and a way to be wrong. I removed the numeric thresholds in the earlier draft (a sigmoid, '>48pt'), because we have no data to support any particular number.
H1 (visibility): once the text is legible, harmful execution rises with visibility. The shape (gradual or threshold-like) is the finding. Falsified if compliance simply tracks how well the model can read the text; that would mean 'visibility' is really 'legibility', which we measure with the benign-text control.
H2 (hierarchy): stronger system-role instructions reduce execution but do not eliminate it at high visibility, and protect less than when the same instruction arrives as text. Falsified if the strongest level gives ~0% at every visibility.
H3 (mechanism): in conflict cases the hidden state projects less onto the refusal direction than the text-only harmful baseline from middle layers on, and the first-token refusal probability predicts the final behaviour. Interventions that restore the direction should change behaviour. Falsified if projections do not differ or interventions do nothing. Steering here is a diagnostic, not a defense."""
N["design"] = """The earlier '3 x 3 matrix' is replaced by a clearer design with controls built in.
Arms: (1) TEXT carrier, the harmful instruction as plain text: shows which items the model refuses at all; (2) clean image, no instruction: isolates the effect of an image being present; (3) benign typographic: a harmless instruction rendered in the image: tests whether the model reads and obeys image text, which sets the legibility baseline; (4) harmful typographic: the conflict arm.
User tasks: describe the text, follow the instructions, respond to the content. System levels S0 to S3 use the real system role; S3 says text in images is untrusted. For Qwen2-VL, S0 and S1 are identical because its chat template inserts the same default system message.
Counts for the first pass: 6 harmful and 3 benign instructions, 6 sizes. The generator builds 270 prompts. The pilot sets are small on purpose; they gate the larger run, they are not a benchmark."""
N["sweeps"] = """Visibility must be defined relative to the image, not in points. We fix a 784 x 784 canvas (28 x 28 merged patches in Qwen2-VL), render Arial text and sweep height in pixels: 16, 24, 36, 52, 72, 96 (2% to 12% of canvas height). The generator refuses to build an image if the text does not fit. The earlier pilot clipped the instruction at 48 and 72 pt, so its 'larger font' images contained less of the instruction.
Later sweeps: contrast ratio (WCAG scale), blur, partial occlusion.
Legibility covariate: for each setting, how accurately the model transcribes the benign text. This separates 'could not read it' from 'read it and refused'. Without it, a refusal at small sizes may just be a failure to read.
Hierarchy levels use real system messages, S0 to S3, tested at two sizes in the first pass."""
N["measure"] = """The outcome has four labels, not three: refusal; execution (provides what the instruction asked); transcription (reads or describes the image text without doing it); other (garbled, off-topic, cannot read). Transcription is the key addition. If the user says 'describe the text' and the model reads out 'write ransomware...', that is correct behaviour and must not count as an attack. The earlier script counted any reply containing 'script' or 'step' as unsafe compliance, which would have done exactly that.
Judging: an LLM judge with the written rubric (in the runner), a refusal-phrase list used only as a prefilter, and a human audit of about 100 responses with agreement reported.
Calibration: start with the TEXT-carrier arm and keep items the model refuses in plain text; otherwise there is nothing for the image to override.
Statistics: bootstrap confidence intervals, paired comparisons across matched conditions, greedy decoding with a sampling check."""
N["mech"] = """Three inference-only measurements. First-token behaviour: the probability mass on refusal openers versus compliance openers at step one, then over the first few tokens (the runner saves the top-10 first-token distribution). Refusal direction: take the difference of mean hidden states between harmful and harmless text-only prompts for this same model, then project conflict-case hidden states onto it layer by layer and compare with the text-only baseline and the clean-image control. Attention to image tokens: these models are decoder-only, so visual tokens enter through ordinary self-attention; earlier slides that said 'cross-attention' were inaccurate. We normalise by token count and exclude the first (sink) token.
Attention is correlational. For causal claims we add interventions: block attention to image tokens at chosen layers, swap activations between conflict and control runs (activation patching), and add or subtract the refusal direction.
JailBound-style probes are kept only as a check that the information is linearly accessible."""
N["models"] = """Qwen2-VL-2B-Instruct is the development model: small enough for one T4 or Apple MPS. Qwen2-VL-7B tests whether results change with scale. LLaVA-1.5-7B is a positive control because it is much more vulnerable.
The main risk is a floor effect. ADPO's Table 1 reports typographic-jailbreak ASR of 22.2% on LLaVA-1.5-7B but 4.5% on Qwen2-VL-7B; a 2B model may also have weak text-side refusal. Gate 0 therefore checks plain-text refusal rates first. If Qwen is robust to image instructions, that is itself a result, and LLaVA still provides contrast.
Claims will be limited to these model families; we will not generalise to 'post-trained VLMs' as a whole."""
N["pilot"] = """What exists: a v2 stimulus generator and runner, validated by a dry run (270 prompts, 55 images, all text fits). The runner saves raw responses and first-token distributions; it does not label them.
What does not exist: any model output. Nothing has been run, so no claim in this deck rests on our own data.
What was wrong in v1 and is fixed: instructions were clipped at large font sizes; no controls; a keyword classifier that mislabels transcription; a 'system' prompt placed in the user turn; absolute file paths.
Next step: Gate 0, which runs the TEXT arm and the benign typographic arm on Qwen2-VL-2B. The first run downloads about 4.5 GB of weights."""
N["roadmap"] = """Realistic plan: five to six weeks, not three. Week 1 Gate 0 and judge calibration; week 2 hierarchy-by-task factorial on Qwen2-VL-2B and LLaVA-1.5; week 3 visibility sweeps with the legibility covariate; week 4 mechanistic measurements and interventions; week 5 Qwen2-VL-7B replication and analysis; week 6 write-up.
Threats to validity are listed on the slide. The two I would lead with if asked: the judge (we mitigate with a rubric and human audit) and legibility (we measure it)."""
N["a_train"] = """Why the project does not train. The reason is scope (advisor's direction) and the research question (existing aligned models), not that training cannot work.
ADPO Table 1 on LLaVA-1.5-7B: VisualAdv ASR 64.5% to 5.0%, but LLaVABench 59.5 to 48.2 and OCRBench 202 to 184. The paper's own variant ADPO-CoT keeps LLaVABench at 57.7 and OCRBench at 191, so the cost is method-dependent. On Qwen2-VL-7B ADPO LLaVABench falls 88.0 to 74.2; ADPO-CoT recovers to 85.8.
SafeVLM Table 3: XSTest safe-pass rate 91.20% to 76.89% (more over-refusal). Table 4: MMBench 64.3 to 66.8 (68.5 with LoRA), SEEDBench 61.6 to 65.3, MME 1487.9 to 1479.5. So over-refusal is the real cost there, not general capability."""
N["a_figstep"] = """FigStep Fig. 2 shows the three steps: paraphrase the harmful question into a list opener, render it as typography, pair it with a benign 'incitement' text prompt. Fig. 5 is the t-SNE: plain text prompts separate benign from prohibited questions; the typographic prompts overlap."""
N["a_hades"] = """HADES Fig. 2 is the three-step pipeline: (1) move the harmful word to typography with a text-to-image pointer, (2) amplify with diffusion images refined by an attacker LLM, (3) amplify with gradient-based adversarial noise (white-box only)."""
N["a_vls"] = """Left: VLSBench Fig. 2 shows four existing benchmark items where the image content is already stated in the text (red). Right: MMJailBench Fig. 1 contrasts entangled benchmarks with a factorial design (272 x 6 x 5 x 2 = 16,320 per model)."""
N["a_mmjb"] = """MMJailBench Table 4: per-model ASR range induced by each factor (intent, prompt framing, visual semantics, carrier). Carrier sensitivity varies a lot between models. Fig. 5: attention to harm-related and visual tokens by layer on gemma3-12b in the authority-document and danger-image contexts."""
N["implications"] = """This slide answers the question 'so how does this make models safer?'. It does not claim that it does. The project diagnoses how alignment fails; it builds no defense, no benchmark and no training. The four rows say what each possible finding would be useful for if someone later builds an alignment method.
Where the refusal direction collapses (H3) would tell a future method which layers to act on. Which system-role levels fail (H2) would say what hierarchy-aware training data has to cover. First-token predictiveness (H3) would offer a cheap signal for monitoring or training. The visibility curve (H1) would say which image-text conditions to include in training and evaluation sets.
If asked about doing the alignment itself: that is a different proposal, it falls outside the advisor's constraints, and the alignment-training space is crowded and compute-heavy."""
