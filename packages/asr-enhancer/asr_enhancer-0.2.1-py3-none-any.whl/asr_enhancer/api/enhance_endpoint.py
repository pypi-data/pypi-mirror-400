"""
ASR Enhancement Endpoint
========================

Simple endpoint that takes audio + primary transcript and returns enhanced text.

Flow:
    Audio + Primary Text (Parakeet)
            ↓
    ┌─────────────────────┐
    │   Gap Detection     │ ← Duration ratio check
    └─────────────────────┘
            ↓
        Has Gaps?
       /        \
      YES        NO
       ↓          ↓
    ┌──────────┐ ┌──────────────┐
    │Secondary │ │Hindi Spelling│
    │ASR       │ │Correction    │
    │(large-v3)│ └──────────────┘
    └──────────┘        ↓
       ↓         ┌──────────────┐
      Merge      │              │
       ↓         │              │
    ┌──────────┐ │   LLM Polish │ ← Both paths!
    │Hindi     │ │   (mT5)      │
    │Spelling  │ │              │
    └──────────┘ │              │
       ↓         │              │
    ┌──────────────────────────┐
    │      LLM Polish (mT5)    │ ← ICICI Banking optimized
    └──────────────────────────┘
            ↓
       Enhanced Text
       (with consent + proper formatting)
"""

import os
import sys
import tempfile
import time
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel, Field

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

router = APIRouter(prefix="/v2", tags=["simple-enhancement"])


# ============================================================================
# Request/Response Models
# ============================================================================

class EnhanceRequest(BaseModel):
    """Request for text-only enhancement (no audio upload)."""
    audio_path: str = Field(..., description="Path to audio file on server")
    primary_text: str = Field(..., description="Primary ASR transcript")
    audio_duration: Optional[float] = Field(None, description="Audio duration in seconds (auto-detected if not provided)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "audio_path": "/path/to/audio.mp3",
                "primary_text": "Yeah कोई भी पैडल कम से एंड फिफ्टी थाउजेंड...",
                "audio_duration": 119.3
            }
        }
    }


