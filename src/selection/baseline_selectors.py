"""Baseline sample selectors for empirical benchmarking:
- Random Sampling
- Low-Gi Selection (Bottom 20%)
- High-Gi Selection (Top 20%)
"""

from typing import List
import numpy as np


class RandomSampleSelector:
    """Randomly selects a fraction rho of candidates."""

    def __init__(self, selection_ratio: float = 0.20, seed: int = 42):
        self.selection_ratio = selection_ratio
        self.rng = np.random.default_rng(seed)

    def select(self, batch_size: int) -> List[int]:
        target_k = max(1, int(np.floor(self.selection_ratio * batch_size)))
        indices = list(range(batch_size))
        return list(self.rng.choice(indices, size=target_k, replace=False))


class LowGradientSampleSelector:
    """Selects samples with the lowest gradient norms (bottom rho)."""

    def __init__(self, selection_ratio: float = 0.20):
        self.selection_ratio = selection_ratio

    def select(self, candidate_indices: List[int], gradient_norms: List[float], original_batch_size: int) -> List[int]:
        target_k = max(1, int(np.floor(self.selection_ratio * original_batch_size)))
        target_k = min(target_k, len(candidate_indices))
        sorted_order = np.argsort(gradient_norms)
        return [candidate_indices[i] for i in sorted_order[:target_k]]


class HighGradientSampleSelector:
    """Selects samples with the highest gradient norms (top rho) - replicates worst-case collapse."""

    def __init__(self, selection_ratio: float = 0.20):
        self.selection_ratio = selection_ratio

    def select(self, candidate_indices: List[int], gradient_norms: List[float], original_batch_size: int) -> List[int]:
        target_k = max(1, int(np.floor(self.selection_ratio * original_batch_size)))
        target_k = min(target_k, len(candidate_indices))
        # Descending order
        sorted_order = np.argsort(gradient_norms)[::-1]
        return [candidate_indices[i] for i in sorted_order[:target_k]]
