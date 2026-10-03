# VLM Safety Alignment: Paper-by-Paper Reading and Results Audit

**Audit snapshot:** 30 September 2026  
**Bibliography audited:** the 29 numbered entries in the proposal deck: 28 VLM papers and [26], an LLM-only project-history paper.  
**Purpose:** a source-traceable reading and explanation guide. It distinguishes the paper's evidence from our proposed pipeline. It is not a leaderboard: datasets, models, response judges, denominators, and metric directions differ.

## How to use this audit

For each paper, read the cited parts in order and open the named table yourself. In your notes, capture: research question; exact data and split; target checkpoint; attack/access assumptions; metric definition and judge; exact table/figure; result; utility/false-refusal side effect; limitation; and the component it informs in our study.

**Evidence labels**

- **Table-verified:** primary full text was opened and the result below was checked against its table/caption or exact result text. A selected result is not a transcription of every row in the paper.
- **Partially verified:** primary metadata/abstract and a selected table or result were checked, but the full method, appendix, or all rows still need a pass.
- **Not table-verified:** bibliography/role is mapped, but no paper-reported numeric result is reproduced here. Do not quote a result from this row in the talk until the paper table is checked.

**Current attack procedure:** [VLM_ATTACK_PROTOCOL_SPEC.md](VLM_ATTACK_PROTOCOL_SPEC.md) contains the proposed operational runbook and its verification gates. This checklist remains the source for paper-by-paper reading and reported evidence; the protocol does not replace reading the primary attack papers.

This is intentionally strict. A paper’s abstract is not a table, a benchmark’s size is not an efficacy result, and “up to” is not an average. Where a result is not verified, the correct cell is **not transcribed**, not an estimate.

## Reading order by pipeline stage

1. **Evaluation contract and threat model:** [1] FigStep, [2] MM-SafetyBench, [3] HADES, [4] JailBreakV-28K, [9] VLSBench, [10] VSCBench, [11] SIUO, [17] USB, [18] MMJailBench.
2. **Training data/objectives and direct alignment baselines:** [5] VLGuard, [6] SafeVLM, [7] SPA-VL, [12] ADPO, [13] Think in Safety, [16] VSFA, [27] HoliSafe/Safe-VLM, [28] DAVSP, [29] Pragma-VL.
3. **Mechanism and system-level alternatives:** [8] CMRM, [15] VLMGuard-R1, [21] GuardAlign, [22] SafeSteer, [23] SafeRI, [24] SafetyReminder, [25] MMAligner.
4. **Specialized / adaptive attack and ecological evaluation:** [14] MemeSafetyBench, [19] PolyJailbreak, [20] JailBound.

The proposed pipeline is a **comparison framework**, not a claim that the papers form one already-validated method: freeze policy and source-intent splits -> train/attach one intervention at a time -> lock a family-held-out attack suite -> measure harmful compliance, benign false refusal, grounding, general capability, and runtime separately.

## Paper cards

### [1] FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts

