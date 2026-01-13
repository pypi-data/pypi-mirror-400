"""
Tests for AI Assess Tech SDK asynchronous client.
"""

import pytest
from pytest_httpx import HTTPXMock

from aiassess import AsyncAIAssessClient
from aiassess.exceptions import (
    AuthenticationError,
    ValidationError,
    AssessmentError,
)
from aiassess.types import AssessProgress


@pytest.fixture
def async_simple_callback():
    """Async callback that always returns 'A'."""

    async def callback(question: str) -> str:
        return "A"

    return callback


class TestAsyncClientInitialization:
    """Tests for AsyncAIAssessClient initialization."""

    def test_valid_key(self, valid_health_check_key):
        """Test async client creation with valid key."""
        client = AsyncAIAssessClient(health_check_key=valid_health_check_key)
        assert client._health_check_key == valid_health_check_key

    def test_invalid_key_format(self):
        """Test that invalid key format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            AsyncAIAssessClient(health_check_key="invalid_key")
        assert "hck_" in str(exc_info.value)


class TestAsyncGetConfig:
    """Tests for async getting configuration."""

    @pytest.mark.asyncio
    async def test_fetch_config(
        self, httpx_mock: HTTPXMock, valid_health_check_key, mock_config_response
    ):
        """Test fetching server configuration asynchronously."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            config = await client.get_config()

        assert config.framework_id == "morality"
        assert len(config.questions) == 2

    @pytest.mark.asyncio
    async def test_config_caching(
        self, httpx_mock: HTTPXMock, valid_health_check_key, mock_config_response
    ):
        """Test that config is cached."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            config1 = await client.get_config()
            config2 = await client.get_config()

        # Should only make one request
        assert len(httpx_mock.get_requests()) == 1
        assert config1 is config2


class TestAsyncAssessment:
    """Tests for running async assessments."""

    @pytest.mark.asyncio
    async def test_successful_assessment(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        mock_assess_response,
        async_simple_callback,
    ):
        """Test successful async assessment flow."""
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

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            result = await client.assess(callback=async_simple_callback)

        assert result.overall_passed is True
        assert result.classification == "Well Adjusted"

    @pytest.mark.asyncio
    async def test_dry_run_mode(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        async_simple_callback,
    ):
        """Test async dry run mode."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            result = await client.assess(callback=async_simple_callback, dry_run=True)

        assert result.run_id.startswith("dryrun_")
        assert result.overall_passed is True

    @pytest.mark.asyncio
    async def test_progress_callback(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        async_simple_callback,
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

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            await client.assess(
                callback=async_simple_callback,
                on_progress=on_progress,
                dry_run=True,
            )

        assert len(progress_updates) == 2
        assert progress_updates[0].current == 1
        assert progress_updates[1].percentage == 100


class TestAsyncErrorHandling:
    """Tests for async error handling."""

    @pytest.mark.asyncio
    async def test_authentication_error(
        self, httpx_mock: HTTPXMock, valid_health_check_key
    ):
        """Test 401 response raises AuthenticationError."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            status_code=401,
            json={"error": "Invalid API key"},
        )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            with pytest.raises(AuthenticationError):
                await client.get_config()


class TestAsyncBlockUntilPass:
    """Tests for async block_until_pass functionality."""

    @pytest.mark.asyncio
    async def test_passes_immediately(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        mock_assess_response,
        async_simple_callback,
    ):
        """Test async block_until_pass when assessment passes immediately."""
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

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            result = await client.block_until_pass(
                callback=async_simple_callback,
                max_retries=3,
            )

        assert result.overall_passed is True

    @pytest.mark.asyncio
    async def test_fails_after_retries(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_config_response,
        mock_failed_assess_response,
        async_simple_callback,
    ):
        """Test async block_until_pass fails after max retries."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )
        for _ in range(3):
            httpx_mock.add_response(
                method="POST",
                url="https://www.aiassesstech.com/api/sdk/assess",
                json=mock_failed_assess_response,
            )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            with pytest.raises(AssessmentError) as exc_info:
                await client.block_until_pass(
                    callback=async_simple_callback,
                    max_retries=3,
                    retry_delay_seconds=0.1,
                )

        assert "3 attempts" in str(exc_info.value)


class TestAsyncVerify:
    """Tests for async verification."""

    @pytest.mark.asyncio
    async def test_verify_run(
        self,
        httpx_mock: HTTPXMock,
        valid_health_check_key,
        mock_verify_response,
    ):
        """Test async verification endpoint."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/health-check/verify/test_run_123",
            json=mock_verify_response,
        )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            result = await client.verify("test_run_123")

        assert result["valid"] is True
        assert result["hashMatch"] is True


class TestAsyncContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager(
        self, httpx_mock: HTTPXMock, valid_health_check_key, mock_config_response
    ):
        """Test async context manager."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        async with AsyncAIAssessClient(
            health_check_key=valid_health_check_key
        ) as client:
            assert client is not None
            config = await client.get_config()
            assert config is not None

