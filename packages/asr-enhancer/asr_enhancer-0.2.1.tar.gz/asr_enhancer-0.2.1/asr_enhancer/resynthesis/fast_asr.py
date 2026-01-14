"""
Fast Secondary ASR
==================

Fast secondary ASR using Faster-Whisper Large-V3 with CTranslate2.
Supports int8 and float16 quantization for optimal speed/accuracy tradeoff.

Faster-Whisper is 4x faster than OpenAI Whisper with similar accuracy.
Large-V3 provides the best accuracy for multilingual transcription.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Literal
import logging

logger = logging.getLogger(__name__)


@dataclass
class ASRResult:
    """Result from ASR processing."""
    
    text: str
    segments: list[dict]  # [{start, end, text}]
    language: str
    confidence: float


class SecondaryASR(ABC):
    """Abstract base class for secondary ASR engines."""
    
    @abstractmethod
    async def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "hi",
    ) -> ASRResult:
        """Transcribe audio file."""
        pass
    
    @abstractmethod
    async def transcribe_segment(
        self,
        audio_path: Union[str, Path],
        start_time: float,
        end_time: float,
        language: str = "hi",
    ) -> ASRResult:
        """Transcribe a specific segment of audio."""
        pass


# Model size options
ModelSize = Literal[
    "tiny", "tiny.en",
    "base", "base.en", 
    "small", "small.en",
    "medium", "medium.en",
    "large-v1", "large-v2", "large-v3",  # large-v3 is recommended
    "distil-large-v2", "distil-large-v3",  # Distilled versions (faster)
]

# Compute type options
ComputeType = Literal[
    "float16",      # Best for GPU with good VRAM
    "int8",         # Best for CPU, good balance
    "int8_float16", # Mixed precision
    "float32",      # Fallback for compatibility
]


class FasterWhisperASR(SecondaryASR):
    """
    Fast secondary ASR using Faster-Whisper Large-V3 (CTranslate2).
    
    Recommended configuration for Hindi/Hinglish:
        - Model: large-v3 (best multilingual accuracy)
        - Compute: int8 (CPU) or float16 (GPU)
    
    Performance (relative to OpenAI Whisper):
        - 4x faster on CPU
        - 2x faster on GPU
        - Same accuracy
    
    Install: 
        pip install faster-whisper
        
    For GPU support:
        pip install faster-whisper[gpu]
    
    Example:
        ```python
        # For CPU (int8 quantization)
        asr = FasterWhisperASR(
            model_size="large-v3",
            device="cpu",
            compute_type="int8",
        )
        
        # For GPU (float16)
        asr = FasterWhisperASR(
            model_size="large-v3",
            device="cuda",
            compute_type="float16",
        )
        
        result = await asr.transcribe("audio.wav", language="hi")
        print(result.text)
        ```
    """
    
    # Recommended settings for different use cases
    PRESETS = {
        "fast_cpu": {
            "model_size": "small",
            "device": "cpu",
            "compute_type": "int8",
        },
        "balanced_cpu": {
            "model_size": "medium",
            "device": "cpu",
            "compute_type": "int8",
        },
        "accurate_cpu": {
            "model_size": "large-v3",
            "device": "cpu",
            "compute_type": "int8",
        },
        "fast_gpu": {
            "model_size": "distil-large-v3",
            "device": "cuda",
            "compute_type": "float16",
        },
        "accurate_gpu": {
            "model_size": "large-v3",
            "device": "cuda",
            "compute_type": "float16",
        },
    }
    
    def __init__(
        self,
        model_size: str = "distil-large-v3",  # Default to distil-large-v3 for speed
        device: str = "auto",  # cpu, cuda, auto
        compute_type: str = "int8",  # int8 for CPU, float16 for GPU
        num_workers: int = 4,  # Parallel workers for faster processing
        cpu_threads: int = 0,  # 0 = auto-detect
        preset: Optional[str] = None,  # Use a preset configuration
    ):
        """
        Initialize Faster-Whisper.
        
        Args:
            model_size: Model to use. Default: "distil-large-v3" for speed
            device: "cpu", "cuda", or "auto"
            compute_type: "int8" (CPU), "float16" (GPU), or "int8_float16"
            num_workers: Number of parallel workers
            cpu_threads: CPU threads (0 = auto)
            preset: Use preset config ("fast_cpu", "accurate_gpu", etc.)
        
        Presets available:
            - fast_cpu: small model, int8
            - balanced_cpu: medium model, int8
            - accurate_cpu: large-v3, int8
            - fast_gpu: distil-large-v3, float16
            - accurate_gpu: large-v3, float16
        """
        # Apply preset if specified
        if preset and preset in self.PRESETS:
            config = self.PRESETS[preset]
            model_size = config["model_size"]
            device = config["device"]
            compute_type = config["compute_type"]
            logger.info(f"Using preset: {preset}")
        
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.num_workers = num_workers
        self.cpu_threads = cpu_threads
        self._model = None
        
        logger.info(
            f"FasterWhisperASR configured: model={model_size}, "
            f"device={device}, compute={compute_type}"
        )
    
    @classmethod
    def from_preset(cls, preset: str) -> "FasterWhisperASR":
        """
        Create ASR instance from preset.
        
        Args:
            preset: One of "fast_cpu", "balanced_cpu", "accurate_cpu",
                   "fast_gpu", "accurate_gpu"
        
        Returns:
            Configured FasterWhisperASR instance
        """
        if preset not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {preset}. Available: {list(cls.PRESETS.keys())}")
        return cls(preset=preset)
    
    def _get_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                
                logger.info(f"Loading Faster-Whisper model: {self.model_size}...")
                
                self._model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    num_workers=self.num_workers,
                    cpu_threads=self.cpu_threads,
                )
                
                logger.info(
                    f"Loaded Faster-Whisper {self.model_size} "
                    f"on {self.device} with {self.compute_type}"
                )
                
            except ImportError:
                raise ImportError(
                    "faster-whisper not installed. "
                    "Install with: pip install faster-whisper\n"
                    "For GPU: pip install faster-whisper[gpu]"
                )
        return self._model
    
    async def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "hi",
    ) -> ASRResult:
        """
        Transcribe full audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code (hi, en, etc.)
            
        Returns:
            ASRResult with transcription
        """
        model = self._get_model()
        
        # Run in thread pool to not block async
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._transcribe_sync(str(audio_path), language),
        )
        
        return result
    
    def _transcribe_sync(self, audio_path: str, language: str) -> ASRResult:
        """Synchronous transcription."""
        model = self._get_model()
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # Filter out silence
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
        )
        
        # Collect segments
        all_segments = []
        full_text = []
        
        for segment in segments:
            all_segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
            })
            full_text.append(segment.text.strip())
        
        return ASRResult(
            text=" ".join(full_text),
            segments=all_segments,
            language=info.language,
            confidence=info.language_probability,
        )
    
    async def transcribe_segment(
        self,
        audio_path: Union[str, Path],
        start_time: float,
        end_time: float,
        language: str = "hi",
    ) -> ASRResult:
        """
        Transcribe a specific segment of audio.
        
        Note: This extracts and processes the segment, which is slower
        than full transcription for single segments. Use batch processing
        for multiple segments.
        
        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            language: Language code
            
        Returns:
            ASRResult for the segment
        """
        # Extract segment using ffmpeg or pydub
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(str(audio_path))
            segment = audio[int(start_time * 1000):int(end_time * 1000)]
            
            # Save temp file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
                segment.export(temp_path, format='wav')
            
            try:
                result = await self.transcribe(temp_path, language)
            finally:
                # Cleanup temp file
                Path(temp_path).unlink(missing_ok=True)
            
            return result
            
        except ImportError:
            raise ImportError(
                "pydub not installed. Install with: pip install pydub"
            )


class ParallelASR:
    """
    Run multiple ASR models in parallel and merge results.
    
    Useful when you want to combine Parakeet's speed with Whisper's robustness.
    """
    
    def __init__(self, primary_asr=None, secondary_asr: Optional[SecondaryASR] = None):
        """
        Initialize parallel ASR.
        
        Args:
            primary_asr: Primary ASR (e.g., Parakeet wrapper)
            secondary_asr: Secondary ASR (e.g., FasterWhisperASR)
        """
        self.primary = primary_asr
        self.secondary = secondary_asr or FasterWhisperASR(model_size="small")
    
    async def transcribe_with_recovery(
        self,
        audio_path: Union[str, Path],
        primary_text: str,
        gap_segments: list[dict],
        language: str = "hi",
    ) -> str:
        """
        Use secondary ASR to fill gaps in primary transcription.
        
        Args:
            audio_path: Path to audio file
            primary_text: Text from primary ASR (Parakeet)
            gap_segments: List of {start_time, end_time} for gaps
            language: Language code
            
        Returns:
            Enhanced transcript with recovered content
        """
        if not gap_segments:
            return primary_text
        
        # Transcribe gap segments
        recovered_texts = []
        for seg in gap_segments:
            try:
                result = await self.secondary.transcribe_segment(
                    audio_path,
                    seg['start_time'],
                    seg['end_time'],
                    language,
                )
                recovered_texts.append({
                    'segment': seg,
                    'recovered': result.text,
                })
            except Exception as e:
                logger.warning(f"Failed to recover segment: {e}")
        
        # Merge recovered content
        # This is a simple merge - could be enhanced with LLM
        enhanced = primary_text
        for rec in recovered_texts:
            if rec['recovered']:
                # Find insertion point based on context
                context = rec['segment'].get('context', '')
                if '[GAP]' in context:
                    before = context.split('[GAP]')[0].strip()[-50:]
                    if before and before in enhanced:
                        # Insert recovered text after the context
                        pos = enhanced.find(before) + len(before)
                        enhanced = enhanced[:pos] + f" {rec['recovered']} " + enhanced[pos:]
        
        return enhanced


class QuickASR:
    """
    Quick ASR check for specific patterns.
    
    Instead of full re-transcription, uses targeted pattern matching
    to recover common missing elements (numbers, amounts, names).
    """
    
    # Patterns to check for in secondary ASR that might be missing
    RECOVERY_PATTERNS = {
        'amount': r'₹?\s*\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:रुपये?|rupees?|lakh|लाख|crore|करोड़)?',
        'phone': r'\d{10}|\d{5}\s*\d{5}',
        'consent': r'(?:सहमति|consent|agree|हाँ|yes|ठीक है|okay)',
        'terms': r'(?:terms?\s*(?:and\s*)?conditions?|नियम\s*(?:और\s*)?शर्तें)',
    }
    
    def __init__(self, secondary_asr: Optional[SecondaryASR] = None):
        """Initialize with optional secondary ASR."""
        self.secondary = secondary_asr
        import re
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE | re.UNICODE)
            for name, pattern in self.RECOVERY_PATTERNS.items()
        }
    
    async def quick_check(
        self,
        audio_path: Union[str, Path],
        start_time: float,
        end_time: float,
        expected_patterns: list[str],
        language: str = "hi",
    ) -> dict[str, list[str]]:
        """
        Quick check for specific patterns in audio segment.
        
        Args:
            audio_path: Path to audio
            start_time: Start time
            end_time: End time
            expected_patterns: List of pattern names to look for
            language: Language code
            
        Returns:
            Dict of pattern name -> found matches
        """
        if not self.secondary:
            return {}
        
        try:
            result = await self.secondary.transcribe_segment(
                audio_path, start_time, end_time, language
            )
            
            found = {}
            for pattern_name in expected_patterns:
                if pattern_name in self.compiled_patterns:
                    matches = self.compiled_patterns[pattern_name].findall(result.text)
                    if matches:
                        found[pattern_name] = matches
            
            return found
            
        except Exception as e:
            logger.warning(f"Quick check failed: {e}")
            return {}


class NeMoFastConformerASR(SecondaryASR):
    """
    Fast Hindi ASR using NVIDIA NeMo FastConformer.
    
    FastConformer is optimized for speed and works great with Hindi.
    Much faster than Whisper for Hindi transcription.
    
    Available models:
        - stt_hi_fastconformer_hybrid_large: Hindi FastConformer (best for Hindi)
        - stt_hi_conformer_ctc_large: Hindi Conformer CTC
        - nvidia/parakeet-tdt-0.6b-v2: Multilingual Parakeet (English-focused)
    
    Install:
        pip install nemo_toolkit[asr]
        
    Example:
        ```python
        asr = NeMoFastConformerASR(model_name="stt_hi_fastconformer_hybrid_large")
        result = await asr.transcribe("audio.wav")
        print(result.text)
        ```
    """
    
    # Available Hindi models
    HINDI_MODELS = {
        "fastconformer_hi": "stt_hi_fastconformer_hybrid_large",
        "conformer_hi": "stt_hi_conformer_ctc_large", 
        "parakeet": "nvidia/parakeet-tdt-0.6b-v2",
    }
    
    def __init__(
        self,
        model_name: str = "stt_hi_fastconformer_hybrid_large",
        device: str = "cpu",  # cpu or cuda
    ):
        """
        Initialize NeMo FastConformer ASR.
        
        Args:
            model_name: NeMo model name or alias (fastconformer_hi, conformer_hi, parakeet)
            device: Device to use (cpu or cuda)
        """
        # Resolve alias
        if model_name in self.HINDI_MODELS:
            model_name = self.HINDI_MODELS[model_name]
        
        self.model_name = model_name
        self.device = device
        self._model = None
        
        logger.info(f"NeMoFastConformerASR configured: model={model_name}, device={device}")
    
    def _get_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                import nemo.collections.asr as nemo_asr
                import torch
                
                logger.info(f"Loading NeMo model: {self.model_name}...")
                
                self._model = nemo_asr.models.ASRModel.from_pretrained(self.model_name)
                
                if self.device == "cuda" and torch.cuda.is_available():
                    self._model = self._model.cuda()
                
                self._model.eval()
                
                logger.info(f"Loaded NeMo {self.model_name} on {self.device}")
                
            except ImportError:
                raise ImportError(
                    "nemo_toolkit not installed. "
                    "Install with: pip install nemo_toolkit[asr]"
                )
        return self._model
    
    async def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "hi",
    ) -> ASRResult:
        """
        Transcribe audio file using NeMo FastConformer.
        
        Args:
            audio_path: Path to audio file
            language: Language code (ignored for Hindi-specific models)
            
        Returns:
            ASRResult with transcription
        """
        model = self._get_model()
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._transcribe_sync(str(audio_path)),
        )
        
        return result
    
    def _transcribe_sync(self, audio_path: str) -> ASRResult:
        """Synchronous transcription."""
        model = self._get_model()
        
        # Transcribe with timestamps
        hypotheses = model.transcribe([audio_path], timestamps=True)
        
        if not hypotheses:
            return ASRResult(text="", segments=[], language="hi", confidence=0.0)
        
        hyp = hypotheses[0]
        text = hyp.text if hasattr(hyp, 'text') else str(hyp)
        
        # Extract segments if available
        segments = []
        if hasattr(hyp, 'timestamp') and hyp.timestamp:
            if 'segment' in hyp.timestamp:
                for seg in hyp.timestamp['segment']:
                    segments.append({
                        'start': seg.get('start', 0),
                        'end': seg.get('end', 0),
                        'text': seg.get('segment', ''),
                    })
        
        return ASRResult(
            text=text,
            segments=segments,
            language="hi",
            confidence=1.0,  # NeMo doesn't provide confidence scores
        )
    
    async def transcribe_segment(
        self,
        audio_path: Union[str, Path],
        start_time: float,
        end_time: float,
        language: str = "hi",
    ) -> ASRResult:
        """
        Transcribe a specific segment of audio.
        
        Args:
            audio_path: Path to audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            language: Language code
            
        Returns:
            ASRResult for the segment
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(str(audio_path))
            segment = audio[int(start_time * 1000):int(end_time * 1000)]
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
                segment.export(temp_path, format='wav')
            
            try:
                result = await self.transcribe(temp_path, language)
            finally:
                Path(temp_path).unlink(missing_ok=True)
            
            return result
            
        except ImportError:
            raise ImportError("pydub not installed. Install with: pip install pydub")


