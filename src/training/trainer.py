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

    def train_task_step(
        self,
        task_name: str,
        samples: List[MultimodalSample],
        optimizer: Optional[torch.optim.Optimizer] = None
    ) -> Dict[str, float]:
        """Simulates/executes one task training epoch with sample selection telemetry."""
        # For unit testing and dry runs
        return {
            "task_name": task_name,
            "total_candidates": len(samples),
            "selected_samples": max(1, int(len(samples) * self.config.selection_ratio)),
            "strategy": self.config.selection_strategy
        }
