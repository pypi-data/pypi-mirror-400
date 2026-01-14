"""
Numeric Pattern Analyzer
========================

Analyzes and detects numeric patterns in transcripts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WordToken


@dataclass
class NumericPattern:
    """Represents a detected numeric pattern."""

    pattern_type: str  # "phone", "otp", "amount", "date", "time", "id", "general"
    start_idx: int
    end_idx: int
    raw_text: str
    normalized_digits: str
    confidence: float
    is_complete: bool
    expected_format: str | None


class NumericPatternAnalyzer:
    """
    Analyzes numeric patterns in ASR output.

    Identifies and categorizes numeric sequences based on
    context and format patterns.
    
    Supports English and Hindi number words.

    Pattern types:
        - phone: Phone numbers (10-15 digits)
        - otp: One-time passwords (4-8 digits)
        - amount: Currency amounts
        - date: Date formats
        - time: Time formats
        - id: ID numbers (various formats)
        - general: Other numeric sequences
    """

    # English number word mappings
    NUMBER_WORDS_EN = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
        "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
        "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
        "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000",
        "million": "1000000", "billion": "1000000000",
        # Common ASR misrecognitions
        "tree": "3", "for": "4", "won": "1", "to": "2", "too": "2",
        "ate": "8", "niner": "9", "oh": "0",
    }
    
    # Hindi number word mappings (Devanagari and transliterated)
    NUMBER_WORDS_HI = {
        # Devanagari
        "शून्य": "0", "एक": "1", "दो": "2", "तीन": "3", "चार": "4",
        "पांच": "5", "छह": "6", "सात": "7", "आठ": "8", "नौ": "9",
        "दस": "10", "ग्यारह": "11", "बारह": "12", "तेरह": "13",
        "चौदह": "14", "पंद्रह": "15", "सोलह": "16", "सत्रह": "17",
        "अठारह": "18", "उन्नीस": "19", "बीस": "20", "तीस": "30",
        "चालीस": "40", "पचास": "50", "साठ": "60", "सत्तर": "70",
        "अस्सी": "80", "नब्बे": "90", "सौ": "100", "हज़ार": "1000",
        "लाख": "100000", "करोड़": "10000000",
        # Transliterated Hindi
        "ek": "1", "do": "2", "teen": "3", "char": "4", "paanch": "5",
        "chhe": "6", "saat": "7", "aath": "8", "nau": "9", "das": "10",
        "gyarah": "11", "barah": "12", "terah": "13", "chaudah": "14",
        "pandrah": "15", "solah": "16", "satrah": "17", "atharah": "18",
        "unnis": "19", "bees": "20", "tees": "30", "chaalis": "40",
        "pachaas": "50", "saath": "60", "sattar": "70", "assi": "80",
        "nabbe": "90", "sau": "100", "hazaar": "1000", "lakh": "100000",
        "crore": "10000000", "karod": "10000000",
        # Common Hindi ASR misrecognitions / English-Hindi code-mixing
        "टू": "2", "ट्री": "3", "फोर": "4", "फाइव": "5",
        "सिक्स": "6", "सेवन": "7", "एट": "8", "नाइन": "9",
        "जीरो": "0", "वन": "1", "टेन": "10",
    }
    
    # Combined mappings
    NUMBER_WORDS = {**NUMBER_WORDS_EN, **NUMBER_WORDS_HI}

    # Pattern contexts
    CONTEXT_PATTERNS = {
        "phone": [
            r"phone", r"mobile", r"cell", r"contact", r"call",
            r"number", r"dial", r"reach",
        ],
        "otp": [
            r"otp", r"code", r"pin", r"verification", r"password",
            r"one\s*time", r"security",
        ],
        "amount": [
            r"dollar", r"rupee", r"euro", r"pound", r"rs\.?",
            r"amount", r"price", r"cost", r"pay", r"₹", r"\$", r"€", r"£",
        ],
        "date": [
            r"date", r"day", r"month", r"year", r"january", r"february",
            r"march", r"april", r"may", r"june", r"july", r"august",
            r"september", r"october", r"november", r"december",
        ],
        "time": [
            r"time", r"clock", r"hour", r"minute", r"second",
            r"a\.?m\.?", r"p\.?m\.?", r"o'clock",
        ],
        "id": [
            r"id", r"number", r"account", r"reference", r"order",
            r"tracking", r"confirmation",
        ],
    }

    def __init__(self):
        """Initialize the pattern analyzer."""
        # Compile context patterns
        self.context_regexes = {
            ptype: re.compile("|".join(patterns), re.IGNORECASE)
            for ptype, patterns in self.CONTEXT_PATTERNS.items()
        }

    def analyze(self, tokens: list[WordToken]) -> list[NumericPattern]:
        """
        Analyze tokens for numeric patterns.

        Args:
            tokens: List of WordToken objects

        Returns:
            List of detected NumericPattern objects
        """
        patterns: list[NumericPattern] = []

        # Find all numeric sequences
        sequences = self._find_sequences(tokens)

        for seq in sequences:
            pattern = self._classify_pattern(seq, tokens)
            if pattern:
                patterns.append(pattern)

        return patterns

    def _find_sequences(self, tokens: list[WordToken]) -> list[dict[str, Any]]:
        """Find numeric sequences in tokens."""
        sequences = []
        i = 0

        while i < len(tokens):
            if self._is_numeric_word(tokens[i].word):
                start_idx = i
                words = []
                digits = []

                while i < len(tokens) and self._is_numeric_word(tokens[i].word):
                    word = tokens[i].word.lower()
                    words.append(tokens[i].word)

                    digit = self._word_to_digit(word)
                    if digit:
                        digits.append(digit)

                    i += 1

                # Only include sequences with actual digits
                if digits:
                    sequences.append({
                        "start_idx": start_idx,
                        "end_idx": i - 1,
                        "words": words,
                        "digits": digits,
                        "avg_confidence": sum(
                            tokens[j].confidence for j in range(start_idx, i)
                        ) / (i - start_idx),
                    })
            else:
                i += 1

        return sequences

    def _is_numeric_word(self, word: str) -> bool:
        """Check if word is numeric."""
        word_lower = word.lower()
        return word_lower in self.NUMBER_WORDS or word.isdigit()

    def _word_to_digit(self, word: str) -> str | None:
        """Convert word to digit string."""
        word_lower = word.lower()
        if word_lower in self.NUMBER_WORDS:
            return self.NUMBER_WORDS[word_lower]
        if word.isdigit():
            return word
        return None

    def _classify_pattern(
        self,
        seq: dict[str, Any],
        tokens: list[WordToken],
    ) -> NumericPattern | None:
        """Classify a numeric sequence."""
        # Get context
        ctx_start = max(0, seq["start_idx"] - 10)
        context = " ".join(t.word for t in tokens[ctx_start : seq["start_idx"]])

        # Determine type from context
        pattern_type = self._get_pattern_type(context)

        # Normalize digits
        normalized = "".join(seq["digits"])

        # Determine completeness
        is_complete = self._check_completeness(pattern_type, normalized)

        # Get expected format
        expected_format = self._get_expected_format(pattern_type)

        return NumericPattern(
            pattern_type=pattern_type,
            start_idx=seq["start_idx"],
            end_idx=seq["end_idx"],
            raw_text=" ".join(seq["words"]),
            normalized_digits=normalized,
            confidence=seq["avg_confidence"],
            is_complete=is_complete,
            expected_format=expected_format,
        )

    def _get_pattern_type(self, context: str) -> str:
        """Determine pattern type from context."""
        for ptype, regex in self.context_regexes.items():
            if regex.search(context):
                return ptype
        return "general"

    def _check_completeness(self, pattern_type: str, digits: str) -> bool:
        """Check if pattern is complete."""
        length = len(digits)

        if pattern_type == "phone":
            return 10 <= length <= 15
        if pattern_type == "otp":
            return 4 <= length <= 8
        if pattern_type == "date":
            return length >= 4  # At least MMDD
        if pattern_type == "time":
            return length >= 3  # At least HMM

        return True  # General patterns are always "complete"

    def _get_expected_format(self, pattern_type: str) -> str | None:
        """Get expected format for pattern type."""
        formats = {
            "phone": "10-15 digits",
            "otp": "4-8 digits",
            "date": "MMDDYYYY or similar",
            "time": "HHMM or HH:MM",
            "amount": "Numeric with optional decimals",
        }
        return formats.get(pattern_type)
