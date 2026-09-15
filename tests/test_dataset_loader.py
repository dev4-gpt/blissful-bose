"""Unit tests for dataset loader and benchmark fixtures."""

import pytest
from src.data.dataset_loader import ContinualMultimodalDataLoader


def test_synthetic_task_sequence_structure():
    sequence = ContinualMultimodalDataLoader.load_task_sequence_synthetic(samples_per_task=10)
    assert len(sequence) == 4
    
    expected_tasks = [
        "Task1_LLaVA_Instruct",
        "Task2_MathVista",
        "Task3_Medical_VQA",
        "Task4_DocVQA"
    ]
    for (name, samples), expected_name in zip(sequence, expected_tasks):
        assert name == expected_name
        assert len(samples) == 10
        assert samples[0].image is not None
        assert samples[0].prompt != ""
        assert samples[0].target != ""


def test_synthetic_safety_benchmarks_structure():
    items = ContinualMultimodalDataLoader.load_safety_benchmarks_synthetic(samples_per_bench=5)
    # 5 FigStep + 5 MM-SafetyBench + 5 POPE = 15 items
    assert len(items) == 15
    
    bench_names = {item.benchmark_name for item in items}
    assert bench_names == {"FigStep", "MM-SafetyBench", "POPE"}
