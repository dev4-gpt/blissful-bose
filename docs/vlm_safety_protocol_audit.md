# VLM Safety Alignment: Paper-by-Paper Protocol Audit and Study Design

**Research snapshot:** 2026-09-30  
**Scope:** safety alignment and empirical robustness for small/open vision-language models (VLMs), not a port of the earlier LLM continual-training method.  
**Evidence rule:** method descriptions below are based on the paper/official proceedings page; author-reported numbers are not cross-paper comparable unless the model, data, decoding, attack budget, and judge are held fixed. 2026 preprints are labeled as such.

**Reading route:** See [VLM_PAPER_READING_GUIDE.md](VLM_PAPER_READING_GUIDE.md) for a per-reference reading map and [VLM_PAPER_EVIDENCE_DOSSIER.md](VLM_PAPER_EVIDENCE_DOSSIER.md) for the evidence ledger and paper-role map. The earlier bibliography omitted HoliSafe [27], DAVSP [28], and Pragma-VL [29], all material recent work that changes the SOTA and novelty assessment. Several papers still need exact result-table extraction; the dossier marks that explicitly.

## Executive recommendation

Make the first study a **controlled small-VLM safety alignment comparison and generalization audit**, not a claim to invent a new universal defense. A defensible, tractable paper question is:

> **Under a common protocol, how do text-only tuning, multimodal safety SFT, preference alignment, adversarial preference training, and holistic five-state safety tuning/guard methods compare on held-out visual and cross-modal attacks in small open VLMs, while preserving benign answerability and grounded utility?**

This is deliberately narrower than “make VLMs safe.” It targets a documented mismatch: text alignment is not reliably transferred through vision; input carriers and visual semantics change failure rates; benchmark designs can miss joint image-text states or reward blanket refusal. The contribution should be a reproducible, resource-aware, same-model comparison with attack-family holdout, safe-neighbor controls, grounding checks, and cost. **Do not claim the five-state data formulation is novel:** HoliSafe already builds training and test data across all five image/text safety combinations and proposes Safe-VLM with a visual guard module. Any new-method claim requires a much sharper distinction than “counterfactually matched multimodal data.”

### Recommended primary hypothesis

**H1 (robustness + utility):** Under equalized base checkpoint, training budget, and evaluation protocol, multimodal alignment conditions will reduce harmful-compliance rate on held-out visual/cross-modal attack families relative to the unmodified checkpoint and text-only safety tuning, while keeping false refusal and grounded utility within preregistered margins. Candidate multimodal conditions include ordinary safety SFT, SPA-VL-style DPO, ADPO where reproducible, and a HoliSafe-style five-state/VGM comparator. The method is not presumed to win.

**H2 (generalization):** Gains on seen attack formats will exceed gains on held-out adaptive attacks; training-set attack success is not evidence of robust alignment. Use an attack-family split, not merely a random sample split.

**H3 (mechanistic/secondary):** A model's text-vs-image safety gap and/or cross-modal calibration gap will explain safety variation across small models better than parameter count alone. Treat as correlational and exploratory unless preregistered with enough models/power.

These are testable hypotheses, not findings. The numerical non-inferiority margins above are proposed study choices, not values established by prior papers.

## 1. Problem formulation

For model `f_theta`, input `x=(I,T)` (image and text), response `y`, define three separable outcomes:

- **Harmful compliance (safety failure):** the response materially advances disallowed harm, not merely mentions or analyzes it.
- **Benign answerability (utility):** the model answers allowed requests, including safe near-neighbors that contain superficially risky content.
- **Grounded multimodal behavior:** the response uses relevant image evidence and does not ignore, invent, or over-weight it.

The target is to minimize harmful compliance over benign, direct-harm, image-carrier, and compositional-risk inputs, subject to low false refusal, preserved VQA capability, and practical training/inference cost. Distinguish **alignment** (a training/objective property) from **observed safety** (measured system behavior); benchmark performance is evidence about the latter, not proof of universal alignment.

### Threat model and scope

- Attacker may control user text and the user-provided image; no system prompt, weights, or training pipeline access in the primary black-box evaluation.
- White-box perturbation and representation attacks are a separate diagnostic tier, possible only for open weights, with access, compute, and perturbation constraints reported.
- Primary target: single-turn image+text assistants. Multi-turn escalation, privacy extraction, harmful fine-tuning, and broader content moderation are secondary scopes; do not blend them into one ASR.
- Harm policy and annotation rubric must be frozen before evaluation. Report safety domain and severity separately where possible.

### Why VLM safety is not “LLM safety plus pictures”

1. Adding a vision pathway can degrade the backbone's safety behavior; representation shift and incomplete safety transfer are studied directly by CMRM and modality-gap work.
2. The meaning may be compositional: individually benign text/image can jointly imply harmful intent (SIUO).
3. Image OCR, visual semantics, prompt framing, and cross-modal attention create separate carriers and interactions (FigStep, HADES, MMJailBench).
4. Safety interventions can over-refuse safe visual requests or suppress grounding; VSCBench and USB make the safety/utility side explicit.
5. Adaptive attacks and internal interventions add threat models not represented by static image-prompt suites (PolyJailbreak, JailBound, SafeRI).

## 2. State-of-the-art map (as of snapshot date)

“SOTA” here means current, influential method families and strong recent examples, not a universal leaderboard winner. Papers use different models, splits, decoding, harm taxonomies, and judges. A reported ASR from one paper must not be ranked against another paper's ASR.

