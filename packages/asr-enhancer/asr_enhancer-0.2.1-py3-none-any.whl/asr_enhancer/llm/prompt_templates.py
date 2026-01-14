"""
Prompt Templates
================

Templates for LLM prompts with anti-hallucination safeguards.
Supports English, Hindi, and code-mixed (Hinglish) transcripts.
"""

from __future__ import annotations

from typing import Any, Optional


class PromptTemplates:
    """
    Manages prompt templates for LLM operations.

    All prompts are designed with anti-hallucination safeguards:
        - Explicit constraints on output
        - Examples of valid/invalid responses
        - Number preservation rules
        - Grounding to source text
    
    Supports:
        - English transcripts
        - Hindi transcripts (Devanagari)
        - Code-mixed Hinglish transcripts
    """

    # System prompt for transcript restoration (Multilingual)
    RESTORATION_SYSTEM = """You are an expert transcript editor for ASR (Automatic Speech Recognition) output. Your task is to fix transcription errors while preserving the speaker's original meaning.

You handle transcripts in:
- English
- Hindi (हिंदी) 
- Hinglish (code-mixed Hindi-English)

STRICT RULES:
1. NEVER add information not present in the original transcript
2. NEVER change or remove numbers, amounts, or numeric sequences
3. ONLY fix obvious ASR errors:
   - Misheard words (e.g., "tree" → "three", "टू" → "दो")
   - Grammar issues
   - Punctuation
4. Preserve code-switching patterns (if speaker mixes Hindi and English, keep it mixed)
5. Keep the same speaking style and tone
6. If unsure about a correction, keep the original word
7. Output ONLY the corrected transcript, no explanations

Common Hindi ASR errors to fix:
- एक/इक → एक (one)
- दो/टू → दो (two)  
- तीन/ट्री → तीन (three)
- चार/फोर → चार (four)
- पांच/फाइव → पांच (five)
- छह/सिक्स → छह (six)
- सात/सेवन → सात (seven)
- आठ/एट → आठ (eight)
- नौ/नाइन → नौ (nine)
- शून्य/जीरो → शून्य (zero)"""

    # System prompt for grammar correction
    GRAMMAR_SYSTEM = """You are a grammar correction assistant for English and Hindi text. Fix grammar and punctuation errors without changing the meaning or adding new content.

RULES:
1. Fix grammar errors only
2. Add appropriate punctuation
3. Do not add, remove, or rephrase content
4. Preserve all numbers and proper nouns exactly
5. For Hindi text, maintain correct मात्रा (vowel marks)
6. For Hinglish, maintain the code-switching pattern
7. Output ONLY the corrected text"""

    # System prompt for punctuation
    PUNCTUATION_SYSTEM = """You are a punctuation assistant. Add punctuation to the text without changing any words.

RULES:
1. Add periods, commas, question marks, and other punctuation
2. For Hindi, use पूर्ण विराम (।) instead of period
3. Do not change, add, or remove any words
4. Preserve the exact wording
5. Output ONLY the punctuated text"""

    # Hindi-specific restoration prompt
    HINDI_RESTORATION_SYSTEM = """आप एक ASR (Automatic Speech Recognition) ट्रांसक्रिप्ट एडिटर हैं। आपका काम है ASR त्रुटियों को ठीक करना।

सख्त नियम:
1. मूल ट्रांसक्रिप्ट में जो नहीं है वह कभी न जोड़ें
2. संख्याएं, राशि या अंक क्रम कभी न बदलें
3. केवल स्पष्ट ASR त्रुटियां ठीक करें
4. अगर संदेह हो तो मूल शब्द रखें
5. केवल सही ट्रांसक्रिप्ट दें, कोई व्याख्या नहीं

आम ASR त्रुटियां:
- टू → दो
- ट्री/tree → तीन  
- फोर → चार
- फाइव → पांच
- सिक्स → छह
- सेवन → सात
- एट/ate → आठ
- नाइन/नाइनर → नौ"""

    def __init__(self, language: str = "auto"):
        """
        Initialize prompt templates.
        
        Args:
            language: Language mode - "en", "hi", "hinglish", or "auto" (detect)
        """
        self.language = language

    def _detect_language(self, text: str) -> str:
        """Detect if text is Hindi, English, or mixed."""
        # Check for Devanagari characters
        devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        total_alpha = sum(1 for c in text if c.isalpha())
        
        if total_alpha == 0:
            return "en"
        
        hindi_ratio = devanagari_count / total_alpha
        
        if hindi_ratio > 0.7:
            return "hi"
        elif hindi_ratio > 0.2:
            return "hinglish"
        else:
            return "en"

    def build_restoration_prompt(
        self,
        transcript: str,
        numbers: list[str] | None = None,
        domain_context: dict[str, Any] | None = None,
        language: str | None = None,
    ) -> str:
        """
        Build prompt for transcript restoration.

        Args:
            transcript: Raw ASR transcript
            numbers: Numbers that must be preserved
            domain_context: Optional domain vocabulary
            language: Override language detection ("en", "hi", "hinglish")

        Returns:
            Complete prompt string
        """
        # Detect or use specified language
        lang = language or self.language
        if lang == "auto":
            lang = self._detect_language(transcript)
        
        # Choose appropriate system prompt
        if lang == "hi":
            system_prompt = self.HINDI_RESTORATION_SYSTEM
        else:
            system_prompt = self.RESTORATION_SYSTEM
        
        parts = [system_prompt, ""]

        # Add number preservation constraint
        if numbers:
            if lang == "hi":
                parts.append(
                    f"महत्वपूर्ण: ये संख्याएं बिना बदले रहनी चाहिए: {', '.join(numbers)}"
                )
            else:
                parts.append(
                    f"IMPORTANT: The following numbers MUST appear unchanged in your output: {', '.join(numbers)}"
                )
            parts.append("")

        # Add domain context
        if domain_context:
            domain_terms = []
            for key in domain_context:
                if isinstance(domain_context[key], list):
                    domain_terms.append(key)
                elif isinstance(domain_context[key], dict):
                    domain_terms.extend(list(domain_context[key].keys())[:10])
            
            domain_terms = domain_terms[:20]

            if domain_terms:
                if lang == "hi":
                    parts.append(
                        f"डोमेन शब्दावली (इन शब्दों को प्राथमिकता दें): {', '.join(domain_terms)}"
                    )
                else:
                    parts.append(
                        f"Domain vocabulary (prefer these spellings): {', '.join(domain_terms)}"
                    )
                parts.append("")

        # Add the transcript
        if lang == "hi":
            parts.append("ठीक करने के लिए ट्रांसक्रिप्ट:")
        else:
            parts.append("TRANSCRIPT TO FIX:")
        parts.append(transcript)
        parts.append("")
        
        if lang == "hi":
            parts.append("सही ट्रांसक्रिप्ट:")
        else:
            parts.append("CORRECTED TRANSCRIPT:")

        return "\n".join(parts)

    def build_grammar_prompt(
        self,
        text: str,
        preserve_meaning: bool = True,
    ) -> str:
        """
        Build prompt for grammar correction.

        Args:
            text: Text to correct
            preserve_meaning: Whether to strictly preserve meaning

        Returns:
            Complete prompt string
        """
        parts = [self.GRAMMAR_SYSTEM, ""]

        if preserve_meaning:
            parts.append(
                "CRITICAL: Do not change the meaning in any way. Only fix grammar."
            )
            parts.append("")

        parts.append("TEXT TO CORRECT:")
        parts.append(text)
        parts.append("")
        parts.append("CORRECTED TEXT:")

        return "\n".join(parts)

    def build_punctuation_prompt(self, text: str) -> str:
        """
        Build prompt for adding punctuation.

        Args:
            text: Unpunctuated text

        Returns:
            Complete prompt string
        """
        parts = [
            self.PUNCTUATION_SYSTEM,
            "",
            "TEXT TO PUNCTUATE:",
            text,
            "",
            "PUNCTUATED TEXT:",
        ]

        return "\n".join(parts)

    def build_comparison_prompt(
        self,
        original: str,
        candidates: list[str],
    ) -> str:
        """
        Build prompt for selecting best candidate.

        Args:
            original: Original transcript
            candidates: List of corrected candidates

        Returns:
            Complete prompt string
        """
        parts = [
            "You are comparing transcript corrections. Select the best one.",
            "",
            "ORIGINAL TRANSCRIPT:",
            original,
            "",
            "CANDIDATES:",
        ]

        for i, candidate in enumerate(candidates, 1):
            parts.append(f"{i}. {candidate}")

        parts.extend([
            "",
            "Select the number of the best candidate (1-{}).".format(len(candidates)),
            "Consider: accuracy, grammar, preservation of meaning, and minimal changes.",
            "",
            "BEST CANDIDATE NUMBER:",
        ])

        return "\n".join(parts)
