# Visual attacks on VLMs: research brief and paper list

## What you asked this research to do

Study the existing research on visual attacks against vision-language models **before proposing a new attack or defense**. Identify the original papers; read them in depth; explain what each actually did, how and why it worked in its experiments, what data and models it used, and how success was measured. Then rerun recoverable original experiments and use the verified findings to design our own contribution.

The deliverable is a paper-based research dossier and reproducible experiment record. Helper functions, a paper-name list, source downloads or one encoder-loss demonstration do not by themselves meet that request. No new synthetic examples or invented results may fill missing original evidence.

For each selected paper, the required analysis is:

1. **Identity and motivation:** original title, authors, version, source link, problem and claimed contribution.
2. **Architecture:** an annotated diagram from inputs through encoder/connector/decoder to response, showing where the attack acts and what is frozen.
3. **Threat model:** attacker access, controlled inputs, objective and constraints.
4. **Mathematics:** every loss, update and constraint, with symbols explained and targeted/untargeted distinctions.
5. **Data:** original dataset/trigger collection, construction, source files, splits, licensing and train/development/evaluation roles.
6. **Procedure:** initialization, preprocessing, optimization, model/checkpoint, decoding, repetitions, selection and compute.
7. **Evaluation:** exact success criterion, denominators, judges/human reviewers, uncertainty, controls, benign utility and costs.
8. **Original evidence:** reported results linked to the actual section/table; limitations and author claims separated from our conclusions.
9. **Reproduction:** rerun attack construction and the chosen original evaluation; record actual outputs and original-versus-reproduced results, with deviations and blockers.
10. **Synthesis:** compare mechanisms and pipelines, identify what is already known, and only then justify a testable contribution.

**Plain-language clarification:** in these papers, “downstream evaluation” means feeding the attack image into the target VLM with the specified text and assessing its generated answer. It is part of testing the attack itself, not a separate future application of the paper. Image optimization alone cannot reproduce the paper's behavioral result.

## The papers we should research first

The initial twelve-paper reading set is P01–P08 and P11–P14 below: three foundations, four digital VLM attack papers, physical injection, one comparison benchmark, two defenses and one survey. P09–P10 connect the historical typographic work. P15–P22 broaden attack coverage as the project evolves. Architecture and evaluation papers support understanding and measurement; they are not all additional attack algorithms.

| Research question | First papers | Intended research product |
|---|---|---|
| What is the mathematics of pixel/patch optimization? | FGSM (P01), Madry/PGD (P02), Adversarial Patch (P03) | Worked equations and constraints; distinguish classifier results from VLM safety |
| What has actually been demonstrated against generative VLMs? | Qi (P04), Jailbreak in Pieces (P05), Image Hijacks (P06), BAP (P07) | Full method/data/model/result analyses and recoverable original experiment contracts |
| What other attack families would our first panel miss? | Physical injection (P08), AttackVLM (P15), imgJP (P16), HADES (P17), Multi-Modal Linkage (P19), visual-modality attacks (P22) | Source-verified expansion of transfer, semantic and scene-based mechanisms |
| How does this connect to our earlier research? | FigStep (P09), MM-SafetyBench (P10) | Typography, framing and content/carrier controls; historical evidence kept separate |
| How should safety and defenses be compared? | MMJ-Bench (P11), AdaShield (P12), JailGuard (P13), HarmBench (P31), StrongREJECT (P32) | Native scoring, safety/utility distinctions, defense assumptions and cost |
| What could invalidate a novelty claim? | VLSBench (P23), DUAL-Bench (P26), MMJailBench (P28), alignment studies (P29–P30) | Closest-prior-work comparison before proposing a contribution |

## Evidence status and full catalogue

28 October 2026. **40 distinct papers** spanning architecture, attacks, safety evaluation and defenses. This is the consolidated reading set for the current atlas and its wider research expansion, not an exhaustive bibliography of the field or every citation ever mentioned in this repository. Preprint and conference versions are one study unless explicitly distinguished.

The [architectural atlas](VISUAL_ATTACK_PIPELINE_ATLAS.md) explains the inspected methods. The [native-paper audit](VISUAL_PAPER_REPRODUCTION_AUDIT.md) preserves code revisions and blockers. Historical prior-art investigations, including additional measurement/steering papers, remain in [NOVELTY_AUDIT_AND_PLAN.md](NOVELTY_AUDIT_AND_PLAN.md); they are not silently promoted into completed attack implementations here.

