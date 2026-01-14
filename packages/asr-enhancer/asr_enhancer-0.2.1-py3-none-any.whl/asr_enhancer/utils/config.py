"""
Configuration Management
========================

Configuration loading and validation for the ASR Enhancement Layer.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class Config:
    """
    Configuration for ASR Enhancement Pipeline.

    Attributes:
        confidence_threshold: Threshold for low-confidence detection
        sliding_window_size: Window size for confidence smoothing
        secondary_asr_backend: Backend for re-ASR ("whisper", "riva")
        device: Inference device ("cpu", "cuda")
        llm_provider: LLM provider ("openai", "ollama", "anthropic")
        llm_model: LLM model name
        fusion_alpha: Weight for original ASR confidence
        fusion_beta: Weight for language model score
        fusion_gamma: Weight for acoustic similarity
        max_concurrent_requests: Maximum concurrent API requests
        log_level: Logging level
    """

    # Detection settings
    confidence_threshold: float = 0.7
    sliding_window_size: int = 3
    min_span_words: int = 1

    # Secondary ASR settings
    secondary_asr_backend: str = "whisper"
    secondary_asr_model: str = "tiny"
    device: str = "cpu"

    # LLM settings
    llm_provider: str = "ollama"
    llm_model: str = "llama3.1"
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # Fusion settings
    fusion_alpha: float = 0.4
    fusion_beta: float = 0.35
    fusion_gamma: float = 0.25

    # API settings
    max_concurrent_requests: int = 10
    request_timeout: float = 60.0
    enable_cors: bool = True

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Paths
    lexicon_dir: Optional[str] = None
    temp_dir: Optional[str] = None
    cache_dir: Optional[str] = None

    # Feature flags
    enable_re_asr: bool = True
    enable_llm_restoration: bool = True
    enable_numeric_reconstruction: bool = True
    enable_vocab_correction: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values."""
        if not 0 <= self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")

        if self.sliding_window_size < 1:
            raise ValueError("sliding_window_size must be at least 1")

        if self.secondary_asr_backend not in ("whisper", "riva", "vosk"):
            raise ValueError(f"Unknown secondary_asr_backend: {self.secondary_asr_backend}")

        if self.device not in ("cpu", "cuda", "mps"):
            raise ValueError(f"Unknown device: {self.device}")

        weights_sum = self.fusion_alpha + self.fusion_beta + self.fusion_gamma
        if abs(weights_sum - 1.0) > 0.01:
            # Normalize weights
            self.fusion_alpha /= weights_sum
            self.fusion_beta /= weights_sum
            self.fusion_gamma /= weights_sum

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "confidence_threshold": self.confidence_threshold,
            "sliding_window_size": self.sliding_window_size,
            "min_span_words": self.min_span_words,
            "secondary_asr_backend": self.secondary_asr_backend,
            "secondary_asr_model": self.secondary_asr_model,
            "device": self.device,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "llm_max_tokens": self.llm_max_tokens,
            "fusion_alpha": self.fusion_alpha,
            "fusion_beta": self.fusion_beta,
            "fusion_gamma": self.fusion_gamma,
            "max_concurrent_requests": self.max_concurrent_requests,
            "request_timeout": self.request_timeout,
            "enable_cors": self.enable_cors,
            "log_level": self.log_level,
            "enable_re_asr": self.enable_re_asr,
            "enable_llm_restoration": self.enable_llm_restoration,
            "enable_numeric_reconstruction": self.enable_numeric_reconstruction,
            "enable_vocab_correction": self.enable_vocab_correction,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


def load_config(path: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment.

    Priority:
        1. Explicit path argument
        2. ASR_ENHANCER_CONFIG environment variable
        3. ./config.json
        4. ~/.asr_enhancer/config.json
        5. Default values

    Args:
        path: Optional path to config file

    Returns:
        Config instance
    """
    config_paths = []

    if path:
        config_paths.append(Path(path))

    env_path = os.environ.get("ASR_ENHANCER_CONFIG")
    if env_path:
        config_paths.append(Path(env_path))

    config_paths.extend([
        Path("./config.json"),
        Path("./asr_enhancer.json"),
        Path.home() / ".asr_enhancer" / "config.json",
    ])

    for config_path in config_paths:
        if config_path.exists():
            with open(config_path, "r") as f:
                data = json.load(f)
            return Config.from_dict(data)

    # Load from environment variables
    return _load_from_env()


def _load_from_env() -> Config:
    """Load configuration from environment variables."""
    config = Config()

    env_mapping = {
        "ASR_CONFIDENCE_THRESHOLD": ("confidence_threshold", float),
        "ASR_WINDOW_SIZE": ("sliding_window_size", int),
        "ASR_SECONDARY_BACKEND": ("secondary_asr_backend", str),
        "ASR_DEVICE": ("device", str),
        "ASR_LLM_PROVIDER": ("llm_provider", str),
        "ASR_LLM_MODEL": ("llm_model", str),
        "ASR_LLM_API_KEY": ("llm_api_key", str),
        "ASR_LOG_LEVEL": ("log_level", str),
    }

    for env_var, (attr, type_fn) in env_mapping.items():
        value = os.environ.get(env_var)
        if value is not None:
            setattr(config, attr, type_fn(value))

    return config
