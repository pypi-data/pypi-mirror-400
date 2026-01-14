"""
Unified ASR Enhancement Pipeline
================================

Single pipeline that handles both gap detection/recovery and text correction.

Flow:
1. Audio + Primary Text comes in
2. Check for gaps (duration ratio + linguistic patterns)
3. IF gaps detected → Run secondary ASR (distil-large-v3) on full audio, merge
4. IF no gaps → Run spelling corrector + LLM punctuation

Default: distil-large-v3 for speed
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union
import logging

from .detectors.smart_gap_detector import SmartGapDetector, GapAnalysisResult
from .resynthesis.fast_asr import FasterWhisperASR, ASRResult
from .utils import HindiTextCorrector, get_logger

logger = get_logger(__name__)


@dataclass
class UnifiedResult:
    """Result from unified pipeline."""
    
    original_text: str
    enhanced_text: str
    had_gaps: bool
    gap_analysis: Optional[GapAnalysisResult] = None
    secondary_asr_text: Optional[str] = None
    corrections_made: list[dict] = field(default_factory=list)
    processing_stages: list[str] = field(default_factory=list)
    confidence: float = 0.0


class LLMTextPolisher:
    """
    LLM-based text polisher for punctuation and spelling.
    
    Used when no gaps are detected to improve text quality.
    Works with local LLM (no API calls).
    """
    
    def __init__(self, local_llm=None):
        """
        Initialize the polisher.
        
        Args:
            local_llm: Pre-loaded local LLM instance from ModelManager
        """
        self.local_llm = local_llm
    
    def polish(self, text: str, domain: str = "general") -> str:
        """
        Polish text with local LLM.
        
        Args:
            text: Input text
            domain: Domain (banking, telecom, general)
            
        Returns:
            Polished text
        """
        if not self.local_llm or not self.local_llm.is_available():
            logger.warning("Local LLM not available, returning original text")
            return text
        
        try:
            # Use local LLM polish method
            polished = self.local_llm.polish_hindi_text(text)
            
            # Sanity check - don't accept if too different
            if len(polished) < len(text) * 0.5 or len(polished) > len(text) * 1.5:
                logger.warning("LLM response too different, using original")
                return text
            
            return polished
            
        except Exception as e:
            logger.warning(f"LLM polishing failed: {e}")
            return text


class UnifiedASRPipeline:
    """
    LLM-based text polisher for punctuation and spelling.
    
    Used when no gaps are detected to improve text quality.
    Works with local LLM (no API calls).
    """
    
    POLISH_PROMPT = """Fix punctuation and minor spelling errors in this Hindi/Hinglish transcript.

RULES:
1. Add proper punctuation (। , ? !)
2. Fix obvious spelling mistakes
3. DO NOT change the meaning or add/remove words
4. Keep the same language mix (Hindi/English)
5. Preserve all numbers and amounts exactly
6. Keep proper nouns as-is

TRANSCRIPT:
{text}

Return ONLY the corrected text, nothing else."""

    BANKING_POLISH_PROMPT = """Fix punctuation and spelling in this banking call transcript.

RULES:
1. Add proper punctuation
2. Fix spelling of banking terms (credit card, interest, premium, etc.)
3. Keep all numbers/amounts EXACTLY as they are
4. Preserve consent phrases exactly
5. DO NOT add or remove any words

TRANSCRIPT:
{text}

