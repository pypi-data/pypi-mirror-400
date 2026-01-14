"""
Domain Term Matcher
===================

Matches and corrects domain-specific terminology.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


@dataclass
class TermMatch:
    """Represents a matched term."""

    start_idx: int
    end_idx: int
    original_text: str
    canonical_form: str
    match_score: float
    match_type: str  # "exact", "fuzzy", "phonetic"


class DomainTermMatcher:
    """
    Matches domain terms in ASR output.

    Uses multiple matching strategies:
        - Exact matching
        - Fuzzy matching (Levenshtein distance)
        - Phonetic matching (Soundex/Metaphone)

    Attributes:
        fuzzy_threshold: Minimum similarity for fuzzy matches
        use_phonetic: Whether to use phonetic matching
    """

    def __init__(
        self,
        fuzzy_threshold: float = 0.8,
        use_phonetic: bool = True,
    ):
        """
        Initialize the term matcher.

        Args:
            fuzzy_threshold: Fuzzy match threshold (0-1)
            use_phonetic: Enable phonetic matching
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.use_phonetic = use_phonetic

    def match(
        self,
        tokens: list[WordToken],
        lexicon: dict[str, list[str]],
    ) -> list[TermMatch]:
        """
        Find domain term matches in tokens.

        Args:
            tokens: List of WordToken objects
            lexicon: Domain lexicon (term -> variants)

        Returns:
            List of TermMatch objects
        """
        matches: list[TermMatch] = []

        # Build reverse index: variant -> canonical
        variant_map = self._build_variant_map(lexicon)

        # Single word matching
        for i, token in enumerate(tokens):
            word_lower = token.word.lower()

            # Exact match
            if word_lower in variant_map:
                matches.append(TermMatch(
                    start_idx=i,
                    end_idx=i,
                    original_text=token.word,
                    canonical_form=variant_map[word_lower],
                    match_score=1.0,
                    match_type="exact",
                ))
                continue

            # Fuzzy match
            fuzzy_match = self._fuzzy_match(word_lower, variant_map)
            if fuzzy_match:
                matches.append(TermMatch(
                    start_idx=i,
                    end_idx=i,
                    original_text=token.word,
                    canonical_form=fuzzy_match[0],
                    match_score=fuzzy_match[1],
                    match_type="fuzzy",
                ))

        # Multi-word phrase matching
        phrase_matches = self._match_phrases(tokens, lexicon)
        matches.extend(phrase_matches)

        return matches

    def _build_variant_map(
        self,
        lexicon: dict[str, list[str]],
    ) -> dict[str, str]:
        """Build variant to canonical mapping."""
        variant_map: dict[str, str] = {}

        for canonical, variants in lexicon.items():
            canonical_lower = canonical.lower()
            variant_map[canonical_lower] = canonical

            for variant in variants:
                variant_map[variant.lower()] = canonical

        return variant_map

    def _fuzzy_match(
        self,
        word: str,
        variant_map: dict[str, str],
    ) -> tuple[str, float] | None:
        """Find fuzzy match for word."""
        best_match = None
        best_score = 0.0

        for variant, canonical in variant_map.items():
            score = self._levenshtein_similarity(word, variant)
            if score >= self.fuzzy_threshold and score > best_score:
                best_score = score
                best_match = canonical

        if best_match:
            return (best_match, best_score)
        return None

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate Levenshtein similarity (1 - normalized distance).

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score (0-1)
        """
        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        len1, len2 = len(s1), len(s2)

        # Create distance matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,      # deletion
                    matrix[i][j - 1] + 1,      # insertion
                    matrix[i - 1][j - 1] + cost,  # substitution
                )

        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)

    def _match_phrases(
        self,
        tokens: list[WordToken],
        lexicon: dict[str, list[str]],
    ) -> list[TermMatch]:
        """Match multi-word phrases."""
        matches: list[TermMatch] = []

        # Get all phrases from lexicon
        phrases = {}
        for canonical, variants in lexicon.items():
            if " " in canonical:
                phrases[canonical.lower()] = canonical
            for variant in variants:
                if " " in variant:
                    phrases[variant.lower()] = canonical

        if not phrases:
            return matches

        # Sliding window for phrases
        max_phrase_len = max(len(p.split()) for p in phrases)

        for i in range(len(tokens)):
            for length in range(2, min(max_phrase_len + 1, len(tokens) - i + 1)):
                phrase_words = [t.word for t in tokens[i : i + length]]
                phrase = " ".join(phrase_words).lower()

                if phrase in phrases:
                    matches.append(TermMatch(
                        start_idx=i,
                        end_idx=i + length - 1,
                        original_text=" ".join(phrase_words),
                        canonical_form=phrases[phrase],
                        match_score=1.0,
                        match_type="exact",
                    ))

        return matches
