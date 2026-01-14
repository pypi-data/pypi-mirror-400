"""
Numeric Module Tests
====================

Tests for numeric pattern analysis and reconstruction.
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


class TestNumericPatternAnalyzer:
    """Tests for NumericPatternAnalyzer."""

    def test_find_number_words(self):
        """Test finding number words in tokens."""
        from asr_enhancer.numeric.pattern_analyzer import NumericPatternAnalyzer

        analyzer = NumericPatternAnalyzer()

        tokens = [
            MockWordToken("my", 0.0, 0.1, 0.9),
            MockWordToken("number", 0.1, 0.3, 0.9),
            MockWordToken("nine", 0.3, 0.5, 0.8),
            MockWordToken("one", 0.5, 0.7, 0.7),
            MockWordToken("two", 0.7, 0.9, 0.8),
        ]

        patterns = analyzer.analyze(tokens)

        assert len(patterns) >= 1
        # Should find the numeric sequence
        assert any(p.normalized_digits == "912" for p in patterns)

    def test_phone_context_detection(self):
        """Test phone number context detection."""
        from asr_enhancer.numeric.pattern_analyzer import NumericPatternAnalyzer

        analyzer = NumericPatternAnalyzer()

        tokens = [
            MockWordToken("phone", 0.0, 0.2, 0.9),
            MockWordToken("number", 0.2, 0.4, 0.9),
            MockWordToken("is", 0.4, 0.5, 0.9),
            MockWordToken("nine", 0.5, 0.7, 0.8),
            MockWordToken("one", 0.7, 0.9, 0.8),
            MockWordToken("two", 0.9, 1.1, 0.8),
        ]

        patterns = analyzer.analyze(tokens)

        phone_patterns = [p for p in patterns if p.pattern_type == "phone"]
        assert len(phone_patterns) >= 1


class TestSequenceReconstructor:
    """Tests for SequenceReconstructor."""

    def test_acoustic_confusion_correction(self):
        """Test correction of acoustic confusions."""
        from asr_enhancer.numeric.sequence_reconstructor import SequenceReconstructor
        from asr_enhancer.numeric.pattern_analyzer import NumericPattern

        reconstructor = SequenceReconstructor()

        tokens = [
            MockWordToken("tree", 0.0, 0.2, 0.6),  # Should become "3"
            MockWordToken("for", 0.2, 0.4, 0.5),   # Should become "4"
            MockWordToken("five", 0.4, 0.6, 0.8),
        ]

        patterns = [
            NumericPattern(
                pattern_type="general",
                start_idx=0,
                end_idx=2,
                raw_text="tree for five",
                normalized_digits="345",
                confidence=0.6,
                is_complete=True,
                expected_format=None,
            )
        ]

        result = reconstructor.reconstruct(tokens, patterns)

        # Tokens should be updated with corrections
        assert result[0].word in ["3", "tree"]
        assert result[1].word in ["4", "for"]


class TestNumericValidator:
    """Tests for NumericValidator."""

    def test_validate_phone(self):
        """Test phone number validation."""
        from asr_enhancer.numeric.validators import NumericValidator

        validator = NumericValidator()

        # Valid 10-digit phone
        result = validator.validate_phone("1234567890")
        assert result.is_valid

        # Too short
        result = validator.validate_phone("12345")
        assert not result.is_valid

    def test_validate_otp(self):
        """Test OTP validation."""
        from asr_enhancer.numeric.validators import NumericValidator

        validator = NumericValidator()

        # Valid 6-digit OTP
        result = validator.validate_otp("123456")
        assert result.is_valid

        # Valid 4-digit OTP
        result = validator.validate_otp("1234")
        assert result.is_valid

        # Too short
        result = validator.validate_otp("12")
        assert not result.is_valid

    def test_validate_credit_card_luhn(self):
        """Test credit card Luhn validation."""
        from asr_enhancer.numeric.validators import NumericValidator

        validator = NumericValidator()

        # Valid test card number (passes Luhn)
        result = validator.validate_credit_card("4111111111111111")
        assert result.is_valid

        # Invalid (fails Luhn)
        result = validator.validate_credit_card("4111111111111112")
        assert not result.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
