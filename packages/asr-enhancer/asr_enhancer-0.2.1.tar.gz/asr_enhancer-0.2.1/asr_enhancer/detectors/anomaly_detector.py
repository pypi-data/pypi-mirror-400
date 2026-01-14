"""
Anomaly Detector
================

Detects anomalies in ASR transcripts including segmentation breaks,
unusual word patterns, and high perplexity phrases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


@dataclass
class Anomaly:
    """Represents a detected anomaly."""

    type: str
    start_idx: int
    end_idx: int
    description: str
    severity: str  # "low", "medium", "high"
    context: str


class AnomalyDetector:
    """
    Detects various anomalies in ASR output.

    Anomaly types:
        - segmentation_break: Unusual gaps in timing
        - repeated_word: Same word repeated multiple times
        - truncated_word: Word appears cut off
        - nonsense_sequence: Sequence of low-meaning tokens
        - timing_overlap: Overlapping word timestamps

    Attributes:
        max_gap_seconds: Maximum allowed gap between words
        repetition_threshold: Number of repetitions to flag
    """

    def __init__(
        self,
        max_gap_seconds: float = 2.0,
        repetition_threshold: int = 3,
    ):
        """
        Initialize the anomaly detector.

        Args:
            max_gap_seconds: Max gap between words (default 2.0s)
            repetition_threshold: Repetitions to flag (default 3)
        """
        self.max_gap_seconds = max_gap_seconds
        self.repetition_threshold = repetition_threshold

        # Patterns for detecting truncated/nonsense words
        self.truncated_pattern = re.compile(r"^[a-z]{1,2}$|['-]$", re.IGNORECASE)
        self.nonsense_pattern = re.compile(r"^[^aeiou]{4,}$", re.IGNORECASE)

    def detect(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """
        Detect all anomalies in token list.

        Args:
            tokens: List of WordToken objects

        Returns:
            List of anomaly dictionaries
        """
        anomalies: list[dict[str, Any]] = []

        anomalies.extend(self._detect_segmentation_breaks(tokens))
        anomalies.extend(self._detect_repetitions(tokens))
        anomalies.extend(self._detect_truncated_words(tokens))
        anomalies.extend(self._detect_timing_overlaps(tokens))

        return anomalies

    def _detect_segmentation_breaks(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """Detect unusual gaps between words."""
        breaks = []

        for i in range(1, len(tokens)):
            prev_end = tokens[i - 1].end_time
            curr_start = tokens[i].start_time
            gap = curr_start - prev_end

            if gap > self.max_gap_seconds:
                context = self._get_context(tokens, i - 1, i)
                breaks.append({
                    "type": "segmentation_break",
                    "start_idx": i - 1,
                    "end_idx": i,
                    "description": f"Gap of {gap:.2f}s between words",
                    "severity": "medium" if gap < 5.0 else "high",
                    "context": context,
                    "gap_seconds": gap,
                })

        return breaks

    def _detect_repetitions(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """Detect repeated words."""
        repetitions = []
        i = 0

        while i < len(tokens):
            word = tokens[i].word.lower()
            count = 1
            j = i + 1

            while j < len(tokens) and tokens[j].word.lower() == word:
                count += 1
                j += 1

            if count >= self.repetition_threshold:
                context = self._get_context(tokens, i, j - 1)
                repetitions.append({
                    "type": "repeated_word",
                    "start_idx": i,
                    "end_idx": j - 1,
                    "description": f"Word '{word}' repeated {count} times",
                    "severity": "medium",
                    "context": context,
                    "repetition_count": count,
                })
                i = j
            else:
                i += 1

        return repetitions

    def _detect_truncated_words(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """Detect potentially truncated words."""
        truncated = []

        for i, token in enumerate(tokens):
            if self.truncated_pattern.match(token.word):
                context = self._get_context(tokens, i, i)
                truncated.append({
                    "type": "truncated_word",
                    "start_idx": i,
                    "end_idx": i,
                    "description": f"Possibly truncated word: '{token.word}'",
                    "severity": "low",
                    "context": context,
                })

        return truncated

    def _detect_timing_overlaps(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """Detect overlapping word timestamps."""
        overlaps = []

        for i in range(1, len(tokens)):
            prev_end = tokens[i - 1].end_time
            curr_start = tokens[i].start_time

            if curr_start < prev_end:
                overlap = prev_end - curr_start
                context = self._get_context(tokens, i - 1, i)
                overlaps.append({
                    "type": "timing_overlap",
                    "start_idx": i - 1,
                    "end_idx": i,
                    "description": f"Timestamp overlap of {overlap:.3f}s",
                    "severity": "low" if overlap < 0.1 else "medium",
                    "context": context,
                    "overlap_seconds": overlap,
                })

        return overlaps

    def _get_context(
        self,
        tokens: list[WordToken],
        start_idx: int,
        end_idx: int,
        window: int = 3,
    ) -> str:
        """Get surrounding context for an anomaly."""
        ctx_start = max(0, start_idx - window)
        ctx_end = min(len(tokens), end_idx + window + 1)
        words = [t.word for t in tokens[ctx_start:ctx_end]]
        return " ".join(words)
