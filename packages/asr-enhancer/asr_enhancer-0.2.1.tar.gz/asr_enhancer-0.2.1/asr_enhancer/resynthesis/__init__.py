"""
Resynthesis Module
==================

Audio segment extraction and secondary ASR processing for low-confidence spans.
"""

from .segment_extractor import SegmentExtractor
from .secondary_asr import SecondaryASREngine
from .whisper_backend import WhisperBackend
from .riva_backend import RivaBackend
from .fast_asr import FasterWhisperASR, ParallelASR, QuickASR, SecondaryASR, ASRResult

__all__ = [
    "SegmentExtractor",
    "SecondaryASREngine", 
    "WhisperBackend",
    "RivaBackend",
    "FasterWhisperASR",
    "ParallelASR",
    "QuickASR",
    "SecondaryASR",
    "ASRResult",
]
