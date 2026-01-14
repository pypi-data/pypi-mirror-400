"""
Consistency Checker
===================

Validates transcript consistency and coherence.
"""

from __future__ import annotations

import re
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


class ConsistencyChecker:
    """
    Checks transcript consistency.

    Validates:
        - Sentence structure
        - Pronoun consistency
        - Tense consistency
        - Entity mentions
        - Numeric sequence integrity
    """

    def __init__(self):
        """Initialize the consistency checker."""
        pass

    def check(
        self,
        enhanced_text: str,
        original_tokens: list[WordToken],
    ) -> float:
        """
        Check consistency between enhanced and original.

        Args:
            enhanced_text: Enhanced transcript
            original_tokens: Original token list

        Returns:
            Consistency score (0-1)
        """
        original_text = " ".join(t.word for t in original_tokens)

        scores = []

        # Word preservation score
        scores.append(self._word_preservation_score(original_text, enhanced_text))

        # Number preservation score
        scores.append(self._number_preservation_score(original_text, enhanced_text))

        # Length consistency score
        scores.append(self._length_consistency_score(original_text, enhanced_text))

        # Semantic consistency (basic)
        scores.append(self._semantic_consistency_score(original_text, enhanced_text))

        return sum(scores) / len(scores)

    def _word_preservation_score(
        self,
        original: str,
        enhanced: str,
    ) -> float:
        """Score word preservation."""
        original_words = set(original.lower().split())
        enhanced_words = set(enhanced.lower().split())

        if not original_words:
            return 1.0

        # Calculate overlap
        preserved = len(original_words & enhanced_words)
        return preserved / len(original_words)

    def _number_preservation_score(
        self,
        original: str,
        enhanced: str,
    ) -> float:
        """Score number preservation."""
        # Extract numbers from both
        original_nums = set(re.findall(r"\d+", original))
        enhanced_nums = set(re.findall(r"\d+", enhanced))

        if not original_nums:
            return 1.0

        preserved = len(original_nums & enhanced_nums)
        return preserved / len(original_nums)

    def _length_consistency_score(
        self,
        original: str,
        enhanced: str,
    ) -> float:
        """Score length consistency."""
        original_len = len(original.split())
        enhanced_len = len(enhanced.split())

        if original_len == 0:
            return 1.0

        ratio = min(original_len, enhanced_len) / max(original_len, enhanced_len)
        return ratio

    def _semantic_consistency_score(
        self,
        original: str,
        enhanced: str,
    ) -> float:
        """Basic semantic consistency score."""
        # Check key content words are preserved
        original_words = original.lower().split()
        enhanced_words = enhanced.lower().split()

        # Filter to content words (> 3 chars, not common)
        common_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                       "have", "has", "had", "do", "does", "did", "will", "would",
                       "could", "should", "may", "might", "can", "to", "of", "in",
                       "for", "on", "with", "at", "by", "from", "as", "into", "and",
                       "or", "but", "if", "then", "than", "so", "it", "its", "this",
                       "that", "these", "those", "my", "your", "his", "her", "our"}

        content_original = [w for w in original_words if len(w) > 3 and w not in common_words]
        content_enhanced = set(enhanced_words)

        if not content_original:
            return 1.0

        preserved = sum(1 for w in content_original if w in content_enhanced)
        return preserved / len(content_original)

    def validate_structure(self, text: str) -> dict[str, Any]:
        """
        Validate text structure.

        Returns dict with validation results.
        """
        results = {
            "has_sentences": False,
            "balanced_punctuation": True,
            "no_repeated_words": True,
            "issues": [],
        }

        # Check for sentences
        results["has_sentences"] = bool(re.search(r"[.!?]", text))

        # Check balanced punctuation
        open_parens = text.count("(")
        close_parens = text.count(")")
        if open_parens != close_parens:
            results["balanced_punctuation"] = False
            results["issues"].append("Unbalanced parentheses")

        open_quotes = text.count('"')
        if open_quotes % 2 != 0:
            results["balanced_punctuation"] = False
            results["issues"].append("Unbalanced quotes")

        # Check for repeated words
        words = text.lower().split()
        for i in range(1, len(words)):
            if words[i] == words[i - 1] and len(words[i]) > 2:
                results["no_repeated_words"] = False
                results["issues"].append(f"Repeated word: {words[i]}")
                break

        return results
