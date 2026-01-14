"""
Detector Tests
==============

Unit tests for error detection modules.
"""

import pytest
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MockWordToken:
    """Mock WordToken for testing."""
    word: str
    start_time: float
    end_time: float
    confidence: float
    is_corrected: bool = False
    correction_source: Optional[str] = None
    alternatives: list = field(default_factory=list)


class TestConfidenceDetector:
    """Tests for ConfidenceDetector."""

    def test_detect_low_confidence_spans(self):
        """Test detection of low-confidence spans."""
        from asr_enhancer.detectors.confidence_detector import ConfidenceDetector

        detector = ConfidenceDetector(threshold=0.7)

        tokens = [
            MockWordToken("hello", 0.0, 0.5, 0.9),
            MockWordToken("world", 0.5, 1.0, 0.4),  # Low confidence
            MockWordToken("test", 1.0, 1.5, 0.3),   # Low confidence
            MockWordToken("good", 1.5, 2.0, 0.85),
        ]

        spans = detector.detect(tokens)

        assert len(spans) == 1
        assert spans[0]["start_idx"] == 1
        assert spans[0]["end_idx"] == 2
        assert len(spans[0]["words"]) == 2

    def test_no_low_confidence(self):
        """Test when all words have high confidence."""
        from asr_enhancer.detectors.confidence_detector import ConfidenceDetector

        detector = ConfidenceDetector(threshold=0.7)

        tokens = [
            MockWordToken("hello", 0.0, 0.5, 0.9),
            MockWordToken("world", 0.5, 1.0, 0.85),
        ]

        spans = detector.detect(tokens)
        assert len(spans) == 0

    def test_confidence_stats(self):
        """Test confidence statistics calculation."""
        from asr_enhancer.detectors.confidence_detector import ConfidenceDetector

        detector = ConfidenceDetector()

        tokens = [
            MockWordToken("a", 0.0, 0.1, 0.8),
            MockWordToken("b", 0.1, 0.2, 0.6),
            MockWordToken("c", 0.2, 0.3, 1.0),
        ]

        stats = detector.get_confidence_stats(tokens)

        assert stats["mean"] == pytest.approx(0.8, rel=0.01)
        assert stats["min"] == 0.6
        assert stats["max"] == 1.0


class TestAnomalyDetector:
    """Tests for AnomalyDetector."""

    def test_detect_repetitions(self):
        """Test detection of repeated words."""
        from asr_enhancer.detectors.anomaly_detector import AnomalyDetector

        detector = AnomalyDetector(repetition_threshold=3)

        tokens = [
            MockWordToken("the", 0.0, 0.1, 0.9),
            MockWordToken("the", 0.1, 0.2, 0.9),
            MockWordToken("the", 0.2, 0.3, 0.9),
            MockWordToken("the", 0.3, 0.4, 0.9),
            MockWordToken("cat", 0.4, 0.5, 0.9),
        ]

        anomalies = detector.detect(tokens)

        repetition_anomalies = [a for a in anomalies if a["type"] == "repeated_word"]
        assert len(repetition_anomalies) == 1
        assert repetition_anomalies[0]["repetition_count"] == 4

    def test_detect_segmentation_breaks(self):
        """Test detection of timing gaps."""
        from asr_enhancer.detectors.anomaly_detector import AnomalyDetector

        detector = AnomalyDetector(max_gap_seconds=1.0)

        tokens = [
            MockWordToken("hello", 0.0, 0.5, 0.9),
            MockWordToken("world", 3.0, 3.5, 0.9),  # 2.5s gap
        ]

        anomalies = detector.detect(tokens)

        breaks = [a for a in anomalies if a["type"] == "segmentation_break"]
        assert len(breaks) == 1
        assert breaks[0]["gap_seconds"] == pytest.approx(2.5, rel=0.01)


class TestNumericGapDetector:
    """Tests for NumericGapDetector."""

    def test_detect_incomplete_phone(self):
        """Test detection of incomplete phone number."""
        from asr_enhancer.detectors.numeric_gap_detector import NumericGapDetector

        detector = NumericGapDetector()

        tokens = [
            MockWordToken("phone", 0.0, 0.3, 0.9),
            MockWordToken("number", 0.3, 0.6, 0.9),
            MockWordToken("is", 0.6, 0.7, 0.9),
            MockWordToken("nine", 0.7, 0.9, 0.7),
            MockWordToken("one", 0.9, 1.1, 0.5),
            MockWordToken("two", 1.1, 1.3, 0.6),
        ]

        gaps = detector.detect(tokens)

        # Should detect incomplete phone number
        assert any(g["gap_type"] == "phone" for g in gaps)

    def test_detect_otp_context(self):
        """Test detection of OTP from context."""
        from asr_enhancer.detectors.numeric_gap_detector import NumericGapDetector

        detector = NumericGapDetector()

        tokens = [
            MockWordToken("otp", 0.0, 0.2, 0.9),
            MockWordToken("is", 0.2, 0.3, 0.9),
            MockWordToken("1", 0.3, 0.4, 0.8),
            MockWordToken("2", 0.4, 0.5, 0.7),
            MockWordToken("3", 0.5, 0.6, 0.6),
        ]

        gaps = detector.detect(tokens)

        # May detect incomplete OTP
        otp_gaps = [g for g in gaps if g["gap_type"] == "otp"]
        # Low confidence should trigger gap detection


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
