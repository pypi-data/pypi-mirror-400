"""
Perplexity Scorer
=================

Scores text quality using perplexity metrics.
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


class PerplexityScorer:
    """
    Scores text using language model perplexity.

    Lower perplexity indicates more natural/fluent text.

    Attributes:
        model: Language model
        tokenizer: Tokenizer
        device: Inference device
    """

    def __init__(
        self,
        model_name: str = "distilgpt2",
        device: Optional[str] = None,
    ):
        """
        Initialize the perplexity scorer.

        Args:
            model_name: HuggingFace model name
            device: Device for inference
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def _ensure_loaded(self) -> bool:
        """Ensure model is loaded."""
        if self._loaded:
            return self.model is not None

        if not TRANSFORMERS_AVAILABLE:
            self._loaded = True
            return False

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            if self.device:
                self.model = self.model.to(self.device)

            self.model.eval()
            self._loaded = True
            return True
        except Exception:
            self._loaded = True
            return False

    def score(self, text: str) -> float:
        """
        Compute perplexity for text.

        Args:
            text: Input text

        Returns:
            Perplexity value (lower is better)
        """
        if not text or not text.strip():
            return float("inf")

        if not self._ensure_loaded():
            # Fallback heuristic
            return self._heuristic_perplexity(text)

        try:
            return self._compute_perplexity(text)
        except Exception:
            return self._heuristic_perplexity(text)

    def _compute_perplexity(self, text: str) -> float:
        """Compute perplexity using the model."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        if self.device:
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss

        return math.exp(loss.item())

    def _heuristic_perplexity(self, text: str) -> float:
        """Estimate perplexity using heuristics."""
        words = text.split()
        if not words:
            return float("inf")

        # Base perplexity
        perplexity = 100.0

        # Adjust for word length
        avg_word_len = sum(len(w) for w in words) / len(words)
        if avg_word_len < 2 or avg_word_len > 12:
            perplexity *= 1.5

        # Adjust for repetition
        unique_ratio = len(set(w.lower() for w in words)) / len(words)
        if unique_ratio < 0.5:
            perplexity *= (2 - unique_ratio)

        # Adjust for punctuation
        punct_count = sum(1 for c in text if c in ".,!?;:")
        if punct_count == 0 and len(words) > 10:
            perplexity *= 1.2

        return perplexity

    def score_batch(self, texts: list[str]) -> list[float]:
        """
        Compute perplexity for multiple texts.

        Args:
            texts: List of texts

        Returns:
            List of perplexity values
        """
        return [self.score(text) for text in texts]

    def normalize_score(
        self,
        perplexity: float,
        max_perplexity: float = 1000.0,
    ) -> float:
        """
        Normalize perplexity to 0-1 score (higher is better).

        Args:
            perplexity: Raw perplexity value
            max_perplexity: Maximum expected perplexity

        Returns:
            Normalized score (0-1)
        """
        if perplexity <= 0:
            return 1.0
        if perplexity >= max_perplexity:
            return 0.0

        # Logarithmic scaling
        log_ppl = math.log(perplexity + 1)
        log_max = math.log(max_perplexity + 1)

        return 1.0 - (log_ppl / log_max)