- **Pipeline role:** image-carried text/OCR attack; use as a fixed attack family, not as a balanced benchmark or training method.
- **Read:** §4 threat model; §5 attack intuition/design; §6.1–6.4 evaluation and ablation; Table 1 main result; Table 2 design ablation; inspect Fig. 2–3 and the SafeBench/SafeBench-Tiny construction.
- **Protocol to explain:** harmful text is rendered typographically into an image and paired with an innocuous prompt that asks the model to complete a numbered list. The paper manually reviews responses; ASR counts policy-violating responses. It repeats each query five times and calls an item successful if any run succeeds.
- **Exact reported result:** Table 1 reports mean FigStep ASR **82.50%** over six open LVLMs versus **44.80%** on vanilla harmful text; mean response perplexity is **7.73** vs **19.26**. Table 2, SafeBench-Tiny, gives FigStep ASR of **92.00% LLaVA, 90.00% MiniGPT4, 82.00% CogVLM**. These are the authors’ historical target models and their ASR protocol, not a prediction for present-day models.
- **Use/caveat:** include a held-out typography/font/rendering slice plus benign OCR controls. The paper itself notes that low ASR can reflect weak instruction understanding, not safety; judge capability and safety separately.
- **Evidence:** **Table-verified** from [paper PDF](https://arxiv.org/pdf/2311.05608), Tables 1–2, §§6.1–6.4.

### [2] MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal Large Language Models

- **Pipeline role:** broad image-based jailbreak benchmark with query-relevant generated-image, OCR/typography, and combined channels; not itself an alignment method.
- **Read:** dataset construction/taxonomy; attack generation; model/setup section; main results and defense-prompt experiment; inspect each channel-specific table and its caption before quoting a score.
- **Exact facts verified:** the primary abstract reports **5,040 text-image pairs**, **13 scenarios**, and evaluation of **12 MLLMs**. It proposes a safety-prompting defense. **Per-model and per-channel result values are not transcribed in this audit yet.**
- **Use/caveat:** select a prespecified channel subset and add safe matched examples; do not use pooled ASR as a proxy for image-grounded safety.
- **Evidence:** **Partially verified** from [primary arXiv record](https://arxiv.org/abs/2311.17600); main result table still needs row-by-row transcription.

### [3] HADES: Images are Achilles’ Heel of Alignment

- **Pipeline role:** semantic image construction/visual concealing-and-amplifying attack; complements OCR attacks.
- **Read:** attack construction and attacker assumptions; experiment setup; the main ASR table and judge; image-generation/ablation analysis; limitations.
- **Deep-pass before A2:** distinguish Typ, black-box +Opt, and white-box +Adv; verify artifact/code access, image-generation/refinement steps, victim-query use, target models, and each table's denominator. See the proposed A2 protocol in [VLM_ATTACK_PROTOCOL_SPEC.md](VLM_ATTACK_PROTOCOL_SPEC.md).
- **Exact reported result:** the primary abstract reports average ASR **90.26% for LLaVA-1.5** and **71.60% for Gemini Pro Vision** under HADES. The exact table number, per-target rows, judging protocol, and image construction details are **not table-verified here**; do not present those abstract aggregates as a per-paper table extract.
- **Use/caveat:** treat as one fixed semantic-visual family, and separate transferability from adaptive attack results.
- **Evidence:** **Partially verified** from [primary arXiv record](https://arxiv.org/abs/2403.09792); table trace remains open.

### [4] JailBreakV-28K

- **Pipeline role:** multi-family attack collection/benchmark testing transfer of LLM jailbreak prompts to MLLMs; it is not one attack algorithm.
- **Read:** §§3.1–3.3 RedTeam-2K/JailBreakV construction; §4.1 metric and targets; §4.2 Tables 1–5; Appendix A attack policy and image conditions.
- **Protocol check:** identify the included attack subtype and source-intent ID for every selected item; do not describe the collection as a single attack algorithm. Compare its native split/judge with the proposed split and judge in the attack protocol.
- **Protocol:** 2,000 source intents across 16 policies; 20,000 text-transfer image/text cases and 8,000 image-based cases. Llama Guard labels unsafe outputs. The paper evaluates 10 open MLLMs.
- **Exact results:** Table 2 reports average ASR **44.0%** over the full 28K benchmark and **50.5%** for the text-transfer attacks. In that table, LLaVA-1.5-7B total ASR is **46.8%**, LLaVA-1.5-13B **50.1%**, and Qwen-VL-Chat **33.7%**. The authors report mean **57.9%** ASR on the Malware policy and **53.1%** on Economic Harm in Table 3; the printed prose calls the latter “Economic Health,” so preserve the table’s category label when presenting.
- **Use/caveat:** split by original intent and attack transformation; its claim that text transfers can dominate is a paper-specific result, not proof visual attacks are unimportant.
- **Evidence:** **Table-verified** from [COLM paper PDF](https://arxiv.org/pdf/2404.03027), Tables 1–4, §§3–4.

### [5] VLGuard: Safety Fine-Tuning at (Almost) No Cost

- **Pipeline role:** multimodal safety instruction data and a practical SFT baseline.
- **Read:** §3 dataset construction/splits; §4 training/evaluation; Table 2 and Fig. 3; Appendix C.4 black-/white-box checks; dataset and model cards.
- **Data facts:** training construction uses 2,000 images (977 harmful, 1,023 safe), yielding about 3,000 image-instruction-response pairs; test contains 1,000 images and Safe-Safe, Safe-Unsafe, and Unsafe conditions. Post-hoc tuning uses 5,000 helpfulness examples to reduce exaggerated safety.
- **Exact result caution:** project notes cite vanilla LLaVA-v1.5-7B FigStep ASR **72.62%** and post-hoc **0.23%**, plus AdvBench suffix ASR **78.27% -> 13.08%**. These values need direct column/caption recheck against the published Table 2 before they are repeated; **they are therefore not promoted as table-verified in this audit**. In particular, “near-zero ASR on AdvBench” is too broad because the suffix attack row is not zero.
- **Use/caveat:** B2 SFT control; retain benign help data and measure false refusal. Record which setting is post-hoc versus mixed fine-tuning.
- **Evidence:** **Partially verified** from [primary paper](https://arxiv.org/abs/2402.02207); dataset summary checked, exact result-row transcription open.

### [6] SafeVLM: Safety Alignment for Vision Language Models

- **Pipeline role:** architectural safety method (safety projector/tokens/head), separate from data-only SFT.
- **Read:** method and two-stage training sections; Tables 1–5; Appendix settings and judge/metric definitions.
- **Selected exact results from project’s prior paper extraction:** Table 3 reports LLaVA-v1.5-7B / SafeVLM / SafeVLM+LoRA AdvBench vanilla ASR **6.45 / 1.72 / 1.90**, AdvBench suffix ASR **78.27 / 67.56 / 69.86**, XSTest safe-instruction pass **91.20 / 76.89 / 78.09**, and unsafe-instruction compliance **26.50 / 7.46 / 6.96**. Table 1/2 reports RTVLM average **6.39 / 8.18 / 8.26** for base / SafeVLM / +LoRA. Table 4 MMBench **64.3 / 66.8 / 68.5**, SEEDBench **61.6 / 65.3 / 63.7**, MME perception **1487.9 / 1479.5 / 1458.8**, MME aggregate **1773.6 / 1762.7 / 1753.8**.
- **Interpretation:** the text safety gains coexist with lower XSTest safe-pass and mixed capability movement. Its listed attack table is text-centric; do not claim these values prove robustness to visual jailbreaks.
- **Evidence:** **Partially verified** from project’s prior table extraction; re-open [primary paper](https://arxiv.org/abs/2405.13581) Tables 1–5 to finish independent audit before final presentation.

### [7] SPA-VL: A Comprehensive Safety Preference Alignment Dataset

- **Pipeline role:** preference dataset plus DPO/PPO training precedent. SPA-VL is a data resource; DPO is an optimization method.
- **Read:** data construction/response selection and quality check; Tables 1–8; especially dataset scale, Table 2 safety-alignment main comparison, and training-data-scale/ablation tables; supplement for exact training recipe.
- **Data verified:** **100,788** `(question, image, chosen response, rejected response)` records, six harm domains, 13 categories, 53 subcategories; responses collected from 12 open/closed VLMs.
- **Exact results:** CVPR primary PDF includes Table 4 response-model-selection safety columns and Tables 5–6 question-type/architecture details. Example Table 6 DPO-with-projector reports MM-SafetyBench average **0.60**, AdvBench suffix **0.00**, and HarmEval USR **0.00** in the paper’s reported metrics; Table 6 DPO without projector reports **1.64**, **0.19**, and **1.13** respectively. These are not Table 2’s full model-vs-model headline comparison. The proposal needs the main Table 2 selected rows transcribed before using SPA-VL as a numeric SOTA slide.
- **Use/caveat:** B3 standard multimodal preference tuning; match chosen/rejected generation and data budgets. Check overlap with held-out benchmark intents.
- **Evidence:** **Partially verified** from the [SPA-VL paper PDF, arXiv:2406.12030](https://arxiv.org/pdf/2406.12030); published in CVPR 2025. Full main-table audit remains open.

### [8] CMRM: Unraveling and Mitigating Safety Alignment Degradation

- **Pipeline role:** representation-level mechanism diagnosis and inference-time correction; no extra safety fine-tuning.
- **Read:** §2 representation-shift experiments; §3 method; §§4.1–4.4 setup/results/utility; Tables 1–3; Appendix A for data, judge, and overhead.
- **Exact Table 1 results:** for LLaVA-v1.5-7B on VLSafe, unsafe rate is **61.53%** baseline (original image), **5.41%** with CMRM-dataset, and **3.15%** with CMRM-sample. The same table reports LLaVA-Bench-Coco **79.20 / 78.70 / 77.30** and ScienceQA **68.03 / 65.89 / 66.14** for base / CMRM-dataset / CMRM-sample. The 3.15% endpoint is a VLSafe original-input result, not a universal rate across benchmarks.
- **Use/caveat:** inference-time comparator and mechanistic hypothesis; include untouched text-only, blank-image, and noise conditions; measure runtime and utility.
- **Evidence:** **Table-verified** from [ACL Findings paper PDF](https://aclanthology.org/2025.findings-acl.186.pdf), Table 1 and §§2–4.

### [9] VLSBench: Unveiling Visual Leakage in Multimodal Safety

- **Pipeline role:** leakage-controlled benchmark testing whether safety-relevant information actually comes from the image.
- **Read:** §§2–3 VSIL definition/data construction; Table 2 alignment comparison; Tables 4–6 ablations; Table 8 comparison; Appendices D/H/J for taxonomy, training and prompts.
- **Data:** 2,241 image-text pairs, 1,957 unique images, six major categories and 19 subcategories. Queries are detoxified/neutralized so risk cannot simply be read from explicit harmful wording.
- **Exact results:** Figure 1/§2 shows on VLSBench the safety rates for LLaVA-1.5-7B: base **6.6%**, MM-SFT **21.3%**, MM-DPO **27.0%**, textual SFT **13.99%**, textual DPO **13.99%**. These are VLSBench safety rates, not ASR (higher is better). In contrast, under the paper’s leakage-affected standard benchmarks, text tuning may look competitive; that is the central validity finding. Table 5 is a 200-sample image/caption/no-vision control; Table 6 reports NSFW detector rates **0.00** for both detectors, supporting that the image itself is not simply explicit NSFW content.
- **Use/caveat:** a core grounding/leakage test. Pair original image with removed, masked, and decoy-image conditions; do not interpret benchmark safety rate as response helpfulness.
- **Evidence:** **Table-verified** from [ACL 2025 paper PDF](https://aclanthology.org/2025.acl-long.405.pdf), Figures 1/4, Tables 2/5/6/8, §§2–3.

### [10] VSCBench: Bridging the Gap in VLM Safety Calibration

- **Pipeline role:** matched safe/unsafe calibration and over-refusal benchmark; evaluates both under-safety and over-safety.
- **Read:** §3 construction (image- and text-centric sets); §4 metric definitions; Table 2 per-model/category safety calibration; Table 3 response types; method comparison/limitations.
- **Data/result facts:** 3,600 image-text pairs and 11 VLMs, as reported in the official ACL paper record. Table 2 reports **SRA_safe**, **SRA_unsafe**, and **SRA_appropriate** by category and model; do not quote one SRA without specifying which. Table 3’s “Pornography” unsafe-query response classification includes GPT-4o toxic **7.5%**, unsafe-nontoxic **78.3%**; LLaVA-13B toxic **32.3%**, unsafe-nontoxic **5.3%**; VLGuard-7B toxic **17.2%**, unsafe-nontoxic **28.3%**. This demonstrates why “unsafe” and “toxic” are not interchangeable.
- **Use/caveat:** score matched pair completion/refusal jointly; report safe answer quality and false refusal separately.
- **Evidence:** **Partially verified** from [ACL paper PDF](https://aclanthology.org/2025.findings-acl.158.pdf), Tables 2–3; construction count and paper record checked. Need transcribe full category breakdown if used as a principal quantitative slide.

### [11] SIUO: Safe Inputs but Unsafe Output

- **Pipeline role:** compositional cross-modal benchmark: each modality can appear safe alone while their combined interpretation implies risk.
- **Read:** benchmark definition and nine-domain taxonomy; construction/annotation and splits; model experiments and evaluation tables; transfer/generalization analysis and appendix.
- **Count:** ACL primary record describes the nine-domain benchmark but not its item count. VLMGuard-R1’s paper explicitly says it uses **all 167 available SIUO instances**; HoliSafe Table 1 prints **269** for its comparison inventory. Treat 167 as the benchmark count used in that later protocol and 269 as a separate cited inventory until the SIUO primary PDF’s exact split/table explains the difference. Do not state they are the same count.
- **Exact result:** the original SIUO paper’s numeric comparison table is **not transcribed here**. VLMGuard-R1’s own result is reported under [15], not to be attributed to SIUO authors.
- **Evidence:** **Partially verified** from [ACL primary record](https://aclanthology.org/2025.findings-naacl.198/) and [VLMGuard-R1 paper PDF](https://aclanthology.org/2026.findings-acl.1986.pdf), §3.1/Appendix A.1; primary SIUO table check still open.

### [12] ADPO: Adversary-Aware DPO

- **Pipeline role:** direct adversarial preference-alignment baseline; strongest direct prior art for training-time adversarial robustness.
- **Read:** §§3–4.4; Fig. 2; Table 1 main safety+utility; Table 2 training cost; Figure 5 alpha ablation; Appendix A attack settings and B added experiments.
- **Protocol:** white-box VisualAdv and MMPGDBlank plus black-box MultiTrust typo/multimodal/crossmodal; HarmBench classifier; LoRA; ASR lower is better; utility values remain in native units.
- **Exact Table 1 selected rows (LLaVA-1.5-7B):** base ASR VisualAdv/MMPGDBlank/MultiTrust typo/multimodal/crossmodal **64.5/84.0/22.2/55.1/42.0**; DPO **12.0/33.0/0.7/8.8/9.6**; ADPO **5.0/0.5/0.0/0.0/0.2**. Utility (MMStar/OCRBench/MM-Vet/LLaVABench) is base **32.7/202/29.9/59.5**, DPO **33.9/198/28.9/54.4**, ADPO **33.7/184/24.2/48.2**. For Qwen2-VL-7B, base ASR is **13.5/30.0/4.5/54.3/6.3** and ADPO **0.0/1.5/0.0/4.0/0.0**; utility changes **58.5/841/64.7/88.0 -> 57.6/830/53.9/74.2**. These are exact cells in Table 1, not common-scale results with other papers.
- **Use/caveat:** B4 only after exact model/data/attack recipe reproduction; report white-box and black-box separately and include utility cost. This is prior art, so do not claim “first adversarial VLM alignment.”
- **Evidence:** **Table-verified** from [EMNLP Findings paper PDF](https://aclanthology.org/2025.findings-emnlp.735.pdf), Table 1/§4; attack and utility rows checked against the table layout.

### [13] Think in Safety

- **Pipeline role:** reasoning-oriented safety training/data for multimodal reasoning models; distinct from ordinary VLM refusal SFT.
- **Read:** model/method and reasoning-data construction; evaluation datasets including MSSBench/SIUO; main safety and capability tables; ablations; Appendix sampling, judge and reasoning-token/runtime cost.
- **Exact result:** no numerical result is reproduced in this audit until its table rows and metric definitions are checked. Do not quote an abstract gain as a table value.
- **Use/caveat:** related-work comparator; include only if the target model has comparable reasoning behavior and added inference tokens are measured.
- **Evidence:** **Not table-verified**. Primary source: [EMNLP 2025 paper](https://aclanthology.org/2025.emnlp-main.261/).

### [14] MemeSafetyBench: Are VLMs Safe in the Wild?

- **Pipeline role:** ecological test on real memes and single-/multi-turn context; not a generic safety benchmark.
- **Read:** dataset sourcing/taxonomy/annotation; Table 2 main harmful/benign results under the three input/context settings; Tables 3–5 category/context analyses; appendix split/label details.
- **Data verified:** 50,430 instances pairing real meme images with harmful and benign instructions; paper studies single- and multi-turn interactions. Existing dossier reports 46,599 harmful and 3,831 benign, but these class counts require verification against the paper’s Table 1 before reuse.
- **Exact result:** the main table values are not transcribed in this audit; the primary abstract states meme inputs increase harmful responses and reduce refusals relative to text-only inputs, but that qualitative summary is not a substitute for Table 2.
- **Use/caveat:** optional ecology slice; due imbalance, report classwise HR/RR/CR, not accuracy alone. Single-turn and multi-turn must remain distinct.
- **Evidence:** **Partially verified** from [EMNLP 2025 paper/PDF](https://aclanthology.org/2025.emnlp-main.1555/).

### [15] VLMGuard-R1

- **Pipeline role:** external multimodal reasoning-driven prompt rewriter. Target model weights remain unchanged; this is a system-level guard, not intrinsic target-model fine-tuning.
- **Read:** §2 method and three-stage data synthesis; §§3.1–3.6 experiments; Tables 1–5; Table 6 refusal-string DSR; Tables 8–9 runtime/scaling; Appendix A.1–A.3 data, metrics, and prompts.
- **Protocol:** Table 1 compares GPT-4o safety (0–10) and helpfulness (%) across five open models and unsafe datasets; the paper also uses 200 VLGuard-Unsafe examples, all **167** SIUO examples, and 300 sampled MM-SafetyBench cases. Table 6’s DSR is a predefined-refusal-string measure, not semantic HCR.
- **Exact result:** the official ACL abstract reports **+43.59% average safety** across five models on SIUO; the table is required to interpret that as the paper’s “safety score” change, not percent points unless the method explicitly defines it so. Project extraction lists Table 1 LLaVA-1.5-7B VLGuard-Unsafe safety/helpfulness **3.71/20.92 -> 6.70/59.30** and SIUO **3.80/44.85 -> 6.77/58.43** with/without rewriter. The Qwen2-VL-7B SIUO helpfulness cell falls **60.24 -> 53.61** while its safety score rises **4.26 -> 6.11**. Confirm each cell in Table 1 and Table 5 before moving it to the deck.
- **Use/caveat:** compare as an optional front-end guard; count extra calls, latency, and transformed-input errors. Never call its DSR semantic safety.
- **Evidence:** **Partially verified** from [ACL 2026 paper PDF](https://aclanthology.org/2026.findings-acl.1986.pdf), Tables 1–2/§3; Table 5 verified separately in the paper extraction; full appendix/cost still needs pass.

### [16] VSFA: Visual Self-Fulfilling Alignment

- **Pipeline role:** training-time, label-free alternative; learns from neutral VQA over threat-related images rather than explicit safety labels.
- **Read:** method/data construction; Table 1 ASR and Constructive Score across four models and image/text/mixed training; Table 2 MM-Vet and benign refusal; Fig. 2 modality ablation; appendices for training scale, image source, and model details.
- **Exact facts:** the paper uses GPT-4o as judge, defines ASR as harmful-intent compliance, Constructive Score across politeness/helpfulness/task completion/logical flow/information richness, and reports MM-Vet plus benign refusal in Table 2. The exact Table 1/2 numeric cells are not transcribed here; no numerical winner claim should be made from this checklist yet.
- **Use/caveat:** compare its threat-image exposure hypothesis against explicit safety SFT using matched data and compute; include its image/text/mixed ablations.
- **Evidence:** **Partially verified** from [ACL 2026 paper PDF](https://aclanthology.org/2026.acl-long.490.pdf), metric and table captions; full numeric table pass open.

### [17] USB: Unified Safety Benchmark

- **Pipeline role:** broad risk-by-modality benchmark with both vulnerability and over-refusal outcomes.
- **Read:** §§2.1–2.5 taxonomy/data construction; Figure 3; Tables 1–3 coverage and data; Table 2 model safety/refusal results; §§3.2–3.3 hard-set and modality findings; Appendix H judge/protocol.
- **Data facts:** 61 tertiary risk categories × four modality combinations = 244 intersections; USB-Base **13,175** pairs and USB-Hard **3,785**; 22 MLLMs (9 commercial, 13 open). Coverage is 98.3% under the paper’s >=20-sample definition. Table 1 reports benchmark-level coverage/safety summary (including 46.38% vulnerability and 27.37% over-refusal in the extracted row); do not confuse these dataset-level values with model SR/RR.
- **Exact selected result:** paper text reports Claude-Sonnet4 safety rate **91.16%** and refusal rate **18.30%**, versus Claude3.5-Sonnet2 **82.79%** and **25.82%**. On USB-Hard, Claude-Sonnet4 **77.82%** and Qwen3.6-Plus **72.85%**; each falls roughly 13–15 points from USB-Base. Table 2 is model performance, where higher safety rate is better; Table 1 benchmark-difficulty SR has the reverse interpretation.
- **Use/caveat:** use a prespecified VLM-relevant slice; separate base/hard and modality cells, preserve the paper’s SR/RR judge protocol.
- **Evidence:** **Table-verified** from [ACL 2026 paper PDF](https://aclanthology.org/2026.acl-long.970.pdf), Tables 1–3, §§2–3.

### [18] MMJailBench

- **Pipeline role:** factorized benchmark that isolates intent, prompt framing, visual semantics, and carrier; not an attack algorithm.
- **Read:** factor definitions/configuration construction; full vs lightweight protocol; 16-model panel; judge/threshold; main and factor-ablation tables; preprint version history and code.
- **Data facts in project notes:** 272 intents × 6 frames × 5 visual semantics × 2 carriers = 16,320 configurations. This count and the reported CASR/model results are not independently table-verified in this pass.
- **Exact result:** not transcribed. Do not imply its factorial sample combinations are all independent source intents or responses.
- **Use/caveat:** benchmark-design precedent for causal attribution and held-out factor combinations; preprint status as of snapshot.
- **Evidence:** **Not table-verified** from [arXiv preprint](https://arxiv.org/abs/2608.25490).

### [19] PolyJailbreak

- **Pipeline role:** adaptive black-box cross-modal attack; reserve as locked adversarial evaluation, not train/validation data.
- **Read:** attack algorithm and feedback loop; attacker query budget; access assumptions; target set; success judge; transfer results and ablations.
- **Deep-pass before A5:** verify final IEEE version vs. arXiv, exact attacker actions, paper-native `T_max`, call accounting, target access, stopping criterion, judge, and released code. The project's proposed 5 discovery + 15 optimization calls is a separate harmonized cap, not a paper result.
- **Exact result:** no numeric value reproduced. Verify budget, number of prompts/iterations, and exact success definition from the version pinned for the project before implementing.
- **Use/caveat:** report success as a function of fixed query budget; don't pool its adaptive attack success with static benchmark ASR.
- **Evidence:** **Not table-verified** from [arXiv preprint](https://arxiv.org/abs/2510.17277).

### [20] JailBound

- **Pipeline role:** white-box internal safety-boundary probe; diagnostic threat tier, not an ordinary black-box image attack.
- **Read:** boundary definition and construction; required model access; attack optimization; main success/transfer tables; perturbation constraints and limitations.
- **Exact result:** not transcribed. No numeric assertion should be made until the full NeurIPS paper and supplement are inspected.
- **Use/caveat:** only for open-weight targets and separately reported with access/compute requirements.
- **Evidence:** **Not table-verified** from [NeurIPS 2025 record](https://papers.neurips.cc/paper_files/paper/2025/hash/7a3c73909dfc23242f32cd6b3b16b00b-Abstract-Conference.html).

### [21] GuardAlign

- **Pipeline role:** test-time unsafe-region detection and cross-modal attention calibration; inference-time/system comparator.
- **Read:** method and detector/calibration stages; ICLR main results table; exact six-model data and benchmarks; ablations, detector error/utility, runtime.
- **Exact result caution:** existing audit cites the abstract’s “up to 39%” unsafe-response reduction and VQAv2 **78.51 -> 79.21**. These are currently **abstract-level claims**, not a verified result-table transcription; “up to” must retain its particular setting and is not an average.
- **Use/caveat:** account for detector false positives and overhead; it is not a weight-alignment baseline.
- **Evidence:** **Partially verified** from [official ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c10c771f52408a2de77d056a4109e93d-Abstract-Conference.html); exact table trace open.

### [22] SafeSteer

- **Pipeline role:** decoding-level safety probe/steering; inference-time alternative.
- **Read:** method/steering-vector construction; exact published ACL Findings version; result tables for safety, utility, attacks, ablations, and latency; compare against earlier similarly named draft only after version resolution.
- **Exact result caution:** existing note says abstract “up to +33.40%”; no table/denominator is transcribed, so do not present as the paper’s average or general gain.
- **Evidence:** **Partially verified** from [ACL Findings 2026 record](https://aclanthology.org/2026.findings-acl.916/); full table pass open.

### [23] SafeRI

- **Pipeline role:** streaming recognizer plus gated LoRA/token-level selective intervention; emerging preprint.
- **Read:** recognizer target/threshold; gated-LoRA mechanism; benchmark data and judges; all main/ablation tables; latency and false-trigger analysis; pin version/date and repository commit.
- **Exact result:** not reproduced here. It is an **arXiv preprint** in this snapshot, not a peer-reviewed settled SOTA result.
- **Evidence:** **Not table-verified** from [arXiv:2609.03544](https://arxiv.org/abs/2609.03544).

### [24] SafetyReminder

- **Pipeline role:** inference-time safety reminder/soft-prompt method.
- **Read:** reminder construction/injection point; training requirements; Table 1 attack results; utility/false-refusal table; ablations; latency and target-version details.
- **Exact result:** earlier notes contain average ASR values but the paper’s Table 1 and judge have not been rechecked in this audit; those numbers are withheld pending source trace.
- **Evidence:** **Not table-verified** from [AAAI 2026 paper record](https://ojs.aaai.org/index.php/AAAI/article/view/40607).

### [25] MMAligner

- **Pipeline role:** representation calibration toward a refusal/safety region; inference/representation comparator.
- **Read:** calibration objective and intervention layer; target models; main safety/utility table; calibration/false-refusal analyses; ablations and code/version.
- **Exact result:** no result copied from an abstract or secondary summary. Full paper table remains to be checked.
- **Evidence:** **Not table-verified** from [arXiv:2608.05909](https://arxiv.org/abs/2608.05909).

### [26] Continual Safety Alignment via Gradient-Based Sample Selection

- **Pipeline role:** LLM-only project history, excluded from VLM evidence and VLM baselines.
- **Read:** only if explaining the project origin: method, task setup, reported LLM results, and assumptions. Do not transfer its values or claim the method works on VLMs.
- **Evidence:** scope classification checked against attached paper; **not a VLM paper**.

### [27] HoliSafe / Safe-VLM

- **Pipeline role:** five-state dataset, benchmark, and integrated visual guard. Direct prior art; the five-state proposal is not novel.
- **Read:** §§2.1–2.2 data and five states; §3 VGM; §§4.1–4.5 results; Tables 1, 3–5; Appendix D.1–D.2 judging/scoring and training setup.
- **Data/method:** 6,689 images and 14,246 image-instruction-response pairs; 10,215 train pairs; 4,031 test Q&A pairs on 1,796 images; seven main categories/eighteen subcategories. A pooled visual representation feeds a two-layer MLP VGM; classification and next-token instruction losses are jointly trained.
- **Exact Table 3 selected results:** LLaVA-v1.5-7B mASR **79.1%** Claude / **91.2%** GPT-4o / **94.0%** Gemini / **95.9%** string match; VLGuard-7B **39.9/49.6/51.9/52.2**; SPA-VL-DPO-7B **40.5/55.6/58.3/63.7**; SafeLLaVA-7B **8.8/15.3/15.8/15.4**. SafeLLaVA Claude safe-pair RR is **1.3%**. The previously circulated **12.3%** is not SafeLLaVA mASR; it is a different model/category cell.
- **Exact Table 4 selected results:** same LLaVA family, SafeLLaVA: VLSBench safety **69.8**, MM-SafetyBench average ASR **7.7**, HarmEval unsafe score **0**, SIUO safe score **60.5** (each in its own metric units). Compare with LLaVA base **6.6 / 60.2 / 44.2 / 21.6** and SPA-VL-DPO **27.0 / 31.7 / 0 / 43.7**.
- **Use/caveat:** reproduction/data/architecture comparator; judge-specific values and GPT-generated supervision limit direct cross-paper claims. Audit exact benchmark-count discrepancy for SIUO rather than merging counts.
- **Evidence:** **Table-verified** from [CVPR Findings paper](https://arxiv.org/pdf/2506.04704), Tables 1/3/4 and Appendices.

### [28] DAVSP: Deep Aligned Visual Safety Prompt

- **Pipeline role:** training-time optimized visual prompt plus activation-space alignment; target LVLM otherwise frozen.
- **Read:** §§3–5.6; Fig. 2; Tables 1–6; extended-version appendix for implementation/adversarial analysis.
- **Data/setup:** harmfulness vector from 470 rejected malicious + 470 benign VLGuard samples; train prompt using 600 harmful MM-SafetyBench + 100 benign MM-Vet items; LLaVA-1.5-13B and Qwen2-VL-7B; DeepSeek-V3 semantic judge for RSR.
- **Exact results:** Table 2 FigStep RSR **84.20%** LLaVA-1.5-13B and **99.20%** Qwen2-VL-7B; MM-SafetyBench SD+TYPO RSR **98.72%** and **99.12%**. Table 1 utility: LLaVA MM-Vet total **39.07**, MME total **1602**, LLaVA-Bench **63.6**; Qwen MM-Vet **61.61**, MME **2146**, LLaVA-Bench **75.2**. Table 4 removing Deep Alignment reduces LLaVA FigStep RSR to **67.00%**; replacing visual padding with additive perturbations gives **76.20%**.
- **Use/caveat:** relevant efficient comparator; common AdaShield-S prompt and white-box source-model prompt optimization are part of its protocol. Report model transfer separately.
- **Evidence:** **Table-verified** from [AAAI 2026 paper](https://ojs.aaai.org/index.php/AAAI/article/view/41149), Tables 1–6.

### [29] Pragma-VL

- **Pipeline role:** end-to-end training-time arbitration of safety and helpfulness: risk-aware visual clustering/cold-start SFT, followed by query-dependent dynamic reward weighting.
- **Read:** §§3–4.4; Fig. 2; Tables 1–4; Appendix D.2 judge/setup; code and compute details. Use the ICLR-published version, not abstract alone.
- **Exact results from the proceedings-indexed paper extraction:** Qwen2.5-VL-7B + Pragma-VL Table 2: BeaverTails-V helpfulness/harmlessness win rates **62.65/67.91**; SPA-VL **87.17/87.92**; MM-SafetyBench helpfulness/harmlessness **52.74/58.99**, ASR **31.66**; SIUO effective/safety **95.21/63.47**. Table 3 general benchmarks: GQA **61.42**, ScienceQA **89.06**, TextVQA **83.75**, VizWizQA **78.90**, VQAv2 **84.20**, MathVista **67.20**. Preserve native score units and do not treat safety/helper pair scores as a shared percentage without confirming table heading.
- **Use/caveat:** direct recent training comparator; Qwen2.5-VL-7B and LLaVA-1.5-7B, GPT-4o judge, 16 A100s are reported in the paper notes; verify compute/recipe from appendix before reproduction.
- **Evidence:** **Partially verified** from [official ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4054556fcaa934b0bf76da52cf4f92cb-Abstract-Conference.html); table values recorded from proceedings-indexed full text, but PDF/appendix source trace and exact metric heading should be rechecked before slide use.

## Corrections and unresolved evidence issues

1. **Do not say all 28 VLM papers are fully audited yet.** The matrix explicitly marks outstanding table checks. The completed artifacts are not equal in verification depth.
2. **HoliSafe’s 12.3% misattribution:** its Table 3 gives SafeLLaVA-7B Claude mASR **8.8%** and RR **1.3%**. Do not reuse 12.3% for that model.
3. **SIUO counts:** the VLMGuard-R1 protocol uses all 167 available items. HoliSafe’s Table 1 comparison lists 269. The primary SIUO source’s count/split should be read before describing why these differ; for now label provenance rather than harmonize.
4. **VLGuard “near-zero” shorthand:** do not claim every text attack is near zero. The existing extracted suffix-ASR result is nonzero, and the source table’s exact row/condition needs recheck.
5. **ADPO row alignment:** Table 1 has now been re-opened and its LLaVA/Qwen rows resolved. Cite its exact columns; do not reuse the earlier misaligned utility tuple from text extraction.
6. **Pragma-VL table units:** confirm each Table 2 header and whether values are rates, scores, or win rates. Do not label all as percent just because some headings say win rate.
7. **SIUO, MM-SafetyBench, HADES, PolyJailbreak, JailBound, SafeRI, SafetyReminder, MMAligner, GuardAlign, SafeSteer, Think in Safety, and MemeSafetyBench** need their primary result tables and supplements fully transcribed before we call this a complete numerical audit.

## What the proposal pipeline can responsibly claim now

- **Problem:** VLM safety is a joint image-text behavior problem with safety, benign answerability, and grounding as separate outcomes.
- **Prior art:** multimodal SFT and preference alignment already exist (VLGuard, SPA-VL, ADPO); representation correction exists (CMRM); visual safety prompting exists (DAVSP); five-way state coverage and VGM already exist (HoliSafe); arbitration training exists (Pragma-VL); external reasoning rewrite and label-free threat-image training are peer-reviewed alternatives (VLMGuard-R1, VSFA).
- **Threat evaluation:** include fixed OCR (FigStep), broad channel slice (MM-SafetyBench), semantic visual attack (HADES), intent-held-out transferred attacks (JailBreakV), compositional SIUO, leakless VLSBench, paired VSCBench, and a preregistered slice of USB. Keep adaptive PolyJailbreak and white-box JailBound/ADPO attacks as separate tiers.
- **Baseline ladder:** native checkpoint; text-only SFT; multimodal safety SFT; standard DPO on preference pairs; ADPO if faithfully reproducible; one direct recent method (HoliSafe/Safe-VLM, DAVSP, or Pragma-VL) only if code/data/model and resources allow. Runtime defenses should be secondary system comparators, not mixed into training leaderboard.
- **Required result reporting:** per-item N and unique intents; semantic harmful-compliance with judge details; benign false-refusal and useful-answer quality; visual grounding controls; general VQA/OCR; latency/additional calls; training compute; confidence intervals. No pooled cross-paper leaderboard.

## Source ledger for remaining full audits

The numbered IEEE reference page in the deck is the bibliographic authority for this checklist. The source links above point to primary paper/proceedings records or PDFs. Before any table result appears in the deck, capture the exact paper version, table number, row label, column label, unit, judge, and checkpoint in the speaker-note/evidence ledger. For inaccessible full text, preserve “not verified” and ask for the paper file rather than filling in from memory or a secondary summary.
