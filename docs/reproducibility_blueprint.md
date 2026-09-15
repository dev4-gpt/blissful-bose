# Reproducibility Blueprint
## Continual Safety Alignment in Small VLMs — Engineering Implementation Guide

**Lead Researcher**: Aryaman Singh Dev (`asd5520@psu.edu`)  
**Advisor**: Prof. Thao Minh Le (`mxl6224@psu.edu`)  
**Repository**: `dev4-gpt/blissful-bose`  
**Document Policy**: Pseudocode is illustrative. For the actual executable implementation, see `src/selection/gradient_selector.py` and `src/training/trainer.py`. Open questions are honest — marked `[OPEN]` where no empirical answer exists yet.

---

## Section 1: How Gradient-Based Sample Selection Works in PyTorch

This section shows how to intercept the backward pass in a Hugging Face-compatible training loop to compute per-sample gradient norms and implement the three-stage Moderate-$G_i$ selection algorithm.

### 1.1 Core Concept: Why Standard Training Loops Won't Work

Standard PyTorch / Hugging Face `Trainer` computes a **mean loss** across the batch and calls `.backward()` once. This produces one gradient vector — the average of all samples. You cannot recover per-sample gradients from this.

```
STANDARD LOOP (cannot extract per-sample gradients):
  loss = mean(L(x_i, y_i) for i in batch)
  loss.backward()    # ONE gradient: average of all samples
  optimizer.step()
```

You need individual backward passes, one per sample candidate. This is the computational cost (~51% overhead, per Bach et al. Appendix).

---

### 1.2 Pseudocode: Three-Stage Moderate-$G_i$ Selection

The pseudocode below matches the algorithm in [`src/selection/gradient_selector.py`](../src/selection/gradient_selector.py).

```python
# =============================================================
# STAGE 1: Loss-Based Pre-Filtering
# =============================================================
# Reference: Bach et al. ACL 2026, Section 4.1
# Purpose: Remove memorized (very low loss) and noisy (very high loss) candidates
#          before incurring the cost of per-sample backward passes.
# Savings: ~32% of candidate backward passes eliminated.

def loss_prefilter(model, candidates, tokenizer, q_low=0.16, q_high=0.84):
    """
    Returns indices of candidates in the middle (q_low, q_high) loss quantile range.
    Uses torch.no_grad() — no gradients computed here.
    """
    losses = []
    model.eval()
    with torch.no_grad():
        for sample in candidates:
            inputs = tokenizer(sample, return_tensors="pt").to(model.device)
            # CRITICAL: mask visual tokens and prompt tokens from loss computation
            # labels[labels == IGNORE_INDEX] = -100  (IGNORE_INDEX = -100)
            outputs = model(**inputs)
            losses.append(outputs.loss.item())

    losses = torch.tensor(losses)
    low_bound  = torch.quantile(losses, q_low)
    high_bound = torch.quantile(losses, q_high)

    filtered_indices = [
        i for i, l in enumerate(losses)
        if low_bound <= l <= high_bound
    ]
    return filtered_indices

# =============================================================
# STAGE 2: Per-Sample Gradient Norm Extraction
# =============================================================
# Reference: Bach et al. ACL 2026, Section 4.1
# CRITICAL IMPLEMENTATION NOTES FOR VLMs:
#   1. Process ONE sample at a time (B=1) to prevent VRAM graph explosion
#   2. Call model.zero_grad(set_to_none=True) after EACH sample — not just each batch
#   3. Use retain_graph=False (default) to immediately free computation graph
#   4. Compute gradient norm only over TARGET parameter subset:
#      - "language" mode: LoRA adapters on LLM backbone only
#      - "projector" mode: spatial merger / cross-attention projector only
#      - "joint" mode: sqrt(||G_language||^2 + ||G_projector||^2)

def compute_gradient_norms(model, filtered_candidates, attribution_mode="joint"):
    """
    Returns G_i for each candidate in filtered_candidates.
    attribution_mode: one of "language", "projector", "joint"
    """
    gradient_norms = []
    model.train()

    for sample in filtered_candidates:
        model.zero_grad(set_to_none=True)  # MUST be set_to_none=True for VRAM safety

        inputs = prepare_inputs(sample, model.device)  # includes label masking
        outputs = model(**inputs)
        loss = outputs.loss
        loss.backward()  # retain_graph=False by default — frees graph immediately

        # Extract gradient norm over target parameter subset
        G_i = extract_norm(model, mode=attribution_mode)
        gradient_norms.append(G_i)

    return gradient_norms


def extract_norm(model, mode):
    """Compute L2 norm over the specified parameter subset."""
    if mode == "language":
        params = [p for n, p in model.named_parameters()
                  if "lora" in n.lower() and p.grad is not None
                  and "visual" not in n.lower() and "projector" not in n.lower()]
    elif mode == "projector":
        params = [p for n, p in model.named_parameters()
                  if ("projector" in n.lower() or "merger" in n.lower())
                  and p.grad is not None]
    elif mode == "joint":
        params = [p for n, p in model.named_parameters()
                  if ("lora" in n.lower() or "projector" in n.lower()
                      or "merger" in n.lower())
                  and p.grad is not None]
    else:
        raise ValueError(f"Unknown attribution mode: {mode}")

    if not params:
        return 0.0

    norms_sq = sum(p.grad.detach().norm(2).item() ** 2 for p in params)
    return norms_sq ** 0.5


# =============================================================
# STAGE 3: Median-Distance Selection
# =============================================================
# Reference: Bach et al. ACL 2026, Section 4.1
# NOTE: Uses MEDIAN not MEAN — robust against heavy-tailed gradient distributions.

def median_select(filtered_candidates, gradient_norms, rho=0.2):
    """
    Select the fraction rho of candidates closest to the median gradient norm.
    rho=0.2 is the recommended default per Bach et al. Section 4.2.
    Robust across rho in [0.1, 0.4] per sensitivity analysis.
    """
    mu_G = torch.tensor(gradient_norms).median().item()
    distances = [(abs(g - mu_G), i) for i, g in enumerate(gradient_norms)]
    distances.sort(key=lambda x: x[0])  # ascending: closest to median first

    n_select = max(1, int(rho * len(filtered_candidates)))
    selected_indices = [i for _, i in distances[:n_select]]

    return [filtered_candidates[i] for i in selected_indices]
```

