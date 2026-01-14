"""
Audio Utilities
===============

Audio processing utilities for the ASR Enhancement Layer.
"""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

try:
    import librosa
    import numpy as np

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf

    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


class AudioUtils:
    """
    Audio processing utilities.

    Provides:
        - Audio loading and saving
        - Resampling
        - Normalization
        - Segment extraction
        - Format conversion
    """

    DEFAULT_SAMPLE_RATE = 16000

    @classmethod
    def load(
        cls,
        path: str,
        sample_rate: Optional[int] = None,
        mono: bool = True,
    ) -> Tuple[any, int]:
        """
        Load audio from file.

        Args:
            path: Path to audio file
            sample_rate: Target sample rate (None = original)
            mono: Convert to mono

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        sr = sample_rate or cls.DEFAULT_SAMPLE_RATE

        if LIBROSA_AVAILABLE:
            audio, actual_sr = librosa.load(path, sr=sr, mono=mono)
            return audio, actual_sr
        elif SOUNDFILE_AVAILABLE:
            audio, actual_sr = sf.read(path)
            if mono and len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            if sample_rate and actual_sr != sample_rate:
                # Basic resampling (not as good as librosa)
                ratio = sample_rate / actual_sr
                new_length = int(len(audio) * ratio)
                indices = (np.arange(new_length) / ratio).astype(int)
                audio = audio[indices]
                actual_sr = sample_rate
            return audio, actual_sr
        else:
            raise RuntimeError("No audio library available. Install librosa or soundfile.")

    @classmethod
    def save(
        cls,
        audio: any,
        path: str,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ) -> None:
        """
        Save audio to file.

        Args:
            audio: Audio data (numpy array)
            path: Output path
            sample_rate: Sample rate
        """
        if SOUNDFILE_AVAILABLE:
            sf.write(path, audio, sample_rate)
        else:
            raise RuntimeError("soundfile is required for saving audio")

    @classmethod
    def get_duration(cls, path: str) -> float:
        """
        Get audio duration in seconds.

        Args:
            path: Path to audio file

        Returns:
            Duration in seconds
        """
        if LIBROSA_AVAILABLE:
            return librosa.get_duration(path=path)
        elif SOUNDFILE_AVAILABLE:
            info = sf.info(path)
            return info.duration
        else:
            raise RuntimeError("No audio library available")

    @classmethod
    def extract_segment(
        cls,
        path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[str] = None,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ) -> str:
        """
        Extract audio segment.

        Args:
            path: Source audio path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output path (generates temp file if None)
            sample_rate: Target sample rate

        Returns:
            Path to extracted segment
        """
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

        duration = end_time - start_time

        if LIBROSA_AVAILABLE:
            audio, sr = librosa.load(
                path,
                sr=sample_rate,
                offset=start_time,
                duration=duration,
            )
            sf.write(output_path, audio, sample_rate)
        else:
            # Fallback to ffmpeg
            import subprocess

            cmd = [
                "ffmpeg", "-y",
                "-i", path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-ar", str(sample_rate),
                "-ac", "1",
                output_path,
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        return output_path

    @classmethod
    def normalize(
        cls,
        audio: any,
        target_db: float = -20.0,
    ) -> any:
        """
        Normalize audio to target dB level.

        Args:
            audio: Audio data
            target_db: Target dB level

        Returns:
            Normalized audio
        """
        if not LIBROSA_AVAILABLE:
            # Simple peak normalization
            peak = np.max(np.abs(audio))
            if peak > 0:
                return audio / peak * 0.9
            return audio

        # RMS normalization
        rms = np.sqrt(np.mean(audio ** 2))
        if rms > 0:
            target_rms = 10 ** (target_db / 20)
            audio = audio * (target_rms / rms)

        # Prevent clipping
        peak = np.max(np.abs(audio))
        if peak > 1.0:
            audio = audio / peak * 0.99

        return audio

    @classmethod
    def resample(
        cls,
        audio: any,
        orig_sr: int,
        target_sr: int,
    ) -> any:
        """
        Resample audio to target sample rate.

        Args:
            audio: Audio data
            orig_sr: Original sample rate
            target_sr: Target sample rate

        Returns:
            Resampled audio
        """
        if orig_sr == target_sr:
            return audio

        if LIBROSA_AVAILABLE:
            return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
        else:
            # Basic resampling
            ratio = target_sr / orig_sr
            new_length = int(len(audio) * ratio)
            indices = (np.arange(new_length) / ratio).astype(int)
            return audio[indices]

    @classmethod
    def to_mono(cls, audio: any) -> any:
        """
        Convert stereo audio to mono.

        Args:
            audio: Audio data (may be stereo)

        Returns:
            Mono audio
        """
        if len(audio.shape) == 1:
            return audio
        return audio.mean(axis=1 if audio.shape[1] == 2 else 0)
