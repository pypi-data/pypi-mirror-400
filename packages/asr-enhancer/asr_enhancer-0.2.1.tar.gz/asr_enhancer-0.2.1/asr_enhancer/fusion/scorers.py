"""
Scoring Functions
=================

Acoustic and language model scorers for hypothesis fusion.
"""

from __future__ import annotations

import math
from typing import Optional

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AcousticScorer:
    """
    Scores acoustic similarity between hypotheses.

    Uses phonetic similarity and edit distance metrics.
    """

    def __init__(self):
        """Initialize the acoustic scorer."""
        pass

    def score(
        self,
        original: str,
        candidate: str,
    ) -> float:
        """
        Score acoustic similarity between strings.

        Args:
            original: Original text
            candidate: Candidate text

        Returns:
            Similarity score (0-1)
        """
        if not original or not candidate:
            return 0.0

        if original.lower() == candidate.lower():
            return 1.0

        # Use phonetic similarity
        phonetic_sim = self._phonetic_similarity(original, candidate)

        # Use edit distance similarity
        edit_sim = self._edit_similarity(original, candidate)

        # Combine scores
        return 0.6 * phonetic_sim + 0.4 * edit_sim

    def _phonetic_similarity(self, s1: str, s2: str) -> float:
        """Calculate phonetic similarity using Soundex."""
        code1 = self._soundex(s1)
        code2 = self._soundex(s2)

        if code1 == code2:
            return 1.0

        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(code1, code2))
        return matches / max(len(code1), len(code2))

    def _soundex(self, word: str) -> str:
        """Calculate Soundex code for word."""
        if not word:
            return "0000"

        word = word.upper()

        # Soundex mapping
        mapping = {
            "B": "1", "F": "1", "P": "1", "V": "1",
            "C": "2", "G": "2", "J": "2", "K": "2",
            "Q": "2", "S": "2", "X": "2", "Z": "2",
            "D": "3", "T": "3",
            "L": "4",
            "M": "5", "N": "5",
            "R": "6",
        }

        # First letter
        code = word[0]

        # Process remaining letters
        prev_code = mapping.get(word[0], "0")
        for char in word[1:]:
            char_code = mapping.get(char, "0")
            if char_code != "0" and char_code != prev_code:
                code += char_code
            prev_code = char_code

            if len(code) >= 4:
                break

        # Pad with zeros
        code = (code + "0000")[:4]
        return code

    def _edit_similarity(self, s1: str, s2: str) -> float:
        """Calculate edit distance similarity."""
        len1, len2 = len(s1), len(s2)

        if len1 == 0 and len2 == 0:
            return 1.0

        # Create matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1].lower() == s2[j - 1].lower() else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j - 1] + cost,
                )

        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)


class LanguageModelScorer:
    """
    Scores text using language model perplexity.

    Uses a lightweight LM for scoring candidate hypotheses.
    """

    def __init__(
        self,
        model_name: str = "distilgpt2",
        device: Optional[str] = None,
    ):
        """
        Initialize the language model scorer.

        Args:
            model_name: HuggingFace model name
            device: Device for inference
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None

        if TRANSFORMERS_AVAILABLE:
            self._load_model()

    def _load_model(self) -> None:
        """Load the language model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            if self.device:
                self.model = self.model.to(self.device)

            self.model.eval()
        except Exception:
            # Model loading failed, use fallback scoring
            self.model = None
            self.tokenizer = None

    def score(self, text: str) -> float:
        """
        Score text fluency.

        Args:
            text: Text to score

        Returns:
            Fluency score (0-1, higher is better)
        """
        if not text:
            return 0.0

        if self.model is None:
            # Fallback: simple heuristic scoring
            return self._heuristic_score(text)

        try:
            perplexity = self._compute_perplexity(text)
            # Convert perplexity to score (lower perplexity = higher score)
            score = 1.0 / (1.0 + math.log(perplexity + 1))
            return min(1.0, max(0.0, score))
        except Exception:
            return self._heuristic_score(text)

    def _compute_perplexity(self, text: str) -> float:
        """Compute perplexity using the language model."""
        inputs = self.tokenizer(text, return_tensors="pt")

        if self.device:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss

        return math.exp(loss.item())

    def _heuristic_score(self, text: str) -> float:
        """Simple heuristic scoring without LM."""
        words = text.split()
        if not words:
            return 0.0

        # Penalize very short or very long words
        avg_word_len = sum(len(w) for w in words) / len(words)
        length_score = 1.0 if 3 <= avg_word_len <= 10 else 0.7

        # Penalize repetition
        unique_ratio = len(set(w.lower() for w in words)) / len(words)
        repetition_score = unique_ratio

        # Basic score
        return 0.5 * length_score + 0.5 * repetition_score