---

### 1.3 Label Masking for VLMs — Critical Implementation Detail

**Why this matters**: If visual tokens contribute to the loss, gradient norms reflect image complexity, not the model's uncertainty about the answer. This invalidates the gradient-as-safety-predictor hypothesis.

```python
def mask_non_response_tokens(input_ids, labels, image_token_ids, pad_token_id):
    """
    Sets labels to IGNORE_INDEX (-100) for all non-response tokens:
      - Image/vision tokens (e.g., <|vision_start|>...<|vision_end|>)
      - System prompt and user prompt tokens
      - Padding tokens
    Gradients will only flow through assistant response tokens.
    """
    IGNORE_INDEX = -100
    masked_labels = labels.clone()

    # Mask image regions
    for token_id in image_token_ids:
        masked_labels[input_ids == token_id] = IGNORE_INDEX

    # Mask padding
    masked_labels[input_ids == pad_token_id] = IGNORE_INDEX

    # Mask prompt (everything before first assistant response token)
    # Implementation depends on chat template — see Qwen2-VL docs
    # for <|im_start|>assistant token position

    return masked_labels
```

For Qwen2-VL specifically: visual token IDs are in the range defined by `model.config.image_token_id`. Use `processor.image_token` to identify them. [Source: Qwen2-VL HuggingFace documentation, not a research paper claim]

---

### 1.4 Integration with Hugging Face Trainer

Instead of overriding the Trainer class, you run sample selection **before** each training step:

```python
# Pseudocode — simplified training loop
# Full implementation: src/training/trainer.py

for task_idx, task_dataset in enumerate(task_sequence):  # 4 tasks: LLaVA → MathVista → VQA-RAD → DocVQA
    # Step 1: Run three-stage selection on this task's data
    filtered_indices = loss_prefilter(model, task_dataset, tokenizer)
    filtered_candidates = [task_dataset[i] for i in filtered_indices]

    for attribution_mode in ["language", "projector", "joint"]:  # ablation
        grad_norms = compute_gradient_norms(model, filtered_candidates, attribution_mode)
        selected_data = median_select(filtered_candidates, grad_norms, rho=0.2)

        # Step 2: Fine-tune on selected_data only
        # Standard Trainer call — no modification needed here
        trainer = Trainer(
            model=model,
            train_dataset=selected_data,
            args=training_args,  # see src/training/config.py
        )
        trainer.train()

    # Step 3: Evaluate safety after every task checkpoint
    asr = evaluate_asr(model, mm_safetybench_set, safety_judge)
    visage = compute_visage(model, theta_0, n_directions=100)
    bwt = compute_bwt(accuracy_matrix, task_idx)
    # Log results for paper table
```

