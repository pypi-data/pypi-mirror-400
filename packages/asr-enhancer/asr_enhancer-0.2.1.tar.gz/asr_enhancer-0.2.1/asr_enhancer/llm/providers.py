"""
LLM Providers
=============

Abstraction layer for different LLM providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from groq import AsyncGroq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize OpenAI provider.

        Args:
            model: Model name
            api_key: OpenAI API key
            base_url: Optional base URL for API
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.client = None

        if OPENAI_AVAILABLE and api_key:
            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
            )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text using OpenAI API."""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
        )

        return response.choices[0].message.content or ""

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return OPENAI_AVAILABLE and self.client is not None


class GroqProvider(LLMProvider):
    """Groq API provider (ultra-fast inference)."""

    def __init__(
        self,
        model: str = "llama-3.1-70b-versatile",
        api_key: Optional[str] = None,
    ):
        """
        Initialize Groq provider.

        Args:
            model: Model name (e.g., llama-3.1-70b-versatile, llama-3.1-8b-instant)
            api_key: Groq API key
        """
        self.model = model
        self.api_key = api_key
        self.client = None

        if GROQ_AVAILABLE and api_key:
            self.client = AsyncGroq(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text using Groq API."""
        if not self.client:
            raise RuntimeError("Groq client not initialized")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
        )

        return response.choices[0].message.content or ""

    def is_available(self) -> bool:
        """Check if Groq is available."""
        return GROQ_AVAILABLE and self.client is not None


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        """
        Initialize Ollama provider.

        Args:
            model: Model name
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text using Ollama API."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for Ollama provider")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not HTTPX_AVAILABLE:
            return False

        try:
            import httpx

            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(
        self,
        model: str = "claude-3-haiku-20240307",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize Anthropic provider.

        Args:
            model: Model name
            api_key: Anthropic API key
        """
        self.model = model
        self.api_key = api_key

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text using Anthropic API."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx is required for Anthropic provider")

        if not self.api_key:
            raise RuntimeError("Anthropic API key required")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", [{}])[0].get("text", "")

    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return HTTPX_AVAILABLE and bool(self.api_key)


def get_provider(
    provider_name: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> LLMProvider:
    """
    Factory function to get LLM provider.

    Args:
        provider_name: Provider name ("openai", "groq", "ollama", "anthropic")
        model: Model name
        api_key: API key (if required)
        base_url: Base URL (optional, not used for Groq)

    Returns:
        LLMProvider instance
    """
    providers = {
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "ollama": OllamaProvider,
        "anthropic": AnthropicProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")

    # Groq doesn't use base_url
    if provider_name == "groq":
        return providers[provider_name](model=model, api_key=api_key)
    
    return providers[provider_name](
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
