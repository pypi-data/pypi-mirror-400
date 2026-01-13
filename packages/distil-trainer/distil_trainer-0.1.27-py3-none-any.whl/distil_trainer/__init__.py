"""
Distil Trainer - A comprehensive knowledge distillation training framework.

This package provides tools for:
- Classical embedding distillation
- Model pruning (depth and width)
- Multilingual model extension
- LLM to embedding model conversion
- Hidden state distillation for transformer models
"""

from distil_trainer.core.config import (
    DistilTrainerConfig,
    DistillationConfig,
    TrainingConfig,
)
from distil_trainer.core.trainer import DistilTrainer
from distil_trainer.core.embedding_trainer import (
    EmbeddingDistillationTrainer,
    EmbeddingTrainerConfig,
)
from distil_trainer.core.hidden_state_trainer import (
    HiddenStateDistillationTrainer,
    HiddenStateTrainerConfig,
)
from distil_trainer.data.embeddings_generator import TeacherEmbeddingsGenerator

__version__ = "0.1.27"
__author__ = "Ali Bayram"
__email__ = "malibayram@gmail.com"

__all__ = [
    # Core
    "DistilTrainer",
    "DistilTrainerConfig",
    "DistillationConfig",
    "TrainingConfig",
    # Embedding Trainer
    "EmbeddingDistillationTrainer",
    "EmbeddingTrainerConfig",
    # Hidden State Trainer
    "HiddenStateDistillationTrainer",
    "HiddenStateTrainerConfig",
    # Data
    "TeacherEmbeddingsGenerator",
    # Version
    "__version__",
]

