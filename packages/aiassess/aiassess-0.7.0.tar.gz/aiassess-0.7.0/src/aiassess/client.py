"""
Synchronous client for AI Assess Tech Python SDK.

Example:
    >>> from aiassess import AIAssessClient
    >>>
    >>> def my_ai(question: str) -> str:
    ...     return openai.chat.completions.create(
    ...         model="gpt-4",
    ...         messages=[{"role": "user", "content": question}]
    ...     ).choices[0].message.content
    >>>
    >>> with AIAssessClient(health_check_key="hck_...") as client:
    ...     result = client.assess(callback=my_ai)
    ...     print(f"Passed: {result.overall_passed}")
"""

from __future__ import annotations

import hashlib
import logging
import os
import platform
import re
import secrets
import sys
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import httpx

from aiassess._version import __version__
from aiassess.types import (
    AICallback,
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
DEFAULT_OVERALL_TIMEOUT = 360.0  # 6 minutes
MAX_RESPONSE_LENGTH = 1000


class AIAssessClient:
    """
    Synchronous client for AI Assess Tech ethical assessments.

    Args:
        health_check_key: Your Health Check Key (format: hck_...)
        base_url: API base URL (default: https://www.aiassesstech.com)
        timeout: Per-request timeout in seconds (default: 30)
        overall_timeout: Overall assessment timeout in seconds (default: 360)
        max_retries: Maximum retry attempts for transient errors (default: 3)

    Example:
        >>> client = AIAssessClient(health_check_key="hck_your_key_here")
        >>> result = client.assess(callback=my_ai_function)
        >>> print(f"Classification: {result.classification}")
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
        # Validate key format
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

        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
            headers={
                "X-Health-Check-Key": health_check_key,
                "Content-Type": "application/json",
                "User-Agent": f"aiassess-python/{__version__}",
                "X-SDK-Version": __version__,
            },
        )

    def assess(
        self,
        callback: AICallback,
        *,
        on_progress: Optional[Callable[[AssessProgress], None]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dry_run: bool = False,
    ) -> AssessmentResult:
        """
        Run an ethical assessment on an AI implementation.

        Args:
            callback: Function that sends a question to your AI and returns the response.
                      Signature: (question: str) -> str
            on_progress: Optional callback for progress updates
            metadata: Optional metadata to store with the assessment
            dry_run: If True, only 5 questions and returns mock scores

        Returns:
            AssessmentResult with scores, pass/fail status, and verification URL

        Raises:
            ValidationError: If callback returns invalid response
            QuestionTimeoutError: If a single question times out
            OverallTimeoutError: If overall assessment times out
            AssessmentError: If assessment fails for other reasons

        Example:
            >>> def my_ai(question: str) -> str:
            ...     response = openai.chat.completions.create(
            ...         model="gpt-4",
            ...         messages=[{"role": "user", "content": question}]
            ...     )
            ...     return response.choices[0].message.content or ""
            >>>
            >>> result = client.assess(callback=my_ai)
        """
        # 1. Fetch server configuration
        config = self._get_config()

        # 2. Generate session ID
        sdk_session_id = f"sdk_{secrets.token_hex(6)}"
        client_started_at = time.time()

        # 3. Select questions
        questions = config.questions[:5] if dry_run else config.questions

        # 4. Collect responses
        responses: List[Dict[str, Any]] = []
        logger.info(f"🚀 Starting assessment ({len(questions)} questions)...")

        for i, q in enumerate(questions):
            # Check overall timeout
            elapsed = time.time() - client_started_at
            if elapsed > self._overall_timeout:
                raise OverallTimeoutError(
                    f"Assessment exceeded overall timeout of {self._overall_timeout}s",
                    completed_questions=i,
                    timeout_ms=int(self._overall_timeout * 1000),
                )

            # Progress callback
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

            # Ask question
            question_start = time.time()
            try:
                formatted = self._format_question(q)
                response = callback(formatted)
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

        client_completed_at = time.time()
        total_duration_ms = int((client_completed_at - client_started_at) * 1000)

        logger.info(f"✅ All questions answered in {total_duration_ms / 1000:.1f}s")

        # Dry run returns mock result
        if dry_run:
            logger.info("🧪 Dry run mode - returning mock scores")
            return self._mock_result(sdk_session_id, config)

        # 5. Submit responses
        logger.info("📤 Submitting responses for scoring...")
        result = self._submit_responses(
            sdk_session_id=sdk_session_id,
            config=config,
            responses=responses,
            total_duration_ms=total_duration_ms,
            metadata=metadata,
        )

        status = "PASSED ✅" if result.overall_passed else "FAILED ❌"
        logger.info(f"📊 Result: {result.classification} ({status})")

        return result

    def block_until_pass(
        self,
        callback: AICallback,
        *,
        max_retries: int = 3,
        retry_delay_seconds: float = 60.0,
        exit_on_failure: bool = False,
        on_progress: Optional[Callable[[AssessProgress], None]] = None,
        on_failure: Optional[Callable[[AssessmentResult, int], None]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssessmentResult:
        """
        Block until assessment passes (for startup health checks).

        Args:
            callback: AI callback function
            max_retries: Maximum retry attempts (default: 3)
            retry_delay_seconds: Delay between retries in seconds (default: 60)
            exit_on_failure: Exit process on final failure (default: False)
            on_progress: Progress callback
            on_failure: Callback on each failed attempt
            metadata: Optional metadata

        Returns:
            AssessmentResult (only if passed)

        Raises:
            AssessmentError: If AI fails after all retries (unless exit_on_failure=True)
        """
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Attempt {attempt}/{max_retries}...")

            result = self.assess(
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
            time.sleep(retry_delay_seconds)

        raise AssertionError("Unexpected: should not reach here")

    def get_config(self) -> ServerConfig:
        """Get the current server configuration (questions, thresholds)."""
        return self._get_config()

    def verify(self, run_id: str) -> Dict[str, Any]:
        """Verify the cryptographic integrity of an assessment result."""
        response = self._request("GET", f"/api/health-check/verify/{run_id}")
        return response

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> "AIAssessClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # Private methods

    def _get_config(self) -> ServerConfig:
        """Fetch and cache server configuration."""
        if self._cached_config is not None:
            return self._cached_config

        response = self._request("GET", "/api/sdk/config")
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
        """Extract answer letter from AI response."""
        cleaned = response.strip().upper()

        # Priority 1: Starts with letter
        if re.match(r"^[ABCD]([^A-Z]|$)", cleaned, re.IGNORECASE):
            return cleaned[0]

        # Priority 2: Common patterns
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

        # Priority 3: First standalone letter
        match = re.search(r"\b([ABCD])\b", cleaned)
        if match:
            return match.group(1)

        raise ValidationError(
            f'Could not extract answer from: "{response[:100]}..."',
            field="response",
        )

    def _submit_responses(
        self,
        sdk_session_id: str,
        config: ServerConfig,
        responses: List[Dict[str, Any]],
        total_duration_ms: int,
        metadata: Optional[Dict[str, Any]],
    ) -> AssessmentResult:
        """Submit responses to server for scoring."""
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

        response = self._request("POST", "/api/sdk/assess", json=payload)
        return AssessmentResult.from_api_response(response)

    def _detect_environment(self) -> ClientEnvironment:
        """Detect client environment information."""
        env = ClientEnvironment(
            python_version=platform.python_version(),
            platform=sys.platform,  # type: ignore
            arch=platform.machine(),
        )

        # CI detection
        if os.environ.get("GITHUB_ACTIONS"):
            env.ci_provider = "github"
            env.ci_job_id = os.environ.get("GITHUB_RUN_ID")
        elif os.environ.get("GITLAB_CI"):
            env.ci_provider = "gitlab"
            env.ci_job_id = os.environ.get("CI_JOB_ID")
        elif os.environ.get("CIRCLECI"):
            env.ci_provider = "circleci"
            env.ci_job_id = os.environ.get("CIRCLE_BUILD_NUM")

        # Git info
        env.git_commit = os.environ.get("GITHUB_SHA") or os.environ.get("CI_COMMIT_SHA")
        env.git_branch = os.environ.get("GITHUB_REF_NAME") or os.environ.get(
            "CI_COMMIT_REF_NAME"
        )

        return env

    def _mock_result(
        self, sdk_session_id: str, config: ServerConfig
    ) -> AssessmentResult:
        """Return mock result for dry run."""
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

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        last_error: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                response = self._client.request(method, path, **kwargs)

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    raise RateLimitError(
                        "Rate limit exceeded",
                        retry_after=retry_after,
                    )

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
                    time.sleep(2**attempt)
                    continue
                raise NetworkError(
                    f"Request timed out after {self._max_retries} attempts",
                    original_error=e,
                ) from e

            except httpx.HTTPError as e:
                last_error = e
                if attempt < self._max_retries - 1:
                    time.sleep(2**attempt)
                    continue
                raise NetworkError(f"HTTP error: {e}", original_error=e) from e

        raise AIAssessError(f"Request failed: {last_error}")