class EnhanceResponse(BaseModel):
    """Response from enhancement endpoint."""
    original_text: str = Field(..., description="Original primary transcript")
    enhanced_text: str = Field(..., description="Enhanced transcript")
    had_gaps: bool = Field(..., description="Whether gaps were detected")
    coverage_percent: float = Field(..., description="Text coverage percentage")
    secondary_asr_used: bool = Field(..., description="Whether secondary ASR was used")
    secondary_asr_text: Optional[str] = Field(None, description="Secondary ASR output if used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


# ============================================================================
# Core Functions
# ============================================================================

def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read audio file: {e}")


def detect_gaps(text: str, duration: float) -> tuple[bool, float]:
    """
    Detect if transcript has gaps based on duration ratio.
    
    Expected: ~13 chars/second for Hindi/Hinglish
    If actual < 70% of expected → gaps detected
    """
    if duration <= 0:
        return False, 1.0
    
    chars_per_sec = len(text) / duration
    expected_ratio = 13.0  # Hindi/Hinglish average
    coverage = min(chars_per_sec / expected_ratio, 1.0)
    
    has_gaps = coverage < 0.70  # Less than 70% coverage
    return has_gaps, coverage


def run_secondary_asr(audio_path: str, app_models=None) -> str:
    """Run Faster-Whisper on audio using pre-loaded model from app state."""
    model = None
    
    # Try to use pre-loaded model
    if app_models and hasattr(app_models, 'whisper_model'):
        model = app_models.whisper_model
    
    # Fallback: load model on demand
    if model is None:
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
        except ImportError:
            raise HTTPException(
                status_code=500, 
                detail="faster-whisper not installed. Run: pip install faster-whisper"
            )
    
    try:
        segments, info = model.transcribe(
            audio_path,
            language="hi",
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )
        
        text = " ".join([seg.text.strip() for seg in segments])
        return text
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Secondary ASR failed: {e}")


def correct_hindi_spelling(text: str) -> str:
    """Apply Hindi/Hinglish spelling corrections for banking domain."""
    # Common ASR errors in banking calls
    corrections = {
        # Numbers misheard
        "फिफ्टी थाउजेंड": "50,000",
        "फिफ्टी थाउज़ेंड": "50,000", 
        "fifty thousand": "50,000",
        "टू हंड्रेड": "200",
        "थ्री हंड्रेड": "300",
        "फाइव हंड्रेड": "500",
        "वन लाख": "1,00,000",
        "टेन थाउजेंड": "10,000",
        
        # Banking terms
        "पीनियम": "प्रीमियम",
        "प्रीमिअम": "प्रीमियम",
        "इंटर वेस्ट": "interest",
        "इंटरेस्ट": "interest",
        "क्रेडिट कार्ड": "credit card",
        "रिवार्ड": "reward",
        "रिवॉर्ड्स": "rewards",
        "कैशबैक": "cashback",
        "ट्रांजैक्शन": "transaction",
        "मिनिमम": "minimum",
        "एनुअल": "annual",
        "चार्जेस": "charges",
        
        # Common misheard words
        "पैडल": "स्पेंड",  # "pedal" → "spend"
        "teachers": "तीस",  # "teachers" → "30"
        "एंड": "और",
    }
    
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    
    return text


def merge_transcripts(primary: str, secondary: str) -> str:
    """
    Merge primary and secondary transcripts.
    Use secondary if significantly longer (recovered missing content).
    """
    if len(secondary) > len(primary) * 1.3:
        # Secondary has much more content - use it
        return secondary
    elif len(secondary) > len(primary):
        # Secondary slightly longer - prefer secondary
        return secondary
    else:
        # Primary is fine
        return primary


def llm_polish(text: str, local_llm=None) -> str:
    """
    Polish text with local LLM for better punctuation and flow.
    
    Args:
        text: Input text
        local_llm: Pre-loaded local LLM instance
        
    Returns:
        Polished text
    """
    if not local_llm or not local_llm.is_available():
        return text  # Skip if LLM not available
    
    try:
        # Use local LLM polish method (no API calls)
        polished = local_llm.polish_hindi_text(text)
        
        # Sanity check
        if polished and len(polished) > len(text) * 0.5:
            return polished
        return text
        
    except Exception:
        return text  # Return original on any error


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_transcript(request: EnhanceRequest, req: Request) -> EnhanceResponse:
    """
    Enhance ASR transcript.
    
    Takes audio path + primary transcript, detects gaps, and either:
    - Runs secondary ASR if gaps detected (>30% content missing)
    - Applies spelling correction + LLM polish if no gaps
    
    Uses pre-loaded models for fast inference.
    """
    start_time = time.perf_counter()
    
    # Get pre-loaded models from app state
    app_models = getattr(req.app.state, 'models', None)
    local_llm = app_models.llm_model if (app_models and app_models.llm_ready) else None
    
    # Validate audio file exists
    if not os.path.exists(request.audio_path):
        raise HTTPException(status_code=404, detail=f"Audio file not found: {request.audio_path}")
    
    # Get audio duration
    duration = request.audio_duration or get_audio_duration(request.audio_path)
    
    # Detect gaps
    has_gaps, coverage = detect_gaps(request.primary_text, duration)
    
    secondary_text = None
    enhanced_text = request.primary_text
    
    if has_gaps:
        # Path A: Gaps detected → Secondary ASR → Merge → Spelling correction → LLM Polish
        secondary_text = run_secondary_asr(request.audio_path, app_models)
        enhanced_text = merge_transcripts(request.primary_text, secondary_text)
        enhanced_text = correct_hindi_spelling(enhanced_text)
        enhanced_text = llm_polish(enhanced_text, local_llm)  # Added LLM polish
    else:
        # Path B: No gaps → Hindi Correction → LLM Polish
        enhanced_text = correct_hindi_spelling(request.primary_text)
        enhanced_text = llm_polish(enhanced_text, local_llm)
    
    processing_time = (time.perf_counter() - start_time) * 1000
    
    return EnhanceResponse(
        original_text=request.primary_text,
        enhanced_text=enhanced_text,
        had_gaps=has_gaps,
        coverage_percent=coverage * 100,
        secondary_asr_used=secondary_text is not None,
        secondary_asr_text=secondary_text,
        processing_time_ms=processing_time,
    )


@router.post("/enhance/upload", response_model=EnhanceResponse)
async def enhance_with_upload(
    req: Request,
    audio: UploadFile = File(..., description="Audio file"),
    primary_text: str = Form(..., description="Primary ASR transcript"),
) -> EnhanceResponse:
    """
    Enhance ASR transcript with audio file upload.
    
    Upload audio file + provide primary transcript.
    Uses pre-loaded models for fast inference.
    """
    start_time = time.perf_counter()
    
    # Get pre-loaded models from app state
    app_models = getattr(req.app.state, 'models', None)
    llm_ready = app_models.llm_ready if app_models else False
    
    # Save uploaded file temporarily
    suffix = Path(audio.filename).suffix if audio.filename else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Get duration
        duration = get_audio_duration(tmp_path)
        
        # Detect gaps
        has_gaps, coverage = detect_gaps(primary_text, duration)
        
        secondary_text = None
        enhanced_text = primary_text
        
        if has_gaps:
            secondary_text = run_secondary_asr(tmp_path, app_models)
            enhanced_text = merge_transcripts(primary_text, secondary_text)
            enhanced_text = correct_hindi_spelling(enhanced_text)
            enhanced_text = llm_polish(enhanced_text, llm_ready)  # Added LLM polish
        else:
            enhanced_text = correct_hindi_spelling(primary_text)
            enhanced_text = llm_polish(enhanced_text, llm_ready)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return EnhanceResponse(
            original_text=primary_text,
            enhanced_text=enhanced_text,
            had_gaps=has_gaps,
            coverage_percent=coverage * 100,
            secondary_asr_used=secondary_text is not None,
            secondary_asr_text=secondary_text,
            processing_time_ms=processing_time,
        )
    
    finally:
        # Cleanup temp file
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/health")
async def health_check(req: Request):
    """Health check endpoint with model status."""
    app_models = getattr(req.app.state, 'models', None)
    return {
        "status": "ok",
        "service": "asr-enhancement-v2",
        "models": {
            "model_loaded": app_models.whisper_model is not None if app_models else False,
            "corrector_ready": app_models.llm_ready if app_models else False,
        }
    }
