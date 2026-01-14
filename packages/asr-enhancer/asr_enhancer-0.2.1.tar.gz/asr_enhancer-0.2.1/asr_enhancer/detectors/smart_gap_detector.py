"""
Smart Gap Detector
==================

Advanced gap detection using:
1. LLM-based semantic analysis
2. Audio duration vs text length ratio
3. Linguistic pattern matching

Automatically identifies segments that need re-processing with secondary ASR.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class GapSegment:
    """A segment identified as potentially having missing content."""
    
    start_time: float  # Estimated start time in seconds
    end_time: float    # Estimated end time in seconds
    gap_type: str      # Type of gap detected
    confidence: float  # Confidence that content is missing
    context: str       # Surrounding text for context
    suggested_content: Optional[str] = None  # LLM-suggested missing content
    recovered_text: Optional[str] = None     # Text recovered from secondary ASR


@dataclass
class GapAnalysisResult:
    """Result of gap analysis."""
    
    original_text: str
    gaps_detected: list[GapSegment]
    duration_ratio: Optional[float]  # chars per second
    expected_ratio: float = 12.0     # typical Hindi speech: ~12 chars/sec
    missing_content_estimate: float = 0.0  # estimated % of missing content
    needs_reprocessing: bool = False
    segments_to_reprocess: list[dict] = field(default_factory=list)


class SmartGapDetector:
    """
    Smart gap detection combining multiple methods.
    
    Methods:
        1. Duration Ratio: Compare audio length vs text length
        2. LLM Semantic: Use LLM to detect incomplete thoughts
        3. Linguistic: Pattern-based detection
    
    Example:
        ```python
        detector = SmartGapDetector(llm_provider="ollama")
        
        result = await detector.analyze(
            text="आपके कार्ड पर चार्ज है।",
            audio_duration=30.0,  # 30 seconds of audio
        )
        
        if result.needs_reprocessing:
            for segment in result.segments_to_reprocess:
                print(f"Re-process: {segment['start_time']}-{segment['end_time']}s")
        ```
    """
    
    # Expected characters per second for different languages
    # Based on typical conversational speech rates
    CHARS_PER_SECOND = {
        "hi": 12.0,    # Hindi: ~12 chars/sec (Devanagari is compact)
        "en": 15.0,    # English: ~15 chars/sec
        "hi-en": 13.0, # Hinglish: ~13 chars/sec (mixed)
    }
    
    # Threshold for detecting missing content
    RATIO_THRESHOLD = 0.7  # If actual ratio < 70% of expected, content is missing
    
    # LLM prompts for different analysis types
    SEMANTIC_GAP_PROMPT = """Analyze this transcript from a phone call for missing or incomplete content.

TRANSCRIPT:
{transcript}

AUDIO DURATION: {duration} seconds

Look for:
1. Incomplete sentences or thoughts that end abruptly
2. Missing numbers/amounts where they should logically appear
3. References to things not mentioned (e.g., "that card" but no card mentioned)
4. Consent phrases that seem incomplete
5. Sudden topic changes suggesting missing transitions
6. Places where audio duration suggests more content should exist

For each gap found, provide:
- position: Text before the gap (last 5-10 words)
- likely_missing: What content is probably missing
- confidence: 0.0 to 1.0
- time_estimate: Approximate position in audio (percentage)

Return as JSON array. Be conservative - only flag clear gaps.
If no gaps found, return empty array: []

IMPORTANT: This is for ASR error recovery, not grammar correction."""

    BANKING_CONTEXT_PROMPT = """You are analyzing a banking/credit card sales call transcript.

TRANSCRIPT:
{transcript}

Common missing elements in such calls:
- Credit card numbers (16 digits)
- CVV (3 digits)
- OTP codes (4-6 digits)
- Amounts (with "rupees" or "₹")
- Consent phrases ("I agree", "haan", "theek hai")
- Terms and conditions acknowledgment
- Phone numbers (10 digits)

Identify places where these elements seem to be missing.

Return JSON array with gaps:
[{{"position": "after 'your card number is'", "likely_missing": "16 digit card number", "confidence": 0.9}}]

