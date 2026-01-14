"""
ASR Quality Enhancement Layer
=============================

A production-grade post-processing pipeline for improving Parakeet Multilingual ASR outputs.

Modules:
    - detectors: Confidence-based error detection
    - resynthesis: Audio slicing and secondary ASR correction
    - numeric: Numeric sequence reconstruction
    - vocab: Domain vocabulary injection
    - llm: LLM-based context restoration
    - fusion: Hypothesis fusion engine
    - validators: Consistency and quality validation
    - api: FastAPI endpoints
    - utils: Shared utilities
"""

__version__ = "0.1.0"
__author__ = "ASR Enhancement Team"

from .core import EnhancementPipeline
from .simple_pipeline import SimpleEnhancementPipeline, quick_enhance
from .unified_pipeline import UnifiedASRPipeline, enhance_audio

__all__ = [
    "EnhancementPipeline",
    "SimpleEnhancementPipeline",
    "UnifiedASRPipeline",
    "quick_enhance",
    "enhance_audio",
    "__version__",
]