---

## Section 2: vLLM for High-Throughput Safety Evaluation

**Motivation**: Evaluating 5,040 MM-SafetyBench pairs across 4 task checkpoints = 20,160 generation calls. Standard Hugging Face `generate()` at ~1 sample/sec = ~5.6 hours per full evaluation. vLLM with PagedAttention reduces this to minutes.

```python
# Reference: src/eval/vllm_evaluator.py
# vLLM documentation: https://docs.vllm.ai/en/latest/models/vlm.html

from vllm import LLM, SamplingParams
from PIL import Image

def batch_evaluate_safety(model_path, test_pairs, max_new_tokens=512):
    """
    Evaluates safety on a list of {"image": path, "prompt": str} dicts.
    Uses vLLM's offline batched inference for VLMs.
    """
    llm = LLM(
        model=model_path,
        max_model_len=4096,
        limit_mm_per_prompt={"image": 1},
    )

    sampling_params = SamplingParams(
        temperature=0.0,       # deterministic for safety evaluation
        max_tokens=max_new_tokens,
    )

    prompts = [
        {
            "prompt": pair["prompt"],
            "multi_modal_data": {"image": Image.open(pair["image"])},
        }
        for pair in test_pairs
    ]

    outputs = llm.generate(prompts, sampling_params)
    responses = [out.outputs[0].text for out in outputs]
    return responses
```

**Note on judge model**: After generating responses, pass them through Llama-Guard-3-8B to classify `safe` / `unsafe`. This is the judge used in the codebase (`src/eval/safety_judge.py`). For FigStep specifically, the text-only judge cannot see the image — pass the ground-truth harmful intent extracted from image metadata alongside the response.

---

## Section 3: Open Questions — Honest Unknowns

The following questions have **no empirical answer yet** for VLMs. They are the research questions this project will investigate.

### [OPEN 1] Which parameter subset drives multimodal safety drift?
**Question**: Does safety basin erosion during VLM continual fine-tuning correlate more strongly with $G_i^{(L)}$ (language LoRA), $G_i^{(P)}$ (projector), or $G_i^{(J)}$ (joint)?  
**Why unknown**: Bach et al. only investigated text-only models where no projector exists. The paper explicitly lists this as future work. [Source: Bach et al., Appendix F]  
**How this project will answer it**: Compare all three attribution modes across the 4-task sequence on Qwen2-VL-2B-Instruct with safety evaluated via MM-SafetyBench and FigStep after each task.

### [OPEN 2] Does image resolution inflate gradient norms artificially?
**Question**: A 448×448 image generates ~1,024 image tokens. More image tokens = larger gradient norm contributions, even if content is identical. Does this confound the gradient-as-safety-predictor hypothesis?  
**Why unknown**: No prior work has studied gradient norm scaling with visual token count in the safety context.  
**Mitigation approach**: Normalize $G_i$ by the number of response tokens (not total sequence length) and analyze whether the normalized score still predicts safety drift.

### [OPEN 3] Can a multimodal VISAGE metric be defined?
**Question**: Peng et al.'s VISAGE (arXiv:2405.17374) perturbs *all* model parameters uniformly. In a VLM with a frozen vision encoder, should perturbations be restricted to the trainable projector and LM backbone? Does this change the basin geometry?  
**Why unknown**: No published work has applied VISAGE-style perturbation analysis to VLM parameter subspaces.

### [OPEN 4] Do visual modality gradients predict FigStep-style jailbreak success?
**Question**: FigStep jailbreaks work because visual token representations bypass text-based safety guardrails. Does high $G_i^{(P)}$ (projector gradient) correlate with vulnerability to FigStep attacks after fine-tuning?  
**Why unknown**: The connection between per-sample projector gradient magnitude during fine-tuning and subsequent FigStep ASR has not been studied.

### [OPEN 5] Does moderate-gradient selection also reduce catastrophic forgetting of safety in VLMs?
**Question**: Bach et al. show that for text LLMs, Moderate-$G_i$ reduces BWT from −18.5% to −4.3% (Qwen3-4B, source: Sec. 5.4). Does this benefit transfer to VLMs where visual task distributions are more diverse?  
**Why unknown**: Directly from Bach et al. Appendix F — multimodal extension is explicitly unaddressed.

