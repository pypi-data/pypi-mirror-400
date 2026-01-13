"""
Tests for AI Assess Tech SDK synchronous client.
"""

import pytest
from pytest_httpx import HTTPXMock

from aiassess import AIAssessClient
from aiassess.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NetworkError,
    AssessmentError,
)
from aiassess.types import AssessProgress


class TestClientInitialization:
    """Tests for AIAssessClient initialization."""

    def test_valid_key(self, valid_health_check_key):
        """Test client creation with valid key."""
        client = AIAssessClient(health_check_key=valid_health_check_key)
        assert client._health_check_key == valid_health_check_key
        client.close()

    def test_invalid_key_format(self):
        """Test that invalid key format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            AIAssessClient(health_check_key="invalid_key")
        assert "hck_" in str(exc_info.value)

    def test_context_manager(self, valid_health_check_key):
        """Test client as context manager."""
        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            assert client is not None

    def test_custom_base_url(self, valid_health_check_key):
        """Test client with custom base URL."""
        client = AIAssessClient(
            health_check_key=valid_health_check_key,
            base_url="https://custom.api.com",
        )
        assert client._base_url == "https://custom.api.com"
        client.close()

    def test_custom_timeout(self, valid_health_check_key):
        """Test client with custom timeout."""
        client = AIAssessClient(
            health_check_key=valid_health_check_key,
            timeout=60.0,
            overall_timeout=600.0,
        )
        assert client._timeout == 60.0
        assert client._overall_timeout == 600.0
        client.close()


class TestGetConfig:
    """Tests for getting configuration."""

    def test_fetch_config(
        self, httpx_mock: HTTPXMock, valid_health_check_key, mock_config_response
    ):
        """Test fetching server configuration."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            config = client.get_config()

        assert config.framework_id == "morality"
        assert len(config.questions) == 2

    def test_config_caching(
        self, httpx_mock: HTTPXMock, valid_health_check_key, mock_config_response
    ):
        """Test that config is cached."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            config1 = client.get_config()
            config2 = client.get_config()

        # Should only make one request
        assert len(httpx_mock.get_requests()) == 1
        assert config1 is config2


class TestAssessment:
    """Tests for running assessments."""

    def test_successful_assessment(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        mock_assess_response,
        simple_ai_callback,
    ):
        """Test successful assessment flow."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )
        httpx_mock.add_response(
            method="POST",
            url="https://www.aiassesstech.com/api/sdk/assess",
            json=mock_assess_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            result = client.assess(callback=simple_ai_callback)

        assert result.overall_passed is True
        assert result.classification == "Well Adjusted"
        assert result.scores.lying == 8.0

    def test_dry_run_mode(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        simple_ai_callback,
    ):
        """Test dry run mode returns mock results."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            result = client.assess(callback=simple_ai_callback, dry_run=True)

        assert result.run_id.startswith("dryrun_")
        assert result.overall_passed is True
        # Should not have made assess call
        requests = httpx_mock.get_requests()
        assert len(requests) == 1  # Only config request
        assert "/api/sdk/assess" not in str(requests[0].url)

    def test_progress_callback(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        simple_ai_callback,
    ):
        """Test progress callback is called correctly."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        progress_updates = []

        def on_progress(p: AssessProgress):
            progress_updates.append(p)

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            client.assess(
                callback=simple_ai_callback,
                on_progress=on_progress,
                dry_run=True,
            )

        assert len(progress_updates) == 2  # 2 questions in mock config
        assert progress_updates[0].current == 1
        assert progress_updates[1].current == 2
        assert progress_updates[1].percentage == 100


class TestAnswerExtraction:
    """Tests for answer letter extraction."""

    @pytest.mark.parametrize(
        "response,expected",
        [
            ("A", "A"),
            ("B", "B"),
            ("a", "A"),
            ("b", "B"),
            ("The answer is A", "A"),
            ("I would choose B", "B"),
            ("C)", "C"),
            ("D.", "D"),
            ("Answer: A", "A"),
            ("My answer is B", "B"),
            ("I select C", "C"),
            ("D - correct answer", "D"),
            ("  A  ", "A"),
            ("Option B is best", "B"),
        ],
    )
    def test_extract_answer_letter(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        response,
        expected,
    ):
        """Test various answer formats are correctly extracted."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            client._get_config()  # Initialize
            extracted = client._extract_answer_letter(response)
            assert extracted == expected

    @pytest.mark.parametrize(
        "invalid_response",
        [
            "",
            "Yes",
            "No",
            "I agree",
            "Maybe",
            "12345",
            "EFGH",
        ],
    )
    def test_invalid_responses(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        invalid_response,
    ):
        """Test that invalid responses raise ValidationError."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            client._get_config()  # Initialize
            with pytest.raises(ValidationError):
                client._extract_answer_letter(invalid_response)


class TestErrorHandling:
    """Tests for error handling."""

    def test_authentication_error(
        self, httpx_mock: HTTPXMock, valid_health_check_key
    ):
        """Test 401 response raises AuthenticationError."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            status_code=401,
            json={"error": "Invalid API key"},
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            with pytest.raises(AuthenticationError):
                client.get_config()

    def test_rate_limit_error(
        self, httpx_mock: HTTPXMock, valid_health_check_key
    ):
        """Test 429 response raises RateLimitError."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            status_code=429,
            headers={"Retry-After": "120"},
            json={"error": "Rate limit exceeded"},
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            with pytest.raises(RateLimitError) as exc_info:
                client.get_config()
            assert exc_info.value.retry_after == 120


class TestQuestionFormatting:
    """Tests for question formatting."""

    def test_format_question(
        self, httpx_mock: HTTPXMock, valid_health_check_key, mock_config_response
    ):
        """Test question formatting."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            config = client.get_config()
            question = config.questions[0]
            formatted = client._format_question(question)

        assert "Test question about honesty" in formatted
        assert "A)" in formatted
        assert "Always tell the truth" in formatted
        assert "ONLY the letter" in formatted


class TestBlockUntilPass:
    """Tests for block_until_pass functionality."""

    def test_passes_immediately(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        mock_assess_response,
        simple_ai_callback,
    ):
        """Test block_until_pass when assessment passes immediately."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )
        httpx_mock.add_response(
            method="POST",
            url="https://www.aiassesstech.com/api/sdk/assess",
            json=mock_assess_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            result = client.block_until_pass(
                callback=simple_ai_callback,
                max_retries=3,
            )

        assert result.overall_passed is True

    def test_fails_after_retries(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        mock_failed_assess_response,
        simple_ai_callback,
    ):
        """Test block_until_pass fails after max retries."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )
        # All attempts fail
        for _ in range(3):
            httpx_mock.add_response(
                method="POST",
                url="https://www.aiassesstech.com/api/sdk/assess",
                json=mock_failed_assess_response,
            )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            with pytest.raises(AssessmentError) as exc_info:
                client.block_until_pass(
                    callback=simple_ai_callback,
                    max_retries=3,
                    retry_delay_seconds=0.1,  # Fast for testing
                )

        assert "3 attempts" in str(exc_info.value)


class TestVerify:
    """Tests for verification."""

    def test_verify_run(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_verify_response,
    ):
        """Test verification endpoint."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/health-check/verify/test_run_123",
            json=mock_verify_response,
        )

        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            result = client.verify("test_run_123")

        assert result["valid"] is True
        assert result["hashMatch"] is True


class TestEnvironmentDetection:
    """Tests for environment detection."""

    def test_detect_environment(self, valid_health_check_key):
        """Test environment detection."""
        with AIAssessClient(health_check_key=valid_health_check_key) as client:
            env = client._detect_environment()

        assert env.python_version is not None
        assert env.platform in ["linux", "darwin", "win32"]
        assert env.arch is not None

