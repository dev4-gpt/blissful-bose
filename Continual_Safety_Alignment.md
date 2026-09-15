# Continual Safety Alignment via Gradient-Based Sample Selection

**Authors:** Thong Bach, Dung Nguyen, Thao Minh Le, Truyen Tran
Applied Artificial Intelligence Initiative (A2I2), Deakin University & Pennsylvania State University

**Abstract**
Large language models require continuous adaptation to new tasks while preserving safety alignment. However, fine-tuning on even benign data often compromises safety behaviors, including refusal of harmful requests, truthfulness, and commonsense reasoning. We investigate which training samples cause alignment drift through a data-centric lens. Our empirical analysis shows samples contribute unequally: high-gradient samples cause greater safety degradation and drive models toward pretrained distributions, while moderate-gradient samples enable task learning with minimal alignment loss. We propose gradient-based sample selection that filters high-gradient samples during fine-tuning. Across multiple model families on continual domain tasks, our method substantially improves alignment preservation while maintaining competitive task performance, without requiring curated safe data or architectural modifications. Our method is robust across selection ratios, task orderings, and diverse attack benchmarks.

## 1 Introduction
Large language models deployed in real-world applications require continuous adaptation to new domains, tasks, and evolving requirements. While initial alignment through reinforcement learning from human feedback (RLHF), direct preference optimization (DPO), and constitutional AI establishes safety properties, subsequent fine-tuning often compromises these carefully cultivated behaviors.

This vulnerability presents a fundamental challenge for LLM deployment. Organizations need to customize models for specific use cases, incorporate new knowledge, and adapt to changing requirements, yet each fine-tuning step risks degrading the alignment properties that make these models safe to deploy. Even fine-tuning on benign, non-malicious datasets can unintentionally weaken safety mechanisms, suggesting that alignment degradation is not merely a consequence of adversarial data but a structural property of fine-tuning itself. While the data content is typically benign, the parameter updates they induce can be destructive to the alignment priors.

Continual learning research has made significant progress on retaining task performance through parameter regularization and experience replay. However, these methods focus on preventing catastrophic forgetting of learned tasks rather than preserving alignment properties. We address a distinct problem:

**The Continual Safety Alignment Problem:** How can we continuously adapt LLMs to new tasks while preserving alignment properties (safety, truthfulness, helpfulness) without requiring curated safe data at each adaptation step?

Rather than constraining model architectures or requiring curated safe datasets at each adaptation step, we investigate this problem through a data-centric lens: *Which training samples cause alignment drift, and can we simply avoid them?*

Recent work reveals two critical properties of aligned models that inform our approach. First, LLMs exhibit *elasticity*: a tendency to revert toward pretrained distributions during fine-tuning because the massive pretraining corpora exerts stronger influence than smaller alignment datasets. This reversion inherently degrades alignment since these pre-training corpora usually lack safety constraints. Second, aligned models occupy a "safety basin" in parameter space with sharp boundaries where safety collapses abruptly.

While these frameworks explain *why* alignment is fragile, they do not predict *which samples* cause drift or *how* to maintain alignment during task adaptation. We hypothesize that training samples activate elastic reversion unequally: samples where aligned predictions diverge substantially from task targets (high gradients) may reverse alignment modifications, while moderate-gradient samples enable learning with minimal drift.

We validate this hypothesis through systematic experiments and propose a practical data-centric solution. Our contributions are:
- **Empirical finding:** We provide empirical evidence that per-sample gradient magnitude predicts safety drift in continual fine-tuning. Through KL-divergence analysis, we show high-gradient samples shift models toward pretrained distributions.
- **Mechanistic analysis:** We characterize high-gradient samples as format mismatches—short-answer tasks where the aligned model’s verbose output distribution diverges from terse targets.
- **Practical recipe:** We propose gradient-based sample selection with a tunable safety-task trade-off, validated across three model families, multiple task sequences and orderings, and diverse safety benchmarks.

## 2 Background