---

## Section 4: Known Limitations — With Citations

| Limitation | Source | Implication for This Project |
|:---|:---|:---|
| ~51% training overhead during sample selection | Bach et al., Appendix (verbatim) | Doubles Stage 2 backward pass time. Mitigated by Stage 1 pre-filtering (removes ~32% of candidates before backward passes). |
| Text-only validation only | Bach et al., Appendix F (verbatim): *"Extending gradient-based selection to vision-language models or other modalities requires further investigation."* | The VLM extension is the core research contribution — results cannot be assumed to match text-only findings. |
| SafeVLM false positives on benign inputs | SafeVLM, arXiv:2405.13581 (ablation section): code reasoning, text translation, celebrity images, artwork, and posters may be classified as risky | Any architectural safety module added to VLM must be evaluated for false refusal rate via XSTest-style benchmarks, not just ASR. |
| HarmBench model identity not specified | Bach et al. Sec. 5.2 (in available summary) — specific model family for HarmBench results is not stated | Cannot directly compare HarmBench results to Qwen2-VL-2B-Instruct without running experiments on the same model family. |
| VISAGE perturbation is architecture-agnostic | Peng et al., arXiv:2405.17374 | Applying VISAGE to VLMs requires deciding whether to perturb only trainable parameters or the full parameter space (including frozen ViT). |
| Selection ratio rho evaluated only on text tasks | Bach et al., Sec. 4.2 (sensitivity analysis over rho in [0.1, 0.4]) | The optimal rho for VLM multimodal tasks is unknown and may differ from the text-LLM setting. |

---

## Section 5: Repository Map

All executable implementations are in the `src/` directory. Tests are in `tests/`.

| Implementation | File | Test File | What It Implements |
|:---|:---|:---|:---|
| Moderate-$G_i$ selector (3 stages + 3 attribution modes) | [`src/selection/gradient_selector.py`](../src/selection/gradient_selector.py) | [`tests/test_gradient_selector.py`](../tests/test_gradient_selector.py) | Full 3-stage algorithm with language/projector/joint attribution |
| Baseline selectors (Random, Low-Gi, High-Gi) | [`src/selection/baseline_selectors.py`](../src/selection/baseline_selectors.py) | (covered in test_gradient_selector.py) | 3 baseline comparison selectors |
| Data types & multimodal fixtures | [`src/data/data_types.py`](../src/data/data_types.py) | — | `MultimodalSample`, `TaskDataset` data classes |
| 4-task dataset loader | [`src/data/dataset_loader.py`](../src/data/dataset_loader.py) | [`tests/test_dataset_loader.py`](../tests/test_dataset_loader.py) | LLaVA-150K → MathVista → VQA-RAD → DocVQA sequence |
| LoRA config & training args | [`src/training/config.py`](../src/training/config.py) | — | Qwen2-VL-2B LoRA config |
| Micro-batched trainer | [`src/training/trainer.py`](../src/training/trainer.py) | [`tests/test_gradient_selector.py`](../tests/test_gradient_selector.py) | 3-pass VRAM-safe training loop |
| Continual learning metrics (BWT, FM, ASR, VISAGE) | [`src/eval/metrics.py`](../src/eval/metrics.py) | [`tests/test_metrics.py`](../tests/test_metrics.py) | All paper metrics with verified formulas |
| Safety judge (Llama-Guard-3-8B) | [`src/eval/safety_judge.py`](../src/eval/safety_judge.py) | [`tests/test_safety_judge.py`](../tests/test_safety_judge.py) | Automated safe/unsafe classification |
| vLLM batch evaluator | [`src/eval/vllm_evaluator.py`](../src/eval/vllm_evaluator.py) | — | High-throughput batched inference driver |
| End-to-end Colab notebook | [`notebooks/continual_safety_vlm.ipynb`](../notebooks/continual_safety_vlm.ipynb) | — | Full pipeline from data loading to evaluation |

**Run all 14 tests** to verify implementation correctness:
```bash
cd ~/Developer/blissful-bose
python3 -m pytest tests/ -v
```

---

*Document version: 2026-09-15. All empirical claims traced to primary sources per the vlm-gradient-safety SKILL.md policy. Open questions are explicitly labeled `[OPEN]` and are not asserted as known results.*
