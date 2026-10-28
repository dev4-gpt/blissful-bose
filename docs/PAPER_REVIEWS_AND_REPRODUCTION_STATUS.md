# Original-paper reviews and reproduction record

28 October 2026. First review batch: the core foundations, VLM methods, benchmark and defense protocols. This is a focused primary-source review with experiment-specific reproduction decisions, not a completed systematic review of the [40-paper catalogue](VISUAL_ATTACK_PAPER_CATALOGUE.md). Architectures and worked common notation are in the [pipeline atlas](VISUAL_ATTACK_PIPELINE_ATLAS.md). All original experiment executions in this batch remain `NOT_RUN`.

Paper findings, release findings, our critique and our measured results are separated below. No missing original examples, scores or labels are generated. Published numbers are reference values, not our outcomes. A source checksum or syntax check does not constitute an attack reproduction.

## 1. What we are comparing

| Study | Optimization target | Access needed to construct attack | Original task | Native experiment currently executable end to end? |
|---|---|---|---|---|
| FGSM | True-class loss | Classifier gradient | Classification | No: exact original checkpoint unresolved |
| Madry/PGD | Worst-case loss within constraint | Classifier gradient | Robust classification | Not yet: choose original released model/config and recover environment |
| Brown patch | Target-class probability over transformations | Classifier/ensemble gradient | Targeted classification and physical patch | No: full original transform/data/config contract unresolved |
| Qi | Corpus sequence likelihood | End-to-end VLM gradient | Generative safety/toxicity | No: original checkpoint/environment and native evaluation unresolved |
| Jailbreak in Pieces | Trigger-representation distance | Accessible CLIP encoder | Compositional jailbreak/injection | Encoder demo prepared; whole experiment blocked by missing original contract |
| Image Hijacks | Context-dependent behavior distribution | End-to-end VLM gradient | Behavior control and prompt matching | Demo configs inspected; full experiment configs unresolved |
| BAP | Corpus image likelihood, then text feedback | Visual gradient plus feedback model | Joint image/text jailbreak | No: code defects and original closed-model dependency |

These methods cannot be ranked using published headline ASRs alone: models, targets, datasets, sampling and success definitions differ. The first reproduction goal is a particular original experiment with its original scoring. A subsequent common-benchmark comparison is a separate study.

## 2. Foundations: what transfers to VLM research and what does not

### FGSM — Goodfellow, Shlens and Szegedy

