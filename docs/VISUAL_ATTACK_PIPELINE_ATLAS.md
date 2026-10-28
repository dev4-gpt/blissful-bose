# Visual attacks: structural and architectural atlas

28 October 2026. Presentation and research-design document. Scope: the registered core papers, the historical typographic experiments and the implemented published-data panel. This is a bounded map, not a claim to cover every published attack. [Paper catalogue](VISUAL_ATTACK_PAPER_CATALOGUE.md) separates source inspection from discovery; [reproduction audit](VISUAL_PAPER_REPRODUCTION_AUDIT.md) records pinned-code obstacles.

**Main finding of this structural analysis:** attacks differ along independent axes: the variable they control, the objective they optimize, the model access they require, the constraint they obey and the behavior used to judge success. FGSM/PGD describe update rules; “patch” describes spatial support; “universal” describes sharing; EOT describes an expectation over transformations. These are composable properties, not mutually exclusive attacks.

No new experimental data, samples or outcomes were generated for this document. Original-paper reproductions remain `NOT_RUN`; earlier completed adaptations remain development evidence. Mechanistic explanations below describe computational paths, not experimentally established causal explanations of unsafe behavior.

## 1. The shared architecture

![Frozen VLM and attack interfaces](../presentation/vlm_attack_architecture.png)

```mermaid
flowchart LR
  A[Attacker controls image pixels or visible content] --> X[Delivered image x]
  X --> P[Preprocess P: decode resize normalize layout]
  P --> E[Vision encoder E: visual features]
  E --> C[Connector C: language-compatible tokens]
  C --> D[Language decoder D: autoregressive generation]
  Q[User task and text prompt q] --> D
  S[System instructions and optional defense prefix] --> D
  D --> R[Generated response r]
  R --> J[Independent task and safety evaluation]
  D -. generative loss gradient .-> O[Input optimizer: model weights frozen]
  E -. encoder-only loss gradient .-> O
  O -. changes pixels only .-> X
```

Write the architecture as \(v=C(E(P(x)))\), \(p_\theta(y\mid x,q)=\prod_t p_\theta(y_t\mid y_{<t},v,q)\). Here \(x\) is the delivered image, \(q\) the text context, \(v\) visual tokens and \(\theta\) all fixed model weights. This abstraction permits different encoders and connectors; it does not assert identical implementations.

| Component | What to learn | Structural consequence for attacks |
|---|---|---|
| Preprocessing | Raw pixels, resizing/cropping, normalization, token layout | The constraint must survive the actual delivery path. A valid pre-save perturbation can change after quantization or resizing. |
| ViT / vision encoder | Patch embeddings, position, attention, feature representations | Input pixels influence many feature tokens; encoder loss can be optimized without decoder access. A ViT patch token is different from an adversarial patch. |
| Connector | Projection/merger, resampling, Q-Former in applicable models | It changes which visual information the decoder receives. CLIP feature similarity alone does not guarantee identical decoder behavior. |
| Decoder | Token embeddings, causal attention, teacher forcing, generation | Target-sequence likelihood and actual free generation are different measurements. |
| Instruction handling | System/user context versus content depicted in an image | Reading image text is useful; treating it as an authoritative instruction can violate the legitimate task. |
| Evaluator | Safety rubric, task correctness, refusal, comprehension | A loss decrease, refusal decrease, exact marker and unsafe assistance answer different questions. |

Our Qwen2.5-VL and SmolVLM implementations use different model/processor paths. The adapters are [Qwen](../tools/vlm_visual_adapter.py) and [SmolVLM](../tools/vlm_visual_smol_adapter.py). Original papers also use LLaVA, MiniGPT-4 and InstructBLIP variants. Replacing one with another changes the experiment, even if this abstract diagram remains valid.

### From pixels to attention: the architectural mathematics

