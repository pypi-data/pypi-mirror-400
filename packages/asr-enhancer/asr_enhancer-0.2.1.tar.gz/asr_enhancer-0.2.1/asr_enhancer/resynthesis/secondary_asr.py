"""
Secondary ASR Engine
====================

Provides secondary ASR processing for low-confidence spans.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from .whisper_backend import WhisperBackend
from .riva_backend import RivaBackend


@dataclass
class ASRHypothesis:
    """Represents an ASR hypothesis with confidence."""

    text: str
    confidence: float
    word_timestamps: list[dict[str, Any]]
    word_confidences: list[float]


class ASRBackend(ABC):
    """Abstract base class for ASR backends."""

    @abstractmethod
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> list[ASRHypothesis]:
        """Transcribe audio and return N-best hypotheses."""
        pass


class SecondaryASREngine:
    """
    Secondary ASR engine for re-processing low-confidence spans.

    Supports multiple backends:
        - whisper: Whisper (tiny/base models for speed)
        - riva: NVIDIA Riva Streaming
        - vosk: Vosk offline ASR

    Attributes:
        backend: ASR backend instance
        n_best: Number of hypotheses to return
    """

    BACKENDS = {
        "whisper": WhisperBackend,
        "riva": RivaBackend,
    }

    def __init__(
        self,
        backend: str = "whisper",
        device: str = "cpu",
        model_size: str = "tiny",
        n_best: int = 3,
        language: Optional[str] = None,
    ):
        """
        Initialize the secondary ASR engine.

        Args:
            backend: Backend name ("whisper", "riva")
            device: Device to use ("cpu", "cuda")
            model_size: Model size for backend
            n_best: Number of hypotheses to return
            language: Optional language code
        """
        self.n_best = n_best
        self.language = language

        if backend not in self.BACKENDS:
            raise ValueError(f"Unknown backend: {backend}. Available: {list(self.BACKENDS.keys())}")

        backend_class = self.BACKENDS[backend]
        self.backend: ASRBackend = backend_class(
            device=device,
            model_size=model_size,
        )

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> list[ASRHypothesis]:
        """
        Transcribe audio segment.

        Args:
            audio_path: Path to audio segment
            language: Optional language override

        Returns:
            List of ASRHypothesis objects (N-best)
        """
        lang = language or self.language
        hypotheses = await self.backend.transcribe(audio_path, lang)
        return hypotheses[: self.n_best]

    async def transcribe_batch(
        self,
        audio_paths: list[str],
        language: Optional[str] = None,
    ) -> list[list[ASRHypothesis]]:
        """
        Transcribe multiple audio segments.

        Args:
            audio_paths: List of paths to audio segments
            language: Optional language code

        Returns:
            List of hypothesis lists (one per audio)
        """
        results = []
        for path in audio_paths:
            hyps = await self.transcribe(path, language)
            results.append(hyps)
        return results
