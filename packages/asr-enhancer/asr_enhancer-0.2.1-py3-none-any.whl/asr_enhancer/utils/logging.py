"""
Logging Utilities
=================

Structured logging for the ASR Enhancement Layer.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional


# Global logger cache
_loggers: dict[str, logging.Logger] = {}


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string
        log_file: Optional file path for logging
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Configure root logger
    root_logger = logging.getLogger("asr_enhancer")
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    if name in _loggers:
        return _loggers[name]

    # Create child logger
    if name.startswith("asr_enhancer"):
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(f"asr_enhancer.{name}")

    _loggers[name] = logger
    return logger


class LogContext:
    """
    Context manager for structured logging with additional context.

    Usage:
        with LogContext(logger, request_id="123"):
            logger.info("Processing request")
    """

    def __init__(self, logger: logging.Logger, **context):
        """
        Initialize log context.

        Args:
            logger: Logger instance
            **context: Additional context fields
        """
        self.logger = logger
        self.context = context
        self._old_factory = None

    def __enter__(self):
        """Enter context."""
        self._old_factory = logging.getLogRecordFactory()

        context = self.context

        def record_factory(*args, **kwargs):
            record = self._old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if self._old_factory:
            logging.setLogRecordFactory(self._old_factory)
        return False


def log_performance(logger: logging.Logger, operation: str):
    """
    Decorator for logging operation performance.

    Args:
        logger: Logger instance
        operation: Operation name

    Usage:
        @log_performance(logger, "enhance_transcript")
        async def enhance(...):
            ...
    """
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"{operation} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"{operation} failed after {elapsed:.3f}s: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"{operation} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"{operation} failed after {elapsed:.3f}s: {e}")
                raise

        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def asyncio_iscoroutinefunction(func) -> bool:
    """Check if function is async."""
    import asyncio
    return asyncio.iscoroutinefunction(func)
