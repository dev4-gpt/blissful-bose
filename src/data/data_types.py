"""Data contracts and schemas for multimodal continual safety alignment."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from PIL import Image


@dataclass
class MultimodalSample:
    """A single multimodal training sample containing image, instruction prompt, and target response."""
    id: str
    prompt: str
    target: str
    task_name: str
    image: Optional[Image.Image] = None
    image_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkItem:
    """An adversarial or evaluation benchmark probe item."""
    id: str
    prompt: str
    benchmark_name: str  # e.g. "MM-SafetyBench", "FigStep", "POPE"
    image: Optional[Image.Image] = None
    image_path: Optional[str] = None
    ground_truth: Optional[str] = None
    attack_category: Optional[str] = None  # e.g. "typographic", "illegal_activity", "hallucination"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationRecord:
    """Record of a model generation and automated safety/capability judgement."""
    item_id: str
    benchmark_name: str
    prompt: str
    model_response: str
    is_safe: bool
    attack_category: Optional[str] = None
    judge_model: str = "llama-guard-3-8b-vision"
    judge_reasoning: Optional[str] = None
    ground_truth: Optional[str] = None
    is_correct: Optional[bool] = None
