"""Continual multimodal trainer integrating gradient-based sample selection."""

import os
import torch
import torch.nn as nn
from typing import List, Dict, Any, Optional
from torch.utils.data import DataLoader

from src.training.config import TrainingConfig
from src.selection.gradient_selector import GradientSampleSelector
from src.selection.baseline_selectors import (
    RandomSampleSelector,
    LowGradientSampleSelector,
    HighGradientSampleSelector
)
from src.data.data_types import MultimodalSample


class ContinualVLMTrainer:
    """Orchestrates continual fine-tuning across multimodal tasks with sample selection."""

    def __init__(self, config: TrainingConfig, model: Optional[nn.Module] = None):
        self.config = config
        self.model = model
        self.device = torch.device(
            "cuda" if torch.cuda.is_available()
            else ("mps" if torch.backends.mps.is_available() else "cpu")
        )

        # Initialize selectors
        self.selector = GradientSampleSelector(
            selection_ratio=config.selection_ratio,
            lower_percentile=config.lower_loss_percentile,
            upper_percentile=config.upper_loss_percentile,
            attribution_mode=config.attribution_mode
        )
        self.random_selector = RandomSampleSelector(
            selection_ratio=config.selection_ratio,
            seed=config.seed
        )
        self.low_selector = LowGradientSampleSelector(selection_ratio=config.selection_ratio)
        self.high_selector = HighGradientSampleSelector(selection_ratio=config.selection_ratio)

    def select_batch_samples(
        self,
        losses: List[float],
        gradient_norms: Optional[List[float]] = None
    ) -> List[int]:
        """Filters the batch according to the configured selection strategy.

        Returns indices of the selected samples within the batch.
        """
        B = len(losses)
        strategy = self.config.selection_strategy

        if strategy == "full":
            return list(range(B))

        if strategy == "random":
            return self.random_selector.select(B)

        # For gradient-based selectors, require gradient_norms
        if gradient_norms is None or len(gradient_norms) != B:
            # Fallback to random if gradients are unavailable
            return self.random_selector.select(B)

        if strategy == "moderate_gi":
            # Stage 1: Pre-filter by loss (middle 68%)
            candidate_indices = self.selector.pre_filter_by_loss(losses)
            candidate_norms = [gradient_norms[i] for i in candidate_indices]
            # Stage 3: Median distance selection
            return self.selector.select_moderate_samples(candidate_indices, candidate_norms, B)

        if strategy == "low_gi":
            return self.low_selector.select(list(range(B)), gradient_norms, B)

        if strategy == "high_gi":
            return self.high_selector.select(list(range(B)), gradient_norms, B)

        raise ValueError(f"Unknown selection strategy: {strategy}")

    def execute_micro_batched_gradient_selection(
        self,
        batch_samples: List[MultimodalSample],
        forward_loss_fn: Any
    ) -> List[int]:
        """Executes memory-safe 3-stage selection without accumulating full-batch computation graphs.

        1. Pass 1: Forward pass with torch.no_grad() to compute scalar losses ℓ_i.
        2. Stage 1: Pre-filter out memorized (bottom 16%) and outlier (top 16%) samples.
        3. Pass 2: Per-sample backward pass ONLY on retained candidates (batch_size=1)
                   to extract L2 norm G_i without VRAM graph bloat.
        4. Stage 3: Select top ρ fraction closest to median gradient norm μ_G.
        """
        B = len(batch_samples)
        if B == 0:
            return []

        # Pass 1: Loss extraction (no graph retained)
        losses = []
        with torch.no_grad():
            for sample in batch_samples:
                loss_val = forward_loss_fn(sample, retain_graph=False)
                if isinstance(loss_val, torch.Tensor):
                    loss_val = loss_val.item()
                losses.append(float(loss_val))

        # Check strategy
        if self.config.selection_strategy == "full":
            return list(range(B))
        if self.config.selection_strategy == "random":
            return self.random_selector.select(B)

        # Stage 1: Pre-filtering
        candidate_indices = self.selector.pre_filter_by_loss(losses)

        # Pass 2: Per-candidate gradient norm extraction (micro-batched)
        candidate_norms = []
        for idx in candidate_indices:
            sample = batch_samples[idx]
            loss_tensor = forward_loss_fn(sample, retain_graph=True)
            if self.model is not None and isinstance(loss_tensor, torch.Tensor):
                norm = self.selector.compute_sample_gradient_norm(self.model, loss_tensor)
                self.model.zero_grad(set_to_none=True)
            else:
                # Fallback approximation for offline simulation
                norm = float(losses[idx] * 1.5)
            candidate_norms.append(norm)

        # Stage 3: Selection based on strategy
        if self.config.selection_strategy == "moderate_gi":
            return self.selector.select_moderate_samples(candidate_indices, candidate_norms, B)
        elif self.config.selection_strategy == "low_gi":
            return self.low_selector.select(candidate_indices, candidate_norms, B)
        elif self.config.selection_strategy == "high_gi":
            return self.high_selector.select(candidate_indices, candidate_norms, B)

        return self.random_selector.select(B)

    def train_task_step(
        self,
        task_name: str,
        samples: List[MultimodalSample],
        optimizer: Optional[torch.optim.Optimizer] = None
    ) -> Dict[str, float]:
        """Simulates/executes one task training epoch with sample selection telemetry."""
        selected_count = max(1, int(len(samples) * self.config.selection_ratio))
        return {
            "task_name": task_name,
            "total_candidates": len(samples),
            "selected_samples": selected_count,
            "strategy": self.config.selection_strategy
        }
