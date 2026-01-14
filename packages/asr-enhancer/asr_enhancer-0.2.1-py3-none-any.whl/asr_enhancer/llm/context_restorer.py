"""
LLM Context Restorer
====================

LLM-based contextual polishing with anti-hallucination safeguards.
"""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .prompt_templates import PromptTemplates
from .providers import LLMProvider, get_provider

if TYPE_CHECKING:
    from ..core import WordToken


class LLMContextRestorer:
    """
    Restores context and fixes grammar using LLM.

    Key features:
        - Anti-hallucination safeguards
        - Number preservation
        - Domain context injection
        - Minimal edit distance goal

    Attributes:
        provider: LLM provider instance
        templates: Prompt templates
        max_retries: Maximum retry attempts
    """

    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llama3.1",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 2,
        temperature: float = 0.1,
    ):
        """
        Initialize the context restorer.

        Args:
            provider: LLM provider name ("openai", "ollama", "anthropic")
            model: Model name
            api_key: API key (if required)
            base_url: Base URL for API (optional)
            max_retries: Maximum retry attempts
            temperature: Sampling temperature (lower = more deterministic)
        """
        self.provider = get_provider(
            provider_name=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
        self.templates = PromptTemplates()
        self.max_retries = max_retries
        self.temperature = temperature

    async def restore(
        self,
        tokens: list[WordToken],
        preserve_numbers: bool = True,
        domain_context: Optional[dict[str, Any]] = None,
        max_tokens: int = 2048,
    ) -> str:
        """
        Restore context and fix transcript.

        Args:
            tokens: List of WordToken objects
            preserve_numbers: Whether to preserve numeric sequences
            domain_context: Optional domain context
            max_tokens: Maximum output tokens

        Returns:
            Enhanced transcript text
        """
        # Build input text
        input_text = " ".join(t.word for t in tokens)

        # Extract numbers to preserve
        numbers_to_preserve = []
        if preserve_numbers:
            numbers_to_preserve = self._extract_numbers(tokens)

        # Build prompt
        prompt = self.templates.build_restoration_prompt(
            transcript=input_text,
            numbers=numbers_to_preserve,
            domain_context=domain_context,
        )

        # Call LLM
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.provider.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                )

                # Validate response
                enhanced_text = self._validate_response(
                    response,
                    input_text,
                    numbers_to_preserve,
                )

                if enhanced_text:
                    return enhanced_text

            except Exception as e:
                if attempt == self.max_retries:
                    # Fall back to original on final failure
                    return input_text
                continue

        return input_text

    def _extract_numbers(self, tokens: list[WordToken]) -> list[str]:
        """Extract numeric sequences from tokens."""
        import re

        numbers = []
        for token in tokens:
            # Match digits and number words
            if token.word.isdigit():
                numbers.append(token.word)
            elif re.match(r"^\d+[.,]\d+$", token.word):
                numbers.append(token.word)

        return numbers

    def _validate_response(
        self,
        response: str,
        original: str,
        numbers: list[str],
    ) -> Optional[str]:
        """
        Validate LLM response against constraints.

        Checks:
            - Numbers are preserved
            - Response is not too different from original
            - No obvious hallucinations
        """
        if not response or not response.strip():
            return None

        response = response.strip()

        # Check number preservation
        for num in numbers:
            if num not in response:
                # Number was lost - reject
                return None

        # Check for excessive changes
        original_words = set(original.lower().split())
        response_words = set(response.lower().split())

        # Calculate overlap
        overlap = len(original_words & response_words)
        original_len = len(original_words)

        if original_len > 0:
            overlap_ratio = overlap / original_len
            if overlap_ratio < 0.5:
                # Too many changes - likely hallucination
                return None

        return response

    async def fix_grammar(
        self,
        text: str,
        preserve_meaning: bool = True,
    ) -> str:
        """
        Fix grammar without changing meaning.

        Args:
            text: Input text
            preserve_meaning: Strict meaning preservation

        Returns:
            Grammar-corrected text
        """
        prompt = self.templates.build_grammar_prompt(
            text=text,
            preserve_meaning=preserve_meaning,
        )

        response = await self.provider.generate(
            prompt=prompt,
            max_tokens=len(text) * 2,
            temperature=0.1,
        )

        return response.strip() if response else text

    async def add_punctuation(self, text: str) -> str:
        """
        Add punctuation to unpunctuated text.

        Args:
            text: Input text without punctuation

        Returns:
            Punctuated text
        """
        prompt = self.templates.build_punctuation_prompt(text)

        response = await self.provider.generate(
            prompt=prompt,
            max_tokens=len(text) * 2,
            temperature=0.1,
        )

        return response.strip() if response else text
