"""
PEARL: Prototype-guided Embedding Refinement via Adaptive Representation Learning

A powerful framework for enhancing embeddings through signal extraction
and prototype-guided feature augmentation.
"""

__version__ = "0.1.1"

from pearl.core.signal_extractor import (
    SignalExtractor,
    SignalExtractorTrainer,
    CentroidManager
)
from pearl.core.paf import (
    PrototypeFeatures,
    PAFAugmentor
)
from pearl.models.rag_classifier import (
    RAGClassifier,
    RAGClassifierWrapper
)
from pearl.models.classifiers import (
    MLPClassifier,
    TransformerClassifier
)
from pearl.pipeline import PEARLPipeline

__all__ = [
    # Version
    "__version__",

    # Core components
    "SignalExtractor",
    "SignalExtractorTrainer",
    "CentroidManager",
    "PrototypeFeatures",
    "PAFAugmentor",

    # Models
    "RAGClassifier",
    "RAGClassifierWrapper",
    "MLPClassifier",
    "TransformerClassifier",

    # Pipeline
    "PEARLPipeline",
]
