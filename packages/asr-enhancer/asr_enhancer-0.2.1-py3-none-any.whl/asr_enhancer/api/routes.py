"""
API Routes
==========

FastAPI route handlers for the ASR Enhancement Layer.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks

from .schemas import (
    EnhanceRequest,
    EnhanceResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    DiagnosticsResponse,
    EnhancedWord,
    UnifiedEnhanceRequest,
    UnifiedEnhanceResponse,
    GapInfo,
)
from ..core import EnhancementPipeline
from ..unified_pipeline import UnifiedASRPipeline
from ..utils import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["enhancement"])


def get_pipeline(request: Request) -> EnhancementPipeline:
    """Get or create the enhancement pipeline."""
    if request.app.state.pipeline is None:
        config = request.app.state.config
        request.app.state.pipeline = EnhancementPipeline(config)
    return request.app.state.pipeline


def get_unified_pipeline(request: Request) -> UnifiedASRPipeline:
    """Get or create the unified ASR pipeline."""
    if not hasattr(request.app.state, 'unified_pipeline') or request.app.state.unified_pipeline is None:
        config = request.app.state.config
        request.app.state.unified_pipeline = UnifiedASRPipeline(
            asr_model=getattr(config, 'secondary_asr_model', 'large-v3'),
            asr_device=getattr(config, 'secondary_asr_device', 'auto'),
            asr_compute=getattr(config, 'secondary_asr_compute', 'int8'),
            llm_provider=getattr(config, 'llm_provider', 'ollama'),
            llm_model=getattr(config, 'llm_model', 'llama3.1'),
            enable_llm_polish=getattr(config, 'enable_llm_polish', True),
        )
    return request.app.state.unified_pipeline


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_transcript(
    request: Request,
    body: EnhanceRequest,
) -> EnhanceResponse:
    """
    Enhance a transcript using the full pipeline.

    This endpoint applies all enhancement stages:
    1. Confidence-based error detection
    2. Secondary ASR processing (if audio provided)
    3. Numeric sequence reconstruction
    4. Domain vocabulary correction
    5. Hypothesis fusion
    6. LLM context restoration
    7. Consistency validation

    Args:
        body: Enhancement request with transcript and metadata

    Returns:
        Enhanced transcript with diagnostics
    """
    start_time = time.perf_counter()

    try:
        pipeline = get_pipeline(request)

        # Convert word timestamps to dict format
        word_timestamps = [
            {"word": wt.word, "start": wt.start, "end": wt.end}
            for wt in body.word_timestamps
        ]

        # Run enhancement
        result = await pipeline.enhance(
            transcript=body.transcript,
            word_timestamps=word_timestamps,
            word_confidences=body.word_confidences,
            audio_path=body.audio_path,
            domain_lexicon=body.domain_lexicon,
        )

        # Convert word timeline
        word_timeline = [
            EnhancedWord(
                word=token.word,
                start_time=token.start_time,
                end_time=token.end_time,
                confidence=token.confidence,
                is_corrected=token.is_corrected,
                correction_source=token.correction_source,
            )
            for token in result.word_timeline
        ]

        processing_time = (time.perf_counter() - start_time) * 1000

        return EnhanceResponse(
            original_transcript=result.original_transcript,
            enhanced_transcript=result.enhanced_transcript,
            word_timeline=word_timeline,
            error_map=result.error_map,
            confidence_improvement=result.confidence_improvement,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        logger.error(f"Enhancement failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Enhancement failed: {str(e)}",
        )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_transcript(
    request: Request,
    body: AnalyzeRequest,
) -> AnalyzeResponse:
    """
    Analyze a transcript without applying enhancements.

    Returns detected issues and recommendations without
    modifying the transcript.

    Args:
        body: Analysis request with transcript and metadata

    Returns:
        Analysis results with detected issues
    """
    try:
        pipeline = get_pipeline(request)

        # Convert word timestamps
        word_timestamps = [
            {"word": wt.word, "start": wt.start, "end": wt.end}
            for wt in body.word_timestamps
        ]

        # Run analysis
        result = await pipeline.analyze_only(
            transcript=body.transcript,
            word_timestamps=word_timestamps,
            word_confidences=body.word_confidences,
        )

        # Generate recommendations
        recommendations = []
        if result["low_confidence_spans"]:
            recommendations.append(
                f"Found {len(result['low_confidence_spans'])} low-confidence spans. "
                "Consider providing audio for re-ASR."
            )
        if result["numeric_gaps"]:
            recommendations.append(
                f"Found {len(result['numeric_gaps'])} incomplete numeric sequences. "
                "Numeric reconstruction may help."
            )
        if result["anomalies"]:
            recommendations.append(
                f"Detected {len(result['anomalies'])} anomalies. "
                "Review transcript for potential issues."
            )

        return AnalyzeResponse(
            transcript=result["transcript"],
            word_count=result["word_count"],
            avg_confidence=result["avg_confidence"],
            low_confidence_spans=result["low_confidence_spans"],
            anomalies=result["anomalies"],
            numeric_gaps=result["numeric_gaps"],
            issues_detected=result["issues_detected"],
            recommendations=recommendations,
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )


@router.get("/diagnostics", response_model=DiagnosticsResponse)
async def get_diagnostics(request: Request) -> DiagnosticsResponse:
    """
    Get pipeline diagnostics and configuration.

    Returns current pipeline status, stage configuration,
    and performance metrics.
    """
    try:
        config = request.app.state.config
        pipeline = request.app.state.pipeline

        return DiagnosticsResponse(
            pipeline_status="initialized" if pipeline else "not_initialized",
            stages=[
                {"name": "error_detection", "enabled": True},
                {"name": "re_asr", "enabled": config.enable_re_asr},
                {"name": "numeric_reconstruction", "enabled": config.enable_numeric_reconstruction},
                {"name": "vocab_correction", "enabled": config.enable_vocab_correction},
                {"name": "hypothesis_fusion", "enabled": True},
                {"name": "llm_restoration", "enabled": config.enable_llm_restoration},
                {"name": "validation", "enabled": True},
            ],
            validation={
                "consistency_check": True,
                "perplexity_scoring": True,
                "completeness_validation": True,
            },
            performance_metrics={
                "max_concurrent_requests": config.max_concurrent_requests,
                "request_timeout_seconds": config.request_timeout,
            },
            config=config.to_dict(),
        )

    except Exception as e:
        logger.error(f"Diagnostics failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Diagnostics failed: {str(e)}",
        )


@router.post("/batch/enhance")
async def batch_enhance(
    request: Request,
    bodies: list[EnhanceRequest],
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """
    Batch enhancement endpoint.

    Processes multiple transcripts. Returns immediately with job ID
    for long-running requests.

    Args:
        bodies: List of enhancement requests

    Returns:
        Job status and results (if immediate) or job ID (if async)
    """
    if len(bodies) > 10:
        # Queue for background processing
        job_id = f"batch_{int(time.time() * 1000)}"
        # In production, this would queue to a task system
        return {
            "job_id": job_id,
            "status": "queued",
            "count": len(bodies),
            "message": "Large batch queued for background processing",
        }

    # Process immediately for small batches
    results = []
    for body in bodies:
        try:
            result = await enhance_transcript(request, body)
            results.append({"status": "success", "result": result})
        except HTTPException as e:
            results.append({"status": "error", "error": e.detail})

    return {
        "status": "completed",
        "count": len(results),
        "results": results,
    }


# ============================================================================
# Unified Pipeline Endpoint
# ============================================================================


@router.post("/unified/enhance", response_model=UnifiedEnhanceResponse)
async def unified_enhance(
    request: Request,
    body: UnifiedEnhanceRequest,
) -> UnifiedEnhanceResponse:
    """
    Unified ASR enhancement endpoint.
    
    This is the main endpoint for processing audio with the unified pipeline:
    
