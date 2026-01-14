"""
Vocabulary Corrector
====================

Applies vocabulary corrections to transcripts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken
    from .term_matcher import TermMatch


class VocabularyCorrector:
    """
    Applies vocabulary corrections to tokens.

    Handles:
        - Single word replacements
        - Multi-word phrase corrections
        - Preserving original case style

    Attributes:
        preserve_case: Whether to preserve original case style
        min_confidence: Minimum match score to apply correction
    """

    def __init__(
        self,
        preserve_case: bool = True,
        min_confidence: float = 0.7,
    ):
        """
        Initialize the vocabulary corrector.

        Args:
            preserve_case: Preserve original case style
            min_confidence: Minimum match score for correction
        """
        self.preserve_case = preserve_case
        self.min_confidence = min_confidence

    def correct(
        self,
        tokens: list[WordToken],
        matches: list[TermMatch],
    ) -> list[WordToken]:
        """
        Apply corrections to tokens.

        Args:
            tokens: List of WordToken objects
            matches: List of TermMatch objects

        Returns:
            Corrected token list
        """
        # Sort matches by position (reverse order for safe modification)
        sorted_matches = sorted(
            matches,
            key=lambda m: m.start_idx,
            reverse=True,
        )

        # Filter by confidence
        valid_matches = [
            m for m in sorted_matches
            if m.match_score >= self.min_confidence
        ]

        # Apply corrections
        for match in valid_matches:
            tokens = self._apply_match(tokens, match)

        return tokens

    def _apply_match(
        self,
        tokens: list[WordToken],
        match: TermMatch,
    ) -> list[WordToken]:
        """Apply a single match correction."""
        if match.start_idx == match.end_idx:
            # Single word replacement
            return self._replace_single(tokens, match)
        else:
            # Multi-word phrase replacement
            return self._replace_phrase(tokens, match)

    def _replace_single(
        self,
        tokens: list[WordToken],
        match: TermMatch,
    ) -> list[WordToken]:
        """Replace a single word."""
        idx = match.start_idx
        if idx >= len(tokens):
            return tokens

        original = tokens[idx]
        corrected_word = match.canonical_form

        if self.preserve_case:
            corrected_word = self._apply_case(
                corrected_word,
                original.word,
            )

        tokens[idx].word = corrected_word
        tokens[idx].is_corrected = True
        tokens[idx].correction_source = f"vocab_{match.match_type}"

        return tokens

    def _replace_phrase(
        self,
        tokens: list[WordToken],
        match: TermMatch,
    ) -> list[WordToken]:
        """Replace a multi-word phrase."""
        start = match.start_idx
        end = match.end_idx

        if start >= len(tokens):
            return tokens

        # Get original case style from first word
        original_first = tokens[start].word
        corrected_words = match.canonical_form.split()

        if self.preserve_case:
            corrected_words = [
                self._apply_case(w, original_first)
                for w in corrected_words
            ]

        # Create new tokens for the phrase
        original_tokens = tokens[start : end + 1]
        new_tokens: list[WordToken] = []

        for i, word in enumerate(corrected_words):
            if i < len(original_tokens):
                # Reuse timing from original token
                new_token = WordToken(
                    word=word,
                    start_time=original_tokens[i].start_time,
                    end_time=original_tokens[i].end_time,
                    confidence=original_tokens[i].confidence,
                    is_corrected=True,
                    correction_source=f"vocab_{match.match_type}",
                )
            else:
                # Estimate timing for extra words
                new_token = WordToken(
                    word=word,
                    start_time=original_tokens[-1].end_time,
                    end_time=original_tokens[-1].end_time,
                    confidence=0.8,
                    is_corrected=True,
                    correction_source=f"vocab_{match.match_type}",
                )
            new_tokens.append(new_token)

        # Replace tokens
        tokens = tokens[:start] + new_tokens + tokens[end + 1:]
        return tokens

    def _apply_case(self, target: str, reference: str) -> str:
        """Apply case style from reference to target."""
        if not reference:
            return target

        if reference.isupper():
            return target.upper()
        if reference.islower():
            return target.lower()
        if reference[0].isupper():
            return target.capitalize()

        return target


# Import WordToken for type hints
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
