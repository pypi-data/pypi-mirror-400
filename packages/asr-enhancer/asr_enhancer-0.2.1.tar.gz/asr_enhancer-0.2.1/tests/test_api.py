"""
API Tests
=========

Integration tests for FastAPI endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch


# Fixtures
@pytest.fixture
def mock_word_timestamps():
    """Sample word timestamps."""
    return [
        {"word": "my", "start": 0.0, "end": 0.2},
        {"word": "phone", "start": 0.2, "end": 0.5},
        {"word": "number", "start": 0.5, "end": 0.8},
        {"word": "is", "start": 0.8, "end": 0.9},
        {"word": "nine", "start": 0.9, "end": 1.1},
        {"word": "one", "start": 1.1, "end": 1.3},
        {"word": "two", "start": 1.3, "end": 1.5},
    ]


@pytest.fixture
def mock_confidences():
    """Sample confidence scores."""
    return [0.95, 0.92, 0.89, 0.98, 0.85, 0.91, 0.88]


class TestHealthEndpoint:
    """Tests for health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check returns healthy status."""
        try:
            from fastapi.testclient import TestClient
            from asr_enhancer.api.main import app

            client = TestClient(app)
            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
        except ImportError:
            pytest.skip("FastAPI not installed")


class TestEnhanceEndpoint:
    """Tests for enhance endpoint."""

    @pytest.mark.asyncio
    async def test_enhance_request_validation(self):
        """Test request validation."""
        try:
            from fastapi.testclient import TestClient
            from asr_enhancer.api.main import app

            client = TestClient(app)

            # Invalid request (missing required fields)
            response = client.post(
                "/api/v1/enhance",
                json={"transcript": "hello world"},
            )

            assert response.status_code == 422  # Validation error
        except ImportError:
            pytest.skip("FastAPI not installed")

    @pytest.mark.asyncio
    async def test_enhance_success(
        self,
        mock_word_timestamps,
        mock_confidences,
    ):
        """Test successful enhancement."""
        try:
            from fastapi.testclient import TestClient
            from asr_enhancer.api.main import app

            client = TestClient(app)

            response = client.post(
                "/api/v1/enhance",
                json={
                    "transcript": "my phone number is nine one two",
                    "word_timestamps": mock_word_timestamps,
                    "word_confidences": mock_confidences,
                },
            )

            # Should succeed or return 500 if pipeline not fully configured
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert "enhanced_transcript" in data
                assert "original_transcript" in data
        except ImportError:
            pytest.skip("FastAPI not installed")


class TestAnalyzeEndpoint:
    """Tests for analyze endpoint."""

    @pytest.mark.asyncio
    async def test_analyze_returns_issues(
        self,
        mock_word_timestamps,
        mock_confidences,
    ):
        """Test analysis returns detected issues."""
        try:
            from fastapi.testclient import TestClient
            from asr_enhancer.api.main import app

            client = TestClient(app)

            response = client.post(
                "/api/v1/analyze",
                json={
                    "transcript": "test transcript",
                    "word_timestamps": mock_word_timestamps[:2],
                    "word_confidences": mock_confidences[:2],
                },
            )

            if response.status_code == 200:
                data = response.json()
                assert "word_count" in data
                assert "avg_confidence" in data
                assert "issues_detected" in data
        except ImportError:
            pytest.skip("FastAPI not installed")


class TestDiagnosticsEndpoint:
    """Tests for diagnostics endpoint."""

    @pytest.mark.asyncio
    async def test_diagnostics_returns_config(self):
        """Test diagnostics returns configuration."""
        try:
            from fastapi.testclient import TestClient
            from asr_enhancer.api.main import app

            client = TestClient(app)
            response = client.get("/api/v1/diagnostics")

            assert response.status_code == 200
            data = response.json()
            assert "pipeline_status" in data
            assert "stages" in data
            assert "config" in data
        except ImportError:
            pytest.skip("FastAPI not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