def get_secondary_asr(
    backend: str = "auto",
    model: str = "auto",
    device: str = "auto",
    **kwargs,
) -> SecondaryASR:
    """
    Factory function to get the best available secondary ASR.
    
    Args:
        backend: ASR backend - "nemo", "faster-whisper", or "auto"
        model: Model name or "auto" for default
        device: Device - "cpu", "cuda", or "auto"
        **kwargs: Additional arguments for the ASR
        
    Returns:
        SecondaryASR instance
        
    Example:
        ```python
        # Auto-select best available
        asr = get_secondary_asr()
        
        # Force NeMo FastConformer
        asr = get_secondary_asr(backend="nemo")
        
        # Force Faster-Whisper
        asr = get_secondary_asr(backend="faster-whisper", model="distil-large-v3")
        ```
    """
    import torch
    
    # Auto-detect device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Auto-detect backend
    if backend == "auto":
        # Try NeMo first (faster for Hindi)
        try:
            import nemo.collections.asr
            backend = "nemo"
            logger.info("Using NeMo backend (faster for Hindi)")
        except ImportError:
            # Fall back to Faster-Whisper
            try:
                import faster_whisper
                backend = "faster-whisper"
                logger.info("Using Faster-Whisper backend")
            except ImportError:
                raise ImportError(
                    "No ASR backend available. Install one of:\n"
                    "  pip install nemo_toolkit[asr]  # For NeMo (faster for Hindi)\n"
                    "  pip install faster-whisper     # For Faster-Whisper"
                )
    
    if backend == "nemo":
        if model == "auto":
            model = "stt_hi_fastconformer_hybrid_large"
        return NeMoFastConformerASR(model_name=model, device=device)
    
    elif backend == "faster-whisper":
        if model == "auto":
            model = "distil-large-v3"
        compute = "float16" if device == "cuda" else "int8"
        return FasterWhisperASR(
            model_size=model,
            device=device,
            compute_type=compute,
            **kwargs,
        )
    
    else:
        raise ValueError(f"Unknown backend: {backend}. Use 'nemo' or 'faster-whisper'")
