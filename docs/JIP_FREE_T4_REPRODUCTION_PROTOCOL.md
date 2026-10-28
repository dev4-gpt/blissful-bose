# Amendment 13 draft: Jailbreak-in-Pieces encoder example on free compute

28 October 2026. **Prepared, not approved or run.** The owner specified Colab T4, free Kaggle if needed and no paid GPU. Proposed maximum: 60 elapsed minutes for one attempt, starting before installs/downloads. The time cap and scientific amendment still require owner acceptance. No previous clock may be reset.

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

Colab: mount private college Drive before any download. Owner performs the authorization click. Select an actually allocated T4; the script records the device and stops on a mismatch. Do not restart/disconnect an existing runtime or silently upgrade to a paid resource. Owner quota/account settings determine whether the assigned runtime is free; this notebook cannot verify billing entitlement.

Kaggle fallback is **prepared but not automatically used**. Before moving, preserve the Colab attempt, confirm the Kaggle notebook and outputs are private, verify free quota and a persistent output path, and allocate the remaining budget explicitly. A second free provider is not permission for a second 60-minute attempt. Never use public Kaggle dataset publication to move private artifacts.

All source downloads, input images, model/artifact manifests, per-step traces, optimized images and raw records remain in a `PRIVATE` folder. Public release is reviewed aggregates and code only. The notebook saves a private zip/checksum and summary before returning. Mid-step time enforcement is cooperative; network downloads have timeouts and the next operation checks the deadline. Runtime/kernel termination can still interrupt preservation; incomplete state must remain visible.

## Reviewable implementation and unresolved fidelity

Notebook: `notebooks/vlm_jip_free_t4.ipynb`, generated by `tools/nb_gen/make_jip_free_t4_nb.py`; helper: `tools/vlm_jip_encoder.py`. Default execution performs no install, network access or GPU work. Requires the exact amendment token and `RUN_APPROVED=True` after owner acceptance.

The helper reimplements the inspected encoder loop and checks source identity; it does not execute unreviewed upstream imports. This, current library/model revisions, frozen parameter gradients, seeds and timed profiling are recorded deviations. It cannot be described as unchanged original-code execution. Dataset completeness, exact historical dependencies, original checkpoint identity and downstream paper evaluation remain unresolved.