Return [] if no gaps found."""

    def __init__(
        self,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.1",
        language: str = "hi-en",
    ):
        """
        Initialize the smart gap detector.
        
        Args:
            llm_provider: LLM provider (ollama, openai, anthropic)
            llm_model: Model name
            language: Primary language (hi, en, hi-en)
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.language = language
        self.expected_ratio = self.CHARS_PER_SECOND.get(language, 13.0)
        
        # LLM client (lazy loaded)
        self._llm_client = None
    
    def _get_llm_client(self):
        """Get or create LLM client."""
        if self._llm_client is None:
            from ..llm.providers import get_provider
            self._llm_client = get_provider(
                self.llm_provider,
                model=self.llm_model,
            )
        return self._llm_client
    
    async def analyze(
        self,
        text: str,
        audio_duration: Optional[float] = None,
        domain: str = "general",
        use_llm: bool = True,
    ) -> GapAnalysisResult:
        """
        Analyze transcript for gaps.
        
        Args:
            text: Transcript text
            audio_duration: Audio duration in seconds (optional but recommended)
            domain: Domain context (banking, telecom, general)
            use_llm: Whether to use LLM for semantic analysis
            
        Returns:
            GapAnalysisResult with detected gaps and recommendations
        """
        gaps: list[GapSegment] = []
        
        # 1. Duration ratio analysis
        duration_ratio = None
        missing_estimate = 0.0
        
        if audio_duration:
            duration_ratio, missing_estimate = self._analyze_duration_ratio(
                text, audio_duration
            )
            logger.info(f"Duration ratio: {duration_ratio:.2f} chars/sec, "
                       f"missing estimate: {missing_estimate:.1%}")
        
        # 2. Linguistic pattern analysis
        linguistic_gaps = self._detect_linguistic_gaps(text)
        gaps.extend(linguistic_gaps)
        
        # 3. LLM semantic analysis (if enabled and gaps suspected)
        if use_llm and (missing_estimate > 0.1 or linguistic_gaps):
            try:
                llm_gaps = await self._detect_semantic_gaps(
                    text, audio_duration, domain
                )
                gaps.extend(llm_gaps)
            except Exception as e:
                logger.warning(f"LLM gap detection failed: {e}")
        
        # Deduplicate and merge overlapping gaps
        gaps = self._merge_gaps(gaps)
        
        # Determine if reprocessing is needed
        needs_reprocessing = (
            missing_estimate > 0.15 or  # More than 15% missing
            len([g for g in gaps if g.confidence >= 0.7]) >= 2  # 2+ high-confidence gaps
        )
        
        # Generate segments for reprocessing
        segments = []
        if needs_reprocessing and audio_duration:
            segments = self._generate_reprocess_segments(
                gaps, audio_duration, len(text)
            )
        
        return GapAnalysisResult(
            original_text=text,
            gaps_detected=gaps,
            duration_ratio=duration_ratio,
            expected_ratio=self.expected_ratio,
            missing_content_estimate=missing_estimate,
            needs_reprocessing=needs_reprocessing,
            segments_to_reprocess=segments,
        )
    
    def _analyze_duration_ratio(
        self,
        text: str,
        audio_duration: float,
    ) -> tuple[float, float]:
        """
        Analyze if text length matches audio duration.
        
        Args:
            text: Transcript text
            audio_duration: Audio duration in seconds
            
        Returns:
            (actual_ratio, missing_estimate)
        """
        # Clean text for accurate count
        clean_text = re.sub(r'\s+', ' ', text.strip())
        char_count = len(clean_text)
        
        # Calculate actual ratio
        actual_ratio = char_count / max(audio_duration, 0.1)
        
        # Compare to expected
        ratio_comparison = actual_ratio / self.expected_ratio
        
        # Estimate missing content
        if ratio_comparison < self.RATIO_THRESHOLD:
            # Content is likely missing
            expected_chars = audio_duration * self.expected_ratio
            missing_chars = expected_chars - char_count
            missing_estimate = missing_chars / expected_chars
        else:
            missing_estimate = 0.0
        
        return actual_ratio, max(0.0, min(1.0, missing_estimate))
    
    def _detect_linguistic_gaps(self, text: str) -> list[GapSegment]:
        """Detect gaps using linguistic patterns."""
        from .gap_detector import LinguisticGapDetector
        
        detector = LinguisticGapDetector()
        raw_gaps = detector.detect_gaps(text)
        
        # Convert to GapSegment
        segments = []
        for gap in raw_gaps:
            segment = GapSegment(
                start_time=0,  # Will be estimated later
                end_time=0,
                gap_type=gap.gap_type,
                confidence=gap.confidence,
                context=f"{gap.context_before}[GAP]{gap.context_after}",
                suggested_content=gap.suggested_content,
            )
            segments.append(segment)
        
        return segments
    
    async def _detect_semantic_gaps(
        self,
        text: str,
        audio_duration: Optional[float],
        domain: str,
    ) -> list[GapSegment]:
        """Use LLM to detect semantic gaps."""
        try:
            llm = self._get_llm_client()
            
            # Choose prompt based on domain
            if domain == "banking":
                prompt = self.BANKING_CONTEXT_PROMPT.format(transcript=text[:3000])
            else:
                duration_str = f"{audio_duration:.1f}" if audio_duration else "unknown"
                prompt = self.SEMANTIC_GAP_PROMPT.format(
                    transcript=text[:3000],
                    duration=duration_str,
                )
            
            # Get LLM response
            response = await llm.generate(prompt)
            
            # Parse JSON response
            import json
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if not json_match:
                return []
            
            gaps_data = json.loads(json_match.group())
            
            # Convert to GapSegment
            segments = []
            for gap in gaps_data:
                # Estimate time from position
                position_text = gap.get('position', '')
                time_estimate = gap.get('time_estimate', 0.5)
                
                if audio_duration:
                    if isinstance(time_estimate, str):
                        time_estimate = float(time_estimate.strip('%')) / 100
                    start_time = time_estimate * audio_duration - 2
                    end_time = time_estimate * audio_duration + 2
                else:
                    start_time = 0
                    end_time = 0
                
                segment = GapSegment(
                    start_time=max(0, start_time),
                    end_time=end_time,
                    gap_type="llm_semantic",
                    confidence=float(gap.get('confidence', 0.7)),
                    context=position_text,
                    suggested_content=gap.get('likely_missing'),
                )
                segments.append(segment)
            
            return segments
            
        except Exception as e:
            logger.warning(f"LLM semantic detection failed: {e}")
            return []
    
    def _merge_gaps(self, gaps: list[GapSegment]) -> list[GapSegment]:
        """Merge overlapping gaps."""
        if len(gaps) <= 1:
            return gaps
        
        # Sort by start time (or by confidence if no time)
        gaps = sorted(gaps, key=lambda g: (g.start_time, -g.confidence))
        
        merged = [gaps[0]]
        for gap in gaps[1:]:
            last = merged[-1]
            
            # Merge if overlapping or very close
            if gap.start_time <= last.end_time + 1:
                # Extend the gap
                last.end_time = max(last.end_time, gap.end_time)
                last.confidence = max(last.confidence, gap.confidence)
                last.gap_type = f"{last.gap_type},{gap.gap_type}"
                if gap.suggested_content and not last.suggested_content:
                    last.suggested_content = gap.suggested_content
            else:
                merged.append(gap)
        
        return merged
    
    def _generate_reprocess_segments(
        self,
        gaps: list[GapSegment],
        audio_duration: float,
        text_length: int,
    ) -> list[dict]:
        """Generate segments for secondary ASR reprocessing."""
        segments = []
        
        for gap in gaps:
            if gap.confidence >= 0.6:
                # Add buffer around gap
                start = max(0, gap.start_time - 3)
                end = min(audio_duration, gap.end_time + 3)
                
                segments.append({
                    'start_time': start,
                    'end_time': end,
                    'gap_type': gap.gap_type,
                    'confidence': gap.confidence,
                    'context': gap.context[:100] if gap.context else '',
                    'suggested': gap.suggested_content,
                })
        
        # If ratio suggests significant missing content but no specific gaps,
        # suggest reprocessing the full audio
        if not segments and audio_duration:
            actual_ratio = text_length / audio_duration
            if actual_ratio < self.expected_ratio * 0.6:
                segments.append({
                    'start_time': 0,
                    'end_time': audio_duration,
                    'gap_type': 'low_content_ratio',
                    'confidence': 0.8,
                    'context': 'Full audio - content ratio too low',
                    'suggested': None,
                })
        
        # Merge overlapping segments
        return self._merge_segment_dicts(segments)
    
    def _merge_segment_dicts(self, segments: list[dict]) -> list[dict]:
        """Merge overlapping segment dictionaries."""
        if len(segments) <= 1:
            return segments
        
        segments = sorted(segments, key=lambda s: s['start_time'])
        
        merged = [segments[0]]
        for seg in segments[1:]:
            last = merged[-1]
            
            if seg['start_time'] <= last['end_time'] + 1:
                last['end_time'] = max(last['end_time'], seg['end_time'])
                last['confidence'] = max(last['confidence'], seg['confidence'])
                last['gap_type'] = f"{last['gap_type']},{seg['gap_type']}"
            else:
                merged.append(seg)
        
        return merged
    
    def analyze_sync(
        self,
        text: str,
        audio_duration: Optional[float] = None,
        domain: str = "general",
    ) -> GapAnalysisResult:
        """
        Synchronous version of analyze (no LLM).
        
        Fast analysis using only duration ratio and linguistic patterns.
        """
        # Don't use asyncio - do analysis directly
        gaps: list[GapSegment] = []
        
        # 1. Duration ratio analysis
        duration_ratio = None
        missing_estimate = 0.0
        
        if audio_duration:
            duration_ratio, missing_estimate = self._analyze_duration_ratio(
                text, audio_duration
            )
        
        # 2. Linguistic pattern analysis
        linguistic_gaps = self._detect_linguistic_gaps(text)
        gaps.extend(linguistic_gaps)
        
        # Merge gaps
        gaps = self._merge_gaps(gaps)
        
        # Determine if reprocessing is needed
        needs_reprocessing = (
            missing_estimate > 0.15 or
            len([g for g in gaps if g.confidence >= 0.7]) >= 2
        )
        
        # Generate segments
        segments = []
        if needs_reprocessing and audio_duration:
            segments = self._generate_reprocess_segments(
                gaps, audio_duration, len(text)
            )
        
        return GapAnalysisResult(
            original_text=text,
            gaps_detected=gaps,
            duration_ratio=duration_ratio,
            expected_ratio=self.expected_ratio,
            missing_content_estimate=missing_estimate,
            needs_reprocessing=needs_reprocessing,
            segments_to_reprocess=segments,
        )