### 2.1 Measuring Alignment via Safety Basins
To study alignment dynamics quantitatively, we adopt the safety basin framework. This framework conceptualizes alignment as occupying a region in parameter space rather than a binary property. Given aligned parameters, the safety landscape is defined by perturbing along a direction. This defines a *safety basin*, the connected region in parameter space where safety properties hold.

A critical empirical finding is that safety basins have *sharp boundaries*: safety exhibits step-function collapse when crossing the boundary, with minimal graceful degradation. This geometry makes large parameter updates particularly dangerous. A single large step can push models from safe to unsafe, while many small updates might stay within the basin.

The VISAGE score quantifies basin volume by averaging safety margin across random perturbation directions. Higher VISAGE indicates larger safety basins and more robust alignment.

### 2.2 Alignment Fragility and Elasticity
Alignment degradation during fine-tuning reflects structural properties of the learning process rather than just adversarial data. Previous work shows that as few as 10 examples can compromise safety, while other studies demonstrate that even benign datasets weaken safety mechanisms.

The elasticity framework provides theoretical grounding for this phenomenon: language models resist alignment modifications and rebound toward pretrained behavior under perturbation. The elastic force is proportional to dataset size. Since pretrain corpora vastly exceed alignment datasets, the pretrained distribution exerts orders of magnitude stronger "pull" on model behavior.

This asymmetry predicts two phenomena: *resistance* (pretrained models resist initial alignment) and *rebound* (aligned models revert toward pretrained behavior under fine-tuning). Our hypothesis extends this framework to the sample level: training samples where aligned predictions diverge substantially from task targets, indicated by high gradient magnitudes, may specifically activate this elastic reversion force.

### 2.3 Problem Formulation
We formalize the continual safety alignment problem, distinguishing it from standard continual learning.
- **Setting:** Consider an aligned model that must learn T tasks sequentially from datasets.
- **Standard Continual Learning:** Minimizes task loss while preventing forgetting of previous tasks.
- **Continual Safety Alignment:** We impose an additional constraint: alignment preservation. The model must remain within the safety basin throughout training.
- **Challenges:** The constraint is difficult to enforce directly due to measurement cost, non-differentiability, and sample-level opacity (unclear which samples contribute to drift).

## 3 Analysis: Which Samples Cause Drift?

Following the data-centric perspective, we investigate: *do all samples contribute equally to alignment drift, or can sample-level properties predict drift risk?*

**Hypothesis:** We hypothesize that per-sample gradient magnitude indicates drift risk. High-gradient samples occur where aligned predictions diverge substantially from task targets, precisely where alignment training modified behavior away from pretrained tendencies. Training on these samples may reverse those modifications, activating elastic reversion.

**Experimental design:** We fine-tune LLaMA-3.1-8B-Instruct and Qwen-2.5-7B-Instruct on Dolly (15K benign instruction-following examples). We compare three selection strategies (using 20% of samples): 
1. Random (baseline)
2. High-Gi (top 20% by gradient norm)
3. Moderate-Gi (20% closest to median gradient norm). 

**Why not low-gradient samples?** Low-Gi provides better safety preservation but consistently trades 0.8–1.9 points of task performance, revealing a Pareto tradeoff. Moderate-Gi provides the best task performance while preserving safety.

### 3.1 Results Support the Hypothesis
**High-gradient samples show greater alignment drift.** High-Gi selection retains only 62-72% of original alignment and increases Attack Success Rate (ASR) by 5-9×, while moderate-Gi selection preserves 83-88% with only 1.5-2× ASR increase. 

**Evidence for elastic reversion mechanism.** Training on High-Gi samples correlates with movement toward pretrained distributions and away from aligned distributions. This pattern is consistent with high-gradient samples activating the elastic reversion force.

