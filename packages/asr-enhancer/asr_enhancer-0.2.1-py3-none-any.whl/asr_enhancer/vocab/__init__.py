"""
Domain Vocabulary Module
========================

Domain-specific vocabulary injection and terminology correction.
"""

from .lexicon_loader import LexiconLoader
from .term_matcher import DomainTermMatcher
from .corrector import VocabularyCorrector

__all__ = ["LexiconLoader", "DomainTermMatcher", "VocabularyCorrector"]