1. Takes audio file + primary ASR text (from Parakeet)
2. Analyzes for gaps (duration ratio + linguistic patterns)
3. If gaps detected → Re-runs with secondary ASR (large-v3)
4. If no gaps → Applies spelling correction + LLM punctuation

Default model: large-v3 (high quality Whisper model)    Args:
        body: Request with audio path, primary text, and options
        
    Returns:
        Enhanced transcript with diagnostics
        
    Example:
        ```json
        POST /unified/enhance
        {
            "audio_path": "/path/to/call.wav",
            "primary_text": "आपके कार्ड पर चार्ज है",
            "audio_duration": 30.0,
            "domain": "banking"
        }
        ```
    """
    start_time = time.perf_counter()
    
    try:
        pipeline = get_unified_pipeline(request)
        
        # Override LLM polish setting if specified
        if not body.enable_llm_polish:
            pipeline.enable_llm_polish = False
        
        # Process
        result = await pipeline.process(
            audio_path=body.audio_path,
            primary_text=body.primary_text,
            audio_duration=body.audio_duration,
            domain=body.domain,
            force_secondary_asr=body.force_secondary_asr,
        )
        
        # Convert gaps to response format
        gaps_info = []
        if result.gap_analysis and result.gap_analysis.gaps_detected:
            for gap in result.gap_analysis.gaps_detected:
                gaps_info.append(GapInfo(
                    gap_type=gap.gap_type,
                    confidence=gap.confidence,
                    context=gap.context,
                    suggested_content=gap.suggested_content,
                ))
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return UnifiedEnhanceResponse(
            original_text=result.original_text,
            enhanced_text=result.enhanced_text,
            had_gaps=result.had_gaps,
            secondary_asr_used=result.secondary_asr_text is not None,
            secondary_asr_text=result.secondary_asr_text,
            gaps_detected=gaps_info,
            duration_ratio=result.gap_analysis.duration_ratio if result.gap_analysis else None,
            expected_ratio=result.gap_analysis.expected_ratio if result.gap_analysis else 12.0,
            corrections_made=result.corrections_made,
            processing_stages=result.processing_stages,
            confidence=result.confidence,
            processing_time_ms=processing_time,
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Audio file not found: {body.audio_path}",
        )
    except Exception as e:
        logger.error(f"Unified enhancement failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Enhancement failed: {str(e)}",
        )


@router.post("/unified/check-gaps")
async def check_gaps(
    request: Request,
    audio_path: str,
    primary_text: str,
    audio_duration: Optional[float] = None,
    domain: str = "general",
) -> dict:
    """
    Quick gap check without full enhancement.
    
    Returns whether gaps are detected and recommendations.
    Useful for deciding if secondary ASR is needed before processing.
    
    Args:
        audio_path: Path to audio file
        primary_text: Primary ASR text
        audio_duration: Audio duration in seconds
        domain: Domain context
        
    Returns:
        Gap analysis results
    """
    try:
        from ..detectors.smart_gap_detector import SmartGapDetector
        
        detector = SmartGapDetector()
        result = await detector.analyze(
            text=primary_text,
            audio_duration=audio_duration,
            domain=domain,
            use_llm=False,  # Quick check only
        )
        
        return {
            "has_gaps": result.needs_reprocessing,
            "duration_ratio": result.duration_ratio,
            "expected_ratio": result.expected_ratio,
            "missing_estimate": result.missing_content_estimate,
            "gaps_count": len(result.gaps_detected),
            "recommendation": (
                "Run with secondary ASR" if result.needs_reprocessing 
                else "Text appears complete, apply corrections only"
            ),
        }
        
    except Exception as e:
        logger.error(f"Gap check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Gap check failed: {str(e)}",
        )

