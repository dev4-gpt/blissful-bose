"""Training configuration for continual multimodal safety alignment."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrainingConfig:
    """Hyperparameters mirroring Bach et al. (ACL 2026), calibrated for Qwen2-VL-2B."""

    model_name_or_path: str = "Qwen/Qwen2-VL-2B-Instruct"
    output_dir: str = "./checkpoints"
    
    # LoRA configuration
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"
    ])
    
    # Optimization
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.03
    batch_size: int = 8
    gradient_accumulation_steps: int = 1
    num_epochs_per_task: int = 1
    
    # Gradient selection parameters (Bach et al. 2026)
    selection_strategy: str = "moderate_gi"  # "moderate_gi", "random", "low_gi", "high_gi", "full"
    selection_ratio: float = 0.20             # rho
    lower_loss_percentile: float = 0.16       # alpha_low (middle 68% pre-filter)
    upper_loss_percentile: float = 0.84       # alpha_high
    attribution_mode: str = "joint"           # "joint", "language", "projector"
    
    # Reproducibility
    seed: int = 42
