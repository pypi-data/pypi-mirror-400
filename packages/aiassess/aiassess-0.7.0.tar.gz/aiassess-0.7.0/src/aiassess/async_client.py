"""
Asynchronous client for AI Assess Tech Python SDK.

Example:
    >>> from aiassess import AsyncAIAssessClient
    >>>
    >>> async def my_ai(question: str) -> str:
    ...     response = await openai.chat.completions.acreate(
    ...         model="gpt-4",
    ...         messages=[{"role": "user", "content": question}]
    ...     )
    ...     return response.choices[0].message.content or ""
    >>>
    >>> async with AsyncAIAssessClient(health_check_key="hck_...") as client:
    ...     result = await client.assess(callback=my_ai)
    ...     print(f"Passed: {result.overall_passed}")
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import platform
import re
import secrets
import sys
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional

import httpx

from aiassess._version import __version__
from aiassess.types import (
    AssessmentResult,
    AssessProgress,
    ClientEnvironment,
    DimensionPassed,
    DimensionScores,
    PrinciplePoints,
    Question,
    ServerConfig,
    VersionInfo,
)
from aiassess.exceptions import (
    AIAssessError,
    AssessmentError,
    AuthenticationError,
    NetworkError,
    OverallTimeoutError,
    QuestionTimeoutError,
    RateLimitError,
    ValidationError,
)

logger = logging.getLogger("aiassess")

DEFAULT_BASE_URL = "https://www.aiassesstech.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_OVERALL_TIMEOUT = 360.0
MAX_RESPONSE_LENGTH = 1000

# Type alias for async callback
AsyncAICallback = Callable[[str], Awaitable[str]]


class AsyncAIAssessClient:
    """
    Asynchronous client for AI Assess Tech ethical assessments.

    Identical to AIAssessClient but uses async/await for all operations.

    Args:
        health_check_key: Your Health Check Key (format: hck_...)
        base_url: API base URL (default: https://www.aiassesstech.com)
        timeout: Per-request timeout in seconds (default: 30)
        overall_timeout: Overall assessment timeout in seconds (default: 360)
        max_retries: Maximum retry attempts for transient errors (default: 3)

    Example:
        >>> async with AsyncAIAssessClient(health_check_key="hck_...") as client:
        ...     result = await client.assess(callback=my_async_ai_function)
    """

    def __init__(
        self,
        health_check_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        overall_timeout: float = DEFAULT_OVERALL_TIMEOUT,
        max_retries: int = 3,
    ) -> None:
        if not health_check_key.startswith("hck_"):
            raise ValidationError(
                'Health Check Key must start with "hck_"',
                field="health_check_key",
            )

        self._health_check_key = health_check_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._overall_timeout = overall_timeout
        self._max_retries = max_retries
        self._cached_config: Optional[ServerConfig] = None

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
            headers={
                "X-Health-Check-Key": health_check_key,
                "Content-Type": "application/json",
                "User-Agent": f"aiassess-python/{__version__}",
                "X-SDK-Version": __version__,
            },
        )

    async def assess(
        self,
        callback: AsyncAICallback,
        *,
        on_progress: Optional[Callable[[AssessProgress], None]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
    ) -> AssessmentResult:
        """
        Run an ethical assessment asynchronously.

        Args:
            callback: Async function that sends a question to your AI.
                      Signature: async (question: str) -> str
            on_progress: Optional callback for progress updates
            metadata: Optional metadata to store with the assessment
            dry_run: If True, only 5 questions and returns mock scores

        Returns:
            AssessmentResult with scores, pass/fail status, and verification URL
        """
        config = await self._get_config()

        sdk_session_id = f"sdk_{secrets.token_hex(6)}"
        start_time = time.time()

        questions = config.questions[:5] if dry_run else config.questions
        responses: List[Dict[str, Any]] = []

        logger.info(f"🚀 Starting assessment ({len(questions)} questions)...")

        for i, q in enumerate(questions):
            elapsed = time.time() - start_time
            if elapsed > self._overall_timeout:
                raise OverallTimeoutError(
                    f"Assessment exceeded overall timeout of {self._overall_timeout}s",
                    completed_questions=i,
                    timeout_ms=int(self._overall_timeout * 1000),
                )

            if on_progress:
                avg_per_question = elapsed / i if i > 0 else 2.0
                on_progress(
                    AssessProgress(
                        current=i + 1,
                        total=len(questions),
                        percentage=int((i + 1) / len(questions) * 100),
                        dimension=q.dimension,
                        question_id=q.id,
                        question_preview=q.text[:50],
                        elapsed_ms=int(elapsed * 1000),
                        estimated_remaining_ms=int(
                            avg_per_question * (len(questions) - i) * 1000
                        ),
                    )
                )

            question_start = time.time()
            try:
                formatted = self._format_question(q)
                response = await callback(formatted)
                answer_letter = self._extract_answer_letter(response)

                responses.append(
                    {
                        "questionId": q.id,
                        "response": response[:MAX_RESPONSE_LENGTH],
                        "answerLetter": answer_letter,
                        "durationMs": int((time.time() - question_start) * 1000),
                    }
                )
            except (QuestionTimeoutError, OverallTimeoutError):
                raise
            except Exception as e:
                raise AssessmentError(
                    f"Failed on question {i + 1}: {e}",
                    completed_questions=i,
                    failed_question_id=q.id,
                ) from e

        total_duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ All questions answered in {total_duration_ms / 1000:.1f}s")

        if dry_run:
            logger.info("🧪 Dry run mode - returning mock scores")
            return self._mock_result(sdk_session_id, config)

        logger.info("📤 Submitting responses for scoring...")
        result = await self._submit_responses(
            sdk_session_id=sdk_session_id,
            config=config,
            responses=responses,
            total_duration_ms=total_duration_ms,
            metadata=metadata,
        )

        status = "PASSED ✅" if result.overall_passed else "FAILED ❌"
        logger.info(f"📊 Result: {result.classification} ({status})")

        return result

    async def block_until_pass(
        self,
        callback: AsyncAICallback,
        *,
        max_retries: int = 3,
        retry_delay_seconds: float = 60.0,
        exit_on_failure: bool = False,
        on_progress: Optional[Callable[[AssessProgress], None]] = None,
        on_failure: Optional[Callable[[AssessmentResult, int], None]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssessmentResult:
        """Block until assessment passes (async version)."""
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Attempt {attempt}/{max_retries}...")

            result = await self.assess(
                callback=callback,
                on_progress=on_progress,
                metadata=metadata,
            )

            if result.overall_passed:
                logger.info(f"✅ AI passed on attempt {attempt}")
                return result

            if on_failure:
                on_failure(result, attempt)

            if attempt == max_retries:
                if exit_on_failure:
                    logger.error(
                        f"❌ AI failed ethical assessment after {max_retries} attempts"
                    )
                    sys.exit(1)
                raise AssessmentError(
                    f"AI failed ethical assessment after {max_retries} attempts",
                    details={"last_result": result.model_dump()},
                )

            logger.info(
                f"⏳ Attempt {attempt} failed, retrying in {retry_delay_seconds}s..."
            )
            await asyncio.sleep(retry_delay_seconds)

        raise AssertionError("Unexpected: should not reach here")

    async def get_config(self) -> ServerConfig:
        """Get the current server configuration."""
        return await self._get_config()

    async def verify(self, run_id: str) -> Dict[str, Any]:
        """Verify the cryptographic integrity of an assessment result."""
        return await self._request("GET", f"/api/health-check/verify/{run_id}")

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncAIAssessClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # Private methods

    async def _get_config(self) -> ServerConfig:
        if self._cached_config is not None:
            return self._cached_config

        response = await self._request("GET", "/api/sdk/config")
        self._cached_config = ServerConfig.model_validate(response)

        logger.info(
            f"📋 Config loaded: {len(self._cached_config.questions)} questions, "
            f"framework: {self._cached_config.framework_id}"
        )

        return self._cached_config

    def _format_question(self, q: Question) -> str:
        """Format a question for the AI."""
        return f"""Please answer the following question by selecting A, B, C, or D.

Question: {q.text}

A) {q.answers[0].text}
B) {q.answers[1].text}
C) {q.answers[2].text}
D) {q.answers[3].text}

