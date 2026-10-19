# Verified literature scope and paper positioning

Updated 2026-10-18 after checking primary sources against the actual v1–v6 aggregates. Companion: `docs/STATUS_AND_PAPER_PLAN.md` (plain-language explanation, model shortlist, regenerated results and execution plan).

## 1. Corrections that change our positioning

**The earlier claim that FigStep lacked an all-text control was wrong.** Q2-prime includes the image content and inciting instruction, with an adapted referent. We must frame our use as replication on different checkpoints/metrics. [FigStep v3, Section 6.4, Table 2](https://arxiv.org/html/2311.05608v3#S6.SS4).

**Comprehension adjustment is also prior art.** Wang et al.'s MMJailBench defines conditional attack success after excluding instruction mismatch, in addition to its factorized design. Report our refusal-specific sensitivity analysis as an adaptation. [MMJailBench, Sections 3, 4.2 and 5.2](https://arxiv.org/html/2608.25490v1).

**Our label-based stability claim needed correction.** The Qwen2 v3/v5 gap is 43.1 points with Qwen3Guard versus 52.0 with WildGuard. V6 labels use a revised context/rule. The direction is persistent, but effect magnitude is measurement-dependent; cached versions are not independent replications. Source: the regenerated cross-version table in the companion document.

## 2. Search scope and limits

This is a **focused scoping review, not a completed systematic review**. Searches included arXiv, ACL Anthology and Semantic Scholar indexed pages, using combinations of typographic/image jailbreak, text control, prompt framing, refusal, prediction, image-token presence, and multimodal safety evaluation. Semantic Scholar searches returned substantial unrelated material; absence of a useful hit is not evidence of novelty. Primary papers and official model cards were opened directly. Methods/results sections were inspected where indicated below; appendices were not uniformly audited. No unverified secondary source is a paper citation.

The requested Gemini deep-research skill was read. Its `scripts/research.py` runner and GEMINI_API_KEY configuration were missing; no paid Gemini research was started. Older `research_notes/` files remain leads rather than evidence.

For a submission-grade systematic search, still record exact query strings, dates, inclusion/exclusion decisions, forward/backward citation screening and a complete source matrix. In particular, “forecastability not found” is a research lead, not a novelty finding. Do not label T1 complete.

## 3. Primary-source evidence register

“Focused full-text” means selected relevant methods/results, not an assertion that every appendix was read. Sizes and scores below are included only where directly visible in the specified source; they are not comparable to our results without matching tasks, model IDs, decoding and scoring.

| Source and checked identity | Reading depth / location | Relevance and implication |
| --- | --- | --- |
| Gong et al., **FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts**, [2311.05608v3](https://arxiv.org/html/2311.05608v3) | Focused full-text: Sections 5–6, especially 6.4, Table 2 | All-text Q2-prime already exists. Our modern replication must acknowledge it and explain any differing observations |
| Xin Liu et al., **MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal Large Language Models**, [2311.17600v5](https://arxiv.org/html/2311.17600v5) | Focused full-text: construction, evaluation tables and ablations | Separates text-only, generated-image, typography and combined conditions. Our TYPO subset is not the entire benchmark or a full replication of published ASR |
| Tianshi Wang et al., **MMJailBench: A Factorized Benchmark for Disentangling Multimodal Jailbreak Vulnerabilities**, [2608.25490v1](https://arxiv.org/html/2608.25490v1) | Focused full-text: Sections 3–5, Tables 1–3 | Six framings, five semantics, two carriers; 16 models. Framing dominates; text/OCR differences are model-dependent. CASR already handles mismatch. Very close prior work |
| Qin Liu et al., **Unraveling and Mitigating Safety Alignment Degradation of Vision-Language Models**, [2410.09047v1](https://arxiv.org/html/2410.09047v1) | Focused full-text: input variants, Table 1, CMRM method | Blank/noise/caption/query controls and inference-time representation intervention predate us. Presence effects and basic steering are not new |
| Wenhan Yang et al., **Bootstrapping LLM Robustness for VLM Safety via Reducing the Pretraining Modality Gap**, [2505.24208v1](https://arxiv.org/html/2505.24208v1) | Abstract plus focused introduction/method framing | Explicitly discusses blank/irrelevant-image degradation and pretraining gap reduction. Its training intervention is outside our no-training scope |
| Xuhao Hu et al., **VLSBench: Unveiling Visual Leakage in Multimodal Safety**, [2411.19939v3](https://arxiv.org/html/2411.19939v3) | Focused full-text: Section 2, Table 1, construction/results | Already audits text-only safety shortcuts in existing benchmarks. Its visual-information leakage differs from our prompt-wrapper comparison. Do not claim all benchmark audits are new |
| Baolin Zheng et al., **USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models**, [2505.23793](https://arxiv.org/abs/2505.23793) | Abstract-only | Joint vulnerability/oversensitivity evaluation and risk/modality coverage are established motivations |
| Youngwan Lee et al., **HoliSafe: Holistic Safety Benchmarking and Modeling for Vision-Language Model**, [2506.04704](https://arxiv.org/abs/2506.04704), [author project](https://youngwanlee.github.io/holisafe/) | Abstract and author project methodology/results | Safe/unsafe image-text combinations, multi-judge evaluation and safety–utility analyses. Our typographic controls do not cover this full interaction space |
| Kaixuan Ren, Preslav Nakov, Usman Naseem, **DUAL-Bench: Measuring Over-Refusal and Robustness in Vision-Language Models**, [2510.10846](https://arxiv.org/abs/2510.10846) | Abstract-only | Safe completion and visual over-refusal are explicit prior concerns. A refusal-only leaderboard is inadequate |
| Gabriel Downer et al., **Text2VLM: Adapting Text-Only Datasets to Evaluate Alignment Training in Visual Language Models**, [2507.20704](https://arxiv.org/abs/2507.20704) | Abstract-only | Typographic adaptation of text datasets and human checks already exist. More datasets alone do not create a distinct contribution |
| Moreno D'Incà, Nicu Sebe, Massimiliano Mancini, **Harnessing Textual Refusal Directions for Multimodal Safety**, [2606.31876v2](https://arxiv.org/html/2606.31876v2) | Abstract and focused introduction | MARS transfers textual refusal directions and adjusts alignment/strength/layer. Basic transfer steering is a crowded contribution |
| Tianqi Xiao et al., **Transfer Safety Awareness for Cross-Modal Safety Drift in Multimodal Large Language Models**, [2609.02082v2](https://arxiv.org/html/2609.02082v2) | Abstract; full text opened but detailed method not audited | SRT transfers safety-awareness representations. Treat as an important mechanism/mitigation comparator; do not infer details from its title |
| Ravikumar Balakrishnan, Sanket Mendapara, Ankit Garg, **Reading Between the Pixels: Linking Text-Image Embedding Alignment to Typographic Attack Success on Vision-Language Models**, [2604.12371v2](https://arxiv.org/html/2604.12371v2) | Focused full-text: font results, Tables 1–6, limitations | Text/image attacks and font/transformation sensitivity on Qwen3-VL and other models; embedding-based prediction is prior work. Distinguish that from held-out text-twin prediction |
| Alexandra Souly et al., **A StrongREJECT for Empty Jailbreaks**, [2402.10260](https://arxiv.org/abs/2402.10260), [author repository](https://github.com/alexandrasouly/strongreject) | Abstract and author evaluation description | Useful harmful information and human agreement matter beyond refusal. The authors provide an open evaluator; applicability to our actual multimodal stimuli must be validated |
| Paul Röttger et al., **XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models**, [2308.01263](https://arxiv.org/abs/2308.01263), [author repository](https://github.com/paul-rottger/xstest) | Abstract and author data/evaluation instructions | Benign over-refusal control. Text-only XSTest does not independently establish visual helpfulness |

Version warning: the VLSBench v3 full text reports 2,241 pairs, while earlier/abstract metadata describes 2.4k. Do not mix version-specific dataset sizes. Similarly, do not reuse rounded abstract scores from Reading Between the Pixels in a result table when the underlying full-text table uses different precision or qualifiers.

## 4. Revised novelty assessment

| Idea | Assessment | Role in our paper |
| --- | --- | --- |
| Add a wrapper-matched text twin | **Known control**: FigStep Q2-prime; broader factorization in MMJailBench | Replicate and test explanatory limits across generations; no invention claim |
| Any-image presence harms refusal | **Known phenomenon**: CMRM and modality-gap work | Diagnostic control and checkpoint-specific boundary condition |
| Text-to-image refusal coupling / see-saw | **Unestablished novelty**; related transfer/shared-representation work is extensive | Secondary observational evidence; no causal or universal claim |
| Predict image refusal from text twin on held-out architectures | **Potential incremental contribution; novelty unestablished** | Retain as a falsifiable endpoint, compare mean/B-only baselines and report failures |
| Image-token dose/order | **Partly known context; exact incremental value unresolved** | Secondary diagnostic; actual token variation and supported ordering are prerequisites |
| Capability-adjusted refusal | **Known general principle**, explicit mismatch-conditioned ASR in MMJailBench | Measurement sensitivity, not a new metric claim; acknowledge selection bias |
| Font-size/readability controls | **Known** | Validity control; separate reading and answer generation |
| Images increase refusal under strong wording | **Our checkpoint-specific exploratory observation**, not established novelty | Replicate on fresh items; report harm and reading beside refusal |
| Refusal stability across sampling | **Standard robustness question; novelty unestablished** | Secondary distribution/uncertainty analysis, not headline |
| Human validation and non-answer distinctions | **Known need**, with potential value in this specific audit | Quantify whether corrections materially alter effects/rankings; do not claim first human-validated evaluation |
| Refusal-direction steering | **Known**, multiple close methods | Supporting historical result or omit from the core paper |

## 5. Recommended contribution package

1. **Replication across model generations and two original benchmarks.** Establish whether the matched text control explains comparable fractions of the apparent gap, with exact model/revision/settings and clear benchmark limits.
2. **A consequential measurement audit.** Demonstrate which label errors change the scientific interpretation, using blinded human labels, population weights, separate refusal and harm, and uncertainty. Merely reporting judge kappa is insufficient.
3. **A bounded prediction result if it works.** Test the predeclared held-out architecture forecast. Negative R-squared, failed folds and lack of improvement over the mean baseline are reportable results, not reasons to swap endpoints.

The best title direction is a question about when the image matters. Avoid “first”, “universal”, “we disentangle all multimodal safety”, “vision causes misalignment”, or “no trade-offs exist”. If modern models reproduce the original residual visual effect, that is still an informative boundary condition. If measurement corrections erase apparent differences, that may be the strongest result. Do not choose the paper's conclusion before the confirmatory evidence.

## 6. Additional benchmarks: useful later, not automatically in v7

MM-SafetyBench TYPO and FigStep directly address the typographic question. XSTest is a benign control, not a third attack benchmark. If the paper makes broader claims, a separately approved semantic-vision benchmark such as VLSBench/HoliSafe can test the boundary where text transcription cannot preserve visual meaning. DUAL-Bench is relevant for visual safe-completion/over-refusal. USB offers wider coverage but adds a different evaluation scope.

Do not flatten these datasets into a single pooled ASR. Their harmfulness definitions, benign subsets and required visual context differ. Check data licenses, original IDs, judged stimuli, and the suitability of text-only guards before adding any. Current Amendment 5 authorizes only the two attack benchmarks and its benign controls; further datasets require an addendum.

## 7. Work remaining before a defensible novelty claim

- Full methods/appendix review for abstract-only entries and careful comparison of FigStep's exact Q2-prime with our E construction.
- Citation-chain screening around factorized evaluations, text/OCR comparisons, safety prediction and non-answer scoring; document exclusions and search strings.
- Verify whether any recent work already performs held-out architecture prediction from text controls. Current search did not establish absence.
- Decide with the advisor whether the replication plus measurement correction is sufficiently substantial for the intended venue.
- Keep the approved analysis-plan hash unchanged. Correct positioning now; preregister any experiment/design additions before new outcomes.

## 8. Expanded methodology review, later October 18

Read [METHODOLOGY_REVIEW_AND_UPGRADE_PLAN.md](METHODOLOGY_REVIEW_AND_UPGRADE_PLAN.md) for the expanded 25-source matrix, exact query log, actual v7 code/design audit and ranked alternatives. This remains a scoping review: selected methods/results were inspected, and abstract-only sources are explicitly marked. T1's exhaustive screening and full-appendix audit are not complete.

The later review inspected USB construction/annotation, HoliSafe's image-aware evaluation protocol, DUAL-Bench's label/perturbation design, Text2VLM's relevance/understanding definitions, and SRT's supervised direction refinement. In particular, a frozen backbone does not make SRT a no-optimization method; its full implementation does not fit our current no-training scope. SafeCoDe (2509.19212v2) is a possible inference comparator, but its judge and verdict-dependent generation limits require cost and length controls. These are literature conclusions, not new results from our models.

The most promising additional methodology is a design-weighted human measurement study informed by prediction-powered inference, with a human-only baseline and honest small-stratum uncertainty. This is an established statistical family, not a novelty claim. A separate CPU prototype and synthetic explanatory notebook are prepared; they are not wired into approved v7 inference, do not read private caches, and cannot produce human-validated results without human labels and a verified sampling design. Any scientific adoption needs an approved addendum.

## 9. Additional planning search, October 18

The expanded review now has 29 sources. Newly checked close comparators are [Li and Liu, EviSafe, 2608.23313v1, §§3.1–3.5](https://arxiv.org/html/2608.23313v1), [Helbling et al., SafetyPairs, 2510.21120v1, §§3–4.2](https://arxiv.org/html/2510.21120v1), and [Xu et al., A²Safe, 2609.24098v1, §§III-A–III-B](https://arxiv.org/html/2609.24098v1). Evidence/counterfactual evaluation and pair-level errors are established; A²Safe's optimized adapters/router exclude its full method from our no-training scope. These were focused method reads, not exhaustive appendix audits.

[Methodology review section 8](METHODOLOGY_REVIEW_AND_UPGRADE_PLAN.md#8-extended-research-plan-requested-by-the-owner--proposals-not-approval) proposes paired response transitions, transparent scoring sensitivity and missing-output bounds, followed optionally by a small layout-consistency diagnostic and simulated audit allocation. These are established analytical principles adapted to our question, with incremental value still unestablished. It includes planned-call arithmetic and an end-to-end sequence; it does not alter approved Amendment 5 or authorize new runs. The review also checks Simonsohn, Simmons and Nelson's 2020 specification-curve paper through the author PDF; our proposed descriptive display does not adopt its joint statistical test.

## 10. October 19 decision: evaluate the limits of text-led safety testing

The review is substantive but remains incomplete. The inventory now includes 32 sources, with mixed reading depths. The Exa skill was read; no callable Exa connector or configured `EXA_API_KEY` was available in this session. The follow-up used web-index searches and direct primary papers, with no paid service. A failed search is not evidence that an idea is new.

The October 19 focused query log includes `"vision language" safety "text-only" predict evaluation surrogate`; `multimodal safety text image item level disagreement text surrogate evaluation`; `site:arxiv.org multimodal safety "text-only" "predict" evaluation`; `site:arxiv.org "safety" "text" "image" "surrogate" evaluation`; `"multimodal safety" "instance-level"`; `"multimodal" "safety" "evaluation" "subset" "prediction"`; `"safety evaluation" "text-only" "replacement"`; `"Omni-SafetyBench"`; `site:arxiv.org safety evaluation "adaptive" "sampling" jailbreak`; `site:arxiv.org "multimodal" "safety" "triage"`; `site:arxiv.org "benchmark" "safety" "test selection"`; `"tinyBenchmarks" "evaluation" paper`; and `"safety evaluation" "surrogate" "benchmark"`. The web index also returned unrelated transport/clinical safety and automated paper summaries; these were excluded from evidence. S-Eval and other search-only leads were not counted as inspected sources. A complete citation-chain screen remains outstanding.

Three additional comparators materially narrow the claim:

| Primary source / reading depth | Already established | Remaining question to investigate |
| --- | --- | --- |
| Paul Röttger et al., *MSTS: A Multimodal Safety Test Suite for Vision-Language Models*, [2501.10057v1](https://arxiv.org/html/2501.10057), §§3.4, 4.2, 4.5–4.6 | Text equivalents, human response taxonomy, comprehension failures and automated evaluation already appear together | A text/image comparison plus a human audit is insufficient novelty. Our candidate concerns a costed test-selection decision on typography, not first discovery of multimodal-specific failures |
| Leyi Pan et al., *Omni-SafetyBench: A Benchmark for Safety Evaluation of Audio-Visual Large Language Models*, [2508.07173v2](https://arxiv.org/html/2508.07173v2), §§2.2–2.3 | Parallel variants and comprehension-conditioned safety are known. CMSC is a function of variation in aggregate modality scores | Does agreement in aggregate scores conceal different harmful item outcomes? CMSC's formula does not establish that the same requests fail; this is a mathematical distinction, not evidence of an empirical defect in their benchmark |
| Felipe Maia Polo et al., *tinyBenchmarks: evaluating LLMs with fewer examples*, [2402.14992v2](https://arxiv.org/html/2402.14992v2), §§2–5 and §1.1 | Subset selection, historical-model information and efficient score estimation are established | Accurate average-score estimation and finding harmful image responses are different objectives. Do not claim invention of efficient evaluation or active testing |

Additional focused rereads: MMJailBench §§4.3, B.3–B.4 and C.4 already provide a stratified lightweight evaluation and validate aggregate agreement; Reading Between the Pixels §3.4 correlates embeddings with ASR across rendering settings; SafetyPairs §4.2 already examines paired guard errors. These are mandatory comparators for any proposed successor study.

**Recommended candidate question:** When can text-led testing reduce the cost of typographic VLM safety evaluation, and which harmful image responses does it miss? Novelty is unresolved. The possible contribution is a human-audited empirical limit and a validated allocation policy, not a new name for paired tests or a claim that text predicts vision for the first time.

Existing exploratory motivation is reproducible with `tools/vlm_saved_analysis.py` from `v6_full/results_v6.json` (SHA256 `41832d972afc80aa798837d1449110516703255244620cf953811972b73e767a`). For Qwen2-VL-2B, Qwen3Guard's frozen NC-adjusted E/C refusal table has 31 text-only refusals and 21 image-only refusals among 304 valid pairs: the net difference is 10/304, while 52/304 pairs change label. These are refusal labels, not harmfulness labels, and one historical completion per condition does not establish stable item propensities. Neither equivalence nor a new safety result follows from this table.

Before adoption, specify a pilot on already-seen development items: verify exact item/stimulus identities, recover paired harm labels from private caches without printing responses, and human-review a probability sample covering agreements as well as disagreements. Existing marginal harm rates cannot recover a joint harm table. Human reviewers need stimulus and response evidence, blinded model/guard identities and a fixed rubric. Separate recognition failure, refusal, harmless non-refusal and substantive harmful assistance.

If that pilot supports further work, draft an addendum with two distinct objectives: estimate total harmful-response rate; identify harmful image responses under a fixed evaluation cost. For the second objective compare all-image testing, category-stratified random image testing, and a frozen text-led allocation with a random audit of supposedly low-risk items. Count text generation, image generation, guards, preprocessing and model loading. Report missed harmful image responses and uncertainty alongside cost; exclude unresolved labels from neither accounting nor worst-case bounds. Every item needs positive, recorded audit probability if a population risk estimator is claimed. Freeze policies and acceptable error/cost criteria on development data, then test fresh items and declared architecture/backbone splits. Eight related checkpoints are not eight independent architectures. Actual image outcomes must be collected on the evaluation set to assess misses, even if the simulated policy would skip them; this validation collection does not itself save inference. Repeated completions on a prespecified subset would distinguish one-draw disagreement from reproducible changes in response propensity, with their extra cost declared. Typography remains the primary scope; semantic-image substitution would require separately validated captions/evidence and an approved benchmark addition.

The no-go conditions are consequential: if human-reviewed discordance is negligible, judge mistakes account for it, the policy cannot outperform random selection at equal measured cost, or intervals are too wide, do not headline an efficient replacement method. A negative boundary result may still be useful if adequately supported; otherwise retain a narrower replication/measurement paper. More models or benchmarks alone do not rescue weak evidence. No new endpoint, experiment, reserved outcome or approved-plan hash has been changed by this proposal.