A simplified ViT forms a token from each image block: \(h_j^0=W_{\rm patch}\operatorname{vec}(b_j)+e_j\), where \(b_j\) is a pixel block and \(e_j\) its position representation. Self-attention computes \(\operatorname{softmax}(QK^\top/\sqrt{d_k})V\). This explains how a local pixel change can affect representations beyond its original spatial block after attention. It does **not** establish that attention spread causes a safety failure. Architectural details differ across encoders; this is a teaching abstraction, not a claim about identical Qwen/Smol internals. Background: [ViT](https://arxiv.org/abs/2010.11929), [Transformer](https://arxiv.org/abs/1706.03762).

The connector may implement a learned projection \(v_j=W_c h_j\), token merging or a query/resampling mechanism. It makes visual features consumable by the language model. A matching visual-encoder vector is therefore only an intermediate target: preprocessing, connector, text context and decoder can all change downstream behavior. This is why encoder-targeting needs a second behavioral evaluation stage.

During generation, visual and textual representations condition the token distribution. The model can use depicted text as information or follow it as an instruction. The computational graph alone does not contain a proof that image content will retain the correct authority level. A trust-boundary evaluation must specify the legitimate task and the unauthorized deviation; OCR success alone cannot diagnose either safety or injection failure.

| Architectural observation | Mechanistic possibility | Evidence needed before a causal claim |
|---|---|---|
| Gradient reaches image | The chosen loss is sensitive to the input under this adapter | Finite differences/direction checks, processor parity and actual generated behavior |
| Encoder distance falls | Surrogate representation moves toward a target | Held-out downstream tasks, matched triggers, controls and transfer evaluation |
| One mask affects many token features | Local perturbations propagate through attention | Controlled spatial/token interventions; observed ASR alone cannot localize the vulnerable block |
| Prefix changes responses | Text context changes the operating behavior | Benign utility, paired safety labels, defense-aware attacks and human review |
| Image presence changes refusal | Multimodal processing changes behavior under this condition | Blank/noise/semantic controls and matched wording; no automatic evidence of a shared safety resource |

These are research-analysis requirements, not newly observed internal-model findings. The earlier see-saw hypothesis is not established by the project data.

## 2. Threat model: entry point versus optimization path

| Family | Attacker changes | Access during construction | Gradient ends at | Deployment entry point |
|---|---|---|---|---|
| Full-image gradient | Pixels under a norm bound | Differentiable target or surrogate | Decoder sequence loss | Image input |
| Localized gradient | Pixels inside a mask | Differentiable target or surrogate | Decoder or classifier loss | Image input |
| Encoder matching | Pixels | Accessible encoder and target representation | Encoder-distance loss | Image input |
| Behavior/prompt matching | Pixels shared across contexts | Differentiable VLM and behavior target/teacher | Output distribution loss | Image input |
| Typography / visual injection | Visible instructions, layout, scene content | Often black-box; gradients optional | No gradient required | Image/scene input |
| Bimodal search | Both image and text | Visual gradients plus text feedback in the original method | Two coordinated objectives | Image and text inputs |
| Physical injection | Physical object/content and position | Observation/query-based selection | No white-box gradient required | Camera capture |

For a differentiable end-to-end objective, the chain rule gives \(\nabla_x L=J_P^\top J_E^\top J_C^\top\nabla_v L\), with the decoder contained in \(\nabla_v L\). Encoder targeting instead uses \(J_P^\top J_E^\top\nabla_e L_E\). These equations identify dependencies; they do not imply that an attacker edits the connector or decoder weights.

“Black-box transfer” means construction on an accessible surrogate and evaluation on another target. It differs from a black-box query attack that searches directly using target responses. Universal across requests, across carrier images, across models and across physical conditions are four different generalization claims.

## 3. Common mathematical contract

The following notation is explanatory and harmonized across methods; it is not a verbatim transcription of every paper's symbols.

For a reference image \(x_0\in[0,1]^{3\times H\times W}\), define \(\mathcal C=\{x:0\le x\le1,\|x-x_0\|_\infty\le\epsilon\}\). Projection \(\Pi_{\mathcal C}\) enforces both constraints. With mask \(M\), also require \((1-M)\odot(x-x_0)=0\).

For a released target continuation \(y^*\), a generative objective is \(L_{\rm seq}(x,q,y^*)=-\sum_t\log p_\theta(y_t^*\mid y_{<t}^*,x,q)\), or the adapter's mean over scored target tokens. State the reduction and label masking explicitly; do not compare loss magnitudes across different token lengths/models as if calibrated.

Teacher forcing supplies the target prefix during optimization. Evaluation generates without that prefix. Therefore lower target NLL is an optimizer diagnostic, not ASR. The harmful target remains private; equations need no public payload example.

| Axis | Alternatives | Why it changes the comparison |
|---|---|---|
| Goal | Untargeted error; specified target; unsafe assistance; task deviation | A classification error is not a jailbreak. |
| Objective | Classification CE; sequence NLL; embedding distance; teacher distribution | Equal update counts do not imply equal objectives. |
| Support | Whole image; bounded local region; replacement patch | Patch area and pixel amplitude are separate budgets. |
| Sharing | One artifact per case; shared artifact over development contexts | Shared artifacts create statistical dependencies. |
| Transform distribution | Identity; flip pair; finite placements; physical capture | Digital augmentation alone establishes no physical robustness. |
| Knowledge | White-box; encoder-only; surrogate transfer; query access | The resources and possible failure modes differ. |

## 4. Paper-by-paper computational diagrams

Each diagram is our explanatory redraw, not a copied paper figure. “Reviewed” means the cited sections and selected sources were inspected; it does not mean every result/appendix has been independently audited. These diagrams show method structure, not executed original-paper experiments.

### 4.1 Goodfellow et al. — FGSM

```mermaid
flowchart LR
 X[Clean image and true label] --> F[Frozen classifier]
 F --> L[Classification loss]
 L -. gradient to pixels .-> S[Signed one-step update]
 S --> A[Projected adversarial image]
 A --> V[Evaluate classifier error]
```

Original mechanism: maximize true-label classification loss using \(x'=\Pi_{\mathcal C}(x_0+\epsilon\operatorname{sign}\nabla_xL)\). The first-order expansion \(L(x_0+\delta)\approx L(x_0)+\delta^\top\nabla L\) yields the sign solution under an infinity-norm box. Our targeted sequence-loss adaptation uses the **minus** sign to minimize NLL. Source: [Goodfellow, Shlens and Szegedy, §§3–4](https://arxiv.org/html/1412.6572v3). Native MNIST/maxout evaluation does not establish VLM safety. Ours: completed targeted adaptation; no original checkpoint reproduction.

### 4.2 Madry et al. — PGD

```mermaid
flowchart LR
 X[Reference image and constraint] --> I[Initialize inside allowed region]
 I --> F[Frozen model and chosen loss]
 F -. input gradient .-> U[Signed step then project]
 U --> F
 U --> A[Selected constrained image]
 A --> V[Independent generation and scoring]
```

For targeted minimization, \(x^{k+1}=\Pi_{\mathcal C}(x^k-\alpha\operatorname{sign}\nabla_xL_{\rm seq}(x^k))\). Random starts and restarts search different parts of the feasible region. The original robust objective \(\min_\theta\mathbb E[\max_{\delta\in S}L(\theta,x+\delta,y)]\) contains an outer weight-training loop; our scope uses only input optimization. Native MNIST/CIFAR-10 classifiers and our VLM sequence targets are different tasks. Source: [Madry et al., §§2,5](https://arxiv.org/html/1706.06083v4). Ours: completed adaptation, selected by optimization loss rather than held-out judge outcomes.

### 4.3 Brown et al. — universal replacement patch

```mermaid
flowchart LR
 P[Shared patch variable] --> A[Compose with background and transform]
 X[Development images and locations] --> A
 A --> F[Frozen classifier or ensemble]
 F --> L[Target-class objective]
 L -. update patch .-> P
 P --> V[Held-out images and separate physical tests]
```

The native objective is \(\max_p\mathbb E_{x,t,\ell}\log P(y^*\mid A(p,x,\ell,t))\), where \(A\) places/transforms the patch. A replacement patch permits large pixel changes within its area; a bounded additive patch additionally limits amplitude. Native ImageNet classification, ensembles, transfer and physical evidence are distinct conditions. Source: [Brown et al., §§2–3, Eq.1](https://arxiv.org/html/1712.09665v2). Our bounded local patch and finite-transform replacement patch are adaptations; neither reproduces the original physical experiment.

### 4.4 Qi et al. — corpus-driven visual adversarial examples

```mermaid
flowchart LR
 C[Released optimization corpus] --> L[Mean target-sequence NLL]
 X[Shared adversarial image] --> V[Original frozen VLM]
 V --> L
 L -. image gradient and projection .-> X
 X --> H[Separate requests and toxicity evaluation]
```

A shared image minimizes corpus continuation NLL, \(\min_{x\in\mathcal C}|\mathcal D|^{-1}\sum_{y\in\mathcal D}L_{\rm seq}(x,q,y)\). Native MiniGPT-4, InstructBLIP and LLaVA variants are evaluated with manual requests and RealToxicityPrompts; optimization corpus and evaluation prompts have different roles. Toxicity scoring and human harmfulness judgments are different endpoints. Source: [Qi et al., §§3–4; Appendix A](https://arxiv.org/html/2306.13213v2). Our short shared-image optimization and released-artifact transfer use changed checkpoints/budgets/evaluation: adaptations, not native reproduction.

### 4.5 Shayegani et al. — Jailbreak in Pieces

```mermaid
flowchart LR
 T[Released text OCR visual or combined trigger] --> Z[Target encoder representation]
 X[Optimized image] --> E[Accessible CLIP encoder]
 E --> L[Representation-distance loss]
 Z --> L
 L -. Adam updates pixels .-> X
 X --> V[Downstream VLM plus text context]
 V --> H[Behavioral evaluation]
```

The structural objective is \(\min_x\|E(P(x))-z_{\rm trigger}\|_2\), with target construction depending on the trigger variant. Decoder gradients are unnecessary, but downstream success still requires testing. The paper's scenario/trigger collection and supplementary AdvBench evaluation are not equivalent to generic HarmBench carriers. Source: [Shayegani, Dong and Abu-Ghazaleh, §§3–4; Algorithm 1](https://arxiv.org/html/2307.14539v2). Released fixed-loop code differs from the paper's convergence description. Ours: reviewed; no measured original trigger-matching result. Encoder closeness alone cannot establish semantic identity or unsafe behavior.

### 4.6 Bailey et al. — Image Hijacks

```mermaid
flowchart LR
 C[Development contexts] --> B[Behavior target or teacher distribution]
 C --> V[Frozen VLM with optimized image]
 X[Shared image variable] --> V
 B --> L[Behavior-matching loss]
 V --> L
 L -. image optimization .-> X
 X --> H[Held-out contexts and task-specific scoring]
```

Behavior matching minimizes expected loss against a specified behavior over contexts. Prompt matching uses a teacher distribution conditioned on a target text prompt: an explanatory form is \(\mathbb E_c H(p_{\rm teacher}(\cdot\mid c),p_\theta(\cdot\mid x,c))\). This is richer than one fixed continuation. Original tasks include specific strings, context-leak formatting, jailbreak behavior and disinformation; Alpaca contexts and AdvBench are task-dependent. Source: [Bailey et al., §§2–4; Appendix C](https://arxiv.org/html/2309.00236v4). Constraints differ by experiment; the paper does not establish patch jailbreaks merely because other tasks use patches. Ours: not reproduced; no actual tool action or data transmission is needed to evaluate output formatting.

### 4.7 Ying et al. — BAP

```mermaid
flowchart LR
 C[Query-agnostic corpus] --> O[Visual PGD stage]
 O --> X[Optimized image]
 Q[Intent-specific text candidate] --> V[Target VLM]
 X --> V
 V --> J[Judge and feedback]
 J --> R[Text refiner]
 R --> Q
 J --> H[Budget-limited task evaluation]
```

BAP composes corpus-driven visual optimization with iterative, intent-specific text refinement from model feedback. These are two stages with separate variables and costs. The original SafetyBench scenarios/deduplicated AdvBench setup, corpus and text-search procedure must be recovered together. Source: [Ying et al., §§4–5; Appendices A,D](https://arxiv.org/html/2406.04031v2). Original closed-model feedback conflicts with the open-only project constraint; a replacement must be labelled adaptation. Our nine-method published-data panel did not execute full BAP. A small hand-selected prompt list would not reproduce its search.

### 4.8 Ling et al. — physical prompt injection

```mermaid
flowchart LR
 P[Candidate visual instructions] --> S[Prompt selection]
 S --> L[Location search]
 L --> C[Scene and camera capture]
 C --> V[VLM carrying out legitimate task]
 V --> J[Unauthorized-deviation criterion]
 J -. selection feedback .-> L
```

The controlled variable is scene-visible content and placement; capture introduces viewpoint, scale, lighting and legibility. This is a trust-boundary attack on task behavior rather than necessarily a pixel-distance optimization. The paper studies Embodied City/Habitat and physical vehicle trials. Source: [Ling et al., §§III–VI](https://arxiv.org/html/2601.17383v1). Our released CyberSecEval3 digital marker diagnostic is a different dataset/protocol. Ours: no physical reproduction; incomplete upstream execution support remains a blocker. Simulated transformations cannot replace physical evidence.

### 4.9 FigStep — typography and framing

```mermaid
flowchart LR
 R[Released SafeBench item] --> T[Typographic image construction]
 T --> V[VLM visual content processing]
 Q[Task wrapper in text] --> V
 V --> A[Generated answer]
 A --> J[Unsafe assistance and comprehension]
 R --> C[Matched all-text control]
```

The image carries text and the surrounding prompt frames the completion task. OCR-like reading and instruction following both matter; no input gradient is required. SafeBench is the source collection. FigStep's all-text Q2-prime ablation already exists, so text-twin controls are not our invention. Source: [Gong et al., §§5–6, especially §6.4](https://arxiv.org/html/2311.05608v3). Our historical experiments test wrapper/content/carrier effects on changed models and metrics; keep their refusal results separate from current HarmBench classifier ASR.

### 4.10 MM-SafetyBench — semantic and typographic carriers

```mermaid
flowchart LR
 Q[Safety scenario and source question] --> K[Extract key concept and revise text]
 K --> I[Released semantic typography or combined image]
 K --> T[Accompanying textual query]
 I --> V[Target VLM]
 T --> V
 V --> J[ASR and refusal assessed separately]
```

The benchmark changes how safety-relevant meaning is divided between image and text. Generated scenes, typography and their combination are different input conditions, not interchangeable clean images. Source: [Liu et al., §2 methodology and §3 experiments](https://arxiv.org/html/2311.17600v2). Our historical TYPO selection does not reproduce every native condition. Its released constructed images are legitimate published data; newly generating replacements would be a new adaptation, which this project has not authorized as substitute evidence.

### 4.11 MMJ-Bench — comparison architecture

```mermaid
flowchart LR
 H[HarmBench source cases] --> A[Specified attack implementations]
 A --> V[Target VLM with chosen defense]
 V --> J[Safety judge and failure accounting]
 U[MM-Vet benign tasks] --> V
 V --> B[Utility evaluation]
 J --> T[Protocol-specific result tables]
 B --> T
```

This is an evaluation framework, not another attack objective. It connects attacks, defenses, safety scoring and normal-task utility; native closed-model and open-classifier scoring must remain distinguishable. Source: [Weng et al., experimental setup and Tables 3–4](https://ojs.aaai.org/index.php/AAAI/article/download/34983/37138). It motivates a common comparison lane, but importing its name does not confer its model/data/scoring coverage. Ours: partial common-benchmark adaptation; no native full-suite reproduction.

### 4.12 AdaShield — instruction-side defense

```mermaid
flowchart LR
 D[Development attacks and defender feedback] --> P[Refined defense prompt pool]
 X[Incoming image and text] --> R[Retrieve applicable defense]
 P --> R
 R --> V[Frozen target VLM]
 X --> V
 V --> E[Safety utility and cost evaluation]
 S[Static variant uses fixed reviewed prompt] --> V
```

AdaShield-S is a manual static prompt; AdaShield-A adds refinement and a defense pool/retrieval procedure. The defense changes text context, not model weights. FigStep/QR and MM-Vet serve attack and utility roles. Source: [Wang et al., §§3–4; Appendix A](https://arxiv.org/html/2403.09513v1). Our generic prefix is not a reproduction of either full released configuration. A defense-aware visual attack would optimize through the defended text context; transfer and benign utility still require measurement.

### 4.13 JailGuard — repeated-inference detector

```mermaid
flowchart LR
 X[Incoming input] --> M[Configured input mutations]
 M --> V[Multiple target-model responses]
 V --> E[Response embeddings and divergence]
 E --> T[Threshold-based detection]
 T --> A[Accept or reject]
 B[Benign evaluation cases] --> F[False-positive and utility assessment]
 T --> F
```

JailGuard uses response instability under input mutation to detect attacks. Explain it abstractly as \(d=\operatorname{Divergence}(e(r_1),\ldots,e(r_m))\), followed by its configured decision rule; this is not a substitute for the paper's precise estimator. Source: [Zhang et al., §§4–6](https://arxiv.org/html/2312.10766v4). Released attack/benign data, mutation policy, encoder, threshold and split are part of the method. Ours: not run. Two-view gradient averaging is an attack construction choice and is not JailGuard detection.

### 4.14 Vision-attack survey — taxonomy layer

```mermaid
flowchart LR
 S[Vision-attack survey] --> T[Task access constraint and setting taxonomy]
 T --> P[Find original method papers]
 P --> C[Verify method code data and evaluation]
 C --> R[Separate reproduction and adaptation lanes]
```

The [survey, §§3–5,7](https://arxiv.org/html/2410.23687v2), supplies taxonomy and citation discovery. It is not a standalone attack to reproduce. Traditional vision benchmarks inform mechanics but do not automatically test generative safety or instruction integrity.

## 5. Map the actual implemented variants onto this architecture

Source of truth: [published-data runner](../tools/vlm_published_benchmarks.py), [optimizer](../tools/vlm_visual_attacks.py), [protocol](PUBLISHED_BENCHMARK_PROTOCOL.md). These are project adaptations; a matching family name never establishes original-paper fidelity.

| Runner ID | Controlled variable and objective | Sharing / transformations | Actual evidence |
|---|---|---|---|
| `fgsm` | Full image; one target-NLL descent step | Per request; identity | Completed on both models |
| `pgd` | Full image; iterative target-NLL descent | Per request; identity | Completed on both |
| `patch` | Masked, amplitude-bounded pixels; target NLL | Per request; fixed support | Completed on both |
| `universal` | One bounded image; mean corpus NLL | Shared across requests, one carrier | Completed on both |
| `universal_patch` | One bounded local change; corpus NLL | Shared across requests, one carrier | Completed on both |
| `universal_eot` | Replacement patch; corpus NLL under finite placements/quarter-turn rotations | One fixed sampled transform per optimization context; same carrier repeated | Smol complete; Qwen nonfinite objective, unavailable |
| `pgd_defense` | Full image; NLL with generic prefix in optimization context | Per request; identity | Completed; needs prefix-present scoring for an adaptive contrast |
| `pgd_flip` | Full image; mean NLL on identity and horizontal flip | Per request; two-view gradient average | Completed; normal-path evaluation is not a flip-defense study |
| `released_qi_16` | Load original released image; no new optimization | Transfer to changed targets | Completed; original 16/255 label is not a certified bound after our resize |
| Separate injection | Released instruction-bearing images and task text | No gradient optimization | Smol marker diagnostic complete; Qwen parity blocked |

For EOT, the generic helper's comment mentions a new evaluation background, but this runner passes the same clean carrier repeatedly. The executed caller determines the scientific interpretation. “Universal” here supports sharing across sampled contexts/requests, not visual-scene generalization. The current finite transform set is reused; it is not newly resampled every iteration or a physical camera distribution.

The optimizer may retain the clean image when no candidate improves the objective. Thus an “attack attempted” can produce no pixel change; report delivered artifact checks separately from optimizer completion. PNG delivery and reload enforce declared pixel bounds/mask support. Released-artifact transfer follows a distinct branch and has no newly verified epsilon bound against the resized carrier.

## 6. Evaluation is a separate pipeline

```mermaid
flowchart LR
 C[Frozen request image and split manifest] --> G[Clean attacked random text-only conditions]
 G --> V[Fixed checkpoint processor and decoding]
 V --> R[Private raw responses and failure metadata]
 R --> S[Safety rubric: relevant prohibited assistance]
 R --> I[Injection rubric: unauthorized task deviation]
 R --> P[Perception rubric: incorrect or targeted answer]
 S --> H[Independent blinded human review]
 I --> H
 P --> H
 H --> A[Paired aggregates uncertainty utility and cost]
```

Our primary recorded safety quantity is \(\widehat{\rm ASR}=N^{-1}\sum_i\mathbf1\{\text{classifier says relevant unsafe assistance}\}\), with all planned cases in \(N\). With \(u\) unresolved and \(k\) positives, report \([k/N,(k+u)/N]\). Those are ambiguity bounds, not confidence intervals. The paired effect is \(N^{-1}\sum_i(a_i-c_i)\) over an explicitly defined valid cohort; disclose missing pairs.

| Current development finding | What it supports | What it cannot establish |
|---|---|---|
| 136/144 method–request cases complete | Implementation coverage on this frozen panel | Reproduction of every original method |
| PGD: Smol clean 1/8, attack 4/8, prefix 4/8 | Changed classifier-labelled outcomes in eight requests | General model/defense ranking |
| PGD: Qwen clean 1/8, attack 2/8, prefix 2/8 | Same limited paired development comparison | A causal encoder/connector weakness |
| Qwen EOT: 0/8 valid | Numerical failure requiring repair | Measured zero ASR or successful defense |
| Smol injected-image marker 0/8; defended-image 1/8 | Literal-marker diagnostic on released cases | Unsafe-assistance ASR or causal injection success |

Every number above comes from [the generated measured-results report](PUBLISHED_BENCHMARK_RESULTS.md), Safety results / Execution coverage / Separate visual-injection diagnostic. It records aggregate SHA256 `f17dc7c58f26b5e9fd3ed395ca55140c39d326df485a6ec21d3c54d5534ef04c`. These are classifier-labelled development outcomes; no human validation or new original-paper experiment is implied. The full method table, paired changes, caps and costs remain in that report.

No benign utility evaluation was completed in this stage. Shared requests and controls are dependent; adding method rows does not add independent requests. Truncated outputs, classifier errors, one carrier and unresolved Qwen paths limit interpretation. Text-only controls cannot establish visual correctness when the legitimate task needs the image.

## 7. Where defenses act, and what an architectural test must show

| Defense interface | Relevant threat | Necessary comparison | Current status |
|---|---|---|---|
| Before/within preprocessing | Pixel sensitivity and patch visibility | Adaptive transform-aware attacks, delivered-image validity, benign accuracy | Proposed broader study; finite-view attack adaptation exists |
| Encoder/connector representations | Embedding transfer and modality coupling | Intervention plus matched input/task controls; changing activations alone does not prove root cause | Extended review; no causal localization established |
| Text context | Instruction interpretation and refusal behavior | Prefix-present clean/attack pairing, defense-aware optimization, over-refusal | Generic prefix measured; AdaShield not reproduced |
| Multiple-inference detector | Unstable responses across mutations | Detection operating point, false positives, query cost, adaptive evasion tests | JailGuard not run |
| Output guard / human review | Harm classification and auditing | Stimulus-aware rubric, parse failures, calibrated human agreement | HarmBench classifier used; human validation pending |

An inference-time wrapper may improve an evaluated safety endpoint. It does not demonstrate improved weight alignment. A blocked output is not automatically successful benign task completion.

## 8. The evolved research structure and next evidence

Organize the wider project into four lanes: **historical typography/measurement**, **native method reproductions**, **matched cross-mechanism comparison**, and **prospective mechanism/defense hypotheses**. Keep their datasets, results and claims separate. The [paper catalogue](VISUAL_ATTACK_PAPER_CATALOGUE.md) expands semantic, transfer, benchmark and safety literature without pretending those newly listed methods have been implemented.

1. Finish native-method contracts: source version, original checkpoint, data identity/split, objective, constraints, preprocessing, decoding, scoring, exact paper table and deviations. Resolve missing artifacts without generating substitute targets.
2. Profile the released Jailbreak-in-Pieces encoder example before promising downstream reproduction; follow with Qi only if original checkpoints fit approved resources. Original BAP feedback and physical capture need explicit scope decisions.
3. Construct a matched published-data lane after methods pass: held-out request/image groups, clean-task counterparts, shared budgets where meaningful, common scorer and two blinded human reviewers. Native ASRs remain in native-protocol tables.
4. Consider hypotheses about deployment/preprocessing transfer or defense generalization only after the wider prior-art check. No novelty claim is earned by drawing this shared diagram.

**Presentation route:** show §1, explain the five independent axes in §3, contrast Qi/Jailbreak-in-Pieces/Image Hijacks/BAP, show typography versus physical injection, then the measured table and honest coverage gaps. This demonstrates what is known, what actually ran and exactly what the next study must resolve.