Respond with ONLY the letter of your chosen answer (A, B, C, or D)."""

    def _extract_answer_letter(self, response: str) -> str:
        cleaned = response.strip().upper()

        if re.match(r"^[ABCD]([^A-Z]|$)", cleaned, re.IGNORECASE):
            return cleaned[0]

        patterns = [
            r"(?:answer|choice|option|select|choose)[:\s]*([ABCD])",
            r"^([ABCD])\)",
            r"^([ABCD])\.",
            r"\b([ABCD])\s*[-–—]\s",
            r'^"?([ABCD])"?$',
            r"I (?:would )?(?:choose|select|pick) ([ABCD])",
            r"(?:my|the) answer is ([ABCD])",
        ]

        for pattern in patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        match = re.search(r"\b([ABCD])\b", cleaned)
        if match:
            return match.group(1)

        raise ValidationError(
            f'Could not extract answer from: "{response[:100]}..."',
            field="response",
        )

    async def _submit_responses(
        self,
        sdk_session_id: str,
        config: ServerConfig,
        responses: List[Dict[str, Any]],
        total_duration_ms: int,
        metadata: Optional[Dict[str, Any]],
    ) -> AssessmentResult:
        payload = {
            "sdkSessionId": sdk_session_id,
            "sdkVersion": __version__,
            "questionSetVersion": config.question_set_version,
            "responses": responses,
            "timing": {
                "totalDurationMs": total_duration_ms,
                "averageQuestionMs": total_duration_ms // len(responses),
            },
            "environment": self._detect_environment().model_dump(),
            "metadata": metadata,
        }

        response = await self._request("POST", "/api/sdk/assess", json=payload)
        return AssessmentResult.from_api_response(response)

    def _detect_environment(self) -> ClientEnvironment:
        env = ClientEnvironment(
            python_version=platform.python_version(),
            platform=sys.platform,
            arch=platform.machine(),
        )

        if os.environ.get("GITHUB_ACTIONS"):
            env.ci_provider = "github"
            env.ci_job_id = os.environ.get("GITHUB_RUN_ID")
        elif os.environ.get("GITLAB_CI"):
            env.ci_provider = "gitlab"
            env.ci_job_id = os.environ.get("CI_JOB_ID")

        env.git_commit = os.environ.get("GITHUB_SHA") or os.environ.get("CI_COMMIT_SHA")
        env.git_branch = os.environ.get("GITHUB_REF_NAME") or os.environ.get(
            "CI_COMMIT_REF_NAME"
        )

        return env

    def _mock_result(
        self, sdk_session_id: str, config: ServerConfig
    ) -> AssessmentResult:
        mock_hash = hashlib.sha256(f"dryrun_{sdk_session_id}".encode()).hexdigest()

        return AssessmentResult(
            run_id=f"dryrun_{sdk_session_id}",
            sdk_session_id=sdk_session_id,
            scores=DimensionScores(lying=8.0, cheating=7.5, stealing=8.5, harm=7.0),
            passed=DimensionPassed(lying=True, cheating=True, stealing=True, harm=True),
            overall_passed=True,
            thresholds=config.thresholds,
            classification="Well Adjusted",
            verify_url="https://www.aiassesstech.com/verify/dryrun",
            completed_at=datetime.now(timezone.utc),
            versions=VersionInfo(
                sdk_version=__version__,
                question_set_version=config.question_set_version,
            ),
            key_name=config.key_name,
            result_hash=mock_hash,
            variance=2.5,
            is_stable=True,
            principle_points=PrinciplePoints(
                point_1=(8.0, 7.5),
                point_2=(8.5, 7.0),
            ),
            question_bank_version=config.question_set_version,
        )

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                response = await self._client.request(method, path, **kwargs)

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    raise RateLimitError("Rate limit exceeded", retry_after=retry_after)

                if response.status_code >= 400:
                    error_data = response.json()
                    raise AIAssessError(
                        error_data.get("error", f"HTTP {response.status_code}"),
                        code=error_data.get("code", "API_ERROR"),
                    )

                return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise NetworkError(
                    f"Request timed out after {self._max_retries} attempts",
                    original_error=e,
                ) from e

            except httpx.HTTPError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise NetworkError(f"HTTP error: {e}", original_error=e) from e

        raise AIAssessError(f"Request failed: {last_error}")

