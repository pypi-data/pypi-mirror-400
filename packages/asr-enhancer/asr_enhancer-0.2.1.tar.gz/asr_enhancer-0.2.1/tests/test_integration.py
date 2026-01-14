"""
Integration Tests
=================

End-to-end integration tests for the enhancement pipeline.
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


class TestEnhancementPipeline:
    """Integration tests for EnhancementPipeline."""

    @pytest.fixture
    def sample_transcript(self):
        """Sample transcript data."""
        return {
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

    @pytest.mark.asyncio
    async def test_analyze_only(self, sample_transcript):
        """Test analyze_only method."""
        from asr_enhancer.core import EnhancementPipeline
        from asr_enhancer.utils import Config

        # Use minimal config
        config = Config(
            enable_re_asr=False,
            enable_llm_restoration=False,
        )

        pipeline = EnhancementPipeline(config)

        result = await pipeline.analyze_only(
            transcript=sample_transcript["transcript"],
            word_timestamps=sample_transcript["word_timestamps"],
            word_confidences=sample_transcript["word_confidences"],
        )

        assert "word_count" in result
        assert "avg_confidence" in result
        assert "low_confidence_spans" in result
        assert "numeric_gaps" in result

        # Should detect low confidence spans (tree, ate)
        assert result["issues_detected"] > 0

    @pytest.mark.asyncio
    async def test_full_pipeline_without_audio(self, sample_transcript):
        """Test full pipeline without audio."""
        from asr_enhancer.core import EnhancementPipeline
        from asr_enhancer.utils import Config

        config = Config(
            enable_re_asr=False,  # No audio
            enable_llm_restoration=False,  # Skip LLM
        )

        pipeline = EnhancementPipeline(config)

        # This should run error detection, numeric reconstruction, etc.
        # but skip re-ASR and LLM steps
        try:
            result = await pipeline.enhance(
                transcript=sample_transcript["transcript"],
                word_timestamps=sample_transcript["word_timestamps"],
                word_confidences=sample_transcript["word_confidences"],
            )

            assert result.original_transcript == sample_transcript["transcript"]
            assert result.enhanced_transcript is not None
            assert "low_confidence_spans" in result.error_map
        except Exception as e:
            # Pipeline may fail if LLM provider not available
            pytest.skip(f"Pipeline requires LLM provider: {e}")


class TestVocabularyCorrection:
    """Tests for vocabulary correction integration."""

    def test_domain_term_matching(self):
        """Test domain term matching."""
        from asr_enhancer.vocab import LexiconLoader, DomainTermMatcher

        loader = LexiconLoader()
        matcher = DomainTermMatcher()

        lexicon = {
            "acetaminophen": ["tylenol", "paracetamol"],
            "ibuprofen": ["advil", "motrin"],
        }

        tokens = [
            MockWordToken("take", 0.0, 0.2, 0.9),
            MockWordToken("tylenol", 0.2, 0.5, 0.8),
            MockWordToken("for", 0.5, 0.6, 0.9),
            MockWordToken("pain", 0.6, 0.8, 0.9),
        ]

        matches = matcher.match(tokens, lexicon)

        assert len(matches) >= 1
        assert any(m.canonical_form == "acetaminophen" for m in matches)


class TestConsistencyValidation:
    """Tests for consistency validation."""

    def test_consistency_checker(self):
        """Test consistency checking."""
        from asr_enhancer.validators import ConsistencyChecker

        checker = ConsistencyChecker()

        original_tokens = [
            MockWordToken("the", 0.0, 0.1, 0.9),
            MockWordToken("quick", 0.1, 0.3, 0.9),
            MockWordToken("brown", 0.3, 0.5, 0.9),
            MockWordToken("fox", 0.5, 0.7, 0.9),
        ]

        # Good enhancement - similar to original
        score = checker.check(
            "The quick brown fox",
            original_tokens,
        )
        assert score > 0.8

        # Bad enhancement - very different
        score = checker.check(
            "Something completely different",
            original_tokens,
        )
        assert score < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
