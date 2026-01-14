"""
Confidence-Based Error Detector
===============================

Detects low-confidence spans using thresholding and sliding windows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


@dataclass
class LowConfidenceSpan:
    """Represents a span of low-confidence words."""

    start_idx: int
    end_idx: int
    start_time: float
    end_time: float
    avg_confidence: float
    words: list[str]
    alternatives: list[dict[str, Any]] | None = None


class ConfidenceDetector:
    """
    Detects low-confidence spans in ASR output.

    Uses sliding window approach to identify contiguous regions
    where confidence falls below threshold.

    Attributes:
        threshold: Confidence threshold (0-1). Words below this are flagged.
        window_size: Sliding window size for smoothing.
        min_span_words: Minimum words to form a span.
    """

    def __init__(
        self,
        threshold: float = 0.7,
        window_size: int = 3,
        min_span_words: int = 1,
    ):
        """
        Initialize the confidence detector.

        Args:
            threshold: Confidence threshold (default 0.7)
            window_size: Sliding window size (default 3)
            min_span_words: Minimum words per span (default 1)
        """
        self.threshold = threshold
        self.window_size = window_size
        self.min_span_words = min_span_words

    def detect(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """
        Detect low-confidence spans in token list.

        Args:
            tokens: List of WordToken objects

        Returns:
            List of span dictionaries with start/end indices, times, and words
        """
        if not tokens:
            return []

        spans: list[dict[str, Any]] = []
        current_span_start: int | None = None
        span_tokens: list[WordToken] = []

        for i, token in enumerate(tokens):
            is_low_confidence = token.confidence < self.threshold

            if is_low_confidence:
                if current_span_start is None:
                    current_span_start = i
                span_tokens.append(token)
            else:
                # End current span if exists
                if current_span_start is not None and len(span_tokens) >= self.min_span_words:
                    span = self._create_span(current_span_start, i - 1, span_tokens)
                    spans.append(span)
                current_span_start = None
                span_tokens = []

        # Handle span at end of transcript
        if current_span_start is not None and len(span_tokens) >= self.min_span_words:
            span = self._create_span(current_span_start, len(tokens) - 1, span_tokens)
            spans.append(span)

        # Apply sliding window smoothing
        spans = self._apply_window_smoothing(spans, tokens)

        return spans

    def _create_span(
        self,
        start_idx: int,
        end_idx: int,
        span_tokens: list[WordToken],
    ) -> dict[str, Any]:
        """Create a span dictionary from tokens."""
        avg_conf = sum(t.confidence for t in span_tokens) / len(span_tokens)
        return {
            "start_idx": start_idx,
            "end_idx": end_idx,
            "start_time": span_tokens[0].start_time,
            "end_time": span_tokens[-1].end_time,
            "avg_confidence": avg_conf,
            "words": [t.word for t in span_tokens],
            "alternatives": None,
        }

    def _apply_window_smoothing(
        self,
        spans: list[dict[str, Any]],
        tokens: list[WordToken],
    ) -> list[dict[str, Any]]:
        """
        Apply sliding window smoothing to merge nearby spans.

        Merges spans that are within window_size tokens of each other.
        """
        if len(spans) <= 1:
            return spans

        merged: list[dict[str, Any]] = []
        current = spans[0].copy()

        for next_span in spans[1:]:
            gap = next_span["start_idx"] - current["end_idx"]

            if gap <= self.window_size:
                # Merge spans
                merged_tokens = tokens[current["start_idx"] : next_span["end_idx"] + 1]
                current = self._create_span(
                    current["start_idx"],
                    next_span["end_idx"],
                    merged_tokens,
                )
            else:
                merged.append(current)
                current = next_span.copy()

        merged.append(current)
        return merged

    def get_confidence_stats(self, tokens: list[WordToken]) -> dict[str, float]:
        """
        Compute confidence statistics for tokens.

        Args:
            tokens: List of WordToken objects

        Returns:
            Dictionary with mean, std, min, max confidence values
        """
        if not tokens:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        confidences = [t.confidence for t in tokens]
        mean = sum(confidences) / len(confidences)
        variance = sum((c - mean) ** 2 for c in confidences) / len(confidences)
        std = variance ** 0.5

        return {
            "mean": mean,
            "std": std,
            "min": min(confidences),
            "max": max(confidences),
        }