**Source:** [Explaining and Harnessing Adversarial Examples, v3, §§3–4](https://arxiv.org/html/1412.6572v3).

**Problem and method.** Small coordinate changes can produce a large aggregate change in a high-dimensional model. FGSM increases classification loss using one signed input-gradient step. The MNIST/maxout experiment is a classifier experiment.

**Math.** Linearizing gives \(L(x+\delta)\approx L(x)+\nabla_xL^\top\delta\). Under \(|\delta_j|\le\epsilon\), each contribution is maximized by \(\delta_j=\epsilon\operatorname{sign}(\partial L/\partial x_j)\). This explains the update rather than treating its sign as a memorized formula. A targeted minimization reverses direction.

**Our methodological assessment.** The update is a useful transparent VLM baseline, but changing class CE to sequence NLL changes the objective and task. An input-gradient demonstration is not a reproduction of the paper's training results. Our no-training constraint excludes reproducing its adversarial-training procedure.

**Reproduction contract.** Recover the selected original trained model, MNIST preprocessing, true-label convention, epsilon and reference result. Freeze weights; calculate the original loss gradient; deliver bounded images; measure clean/attacked classification error on original test IDs. We have not recovered an exact original maxout checkpoint. No new classifier training or substitute checkpoint is used to hide that gap. **Our result: NOT_RUN.**

### PGD — Madry, Makelov, Schmidt, Tsipras and Vladu

**Source:** [Towards Deep Learning Models Resistant to Adversarial Attacks, v4, §§2,5](https://arxiv.org/html/1706.06083v4). [Pinned MNIST release](https://github.com/MadryLab/mnist_challenge/tree/3ee3643c4a8c59458d8c191b84027f4a6cbd9580), [CIFAR-10 release](https://github.com/MadryLab/cifar10_challenge/tree/f15682d9f1e26eb47a2d3b371ef8b6c7abcf6276).

**Method.** The paper formulates robust training as \(\min_\theta\mathbb E\max_{\delta\in S} L(\theta,x+\delta,y)\). PGD approximately solves the constrained inner search; evaluating released trained weights does not require retraining.

**Math and architecture.** \(x^{k+1}=\Pi_{x_0+S}(x^k+\alpha\operatorname{sign}\nabla_xL)\), including valid pixel bounds. Projection prevents cumulative updates escaping the threat model. A random start searches a different initial point; additional restarts and alternative losses are separate evaluation choices.

**Release evidence.** The inspected CIFAR configuration uses epsilon 8, step 2, ten steps and random start in its pixel scale. The MNIST configuration uses 0.3, 0.01 and 40 steps. These release defaults are not automatically every paper-table attack. Code-source identities are recorded in [the audit](VISUAL_PAPER_REPRODUCTION_AUDIT.md).

**Our assessment.** This is a promising foundation reproduction if the original released pretrained model and compatible inference environment can be recovered. Report classifier accuracy, not VLM jailbreak ASR. A changed architecture or newly trained model would not reproduce the selected original checkpoint experiment. **Our result: NOT_RUN.**

### Adversarial Patch — Brown, Mané, Roy, Abadi and Gilmer

**Source:** [Adversarial Patch, v2, §§2–3, Eq.1](https://arxiv.org/html/1712.09665v2).

**Method and original setting.** One replacement patch is optimized across image backgrounds and transformations for targeted ImageNet classification, including ensemble/transfer and separate physical evidence.

**Math.** \(p^*=\arg\max_p\mathbb E_{x,t,\ell}\log P(y^*\mid A(p,x,t,\ell))\). Here \(p\) is the optimized patch, \(x\) the background, \(t\) a transform, \(\ell\) placement and \(A\) composition. Universality concerns the distribution over which this same artifact works.

**Our assessment.** Norm-bounded local perturbations and box-only replacement patches use different budgets. A single carrier and a finite transform set do not reproduce cross-scene or physical generalization. Our replacement-EOT helper is consequently an adaptation.

**Reproduction contract.** Select one original single/ensemble/transfer condition, recover its classifier(s), image selection, transform/placement distribution, patch support and evaluation scale. Optimize only the patch; evaluate on held-out original backgrounds; reproduce capture conditions only for a physical claim. Full original artifacts/configuration are unresolved. **Our result: NOT_RUN.**

## 3. Qi et al.: corpus likelihood through the complete VLM

**Identity:** Xiangyu Qi, Kaixuan Huang, Ashwinee Panda, Peter Henderson, Mengdi Wang and Prateek Mittal. [Visual Adversarial Examples Jailbreak Aligned Large Language Models, v2](https://arxiv.org/html/2306.13213v2), §§3–4, Appendix A. [Official pinned release](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models/tree/5fc9883cfa9b4183cf05c6eceef49e449e45e9c9).

**Research question.** Can a visual artifact optimized against an aligned VLM encourage harmful generation beyond the optimization corpus?

**Construction versus testing.** The optimization corpus supplies target continuations; manual requests and RealToxicityPrompts supply different evaluations. Those roles must remain separate. The image is shared; gradients traverse the encoder, multimodal interface and decoder. Model weights stay fixed.

**Objective.** Minimize corpus NLL, \(J(x)=-|Y|^{-1}\sum_{y\in Y}\log p_\theta(y\mid x)\), under the chosen constraint. Target likelihood is a construction surrogate; it does not label generated outputs as harmful.

**Original result anchor, not ours.** Table 1's identity-attack rates are **26.2** for the benign image and **61.5** for the 16/255 image, in percent. Its human experiment samples ten outputs per instruction using nucleus p=0.9 and temperature=1 (§4.2). The toxicity evaluation uses a different endpoint (§4.3).

**Release audit and exact rerun.** The MiniGPT entrypoint's actual parser uses underscore flags. Its call hardcodes 5000 iterations/batch eight; the attacker loop is inclusive, so nominal iterations and effective updates differ. The released processor uses 224 pixels. These are pinned-source findings, not assumptions about modern Qwen preprocessing.

**Our critique.** A fixed artifact reused across requests creates dependence. Toxicity, relevant unsafe assistance and refusal cannot be substituted for one another. Current checkpoint substitutions can test portability but cannot be retroactively called native replication.

**Required attempt:** original supported checkpoint → released image/corpus → original objective/budget → saved artifact → native request/sampling protocol → original human/toxicity scoring → selected table comparison. No new replacement corpus. Exact weight availability, memory and service-compatible evaluation remain unresolved. Our earlier eight-request Qwen/Smol panel is an adaptation. **Native result: NOT_RUN.**

## 4. Jailbreak in Pieces: encoder targeting plus behavioral testing

**Identity:** Erfan Shayegani, Yue Dong and Nael Abu-Ghazaleh. [Jailbreak in pieces: Compositional Adversarial Attacks on Multi-Modal Language Models, v2](https://arxiv.org/html/2307.14539v2), §3, Eq.3–4/Algorithm 1, §4 and Appendix H. [Official pinned release](https://github.com/erfanshayegani/Jailbreak-In-Pieces/tree/b7b2bce812adada23f583f63f63e564f84d277c6).

**Method.** Construct a target embedding from text, OCR, a visual image or combined visual/OCR content. Optimize an input image toward it using CLIP access, then assess the compositional VLM response with the original text context. The loss is representation distance, not generative NLL.

**Paper result anchor, not ours.** Table 1 reports LLaVA averages **0.007**, **0.849**, **0.849**, **0.870** for textual, OCR, visual and combined triggers. Its main design specifies 6400 generations (§4). These numbers are native-protocol references, not expected outcomes of our current deployment.

**Actual release evidence.** The pinned tree has 15 files: source/README/license, selected inputs and output examples. It does not provide a verified complete main-study manifest. The visual demo uses CLIP ViT-L/14-336, unnormalized image preprocessing, Adam 0.1, a fixed 5000-update loop, clamping and JPEG delivery. The paper uses a convergence description. The later README's model example must not silently define the historical checkpoint.

**Our critique.** Small embedding distance is an intermediate criterion, not proof that a VLM cannot distinguish inputs or that unsafe assistance follows. Decoder context and delivered-image processing still matter. Appendix H's task-fulfillment rubric is more specific than mere non-refusal.

**Required attempt:** original trigger and initialization → selected original optimization branch → delivery/reload → original-compatible VLM and released prompt → original sampling → human/evaluation protocol → per-trigger result comparison. Full original data/checkpoint identities remain unresolved. The [prepared notebook](../notebooks/vlm_jip_free_t4.ipynb) includes an encoder prerequisite and explicit whole-paper blockers. **Native result: NOT_RUN.**

## 5. Image Hijacks: match behavior over contexts

**Identity:** Luke Bailey, Euan Ong, Stuart Russell and Scott Emmons. [Image Hijacks: Adversarial Images can Control Generative Models at Runtime, v4](https://arxiv.org/html/2309.00236v4), §§2–4 and Appendix C. [Official pinned release](https://github.com/euanong/image-hijacks/tree/2a4403cf67e8578afdd6e56096ff31524aaa63e7).

**Method.** The target is a function of input context, rather than one fixed answer. Behavior matching minimizes teacher-forced CE against that function. Prompt matching obtains the target distribution from a model conditioned on the selected instruction, and matches it across contexts.

**Mathematics.** \(\min_x\sum_{c\in C}\mathcal L(M_\phi^{\rm force}(x,c,B(c)),B(c))\). For prompt matching, \(B_p(c)=M_\phi(I,p\Vert c)\). Matching a teacher's token distributions preserves more behavior information than optimizing one continuation.

**Original experiment roles.** Alpaca contexts and AdvBench are task-specific. Specific-string, context-formatting, jailbreak and disinformation results have different criteria and constraints. The paper's patch settings in other tasks do not establish a patch-jailbreak result.

**Original result extraction status.** Method and experimental setup inspected; no numeric row is copied here until its task, constraint, split and scoring are checked together. This is an explicit remaining review item, not a fabricated result placeholder.

**Release audit.** The demo config contains string/leak-context jobs and its own dataset mixture/splits. A full-results configuration referenced in the README was absent from the inspected tree; jailbreak configurations were described as forthcoming. A demo's validation counts cannot stand in for the paper's table setup.

**Our critique and rerun target.** First recover one complete released behavior experiment, then its original checkpoint, contexts, teacher targets, optimization/selection and held-out evaluator. Reproduce that task before expanding to other branches. Evaluate leak-format text without sending data or invoking tools. **Native result: NOT_RUN.**

## 6. BAP: visual optimization followed by text feedback

**Identity:** Zonghao Ying, Aishan Liu, Tianyuan Zhang, Zhengmin Yu, Siyuan Liang, Xianglong Liu and Dacheng Tao. [Jailbreak Vision Language Models via Bi-Modal Adversarial Prompt, v2](https://arxiv.org/html/2406.04031v2), §§4–5 and Appendices A,D. [Official pinned release](https://github.com/NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt/tree/5350c0bfeb01d9e485603b85a03500280886d275).

**Method.** A query-agnostic visual stage is followed by intent-specific text refinement based on failed responses and an LLM judge. It is not a fixed prompt bank and not joint gradient descent over text tokens and pixels.

**Mathematics.** The visual stage minimizes corpus NLL. The text stage uses a discrete feedback operator \(q_{i+1}=R(q_{\rm intent},q_i,r_i)\), with judge/stop rules controlling selection. Original image and text budgets are separate.

**Native setup.** §5.1 uses LLaVA-1.5-7B, MiniGPT-4/Vicuna-7B and InstructBLIP/Vicuna-7B. SafetyBench scenarios are merged with deduplicated AdvBench items. The original feedback implementation uses ChatGPT. Exact merged inputs are part of reproduction, not an interchangeable benchmark label.

**Selected published result, not ours.** Table 1 reports MiniGPT4 illegal-activity **2.13** under No Attack and **59.04** under BAP, in percent. These are not matched to our eight-request HarmBench experiment and must not be compared as if they share a denominator/protocol.

**Release evidence.** The visual call uses 3000 updates, batch two, epsilon32/255 and alpha1/255. Syntax checks fail for `CoT.py` at line58 and `Eval.py` at line138 in the pinned source. Preserve the defects and record any repair as a source change. No original unmodified runnable full pipeline is established.

**Our critique and rerun target.** Recover the exact corpus/merged split and feedback settings; separately validate any source repair. Replacing the closed feedback model or judge changes the scientific method. Under open-only/no-paid-resource constraints, an open feedback version is an adaptation requiring its own protocol. **Native result: NOT_RUN.**

## 7. Reproduction decisions after this review batch

| Candidate | Concrete next operation | Evidence required to proceed | Expected label until reviewed |
|---|---|---|---|
| JIP released encoder example | Execute inspected original-compatible encoder procedure and preserve artifacts | Approved free-resource path, frozen source/model/input identities and measured budget | Component/release reproduction candidate; not whole paper |
| JIP main result | Recover complete original main-study contract | Scenario/trigger/prompt manifest, exact target models/sampling and human scoring | Blocked; cannot fill with synthetic inputs |
| Qi selected original experiment | Recover supported checkpoint and native evaluator | Original weight/processor/data identities, memory profile and scoring availability | Blocked until verified |
| Image Hijacks released demo | Select one available complete behavior task | Task-specific source/checkpoint/context/evaluator contract | Release/demo reproduction; not all paper branches |
| PGD challenge evaluation | Recover official pretrained checkpoint and environment | Native model/data/configuration and reference comparison | Selected classifier experiment; no VLM safety claim |
| BAP full method | Resolve source defects, original merged data and feedback dependency | Native runnable code/config and permitted feedback service | Blocked under current open-only constraints |

The next scientific result should be an actual executed, preserved method/evaluation record. Adding more wrappers or printing a readiness dictionary does not satisfy that milestone. The owner authorized the existing college Colab T4 allocation without purchases. The first bounded encoder attempt is being prepared; it does not complete the whole paper.

## 8. Typographic, physical and defense papers

### FigStep — Gong et al.

**Source:** [FigStep, v3, §§5–6 and Appendix C](https://arxiv.org/html/2311.05608v3). The procedure combines a rendered instruction/list with a text completion wrapper. SafeBench supplies the evaluation collection; SafeBench-Tiny supplies the ablation subset. No gradient computation is necessary.

**Important original result:** Table 2 reports LLaVA **60.00%** for the all-text Q2-prime control and **92.00%** for FigStep. This is an original ablation, not our observation. Both content and framing belong in the contract; merely comparing a generic text question with a wrapped image changes multiple factors.

**Our assessment.** The paper already contains the all-text control and discusses comprehension limitations. Replicating those controls on changed checkpoints is useful, but not an invention. Refusal-only labels cannot substitute for the original safety rubric.

**Reproduction target:** recover the native SafeBench-Tiny ablation items, original model identity, renderer/font/size, wrapper, decoding and scoring; rerun its exact conditions, then compare Table 2. Paper version matters. The existing historical study does not automatically fill this native table. **Native result: NOT_RUN.**

### MM-SafetyBench — Liu et al.

**Source:** [MM-SafetyBench, v2, §§2–3](https://arxiv.org/html/2311.17600v2). The method distributes safety-relevant content across query text, semantic imagery and typography, with separate and combined image conditions. Its dataset construction and result conditions must be identified from the exact release.

**Architecture and evaluation.** Image content reaches the visual encoder while the accompanying query enters the decoder context. Semantic scene information and readable text are different carriers. ASR and refusal are explicitly separate metrics in the paper; the safety-prompt experiment is a further condition.

**Our assessment.** Using a TYPO subset does not test the generated-scene or combined branches. A plain carrier paired with a harmful question does not test reasoning about the scene. The selected risk scenarios, image construction and prompt transformations must remain traceable.

**Reproduction target:** one released native image condition with original IDs/checkpoint/prompt/decoding and original scoring, alongside its native baseline. Then expand conditions. Native full-table numeric extraction and release-level split/license audit remain open here. **Native result: NOT_RUN.**

### Physical Prompt Injection — Ling et al.

**Source:** [Physical Prompt Injection Attacks on Large Vision–Language Models, v1, §§III–VI](https://arxiv.org/html/2601.17383v1). The attack selects visual instructions and scene placement under a black-box/query-agnostic threat model. Simulation and physical capture have distinct experimental evidence.

**Procedure and data.** Prompt selection → location search → rendered/captured scene → legitimate VLM task → unauthorized-deviation scoring. Embodied City, Habitat and vehicle/camera experiments cannot be replaced by digital marker examples while retaining the native label.

**Release finding.** The [pinned official README](https://github.com/2023cghacker/Physical-Prompt-Injection-Attack/blob/7291d92ee05c4b9079ef824e0b4bd12e8e14316c/README.md) says the code is being organized and is not fully runnable. Scene/capture artifacts and exact experiment settings are unresolved. No full physical replay is planned on a Colab-only setup.

**Our assessment.** This paper broadens the threat model and should be reviewed even if reproduction is resource-blocked. OCR readability, attack placement, task correctness and physical robustness require distinct checks. **Native result: NOT_RUN; physical experiment outside the initial execution scope.**

### MMJ-Bench — Weng et al.

**Source:** [AAAI 2025 original paper, setup and Tables 3–4](https://ojs.aaai.org/index.php/AAAI/article/download/34983/37138). This is the comparison framework connecting attacks, target VLMs, defenses, safety evaluation and benign utility. It is not an additional input-optimization algorithm.

**Data and scoring roles.** HarmBench supports behavior evaluation and MM-Vet supports useful-task evaluation. Original open-classifier and closed-model judgments must remain separate. A common benchmark changes some original attack protocols intentionally; that is why native reproduction and matched comparison need two tables.

**Reproduction target:** select one completely recoverable attack/model/defense row, recover released generation and scoring settings, run the original cases and separately measure utility. Do not count repeated controls or method variants as independent behaviors. Full native row-level protocol and numeric extraction remain open. **Native result: NOT_RUN.**

### AdaShield — Wang et al.

**Source:** [AdaShield, v1, §§3–4 and Appendix A](https://arxiv.org/html/2403.09513v1). AdaShield-S uses the original static prompt. AdaShield-A uses target responses and defender refinement to construct a prompt pool, then retrieves a suitable defense for incoming queries. Model weights remain fixed; prompt-pool development still requires its own split.

**Data and architectural position.** The defense changes instruction context before generation. FigStep/QR attack inputs and MM-Vet benign utility have different roles. A generic safety prefix does not instantiate the released static prompt or adaptive retrieval system.

**Our assessment.** Defense strength must be evaluated with over-refusal, task completion, refinement/query costs and defense-aware attacks. Original closed-model-dependent steps conflict with the open-only project constraint if reproduced literally.

**Reproduction target:** start with a verified static-variant row and its native utility control, then consider the adaptive pool once original artifacts/dependencies are audited. No numerical defense effect is imported from an unmatched model/protocol. **Native result: NOT_RUN.**

### JailGuard — Zhang et al.

**Source:** [JailGuard, v4, §§4–6](https://arxiv.org/html/2312.10766v4). Generate configured input mutations, obtain multiple target responses, embed them and apply the original divergence/threshold policy. It is repeated-inference detection, not simply a transformed-image classifier.

**Concrete visual mechanisms.** The paper's image mutators include geometric, regional and photometric operations. Mutation strength can also damage benign input meaning, so response variation alone needs a calibrated decision rule and false-positive evaluation. The exact mutation distribution, combination policy, number of variants, response encoder and threshold are part of the method.

**Our assessment and rerun target.** Recover one complete visual condition from the official attack/benign release; hold its development and evaluation portions separate; run the native target, response comparison and detector. Report detection metrics, accepted-input task outcomes and query cost separately. Our flip-aware PGD is not this defense. Native full estimator/configuration and result-table extraction remain unfinished. **Native result: NOT_RUN.**

### Vision-attack survey — Zhang et al.

**Source:** [Adversarial Attacks of Vision Tasks in the Past 10 Years: A Survey, v2](https://arxiv.org/html/2410.23687v2), selected taxonomy sections. Its contribution is organization and synthesis across traditional vision and LVLM attacks. It supports discovery and mechanism comparisons, but another paper's original dataset, hyperparameters and result tables still require direct verification. **There is no standalone survey attack experiment to reproduce.**

## 9. Status and remaining review work

**Completed in this batch:** focused primary-method reviews, selected original result anchors, computational distinctions, pinned release findings and experiment-specific reproduction decisions. Paper results above are attributed to their original sections/tables. They are not our reproduced results.

**Not completed:** full-table/appendix audit for every paper, original checkpoint/environment recovery, new GPU execution, complete native ASR evaluation or independent human review. The [existing measured adaptations](PUBLISHED_BENCHMARK_RESULTS.md) remain a different evidence lane.

Next depth pass: finish complete table/appendix/configuration audits for the focused reviews above, then promote AttackVLM/imgJP/HADES and newer semantic attacks from discovery into original-method reviews. Newly catalogued abstracts must be checked against full text and source before implementation details are imported.

Public exports remain code, reviewed source identifiers and aggregates only. Prompts, image stimuli, optimized artifacts, model replies and annotations remain private. The project continues with no model training, no fabricated test data and no paid-GPU purchase.

## Execution handoff — 28 October 2026

A distinct college-Drive notebook was saved as [JIP_20261028_REPRODUCTION_REVIEW_PENDING.ipynb](https://colab.research.google.com/drive/14CvxKLpOJuhxK-UN9In9am8UBVwx6qpn?authuser=2). The owner subsequently authorized the existing T4 allocation without purchases. Its encoder run is a component attempt under Amendment 13; full-paper ASR remains NOT_RUN. Record completion/failure and archive identity here after actual execution.

Additional source recovery: official MNIST pretrained archives exist at model-repository revision `fc50473cb7d2550cc5f5c9fadf47d171ac66d7b4`; `adv_trained.zip` has Git blob `5522769558a570818f3e79bf465dd7f094f5783a`, 21186578 bytes. This is repository metadata, not a downloaded/validated checkpoint or a reproduced model result. Exact challenge-to-paper table correspondence and legacy inference environment still need verification.

Execution update: Run all was started in the separate Drive copy. It is waiting for the owner-only Drive mount authorization before installation/model download or the scientific attempt clock. No encoder or native-paper ASR result exists yet. NotebookLM analysis brief: [requirements and source list](NOTEBOOKLM_VLM_RESEARCH_BRIEF.md).

Mount recovery: the initial mount failed; retrying only that cell succeeded (`Mounted at /content/drive`). Browser control was then disabled in Work settings before remaining cells could be verified. No new encoder result or ASR is reported; inspect the live/persistent state before continuing.

Verified launch update: the college-Drive attempt clock started at 2026-10-28 16:45:47 America/New_York, deadline 17:45:47. Its private identity records Tesla T4 and CLIP revision `ce19dc912ca5cd21c8a653c79e251e808ccabcd1`. Setup/model loading is in progress; no completed optimizer result or downstream ASR is inferred. The recovered source/hash cells preceded the bounded driver; an earlier missing-variable error occurred before its clock.

Measured encoder profile (private `profile_50/status_PRIVATE.json`): 50 updates completed; initial distance `18.397844314575195`, final tensor distance `8.296499252319336`, JPEG-reloaded distance `14.841279029846191`; elapsed `13.302191429000004` seconds. These values describe one released example and one component, not safety ASR. The driver created the distinct `release_5000` stage; its completion remains unverified.

## Completed encoder component: 28 October 2026

The saved controller reports `encoder_process_complete_requires_review`; 5000/5000 updates completed. This is a disclosed reimplementation of the released visual encoder example, not the whole paper or a native ASR reproduction.

| Stage | Initial feature distance | Final tensor distance | JPEG reload distance | Optimization seconds |
|---|---:|---:|---:|---:|
| Profile, 50 updates | 18.397844314575195 | 8.296499252319336 | 14.841279029846191 | 13.302191429000004 |
| Separate release-length, 5000 updates | 18.397844314575195 | 0.6099005937576294 | 15.424763679504395 | 1507.081493692 |

Frozen weights matched before/after. Peak allocated memory was 2571547136 bytes. Controller elapsed time including setup was 1596.6343314647675 seconds. These are saved engineering measurements on the released example, not independent samples, human semantic equivalence or unsafe-assistance ASR.

The optimized tensor improved the chosen embedding objective, but the delivered JPEG lost much of that improvement. This delivery discrepancy must be diagnosed before any downstream behavioral claim. Neither the final tensor nor JPEG establishes the paper's convergence/behavior results. No new optimizer attempt is authorized by reading these results.

Private archive: 389414 bytes; SHA256 `c440f749e57f7d907f418e28ffb0f877b1b2d466ac233f6256550b5fde9388ed`, verified against the actual locally visible Drive archive. Native downstream ASR remains NOT_MEASURED. The driver now redisplays an existing summary on rerun without deleting its clock or launching a duplicate process.
