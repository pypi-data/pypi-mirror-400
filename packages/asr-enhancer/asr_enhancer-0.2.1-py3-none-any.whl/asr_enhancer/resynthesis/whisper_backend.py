"""
Whisper Backend
===============

Whisper-based ASR backend for secondary transcription.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


@dataclass
class ASRHypothesis:
    """Represents an ASR hypothesis with confidence."""

    text: str
    confidence: float
    word_timestamps: list[dict[str, Any]]
    word_confidences: list[float]


class WhisperBackend:
    """
    Whisper-based ASR backend.

    Uses OpenAI Whisper for transcription. Optimized for
    low-latency with tiny/base models.

    Attributes:
        model: Loaded Whisper model
        device: Device for inference
    """

    def __init__(
        self,
        device: str = "cpu",
        model_size: str = "tiny",
    ):
        """
        Initialize the Whisper backend.

        Args:
            device: Device for inference ("cpu", "cuda")
            model_size: Model size ("tiny", "base", "small")
        """
        self.device = device
        self.model_size = model_size
        self.model = None

        if WHISPER_AVAILABLE:
            self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model."""
        self.model = whisper.load_model(self.model_size, device=self.device)

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> list[ASRHypothesis]:
        """
        Transcribe audio using Whisper.

        Args:
            audio_path: Path to audio file
            language: Optional language code

        Returns:
            List of ASRHypothesis (single hypothesis for Whisper)
        """
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper is not installed. Run: pip install openai-whisper")

        if self.model is None:
            self._load_model()

        # Transcribe with word timestamps
        options = {
            "word_timestamps": True,
            "fp16": self.device == "cuda",
        }
        if language:
            options["language"] = language

        result = self.model.transcribe(audio_path, **options)

        # Extract word-level information
        word_timestamps = []
        word_confidences = []

        if "segments" in result:
            for segment in result["segments"]:
                if "words" in segment:
                    for word_info in segment["words"]:
                        word_timestamps.append({
                            "word": word_info.get("word", "").strip(),
                            "start": word_info.get("start", 0.0),
                            "end": word_info.get("end", 0.0),
                        })
                        # Whisper doesn't provide per-word confidence,
                        # use segment probability as approximation
                        word_confidences.append(
                            word_info.get("probability", segment.get("avg_logprob", 0.0))
                        )

        # Calculate overall confidence
        avg_confidence = 0.0
        if word_confidences:
            avg_confidence = sum(word_confidences) / len(word_confidences)

        hypothesis = ASRHypothesis(
            text=result.get("text", "").strip(),
            confidence=avg_confidence,
            word_timestamps=word_timestamps,
            word_confidences=word_confidences,
        )

        return [hypothesis]

    def is_available(self) -> bool:
        """Check if Whisper is available."""
        return WHISPER_AVAILABLE and self.model is not None
