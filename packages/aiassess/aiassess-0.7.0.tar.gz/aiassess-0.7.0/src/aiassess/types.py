"""
Type definitions for AI Assess Tech Python SDK.

Uses Pydantic v2 for runtime validation and serialization.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from typing import Awaitable

# Type aliases
Provider = Literal["openai", "anthropic", "gemini", "grok", "ollama", "mistral", "custom"]
Dimension = Literal["Lying", "Cheating", "Stealing", "Harm"]
Classification = Literal["Well Adjusted", "Misguided", "Manipulative", "Psychopath"]
PassFail = Literal["PASS", "WARNING", "FAIL"]

# Callback type for AI interaction
AICallback = Callable[[str], str]
AsyncAICallback = Callable[[str], "Awaitable[str]"]


class DimensionScores(BaseModel):
    """Scores for each ethical dimension (0-10 scale, higher = more ethical)."""

    lying: float = Field(..., ge=0, le=10, description="Lying dimension score")
    cheating: float = Field(..., ge=0, le=10, description="Cheating dimension score")
    stealing: float = Field(..., ge=0, le=10, description="Stealing dimension score")
    harm: float = Field(..., ge=0, le=10, description="Harm dimension score")

    @property
    def overall(self) -> float:
        """Calculate overall average score."""
        return (self.lying + self.cheating + self.stealing + self.harm) / 4


class DimensionPassed(BaseModel):
    """Pass/fail status for each dimension."""

    lying: bool
    cheating: bool
    stealing: bool
    harm: bool


class AssessProgress(BaseModel):
    """Progress update during assessment."""

    current: int = Field(..., ge=1, description="Current question number")
    total: int = Field(..., ge=1, description="Total questions")
    percentage: int = Field(..., ge=0, le=100, description="Completion percentage")
    dimension: Dimension = Field(..., description="Current dimension being tested")
    question_id: str = Field(..., description="Current question ID")
    question_preview: str = Field(..., description="First 50 chars of question")
    elapsed_ms: int = Field(..., ge=0, description="Elapsed time in milliseconds")
    estimated_remaining_ms: int = Field(..., ge=0, description="Estimated remaining time")


class VersionInfo(BaseModel):
    """Version information for traceability."""

    sdk_version: str
    question_set_version: str


class PrinciplePoints(BaseModel):
    """Principle point coordinates for visualization."""

    point_1: Tuple[float, float] = Field(..., description="(lying, cheating) coordinates")
    point_2: Tuple[float, float] = Field(..., description="(stealing, harm) coordinates")


class AssessmentResult(BaseModel):
    """Complete assessment result with all scoring data."""

    run_id: str = Field(..., description="Server-generated run ID")
    sdk_session_id: str = Field(..., description="Client-generated session ID")
    scores: DimensionScores = Field(..., description="Scores per dimension")
    passed: DimensionPassed = Field(..., description="Pass/fail per dimension")
    overall_passed: bool = Field(..., description="Overall pass (all dimensions)")
    thresholds: DimensionScores = Field(..., description="Thresholds used")
    classification: Classification = Field(..., description="Personality classification")
    verify_url: str = Field(..., description="Verification URL")
    completed_at: datetime = Field(..., description="Completion timestamp")
    versions: VersionInfo = Field(..., description="Version information")
    key_name: str = Field(..., description="Key label used")

    # Patent specification fields
    result_hash: str = Field(..., description="SHA-256 hash for cryptographic verification")
    variance: float = Field(..., ge=0, description="Variance between principle points")
    is_stable: bool = Field(..., description="True if variance < 5 (stable result)")
    principle_points: PrinciplePoints = Field(..., description="Coordinates for dual moral map")
    question_bank_version: str = Field(..., description="Question bank version for verification")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "AssessmentResult":
        """Parse API response into AssessmentResult."""
        return cls(
            run_id=data["runId"],
            sdk_session_id=data["sdkSessionId"],
            scores=DimensionScores(**data["scores"]),
            passed=DimensionPassed(**data["passed"]),
            overall_passed=data["overallPassed"],
            thresholds=DimensionScores(**data["thresholds"]),
            classification=data["classification"],
            verify_url=data["verifyUrl"],
            completed_at=datetime.fromisoformat(data["completedAt"].replace("Z", "+00:00")),
            versions=VersionInfo(
                sdk_version=data["versions"]["sdkVersion"],
                question_set_version=data["versions"]["questionSetVersion"],
            ),
            key_name=data["keyName"],
            result_hash=data["resultHash"],
            variance=data["variance"],
            is_stable=data["isStable"],
            principle_points=PrinciplePoints(
                point_1=(data["principlePoint1"]["x"], data["principlePoint1"]["y"]),
                point_2=(data["principlePoint2"]["x"], data["principlePoint2"]["y"]),
            ),
            question_bank_version=data["questionBankVersion"],
        )

    def to_array(self) -> Tuple[float, float, float, float, bool, bool, bool, bool]:
        """
        Convert to flat array format.

        Returns:
            Tuple of (lying_score, cheating_score, stealing_score, harm_score,
                      lying_passed, cheating_passed, stealing_passed, harm_passed)
        """
        return (
            self.scores.lying,
            self.scores.cheating,
            self.scores.stealing,
            self.scores.harm,
            self.passed.lying,
            self.passed.cheating,
            self.passed.stealing,
            self.passed.harm,
        )


class Answer(BaseModel):
    """Individual answer option with scoring."""

    letter: str = Field(..., description="A, B, C, or D")
    text: str = Field(..., description="Full answer text")
    score: int = Field(..., ge=0, le=10, description="Score value (0-10)")
    personality: Classification = Field(..., description="Personality mapping")


class Question(BaseModel):
    """Individual question from the server."""

    id: str = Field(..., description="Question ID")
    text: str = Field(..., description="Question text")
    dimension: Dimension = Field(..., description="Ethical dimension being tested")
    principle_id: int = Field(..., alias="principleId", description="Principle ID")
    principle_text: str = Field(..., alias="principleText", description="Principle text")
    answers: List[Answer] = Field(..., description="Answer options with scores")

    model_config = {"populate_by_name": True}


class ServerConfig(BaseModel):
    """Configuration returned from server."""

    test_mode: Literal["ISOLATED", "CONVERSATIONAL", "SDK"] = Field(..., alias="testMode")
    framework_id: str = Field(..., alias="frameworkId")
    question_set_version: str = Field(..., alias="questionSetVersion")
    thresholds: DimensionScores
    questions: List[Question]
    key_name: str = Field(..., alias="keyName")
    organization_name: str = Field(..., alias="organizationName")

    model_config = {"populate_by_name": True}


class ClientEnvironment(BaseModel):
    """Auto-detected client environment information."""

    python_version: Optional[str] = None
    platform: Optional[Literal["linux", "darwin", "win32"]] = None
    arch: Optional[str] = None
    ci_provider: Optional[str] = None
    ci_job_id: Optional[str] = None
    git_commit: Optional[str] = None
    git_branch: Optional[str] = None

    # Enterprise additions
    hostname: Optional[str] = None
    container_id: Optional[str] = None
    cloud_provider: Optional[Literal["aws", "gcp", "azure", "other"]] = None
    deployment_env: Optional[Literal["development", "staging", "production"]] = None


class VerificationResult(BaseModel):
    """Result of cryptographic verification."""

    valid: bool = Field(..., description="Overall verification status")
    stored_hash: str = Field(..., description="Hash stored on server")
    computed_hash: str = Field(..., description="Hash computed from result data")
    hash_match: bool = Field(..., description="Whether hashes match")
    question_bank_verified: bool = Field(..., description="Question bank hash verified")
    bank_hash: Optional[str] = Field(None, description="Question bank hash if verified")

