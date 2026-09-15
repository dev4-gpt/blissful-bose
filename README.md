# Continual Safety Alignment in Small Vision-Language Models (VLMs) via Multimodal Gradient-Based Sample Selection

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dev4-gpt/blissful-bose/blob/master/notebooks/continual_safety_vlm.ipynb)
[![CI Tests](https://img.shields.io/badge/pytest-13%20passed-brightgreen.svg)]()
[![Model](https://img.shields.io/badge/Base%20Model-Qwen2--VL--2B--Instruct-blue.svg)]()
[![Venue Target](https://img.shields.io/badge/Target-CVPR%20%2F%20ACL%20%2F%20NeurIPS-purple.svg)]()

> **Lead Researcher**: Aryaman  
> **Reference Paper**: *Continual Safety Alignment via Gradient-Based Sample Selection* (Bach, Nguyen, Le, & Tran — ACL 2026 Findings / [arXiv:2604.17215](https://arxiv.org/abs/2604.17215))

---

## 📌 Executive Overview

When safety-aligned Large Vision-Language Models (VLMs) like `Qwen2-VL-2B-Instruct` undergo sequential fine-tuning on downstream tasks (e.g., visual reasoning, medical QA, document analysis), they suffer from severe **multimodal alignment drift**. Fine-tuning on even benign datasets erodes refusal guardrails, heightens hallucination, and exposes the model to cross-modal jailbreaks.

This repository adapts and extends the data-centric framework of **Bach et al. (ACL 2026)** from text LLMs to **Small VLMs**:
1. High-gradient training samples activate **elastic reversion** toward the unaligned pretraining distribution, collapsing the model's safety basin.
2. Filtering out high-gradient samples via **Moderate-$G_i$ selection** preserves multimodal safety guardrails without requiring curated safe replay data or architectural modifications.
3. We introduce **Multimodal Gradient Attribution**, evaluating whether sample selection is best guided by the Language LoRA gradients, Multimodal Projector gradients, or Joint parameter norms.

---

## 🏗️ Architecture & Pipeline

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                           HYBRID TRAINING & EVALUATION PIPELINE                       │
└───────────────────────────────────────────────────────────────────────────────────────┘
          │                                                                │
          ▼                                                                ▼
┌──────────────────────────────────────────┐    ┌───────────────────────────────────────┐
│     TRAINING ENGINE (Google Colab)       │    │     EVALUATION ENGINE (vLLM)          │
├──────────────────────────────────────────┤    ├───────────────────────────────────────┤
│ • PyTorch + Hugging Face PEFT (LoRA r=16)│    │ • vLLM PagedAttention Batch Engine   │
│ • Loss Pre-Filtering (Middle 68%)        │    │ • MM-SafetyBench (5,040 test pairs)   │
│ • Per-Sample Gradient Norm Extraction    │    │ • FigStep (Typographic jailbreaks)    │
│ • Moderate-Gi Selection (ρ = 0.20)       │    │ • POPE (Object hallucination probes)  │
│ • Sequential Checkpoint Export           │    │ • 5,000+ probes evaluated in 3 mins   │
└──────────────────────────────────────────┘    └───────────────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Run in Google Colab (Recommended)
Click the badge above or open [`notebooks/continual_safety_vlm.ipynb`](notebooks/continual_safety_vlm.ipynb) directly in Google Colab on a GPU runtime (T4, L4, or A100).

### 2. Local Setup & Testing
```bash
git clone https://github.com/dev4-gpt/blissful-bose.git
cd blissful-bose

# Install dependencies
pip install -r requirements.txt

# Run full test suite (13 unit tests)
python3 -m pytest tests/
```

---

## 📂 Repository Structure

```
blissful-bose/
├── docs/
│   ├── MASTER_RESEARCH_COMPENDIUM.md      # ⭐ Master all-in-one dossier, paper citations & PPT blueprint
│   ├── presentation_blueprint.md          # 11-slide presentation script & advisor Q&A
│   ├── sota_landscape_survey.md           # 20+ paper survey across 6 defense families
│   ├── methodology_comparison.md          # Head-to-head comparison table of all defenses
│   ├── gradient_strategy_dossier.md       # Mathematical formulation & gradient mechanics
│   └── reproducibility_blueprint.md       # PyTorch autograd pseudocode & open research questions
├── RESEARCH_METHODOLOGY_AND_VLM_SPEC.md   # Authoritative numerical tables (Bach et al. Tables 2, 4-8)
├── STUDY_AND_PRESENTATION_PLAYBOOK.md     # Study guide & metric formulas
├── Continual_Safety_Alignment.md          # Full notes on Bach et al. (ACL 2026)
├── notebooks/
│   └── continual_safety_vlm.ipynb         # End-to-end Colab training & vLLM evaluation
├── src/
│   ├── data/
│   │   ├── data_types.py                  # Multimodal dataclasses & schemas
│   │   └── dataset_loader.py              # Task sequence & benchmark fixture loaders
│   ├── selection/
│   │   ├── gradient_selector.py           # 3-stage Moderate-Gi algorithm & attribution modes
│   │   └── baseline_selectors.py          # Random, Low-Gi, High-Gi selectors
│   ├── training/
│   │   ├── config.py                      # TrainingConfig hyperparameters
│   │   └── trainer.py                     # ContinualVLMTrainer loop
│   └── eval/
│       ├── metrics.py                     # ASR, BWT, FM, and VISAGE score math
│       ├── safety_judge.py                # Automated refusal/compliance classifier
│       └── vllm_evaluator.py              # High-throughput vLLM batched inference
├── tests/
│   ├── test_gradient_selector.py          # Unit tests for selection math & autograd
│   ├── test_metrics.py                    # Unit tests for BWT, FM, and ASR
│   ├── test_dataset_loader.py             # Unit tests for dataset loaders
│   └── test_safety_judge.py               # Unit tests for compliance judgment
├── pyproject.toml
└── requirements.txt
```

---

## 📖 Citation

If referencing this methodology, cite the primary foundational paper:

```bibtex
@inproceedings{bach2026continual,
  title={Continual Safety Alignment via Gradient-Based Sample Selection},
  author={Bach, Thong and Nguyen, Dung and Le, Thao Minh and Tran, Truyen},
  booktitle={Findings of the Association for Computational Linguistics: ACL 2026},
  year={2026},
  url={https://arxiv.org/abs/2604.17215}
}
```