Reading status: **M** = original methods/setup and selected appendices inspected, full table/release audit incomplete; **H** = focused full-text inspection recorded in the historical novelty audit; **A** = original title/metadata/abstract checked, detailed method unverified. None of these means independently reproduced. All new native-paper runs in the registered workbench remain `NOT_RUN`.

## Core attack mechanisms, evaluation and defense structure

| ID | Original paper | Pipeline role / why it matters | Inspection |
|---|---|---|---|
| P01 | Goodfellow et al., [Explaining and Harnessing Adversarial Examples](https://arxiv.org/html/1412.6572v3) | FGSM: input-gradient classification baseline; §§3–4 | M |
| P02 | Madry et al., [Towards Deep Learning Models Resistant to Adversarial Attacks](https://arxiv.org/html/1706.06083v4) | PGD inner search versus outer robust training; §§2,5 | M |
| P03 | Brown et al., [Adversarial Patch](https://arxiv.org/html/1712.09665v2) | Universal replacement patch, transformations and physical evidence; §§2–3 | M |
| P04 | Qi et al., [Visual Adversarial Examples Jailbreak Aligned Large Language Models](https://arxiv.org/html/2306.13213v2) | Corpus sequence objective through a frozen VLM; §§3–4, Appendix A | M |
| P05 | Shayegani et al., [Jailbreak in pieces: Compositional Adversarial Attacks on Multi-Modal Language Models](https://arxiv.org/html/2307.14539v2) | Encoder-targeted trigger representations; §§3–4, Algorithm 1 | M |
| P06 | Bailey et al., [Image Hijacks: Adversarial Images can Control Generative Models at Runtime](https://arxiv.org/html/2309.00236v4) | Behavior and teacher-distribution prompt matching; §§2–4, Appendix C | M |
| P07 | Ying et al., [Jailbreak Vision Language Models via Bi-Modal Adversarial Prompt](https://arxiv.org/html/2406.04031v2) | Visual gradient stage plus iterative text feedback; §§4–5, Appendices A,D | M |
| P08 | Ling et al., [Physical Prompt Injection Attacks on Large Vision–Language Models](https://arxiv.org/html/2601.17383v1) | Scene-visible content, selection, placement and camera; §§III–VI | M |
| P09 | Gong et al., [FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts](https://arxiv.org/html/2311.05608v3) | Typography and framing; existing all-text control; §§5–6 | H |
| P10 | Liu et al., [MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal Large Language Models](https://arxiv.org/html/2311.17600v2) | Semantic/typographic carriers and multimodal query construction; §§2–3 | H; version distinction retained |
| P11 | Weng et al., [MMJ-Bench: A Comprehensive Study on Jailbreak Attacks and Defenses for Vision Language Models](https://ojs.aaai.org/index.php/AAAI/article/download/34983/37138) | Common attack/defense comparison and benign utility; setup, Tables 3–4 | M |
| P12 | Wang et al., [AdaShield: Safeguarding Multimodal Large Language Models from Structure-based Attack via Adaptive Shield Prompting](https://arxiv.org/html/2403.09513v1) | Static defense and adaptive prompt pool/retrieval; §§3–4 | M |
| P13 | Zhang et al., [JailGuard: A Universal Detection Framework for Prompt-based Attacks on LLM Systems](https://arxiv.org/html/2312.10766v4) | Mutation, repeated generation and divergence detection; §§4–6 | M |
| P14 | Zhang et al., [Adversarial Attacks of Vision Tasks in the Past 10 Years: A Survey](https://arxiv.org/abs/2410.23687) | Taxonomy and discovery; not a separate attack to run | M; selected taxonomy sections |

## Wider visual mechanisms and transfer — newly screened

These papers expand scope beyond the first implementation. Entries describe abstract-level relevance only. No detailed hyperparameters, datasets, reported ASRs or mechanistic conclusions are imported until the original methods, result tables and release are audited.

| ID | Original paper | Relevance to the evolved project | Inspection |
|---|---|---|---|
| P15 | Zhao et al., [On Evaluating Adversarial Robustness of Large Vision-Language Models](https://arxiv.org/abs/2305.16934) | AttackVLM: surrogate visual models, transfer and black-box targeted evasion | A |
| P16 | Niu et al., [Jailbreaking Attack against Multimodal Large Language Model](https://arxiv.org/abs/2402.02309) | imgJP: likelihood-based image jailbreak prompts, sharing and transfer | A |
| P17 | Li et al., [Images are Achilles’ Heel of Alignment: Exploiting Visual Vulnerabilities for Jailbreaking Multimodal Large Language Models](https://arxiv.org/abs/2403.09792) | HADES: images alter how malicious intent is expressed and amplified | A |
| P18 | Luo et al., [JailBreakV: A Benchmark for Assessing the Robustness of MultiModal Large Language Models against Jailbreak Attacks](https://arxiv.org/abs/2404.03027) | Text-to-multimodal attack transfer; benchmark known as JailBreakV-28K | A |
| P19 | Wang et al., [Jailbreak Large Vision-Language Models Through Multi-Modal Linkage](https://aclanthology.org/2025.acl-long.74/) | Cross-modal linkage; inspect semantics/control design before implementation | A |
| P20 | Pathade, [Invisible Injections: Exploiting Vision-Language Models Through Steganographic Prompt Embedding](https://arxiv.org/abs/2507.22304) | Candidate hidden-content injection; strong abstract claims require independent scrutiny | A |
| P21 | Wang et al., [PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs](https://arxiv.org/abs/2510.17277) | Black-box cross-modal framework; keep query/access budget explicit | A |
| P22 | Azulay et al., [Jailbreaking Vision-Language Models Through the Visual Modality](https://arxiv.org/abs/2605.00583) | Visual ciphers, semantic substitution and analogy broaden the pixel/typography taxonomy | A |

## Benchmarks that prevent a misleading comparison

| ID | Original paper | What must be checked before dataset use | Inspection |
|---|---|---|---|
| P23 | [VLSBench: Unveiling Visual Leakage in Multimodal Safety](https://arxiv.org/abs/2411.19939) | Visual dependence versus text-only leakage; source construction, splits and licenses | A this pass; H §2/Table 1 in historical audit |
| P24 | [USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models](https://arxiv.org/abs/2505.23793) | Risk/modality coverage and vulnerability versus oversensitivity | A |
| P25 | [HoliSafe: Holistic Safety Benchmarking and Modeling for Vision-Language Model](https://arxiv.org/abs/2506.04704) | Image/text safety combinations; benchmark use versus trained mitigation | A |
| P26 | [DUAL-Bench: Measuring Over-Refusal and Robustness in Vision-Language Models](https://arxiv.org/abs/2510.10846) | Safe completion and benign tasks with risky visual content | A this pass; H §§3–4 in historical audit |
| P27 | [Text2VLM: Adapting Text-Only Datasets to Evaluate Alignment Training in Visual Language Models](https://arxiv.org/abs/2507.20704) | Typographic dataset adaptation already exists; check semantic preservation | A |
| P28 | [MMJailBench: A Factorized Benchmark for Disentangling Multimodal Jailbreak Vulnerabilities](https://arxiv.org/abs/2608.25490) | Framing, visual semantics and carriers; closest comparator for factorization claims | A this pass; H §§3–5 in historical audit |

**MMJ-Bench (P11) and MMJailBench (P28) are different papers.** HarmBench supplies behavior/scoring infrastructure; it does not by itself provide a natural-image safety scene dataset. SafeBench, MM-SafetyBench and the BAP paper's SafetyBench naming must be resolved by exact source files rather than name similarity.

## Mechanism and alignment context

| ID | Original paper | Why it changes interpretation | Inspection |
|---|---|---|---|
| P29 | Pantazopoulos et al., [Learning To See But Forgetting To Follow: Visual Instruction Tuning Makes LLMs More Prone To Jailbreak Attacks](https://arxiv.org/abs/2405.04403) | Prior work on the relationship between visual integration and safety; no general text-versus-vision superiority assumption | A |
| P30 | Liu et al., [Unraveling and Mitigating Safety Alignment Degradation of Vision-Language Models](https://arxiv.org/abs/2410.09047) | Representation-gap and input-presence controls precede us | A this pass; H input variants/Table 1/CMRM in historical audit |

Training-based findings may inform background. They do not satisfy this project's frozen-weight, no-training constraint or demonstrate that our input wrappers improve model-weight alignment.

## Evaluation and benign utility

| ID | Original paper | Role | Inspection |
|---|---|---|---|
| P31 | Mazeika et al., [HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal](https://arxiv.org/abs/2402.04249) | Released behaviors and evaluator infrastructure used in the current adaptation; pinned implementation details are in our protocol | A metadata; project code/protocol inspected separately |
| P32 | Souly et al., [A StrongREJECT for Empty Jailbreaks](https://arxiv.org/abs/2402.10260) | Useful harmful assistance differs from non-refusal; evaluator validation comparator | A this pass; H §§2–3/appendices in historical audit |
| P33 | Röttger et al., [XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models](https://arxiv.org/abs/2308.01263) | Text benign-control source; not automatically visual-task utility | A metadata; historical dataset use separate |

The actual visual-injection diagnostic source is the official [CyberSecEval3 visual-prompt-injection dataset](https://huggingface.co/datasets/facebook/cyberseceval3-visual-prompt-injection), pinned in [our protocol](PUBLISHED_BENCHMARK_PROTOCOL.md). It is a dataset entry, not counted as an additional paper. Do not cite the original secure-coding CyberSecEval paper as if it described this later visual release. The earlier chat's attribution of “INJECAGENT” to the physical-injection paper was also unsupported and should not enter the presentation.

## Architecture learning sequence

| ID | Original paper | Learn this to understand the attack equations | Inspection |
|---|---|---|---|
| P34 | Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Attention, token representations, forward/backward computational graphs | A; learning assignment |
| P35 | Dosovitskiy et al., [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) | Vision patch embeddings and transformer encoding | A; learning assignment |
| P36 | Radford et al., [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) | CLIP's image/text representation space; encoder-targeted attacks | A; learning assignment |
| P37 | Li et al., [BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models](https://arxiv.org/abs/2301.12597) | Q-Former-style bridging; do not assume every VLM uses it | A; learning assignment |
| P38 | Liu et al., [Visual Instruction Tuning](https://arxiv.org/abs/2304.08485) | LLaVA's visual-language interface and instruction-conditioned generation | A; learning assignment |
| P39 | Bai et al., [Qwen2.5-VL Technical Report](https://arxiv.org/abs/2502.13923) | Architecture-specific visual processing for our main target; exact checkpoint/processor still matter | A; learning assignment |
| P40 | Fu and Zhang, [Adversarial Defense in Vision-Language Models: An Overview](https://arxiv.org/abs/2601.12443) | Wider defense taxonomy; verify generative-VLM versus CLIP task applicability | A; discovery survey |

For SmolVLM, use the official [tested checkpoint card](https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct) and pinned model configuration recorded in our protocol. A model card is not counted as a paper or a substitute for auditing its actual processor and implementation.

## How to turn this catalogue into wider research

**First deep-reading batch:** P04–P07 contrast end-to-end corpus NLL, encoder-only targeting, behavior matching and multimodal feedback. P09–P10 explain the historical track. P11–P13 explain evaluation and defense architecture. These have atlas diagrams already; original runs remain separate.

**Next audit batch:** P15–P17 and P22 extend transfer and semantic visual mechanisms; P23/P26/P28 check whether visual dependence, benign utility and framing/carrier decomposition already cover proposed novelty. Promote a paper only after verifying original methods, tables, appendices and code/data access. Do not infer precise procedures from these catalogue summaries.

For each paper, complete the same record: exact version and publication; original code/checkpoint; attacker objective/access/controlled variable; mathematical loss and update; data construction/license/splits; preprocessing and decoding; sample/step/query budgets; original evaluation and result-table reference; human involvement; release defects; feasibility; and deviations in our implementation.

**Scope decision:** broad review is appropriate; executing every variant is not the same task. Rank potential reproductions by distinct mechanism, accessible native artifacts, open-model compatibility, T4 feasibility and value beyond existing benchmarks. Physical capture, poisoning/backdoors, video and actual agent actions remain separate future scopes. No synthetic replacement data or invented results are needed to document those boundaries.

This pass searched primary arXiv/ACL/publisher sources using visual jailbreak, transfer, semantic visual attacks, prompt injection, benchmarks and defenses, and reopened the listed new abstracts on October 28. It did not exhaust every venue/citation chain; papers absent from this bounded catalogue may still be highly relevant. A systematic-review claim requires an explicit search protocol, deduplication and inclusion/exclusion record.
