# Original-paper reproduction audit

28 October 2026. Scope: the twelve registered core readings, not every visual attack
ever published. This audit advances methods/setup, selected appendix and source inspection;
it is not a declaration that every full text, appendix, release and result table is verified.
No new scientific GPU run was launched for this audit. Earlier 136/144 cases remain
published-source **adaptations**, not retroactively faithful paper reproductions.

Actual source audit: 22 pinned official source/configuration/README files, 120,547 bytes,
all matching their Git blob identities. Python syntax checks identified the two BAP
defects recorded below. This validates source identity and detects syntax failures;
it does not verify model loading, dataset completeness or successful attacks.

## The requested change

Each study needs its native data, model, objective, attack budget, preprocessing,
selection rule, decoding and endpoint. A second common-benchmark comparison can change
these deliberately, but must keep a separate adaptation label. Dataset names alone do
not establish fidelity. A literature review, source audit, executable mechanism and
completed reproduction are four different milestones.

The new notebook is `notebooks/vlm_paper_reproduction.ipynb`; its generator is
`tools/nb_gen/make_paper_reproduction_nb.py`. The executable registry, source hash checks,
fidelity checks and explicitly gated original-code entrypoints live in
`tools/vlm_paper_protocols.py`. No missing original targets or datasets are fabricated.

## Method and data ledger

