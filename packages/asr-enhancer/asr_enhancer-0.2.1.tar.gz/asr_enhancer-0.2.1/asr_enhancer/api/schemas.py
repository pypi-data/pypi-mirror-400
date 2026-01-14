"""
API Schemas
===========

Pydantic models for API request/response validation.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Request Models
# ============================================================================


class WordTimestamp(BaseModel):
    """Word with timing information."""

    word: str = Field(..., description="The word text")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")


class EnhanceRequest(BaseModel):
    """Request for transcript enhancement."""

    transcript: str = Field(
        ...,
        description="Raw transcript from Parakeet ASR",
        min_length=1,
    )
    word_timestamps: list[WordTimestamp] = Field(
        ...,
        description="Word-level timestamps",
    )
    word_confidences: list[float] = Field(
        ...,
        description="Confidence scores per word (0-1)",
    )
    audio_path: Optional[str] = Field(
        None,
        description="Path to audio file for re-ASR (optional)",
    )
    domain_lexicon: Optional[dict[str, list[str]]] = Field(
        None,
        description="Domain-specific vocabulary mapping",
    )
    options: Optional[dict[str, Any]] = Field(
        None,
        description="Additional processing options",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "transcript": "my phone number is nine one two tree four five six seven ate nine",
                "word_timestamps": [
                    {"word": "my", "start": 0.0, "end": 0.2},
                    {"word": "phone", "start": 0.2, "end": 0.5},
                    {"word": "number", "start": 0.5, "end": 0.8},
                    {"word": "is", "start": 0.8, "end": 0.9},
                    {"word": "nine", "start": 0.9, "end": 1.1},
                    {"word": "one", "start": 1.1, "end": 1.3},
                    {"word": "two", "start": 1.3, "end": 1.5},
                    {"word": "tree", "start": 1.5, "end": 1.7},
                    {"word": "four", "start": 1.7, "end": 1.9},
                    {"word": "five", "start": 1.9, "end": 2.1},
                    {"word": "six", "start": 2.1, "end": 2.3},
                    {"word": "seven", "start": 2.3, "end": 2.5},
                    {"word": "ate", "start": 2.5, "end": 2.7},
                    {"word": "nine", "start": 2.7, "end": 2.9},
                ],
                "word_confidences": [
                    0.95, 0.92, 0.89, 0.98, 0.85, 0.91, 0.88,
                    0.45, 0.92, 0.87, 0.90, 0.93, 0.38, 0.91
                ],
            }
        }
    }


class AnalyzeRequest(BaseModel):
    """Request for transcript analysis (no enhancement)."""

    transcript: str = Field(
        ...,
        description="Raw transcript to analyze",
    )
    word_timestamps: list[WordTimestamp] = Field(
        ...,
        description="Word-level timestamps",
    )
    word_confidences: list[float] = Field(
        ...,
        description="Confidence scores per word",
    )


# ============================================================================
# Response Models
# ============================================================================


class EnhancedWord(BaseModel):
    """Enhanced word with metadata."""

    word: str
    start_time: float
    end_time: float
    confidence: float
    is_corrected: bool = False
    correction_source: Optional[str] = None


class ErrorSpan(BaseModel):
    """Detected error span."""

    start_idx: int
    end_idx: int
    start_time: float
    end_time: float
    error_type: str
    description: str
    severity: str


class EnhanceResponse(BaseModel):
    """Response from enhancement endpoint."""

    original_transcript: str = Field(
        ...,
        description="Original input transcript",
    )
    enhanced_transcript: str = Field(
        ...,
        description="Enhanced transcript",
    )
    word_timeline: list[EnhancedWord] = Field(
        ...,
        description="Enhanced word-level timeline",
    )
    error_map: dict[str, list[dict[str, Any]]] = Field(
        ...,
        description="Detected errors by type",
    )
    confidence_improvement: float = Field(
        ...,
        description="Confidence improvement percentage",
    )
    processing_time_ms: float = Field(
        ...,
        description="Processing time in milliseconds",
    )


class AnalyzeResponse(BaseModel):
    """Response from analysis endpoint."""

    transcript: str
    word_count: int
    avg_confidence: float
    low_confidence_spans: list[dict[str, Any]]
    anomalies: list[dict[str, Any]]
    numeric_gaps: list[dict[str, Any]]
    issues_detected: int
    recommendations: list[str]


class DiagnosticsResponse(BaseModel):
    """Response from diagnostics endpoint."""

    pipeline_status: str
    stages: list[dict[str, Any]]
    validation: dict[str, Any]
    performance_metrics: dict[str, float]
    config: dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    components: dict[str, bool | str] = Field(
        ...,
        description="Component availability",
    )


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID")


# ============================================================================
# Unified Pipeline Models
# ============================================================================


class UnifiedEnhanceRequest(BaseModel):
    """Request for unified ASR enhancement pipeline."""

    audio_path: str = Field(
        ...,
        description="Path to the audio file",
    )
    primary_text: str = Field(
        ...,
        description="Primary ASR output (from Parakeet)",
        min_length=1,
    )
    audio_duration: Optional[float] = Field(
        None,
        description="Audio duration in seconds (auto-detected if not provided)",
    )
    domain: str = Field(
        "general",
        description="Domain context (banking, telecom, insurance, general)",
    )
    force_secondary_asr: bool = Field(
        False,
        description="Force re-run with secondary ASR even if no gaps detected",
    )
    enable_llm_polish: bool = Field(
        True,
        description="Enable LLM-based punctuation and spelling correction",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "audio_path": "/path/to/call.wav",
                "primary_text": "आपके कार्ड पर चार्ज है प्रीमियम फ्री है",
                "audio_duration": 30.0,
                "domain": "banking",
                "force_secondary_asr": False,
                "enable_llm_polish": True,
            }
        }
    }


class GapInfo(BaseModel):
    """Information about a detected gap."""

    gap_type: str = Field(..., description="Type of gap detected")
    confidence: float = Field(..., description="Detection confidence (0-1)")
    context: str = Field(..., description="Surrounding text context")
    suggested_content: Optional[str] = Field(
        None, description="LLM-suggested missing content"
    )


class UnifiedEnhanceResponse(BaseModel):
    """Response from unified enhancement pipeline."""

    original_text: str = Field(
        ...,
        description="Original primary ASR text",
    )
    enhanced_text: str = Field(
        ...,
        description="Enhanced transcript",
    )
    had_gaps: bool = Field(
        ...,
        description="Whether gaps were detected and recovered",
    )
    secondary_asr_used: bool = Field(
        ...,
        description="Whether secondary ASR was used",
    )
    secondary_asr_text: Optional[str] = Field(
        None,
        description="Text from secondary ASR (if used)",
    )
    gaps_detected: list[GapInfo] = Field(
        default_factory=list,
        description="List of gaps detected",
    )
    duration_ratio: Optional[float] = Field(
        None,
        description="Characters per second ratio",
    )
    expected_ratio: float = Field(
        12.0,
        description="Expected characters per second",
    )
    corrections_made: list[dict] = Field(
        default_factory=list,
        description="List of corrections applied",
    )
    processing_stages: list[str] = Field(
        default_factory=list,
        description="Stages executed in pipeline",
    )
    confidence: float = Field(
        ...,
        description="Overall confidence score (0-1)",
    )
    processing_time_ms: float = Field(
        ...,
        description="Processing time in milliseconds",
    )

