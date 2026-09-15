"""Unit tests for continual learning metrics and ASR calculations."""

import pytest
import numpy as np

from src.eval.metrics import (
    compute_asr,
    compute_accuracy,
    compute_continual_learning_metrics,
    compute_visage_score
)
from src.data.data_types import EvaluationRecord


def test_compute_asr():
    records = [
        EvaluationRecord(item_id="1", benchmark_name="test", prompt="p", model_response="r", is_safe=True),
        EvaluationRecord(item_id="2", benchmark_name="test", prompt="p", model_response="r", is_safe=False),
        EvaluationRecord(item_id="3", benchmark_name="test", prompt="p", model_response="r", is_safe=True),
        EvaluationRecord(item_id="4", benchmark_name="test", prompt="p", model_response="r", is_safe=False),
    ]
    # 2 out of 4 are unsafe -> 50% ASR
    asr = compute_asr(records)
    assert asr == 50.0


def test_compute_continual_learning_metrics_known_matrix():
    # Matrix R of shape (3, 3) representing accuracy on tasks 0, 1, 2
    # R[i, j] = accuracy on task j after training on task i
    # Task 0 peak is 80.0, after task 1 drops to 70.0, after task 2 drops to 60.0
    # Task 1 peak is 75.0, after task 2 drops to 70.0
    # Task 2 accuracy is 85.0
    R = np.array([
        [80.0,  0.0,  0.0],
        [70.0, 75.0,  0.0],
        [60.0, 70.0, 85.0]
    ])

    metrics = compute_continual_learning_metrics(R)
    
    # Final Avg = (60.0 + 70.0 + 85.0) / 3 = 71.67
    assert abs(metrics["avg_accuracy"] - 71.67) < 0.05
    
    # BWT = 0.5 * [(R[2,0] - R[0,0]) + (R[2,1] - R[1,1])]
    #     = 0.5 * [(60 - 80) + (70 - 75)] = 0.5 * [-20 + -5] = -12.5
    assert abs(metrics["bwt"] - (-12.5)) < 0.01

    # FM = 0.5 * [(80 - 60) + (75 - 70)] = 0.5 * [20 + 5] = 12.5
    assert abs(metrics["forgetting_measure"] - 12.5) < 0.01

    # Max single-step drop:
    # Task 0: 80 -> 70 (drop 10), 70 -> 60 (drop 10)
    # Task 1: 75 -> 70 (drop 5)
    # Max drop = 10.0
    assert abs(metrics["max_drop"] - 10.0) < 0.01


def test_compute_visage_score():
    margins = [80.0, 90.0, 70.0, 60.0]
    score = compute_visage_score(margins)
    assert score == 75.0
