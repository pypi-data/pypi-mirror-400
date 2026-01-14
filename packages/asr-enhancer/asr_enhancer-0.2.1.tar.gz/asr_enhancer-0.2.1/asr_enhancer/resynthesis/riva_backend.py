"""
Riva Backend
============

NVIDIA Riva-based ASR backend for secondary transcription.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

try:
    import riva.client

    RIVA_AVAILABLE = True
except ImportError:
    RIVA_AVAILABLE = False


@dataclass
class ASRHypothesis:
    """Represents an ASR hypothesis with confidence."""

    text: str
    confidence: float
    word_timestamps: list[dict[str, Any]]
    word_confidences: list[float]


class RivaBackend:
    """
    NVIDIA Riva-based ASR backend.

    Uses Riva Streaming ASR for low-latency transcription.

    Attributes:
        client: Riva ASR client
        device: Device for inference
    """

    def __init__(
        self,
        device: str = "cpu",
        model_size: str = "default",
        server_url: str = "localhost:50051",
    ):
        """
        Initialize the Riva backend.

        Args:
            device: Device for inference (used for local processing)
            model_size: Model configuration (ignored for Riva)
            server_url: Riva server URL
        """
        self.device = device
        self.server_url = server_url
        self.client = None

        if RIVA_AVAILABLE:
            self._init_client()

    def _init_client(self) -> None:
        """Initialize the Riva client."""
        auth = riva.client.Auth(uri=self.server_url)
        self.client = riva.client.ASRService(auth)

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> list[ASRHypothesis]:
        """
        Transcribe audio using Riva.

        Args:
            audio_path: Path to audio file
            language: Optional language code

        Returns:
            List of ASRHypothesis objects
        """
        if not RIVA_AVAILABLE:
            raise RuntimeError(
                "Riva is not installed. See: https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html"
            )

        if self.client is None:
            self._init_client()

        # Read audio file
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        # Configure recognition
        config = riva.client.RecognitionConfig(
            language_code=language or "en-US",
            max_alternatives=3,
            enable_word_time_offsets=True,
            enable_word_confidence=True,
        )

        # Perform recognition
        response = self.client.offline_recognize(audio_data, config)

        hypotheses = []
        for result in response.results:
            for alt in result.alternatives:
                word_timestamps = []
                word_confidences = []

                for word_info in alt.words:
                    word_timestamps.append({
                        "word": word_info.word,
                        "start": word_info.start_time,
                        "end": word_info.end_time,
                    })
                    word_confidences.append(word_info.confidence)

                hypothesis = ASRHypothesis(
                    text=alt.transcript,
                    confidence=alt.confidence,
                    word_timestamps=word_timestamps,
                    word_confidences=word_confidences,
                )
                hypotheses.append(hypothesis)

        return hypotheses if hypotheses else [self._empty_hypothesis()]

    def _empty_hypothesis(self) -> ASRHypothesis:
        """Return empty hypothesis."""
        return ASRHypothesis(
            text="",
            confidence=0.0,
            word_timestamps=[],
            word_confidences=[],
        )

    def is_available(self) -> bool:
        """Check if Riva is available."""
        return RIVA_AVAILABLE and self.client is not None
