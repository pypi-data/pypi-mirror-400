"""
Segment Extractor
=================

Extracts audio segments for re-ASR processing.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

try:
    import librosa
    import soundfile as sf

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class SegmentExtractor:
    """
    Extracts audio segments based on timestamps.

    Supports slicing audio using librosa or falling back to ffmpeg.

    Attributes:
        sample_rate: Target sample rate for extracted segments
        padding_seconds: Padding to add around segment boundaries
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        padding_seconds: float = 0.1,
        temp_dir: Optional[str] = None,
    ):
        """
        Initialize the segment extractor.

        Args:
            sample_rate: Target sample rate (default 16000)
            padding_seconds: Padding around segments (default 0.1s)
            temp_dir: Directory for temporary files
        """
        self.sample_rate = sample_rate
        self.padding_seconds = padding_seconds
        self.temp_dir = temp_dir or tempfile.gettempdir()

    def extract(
        self,
        audio_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Extract audio segment from file.

        Args:
            audio_path: Path to source audio file
            start_time: Segment start time in seconds
            end_time: Segment end time in seconds
            output_path: Optional output path (generates temp file if None)

        Returns:
            Path to extracted audio segment

        Raises:
            RuntimeError: If extraction fails
        """
        # Apply padding
        padded_start = max(0, start_time - self.padding_seconds)
        padded_end = end_time + self.padding_seconds

        if output_path is None:
            output_path = str(
                Path(self.temp_dir) / f"segment_{padded_start:.3f}_{padded_end:.3f}.wav"
            )

        if LIBROSA_AVAILABLE:
            return self._extract_with_librosa(
                audio_path, padded_start, padded_end, output_path
            )
        else:
            return self._extract_with_ffmpeg(
                audio_path, padded_start, padded_end, output_path
            )

    def _extract_with_librosa(
        self,
        audio_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> str:
        """Extract segment using librosa."""
        # Load audio with offset and duration
        duration = end_time - start_time
        audio, sr = librosa.load(
            audio_path,
            sr=self.sample_rate,
            offset=start_time,
            duration=duration,
        )

        # Save segment
        sf.write(output_path, audio, self.sample_rate)
        return output_path

    def _extract_with_ffmpeg(
        self,
        audio_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> str:
        """Extract segment using ffmpeg subprocess."""
        import subprocess

        duration = end_time - start_time
        cmd = [
            "ffmpeg",
            "-y",
            "-i", audio_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-ar", str(self.sample_rate),
            "-ac", "1",
            "-acodec", "pcm_s16le",
            output_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg extraction failed: {result.stderr}")

        return output_path

    def extract_multiple(
        self,
        audio_path: str,
        segments: list[tuple[float, float]],
    ) -> list[str]:
        """
        Extract multiple segments from audio file.

        Args:
            audio_path: Path to source audio
            segments: List of (start_time, end_time) tuples

        Returns:
            List of paths to extracted segments
        """
        return [
            self.extract(audio_path, start, end)
            for start, end in segments
        ]
