"""
Exception hierarchy for AI Assess Tech Python SDK.

Follows Stripe/OpenAI pattern with specific, actionable exceptions.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class AIAssessError(Exception):
    """
    Base exception for all AI Assess Tech SDK errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r})"


class AuthenticationError(AIAssessError):
    """
    Raised when authentication fails.

    Common causes:
    - Invalid or expired Health Check Key
    - Key format incorrect (should start with 'hck_')
    - Key revoked or deactivated
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, code="AUTHENTICATION_ERROR", details=details)


class RateLimitError(AIAssessError):
    """
    Raised when rate limit is exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, code="RATE_LIMIT_ERROR", details=details)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message} (retry after {self.retry_after}s)"


class ValidationError(AIAssessError):
    """
    Raised when input validation fails.

    Common causes:
    - Invalid Health Check Key format
    - Missing required parameters
    - Invalid AI response format
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.field = field
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class AssessmentError(AIAssessError):
    """
    Raised when an assessment fails.

    Attributes:
        completed_questions: Number of questions completed before failure
        failed_question_id: ID of the question that caused failure
    """

    def __init__(
        self,
        message: str,
        completed_questions: Optional[int] = None,
        failed_question_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.completed_questions = completed_questions
        self.failed_question_id = failed_question_id
        details = details or {}
        if completed_questions is not None:
            details["completed_questions"] = completed_questions
        if failed_question_id:
            details["failed_question_id"] = failed_question_id
        super().__init__(message, code="ASSESSMENT_ERROR", details=details)


class QuestionTimeoutError(AssessmentError):
    """Raised when a single question times out."""

    def __init__(
        self,
        message: str,
        question_id: str,
        timeout_ms: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.question_id = question_id
        self.timeout_ms = timeout_ms
        details = details or {}
        details["question_id"] = question_id
        details["timeout_ms"] = timeout_ms
        super().__init__(
            message,
            failed_question_id=question_id,
            details=details,
        )
        self.code = "QUESTION_TIMEOUT_ERROR"


class OverallTimeoutError(AssessmentError):
    """Raised when the overall assessment times out."""

    def __init__(
        self,
        message: str,
        completed_questions: int,
        timeout_ms: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.timeout_ms = timeout_ms
        details = details or {}
        details["timeout_ms"] = timeout_ms
        super().__init__(
            message,
            completed_questions=completed_questions,
            details=details,
        )
        self.code = "OVERALL_TIMEOUT_ERROR"


class NetworkError(AIAssessError):
    """
    Raised when a network error occurs.

    Common causes:
    - Connection refused
    - DNS resolution failed
    - SSL/TLS errors
    - Request timeout
    """

    def __init__(
        self,
        message: str = "Network error occurred",
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.original_error = original_error
        details = details or {}
        if original_error:
            details["original_error"] = str(original_error)
        super().__init__(message, code="NETWORK_ERROR", details=details)

