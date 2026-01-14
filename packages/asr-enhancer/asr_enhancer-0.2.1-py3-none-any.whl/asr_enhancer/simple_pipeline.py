"""
Simple Enhancement Pipeline
============================

Simplified pipeline for plain text ASR output (no timestamps).
Optimized for speed and works with Parakeet's plain text output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import asyncio

from .detectors.gap_detector import LinguisticGapDetector, LLMGapDetector, GapInfo
from .numeric import NumericPatternAnalyzer, SequenceReconstructor
from .vocab import VocabularyCorrector
from .utils import HindiTextCorrector, get_logger
from .llm import LLMContextRestorer

logger = get_logger(__name__)


@dataclass
class SimpleEnhancementResult:
    """Result from simple enhancement."""
    
    original_text: str
    enhanced_text: str
    corrections_made: list[dict]
    gaps_detected: list[dict]
    diagnostics: dict[str, Any]


class SimpleEnhancementPipeline:
    """
    Simple enhancement pipeline for plain text.
    
    No timestamps required - works with Parakeet's plain text output.
    
    Pipeline stages:
        1. Gap Detection (linguistic patterns)
        2. Numeric Correction (acoustic confusions)
        3. Hindi Text Correction
        4. Vocabulary Correction
        5. LLM Polishing (optional)
    
    Example:
        ```python
        pipeline = SimpleEnhancementPipeline()
        result = await pipeline.enhance(
            "पीनियम फ्री है और इंटर वेस्ट नहीं लगता",
            domain="banking"
        )
        print(result.enhanced_text)
        # "Premium फ्री है और Interest नहीं लगता"
        ```
    """
    
    # Domain-specific lexicons
    DOMAIN_LEXICONS = {
        'banking': {
            'Credit Card': ['क्रेडिट कार्ड', 'credit card'],
            'Interest': ['इंटरेस्ट', 'ब्याज', 'इंटर वेस्ट'],
            'Premium': ['प्रीमियम', 'पीनियम'],
            'Annual Fee': ['वार्षिक शुल्क', 'annual fee'],
            'Consent': ['सहमति', 'consent'],
            'Charges': ['चार्जेस', 'चार्ज', 'शुल्क'],
        },
        'telecom': {
            'Recharge': ['रिचार्ज', 'recharge'],
            'Plan': ['प्लान', 'plan'],
            'Validity': ['वैलिडिटी', 'validity'],
            'Data': ['डेटा', 'data'],
        },
        'insurance': {
            'Premium': ['प्रीमियम', 'पीनियम'],
            'Coverage': ['कवरेज', 'coverage'],
            'Claim': ['क्लेम', 'claim'],
            'Policy': ['पॉलिसी', 'policy'],
        },
    }
    
    def __init__(
        self,
        enable_llm: bool = False,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.1",
    ):
        """
        Initialize the simple pipeline.
        
        Args:
            enable_llm: Whether to use LLM for polishing
            llm_provider: LLM provider (ollama, openai, anthropic)
            llm_model: Model name
        """
        self.enable_llm = enable_llm
        
        # Initialize components
        self.gap_detector = LinguisticGapDetector()
        self.numeric_analyzer = NumericPatternAnalyzer()
        self.sequence_reconstructor = SequenceReconstructor()
        self.hindi_corrector = HindiTextCorrector()
        self.vocab_corrector = VocabularyCorrector()
        
        # LLM components (lazy loaded)
        self._llm_restorer = None
        self._llm_gap_detector = None
        self.llm_provider = llm_provider
        self.llm_model = llm_model
    
    def _get_llm_restorer(self):
        """Lazy load LLM restorer."""
        if self._llm_restorer is None and self.enable_llm:
            self._llm_restorer = LLMContextRestorer(
                provider=self.llm_provider,
                model=self.llm_model,
            )
        return self._llm_restorer
    
    async def enhance(
        self,
        text: str,
        domain: Optional[str] = None,
        audio_path: Optional[str] = None,
        audio_duration: Optional[float] = None,
    ) -> SimpleEnhancementResult:
        """
        Enhance plain text transcript.
        
        Args:
            text: Raw transcript from Parakeet
            domain: Domain hint (banking, telecom, insurance)
            audio_path: Optional audio path for secondary ASR
            audio_duration: Audio duration in seconds (helps estimate gap positions)
            
        Returns:
            SimpleEnhancementResult with enhanced text
        """
        logger.info(f"Starting simple enhancement (length={len(text)})")
        
        diagnostics = {"stages": []}
        corrections = []
        original_text = text
        enhanced_text = text
        
        # Stage 1: Gap Detection
        logger.debug("Stage 1: Gap Detection")
        gaps = self.gap_detector.detect_gaps(enhanced_text)
        gap_info = [
            {
                'position': g.position,
                'type': g.gap_type,
                'confidence': g.confidence,
                'context': g.context_before[-30:] + " | " + g.context_after[:30],
            }
            for g in gaps
        ]
        diagnostics["stages"].append({
            "name": "gap_detection",
            "gaps_found": len(gaps),
            "high_confidence_gaps": sum(1 for g in gaps if g.confidence >= 0.7),
        })
        
        # Stage 2: Numeric Correction
        logger.debug("Stage 2: Numeric Correction")
        # For plain text, we apply acoustic corrections directly
        words = enhanced_text.split()
        corrected_words = []
        numeric_corrections = 0
        
        for word in words:
            corrected = self.sequence_reconstructor.correct_word(word)
            if corrected != word:
                corrections.append({
                    "type": "numeric",
                    "original": word,
                    "corrected": corrected,
                })
                numeric_corrections += 1
            corrected_words.append(corrected)
        
        enhanced_text = " ".join(corrected_words)
        diagnostics["stages"].append({
            "name": "numeric_correction",
            "corrections": numeric_corrections,
        })
        
        # Stage 3: Hindi Text Correction
        logger.debug("Stage 3: Hindi Correction")
        hindi_corrected = self.hindi_corrector.correct(enhanced_text)
        if hindi_corrected != enhanced_text:
            corrections.append({
                "type": "hindi",
                "original": enhanced_text[:100],
                "corrected": hindi_corrected[:100],
            })
        enhanced_text = hindi_corrected
        diagnostics["stages"].append({
            "name": "hindi_correction",
            "changed": hindi_corrected != enhanced_text,
        })
        
        # Stage 4: Domain Vocabulary Correction
        if domain and domain in self.DOMAIN_LEXICONS:
            logger.debug(f"Stage 4: Domain Vocabulary ({domain})")
            lexicon = self.DOMAIN_LEXICONS[domain]
            vocab_corrections = 0
            
            for canonical, variants in lexicon.items():
                for variant in variants:
                    if variant.lower() in enhanced_text.lower() and variant != canonical:
                        # Replace variant with canonical
                        import re
                        pattern = re.compile(re.escape(variant), re.IGNORECASE)
                        new_text = pattern.sub(canonical, enhanced_text)
                        if new_text != enhanced_text:
                            corrections.append({
                                "type": "vocabulary",
                                "original": variant,
                                "corrected": canonical,
                            })
                            vocab_corrections += 1
                            enhanced_text = new_text
            
            diagnostics["stages"].append({
                "name": "vocabulary_correction",
                "domain": domain,
                "corrections": vocab_corrections,
            })
        
        # Stage 5: LLM Polishing (optional)
        if self.enable_llm:
            logger.debug("Stage 5: LLM Polishing")
            try:
                restorer = self._get_llm_restorer()
                if restorer:
                    # Simple polishing - fix grammar and fill obvious gaps
                    polished = await restorer.polish_text(
                        enhanced_text,
                        preserve_numbers=True,
                        language="hi",
                    )
                    if polished and polished != enhanced_text:
                        corrections.append({
                            "type": "llm_polish",
                            "changes": "grammar and context fixes",
                        })
                        enhanced_text = polished
                    diagnostics["stages"].append({
                        "name": "llm_polishing",
                        "applied": True,
                    })
            except Exception as e:
                logger.warning(f"LLM polishing failed: {e}")
                diagnostics["stages"].append({
                    "name": "llm_polishing",
                    "applied": False,
                    "error": str(e),
                })
        
        # Calculate improvement
        diagnostics["summary"] = {
            "original_length": len(original_text),
            "enhanced_length": len(enhanced_text),
            "total_corrections": len(corrections),
            "gaps_detected": len(gaps),
        }
        
        return SimpleEnhancementResult(
            original_text=original_text,
            enhanced_text=enhanced_text,
            corrections_made=corrections,
            gaps_detected=gap_info,
            diagnostics=diagnostics,
        )
    
    def enhance_sync(
        self,
        text: str,
        domain: Optional[str] = None,
    ) -> SimpleEnhancementResult:
        """
        Synchronous version of enhance (no LLM).
        
        Fastest option for simple corrections.
        
        Args:
            text: Raw transcript
            domain: Domain hint
            
        Returns:
            SimpleEnhancementResult
        """
        # Disable LLM for sync
        old_llm = self.enable_llm
        self.enable_llm = False
        
        try:
            result = asyncio.get_event_loop().run_until_complete(
                self.enhance(text, domain)
            )
        finally:
            self.enable_llm = old_llm
        
        return result
    
    def quick_fix(self, text: str) -> str:
        """
        Ultra-fast correction (no async, no LLM).
        
        Just applies Hindi and numeric corrections.
        
        Args:
            text: Raw transcript
            
        Returns:
            Corrected text
        """
        # Apply acoustic corrections to each word
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Numeric/acoustic corrections
            corrected = self.sequence_reconstructor.correct_word(word)
            corrected_words.append(corrected)
        
        text = " ".join(corrected_words)
        
        # Hindi corrections
        text = self.hindi_corrector.correct(text)
        
        return text


# Convenience function
def quick_enhance(text: str, domain: str = "banking") -> str:
    """
    Quick enhancement for plain text.
    
    Args:
        text: Raw Parakeet transcript
        domain: Domain (banking, telecom, insurance)
        
    Returns:
        Enhanced text
    """
    pipeline = SimpleEnhancementPipeline(enable_llm=False)
    return pipeline.quick_fix(text)
