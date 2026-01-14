"""
Text Utilities
==============

Text processing utilities for the ASR Enhancement Layer.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Tuple


class TextUtils:
    """
    Text processing utilities.

    Provides:
        - Text normalization
        - Tokenization
        - Number conversion
        - Punctuation handling
    """

    # Number words for conversion
    NUMBER_WORDS = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
        "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
        "million": 1000000, "billion": 1000000000,
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Normalize text for comparison.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Unicode normalization
        text = unicodedata.normalize("NFKC", text)

        # Lowercase
        text = text.lower()

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Split on whitespace and punctuation
        tokens = re.findall(r"\b\w+\b|[^\w\s]", text)
        return tokens

    @classmethod
    def words_to_number(cls, words: List[str]) -> int | None:
        """
        Convert number words to integer.

        Args:
            words: List of number words

        Returns:
            Integer value or None if conversion fails
        """
        if not words:
            return None

        total = 0
        current = 0

        for word in words:
            word_lower = word.lower()

            if word_lower not in cls.NUMBER_WORDS:
                # Check if it's a digit
                if word.isdigit():
                    current = current * 10 + int(word)
                    continue
                return None

            value = cls.NUMBER_WORDS[word_lower]

            if value == 100:
                current = current * 100 if current else 100
            elif value >= 1000:
                current = current * value if current else value
                total += current
                current = 0
            else:
                current += value

        return total + current

    @classmethod
    def number_to_words(cls, number: int) -> str:
        """
        Convert integer to number words.

        Args:
            number: Integer value

        Returns:
            Number as words
        """
        if number == 0:
            return "zero"

        if number < 0:
            return "minus " + cls.number_to_words(-number)

        # Reverse mapping
        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                "sixteen", "seventeen", "eighteen", "nineteen"]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        def convert_chunk(n: int) -> str:
            if n == 0:
                return ""
            if n < 10:
                return ones[n]
            if n < 20:
                return teens[n - 10]
            if n < 100:
                return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")
            return ones[n // 100] + " hundred" + (" " + convert_chunk(n % 100) if n % 100 else "")

        result = []

        if number >= 1000000000:
            result.append(convert_chunk(number // 1000000000) + " billion")
            number %= 1000000000

        if number >= 1000000:
            result.append(convert_chunk(number // 1000000) + " million")
            number %= 1000000

        if number >= 1000:
            result.append(convert_chunk(number // 1000) + " thousand")
            number %= 1000

        if number > 0:
            result.append(convert_chunk(number))

        return " ".join(result)

    @classmethod
    def extract_numbers(cls, text: str) -> List[Tuple[str, int, int]]:
        """
        Extract numeric sequences from text.

        Args:
            text: Input text

        Returns:
            List of (number_string, start_pos, end_pos) tuples
        """
        numbers = []

        # Find digit sequences
        for match in re.finditer(r"\d+(?:[.,]\d+)?", text):
            numbers.append((match.group(), match.start(), match.end()))

        return numbers

    @classmethod
    def add_punctuation_simple(cls, text: str) -> str:
        """
        Add basic punctuation to text (simple rule-based).

        Args:
            text: Unpunctuated text

        Returns:
            Text with basic punctuation
        """
        if not text:
            return text

        # Ensure first letter is capitalized
        text = text[0].upper() + text[1:] if text else text

        # Add period at end if missing
        if text and text[-1] not in ".!?":
            text += "."

        return text

    @classmethod
    def clean_transcript(cls, text: str) -> str:
        """
        Clean ASR transcript output.

        Args:
            text: Raw transcript

        Returns:
            Cleaned transcript
        """
        # Remove filler words
        fillers = ["um", "uh", "er", "ah", "like", "you know", "i mean"]
        text_lower = text.lower()

        for filler in fillers:
            pattern = r"\b" + re.escape(filler) + r"\b"
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Remove repeated words
        text = re.sub(r"\b(\w+)( \1)+\b", r"\1", text, flags=re.IGNORECASE)

        # Clean up whitespace
        text = " ".join(text.split())

        return text

    @classmethod
    def levenshtein_distance(cls, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein edit distance.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance
        """
        if len(s1) < len(s2):
            return cls.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @classmethod
    def similarity(cls, s1: str, s2: str) -> float:
        """
        Calculate string similarity (0-1).

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        distance = cls.levenshtein_distance(s1.lower(), s2.lower())
        max_len = max(len(s1), len(s2))

        return 1.0 - (distance / max_len)
