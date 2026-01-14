"""
Hypothesis Fusion Engine
========================

Combines multiple ASR hypotheses using weighted scoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from .scorers import AcousticScorer, LanguageModelScorer
from .selector import CandidateSelector

if TYPE_CHECKING:
    from ..core import WordToken


@dataclass
class FusedToken:
    """Token after hypothesis fusion."""

    word: str
    start_time: float
    end_time: float
    confidence: float
    source: str  # "original", "secondary", "fused"
    candidates: list[tuple[str, float]]


class HypothesisFusionEngine:
    """
    Fuses multiple ASR hypotheses into a single best output.

    Scoring formula:
        Score = α·ParakeetConfidence + β·LMScore + γ·AcousticSim

    Where:
        α = weight for original ASR confidence
        β = weight for language model score
        γ = weight for acoustic similarity

    Attributes:
        alpha: Original ASR confidence weight
        beta: Language model weight
        gamma: Acoustic similarity weight
        acoustic_scorer: Acoustic similarity scorer
        lm_scorer: Language model scorer
        selector: Candidate selector
    """

    def __init__(
        self,
        alpha: float = 0.4,
        beta: float = 0.35,
        gamma: float = 0.25,
    ):
        """
        Initialize the fusion engine.

        Args:
            alpha: Original ASR confidence weight
            beta: Language model weight
            gamma: Acoustic similarity weight
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.acoustic_scorer = AcousticScorer()
        self.lm_scorer = LanguageModelScorer()
        self.selector = CandidateSelector()

    def fuse(
        self,
        original_tokens: list[WordToken],
        low_confidence_spans: list[dict[str, Any]],
    ) -> list[WordToken]:
        """
        Fuse original tokens with secondary ASR alternatives.

        Args:
            original_tokens: Original ASR tokens
            low_confidence_spans: Spans with secondary ASR alternatives

        Returns:
            Fused token list
        """
        # Create working copy
        fused_tokens = list(original_tokens)

        for span in low_confidence_spans:
            alternatives = span.get("alternatives", [])
            if not alternatives:
                continue

            start_idx = span["start_idx"]
            end_idx = span["end_idx"]

            # Get original tokens for this span
            span_tokens = fused_tokens[start_idx : end_idx + 1]

            # Score all candidates
            candidates = self._score_candidates(span_tokens, alternatives)

            # Select best
            best = self.selector.select(candidates)

            # Apply best candidate
            if best and best != span_tokens:
                fused_tokens = self._apply_candidate(
                    fused_tokens, start_idx, end_idx, best
                )

        return fused_tokens

    def _score_candidates(
        self,
        original_tokens: list[WordToken],
        alternatives: list[Any],
    ) -> list[tuple[list[WordToken], float]]:
        """Score all candidates including original."""
        candidates: list[tuple[list[WordToken], float]] = []

        # Score original
        original_score = self._compute_score(original_tokens, is_original=True)
        candidates.append((original_tokens, original_score))

        # Score alternatives
        for alt in alternatives:
            if hasattr(alt, "word_timestamps"):
                alt_tokens = self._build_tokens_from_hypothesis(alt)
                alt_score = self._compute_score(alt_tokens, is_original=False)
                candidates.append((alt_tokens, alt_score))

        return candidates

    def _compute_score(
        self,
        tokens: list[WordToken],
        is_original: bool,
    ) -> float:
        """Compute fusion score for tokens."""
        if not tokens:
            return 0.0

        # Original ASR confidence
        avg_confidence = sum(t.confidence for t in tokens) / len(tokens)

        # Language model score
        text = " ".join(t.word for t in tokens)
        lm_score = self.lm_scorer.score(text)

        # Acoustic score (higher for original)
        acoustic_score = 0.8 if is_original else 0.6

        # Combine scores
        total = (
            self.alpha * avg_confidence
            + self.beta * lm_score
            + self.gamma * acoustic_score
        )

        return total

    def _build_tokens_from_hypothesis(self, hypothesis: Any) -> list[WordToken]:
        """Build WordToken list from ASR hypothesis."""
        tokens = []

        word_timestamps = getattr(hypothesis, "word_timestamps", [])
        word_confidences = getattr(hypothesis, "word_confidences", [])

        for i, ts in enumerate(word_timestamps):
            conf = word_confidences[i] if i < len(word_confidences) else 0.5
            token = WordToken(
                word=ts.get("word", ""),
                start_time=ts.get("start", 0.0),
                end_time=ts.get("end", 0.0),
                confidence=conf,
            )
            tokens.append(token)

        return tokens

    def _apply_candidate(
        self,
        tokens: list[WordToken],
        start_idx: int,
        end_idx: int,
        candidate: list[WordToken],
    ) -> list[WordToken]:
        """Apply selected candidate to token list."""
        # Mark candidate tokens as corrected
        for token in candidate:
            token.is_corrected = True
            token.correction_source = "fusion"

        # Replace tokens
        return tokens[:start_idx] + candidate + tokens[end_idx + 1 :]


# Import for type hints
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WordToken:
    """Represents a single word with metadata."""

    word: str
    start_time: float
    end_time: float
    confidence: float
    is_corrected: bool = False
    correction_source: Optional[str] = None
    alternatives: list[str] = field(default_factory=list)
