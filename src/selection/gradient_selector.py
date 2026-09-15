"""Gradient-Based Sample Selection Engine for Continual Multimodal Alignment.

Implements the 3-stage Moderate-Gi algorithm from Bach et al. (ACL 2026),
extended for Vision-Language Models (VLMs) with multimodal gradient attribution.
"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import torch
import torch.nn as nn


class GradientSampleSelector:
    """Selects training samples based on loss pre-filtering and median gradient norm proximity."""

    def __init__(
        self,
        selection_ratio: float = 0.20,
        lower_percentile: float = 0.16,
        upper_percentile: float = 0.84,
        attribution_mode: str = "joint"
    ):
        """
        Args:
            selection_ratio (rho): Fraction of the batch/dataset to select (default: 0.20).
            lower_percentile (alpha_low): Bottom cutoff for loss pre-filtering (default: 0.16).
            upper_percentile (alpha_high): Top cutoff for loss pre-filtering (default: 0.84).
            attribution_mode: Parameter group to calculate gradient norms for:
                - 'joint': All trainable parameters (Projector + LoRA).
                - 'language': Only LLM language backbone LoRA parameters.
                - 'projector': Only multimodal projector / spatial merger parameters.
        """
        if not (0.0 < selection_ratio <= 1.0):
            raise ValueError(f"selection_ratio must be in (0, 1], got {selection_ratio}")
        if not (0.0 <= lower_percentile < upper_percentile <= 1.0):
            raise ValueError("Invalid percentiles: require 0 <= lower_percentile < upper_percentile <= 1")
        if attribution_mode not in {"joint", "language", "projector"}:
            raise ValueError(f"Unknown attribution_mode: {attribution_mode}")

        self.selection_ratio = selection_ratio
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        self.attribution_mode = attribution_mode

    def pre_filter_by_loss(self, losses: List[float]) -> List[int]:
        """Stage 1: Pre-filters out memorized (low loss) and outlier (high loss) samples.

        Args:
            losses: Scalar losses for each sample in the candidate batch.

        Returns:
            List of indices that fall within [Q_low, Q_high].
        """
        if not losses:
            return []
        if len(losses) < 4:
            # Not enough samples to compute reliable quantiles; retain all
            return list(range(len(losses)))

        loss_arr = np.array(losses, dtype=np.float64)
        q_low = np.percentile(loss_arr, self.lower_percentile * 100.0)
        q_high = np.percentile(loss_arr, self.upper_percentile * 100.0)

        # Middle ~68%
        retained = [i for i, val in enumerate(loss_arr) if q_low <= val <= q_high]

        # Safety fallback: ensure at least enough samples for selection target
        target_count = max(1, int(np.floor(self.selection_ratio * len(losses))))
        if len(retained) < target_count:
            # Fallback to sorting by distance to median loss
            med = np.median(loss_arr)
            retained = list(np.argsort(np.abs(loss_arr - med)))[:target_count]

        return retained

    def filter_trainable_parameters(
        self,
        model: nn.Module
    ) -> List[Tuple[str, nn.Parameter]]:
        """Filters model parameters based on the chosen attribution mode."""
        selected = []
        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue

            name_lower = name.lower()
            if self.attribution_mode == "joint":
                selected.append((name, param))
            elif self.attribution_mode == "language":
                # Matches LoRA / LLM decoder parameters
                if "lora" in name_lower or "language_model" in name_lower or "model.layers" in name_lower:
                    selected.append((name, param))
            elif self.attribution_mode == "projector":
                # Matches Vision-Language connector / spatial merger
                if "merger" in name_lower or "projector" in name_lower or "visual.merger" in name_lower:
                    selected.append((name, param))

        # Fallback if specific component has no trainable params
        if not selected:
            selected = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
        return selected

    def compute_sample_gradient_norm(
        self,
        model: nn.Module,
        loss: torch.Tensor
    ) -> float:
        """Stage 2: Computes L2 gradient norm for a single sample."""
        target_params = [p for _, p in self.filter_trainable_parameters(model)]
        if not target_params:
            return 0.0

        # Compute gradients with retain_graph if needed
        grads = torch.autograd.grad(
            loss,
            target_params,
            retain_graph=True,
            create_graph=False,
            allow_unused=True
        )

        total_norm_sq = 0.0
        for g in grads:
            if g is not None:
                total_norm_sq += torch.sum(g.detach() ** 2).item()

        return float(np.sqrt(total_norm_sq))

    def select_moderate_samples(
        self,
        candidate_indices: List[int],
        gradient_norms: List[float],
        original_batch_size: int
    ) -> List[int]:
        """Stage 3: Selects samples closest to the median gradient norm.

        Args:
            candidate_indices: Indices of samples that passed loss pre-filtering.
            gradient_norms: Corresponding L2 gradient norms for candidate_indices.
            original_batch_size: Total batch size before pre-filtering.

        Returns:
            List of selected original sample indices of size floor(rho * original_batch_size).
        """
        if not candidate_indices or not gradient_norms:
            return []

        target_k = max(1, int(np.floor(self.selection_ratio * original_batch_size)))
        target_k = min(target_k, len(candidate_indices))

        norms_arr = np.array(gradient_norms, dtype=np.float64)
        median_norm = float(np.median(norms_arr))

        # Distance to median gradient norm
        distances = np.abs(norms_arr - median_norm)
        sorted_order = np.argsort(distances)

        # Select top target_k
        selected_candidates = [candidate_indices[idx] for idx in sorted_order[:target_k]]
        return selected_candidates
