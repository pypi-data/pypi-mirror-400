"""Data module for distillation training."""

from distil_trainer.data.datamodule import DistillationDataModule
from distil_trainer.data.datasets import (
    SentenceDistillationDataset,
    TripletDataset,
    ParallelSentencesDataset,
)
from distil_trainer.data.collators import DistillationCollator
from distil_trainer.data.embeddings_generator import TeacherEmbeddingsGenerator
from distil_trainer.data.loaders import DatasetLoaders

# Optional import for OllamaEmbeddingsGenerator
try:
    from distil_trainer.data.ollama_embeddings_generator import OllamaEmbeddingsGenerator
except ImportError:
    OllamaEmbeddingsGenerator = None

__all__ = [
    "DistillationDataModule",
    "SentenceDistillationDataset",
    "TripletDataset",
    "ParallelSentencesDataset",
    "DistillationCollator",
    "DatasetLoaders",
    "TeacherEmbeddingsGenerator",
    "OllamaEmbeddingsGenerator",
]

