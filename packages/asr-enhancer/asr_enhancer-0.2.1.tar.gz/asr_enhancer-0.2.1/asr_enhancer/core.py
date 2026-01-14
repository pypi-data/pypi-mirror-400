"""
Core Enhancement Pipeline
=========================

Orchestrates all enhancement modules in a configurable pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .detectors import ConfidenceDetector, AnomalyDetector, NumericGapDetector
from .resynthesis import SegmentExtractor, SecondaryASREngine
from .numeric import NumericPatternAnalyzer, SequenceReconstructor
from .vocab import LexiconLoader, DomainTermMatcher, VocabularyCorrector
from .llm import LLMContextRestorer
from .fusion import HypothesisFusionEngine
from .validators import ConsistencyChecker, PerplexityScorer, CompletenessValidator
from .utils import Config, get_logger, HindiTextCorrector

logger = get_logger(__name__)


@dataclass
class WordToken:
    """Represents a single word with metadata."""

    word: str
    start_time: float
    end_time: float
    confidence: float
    is_corrected: bool = False
    correction_source: Optional[str] = None
    alternatives: list[str] = field(default_factory=list)


@dataclass
class TranscriptSegment:
    """A segment of the transcript, possibly spanning multiple words."""

    tokens: list[WordToken]
    segment_confidence: float
    needs_correction: bool = False
    error_type: Optional[str] = None


@dataclass
class EnhancementResult:
    """Result of the enhancement pipeline."""

    original_transcript: str
    enhanced_transcript: str
    word_timeline: list[WordToken]
    error_map: dict[str, Any]
    diagnostics: dict[str, Any]
    confidence_improvement: float


class EnhancementPipeline:
    """
    Main orchestrator for ASR Quality Enhancement.

    Pipeline stages:
        1. Error Detection (confidence + anomaly + numeric gaps)
        2. Audio Segment Extraction (for low-confidence spans)
        3. Secondary ASR Processing
        4. Numeric Reconstruction
        5. Domain Vocabulary Correction
        6. Hypothesis Fusion
        7. LLM Context Restoration
        8. Consistency Validation

    Attributes:
        config: Pipeline configuration
        confidence_detector: Detects low-confidence spans
        anomaly_detector: Detects anomalies in transcript
        numeric_detector: Detects numeric gaps
        segment_extractor: Extracts audio segments
        secondary_asr: Secondary ASR engine
        numeric_analyzer: Analyzes numeric patterns
        sequence_reconstructor: Reconstructs numeric sequences
        lexicon_loader: Loads domain lexicons
        term_matcher: Matches domain terms
        vocab_corrector: Corrects vocabulary
        llm_restorer: LLM-based context restoration
        fusion_engine: Hypothesis fusion
        consistency_checker: Validates consistency
        perplexity_scorer: Scores perplexity
        completeness_validator: Validates completeness
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the enhancement pipeline.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or Config()

        # Initialize detectors
        self.confidence_detector = ConfidenceDetector(
            threshold=self.config.confidence_threshold,
            window_size=self.config.sliding_window_size,
        )
        self.anomaly_detector = AnomalyDetector()
        self.numeric_detector = NumericGapDetector()

        # Initialize resynthesis components
        self.segment_extractor = SegmentExtractor()
        self.secondary_asr = SecondaryASREngine(
            backend=self.config.secondary_asr_backend,
            device=self.config.device,
        )

        # Initialize numeric processing
        self.numeric_analyzer = NumericPatternAnalyzer()
        self.sequence_reconstructor = SequenceReconstructor()

        # Initialize vocabulary components
        self.lexicon_loader = LexiconLoader()
        self.term_matcher = DomainTermMatcher()
        self.vocab_corrector = VocabularyCorrector()

        # Initialize LLM components
        self.llm_restorer = LLMContextRestorer(
            provider=self.config.llm_provider,
            model=self.config.llm_model,
        )

        # Initialize fusion engine
        self.fusion_engine = HypothesisFusionEngine(
            alpha=self.config.fusion_alpha,
            beta=self.config.fusion_beta,
            gamma=self.config.fusion_gamma,
        )

        # Initialize validators
        self.consistency_checker = ConsistencyChecker()
        self.perplexity_scorer = PerplexityScorer()
        self.completeness_validator = CompletenessValidator()
        
        # Initialize Hindi text corrector
        self.hindi_corrector = HindiTextCorrector()

        logger.info("Enhancement pipeline initialized")

    async def enhance(
        self,
        transcript: str,
        word_timestamps: list[dict[str, Any]],
        word_confidences: list[float],
        audio_path: Optional[str] = None,
        domain_lexicon: Optional[dict[str, list[str]]] = None,
    ) -> EnhancementResult:
        """
        Run the full enhancement pipeline.

        Args:
            transcript: Raw transcript from Parakeet ASR
            word_timestamps: List of {word, start, end} dicts
            word_confidences: Confidence scores per word
            audio_path: Optional path to audio file for re-ASR
            domain_lexicon: Optional domain-specific vocabulary

        Returns:
            EnhancementResult with enhanced transcript and diagnostics
        """
        logger.info("Starting enhancement pipeline")
        diagnostics: dict[str, Any] = {"stages": []}

        # Build initial token list
        tokens = self._build_tokens(word_timestamps, word_confidences)

        # Stage 1: Error Detection
        logger.debug("Stage 1: Error Detection")
        low_confidence_spans = self.confidence_detector.detect(tokens)
        anomalies = self.anomaly_detector.detect(tokens)
        numeric_gaps = self.numeric_detector.detect(tokens)

        error_map = {
            "low_confidence_spans": low_confidence_spans,
            "anomalies": anomalies,
            "numeric_gaps": numeric_gaps,
        }
        diagnostics["stages"].append({"name": "error_detection", "errors_found": len(low_confidence_spans)})

        # Stage 2 & 3: Re-ASR for low-confidence spans
        if audio_path and low_confidence_spans:
            logger.debug("Stage 2-3: Re-ASR Processing")
            for span in low_confidence_spans:
                segment = self.segment_extractor.extract(
                    audio_path,
                    span["start_time"],
                    span["end_time"],
                )
                alternatives = await self.secondary_asr.transcribe(segment)
                span["alternatives"] = alternatives
            diagnostics["stages"].append({"name": "re_asr", "segments_processed": len(low_confidence_spans)})

        # Stage 4: Numeric Reconstruction
        logger.debug("Stage 4: Numeric Reconstruction")
        numeric_patterns = self.numeric_analyzer.analyze(tokens)
        if self.config.enable_numeric_reconstruction and numeric_patterns:
            tokens = self.sequence_reconstructor.reconstruct(tokens, numeric_patterns)
        diagnostics["stages"].append({"name": "numeric_reconstruction", "patterns_found": len(numeric_patterns)})

        # Stage 5: Domain Vocabulary Correction
        if domain_lexicon and self.config.enable_vocab_correction:
            logger.debug("Stage 5: Domain Vocabulary Correction")
            self.lexicon_loader.load(domain_lexicon)
            matches = self.term_matcher.match(tokens, domain_lexicon)
            tokens = self.vocab_corrector.correct(tokens, matches)
            diagnostics["stages"].append({"name": "vocab_correction", "corrections": len(matches)})

        # Stage 5.5: Hindi Text Correction (always runs, handles Hinglish)
        logger.debug("Stage 5.5: Hindi Text Correction")
        hindi_corrections = []
        for token in tokens:
            original_word = token.word
            corrected_word = self.hindi_corrector.correct(original_word)
            if corrected_word != original_word:
                token.word = corrected_word
                token.is_corrected = True
                token.correction_source = "hindi_corrector"
                hindi_corrections.append((original_word, corrected_word))
        if hindi_corrections:
            diagnostics["stages"].append({
                "name": "hindi_correction", 
                "corrections": len(hindi_corrections),
                "examples": hindi_corrections[:5]
            })

        # Stage 6: Hypothesis Fusion
        logger.debug("Stage 6: Hypothesis Fusion")
        tokens = self.fusion_engine.fuse(tokens, low_confidence_spans)
        diagnostics["stages"].append({"name": "hypothesis_fusion", "fused": True})

        # Build enhanced text from tokens
        enhanced_text = " ".join(t.word for t in tokens)

        # Stage 7: LLM Context Restoration (optional)
        if self.config.enable_llm_restoration:
            logger.debug("Stage 7: LLM Context Restoration")
            try:
                llm_text = await self.llm_restorer.restore(
                    tokens,
                    preserve_numbers=True,
                    domain_context=domain_lexicon,
                )
                if llm_text and llm_text != enhanced_text:
                    enhanced_text = llm_text
                diagnostics["stages"].append({"name": "llm_restoration", "applied": True})
            except Exception as e:
                logger.warning(f"LLM restoration failed: {e}")
                diagnostics["stages"].append({"name": "llm_restoration", "applied": False, "error": str(e)})
        else:
            diagnostics["stages"].append({"name": "llm_restoration", "applied": False, "reason": "disabled"})

        # Stage 8: Validation
        logger.debug("Stage 8: Validation")
        consistency_score = self.consistency_checker.check(enhanced_text, tokens)
        perplexity = self.perplexity_scorer.score(enhanced_text)
        is_complete = self.completeness_validator.validate(enhanced_text, numeric_gaps)

        diagnostics["validation"] = {
            "consistency_score": consistency_score,
            "perplexity": perplexity,
            "is_complete": is_complete,
        }

        # Calculate confidence improvement
        original_avg_conf = sum(word_confidences) / len(word_confidences) if word_confidences else 0
        enhanced_avg_conf = sum(t.confidence for t in tokens) / len(tokens) if tokens else 0
        confidence_improvement = enhanced_avg_conf - original_avg_conf

        result = EnhancementResult(
            original_transcript=transcript,
            enhanced_transcript=enhanced_text,
            word_timeline=tokens,
            error_map=error_map,
            diagnostics=diagnostics,
            confidence_improvement=confidence_improvement,
        )

        logger.info(f"Enhancement complete. Confidence improvement: {confidence_improvement:.2%}")
        return result

    def _build_tokens(
        self,
        word_timestamps: list[dict[str, Any]],
        word_confidences: list[float],
    ) -> list[WordToken]:
        """Build WordToken list from raw inputs."""
        tokens = []
        for i, ts in enumerate(word_timestamps):
            conf = word_confidences[i] if i < len(word_confidences) else 0.0
            token = WordToken(
                word=ts.get("word", ""),
                start_time=ts.get("start", 0.0),
                end_time=ts.get("end", 0.0),
                confidence=conf,
            )
            tokens.append(token)
        return tokens

    async def analyze_only(
        self,
        transcript: str,
        word_timestamps: list[dict[str, Any]],
        word_confidences: list[float],
    ) -> dict[str, Any]:
        """
        Analyze transcript without enhancement (diagnostics only).

        Args:
            transcript: Raw transcript
            word_timestamps: Word timing information
            word_confidences: Confidence scores

        Returns:
            Analysis results with detected issues
        """
        tokens = self._build_tokens(word_timestamps, word_confidences)

        low_confidence_spans = self.confidence_detector.detect(tokens)
        anomalies = self.anomaly_detector.detect(tokens)
        numeric_gaps = self.numeric_detector.detect(tokens)

        return {
            "transcript": transcript,
            "word_count": len(tokens),
            "avg_confidence": sum(word_confidences) / len(word_confidences) if word_confidences else 0,
            "low_confidence_spans": low_confidence_spans,
            "anomalies": anomalies,
            "numeric_gaps": numeric_gaps,
            "issues_detected": len(low_confidence_spans) + len(anomalies) + len(numeric_gaps),
        }