class GapRecoveryPipeline:
    """
    Complete pipeline for detecting and recovering missing content.
    
    Uses Faster-Whisper Large-V3 as secondary ASR for best accuracy.
    
    Combines:
        1. Smart gap detection (duration ratio + linguistic + LLM)
        2. Secondary ASR (Faster-Whisper Large-V3) for recovery
        3. Content merging
    
    Example:
        ```python
        # Default: Large-V3 with int8 (CPU)
        pipeline = GapRecoveryPipeline()
        
        # GPU with float16
        pipeline = GapRecoveryPipeline(
            secondary_asr_preset="accurate_gpu"
        )
        
        result = await pipeline.recover(
            text="पीनियम फ्री है।",
            audio_path="/path/to/audio.wav",
            audio_duration=30.0,
        )
        
        print(result.recovered_text)
        ```
    """
    
    def __init__(
        self,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.1",
        secondary_asr: str = "faster-whisper",
        secondary_asr_model: str = "large-v3",  # Default to large-v3 for best accuracy
        secondary_asr_device: str = "auto",
        secondary_asr_compute: str = "int8",  # int8 for CPU, float16 for GPU
        secondary_asr_preset: Optional[str] = None,  # Use preset instead of manual config
    ):
        """
        Initialize the recovery pipeline.
        
        Args:
            llm_provider: LLM provider for gap detection (ollama, openai)
            llm_model: LLM model name
            secondary_asr: Secondary ASR engine ("faster-whisper")
            secondary_asr_model: Model size ("large-v3" recommended)
            secondary_asr_device: Device ("cpu", "cuda", "auto")
            secondary_asr_compute: Compute type ("int8" for CPU, "float16" for GPU)
            secondary_asr_preset: Use preset config:
                - "fast_cpu": small, int8
                - "balanced_cpu": medium, int8  
                - "accurate_cpu": large-v3, int8 (default)
                - "fast_gpu": distil-large-v3, float16
                - "accurate_gpu": large-v3, float16
        """
        self.gap_detector = SmartGapDetector(
            llm_provider=llm_provider,
            llm_model=llm_model,
        )
        
        self.secondary_asr_type = secondary_asr
        self.secondary_asr_model = secondary_asr_model
        self.secondary_asr_device = secondary_asr_device
        self.secondary_asr_compute = secondary_asr_compute
        self.secondary_asr_preset = secondary_asr_preset
        self._secondary_asr = None
    
    def _get_secondary_asr(self):
        """Get or create secondary ASR (Faster-Whisper Large-V3)."""
        if self._secondary_asr is None:
            if self.secondary_asr_type == "faster-whisper":
                from ..resynthesis.fast_asr import FasterWhisperASR
                
                # Use preset if specified
                if self.secondary_asr_preset:
                    self._secondary_asr = FasterWhisperASR.from_preset(
                        self.secondary_asr_preset
                    )
                else:
                    # Manual configuration with Large-V3 defaults
                    self._secondary_asr = FasterWhisperASR(
                        model_size=self.secondary_asr_model,
                        device=self.secondary_asr_device,
                        compute_type=self.secondary_asr_compute,
                    )
                
                logger.info(
                    f"Secondary ASR: Faster-Whisper {self.secondary_asr_model} "
                    f"({self.secondary_asr_compute})"
                )
            else:
                # Fallback to standard whisper backend
                from ..resynthesis import WhisperBackend
                self._secondary_asr = WhisperBackend()
        
        return self._secondary_asr
    
    async def recover(
        self,
        text: str,
        audio_path: Union[str, Path],
        audio_duration: Optional[float] = None,
        domain: str = "general",
        language: str = "hi",
    ) -> dict[str, Any]:
        """
        Detect gaps and recover missing content.
        
        Args:
            text: Original transcript from Parakeet
            audio_path: Path to audio file
            audio_duration: Audio duration (calculated if not provided)
            domain: Domain context
            language: Language code
            
        Returns:
            Recovery result with original, recovered text, and diagnostics
        """
        audio_path = Path(audio_path)
        
        # Get audio duration if not provided
        if audio_duration is None:
            audio_duration = self._get_audio_duration(audio_path)
        
        # Detect gaps
        analysis = await self.gap_detector.analyze(
            text=text,
            audio_duration=audio_duration,
            domain=domain,
            use_llm=True,
        )
        
        # If no reprocessing needed, return original
        if not analysis.needs_reprocessing:
            return {
                'original_text': text,
                'recovered_text': text,
                'gaps_found': len(analysis.gaps_detected),
                'content_recovered': False,
                'analysis': analysis,
            }
        
        # Process segments with secondary ASR
        asr = self._get_secondary_asr()
        recovered_segments = []
        
        for segment in analysis.segments_to_reprocess:
            try:
                result = await asr.transcribe_segment(
                    audio_path,
                    segment['start_time'],
                    segment['end_time'],
                    language=language,
                )
                
                recovered_segments.append({
                    'segment': segment,
                    'recovered_text': result.text,
                    'confidence': result.confidence,
                })
                
            except Exception as e:
                logger.warning(f"Failed to process segment: {e}")
        
        # Merge recovered content with original
        merged_text = self._merge_recovered_content(
            text, recovered_segments, audio_duration
        )
        
        return {
            'original_text': text,
            'recovered_text': merged_text,
            'gaps_found': len(analysis.gaps_detected),
            'segments_processed': len(recovered_segments),
            'content_recovered': merged_text != text,
            'missing_estimate': analysis.missing_content_estimate,
            'analysis': analysis,
            'recovered_segments': recovered_segments,
        }
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            return len(audio) / 1000.0
        except ImportError:
            # Fallback: estimate from file size (rough approximation)
            file_size = audio_path.stat().st_size
            # Assume ~16kbps for compressed audio
            return file_size / (16 * 1024 / 8)
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return 0.0
    
    def _merge_recovered_content(
        self,
        original_text: str,
        recovered_segments: list[dict],
        audio_duration: float,
    ) -> str:
        """
        Merge recovered content into original text.
        
        Uses time-based positioning to insert recovered content.
        """
        if not recovered_segments:
            return original_text
        
        # If we recovered full audio, use the better version
        if len(recovered_segments) == 1:
            seg = recovered_segments[0]
            if seg['segment']['start_time'] == 0 and seg['segment']['end_time'] >= audio_duration * 0.9:
                # Full audio was reprocessed
                recovered_text = seg['recovered_text']
                
                # Use longer text (likely more complete)
                if len(recovered_text) > len(original_text) * 1.1:
                    return recovered_text
        
        # For partial segments, we need smarter merging
        # This is a simplified version - could use LLM for better merging
        merged = original_text
        
        for rec in recovered_segments:
            recovered_text = rec['recovered_text']
            segment = rec['segment']
            
            # Find insertion point based on context
            context = segment.get('context', '')
            
            if context and '[GAP]' in context:
                before_context = context.split('[GAP]')[0].strip()
                
                # Find this context in original
                if before_context and before_context in merged:
                    # Insert after context
                    pos = merged.find(before_context) + len(before_context)
                    
                    # Check if recovered text adds new content
                    after_original = merged[pos:pos+50].strip()
                    if recovered_text not in after_original:
                        merged = merged[:pos] + f" {recovered_text} " + merged[pos:]
        
        # Clean up extra spaces
        merged = re.sub(r'\s+', ' ', merged).strip()
        
        return merged