| Paper and inspected locations | Native procedure / data | Required fidelity work before a result |
|---|---|---|
| Goodfellow et al., [FGSM, §§3–4](https://arxiv.org/html/1412.6572v3) | Untargeted classification loss sign step; MNIST/maxout experiment | Recover exact trained weights and scaling; generative target minimization changes the task |
| Madry et al., [PGD, §§2,5](https://arxiv.org/html/1706.06083v4) | Constrained classification inner search; MNIST/CIFAR-10 | Separate attack evaluation from excluded weight training; match checkpoint and selected paper-table attack |
| Brown et al., [patch, §§2–3](https://arxiv.org/html/1712.09665v2) | Universal replacement patch over images, locations, rotations/scales; ImageNet classifiers | Recover exact distributions, selection and model ensemble; physical evidence requires actual capture |
| Qi et al., [§§3–4; Appendix A](https://arxiv.org/html/2306.13213v2) | Corpus likelihood; released 66 targets, 40 manual requests and RealToxicityPrompts challenging evaluation | Original checkpoints, corpus sampling, preprocessing, budgets, decoding and toxicity/human protocols |
| Shayegani et al., [§§3–4; Algorithm 1](https://arxiv.org/html/2307.14539v2) | CLIP embedding matching; text/OCR/visual/combined triggers and scenario collection | Align paper and later code release; recover full trigger collection and test settings |
| Bailey et al., [§§2–4; Appendix C](https://arxiv.org/html/2309.00236v4) | Behavior and soft-distribution prompt matching; Alpaca contexts, AdvBench for jailbreak | Recover task-specific split/config; official demo is narrower than paper experiments |
| Ying et al., [§§4–5; Appendices A,D](https://arxiv.org/html/2406.04031v2) | Query-agnostic visual PGD plus iterative text feedback; paper SafetyBench scenarios and deduplicated AdvBench | Freeze original corpus/merge/splits; original ChatGPT feedback conflicts with open-only scope |
| Ling et al., [§§III–VI](https://arxiv.org/html/2601.17383v1) | Visual prompt selection/location search, Embodied City/Habitat, physical vehicle trials | Upstream incomplete-run warning; simulator, scene/camera conditions and hardware unavailable in current scope |
| Weng et al., [MMJ-Bench, setup and Tables 3–4](https://ojs.aaai.org/index.php/AAAI/article/download/34983/37138) | Unified HarmBench attack/completion scoring and MM-Vet utility | Benchmark protocol, not another individual attack; GPT-4 and open classifier are distinct evaluations |
| Wang et al., [AdaShield, §§3–4; Appendix A](https://arxiv.org/html/2403.09513v1) | Static/adaptive defense; FigStep, QR and MM-Vet | Original prompts/pool, split and retrieval/refinement; generic prefix does not reproduce this system |
| Zhang et al., [JailGuard, §§4–6](https://arxiv.org/html/2312.10766v4) | Mutations, response divergence and detection; released attack/benign collection | Match visual mutation policy, query budget, encoder, threshold and development/evaluation split |
| Zhang et al., [survey, §§3–5,7](https://arxiv.org/html/2410.23687v2) | Taxonomy and citation discovery | No separate experiment to reproduce; verify each cited original independently |

## Source findings that change implementation decisions

### Qi: use the actual parser and loop, not just README flags

Pinned [entrypoint](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models/blob/5fc9883cfa9b4183cf05c6eceef49e449e45e9c9/minigpt_visual_attack.py),
lines 28–32 and 114–121: the parser uses `--cfg_path`/`--gpu_id`; the attack calls
hardcode `num_iter=5000`, batch size 8, and divide alpha/epsilon by 255.
The [attacker loop](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models/blob/5fc9883cfa9b4183cf05c6eceef49e449e45e9c9/minigpt_utils/visual_attacker.py)
uses `range(num_iter + 1)`. Record nominal iterations and effective updates separately.
A tiny `--n_iters` argument would not make a bounded smoke run of this entrypoint.
The [released configuration](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models/blob/5fc9883cfa9b4183cf05c6eceef49e449e45e9c9/eval_configs/minigpt4_eval.yaml)
uses image size 224. Our 448-pixel Qwen/Smol adapter is a different deployment.

### Jailbreak in Pieces: original encoder examples are available

Pinned [source](https://github.com/erfanshayegani/Jailbreak-In-Pieces/blob/b7b2bce812adada23f583f63f63e564f84d277c6/src/adv_image.py),
lines 69–86 and 101–136: CLIP ViT-L/14-336, normalization disabled for this image
processor path, released white initialization and visual trigger, Adam learning rate
0.1, 5000 updates, pixel clamping, JPEG export. The code has a fixed loop; the paper
describes a convergence criterion. Preserve that difference rather than silently
calling one the other. Example availability does not establish complete scenario coverage.
The repository README's later LLaVA-1.5 example is also not automatically the paper model.

### Image Hijacks: demo availability is not full experiment availability

Pinned [demo config](https://github.com/euanong/image-hijacks/blob/2a4403cf67e8578afdd6e56096ff31524aaa63e7/experiments/exp_demo_imgs/config.py)
contains leak-context and specific-string jobs, full-image constraints, four epsilon
settings and LLaVA variants; it mixes Alpaca/LLaVA contexts with its own splits.
The [README](https://github.com/euanong/image-hijacks/blob/2a4403cf67e8578afdd6e56096ff31524aaa63e7/README.md)
references `exp_results_tables/config.py`, absent from the inspected pinned tree,
and says jailbreak configurations are forthcoming. Do not invent missing configurations
or substitute the demo split for the paper's split. Text formatting is evaluated only;
no actual email, tool invocation or data transmission belongs in the study.

### BAP and PPIA: constraints that cannot be fixed by renaming an adaptation

Pinned [BAP visual entrypoint](https://github.com/NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt/blob/5350c0bfeb01d9e485603b85a03500280886d275/VAP.py)
sets 3000 iterations, epsilon 32/255, alpha 1/255 and batch size 2 in the attack call.
The [text demo](https://github.com/NY1024/BAP-Jailbreak-Vision-Language-Models-via-Bi-Modal-Adversarial-Prompt/blob/5350c0bfeb01d9e485603b85a03500280886d275/CoT.py)
calls GPT-3.5-turbo; a small fixed candidate list does not instantiate its feedback search.
Actual syntax checks of pinned `CoT.py` and `Eval.py` fail at lines 58 and 138,
respectively (duplicated assignment; missing function-definition colon).
Record these upstream defects; do not silently repair them and call the source
unchanged. Source identity and executable validity are separate checks.
The [PPIA README](https://github.com/2023cghacker/Physical-Prompt-Injection-Attack/blob/7291d92ee05c4b9079ef824e0b4bd12e8e14316c/README.md)
states that the code is being organized and cannot yet run fully. CyberSecEval3 image
markers are a separate benchmark, not PPIA's original simulation or physical collection.

### PGD: code release defaults need a configuration identity

Pinned [CIFAR-10 config](https://github.com/MadryLab/cifar10_challenge/blob/f15682d9f1e26eb47a2d3b371ef8b6c7abcf6276/config.json)
has epsilon 8, step size 2, 10 steps, random start and cross-entropy in that release's
pixel scale. Pinned [MNIST config](https://github.com/MadryLab/mnist_challenge/blob/3ee3643c4a8c59458d8c191b84027f4a6cbd9580/config.json)
has epsilon 0.3, step 0.01 and 40 steps. These are distinct release configurations;
do not infer that either reproduces every result table or convert scales without tracing code.

## Execution and evidence requirements

Before any new scientific run, freeze original source and environment, checkpoint and
processor hashes, source data/target hashes, original split selection, image transforms,
optimizer/update count, model sampling and judge protocol. Record a measured memory/time
profile and owner-approved budget. Keep prompts, images, raw replies and annotations private.
The original 120/60-minute clocks are expired and cannot be reset for these new studies.

No new original-paper ASR exists yet. The new notebook reports `NOT_RUN`, not zero ASR.
Only independent data/config/result review can promote a completed run to a reproduction.
Reduced scale retains an explicit sample/compute deviation; changing model, surrogate,
data, split or judge creates an adaptation even if the mathematical idea is preserved.

For comparison later: retain a separate common-benchmark lane with identical held-out
requests/images, budgets and scorer across attacks. Native-paper ASRs belong in their
own tables. Human agreement, benign utility and adaptive-defense evaluations remain required.

## Concrete next run proposal — draft, not approved or executed

Start with the released Jailbreak-in-Pieces encoder example: exact pinned source and
released initialization/trigger, original CLIP variant, original optimizer/loop and output
encoding. First audit dependency/model revisions, normalize/save-reload behavior, license,
and T4 gradients/memory. A bounded feasibility stage estimates cost; it is not a paper ASR.
Then reproduce downstream behavior with paper-compatible models and released prompts,
once their version/split differences are resolved. No manufactured triggers are permitted.

Qi original-checkpoint work follows only after weight access and memory feasibility;
do not promise the paper's A100 procedure fits a T4. Original BAP closed-model feedback
and physical capture cannot be called faithful under the current open-only/T4 scope.
Resolve those constraints explicitly; do not generate replacement corpora to hide them.
