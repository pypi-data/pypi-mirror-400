"""
Candidate Selector
==================

Selects best candidate from scored hypotheses.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


class CandidateSelector:
    """
    Selects the best candidate from scored hypotheses.

    Selection strategies:
        - highest_score: Simple maximum score
        - confidence_weighted: Weight by confidence
        - consensus: Prefer candidates with word overlap
    """

    def __init__(
        self,
        strategy: str = "highest_score",
        min_improvement: float = 0.05,
    ):
        """
        Initialize the candidate selector.

        Args:
            strategy: Selection strategy
            min_improvement: Minimum improvement over original to select alternative
        """
        self.strategy = strategy
        self.min_improvement = min_improvement

    def select(
        self,
        candidates: list[tuple[list[Any], float]],
    ) -> list[Any] | None:
        """
        Select best candidate from scored list.

        Args:
            candidates: List of (tokens, score) tuples

        Returns:
            Best token list or None
        """
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0][0]

        if self.strategy == "highest_score":
            return self._select_highest_score(candidates)
        elif self.strategy == "confidence_weighted":
            return self._select_confidence_weighted(candidates)
        elif self.strategy == "consensus":
            return self._select_consensus(candidates)
        else:
            return self._select_highest_score(candidates)

    def _select_highest_score(
        self,
        candidates: list[tuple[list[Any], float]],
    ) -> list[Any]:
        """Select candidate with highest score."""
        # First candidate is assumed to be original
        original_tokens, original_score = candidates[0]

        best_tokens = original_tokens
        best_score = original_score

        for tokens, score in candidates[1:]:
            # Require minimum improvement to prefer alternative
            if score > best_score + self.min_improvement:
                best_tokens = tokens
                best_score = score

        return best_tokens

    def _select_confidence_weighted(
        self,
        candidates: list[tuple[list[Any], float]],
    ) -> list[Any]:
        """Select with confidence weighting."""
        original_tokens, original_score = candidates[0]

        # Calculate confidence-weighted scores
        weighted_candidates = []
        for tokens, score in candidates:
            if tokens:
                avg_conf = sum(
                    getattr(t, "confidence", 0.5) for t in tokens
                ) / len(tokens)
                weighted_score = score * (0.5 + 0.5 * avg_conf)
                weighted_candidates.append((tokens, weighted_score))

        if not weighted_candidates:
            return original_tokens

        # Select highest weighted score with improvement threshold
        best_tokens, best_score = weighted_candidates[0]
        for tokens, score in weighted_candidates[1:]:
            if score > best_score + self.min_improvement:
                best_tokens = tokens
                best_score = score

        return best_tokens

    def _select_consensus(
        self,
        candidates: list[tuple[list[Any], float]],
    ) -> list[Any]:
        """Select based on consensus (word overlap)."""
        if len(candidates) < 2:
            return candidates[0][0] if candidates else []

        original_tokens = candidates[0][0]

        # Build word frequency from all candidates
        word_freq: dict[str, int] = {}
        for tokens, _ in candidates:
            for token in tokens:
                word = getattr(token, "word", str(token)).lower()
                word_freq[word] = word_freq.get(word, 0) + 1

        # Score each candidate by consensus
        consensus_scores = []
        for tokens, base_score in candidates:
            consensus = sum(
                word_freq.get(getattr(t, "word", str(t)).lower(), 0)
                for t in tokens
            )
            combined_score = base_score + 0.1 * (consensus / len(candidates))
            consensus_scores.append((tokens, combined_score))

        # Select best
        best_tokens = original_tokens
        best_score = consensus_scores[0][1] if consensus_scores else 0

        for tokens, score in consensus_scores[1:]:
            if score > best_score + self.min_improvement:
                best_tokens = tokens
                best_score = score

        return best_tokens
