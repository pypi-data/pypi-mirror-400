"""
Lexicon Loader
==============

Loads and manages domain-specific lexicons.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


class LexiconLoader:
    """
    Loads domain lexicons from various sources.

    Supports:
        - JSON files
        - In-memory dictionaries
        - Database backends (extensible)

    Lexicon format:
        {
            "domain": "medical",
            "terms": {
                "acetaminophen": ["tylenol", "paracetamol"],
                "ibuprofen": ["advil", "motrin"],
            },
            "phrases": {
                "blood pressure": ["bp"],
                "heart rate": ["hr", "pulse"],
            }
        }
    """

    def __init__(self):
        """Initialize the lexicon loader."""
        self._lexicons: dict[str, dict[str, Any]] = {}
        self._term_index: dict[str, list[str]] = {}
        self._phrase_index: dict[str, list[str]] = {}

    def load(self, source: str | dict[str, Any]) -> None:
        """
        Load lexicon from source.

        Args:
            source: Path to JSON file or dictionary
        """
        if isinstance(source, str):
            lexicon = self._load_from_file(source)
        else:
            lexicon = source

        self._process_lexicon(lexicon)

    def _load_from_file(self, path: str) -> dict[str, Any]:
        """Load lexicon from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _process_lexicon(self, lexicon: dict[str, Any]) -> None:
        """Process and index lexicon entries."""
        domain = lexicon.get("domain", "default")
        self._lexicons[domain] = lexicon

        # Index terms
        terms = lexicon.get("terms", {})
        for canonical, variants in terms.items():
            canonical_lower = canonical.lower()
            if canonical_lower not in self._term_index:
                self._term_index[canonical_lower] = []

            for variant in variants:
                variant_lower = variant.lower()
                self._term_index[variant_lower] = [canonical]

        # Index phrases
        phrases = lexicon.get("phrases", {})
        for canonical, variants in phrases.items():
            canonical_lower = canonical.lower()
            if canonical_lower not in self._phrase_index:
                self._phrase_index[canonical_lower] = []

            for variant in variants:
                variant_lower = variant.lower()
                self._phrase_index[variant_lower] = [canonical]

    def get_canonical(self, term: str) -> Optional[str]:
        """
        Get canonical form of a term.

        Args:
            term: Input term

        Returns:
            Canonical form or None if not found
        """
        term_lower = term.lower()

        if term_lower in self._term_index:
            matches = self._term_index[term_lower]
            return matches[0] if matches else None

        return None

    def get_phrase_canonical(self, phrase: str) -> Optional[str]:
        """
        Get canonical form of a phrase.

        Args:
            phrase: Input phrase

        Returns:
            Canonical form or None if not found
        """
        phrase_lower = phrase.lower()

        if phrase_lower in self._phrase_index:
            matches = self._phrase_index[phrase_lower]
            return matches[0] if matches else None

        return None

    def get_all_terms(self) -> list[str]:
        """Get all indexed terms."""
        return list(self._term_index.keys())

    def get_all_phrases(self) -> list[str]:
        """Get all indexed phrases."""
        return list(self._phrase_index.keys())

    def save(self, path: str, domain: str = "default") -> None:
        """
        Save lexicon to file.

        Args:
            path: Output path
            domain: Domain to save
        """
        if domain not in self._lexicons:
            raise ValueError(f"Domain not found: {domain}")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._lexicons[domain], f, indent=2)