### 3.2 Gradient Direction Analysis: Preliminary Investigation
To explore whether high-gradient samples have gradients aligned with the reversion direction, we analyze gradient directions across parameter subsets using TopK-Cosine similarity. High-gradient samples exhibit higher directional alignment with the reversion direction compared to moderate-gradient samples in final-layer parameters, although specific components vary by architecture. This confirms that the signal localizes to alignment-critical parameters.

### 3.3 Implications for Method Design
These findings validate our data-centric approach: filter high-gradient samples during fine-tuning. Moderate-gradient samples provide sufficient learning signal for task adaptation while avoiding alignment-reversing effects.

## 4 Method: Gradient-Based Sample Selection

### 4.1 Algorithm
The algorithm operates in three stages:
1. **Loss-based pre-filtering** removes extreme samples (very low loss = memorized; very high loss = outliers).
2. **Gradient computation** on filtered candidates, reducing computational cost.
3. **Median-based selection** chooses samples closest to median gradient norm, avoiding both high-gradient (causing alignment drift) and low-gradient samples (providing minimal learning signal).

We use median (not mean) for robustness against heavy-tailed gradient distributions. Selection ratio ρ = 0.2 balances quality vs. cost.

### 4.2 Sensitivity to Selection Ratio
We conduct a systematic sensitivity analysis on selection ratios. Results are robust across ρ ∈ [0.1, 0.4]. Smaller ρ (stricter filtering) provides slightly better safety at marginal task performance cost. We recommend ρ = 0.2 as a default.

## 5 Experiments

### 5.1 Experimental Setup
- **Models and tasks:** Qwen2.5-7B-Instruct, LLaMA-3.1-8B-Instruct, and Qwen3-4B-Instruct. We fine-tune sequentially on four domains: Dolly, GSM8K, MedMCQA, and Squad_v2.
- **Baselines:** Standard fine-tuning, Random sampling, KL-divergence regularization, O-LoRA, EWC, and Gradient Clipping.
- **Evaluation:** Task performance and Alignment (AdvBench, HarmBench, TruthfulQA, ARC-C, BoolQ, HellaSwag, Winogrande).

### 5.2 Alignment Preservation
**Safety preservation:** Moderate-Gi achieves substantially lower attack success rates throughout continual learning. On Qwen2.5, our method achieves 10.2% ASR versus 36.7% for the baseline—representing a 3.6× reduction. It also generalizes to diverse attack vectors (HarmBench).

**Truthfulness and general capabilities:** Moderate-Gi maintains factual accuracy matching or exceeding baselines and competitive general capabilities. Sample selection preserves model competencies while improving safety.

### 5.3 Continual Learning Performance
Our gradient-based selection consistently outperforms baselines in maintaining balanced performance across tasks.

### 5.4 Catastrophic Forgetting Analysis
We analyze catastrophic forgetting using Backward Transfer (BWT) and Forgetting Measure (FM). Moderate-Gi achieves significant improvements in BWT and reduces the maximum single-step performance drop.

**Task Interference Analysis:** Task interference drops significantly compared to the baseline, explaining why gradient-based selection preserves prior knowledge.

## 6 Conclusion
We presented an empirical investigation of which training samples cause alignment drift during continual fine-tuning. High-gradient samples accelerate reversion toward pretrained distributions, while moderate-gradient samples enable task learning with minimal alignment loss. Our gradient-based sample selection filters high-gradient samples during fine-tuning, achieving strong alignment preservation with consistent gains across task orderings, diverse safety benchmarks, and selection ratios. 

## Appendices Summary
- **Extended Background:** Discusses the data compression theory underlying the elasticity framework.
- **Sample Audit:** High-gradient samples are often format mismatches, not content-based outliers. They are dominated by short-answer tasks where the aligned model's verbose output distribution diverges from terse targets.
- **Why Not Gradient Clipping?** Clipping attenuates step size but still trains on high-gradient samples, meaning the model still receives a learning signal pushing toward pretrained distributions. Our method removes these samples entirely.
- **Limitations:** Focuses on text-only models (extending to vision-language models requires further investigation) and incurs a ~51% computational overhead during training.
