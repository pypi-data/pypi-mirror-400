"""
Tests for AI Assess Tech SDK exceptions.
"""

import pytest

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


class TestAIAssessError:
    """Tests for base AIAssessError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = AIAssessError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.code == "UNKNOWN_ERROR"
        assert error.details == {}

    def test_error_with_code(self):
        """Test error with custom code."""
        error = AIAssessError("Failed", code="CUSTOM_ERROR")
        assert error.code == "CUSTOM_ERROR"

    def test_error_with_details(self):
        """Test error with details."""
        error = AIAssessError("Failed", details={"key": "value"})
        assert error.details == {"key": "value"}

    def test_str_representation(self):
        """Test string representation."""
        error = AIAssessError("Failed", code="TEST_ERROR")
        assert str(error) == "[TEST_ERROR] Failed"

    def test_repr(self):
        """Test repr."""
        error = AIAssessError("Failed", code="TEST_ERROR")
        assert "AIAssessError" in repr(error)


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()
        assert error.message == "Authentication failed"
        assert error.code == "AUTHENTICATION_ERROR"

    def test_custom_message(self):
        """Test custom error message."""
        error = AuthenticationError("Invalid key format")
        assert error.message == "Invalid key format"


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_default_retry_after(self):
        """Test default retry_after value."""
        error = RateLimitError()
        assert error.retry_after == 60

    def test_custom_retry_after(self):
        """Test custom retry_after value."""
        error = RateLimitError("Too many requests", retry_after=120)
        assert error.retry_after == 120

    def test_str_includes_retry_after(self):
        """Test string includes retry_after."""
        error = RateLimitError("Too fast", retry_after=30)
        assert "30s" in str(error)


class TestValidationError:
    """Tests for ValidationError."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Invalid input")
        assert error.message == "Invalid input"
        assert error.code == "VALIDATION_ERROR"
        assert error.field is None

    def test_with_field(self):
        """Test validation error with field."""
        error = ValidationError("Must be positive", field="amount")
        assert error.field == "amount"
        assert error.details["field"] == "amount"


class TestAssessmentError:
    """Tests for AssessmentError."""

    def test_basic_assessment_error(self):
        """Test basic assessment error."""
        error = AssessmentError("Assessment failed")
        assert error.message == "Assessment failed"
        assert error.completed_questions is None
        assert error.failed_question_id is None

    def test_with_context(self):
        """Test assessment error with context."""
        error = AssessmentError(
            "Question failed",
            completed_questions=5,
            failed_question_id="q6",
        )
        assert error.completed_questions == 5
        assert error.failed_question_id == "q6"
        assert error.details["completed_questions"] == 5
        assert error.details["failed_question_id"] == "q6"


class TestQuestionTimeoutError:
    """Tests for QuestionTimeoutError."""

    def test_creation(self):
        """Test question timeout error creation."""
        error = QuestionTimeoutError(
            "Question timed out",
            question_id="q10",
            timeout_ms=30000,
        )
        assert error.question_id == "q10"
        assert error.timeout_ms == 30000
        assert error.code == "QUESTION_TIMEOUT_ERROR"
        assert error.failed_question_id == "q10"


class TestOverallTimeoutError:
    """Tests for OverallTimeoutError."""

    def test_creation(self):
        """Test overall timeout error creation."""
        error = OverallTimeoutError(
            "Assessment timed out",
            completed_questions=50,
            timeout_ms=360000,
        )
        assert error.completed_questions == 50
        assert error.timeout_ms == 360000
        assert error.code == "OVERALL_TIMEOUT_ERROR"


class TestNetworkError:
    """Tests for NetworkError."""

    def test_default_message(self):
        """Test default network error message."""
        error = NetworkError()
        assert error.message == "Network error occurred"
        assert error.code == "NETWORK_ERROR"

    def test_with_original_error(self):
        """Test network error with original exception."""
        original = ConnectionError("Connection refused")
        error = NetworkError("Connection failed", original_error=original)
        assert error.original_error is original
        assert "Connection refused" in error.details["original_error"]


class TestErrorHierarchy:
    """Tests for exception hierarchy."""

    def test_all_inherit_from_base(self):
        """Test all exceptions inherit from AIAssessError."""
        exceptions = [
            AuthenticationError(),
            RateLimitError(),
            ValidationError("test"),
            AssessmentError("test"),
            QuestionTimeoutError("test", "q1", 1000),
            OverallTimeoutError("test", 5, 1000),
            NetworkError(),
        ]

        for exc in exceptions:
            assert isinstance(exc, AIAssessError)

    def test_timeout_errors_are_assessment_errors(self):
        """Test timeout errors inherit from AssessmentError."""
        question_timeout = QuestionTimeoutError("test", "q1", 1000)
        overall_timeout = OverallTimeoutError("test", 5, 1000)

        assert isinstance(question_timeout, AssessmentError)
        assert isinstance(overall_timeout, AssessmentError)

    def test_can_catch_by_base_class(self):
        """Test catching by base class."""
        try:
            raise AuthenticationError("Invalid key")
        except AIAssessError as e:
            assert e.code == "AUTHENTICATION_ERROR"

