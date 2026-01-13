"""Core PEARL components."""

from pearl.core.signal_extractor import (
    SignalExtractor,
    SignalExtractorTrainer,
    CentroidManager
)
from pearl.core.paf import (
    PrototypeFeatures,
    PAFAugmentor
)

__all__ = [
    "SignalExtractor",
    "SignalExtractorTrainer",
    "CentroidManager",
    "PrototypeFeatures",
    "PAFAugmentor",
]
