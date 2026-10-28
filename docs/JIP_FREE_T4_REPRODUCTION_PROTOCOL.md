# Amendment 13 draft: Jailbreak-in-Pieces encoder example on free compute

28 October 2026. **First bounded attempt authorized; execution pending.** After requesting reproduction and review, the owner clarified: “Existing Colab T4 allocation is okay; no purchases.” Proceed with the previously proposed 60-minute maximum for this first encoder attempt, including installs/downloads; this is not authorization for unbounded whole-paper runs or new purchases. No previous clock may be reset.

## Correction: full-paper reproduction is the objective

The initial notebook implemented an encoder feasibility stage only. That is insufficient for the owner's requested paper reproduction. The full study must connect **original inputs → attack construction → original-compatible target models → repeated downstream generations → native evaluation → comparison with published tables**. The executable 50/5000-update encoder stage below is one prerequisite, not the whole study or a proxy for ASR.

| Reproduction component | Original evidence to match | Current readiness |
|---|---|---|
| Four trigger branches | Text-encoder target, OCR image target, visual image target, combined image target; Eq.3 | Only the released visual encoder example is implemented here |
| Algorithm 1 | Target embedding, initialization, Adam/image updates, convergence rule; §3 | Released fixed-length loop available; paper convergence variant not implemented |
| Main safety evaluation | LLaVA and LLaMA-Adapter V2; scenario/image/prompt/repetition design; §4 | Exact historical checkpoints, complete original inputs and decoding not yet recovered |
| Primary scoring | Scenario-relevant harmful task fulfillment; §4 and Appendix H | Original-compatible human protocol and reviewers not yet established |
| Supplemental scoring | Original toxicity models/services; §4 | Native versions/configuration and service availability unresolved |
| Other experiments | Indirect/direct hidden injection, AdvBench supplement and qualitative grounding | Distinct original inputs/settings not yet recovered as complete collections |
| Published comparison | Native per-model/per-trigger results and uncertainty | No new downstream result exists |

The pinned official repository tree contains a small demo release: source, README, two visual targets, two initialization/background files and selected output examples. It does not supply a verified complete scenario/trigger/prompt manifest or the full paper experiment driver. The later README's LLaVA-1.5 example is not proof of the historical checkpoint. These are actual reproducibility blockers; another dataset or a new synthetic trigger would not resolve them faithfully.

The paper's main experiment describes 6400 generations, using two models, eight scenarios, eight images, two prompts and 25 repetitions (§4). Its primary endpoint requires task-fulfilling harmful assistance, not just a smaller embedding loss or a refusal keyword. This scale is a source requirement, not a promise that the unprofiled whole study fits one free session. Do not add another clock or paid GPU to conceal a feasibility limit.

**Whole-paper completion rule:** all selected experiment branches have original-source manifests and compatible checkpoints/configuration, actual attack artifacts, completed generation/scoring coverage and a table-level comparison with documented deviations. Any missing component remains blocked or partial. The notebook must report this state before showing the encoder appendix. Author-contact or newly discovered official artifacts may resolve missing inputs; no message is sent to authors without owner authorization.

**Strategy:** finish the release/data/checkpoint audit first, select a specific recoverable paper experiment, and rerun its attack algorithm and downstream evaluation together. A declared reduced-scale reproduction may use fewer original items/repetitions while retaining the method; changed checkpoints/objectives/judges are adaptations. If the required original collection cannot be recovered, prioritize a paper with a complete accessible release rather than inventing substitutes.

## Research scope and evidence labels