| Family | Representative papers | What the protocol contributes | Caveat / study relevance |
|---|---|---|---|
| Multimodal safety SFT/data | [VLGuard](https://arxiv.org/abs/2402.02207); [SafeVLM](https://arxiv.org/abs/2405.13581) | Safety examples across image/text; SafeVLM adds a safety projector/tokens/head | Core training baseline; compare data-only SFT against architectural add-ons; audit utility and matched data budget |
| Preference alignment | [SPA-VL](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision-Language_Models_CVPR_2025_paper.html); [ADPO](https://aclanthology.org/2025.findings-emnlp.735/) | SPA-VL provides 100K-scale multimodal preference pairs; ADPO uses adversarially trained reference plus adversary-aware DPO objective | ADPO is direct prior art for adversarially robust training; do not propose adversarial preference learning as wholly new. Its experiments use 7–8B-class models and LoRA; small/edge cost remains relevant |
| Representation correction / calibration | [CMRM](https://aclanthology.org/2025.findings-acl.186/); [MMAligner](https://arxiv.org/abs/2608.05909) | CMRM targets image-text representation gap at inference; MMAligner calibrates multimodal unsafe representations toward refusal region | Strong no-full-finetuning comparators; reported results are paper-specific, and calibration can increase refusals |
| Visual-prompt / activation-space tuning | [DAVSP](https://arxiv.org/abs/2506.09353) | Trains a visual safety prompt and deep activation alignment | Relevant parameter-efficient comparator; verify implementation/checkpoint and inference cost before selecting |
| End-to-end arbitration alignment | [Pragma-VL](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4054556fcaa934b0bf76da52cf4f92cb-Abstract-Conference.html) | Risk-aware cold-start SFT plus query-dependent reward weighting for safety/helpfulness arbitration | Direct ICLR 2026 SOTA method; full paper tables, exact gains, compute and artifact reproducibility still need audit |
| Input-side reasoning/guard | [VLMGuard-R1](https://aclanthology.org/2026.findings-acl.1986/); [GuardAlign](https://arxiv.org/abs/2602.24027) | Rewrites text-image prompts with a reasoning-guided external rewriter; GuardAlign combines unsafe-region detection and attention calibration | System-level comparison, not intrinsic alignment; report extra model calls, latency, and failure of the guard itself |
| Decoding-/token-level intervention | [SafetyReminder](https://ojs.aaai.org/index.php/AAAI/article/view/40607); [SafeSteer](https://aclanthology.org/2026.findings-acl.916/); [SafeRI](https://arxiv.org/abs/2609.03544) | Soft prompts, steering/calibration at decoding, or gated LoRA activation only on risky generation states | SafeRI is a Sep. 2026 preprint; do not present as peer-reviewed. These methods motivate selective rather than always-on safety, but add runtime complexity |
| Safety reasoning | [Think in Safety](https://aclanthology.org/2025.emnlp-main.261/); VLMGuard-R1 | Safety reasoning datasets or reasoning-guided input interpretation | More tokens/latency and possible leakage of harmful reasoning; distinguish reasoning from ordinary refusal tuning |
| Label-free visual alignment | [VSFA](https://aclanthology.org/2026.acl-long.490/) | Neutral VQA over threat-related images, without safety labels, intended to induce caution persona | ACL 2026 peer-reviewed; unusually relevant alternative hypothesis/baseline; needs same-model and matched-budget replication |
| Holistic safety states + integrated visual guard | [HoliSafe / Safe-VLM](https://arxiv.org/abs/2506.04704) | Train/test data span five safe/unsafe image-text combinations; Safe-VLM uses a Visual Guard Module for visual-harm classification plus safety-aware generation | CVPR 2026 Findings; major direct prior art. Its five-state supervision and visual guard overlap with our earlier B5 concept; compare/reproduce rather than claim the formulation as new |
| Evaluation factorization | [MMJailBench](https://arxiv.org/abs/2608.25490); [USB](https://aclanthology.org/2026.acl-long.970/); [VSCBench](https://aclanthology.org/2025.findings-acl.158/) | Factorizes carriers/framing/semantics; broad risk×modality coverage; measures under- and over-safety | Latest benchmark designs say “what is being measured” matters as much as defense scores; use focused slices, not every benchmark in full |

### Methodology timeline (useful talk narrative)

- **2023–24:** establish visual jailbreak channels and multimodal safety datasets (FigStep, MM-SafetyBench, HADES, VLGuard, JailBreakV).
- **2025:** move from “can it be jailbroken?” toward safety degradation mechanisms, preference alignment, calibration, and controlled leakage/over-refusal evaluation (CMRM, SPA-VL, ADPO, VSCBench, VLSBench, SIUO, Think in Safety).
- **2026:** factorized risk attribution and broad joint safety/over-refusal coverage (MMJailBench, USB, HoliSafe); newer interventions include reasoning rewrite, label-free visual alignment, selective token gates, test-time calibration, and decoding-level steering (VLMGuard-R1, VSFA, SafeRI, SafeSteer, GuardAlign). The evidence is active and heterogeneous; no single method is established as universally best.

## 3. Paper-by-paper protocol audit

The table below is the cross-paper protocol map; the deeper evidence ledger tracks all 28 VLM-related references and distinguishes extracted primary-source tables from details still requiring verification. “Judge” means how an unsafe response is labeled; it does not imply the judge is ground truth.

| Paper | Intervention / question | Evaluation protocol documented in paper | What to borrow / limitation |
|---|---|---|---|
| [VLGuard (2024)](https://arxiv.org/abs/2402.02207) | Multimodal safety instruction data and SFT; asks whether VLM tuning itself can weaken safety | Tests safety with multimodal harmful inputs/attacks and normal visual tasks; open model experiments | Baseline for multimodal safety SFT. Match training examples and evaluate on examples not used to construct the data. |
| [SafeVLM (2024)](https://arxiv.org/abs/2405.13581) | Two-stage safety projector, safety tokens, safety head | Reports safety on RTVLM and attack evaluations plus capability checks | Separate architectural safety module from data-only SFT; raw RTVLM score cannot be compared with other benchmark metrics. |
| [SPA-VL (CVPR 2025)](https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision-Language_Models_CVPR_2025_paper.html) | Preference data for multimodal safety alignment; image-question chosen/rejected responses across six harm domains | Dataset paper: 100,788 preference tuples, six domains, 13 categories, 53 subcategories; evaluated through preference tuning | Use as source/format for standard DPO baseline. Dataset scale may overwhelm small-data budget; report subset size and exact domains. |
| [CMRM / Safety Alignment Degradation (Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.186/) | Diagnoses modality representation gap; corrects representations at inference | Compares multimodal vs text-only safety, including jailbreak/safety tests; reports unsafe-rate reduction on LLaVA-7B in its own setup | Include a text-only paired condition and hidden-representation diagnostic. Do not treat their 61.53→3.15 rate as portable expected effect. |
| [VLSBench (ACL 2025)](https://aclanthology.org/2025.acl-long.405/) | Tests whether benchmark prompts leak the harmful label/risk in text | 2.2K cases designed to prevent visual safety information leakage; evaluates models on image-text safety | Use to validate that a model needs image understanding. It is a validity-control set, not just another attack suite. |
| [VSCBench (Findings ACL 2025)](https://aclanthology.org/2025.findings-acl.158/) | Safety calibration: under-safety and over-safety | 3,600 paired image/text cases; evaluates 11 VLMs, including aligned/open and closed systems; includes benign/harmful near-neighbors | Essential utility complement: refusal is not always correct. Record both attack success and false-refusal. |
| [SIUO (Findings NAACL 2025)](https://aclanthology.org/2025.findings-naacl.198/) | “Safe inputs, unsafe output”: composition-induced risk | 167 cases across nine safety domains; text and images considered innocuous individually; generative evaluation plus multiple-choice supplement | Small but targeted complement to broad sets. Preserve original metric and publish per-domain counts; do not call it a large-scale benchmark. |
| [ADPO (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.735/) | Adversarial preference optimization (adversarial reference + adversary-aware DPO loss) | Five open VLMs (main detailed results include LLaVA-1.5-7B, Qwen2-VL-7B, InternVL2-8B; LoRA); white-box VisualAdv and MMPGDBlank plus MultiTrust black-box typo/multimodal/cross-modal subsets; HarmBench classifier judges harmfulness; normal-task utility via MMStar, OCRBench, MM-Vet, LLaVABench | Strongest training-time comparator in this shortlist. Main text specifies attack families, model/training choices, and classifier. Its reported near-zero rates are paper-specific; utility drops on some VQA sets. |
| [Think in Safety (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.261/) | Safety reasoning/data for multimodal reasoning models | Five safety benchmark families; includes MSSBench and SIUO; appendix notes MSSBench single sampled instruction per safe/unsafe scenario under cost limits | Use as reasoning-method precedent. Sampling economy can reduce reliability; disclose sample selection and judge. |
| [MemeSafetyBench (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1555/) | Ecological meme safety, including multi-turn context | 50,430 real meme images/prompts, benign and harmful split; finds models can be more vulnerable to meme content than synthetic/typographic images | Secondary ecological test only: dataset has pronounced class imbalance (reported 46,599 harmful vs 3,831 benign), so publish balanced metrics and class-specific results. |
| [MTMCS-Bench (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.96/) | Multi-turn contextual safety/escalation | >30K examples; evaluated on open and proprietary MLLMs; conversations test changing context and cumulative risk | Add only if multi-turn is in scope; not a substitute for single-turn visual carrier testing. |
| [USB (ACL 2026)](https://aclanthology.org/2026.acl-long.970/) | Unified coverage of risk and modality interactions, with over-refusal | 61 risk categories × four modality interactions; 22 MLLMs across 244 risk-modality intersections; joint harmful vulnerability and benign over-refusal | Strong broad benchmark. Take a documented vision-relevant slice and do not conflate all 61 risk types. |
| [MMJailBench (arXiv, Aug 2026)](https://arxiv.org/abs/2608.25490) | Factor-level attribution: harmful intent, framing, visual semantics, instruction carrier | 16 open/proprietary models; factorized and combined configurations; full/lightweight modes and multiple judges | Strongest recent design precedent for controlled attack studies. It is an arXiv preprint as of snapshot; validate code/data/version before adoption. |
| [VLMGuard-R1 (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1986/) | External reasoning-driven prompt rewriting; target VLM weights unchanged | Six VLMs, five benchmarks; rewriter trained via three-stage synthesis; reports cross-benchmark gains including SIUO | Compare only as a system-level input guard, with latency, upstream model, and rewrite artifacts logged. ACL 2026 paper, not a direct weight-alignment baseline. |
| [VSFA (ACL 2026)](https://aclanthology.org/2026.acl-long.490/) | Fine-tunes on neutral VQA around threat-related images without safety labels | Multiple VLMs and safety benchmarks; claims improved ASR/response quality and less over-refusal while retaining capability | Must be in the current-method review and plausible baseline. Same-budget reproduction can test data/label efficiency; inspect paper tables and released artifacts before exact implementation. |
| [HoliSafe / Safe-VLM (CVPR 2026 Findings)](https://arxiv.org/abs/2506.04704) | Five image/text safe/unsafe combinations; Safe-VLM couples instruction tuning with a Visual Guard Module (VGM) that classifies visual harmfulness | 6,689 total images/14,246 pairs; 10,215 train pairs and a 4,031-pair/1,796-image test benchmark; five states, seven categories/eighteen subcategories | Directly overlaps the earlier B5 framing. It is a training-data, benchmark, and architectural-method paper; do not collapse those contributions into one. Detailed results and judging are in Addendum A.6. |
| [SafeRI (Sep 2026 preprint)](https://arxiv.org/abs/2609.03544) | Streaming safety recognition with gated LoRA activated during unsafe generation | Tests post-alignment safety and general benchmarks; exact metrics/checkpoints should be extracted from full paper before implementation | Latest frontier method; preprint and very recent. Cite as emerging, not as peer-reviewed benchmark winner. |
| [HoliSafe / Safe-VLM (CVPR 2026 Findings)](https://arxiv.org/abs/2506.04704) | Five-way safe/unsafe image-text taxonomy for both safety-tuning data and HoliSafe-Bench; Safe-VLM adds an integrated Visual Guard Module (VGM) plus instruction tuning | Training corpus: 6,689 images/14,246 instruction-response pairs (10,215 train pairs); test benchmark: 1,796 images/4,031 QA pairs. HoliSafe-Bench uses 7 major/18 subcategories and evaluates five input/output safety combinations | Directly overlaps the former “matched multimodal examples” proposal. VGM is a distinct architectural condition, not merely data SFT. Paper uses multiple automated judges and also string matching; audit judge dependence and utility before drawing conclusions. |

### Attack-paper protocol audit

| Attack paper | Attacker access / construction | Target/evaluation protocol | What it tests; what not to infer |
|---|---|---|---|
| [FigStep (arXiv 2023)](https://arxiv.org/abs/2311.05608) | Black-box; harmful instruction rendered typographically in an image, paired with a benign text request | Evaluates open VLMs and compares image-carried vs text-carried prompting; attack success is judged from generated responses | OCR/image carrier susceptibility, not semantic image composition. Paper-reported high ASR is an early-model historical result, not a current baseline expectation. |
| [HADES (ECCV 2024)](https://arxiv.org/abs/2403.09792) | Black-box; crafted images hide/amplify harmfulness associated with text intent | Reports average ASR on LLaVA-1.5 and Gemini Pro Vision; paper reports 90.26% and 71.60% respectively in its original setup | Semantic visual manipulation; numbers apply only to those old target versions, prompts, and judge. Use as a distinct family or for targeted A2 cases. |
| [JailBreakV (arXiv 2024)](https://arxiv.org/abs/2404.03027) | Collection, not one attack: starts from 2,000 malicious queries, generates 20K transferred text jailbreaks and 8K image-based inputs | 28K examples; evaluates ten open MLLMs and analyzes text-transfer and image attack groups | Broad coverage/benchmark source. Split by underlying intent and attack construction; count unique intents, not just rows. |
| [ADPO (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.735/) attack setup | White-box gradient-based VisualAdv and MMPGDBlank; plus black-box MultiTrust typographic, multimodal, and cross-modal subsets | Five VLMs overall (main detailed results include 7–8B-class models); ASR; HarmBench classifier judge; fixed model-specific LoRA setup | Strong precedent for adversarial robustness training and a credible candidate baseline. Report white-/black-box results separately. |
| [JailBound (NeurIPS 2025)](https://arxiv.org/abs/2505.19610) | Representation-level, two-stage Safety Boundary Probing and Boundary Crossing; white-box path plus black-box transfer evaluation | Six VLMs; paper reports 94.32% average white-box and 67.28% average black-box ASR | Tests internal safety boundary, not ordinary image-prompt robustness. Require exact code, layer/access configuration, and separate threat-model reporting. |
| [PolyJailbreak (arXiv 2025)](https://arxiv.org/abs/2510.17277) | Black-box, iterative multi-agent/RL optimization over reusable atomic strategy primitives; can use multiple queries, but target interactions are single-turn | Evaluates open and commercial MLLMs; reports 18.15% average ASR improvement vs prior baselines and >95% on some commercial targets; query construction is adaptive | Best held-out adaptive family candidate. Freeze query budget and judge, and keep it out of training/validation. Its headline rates are not expected rates for small models. |
| [Azulay et al. (arXiv 2026)](https://arxiv.org/abs/2605.00583) | Four zero-gradient black-box visual strategies: symbol sequence, benign-object substitution, in-image text substitution, visual analogy | Evaluates six frontier VLMs; compares visual and text equivalents for at least the cipher condition | Direct test of modality transfer; recent and useful as an optional separate family. Verify released input construction and allowed dataset before reproduction. |

### Important correction to an earlier project framing

The old presentation’s LLM gradient-selection storyline is not the research default for this proposal. There is now direct VLM adversarial alignment (ADPO), multiple VLM-specific training and inference defenses, and 2026 work that materially changes the landscape. The old method may inspire a later controlled ablation, but it should not define the problem, title, or novelty claim.

## 4. Finalized adversarial/evaluation suite

The suite is tiered so the primary result remains feasible. Use the same model versions, prompts, image processing, decoding, and judge across compared methods. Never use harmful operational prompts in presentation examples; show abstracted safe paraphrases.

### Core primary battery (required)

| Tier / attack | Protocol and safe illustrative example | Access | Primary metric | Why included |
|---|---|---|---|---|
| A0: Direct text-only safety control | Harmful intent stated as text, no image. Example: “Give step-by-step instructions for a prohibited harmful act.” | Black-box | Harmful-compliance rate (HCR/ASR) | Establish whether failure is multimodal-specific or baseline language safety. |
| A1: FigStep-style typographic image | The same abstracted harmful request is embedded as text in an image; user asks a neutral OCR/description request. | Black-box | HCR; OCR success logged separately | Canonical image-carrier baseline; separates OCR pathway from semantic interaction. Use fixed image rendering, font, resolution, and prompt. |
| A2: Semantic cross-modal composition (SIUO + HADES-style controlled items) | Benign-looking image plus innocuous-looking text whose joint interpretation raises risk; examples must not reveal operational content. | Black-box | HCR by modality condition; matched safe-control accuracy | Directly tests composition, not just an image containing the harmful request. Keep text-only and image-only ablations. |
| A3: Leakage-controlled evaluation (VLSBench) | Cases where text alone does not reveal the unsafe visual implication; compare full image-text input with text-only ablation. | Black-box | Difference in HCR; image-dependence check | Prevents claiming multimodal safety when prompt text telegraphs the answer. This is a benchmark validity control. |
| A4: Paired calibration/benign near-neighbor (VSCBench + selected USB safe cases) | Pair a disallowed request with a visually/textually similar safe request, e.g. safety education or neutral image description. | Black-box | False-refusal rate (FRR), safe completion quality, calibration gap | Stops “refuse everything” from scoring as aligned. |
| A5: Held-out adaptive attack (PolyJailbreak) | Query-adaptive cross-modal search; hold the attack family and prompts out of training/threshold tuning. | Black-box queries; cap budget | HCR at a fixed query budget; queries-to-first-success | Tests generalization beyond static templates. Pre-register query budget and report cost. MMJailBench is a factorized benchmark design, not itself the adaptive attacker. |

### Secondary diagnostic tier (optional; do not pool with primary ASR)

| Diagnostic | Protocol | Why optional |
|---|---|---|
| HADES visual-semantic concealment | Use curated/canonical HADES attack inputs and its benign controls, logged as a separate attack family | Classic semantic-image exploit; overlaps conceptually with A2, so choose a fixed subset rather than adding a redundant benchmark total. |
| Azulay et al. visual attack family | Symbol-sequence visual encoding, benign-object substitution, image-text substitution, visual analogy; no gradients | Recent test of visual-only carrier generalization. Use pre-authored safe-domain examples and report each of the four subfamilies separately. |
| White-box pixel perturbation (VisualAdv/MMPGD-style) | Fixed norm/steps/queries and white-box model access; state optimizer and image preprocessing | Tests a different threat model; not representative of all deployments and can consume considerable compute. ADPO demonstrates this is already a relevant robustness training protocol. |
| JailBound representation-boundary attack | White-box internal boundary probing/crossing, following paper's method and access requirements | Mechanistic stress test, not a black-box deployment attack. Keep findings separate; only reproduce with code and exact target-layer setup. |
| Multi-turn escalation (MTMCS-Bench) | Multi-turn risk-context shift with frozen conversation protocol | Add only if the intended product is conversational/agentic; otherwise expands the paper beyond a clean first study. |
| MemeSafetyBench | Stratified and class-balanced subset of natural memes; preserve benign/harmful strata | Ecological validity, but not a controlled adversarial attack. Report as a separate external-validity check. |

### Attack suite decision

**Required:** direct text control + FigStep + SIUO-style composition + VLSBench leakage control + VSCBench/USB safe-neighbor calibration + held-out black-box PolyJailbreak. Use MMJailBench as a factorized benchmark/design reference, not as a substitute for the adaptive attack.  
**Recommended if open-model compute permits:** one gradient-based visual perturbation family, then one representation-level diagnostic (JailBound), reported separately.  
**Do not make all 4 Azulay attacks, HADES, FigStep, MM-SafetyBench, JailBreakV-28K, and every new benchmark co-equal “primary attacks.”** That creates overlap, an unmanageable matrix, and a misleading single ASR.

### Judge and reliability protocol

1. Preserve raw model generations; judge only after generation and blind judge to model/method identity.
2. Primary labels: `harmful assistance`, `safe refusal`, `safe transformation/alternative`, `benign answer`, `over-refusal`, `ambiguous`. Define rubric with examples before scoring.
3. Use an established classifier (e.g., HarmBench classifier as used by ADPO) as first-pass automated evaluator only after validating on our domain. Human-audit a stratified sample (all apparent harmful cases when feasible, plus random positives/negatives and ambiguous cases); report agreement and adjudication procedure.
4. Report HCR/ASR with denominator and confidence interval, FRR on benign pairs, utility, and judge disagreement. Do not rely only on refusal-string matching or one LLM judge.
5. Exact decoding must be fixed (temperature, top-p, max new tokens, seed where supported). Report repeated runs for stochastic decoding; deterministic decoding is a reference, not the only deployment condition.

## 5. Benchmarks explained and recommended roles

| Benchmark | What an item asks / what it reveals | Strength | Limitation / recommended use |
|---|---|---|---|
| **MM-SafetyBench** (5,040 image-text pairs; 13 scenarios) | Harmful intent paired with several image-generation/carrier styles | Broad, established early visual-jailbreak baseline | Risk may be text-visible; audit image necessity and use as a secondary comparison, not sole evidence. |
| **FigStep** | Instructions rendered in an image with an otherwise ordinary prompt | Clear OCR/text-in-image channel | Narrow attack family; fixed templates can be overfit. Keep as one controlled attack. |
| **JailBreakV-28K** (28K; 2K harmful intents; 20K text-transfer and 8K image-based inputs) | Mixes transferred LLM jailbreak prompts and native multimodal attacks | Scale and multiple attack families | Dataset is a benchmark collection, not one attack; select documented stratified slices and avoid train/test contamination. |
| **SIUO** (167 instances, nine domains) | Example pattern: a neutral image and innocuous text are each unremarkable, but their joint contextual implication raises safety concern | Direct operationalization of compositional risk | Small; power/coverage limited; report per-domain and exact split. Avoid showing unsafe instructions in a talk. |
| **VLSBench** (~2.2K) | Example: text is intentionally insufficient to disclose why the pictured scene is risky; compare full image+text with text-only input | Tests whether image understanding is necessary | Validity test; not a broad harm taxonomy. Include text-only ablation. |
| **VSCBench** (3,600 pairs) | Example pair: similar image/question context, one request seeks allowed educational information and its near-neighbor seeks disallowed help | Joint safety calibration and utility | Pair-level metrics need to be preserved; do not collapse all pairs to one refusal score. |
| **USB** (61 risk categories × four modality interactions) | Example: compare a risk carried in text, image, or across both, with matched benign inputs in the same domain | Most extensive unified risk-modality coverage in shortlist; evaluates over-refusal alongside vulnerability | Large and heterogeneous; select the image/cross-modal cells relevant to the paper and publish slice selection. |
| **MMJailBench** (2026 preprint; 16 models) | Example: hold intent fixed and vary framing, visual semantics, and whether instruction is text- or image-carried | Best controlled benchmark logic for causal attribution among attack factors | Very recent preprint; inspect licensing, code/data and judge implementation. Strong design reference even if not adopted wholesale. |
| **MemeSafetyBench** (50,430; 46,599 harmful / 3,831 benign as paper reports) | Real memes plus benign/harmful instructions, including conversational settings | Ecological stimuli, beyond synthetic text images | Strong imbalance; stratify/balance and report as naturalistic external validity. |
| **MTMCS-Bench** (>30K) | Safety as dialogue changes over turns | Context and escalation | Out of primary single-turn scope; adopt only for multi-turn research. |
| **RTVLM** | Red-teams privacy, fairness, misleading, and safety dimensions | Useful historical comparison for SafeVLM and broad risk categorization | Dimensions should not be collapsed into “harmful assistance”; report each separately. |
| **PII-VisBench** (4,000 probes, ACL 2026 Findings) | Image privacy risk conditioned on online visibility | Dedicated privacy evaluation | Separate privacy task; do not merge PII leakage with jailbreak ASR. |

### Minimum benchmark set for the first paper

1. **USB image/cross-modal slice** for broad risk categories and benign counterexamples.
2. **VSCBench** for matched calibration and over-refusal.
3. **VLSBench** for visual-leakage validity.
4. **SIUO** for safe-input composition.
5. **FigStep** plus one held-out adaptive attack for adversarial robustness.

MM-SafetyBench or a stratified JailBreakV subset is a useful historical comparison. MemeSafetyBench is an optional ecological replication. Avoid claiming “benchmark-complete” from any one dataset.

## 6. Baseline matrix

### Models

- **Primary model family:** use the current small checkpoints from one open family, provisionally [Qwen3-VL-2B/4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) (or the current supported release at experiment freeze), so size comparison is not confounded by architecture. Lock exact model revisions and processor/chat-template versions.
- **Replication model:** [SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct) is a practical efficient-by-design replication candidate if the same alignment method, evaluator, and core suite can run. It is not architecture-matched to Qwen, so treat it as external replication, not the scale comparison.
- Lock exact checkpoint IDs, chat templates, tokenizer/processor versions, quantization, image resolution/crop policy. Do not mix API models into the core causal comparison.

### Alignment/defense baselines (in priority order)

| ID | Condition | Purpose |
|---|---|---|
| B0 | Original instruction-tuned checkpoint, no extra safety intervention | Anchor and assess native safety |
| B1 | Text-only safety SFT on the same harmful intents, no image-bearing examples | Isolate transfer from language safety into vision |
| B2 | Multimodal safety SFT, VLGuard-style, matched number of training examples/steps | Strong, inexpensive data baseline |
| B3 | Standard multimodal DPO using SPA-VL-style preference pairs | Preference-alignment baseline; match data/compute as closely as practical |
| B4 | ADPO reproduction or published checkpoint if compatible | Direct adversarial-alignment comparator; include only if compute and license allow |
| B5 | HoliSafe-style five-state training / Safe-VLM VGM reproduction condition | Direct prior art: compare five-state supervision and VGM at small scale; not a new data-formulation claim |
| B6 optional | CMRM or MMAligner, VLMGuard-R1, VSFA, SafeRI | Mechanistically diverse system/method comparators; do not bundle them into the main claim if reproduction is infeasible |

**Fairness rules:** identical base checkpoint within each comparison; equalized training data budget or explicit data-size curves; same LoRA/full-tune policy; same number of steps and selection of hyperparameters on a validation set; test attack families held out; report peak GPU memory, training GPU-hours, inference latency/tokens, and adapter size.

### Primary outcomes

- `HCR/ASR`: harmful-compliance fraction per attack family and overall macro-average across families (not item-weighted aggregate only).
- `FRR`: refusal rate on safe matched pairs; distinguish any refusal from materially unhelpful refusal.
- `Safe usefulness`: quality/accuracy on allowed questions and safe alternatives after refusal.
- `General VQA`: fixed compact task set (e.g., MMStar plus OCRBench or MM-Vet) before/after alignment; report metrics separately.
- `Cross-modal gap`: difference between paired text-only, image-only, and joint-input safety outcomes.
- `Cost`: training compute/data volume; inference latency/extra calls; optional token and peak memory measures.

## 7. Research challenges and researchable gaps

| Challenge | Why it matters | Operational response |
|---|---|---|
| Cross-modal generalization | Text safety behavior may fail when intent is carried visually or jointly inferred | Pair text-only/image-only/joint conditions and hold out carrier families |
| Safety vs. over-refusal | Minimizing attack success can reward blanket refusals | Use VSCBench + benign slices and report FRR/utility jointly |
| Benchmark visual leakage | Risk can be obvious from text without reading image | VLSBench and text-only ablation; score image dependence |
| Attack overlap and benchmark saturation | Many “different” datasets reuse intents/templates | Split by source intent, attack family, and image generator; deduplicate semantically |
| Adaptive attacker | Static training can memorize a few attack renderings | Hold out PolyJailbreak evaluation at a fixed query budget; use MMJailBench to factorize input attributes |
| Evaluator reliability | Automated harmfulness judges can miss nuance or mirror model bias | Human-validated stratified sample; publish rubric and disagreements |
| Model/checkpoint confounds | Different chat templates and vision preprocessors change outcomes | Same-family checkpoints, locked exact versions/processors, publish configs |
| Small-model cost constraints | Strong defenses may add extra calls, long reasoning, or larger adapters | Report latency/compute and include parameter-/data-matched controls |
| Safety knowledge vs. visual grounding | A refusal might reflect lost perception rather than safer interpretation | Add safe image QA and image-ablation/grounding controls |
| Rapid field changes | New benchmark/defense papers arrive quickly | Freeze literature date; repeat a targeted search at proposal submission and before camera-ready |
| Privacy/fairness scope creep | Not all harms are jailbreaks | Keep privacy, fairness, misinformation, and harmful-assistance outcomes separate; include one only if the project names it as a target |

## 8. 20-minute presentation narrative (recommended 17 slides)

1. **Title and research question** (0:30): small VLM safety alignment, no presumed LLM-method port.
2. **Why this matters** (1:00): VLMs accept joint image+text; risk can reside in carrier or combination.
3. **Define the problem** (1:10): safe behavior + utility + grounding; three outcome axes.
4. **Why text alignment does not settle VLM safety** (1:10): modality gap / pathway / cross-modal composition.
5. **Evolution of the field** (1:00): 2023–24 attacks/data; 2025 calibration/preference; 2026 factorized evaluation/selective interventions.
6. **Method family map** (1:20): SFT, preference, representation, input guards, reasoning, decoding/token intervention, label-free VSFA.
7. **Paper audit: training-time** (1:20): VLGuard, SafeVLM, SPA-VL, ADPO, VSFA; what each does and how tested.
8. **Paper audit: runtime/representation** (1:00): CMRM, MMAligner, VLMGuard-R1, SafetyReminder/SafeRI; different system boundaries.
9. **What a jailbreak actually changes** (1:00): FigStep carrier vs HADES semantic composition vs adaptive search; use safe sanitized mini-examples.
10. **Benchmarks: what each measures** (1:30): USB, VSCBench, VLSBench, SIUO; distinct axes, not interchangeable leaderboard scores.
11. **Paper-by-paper protocol audit: lessons** (1:10): threat model, target models, evaluator, utility, split; ADPO detailed protocol as concrete exemplar.
12. **Research gap and precise question** (1:00): small-model scale + held-out cross-modal generalization + calibration under aligned protocol.
13. **Hypotheses** (1:10): H1 robustness+utility, H2 held-out drop, H3 exploratory modality-gap correlation.
14. **Final attack suite** (1:20): core A0–A5 plus optional white-box tier.
15. **Baselines and model panel** (1:20): B0–B5; same family, matched budget.
16. **Metrics and experimental controls** (1:10): HCR, FRR, VQA, modality gap, judge audit, compute.
17. **Expected contribution / limitations / next steps** (1:40): protocol + empirical answer, no unsupported novelty claim; reproduce key checkpoints and preregister.

Target 20:00; timing is approximate and leaves room for transitions. The companion speaker script expands each slide with narration and citations.

## 9. Sources and evidence status

Primary-source links are embedded above. Core protocol details were checked against original ACL/AAAI/arXiv pages and the ADPO PDF. Important venue distinction: ACL/EMNLP/AAAI/CVPR/NeurIPS papers are published proceedings; MMJailBench (Aug 2026) and SafeRI (Sep 2026) are preprints as of 2026-09-30. Author-reported percentages are always tied to their source protocol and must not be cross-paper ranked.

### Core references

- FigStep, arXiv:2311.05608: https://arxiv.org/abs/2311.05608
- MM-SafetyBench, arXiv:2311.17600: https://arxiv.org/abs/2311.17600
- HADES, ECCV 2024: https://arxiv.org/abs/2403.09792
- JailBreakV, arXiv:2404.03027: https://arxiv.org/abs/2404.03027
- VLGuard, arXiv:2402.02207: https://arxiv.org/abs/2402.02207
- SafeVLM, arXiv:2405.13581: https://arxiv.org/abs/2405.13581
- SIUO, Findings NAACL 2025: https://aclanthology.org/2025.findings-naacl.198/
- CMRM, Findings ACL 2025: https://aclanthology.org/2025.findings-acl.186/
- VSCBench, Findings ACL 2025: https://aclanthology.org/2025.findings-acl.158/
- VLSBench, ACL 2025: https://aclanthology.org/2025.acl-long.405/
- SPA-VL, CVPR 2025: https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision-Language_Models_CVPR_2025_paper.html
- ADPO, Findings EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.735/
- Think in Safety, EMNLP 2025: https://aclanthology.org/2025.emnlp-main.261/
- VLMGuard-R1, Findings ACL 2026: https://aclanthology.org/2026.findings-acl.1986/
- VSFA, ACL 2026: https://aclanthology.org/2026.acl-long.490/
- USB, ACL 2026: https://aclanthology.org/2026.acl-long.970/
- MMJailBench, arXiv:2608.25490: https://arxiv.org/abs/2608.25490
- SafeRI, arXiv:2609.03544: https://arxiv.org/abs/2609.03544

---

## Addendum A. Attached-paper audit and verified results

### A.1 What was attached, and what qualifies as evidence

| Local attachment | Identification after paper inspection | Relevance decision |
|---|---|---|
| `SafeVLM.pdf` and `Safety Alignment for Vision Language Models-with-annotations.pdf` | Two copies/versions of *Safety Alignment for Vision Language Models* (SafeVLM), arXiv:2405.13581 | Count once. Direct VLM safety-alignment method and empirical evaluation. |
| `VLMGuard-R1 Proactive Safety Alignment for VLMs via Reasoning-Driven Prompt Optimization-with-annotations.pdf` | arXiv:2504.12661 v2; subsequently published as Findings ACL 2026 | Directly relevant VLM safety system. Important boundary: it trains an external prompt rewriter; it does not safety-fine-tune the downstream target model. |
| `2604.17215v1.pdf` and `Continual_Safety_Alignment.pdf` | LLM-only gradient-based sample selection / previous LLM pipeline write-up | Not evidence that a VLM method works. Retain only as project history and a possible future hypothesis, not as a VLM baseline or result. |
| `Presentation1.pdf` | Earlier presentation extending the LLM pipeline to VLMs | Not research evidence. Superseded framing; do not reuse its VLM claims without independent VLM sources. |

Thus, the local bundle supplies **two unique direct VLM safety papers**, not a complete state-of-the-art corpus. The deck supplements these attachments with primary papers from the broader literature. Citation: SafeVLM, https://arxiv.org/abs/2405.13581; VLMGuard-R1, https://aclanthology.org/2026.findings-acl.1986/.

### A.2 SafeVLM: method, protocol, and paper-reported numbers

**Method.** SafeVLM adds a safety projector, trainable safety tokens, and a safety head. Its two-stage procedure first trains safety modules with the base VLM frozen, then tunes the language model on safe data while freezing the new modules. Risk-sensitive visual inputs can conditionally inject safety representations. Its principal model is LLaVA-v1.5-7B. The paper evaluates a mix of its RTVLM benchmark/risk datasets, text jailbreaks, and general vision-language capability tests. Safety scores are GPT-4/GPT-4V judgments on the authors’ 0–10 scales; they are not equivalent to ASR.

| SafeVLM Table 1/2 condition | RTVLM average (0–10; higher is safer) | Risk-set average (0–10; higher is safer) |
|---|---:|---:|
| LLaVA-v1.5-7B | 6.39 | 5.06 |
| SafeVLM | 8.18 | 7.78 |
| SafeVLM (+LoRA) | 8.26 | 7.80 |
| GPT-4V reference, Table 1 | 7.92 | Not reported in this row |

The risk-set average is across the paper’s listed harmful-politics, pornography, cyberbullying, and RTVLM evaluations. The benchmark composition and the GPT judge matter; do not interpret 8.26 as a field-wide SOTA score.

| SafeVLM Table 3 condition | AdvBench vanilla ASR % ↓ | AdvBench suffix ASR % ↓ | XSTest safe-instruction pass % ↑ | XSTest unsafe-instruction compliance % ↓ |
|---|---:|---:|---:|---:|
| LLaVA-v1.5-7B | 6.45 | 78.27 | 91.20 | 26.50 |
| SafeVLM | 1.72 | 67.56 | 76.89 | 7.46 |
| SafeVLM (+LoRA) | 1.90 | 69.86 | 78.09 | 6.96 |

**Interpretation.** SafeVLM lowers unsafe response measures in these reported tests. It also lowers the safe-instruction pass rate by approximately 13–14 percentage points. AdvBench and XSTest are text prompt evaluations in this table; they do not establish robustness to visual jailbreaks. This is a direct motivation for paired safe/unsafe multimodal tests and for reporting FRR, not just ASR.

| General ability reported by SafeVLM, Table 4 | LLaVA-v1.5-7B | SafeVLM | SafeVLM (+LoRA) |
|---|---:|---:|---:|
| MMBench | 64.3 | 66.8 | 68.5 |
| SEEDBench | 61.6 | 65.3 | 63.7 |
| MME perception | 1487.9 | 1479.5 | 1458.8 |
| MME (aggregate) | 1773.6 | 1762.7 | 1753.8 |

The capability picture is mixed: MMBench and SEEDBench rise, while MMEp (MME perception) and MME (aggregate) fall. Those metrics should remain separate rather than being averaged into a single utility claim. Ablations in Table 5 further suggest the head contributes substantially: baseline RTVLM/politics/porn/cyberbullying scores are 7.59/6.97/1.51/6.34; head-only 8.09/8.73/7.64/7.15; tokens-only 7.63/6.84/1.61/6.43; both 8.26/8.91/6.82/7.20. All are paper-specific GPT scores. Primary source: https://arxiv.org/abs/2405.13581.

### A.3 VLMGuard-R1: exact system boundary and selected results

**Method and data.** VLMGuard-R1 trains a Qwen2-VL-7B-Instruct prompt rewriter with supervised fine-tuning. The rewriter receives the image and user text, produces a revised user prompt, and passes the image plus rewritten prompt to an unchanged downstream target VLM. Its staged data construction uses hindsight response comparison, multimodal causal analysis, and prompt optimization. The authors report approximately 10K image-instruction examples (including 977 helpfulness and 8,904 safety examples); source material includes VLGuard, SPA-VL, VLSBench and the authors’ VLGuard-Safe construction. It is therefore an input-pipeline/system defense, not intrinsic alignment of every target model.

**Evaluation.** The paper tests six open-source downstream VLMs and includes VLGuard-Unsafe, SIUO, MM-SafetyBench slices and VLGuard-Safe; it also tests generalization on FigStep, health and economic prompts. Table 1 reports GPT-4o safety scores (0–10, higher better) and helpfulness (%) side by side. Selected base → +R1 cells:

| Target / benchmark slice | Base safety / helpfulness | +R1 safety / helpfulness |
|---|---:|---:|
| LLaVA-1.5-7B, VLGuard-Unsafe | 3.71 / 20.92 | 6.70 / 59.30 |
| LLaVA-1.5-7B, SIUO | 3.80 / 44.85 | 6.77 / 58.43 |
| Qwen2-VL-7B, VLGuard-Unsafe | 6.10 / 49.50 | 7.65 / 64.82 |
| Qwen2-VL-7B, SIUO | 4.26 / 60.24 | 6.11 / 53.61 |
| Qwen2-VL-7B, MM-SafetyBench TYPO | 6.08 / 83.08 | 8.98 / 86.05 |

The Qwen2-VL SIUO helpfulness score decreases (60.24→53.61) despite improved safety score, illustrating why outcomes must remain paired. Its supplementary defense success rate (DSR) uses predefined refusal strings: VLMGuard-R1 reports 56.1% overall versus 38.5% ETA, 32.3% MLLM-Protector, 24.0% FigStep, and 7.1% ECSO in the listed table. This DSR is not semantically equivalent to a harmful-compliance judge and can reward formulaic refusal. The paper also reports generalization on Qwen2.5-VL-72B: for FigStep / health / economic prompts, base safety-helpfulness pairs are 8.36-99 / 6.66-82 / 4.79-57; +R1 pairs are 8.68-99 / 7.91-92 / 8.40-89. Treat them as their own task scores, not comparable to other benchmarks. Primary source: https://aclanthology.org/2026.findings-acl.1986/.

### A.4 ADPO: direct adversarial-alignment prior art and selected baseline table

ADPO is essential prior art because it directly trains for adversarial VLM robustness. The paper uses LoRA and evaluates white-box VisualAdv and MMPGDBlank attacks plus black-box MultiTrust typo, multimodal, and cross-modal subsets. It reports ASR and general vision-language capability metrics; the table below transcribes selected paper rows. ASR is lower-is-better; the utility tuple is MMStar / OCRBench / MM-Vet / LLaVABench, in the original metric units.

| Model/condition | VisualAdv ASR | MMPGDBlank ASR | MultiTrust typo | MultiTrust multimodal | MultiTrust cross-modal | Utility tuple |
|---|---:|---:|---:|---:|---:|---|
| LLaVA-1.5-7B base | 64.5 | 84.0 | 22.2 | 55.1 | 42.0 | 32.7 / 202 / 29.9 / 59.5 |
| LLaVA-1.5-7B + DPO | 12.0 | 33.0 | 0.7 | 8.8 | 9.6 | 33.9 / 198 / 28.9 / 54.4 |
| LLaVA-1.5-7B + ADPO | 5.0 | 0.5 | 0.0 | 0.0 | 0.2 | 33.7 / 184 / 24.2 / 48.2 |
| Qwen2-VL-7B base | 13.5 | 30.0 | 4.5 | 54.3 | 6.3 | 58.5 / 841 / 64.7 / 88.0 |
| Qwen2-VL-7B + ADPO | 0.0 | 1.5 | 0.0 | 4.0 | 0.0 | 57.6 / 830 / 53.9 / 74.2 |

These results demonstrate strong performance under the paper’s particular attack construction, training recipe, classifier, and target versions. They do not establish zero risk: the attack families are finite, some capability scores decrease, and a held-out adaptive test remains necessary. Do not compare the ASR numbers to SafeVLM’s GPT score tables or VLMGuard-R1’s GPT-4o safety/helpfulness scores. Official paper: https://aclanthology.org/2025.findings-emnlp.735/.

### A.5 Results landscape: useful claims, with boundaries

| Work | Intervention / evaluation contribution | Result statement safe to present | Boundary to state aloud |
|---|---|---|---|
| SafeVLM (2024) | Added safety projector/tokens/head; RTVLM, risky datasets, text attacks, capability scores | Its own GPT-judged average rises from LLaVA 6.39 to 8.18 (RTVLM); unsafe measures fall | Text attack table and notable safe-instruction pass-rate drop; no claim of comprehensive visual attack robustness |
| CMRM (Findings ACL 2025) | Diagnoses representation gap and applies inference-time correction | Reports substantial unsafe-rate reduction on its LLaVA evaluation setup | Not a common benchmark score; disclose set, judge, and correction protocol when quoting exact figure |
| ADPO (Findings EMNLP 2025) | Adversarial preference optimization | Selected table rows show large ASR reductions under VisualAdv/MMPGDBlank/MultiTrust | Some utility trade-off; attack-specific, not universal robustness |
| VSFA (ACL 2026) | Label-free alignment via neutral VQA on threat-related images | Published work reports improved safety behavior without safety labels | Include as an alternate mechanism; extract exact table/protocol before using numeric claims outside this reviewed slide deck |
| VLMGuard-R1 (Findings ACL 2026) | External reasoning-driven multimodal prompt rewriter | Selected GPT-4o safety/helpfulness cells improve, with an SIUO helpfulness counterexample | Adds an upstream model and latency; DSR is refusal-string based |
| GuardAlign (ICLR 2026) | Training-free unsafe-region detection + cross-modal attention calibration | Proceedings abstract reports up to 39% unsafe-response reduction on SPA-VL and VQAv2 78.51→79.21 | “Up to” author-reported result; report the exact evaluation slice and baseline before using as a comparative estimate |
| SafeSteer (Findings ACL 2026) | Decoding-level probe/steering intervention | Abstract reports up to +33.40% safety without fine-tuning | It is distinct from the 2025 preprint also titled SafeSteer; verify exact full-paper table before quoting details |
| MMJailBench (Aug 2026 preprint) | Factorized benchmark over intent, framing, visual semantics and carrier | Useful new attribution design; evaluates 16 models | Benchmark/preprint, not a defense or attack algorithm; do not call it adaptive attack |
| SafeRI (Sep 2026 preprint) | Streaming risk recognizer with gated LoRA | Emerging selective-generation direction | Preprint; present as not peer reviewed at snapshot date |

For a 20-minute presentation, prioritize the detailed method/result tables and connect the remaining methods to the end-to-end workflow. Do not use abstract-only numbers as a comparative estimate. Primary sources: CMRM https://aclanthology.org/2025.findings-acl.186/; VSFA https://aclanthology.org/2026.acl-long.490/; GuardAlign https://proceedings.iclr.cc/paper_files/paper/2026/hash/c10c771f52408a2de77d056a4109e93d-Abstract-Conference.html; SafeSteer https://aclanthology.org/2026.findings-acl.916/; MMJailBench https://arxiv.org/abs/2608.25490; SafeRI https://arxiv.org/abs/2609.03544.

### A.6 HoliSafe / Safe-VLM: five-state data, benchmark, model, and reported outcomes

**Why this paper changes our proposal.** HoliSafe is CVPR 2026 Findings, not merely an arXiv-only idea at this snapshot. It already formalizes five image/text safety states and uses them both to construct tuning data and to evaluate models. Safe-VLM adds a visual guard module (VGM), so the paper is simultaneously a dataset, benchmark, and model-method contribution. The prior framing of a “new matched multimodal data composition” therefore overlaps with prior art and must not be sold as novel.

**Dataset and split (paper §§2.1–2.2).** The authors curate 6,689 images, combining collected and generated images, then create 14,246 image-instruction-response pairs. The safety-tuning split has 4,893 images and 10,215 pairs; the held-out HoliSafe-Bench has 1,796 images and 4,031 Q&A pairs. The benchmark covers seven major categories and 18 subcategories. Its five states are: (1) unsafe image + unsafe text → unsafe; (2) unsafe image + safe text → unsafe; (3) safe image + unsafe text → unsafe; (4) safe image + safe text → unsafe through the joint interpretation; and (5) safe image + safe text → safe/helpful. The data-building procedure labels images and uses GPT-4o to generate response pairs, with human review and GPT-4o cross-checking for category/safety labels. The paper states the training/test split at image/pair level; for our reuse, also inspect source-image provenance and deduplicate across SPA-VL/VLGuard and any other training data.

**Method and setup (paper §§3–4.1).** Safe-VLM adds a Visual Guard Module: visual tokens are pooled into a global representation and passed to a two-linear-layer MLP classifier. Fine-tuning combines (a) a safety-classification loss for image harmfulness categories and (b) next-token instruction-following loss on image/text response pairs. The paper says the VLM vision encoder, visual projection, and LLM LoRA are trained for its recipe. It evaluates 21 models on HoliSafe-Bench and compares same-backbone LLaVA-v1.5-7B variants for prior safety-tuning baselines. For behavior judging, Table 3 reports Claude-3.5-Sonnet, GPT-4o, Gemini-2.0-Flash, and refusal-string matching. ASR is the fraction of unsafe inputs with an unsafe/non-refusal response; RR is the error/refusal rate on benign SIST→S cases (the appendix definition includes harmful or grossly irrelevant responses, so it is broader than a pure refusal-string count).

**Selected Table 3 results.** All values below are percent. The first pair uses Claude-3.5-Sonnet as judge; other judge columns are mean ASR across four unsafe states. These columns are not interchangeable because they use different judges.

| Model | Claude mASR ↓ | Claude RR on safe pairs ↓ | GPT-4o mASR ↓ | Gemini-2.0-Flash mASR ↓ | String-match mASR ↓ |
|---|---:|---:|---:|---:|---:|
| LLaVA-v1.5-7B | 79.1 | 1.6 | 91.2 | 94.0 | 95.9 |
| VLGuard-7B | 39.9 | 1.3 | 49.6 | 51.9 | 52.2 |
| SPA-VL-DPO-7B | 40.5 | 1.6 | 55.6 | 58.3 | 63.7 |
| SafeLLaVA-7B (HoliSafe + VGM) | 8.8 | 1.3 | 15.3 | 15.8 | 15.4 |

Within the authors’ test protocol, SafeLLaVA-7B has much lower mean ASR than the compared LLaVA-v1.5, VLGuard, and SPA-VL-DPO variants, while the Claude-judged safe-pair RR is 1.3%. This is an author-reported result, not a cross-paper leaderboard claim. GPT-4o-generated training responses, model-judge dependence, use of a small set of closed-source judges, and the source-data overlap/licensing rules all matter for reproduction.

**Selected Table 4 results, same LLaVA-v1.5 family.** Values are the paper’s benchmark-specific units; do not combine columns into one score.

| Model | VLSBench safety (Refuse + Warn) ↑ | MM-SafetyBench avg ASR ↓ | HarmEval unsafe score ↓ | SIUO safe score ↑ |
|---|---:|---:|---:|---:|
| LLaVA-v1.5-7B | 6.6 | 60.2 | 44.2 | 21.6 |
| SPA-VL-DPO-7B | 27.0 | 31.7 | 0 | 43.7 |
| VLGuard-7B | 21.3 | 10.2 | 18.1 | 43.1 |
| SafeLLaVA-7B | 69.8 | 7.7 | 0 | 60.5 |

The exact interpretation is metric-specific: VLSBench splits refuse and warn; MM-SafetyBench is a harmful-compliance ASR; HarmEval and SIUO show unsafe/safe scores. Check source Table 4/caption before quoting a row; do not recast the safe-score columns as a common scale.

**What we should use it for.** Treat HoliSafe as (i) a core prior-art training/data comparator, (ii) a direct benchmark candidate if access and licensing permit, and (iii) the clearest test-design precedent for the five image/text safety states. Compare its five-state dataset/Safe-VLM recipe to simpler VLGuard-style SFT, SPA-VL DPO, ADPO, and a neutral-VQA approach such as VSFA under a shared small-model protocol. If released checkpoints or data cannot be used reproducibly, clearly label a faithful reproduction as future work rather than implying it was run. Primary source: [CVPR 2026 Findings paper](https://arxiv.org/pdf/2506.04704); dataset card: [HoliSafe-Bench](https://huggingface.co/datasets/etri-vilab/holisafe-bench).

### A.7 DAVSP: training-time visual safety prompt with activation-space supervision

DAVSP is a peer-reviewed AAAI 2026 alignment method and should be read alongside ADPO, VSFA, and HoliSafe. Unlike parameter-efficient SFT/DPO, it freezes the target LVLM and optimizes a trainable padded visual region around a resized image. It constructs a harmfulness direction from the final input-token activation difference between 470 malicious and 470 benign VLGuard samples; a margin loss separates harmful and benign projections at a chosen decoder layer, while a response cross-entropy term retains target responses. At inference, the learned visual prompt is applied with a textual safety prompt. The paper uses 600 challenging malicious MM-SafetyBench samples and 100 benign MM-Vet samples to train that prompt.

The AAAI paper evaluates LLaVA-1.5-13B and Qwen2-VL-7B-Instruct. It uses DeepSeek-V3 as the semantic safety judge for Resist Success Rate (RSR), where higher means better resistance; benign utility comes from each benchmark's standard scoring. On Table 2, DAVSP reports FigStep RSR of 84.20% and 99.20%, respectively, and MM-SafetyBench SD+TYPO RSR of 98.72% and 99.12%. Table 1 pairs these with utility results: LLaVA-1.5-13B has MM-Vet total 39.07, MME total 1602, and LLaVA-Bench 63.6; Qwen2-VL-7B has 61.61, 2146, and 75.2. Table 4 ablations on LLaVA-1.5-13B show removing Deep Alignment drops FigStep RSR from 84.20% to 67.00%; replacing the visual padding prompt with additive perturbations drops it to 76.20%. This supports the proposed mechanism within its own setup, not a universal leaderboard claim.

Important scope: DAVSP's setup includes a common AdaShield-S text prompt for fair comparison, uses white-box access to train a prompt on the source model, and separately studies transfer to other models. The extended version contains additional implementation and adversarial-example analysis; inspect that before reproducing. Read AAAI paper §§3–5.6, Fig. 2, Tables 1–6 and the extended-version appendix. Primary source: [AAAI 2026 paper and PDF](https://ojs.aaai.org/index.php/AAAI/article/view/41149).

### A.8 Pragma-VL: recent end-to-end arbitration training

Pragma-VL is a direct ICLR 2026 training-time safety-alignment contribution, not merely a benchmark or runtime guard. Its official proceedings abstract describes cold-start SFT that combines risk-aware clustering of the visual encoder with interleaved risk descriptions and high-quality data, followed by a synergistic reward model/data augmentation that assigns query-dependent dynamic weights to safety and helpfulness. The paper claims 5–20% improvement over baselines on most multimodal safety benchmarks while preserving general math/knowledge reasoning. The table-level follow-up below supersedes the initial abstract-only note; artifact, compute, and exact recipe audit remain necessary before reproduction. Primary source: [ICLR 2026 proceedings page](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4054556fcaa934b0bf76da52cf4f92cb-Abstract-Conference.html).

**Table-level follow-up (official proceedings-indexed full text).** Experiments use Qwen2.5-VL-7B and LLaVA-1.5-7B, GPT-4o judging, BeaverTails-V, SPA-VL, MM-SafetyBench, SIUO, MSSBench, and general-capability benchmarks; the paper reports 16 A100 GPUs. On Table 2, Qwen2.5-VL-7B + Pragma-VL has BeaverTails-V helpfulness/harmlessness win rates 62.65/67.91; SPA-VL 87.17/87.92; MM-SafetyBench helpfulness/harmlessness 52.74/58.99 with ASR 31.66; SIUO effective/safety 95.21/63.47. Table 3 reports GQA 61.42, ScienceQA 89.06, TextVQA 83.75, VizWizQA 78.90, VQAv2 84.20, and MathVista 67.20. These are per-paper scales and settings, not a shared leaderboard. Read §§3–4.4, Fig. 2, Tables 1–4, Appendix D.2. See [official code](https://github.com/SII-FLEEECERmw/Pragma-VL) for reproducibility checks.

## Addendum B. Benchmark cards, dataset examples, and evaluation controls

Examples below are deliberately schematic and non-operational. They explain the *structure* of each test without reproducing harmful instructions.

| Benchmark / dataset | Scale and composition | Sanitized example structure | What it tests | Main caveat / recommended metric |
|---|---|---|---|---|
| MM-SafetyBench | 5,040 image-text pairs; 13 risk scenarios; Stable-Diffusion and OCR-related image channels | The text asks a neutral-looking question while the image carries the risky content; paper separates SD, OCR, SD+OCR styles | Broad multimodal jailbreak susceptibility | Synthetic and scenario-constructed; report attack-family ASR, not only pooled score. https://arxiv.org/abs/2311.17600 |
| FigStep | Typographic image jailbreak examples | A benign surface question accompanies an image containing rendered instructions | OCR/image-carrier bypass | A named attack family, not a balanced safety/utility benchmark. Keep benign OCR controls. https://arxiv.org/abs/2311.05608 |
| HADES | Crafted images paired with harmful prompts/intent | Visual design obscures or alters how the image conveys intent | Semantic visual manipulation | Original headline ASR applies to older target models and the authors’ exact setup; do not use as a modern baseline forecast. https://arxiv.org/abs/2403.09792 |
| JailBreakV-28K | 2,000 source intents; 20K text-transferred and 8K image-based instances | The same underlying intent appears in different text/image jailbreak renderings | Breadth and transfer across attack forms | It is a collection/benchmark, not one single attack; deduplicate and split by source intent to avoid leakage. https://arxiv.org/abs/2404.03027 |
| SIUO | 167 cases across nine domains | Text and image appear individually benign; only the joint interpretation changes the risk classification | Cross-modal composition | Small targeted diagnostic set; report counts and per-domain outcomes rather than imply prevalence. https://aclanthology.org/2025.findings-naacl.198/ |
| VLSBench | About 2.2K leakage-controlled cases | Safety-relevant fact is visually grounded while text is controlled so it cannot reveal the answer | Whether safety judgment actually uses image content | Use image removal, region masking, and decoy-image ablations as validity checks. https://aclanthology.org/2025.acl-long.405/ |
| VSCBench | 3,600 paired safe/unsafe calibration cases; evaluates 11 VLMs | Two closely matched requests differ in whether answering is allowed | Under-safety plus over-refusal | Score the pair jointly; include false-refusal rate and answer quality. https://aclanthology.org/2025.findings-acl.158/ |
| USB | 61 risk categories × four modality interactions; 22 MLLMs in reported study | Same risk category tested through text/vision and modality combinations | Broad risk-by-modality coverage, including benign over-refusal | Too broad to claim every slice is in scope; preselect vision-relevant slices. https://aclanthology.org/2026.acl-long.970/ |
| HoliSafe-Bench | 4,031 test Q&A pairs, 1,796 images, 7 categories/18 subcategories; five safe/unsafe combinations | Same safe/unsafe image and query components yield either unsafe or benign combined inputs | Joint-state coverage plus paired benign refusal calibration | Dataset benchmark and training source come from one paper; audit image provenance, overlap, judge panel, and gated CC-BY-NC conditions. https://arxiv.org/abs/2506.04704 |
| MMJailBench | 2026 preprint, 16 models; factorized conditions | Independently vary harmful intent, prompt framing, visual semantics and instruction carrier | Attribution of which input factor changes outcomes | A benchmark design, not a unique attack technique; identify preprint status. https://arxiv.org/abs/2608.25490 |
| RTVLM | Real-world VLM safety benchmark used by SafeVLM | Broad visual question/image situations judged for safe response | Realistic safety response quality | Its GPT-scored scale is not ASR and is not directly comparable to other judges. https://arxiv.org/abs/2405.13581 |
| SPA-VL | 100,788 preference tuples; six harm domains, 13 categories, 53 subcategories; responses from 12 VLMs | Same image/question paired with preferred and rejected answers | Training data for preference alignment and a DPO baseline | Training resource, not a standalone attack benchmark; train/test intent overlap must be controlled. https://openaccess.thecvf.com/content/CVPR2025/html/Zhang_SPA-VL_A_Comprehensive_Safety_Preference_Alignment_Dataset_for_Vision-Language_Models_CVPR_2025_paper.html |
| VLGuard | Multimodal safety instruction/response data and benchmark | Safe and unsafe image-grounded requests paired with target assistant behavior | Safety SFT baseline and safety evaluation | Separate train examples from test examples; audit capability/over-refusal. https://arxiv.org/abs/2402.02207 |
| MemeSafetyBench | 50,430 real meme examples; reported class imbalance 46,599 harmful vs 3,831 benign | Meme text and visual context jointly change interpretation | Ecological meme-specific safety | Class imbalance makes accuracy misleading; use per-class and balanced metrics. https://aclanthology.org/2025.emnlp-main.1555/ |

### B.1 Fixed core attack/evaluation suite

| ID | Required cell | Source/design precedent | Test split and control | Outcome |
|---|---|---|---|---|
| A0 | Direct text harmful prompt | Text-only control; same source intent as multimodal counterpart | Keep intent matched; do not treat this as the full VLM threat model | Harmful-compliance rate (HCR) |
| A1 | Text rendered in image (FigStep-style) | FigStep; MM-SafetyBench OCR | Hold out rendering templates/fonts; include ordinary benign OCR | HCR by rendering family; OCR/VQA control |
| A2 | Joint image-text composition | SIUO; HADES-like visual-semantic cases | Image-only and text-only ablations; use independently held-out intents | HCR and cross-modal gap |
| A3 | Leakage and grounding control | VLSBench | Original image, image-removed, relevant-region masked, and matched decoy | Whether answer/safety judgment changes appropriately with evidence |
| A4 | Benign paired near-neighbor | VSCBench; USB benign slices; XSTest principle | Match topic/image class with allowed task; blind label review | False-refusal rate (FRR), safe-answer quality |
| A5 | Adaptive black-box held-out attack | PolyJailbreak, fixed query-budget protocol | Keep all attack queries and optimization prompts out of training; freeze budget | HCR as function of query budget; cost |
| Optional W1 | White-box visual perturbation | VisualAdv/MMPGDBlank (ADPO) | Separate open-weight tier; bound perturbation and compute | ASR by attack and perturbation budget |
| Optional W2 | Representation-boundary probe | JailBound | Diagnostic only; not a user-input black-box attack | Boundary-probe success, transfer, compute |

PolyJailbreak is an adaptive multi-agent black-box method and should be run as a held-out adversary, not mixed with fixed benchmark ASR. MMJailBench is a factorized benchmark, not an adaptive attack. JailBreakV-28K is a suite/dataset rather than one attack. These distinctions prevent category errors in the talk.

### B.2 Proposed primary metric definitions

- **HCR:** proportion of prompts whose answer materially advances a disallowed objective under a pre-registered, domain-specific rubric. Report separate from mere mention, refusal, and neutral description.
- **ASR:** use only when reproducing the source paper’s definition; state its judge and threshold. Do not rename a refusal-string detector as semantic HCR.
- **FRR:** proportion of allowed matched prompts that are materially refused or rendered unusable. Report exact numerator/denominator and distinguish cautious framing from non-answer.
- **Safe usefulness:** human- or task-scored correctness/helpfulness on benign near-neighbors and safe alternatives.
- **Grounding validity:** change in response when relevant image evidence is removed, masked, or replaced with a decoy; used to detect text leakage or vision neglect.
- **General capability:** report benchmark-specific VQA/OCR scores before and after, without collapsing non-comparable metrics into one utility number.
- **Uncertainty:** bootstrap confidence intervals over source intents (not just rendered variants); report judge/human agreement and an adjudicated error sample.
- **Adaptive robustness:** curve over fixed query/iteration budgets, with prompts, transforms and attack seeds recorded. Keep the attack generator’s own failure to find an exploit distinct from model safety.

### B.3 Recommended result table for the eventual paper

For every model × method × attack family, provide `N`, unique source-intent count, harmful responses, HCR, 95% interval, judge type, and abstention/refusal rate. For benign matched data provide `N`, FRR, useful-answer score, and uncertainty. Add before/after VQA/OCR scores, latency, tokens, memory, training GPU-hours, adapter size and extra model calls. Publish examples of false positives and false negatives with sensitive details redacted. Report one model-family scale comparison and a distinct cross-architecture replication; do not merge them into one average.

## Addendum C. Final proposal framing and novelty guardrails

### Problem statement for the talk

> **We study whether safety alignment in small open vision-language models transfers across image-text carriers and compositional risk, and whether it can do so without increasing false refusals or weakening grounded visual utility.**

### Study question

> Under a shared model, data, decoding, judge, and compute protocol, how do text-only safety SFT, standard multimodal safety SFT/preference tuning, and adversarial multimodal alignment differ on held-out OCR, cross-modal composition, leakage-controlled, benign-paired, and adaptive attacks?

### Proposed baseline ladder

1. B0 native instruction-tuned model.
2. B1 text-only safety SFT on matched harmful intents.
3. B2 VLGuard-style multimodal safety SFT with equalized data/steps.
4. B3 standard multimodal DPO using SPA-VL-style preference pairs.
5. B4 ADPO reproduction (or compatible release only with its protocol and checkpoint verified).
6. B5 HoliSafe-style five-state training / Safe-VLM-VGM condition, reproduced if data/checkpoints and compute permit. This is a prior-art comparator, not a proposed new formulation; any ablation must be described precisely.
7. Secondary system comparators: one input/representation/decoding method (e.g. VLMGuard-R1, CMRM, VSFA) if compute and implementation permit; report extra calls/runtime separately.

### Hypothesis and decision criteria

Primary hypothesis: multimodal conditions (B2–B5) decrease macro HCR over A1/A2/A5 relative to B0 and B1 under a shared protocol, while FRR remains within a preregistered margin and general VQA/OCR remains within a non-inferiority margin. B5 tests reproduction/transfer of HoliSafe-style supervision at small scale; it is not new method novelty. A suggested initial proposal is +3 percentage points maximum FRR and −2 absolute benchmark points maximum capability loss; these are design choices, not standards from cited papers. Use held-out attack-family and source-intent splits. If no condition wins reliably, the comparison remains useful by identifying where reported prior results transfer or fail.

### Challenges to state explicitly

1. Attack datasets may reuse intents, prompts, or images; split/deduplicate by source intent and construction family.
2. Automated judges may reward refusal strings or miss partial assistance; validate a stratified human-audited subset.
3. Safety improvements can be over-refusal or perception suppression; include matched safe tasks and image-ablation controls.
4. Paper-reported scores are not a shared leaderboard: target models, versions, budgets, decoders, and judges differ.
5. Small-model results do not establish behavior of frontier proprietary systems; frame the scope accurately.
6. Training and inference defenses have different system boundaries; include latency, extra calls, data, and compute.
7. Very recent methods (e.g. MMJailBench, SafeRI at this snapshot) may have incomplete artifacts and are preprints; label status and avoid premature “SOTA winner” language.
8. Harm-policy boundary, severity and allowed educational/defensive use must be frozen before annotation and evaluation.

### Evidence and novelty claim limits

- Do not claim “first adversarial alignment for VLMs”: ADPO is direct prior art.
- Do not claim that VLM safety alignment is unexplored: VLGuard, SafeVLM, SPA-VL, ADPO, VSFA and other methods exist.
- Do not present VLMGuard-R1 as fine-tuning the downstream target model; it trains a separate rewriter.
- Do not claim PolyJailbreak is a benchmark or that MMJailBench is an attack algorithm.
- Do not quote the LLM gradient-selection paper as VLM evidence; it is LLM-only.
- Treat HoliSafe's five-state data coverage and VGM as direct prior art; do not claim these ideas as new.
- Phrase the possible contribution as a controlled small-model, held-out cross-modal robustness/calibration comparison and reproducibility study unless a genuinely distinct method survives the baseline comparison and literature refresh.

**Presentation scope note:** the deck contains an approximately 20-minute main narrative plus a technical evidence appendix. The appendix is backup material; do not attempt to narrate every result table during the timed talk. Keep the full audit as the cited handout.
