"""
Numeric Gap Detector
====================

Detects missing or incomplete numeric sequences in ASR output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


@dataclass
class NumericGap:
    """Represents a detected numeric gap or incomplete sequence."""

    start_idx: int
    end_idx: int
    original_text: str
    gap_type: str  # "phone", "otp", "amount", "id", "general"
    expected_length: int | None
    detected_length: int
    confidence: float


class NumericGapDetector:
    """
    Detects incomplete or missing numeric sequences.

    Handles:
        - Phone numbers (10-15 digits)
        - OTP codes (4-8 digits)
        - Currency amounts
        - ID numbers
        - General numeric sequences

    Uses pattern matching and contextual cues to identify gaps.
    """

    # Number word mappings
    NUMBER_WORDS = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
        "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
        "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
        "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000",
        "million": "1000000", "billion": "1000000000",
        # Common misspellings
        "tree": "3", "for": "4", "fir": "5", "sex": "6", "ate": "8", "niner": "9",
    }

    # Context patterns that indicate numeric sequences
    PHONE_PATTERNS = [
        r"phone\s*(?:number)?",
        r"call\s*(?:me|us|at)?",
        r"mobile",
        r"contact",
        r"reach\s*(?:me|us)?",
    ]

    OTP_PATTERNS = [
        r"otp",
        r"one\s*time\s*(?:password|code)?",
        r"verification\s*code",
        r"pin\s*(?:code)?",
    ]

    AMOUNT_PATTERNS = [
        r"(?:dollar|rupee|euro|pound)s?",
        r"(?:rs\.?|₹|\$|€|£)",
        r"amount",
        r"price",
        r"cost",
        r"payment",
    ]

    def __init__(
        self,
        phone_length_range: tuple[int, int] = (10, 15),
        otp_length_range: tuple[int, int] = (4, 8),
    ):
        """
        Initialize the numeric gap detector.

        Args:
            phone_length_range: Expected phone number length range
            otp_length_range: Expected OTP length range
        """
        self.phone_length_range = phone_length_range
        self.otp_length_range = otp_length_range

        # Compile patterns
        self.phone_re = re.compile("|".join(self.PHONE_PATTERNS), re.IGNORECASE)
        self.otp_re = re.compile("|".join(self.OTP_PATTERNS), re.IGNORECASE)
        self.amount_re = re.compile("|".join(self.AMOUNT_PATTERNS), re.IGNORECASE)
        self.digit_re = re.compile(r"\d+")

    def detect(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """
        Detect numeric gaps in token list.

        Args:
            tokens: List of WordToken objects

        Returns:
            List of numeric gap dictionaries
        """
        gaps: list[dict[str, Any]] = []

        # Find numeric sequences
        sequences = self._find_numeric_sequences(tokens)

        for seq in sequences:
            gap_info = self._analyze_sequence(seq, tokens)
            if gap_info:
                gaps.append(gap_info)

        return gaps

    def _find_numeric_sequences(
        self,
        tokens: list[WordToken],
    ) -> list[dict[str, Any]]:
        """Find all numeric sequences in tokens."""
        sequences = []
        i = 0

        while i < len(tokens):
            if self._is_numeric_token(tokens[i]):
                start_idx = i
                digits = []
                original_words = []

                while i < len(tokens) and self._is_numeric_token(tokens[i]):
                    word = tokens[i].word.lower()
                    original_words.append(tokens[i].word)

                    # Extract digits
                    if word in self.NUMBER_WORDS:
                        digits.append(self.NUMBER_WORDS[word])
                    elif self.digit_re.match(word):
                        digits.append(word)

                    i += 1

                sequences.append({
                    "start_idx": start_idx,
                    "end_idx": i - 1,
                    "digits": digits,
                    "original_words": original_words,
                    "avg_confidence": sum(
                        tokens[j].confidence for j in range(start_idx, i)
                    ) / (i - start_idx),
                })
            else:
                i += 1

        return sequences

    def _is_numeric_token(self, token: WordToken) -> bool:
        """Check if token represents a number."""
        word = token.word.lower()
        return word in self.NUMBER_WORDS or bool(self.digit_re.match(word))

    def _analyze_sequence(
        self,
        seq: dict[str, Any],
        tokens: list[WordToken],
    ) -> dict[str, Any] | None:
        """Analyze a numeric sequence for gaps."""
        # Get context before sequence
        context_start = max(0, seq["start_idx"] - 5)
        context_words = " ".join(t.word for t in tokens[context_start : seq["start_idx"]])

        # Determine sequence type
        seq_type = self._determine_sequence_type(context_words)

        # Calculate digit count
        digit_str = "".join(seq["digits"])
        detected_length = len(digit_str)

        # Determine expected length
        expected_length = self._get_expected_length(seq_type)

        # Check if there's a gap
        is_gap = False
        if expected_length:
            is_gap = detected_length < expected_length[0]
        elif detected_length > 0 and seq["avg_confidence"] < 0.6:
            # Low confidence numeric sequence
            is_gap = True

        if not is_gap:
            return None

        return {
            "start_idx": seq["start_idx"],
            "end_idx": seq["end_idx"],
            "original_text": " ".join(seq["original_words"]),
            "detected_digits": digit_str,
            "gap_type": seq_type,
            "expected_length": expected_length[0] if expected_length else None,
            "detected_length": detected_length,
            "confidence": seq["avg_confidence"],
            "start_time": tokens[seq["start_idx"]].start_time,
            "end_time": tokens[seq["end_idx"]].end_time,
        }

    def _determine_sequence_type(self, context: str) -> str:
        """Determine the type of numeric sequence from context."""
        if self.phone_re.search(context):
            return "phone"
        if self.otp_re.search(context):
            return "otp"
        if self.amount_re.search(context):
            return "amount"
        return "general"

    def _get_expected_length(self, seq_type: str) -> tuple[int, int] | None:
        """Get expected length range for sequence type."""
        if seq_type == "phone":
            return self.phone_length_range
        if seq_type == "otp":
            return self.otp_length_range
        return None