Source: Shayegani, Dong and Abu-Ghazaleh, [Jailbreak in pieces](https://arxiv.org/html/2307.14539v2), §§3–4, Algorithm 1; official [released encoder example](https://github.com/erfanshayegani/Jailbreak-In-Pieces/blob/b7b2bce812adada23f583f63f63e564f84d277c6/src/adv_image.py).

This first stage reproduces the **released visual-trigger encoder optimization procedure**, with explicit implementation/environment differences. It does not reproduce all trigger branches, the complete scenario collection, downstream VLM sampling, human ratings or a paper result table. The released fixed loop and the paper's convergence algorithm are distinct. Initially label this `encoder-method adaptation / release-reproduction candidate`; independent review is needed for promotion.

No new prompts, trigger images, targets, test examples or human labels are generated. Use the two exact images already released by the authors. The white initialization is an original published input, not newly fabricated test data. Do not print/display or publicly export the trigger or optimized image.

## Fixed construction contract

- Official repository revision: `b7b2bce812adada23f583f63f63e564f84d277c6`.
- `src/adv_image.py` Git blob: `b9cd5f79bfd087f92481ead5443e10b0e3dd14fa`.
- Released visual target blob: `70dee0d7a36dc78f56bf1e65d8ecba4280d7cab7`; released white initialization blob: `743f5240ddabe0c05f367f5b5b9f9af4f011c638`.
- CLIP: `openai/clip-vit-large-patch14-336`; resolve and freeze its actual repository SHA before downloading weights. This is a current available revision, not proof of the paper-era weight identity.
- Original image processor settings, with `do_normalize=False`, as in the released example; record effective resize/crop/rescale configuration and delivered tensor size.
- FP32, batch one, seed 42, frozen weights; only input pixels trainable. Original source leaves parameter gradients enabled, although its optimizer updates only the image. Freezing parameter gradients is a disclosed memory implementation change; it does not train or alter the model weights.
- Loss: `torch.nn.PairwiseDistance(p=2)` between candidate and released-target CLIP image features. Preserve default epsilon and unnormalized features. Do not substitute cosine similarity, normalized CLIP embeddings or sequence NLL.
- Adam learning rate 0.1; clamp candidate pixels to [0,1] after each step. No infinity-norm bound or patch mask is added: the released example is a full-image, box-constrained optimization.
- Delivery: multiply by 255, truncate to uint8, save JPEG using recorded Pillow settings/version, reopen through the same processor, then measure embedding distance again. JPEG and clamping effects are reported separately.

## Stages, endpoints and stopping

**E13a, engineering feasibility:** run 50 updates from the original initialization. Record finite input gradients, frozen-weight identities, initial/final feature distance, gradient magnitude, wall time, GPU allocation peak, device and actual software versions. Also report distance after saving/reloading. No success threshold is imported from a different representation definition.

**E13b, release-length attempt:** if E13a passes and its measured cost projects that an independent 5000-update run plus preservation fits the same original 60-minute clock with a five-minute reserve, restart from the original initialization for that explicitly separate 5000-update attempt. Do not count the profile's 50 updates toward the released loop. Otherwise stop with a costed feasibility report; do not silently shrink the native-length run.

Both stages use the same released pair. They are not independent test samples. All outcomes are descriptive engineering evidence. Hypothesis: input optimization can reduce this released example's encoder distance within the selected deployment. Finite gradients or lower loss do not establish human-semantic equivalence or unsafe model behavior. Nonfinite loss/gradient, absent CUDA, wrong source hash or changed weights stops the attempt. A timeout is incomplete, not a negative ASR.

**No safety-ASR endpoint in this stage.** A downstream reproduction needs verified original-compatible VLM/checkpoint, released task prompts, original sampling/evaluation and separate human protocol. Do not substitute newly created targets to obtain a result quickly.

## Compute and privacy contract

Colab: mount private college Drive before any download. Owner performs the authorization click. Select an actually allocated T4; the script records the device and stops on a mismatch. Use the existing authorized allocation; do not purchase resources, upgrade, restart or disconnect an existing runtime. The notebook cannot determine billing entitlement.

Kaggle fallback is **prepared but not automatically used**. Before moving, preserve the Colab attempt, confirm the Kaggle notebook and outputs are private, verify free quota and a persistent output path, and allocate the remaining budget explicitly. A second free provider is not permission for a second 60-minute attempt. Never use public Kaggle dataset publication to move private artifacts.

All source downloads, input images, model/artifact manifests, per-step traces, optimized images and raw records remain in a `PRIVATE` folder. Public release is reviewed aggregates and code only. The notebook saves a private zip/checksum and summary before returning. Mid-step time enforcement is cooperative; network downloads have timeouts and the next operation checks the deadline. Runtime/kernel termination can still interrupt preservation; incomplete state must remain visible.

## Reviewable implementation and unresolved fidelity

Notebook: `notebooks/vlm_jip_free_t4.ipynb`, generated by `tools/nb_gen/make_jip_free_t4_nb.py`; helper: `tools/vlm_jip_encoder.py`. Default execution performs no install, network access or GPU work. Requires the exact amendment token and `RUN_APPROVED=True` after owner acceptance.

The helper reimplements the inspected encoder loop and checks source identity; it does not execute unreviewed upstream imports. This, current library/model revisions, frozen parameter gradients, seeds and timed profiling are recorded deviations. It cannot be described as unchanged original-code execution. Dataset completeness, exact historical dependencies, original checkpoint identity and downstream paper evaluation remain unresolved.
