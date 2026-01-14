"""
Completeness Validator
======================

Validates transcript completeness and integrity.
"""

from __future__ import annotations

import re
from typing import Any


class CompletenessValidator:
    """
    Validates transcript completeness.

    Checks:
        - Numeric sequence completeness
        - Sentence completeness
        - Key information preservation
        - Gap detection
    """

    def __init__(self):
        """Initialize the completeness validator."""
        pass

    def validate(
        self,
        enhanced_text: str,
        numeric_gaps: list[dict[str, Any]],
    ) -> bool:
        """
        Validate transcript completeness.

        Args:
            enhanced_text: Enhanced transcript
            numeric_gaps: Detected numeric gaps

        Returns:
            True if complete, False otherwise
        """
        # Check numeric completeness
        numeric_complete = self._check_numeric_completeness(
            enhanced_text, numeric_gaps
        )

        # Check sentence completeness
        sentence_complete = self._check_sentence_completeness(enhanced_text)

        # Overall completeness
        return numeric_complete and sentence_complete

    def _check_numeric_completeness(
        self,
        text: str,
        gaps: list[dict[str, Any]],
    ) -> bool:
        """Check if numeric sequences are complete."""
        for gap in gaps:
            gap_type = gap.get("gap_type", "general")
            expected_length = gap.get("expected_length")

            if expected_length is None:
                continue

            # Find the reconstructed number in text
            # This is a simplified check
            if gap_type == "phone":
                # Look for phone-like sequences
                phone_pattern = r"\b\d{10,15}\b"
                matches = re.findall(phone_pattern, re.sub(r"[^\d]", "", text))
                if not matches:
                    return False

            elif gap_type == "otp":
                # Look for OTP-like sequences
                otp_pattern = r"\b\d{4,8}\b"
                if not re.search(otp_pattern, text):
                    # May still be valid if spoken as words
                    pass

        return True

    def _check_sentence_completeness(self, text: str) -> bool:
        """Check if sentences are complete."""
        if not text.strip():
            return False

        # Check for trailing incomplete words
        words = text.split()
        if words and len(words[-1]) == 1 and words[-1].isalpha():
            return False

        # Check for balanced structure
        open_count = text.count("(") + text.count("[") + text.count("{")
        close_count = text.count(")") + text.count("]") + text.count("}")

        if open_count != close_count:
            return False

        return True

    def get_completeness_report(
        self,
        enhanced_text: str,
        original_tokens: list[Any],
        numeric_gaps: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Generate detailed completeness report.

        Args:
            enhanced_text: Enhanced transcript
            original_tokens: Original tokens
            numeric_gaps: Detected numeric gaps

        Returns:
            Detailed report dictionary
        """
        report = {
            "is_complete": True,
            "word_count": len(enhanced_text.split()),
            "original_word_count": len(original_tokens),
            "numeric_gaps_resolved": 0,
            "numeric_gaps_remaining": 0,
            "issues": [],
        }

        # Check word count change
        word_diff = report["word_count"] - report["original_word_count"]
        if abs(word_diff) > report["original_word_count"] * 0.3:
            report["issues"].append(
                f"Significant word count change: {word_diff:+d} words"
            )

        # Check numeric gaps
        for gap in numeric_gaps:
            gap_type = gap.get("gap_type", "general")
            detected_digits = gap.get("detected_digits", "")
            expected_length = gap.get("expected_length")

            if expected_length and len(detected_digits) >= expected_length:
                report["numeric_gaps_resolved"] += 1
            else:
                report["numeric_gaps_remaining"] += 1
                report["issues"].append(
                    f"Incomplete {gap_type} sequence: {detected_digits}"
                )

        if report["numeric_gaps_remaining"] > 0:
            report["is_complete"] = False

        # Check sentence structure
        if not self._check_sentence_completeness(enhanced_text):
            report["is_complete"] = False
            report["issues"].append("Incomplete sentence structure detected")

        return report

    def check_key_terms_preserved(
        self,
        enhanced_text: str,
        key_terms: list[str],
    ) -> dict[str, bool]:
        """
        Check if key terms are preserved.

        Args:
            enhanced_text: Enhanced transcript
            key_terms: List of key terms to check

        Returns:
            Dict mapping term -> preserved status
        """
        text_lower = enhanced_text.lower()
        return {term: term.lower() in text_lower for term in key_terms}
