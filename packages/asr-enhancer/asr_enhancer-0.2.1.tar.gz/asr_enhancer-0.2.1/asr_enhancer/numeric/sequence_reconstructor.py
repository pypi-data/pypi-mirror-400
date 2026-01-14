"""
Sequence Reconstructor
======================

Reconstructs incomplete numeric sequences using rules and ML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken
    from .pattern_analyzer import NumericPattern


@dataclass
class ReconstructionResult:
    """Result of sequence reconstruction."""

    original: str
    reconstructed: str
    confidence: float
    method: str  # "rule", "acoustic", "llm", "hybrid"
    changes: list[dict[str, Any]]


class SequenceReconstructor:
    """
    Reconstructs incomplete numeric sequences.

    Uses multiple strategies:
        1. Rule-based reconstruction (pattern completion)
        2. Acoustic similarity matching
        3. LLM-based inference
        4. Hybrid combination

    Attributes:
        min_confidence: Minimum confidence for reconstruction
        use_llm_fallback: Whether to use LLM for ambiguous cases
    """

    # Common acoustic confusions: word -> [digit, word_form]
    # Use index 1 for word form, index 0 for digit form
    # English confusions
    ACOUSTIC_CONFUSIONS_EN = {
        "tree": ["3", "three"],
        "for": ["4", "four"],
        "won": ["1", "one"],
        "to": ["2", "two"],
        "too": ["2", "two"],
        "ate": ["8", "eight"],
        "sex": ["6", "six"],
        "niner": ["9", "nine"],
        "oh": ["0", "zero"],
        "fi": ["5", "five"],
        "sven": ["7", "seven"],
    }
    
    # Hindi/Hinglish confusions (transliterated and Devanagari)
    ACOUSTIC_CONFUSIONS_HI = {
        # English words misheard in Hindi context
        "टू": ["2", "दो"],
        "ट्री": ["3", "तीन"],
        "फोर": ["4", "चार"],
        "फाइव": ["5", "पांच"],
        "सिक्स": ["6", "छह"],
        "सेवन": ["7", "सात"],
        "एट": ["8", "आठ"],
        "नाइन": ["9", "नौ"],
        "नाइनर": ["9", "नौ"],
        "जीरो": ["0", "शून्य"],
        "वन": ["1", "एक"],
        "टेन": ["10", "दस"],
        # Transliterated confusions
        "tu": ["2", "do"],
        "fore": ["4", "char"],
        # Common Hindi ASR errors
        "इक": ["1", "एक"],
        "दौ": ["2", "दो"],
        "तिन": ["3", "तीन"],
        # Large numbers in Hindi
        "पचास": ["50", "पचास"],
        "सौ": ["100", "सौ"],
        "हज़ार": ["1000", "हज़ार"],
        "लाख": ["100000", "लाख"],
        "करोड़": ["10000000", "करोड़"],
    }
    
    # Combined confusions
    ACOUSTIC_CONFUSIONS = {**ACOUSTIC_CONFUSIONS_EN, **ACOUSTIC_CONFUSIONS_HI}

    # Pattern completion rules
    COMPLETION_RULES = {
        "phone": {
            "min_length": 10,
            "max_length": 15,
            "prefixes": ["91", "1", "44", "86"],
        },
        "otp": {
            "min_length": 4,
            "max_length": 8,
        },
    }

    def __init__(
        self,
        min_confidence: float = 0.5,
        use_llm_fallback: bool = True,
    ):
        """
        Initialize the sequence reconstructor.

        Args:
            min_confidence: Minimum confidence threshold
            use_llm_fallback: Use LLM for ambiguous cases
        """
        self.min_confidence = min_confidence
        self.use_llm_fallback = use_llm_fallback

    def correct_word(self, word: str) -> str:
        """
        Apply acoustic correction to a single word.
        
        This is a fast method for plain text processing.
        
        Args:
            word: Single word to correct
            
        Returns:
            Corrected word (or original if no correction)
        """
        word_lower = word.lower()
        
        # Check acoustic confusions
        if word_lower in self.ACOUSTIC_CONFUSIONS:
            # Return the word form (index 1), not the digit
            return self.ACOUSTIC_CONFUSIONS[word_lower][1]
        
        return word
        self.use_llm_fallback = use_llm_fallback

    def reconstruct(
        self,
        tokens: list[WordToken],
        patterns: list[NumericPattern],
    ) -> list[WordToken]:
        """
        Reconstruct numeric sequences in tokens.

        Args:
            tokens: List of WordToken objects
            patterns: Detected numeric patterns

        Returns:
            Updated token list with reconstructed numbers
        """
        # Work on a copy
        updated_tokens = list(tokens)

        for pattern in patterns:
            # Always try acoustic correction, not just for incomplete patterns
            result = self._reconstruct_pattern(pattern, updated_tokens)
            if result and result.confidence >= self.min_confidence:
                updated_tokens = self._apply_reconstruction(
                    updated_tokens, pattern, result
                )

        return updated_tokens

    def _reconstruct_pattern(
        self,
        pattern: NumericPattern,
        tokens: list[WordToken],
    ) -> ReconstructionResult | None:
        """Reconstruct a single pattern."""
        # Always try acoustic matching first - these are corrections we want to apply
        acoustic_result = self._acoustic_reconstruction(pattern, tokens)
        
        # Try rule-based for completeness checks
        rule_result = self._rule_based_reconstruction(pattern)
        
        # If we have acoustic corrections, prioritize them
        if acoustic_result and acoustic_result.changes:
            # Combine with rule result if available
            if rule_result:
                return self._hybrid_reconstruction(acoustic_result, rule_result)
            return acoustic_result
        
        # Fall back to rule-based
        if rule_result and rule_result.confidence >= 0.8:
            return rule_result

        return acoustic_result or rule_result

    def _rule_based_reconstruction(
        self,
        pattern: NumericPattern,
    ) -> ReconstructionResult | None:
        """Apply rule-based reconstruction."""
        digits = pattern.normalized_digits
        changes: list[dict[str, Any]] = []

        if pattern.pattern_type == "phone":
            rules = self.COMPLETION_RULES["phone"]

            # Check for missing country code
            if len(digits) == 10:
                # Likely missing country code
                return ReconstructionResult(
                    original=digits,
                    reconstructed=digits,  # Keep as-is, it's valid
                    confidence=0.9,
                    method="rule",
                    changes=[],
                )

            # Check for partial number
            if len(digits) < rules["min_length"]:
                # Cannot reliably complete
                return ReconstructionResult(
                    original=digits,
                    reconstructed=digits,
                    confidence=0.3,
                    method="rule",
                    changes=[{"type": "incomplete", "missing": rules["min_length"] - len(digits)}],
                )

        elif pattern.pattern_type == "otp":
            rules = self.COMPLETION_RULES["otp"]

            if rules["min_length"] <= len(digits) <= rules["max_length"]:
                return ReconstructionResult(
                    original=digits,
                    reconstructed=digits,
                    confidence=0.95,
                    method="rule",
                    changes=[],
                )

        return None

    def _acoustic_reconstruction(
        self,
        pattern: NumericPattern,
        tokens: list[WordToken],
    ) -> ReconstructionResult | None:
        """Apply acoustic-based reconstruction."""
        changes: list[dict[str, Any]] = []
        reconstructed = []

        for i in range(pattern.start_idx, pattern.end_idx + 1):
            if i < len(tokens):
                word = tokens[i].word.lower()

                if word in self.ACOUSTIC_CONFUSIONS:
                    # Acoustic confusion detected
                    # Use word form (index 1) for readable output
                    correction = self.ACOUSTIC_CONFUSIONS[word][1]
                    changes.append({
                        "idx": i,
                        "original": word,
                        "corrected": correction,
                        "digit": self.ACOUSTIC_CONFUSIONS[word][0],
                        "type": "acoustic_confusion",
                    })
                    reconstructed.append(self.ACOUSTIC_CONFUSIONS[word][0])  # digit for pattern
                elif word.isdigit():
                    reconstructed.append(word)
                else:
                    # Try to extract digit
                    digit = self._extract_digit(word)
                    if digit:
                        reconstructed.append(digit)

        if not changes:
            return None

        reconstructed_str = "".join(reconstructed)
        confidence = 0.7 + (0.1 * len(changes) / max(1, len(reconstructed)))

        return ReconstructionResult(
            original=pattern.normalized_digits,
            reconstructed=reconstructed_str,
            confidence=min(0.95, confidence),
            method="acoustic",
            changes=changes,
        )

    def _extract_digit(self, word: str) -> str | None:
        """Extract digit from word."""
        # Number word mapping
        number_words = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        }
        return number_words.get(word.lower())

    def _hybrid_reconstruction(
        self,
        rule_result: ReconstructionResult,
        acoustic_result: ReconstructionResult,
    ) -> ReconstructionResult:
        """Combine rule-based and acoustic results."""
        # Prefer the one with higher confidence
        if rule_result.confidence >= acoustic_result.confidence:
            base = rule_result
            other = acoustic_result
        else:
            base = acoustic_result
            other = rule_result

        # Merge changes
        all_changes = base.changes + other.changes

        return ReconstructionResult(
            original=base.original,
            reconstructed=base.reconstructed,
            confidence=(base.confidence + other.confidence) / 2,
            method="hybrid",
            changes=all_changes,
        )

    def _apply_reconstruction(
        self,
        tokens: list[WordToken],
        pattern: NumericPattern,
        result: ReconstructionResult,
    ) -> list[WordToken]:
        """Apply reconstruction to tokens."""
        for change in result.changes:
            if "idx" in change:
                idx = change["idx"]
                if idx < len(tokens):
                    tokens[idx].word = change["corrected"]
                    tokens[idx].is_corrected = True
                    tokens[idx].correction_source = result.method

        return tokens
