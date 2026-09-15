"""Unit tests for the 3-stage Gradient-Based Sample Selection Engine."""

import pytest
import numpy as np
import torch
import torch.nn as nn

from src.selection.gradient_selector import GradientSampleSelector
from src.selection.baseline_selectors import (
    RandomSampleSelector,
    LowGradientSampleSelector,
    HighGradientSampleSelector
)


class DummyVLM(nn.Module):
    """Simple dual-component module simulating Projector + LLM LoRA."""

    def __init__(self):
        super().__init__()
        # Simulating projector
        self.visual_merger = nn.Linear(4, 4)
        # Simulating language backbone
        self.language_model_lora = nn.Linear(4, 2)

    def forward(self, x):
        proj = self.visual_merger(x)
        out = self.language_model_lora(proj)
        return out


def test_loss_pre_filtering_retains_middle_quantiles():
    selector = GradientSampleSelector(
        selection_ratio=0.20,
        lower_percentile=0.16,
        upper_percentile=0.84
    )
    # 100 uniformly spaced losses from 0 to 99
    losses = list(range(100))
    retained = selector.pre_filter_by_loss(losses)

    # 16th percentile is ~15.84, 84th is ~83.16 -> indices 16 to 83 inclusive = 68 samples
    assert len(retained) == 68
    assert min(retained) == 16
    assert max(retained) == 83


def test_median_gradient_selection_picks_closest_to_median():
    selector = GradientSampleSelector(selection_ratio=0.20)
    
    # 10 candidate indices with given gradient norms
    candidate_indices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    # Gradient norms: median of [1, 2, 3, 4, 5, 6, 7, 8, 9, 20] is (5 + 6) / 2 = 5.5
    gradient_norms = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 20.0]
    
    # For batch_size = 10 and rho = 0.20, target_k = 2
    # Closest to 5.5 are 5.0 (diff 0.5) and 6.0 (diff 0.5)
    selected = selector.select_moderate_samples(
        candidate_indices=candidate_indices,
        gradient_norms=gradient_norms,
        original_batch_size=10
    )
    
    assert len(selected) == 2
    assert set(selected) == {14, 15}  # index 14 has norm 5.0, index 15 has norm 6.0


def test_per_sample_gradient_norm_computation():
    model = DummyVLM()
    selector = GradientSampleSelector(attribution_mode="joint")
    
    x = torch.randn(1, 4)
    out = model(x)
    loss = torch.sum(out ** 2)
    
    norm = selector.compute_sample_gradient_norm(model, loss)
    assert isinstance(norm, float)
    assert norm > 0.0


def test_attribution_modes_filter_target_parameters():
    model = DummyVLM()
    
    selector_joint = GradientSampleSelector(attribution_mode="joint")
    selector_lang = GradientSampleSelector(attribution_mode="language")
    selector_proj = GradientSampleSelector(attribution_mode="projector")
    
    params_joint = selector_joint.filter_trainable_parameters(model)
    params_lang = selector_lang.filter_trainable_parameters(model)
    params_proj = selector_proj.filter_trainable_parameters(model)
    
    # Joint should have all 4 parameter tensors (weight & bias for merger, weight & bias for lora)
    assert len(params_joint) == 4
    # Language only has the language_model_lora parameters (2)
    assert len(params_lang) == 2
    assert all("lora" in name for name, _ in params_lang)
    # Projector only has the visual_merger parameters (2)
    assert len(params_proj) == 2
    assert all("merger" in name for name, _ in params_proj)


def test_baseline_selectors():
    # Random selector
    rand_sel = RandomSampleSelector(selection_ratio=0.20, seed=123)
    selected_rand = rand_sel.select(batch_size=20)
    assert len(selected_rand) == 4
    
    # Low-Gi selector
    low_sel = LowGradientSampleSelector(selection_ratio=0.20)
    selected_low = low_sel.select(
        candidate_indices=[0, 1, 2, 3, 4],
        gradient_norms=[10.0, 1.0, 5.0, 0.5, 8.0],
        original_batch_size=5
    )
    assert selected_low == [3]  # Lowest norm is 0.5 at index 3
    
    # High-Gi selector
    high_sel = HighGradientSampleSelector(selection_ratio=0.20)
    selected_high = high_sel.select(
        candidate_indices=[0, 1, 2, 3, 4],
        gradient_norms=[10.0, 1.0, 5.0, 0.5, 8.0],
        original_batch_size=5
    )
    assert selected_high == [0]  # Highest norm is 10.0 at index 0


def test_micro_batched_trainer_selection():
    from src.training.config import TrainingConfig
    from src.training.trainer import ContinualVLMTrainer
    from src.data.dataset_loader import ContinualMultimodalDataLoader

    model = DummyVLM()
    config = TrainingConfig(selection_strategy="moderate_gi", selection_ratio=0.20)
    trainer = ContinualVLMTrainer(config=config, model=model)

    samples = [
        ContinualMultimodalDataLoader.create_synthetic_sample(f"sample_{i}", "task1")
        for i in range(10)
    ]

    # Mock loss function returning a tensor
    def mock_loss_fn(sample, retain_graph=False):
        # Deterministic loss with a tensor depending on model params
        idx = int(sample.id.split("_")[1])
        x = torch.ones(1, 4) * (idx + 1)
        out = model(x)
        return torch.sum(out ** 2)

    selected = trainer.execute_micro_batched_gradient_selection(samples, mock_loss_fn)
    assert len(selected) == 2  # 20% of 10
    assert all(isinstance(idx, int) for idx in selected)