Return ONLY the corrected text."""

    def __init__(
        self,
        local_llm=None,
    ):
        """
        Initialize the polisher.
        
        Args:
            local_llm: Pre-loaded local LLM instance from ModelManager
        """
        self.local_llm = local_llm
    
    def polish(
        self,
        text: str,
        domain: str = "general",
    ) -> str:
        """
        Polish text with local LLM.
        
        Args:
            text: Input text
            domain: Domain (banking, telecom, general)
            
        Returns:
            Polished text
        """
        if not self.local_llm or not self.local_llm.is_available():
            logger.warning("Local LLM not available, returning original text")
            return text
        
        try:
            # Use local LLM polish method
            polished = self.local_llm.polish_hindi_text(text)
            
            # Sanity check - don't accept if too different
            if len(polished) < len(text) * 0.5 or len(polished) > len(text) * 1.5:
                logger.warning("LLM response too different, using original")
                return text
            
            return polished
            
        except Exception as e:
            logger.warning(f"LLM polishing failed: {e}")
            return text
        return self._client
    
    async def polish(
        self,
        text: str,
        domain: str = "general",
    ) -> str:
        """
        Polish text with LLM.
        
        Args:
            text: Input text
            domain: Domain (banking, telecom, general)
            
        Returns:
            Polished text
        """
        try:
            client = self._get_client()
            
            if domain == "banking":
                prompt = self.BANKING_POLISH_PROMPT.format(text=text)
            else:
                prompt = self.POLISH_PROMPT.format(text=text)
            
            response = await client.complete(prompt)
            
            # Clean response
            polished = response.strip()
            
            # Sanity check - don't accept if too different
            if len(polished) < len(text) * 0.5 or len(polished) > len(text) * 1.5:
                logger.warning("LLM response too different, using original")
                return text
            
            return polished
            
        except Exception as e:
            logger.warning(f"LLM polishing failed: {e}")
            return text
    
    def polish_sync(self, text: str, domain: str = "general") -> str:
        """Synchronous polish."""
        import threading
        result = [text]
        
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result[0] = loop.run_until_complete(self.polish(text, domain))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join(timeout=30)
        
        return result[0]


class UnifiedASRPipeline:
    """
    Unified ASR Enhancement Pipeline.
    
    Single entry point for all ASR enhancement:
    - Gap detection and recovery
    - Spelling correction
    - LLM-based punctuation
    
    Flow:
        1. Analyze text for gaps (duration ratio + patterns)
        2. If gaps → Re-run full audio with secondary ASR
        3. If no gaps → Spelling correction + LLM polish
    
    Example:
        ```python
        pipeline = UnifiedASRPipeline()
        
        result = await pipeline.process(
            audio_path="call.wav",
            primary_text="आपके कार्ड पर चार्ज है",
            audio_duration=30.0,
        )
        
        print(result.enhanced_text)
        print(f"Had gaps: {result.had_gaps}")
        ```
    """
    
    def __init__(
        self,
        # Secondary ASR settings (default: distil-large-v3 for speed)
        asr_model: str = "distil-large-v3",
        asr_device: str = "auto",
        asr_compute: str = "int8",
        asr_preset: Optional[str] = None,
        
        # LLM settings (local LLM, no API calls)
        local_llm=None,  # Pre-loaded local LLM instance
        enable_llm_polish: bool = True,
        
        # Gap detection settings
        gap_threshold: float = 0.7,  # If ratio < 70% expected, has gaps
        language: str = "hi-en",
    ):
        """
        Initialize the unified pipeline.
        
        Args:
            asr_model: Secondary ASR model (default: distil-large-v3)
            asr_device: Device (auto, cpu, cuda)
            asr_compute: Compute type (int8, float16)
            asr_preset: Use preset instead of manual config
            local_llm: Pre-loaded local LLM instance (no API calls)
            enable_llm_polish: Whether to use LLM for text polishing
            gap_threshold: Threshold for gap detection (0-1)
            language: Primary language (hi, en, hi-en)
        """
        self.asr_model = asr_model
        self.asr_device = asr_device
        self.asr_compute = asr_compute
        self.asr_preset = asr_preset
        self.local_llm = local_llm
        self.enable_llm_polish = enable_llm_polish
        self.gap_threshold = gap_threshold
        self.language = language
        
        # Components (lazy loaded)
        self._gap_detector = None
        self._secondary_asr = None
        self._text_polisher = None
        self._hindi_corrector = None
        
        logger.info(
            f"UnifiedASRPipeline initialized: "
            f"asr_model={asr_model}, llm={enable_llm_polish}"
        )
    
    def _get_gap_detector(self) -> SmartGapDetector:
        """Lazy load gap detector."""
        if self._gap_detector is None:
            self._gap_detector = SmartGapDetector(
                llm_provider=self.llm_provider,
                llm_model=self.llm_model,
                language=self.language,
            )
            # Adjust threshold
            self._gap_detector.RATIO_THRESHOLD = self.gap_threshold
        return self._gap_detector
    
    def _get_secondary_asr(self) -> FasterWhisperASR:
        """Lazy load secondary ASR."""
        if self._secondary_asr is None:
            if self.asr_preset:
                self._secondary_asr = FasterWhisperASR.from_preset(self.asr_preset)
            else:
                self._secondary_asr = FasterWhisperASR(
                    model_size=self.asr_model,
                    device=self.asr_device,
                    compute_type=self.asr_compute,
                )
        return self._secondary_asr
    
    def _get_text_polisher(self) -> LLMTextPolisher:
        """Lazy load text polisher."""
        if self._text_polisher is None:
            # Get local LLM from app state if available
            local_llm = getattr(self, 'local_llm', None)
            self._text_polisher = LLMTextPolisher(local_llm=local_llm)
        return self._text_polisher
    
    def _get_hindi_corrector(self) -> HindiTextCorrector:
        """Lazy load Hindi corrector."""
        if self._hindi_corrector is None:
            self._hindi_corrector = HindiTextCorrector()
        return self._hindi_corrector
    
    async def process(
        self,
        audio_path: Union[str, Path],
        primary_text: str,
        audio_duration: Optional[float] = None,
        domain: str = "general",
        force_secondary_asr: bool = False,
    ) -> UnifiedResult:
        """
        Process audio with unified pipeline.
        
        Args:
            audio_path: Path to audio file
            primary_text: Primary ASR output (from Parakeet)
            audio_duration: Audio duration in seconds (will be computed if not provided)
            domain: Domain context (banking, telecom, general)
            force_secondary_asr: Force re-run with secondary ASR even if no gaps
            
        Returns:
            UnifiedResult with enhanced text
        """
        logger.info(f"Processing: text_len={len(primary_text)}, domain={domain}")
        
        stages = []
        corrections = []
        
        # Get audio duration if not provided
        if audio_duration is None:
            audio_duration = await self._get_audio_duration(audio_path)
        
        # Step 1: Analyze for gaps
        stages.append("gap_analysis")
        gap_detector = self._get_gap_detector()
        
        gap_result = await gap_detector.analyze(
            text=primary_text,
            audio_duration=audio_duration,
            domain=domain,
            use_llm=False,  # Quick check first
        )
        
        has_gaps = gap_result.needs_reprocessing or force_secondary_asr
        secondary_text = None
        enhanced_text = primary_text
        
        if has_gaps:
            # Step 2A: Gaps detected - Run secondary ASR on full audio
            logger.info(f"Gaps detected (ratio={gap_result.duration_ratio:.2f}), running secondary ASR")
            stages.append("secondary_asr")
            
            try:
                secondary_asr = self._get_secondary_asr()
                asr_result = await secondary_asr.transcribe(
                    audio_path,
                    language="hi" if self.language.startswith("hi") else "en",
                )
                secondary_text = asr_result.text
                
                # Merge primary and secondary (prefer secondary for gaps)
                enhanced_text = await self._merge_transcripts(
                    primary_text,
                    secondary_text,
                    gap_result,
                )
                
                corrections.append({
                    "type": "secondary_asr",
                    "original_ratio": gap_result.duration_ratio,
                    "recovered_length": len(secondary_text),
                })
                
            except Exception as e:
                logger.error(f"Secondary ASR failed: {e}")
                enhanced_text = primary_text
        
        else:
            # Step 2B: No gaps - Apply corrections only
            logger.info("No gaps detected, applying corrections")
        
        # Step 3: Hindi spelling correction (always applied)
        stages.append("hindi_correction")
        hindi_corrector = self._get_hindi_corrector()
        
        original_for_correction = enhanced_text
        enhanced_text = hindi_corrector.correct(enhanced_text)
        
        if enhanced_text != original_for_correction:
            corrections.append({
                "type": "hindi_correction",
                "changes": self._diff_text(original_for_correction, enhanced_text),
            })
        
        # Step 4: LLM polishing (if enabled and no major gaps)
        if self.enable_llm_polish:
            stages.append("llm_polish")
            
            try:
                polisher = self._get_text_polisher()
                original_for_polish = enhanced_text
                enhanced_text = await polisher.polish(enhanced_text, domain)
                
                if enhanced_text != original_for_polish:
                    corrections.append({
                        "type": "llm_polish",
                        "domain": domain,
                    })
                    
            except Exception as e:
                logger.warning(f"LLM polish failed: {e}")
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            gap_result,
            has_gaps,
            secondary_text is not None,
        )
        
        return UnifiedResult(
            original_text=primary_text,
            enhanced_text=enhanced_text,
            had_gaps=has_gaps,
            gap_analysis=gap_result,
            secondary_asr_text=secondary_text,
            corrections_made=corrections,
            processing_stages=stages,
            confidence=confidence,
        )
    
    async def _get_audio_duration(self, audio_path: Union[str, Path]) -> float:
        """Get audio duration in seconds."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            return len(audio) / 1000.0
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 0.0
    
    async def _merge_transcripts(
        self,
        primary: str,
        secondary: str,
        gap_result: GapAnalysisResult,
    ) -> str:
        """
        Merge primary and secondary transcripts.
        
        Strategy:
        - If secondary is significantly longer, prefer it
        - Otherwise, use word-level comparison
        """
        # If secondary is much longer, likely recovered missing content
        if len(secondary) > len(primary) * 1.2:
            logger.info("Secondary transcript longer, using it as base")
            return secondary
        
        # If similar length, prefer primary (faster ASR usually cleaner)
        if 0.9 <= len(secondary) / len(primary) <= 1.1:
            return primary
        
        # For complex cases, just use the longer one
        return secondary if len(secondary) > len(primary) else primary
    
    def _diff_text(self, original: str, corrected: str) -> list[dict]:
        """Get list of changes between original and corrected."""
        # Simple diff - just count changes
        original_words = set(original.split())
        corrected_words = set(corrected.split())
        
        added = corrected_words - original_words
        removed = original_words - corrected_words
        
        return [
            {"added": list(added)[:5]},
            {"removed": list(removed)[:5]},
        ]
    
    def _calculate_confidence(
        self,
        gap_result: GapAnalysisResult,
        had_gaps: bool,
        recovered: bool,
    ) -> float:
        """Calculate overall confidence score."""
        base_confidence = 0.8
        
        # Reduce if gaps were detected
        if had_gaps:
            base_confidence -= 0.2
        
        # Increase if recovered successfully
        if recovered:
            base_confidence += 0.15
        
        # Adjust based on duration ratio
        if gap_result.duration_ratio:
            ratio_score = min(gap_result.duration_ratio / gap_result.expected_ratio, 1.0)
            base_confidence = (base_confidence + ratio_score) / 2
        
        return max(0.1, min(1.0, base_confidence))
    
    def process_sync(
        self,
        audio_path: Union[str, Path],
        primary_text: str,
        audio_duration: Optional[float] = None,
        domain: str = "general",
    ) -> UnifiedResult:
        """Synchronous version of process."""
        import threading
        
        result = [None]
        error = [None]
        
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result[0] = loop.run_until_complete(
                    self.process(audio_path, primary_text, audio_duration, domain)
                )
            except Exception as e:
                error[0] = e
            finally:
                loop.close()
        
        thread = threading.Thread(target=run)
        thread.start()
        thread.join(timeout=120)  # 2 minute timeout
        
        if error[0]:
            raise error[0]
        
        return result[0]


# Convenience function
async def enhance_audio(
    audio_path: Union[str, Path],
    primary_text: str,
    audio_duration: Optional[float] = None,
    domain: str = "general",
    **kwargs,
) -> UnifiedResult:
    """
    Convenience function for one-shot enhancement.
    
    Args:
        audio_path: Path to audio file
        primary_text: Primary ASR text
        audio_duration: Audio duration (optional)
        domain: Domain (banking, telecom, general)
        **kwargs: Additional pipeline config
        
    Returns:
        UnifiedResult
    """
    pipeline = UnifiedASRPipeline(**kwargs)
    return await pipeline.process(
        audio_path=audio_path,
        primary_text=primary_text,
        audio_duration=audio_duration,
        domain=domain,
    )
