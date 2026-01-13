"""
AI Assess Tech Python SDK

Assess AI systems for ethical alignment across 4 dimensions:
Lying, Cheating, Stealing, and Harm.

Example:
    >>> from aiassess import AIAssessClient
    >>>
    >>> client = AIAssessClient(health_check_key="hck_...")
    >>> result = client.assess(callback=lambda q: my_ai.chat(q))
    >>> print(f"Passed: {result.overall_passed}")

"""

from aiassess._version import __version__
from aiassess.client import AIAssessClient
from aiassess.async_client import AsyncAIAssessClient
from aiassess.types import (
    AssessmentResult,
    AssessProgress,
    DimensionScores,
    DimensionPassed,
    ServerConfig,
    ClientEnvironment,
    Question,
    Answer,
    PrinciplePoints,
    VersionInfo,
    VerificationResult,
)
from aiassess.exceptions import (
    AIAssessError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    AssessmentError,
    QuestionTimeoutError,
    OverallTimeoutError,
    NetworkError,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "AIAssessClient",
    "AsyncAIAssessClient",
    # Types
    "AssessmentResult",
    "AssessProgress",
    "DimensionScores",
    "DimensionPassed",
    "ServerConfig",
    "ClientEnvironment",
    "Question",
    "Answer",
    "PrinciplePoints",
    "VersionInfo",
    "VerificationResult",
    # Exceptions
    "AIAssessError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "AssessmentError",
    "QuestionTimeoutError",
    "OverallTimeoutError",
    "NetworkError",
]

