"""
Tests for AI Assess Tech SDK types.
"""

import pytest
from datetime import datetime, timezone

from aiassess.types import (
    Answer,
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


class TestDimensionScores:
    """Tests for DimensionScores model."""

    def test_valid_scores(self):
        """Test valid score creation."""
        scores = DimensionScores(lying=8.0, cheating=7.5, stealing=9.0, harm=6.0)
        assert scores.lying == 8.0
        assert scores.cheating == 7.5
        assert scores.stealing == 9.0
        assert scores.harm == 6.0

    def test_overall_calculation(self):
        """Test overall score calculation."""
        scores = DimensionScores(lying=8.0, cheating=8.0, stealing=8.0, harm=8.0)
        assert scores.overall == 8.0

    def test_overall_calculation_mixed(self):
        """Test overall score with mixed values."""
        scores = DimensionScores(lying=10.0, cheating=0.0, stealing=5.0, harm=5.0)
        assert scores.overall == 5.0

    def test_boundary_values(self):
        """Test boundary values (0 and 10)."""
        scores = DimensionScores(lying=0.0, cheating=10.0, stealing=0.0, harm=10.0)
        assert scores.lying == 0.0
        assert scores.cheating == 10.0

    def test_invalid_score_too_high(self):
        """Test that scores > 10 are rejected."""
        with pytest.raises(ValueError):
            DimensionScores(lying=11.0, cheating=7.5, stealing=8.5, harm=7.0)

    def test_invalid_score_too_low(self):
        """Test that scores < 0 are rejected."""
        with pytest.raises(ValueError):
            DimensionScores(lying=-1.0, cheating=7.5, stealing=8.5, harm=7.0)


class TestDimensionPassed:
    """Tests for DimensionPassed model."""

    def test_all_passed(self):
        """Test all dimensions passed."""
        passed = DimensionPassed(lying=True, cheating=True, stealing=True, harm=True)
        assert passed.lying is True
        assert passed.cheating is True
        assert passed.stealing is True
        assert passed.harm is True

    def test_all_failed(self):
        """Test all dimensions failed."""
        passed = DimensionPassed(lying=False, cheating=False, stealing=False, harm=False)
        assert passed.lying is False
        assert passed.cheating is False

    def test_mixed_results(self):
        """Test mixed pass/fail results."""
        passed = DimensionPassed(lying=True, cheating=False, stealing=True, harm=False)
        assert passed.lying is True
        assert passed.cheating is False
        assert passed.stealing is True
        assert passed.harm is False


class TestAssessProgress:
    """Tests for AssessProgress model."""

    def test_valid_progress(self):
        """Test valid progress creation."""
        progress = AssessProgress(
            current=5,
            total=120,
            percentage=4,
            dimension="Lying",
            question_id="q123",
            question_preview="Is it ethical to...",
            elapsed_ms=5000,
            estimated_remaining_ms=115000,
        )
        assert progress.current == 5
        assert progress.total == 120
        assert progress.dimension == "Lying"
        assert progress.question_id == "q123"

    def test_progress_at_start(self):
        """Test progress at the start."""
        progress = AssessProgress(
            current=1,
            total=120,
            percentage=0,
            dimension="Lying",
            question_id="q1",
            question_preview="First question",
            elapsed_ms=0,
            estimated_remaining_ms=240000,
        )
        assert progress.current == 1
        assert progress.percentage == 0

    def test_progress_at_end(self):
        """Test progress at the end."""
        progress = AssessProgress(
            current=120,
            total=120,
            percentage=100,
            dimension="Harm",
            question_id="q120",
            question_preview="Last question",
            elapsed_ms=240000,
            estimated_remaining_ms=0,
        )
        assert progress.current == 120
        assert progress.percentage == 100


class TestAnswer:
    """Tests for Answer model."""

    def test_valid_answer(self):
        """Test valid answer creation."""
        answer = Answer(
            letter="A",
            text="Always tell the truth",
            score=10,
            personality="Well Adjusted",
        )
        assert answer.letter == "A"
        assert answer.text == "Always tell the truth"
        assert answer.score == 10
        assert answer.personality == "Well Adjusted"

    def test_all_personalities(self):
        """Test all personality types."""
        for personality in ["Well Adjusted", "Misguided", "Manipulative", "Psychopath"]:
            answer = Answer(letter="A", text="Test", score=5, personality=personality)
            assert answer.personality == personality


class TestQuestion:
    """Tests for Question model."""

    def test_valid_question(self):
        """Test valid question creation."""
        question = Question(
            id="q123",
            text="Is it ethical to lie?",
            dimension="Lying",
            principleId=1,
            principleText="Transparency",
            answers=[
                Answer(letter="A", text="No", score=10, personality="Well Adjusted"),
                Answer(letter="B", text="Sometimes", score=7, personality="Misguided"),
                Answer(letter="C", text="Often", score=3, personality="Manipulative"),
                Answer(letter="D", text="Yes", score=0, personality="Psychopath"),
            ],
        )
        assert question.id == "q123"
        assert question.dimension == "Lying"
        assert len(question.answers) == 4


class TestPrinciplePoints:
    """Tests for PrinciplePoints model."""

    def test_valid_points(self):
        """Test valid principle points."""
        points = PrinciplePoints(point_1=(8.0, 7.5), point_2=(8.5, 7.0))
        assert points.point_1 == (8.0, 7.5)
        assert points.point_2 == (8.5, 7.0)


class TestAssessmentResult:
    """Tests for AssessmentResult model."""

    def test_from_api_response(self, mock_assess_response):
        """Test parsing from API response."""
        result = AssessmentResult.from_api_response(mock_assess_response)

        assert result.run_id == "test_run_123"
        assert result.sdk_session_id == "sdk_abc123"
        assert result.overall_passed is True
        assert result.classification == "Well Adjusted"
        assert result.scores.lying == 8.0
        assert result.result_hash.startswith("a1b2c3")
        assert result.variance == 2.5
        assert result.is_stable is True
        assert result.principle_points.point_1 == (8.0, 7.5)

    def test_to_array(self, mock_assess_response):
        """Test conversion to array format."""
        result = AssessmentResult.from_api_response(mock_assess_response)
        arr = result.to_array()

        assert arr == (8.0, 7.5, 8.5, 7.0, True, True, True, True)

    def test_failed_result_to_array(self, mock_failed_assess_response):
        """Test failed result array format."""
        result = AssessmentResult.from_api_response(mock_failed_assess_response)
        arr = result.to_array()

        assert arr == (4.0, 5.0, 4.5, 3.0, False, False, False, False)


class TestClientEnvironment:
    """Tests for ClientEnvironment model."""

    def test_minimal_environment(self):
        """Test minimal environment."""
        env = ClientEnvironment()
        assert env.python_version is None
        assert env.ci_provider is None

    def test_full_environment(self):
        """Test full environment."""
        env = ClientEnvironment(
            python_version="3.11.0",
            platform="linux",
            arch="x86_64",
            ci_provider="github",
            ci_job_id="12345",
            git_commit="abc123",
            git_branch="main",
            hostname="server-1",
            container_id="docker-abc",
            cloud_provider="aws",
            deployment_env="production",
        )
        assert env.python_version == "3.11.0"
        assert env.ci_provider == "github"
        assert env.deployment_env == "production"


class TestServerConfig:
    """Tests for ServerConfig model."""

    def test_from_response(self, mock_config_response):
        """Test parsing server config from response."""
        config = ServerConfig.model_validate(mock_config_response)

        assert config.test_mode == "ISOLATED"
        assert config.framework_id == "morality"
        assert len(config.questions) == 2
        assert config.key_name == "Test Key"
        assert config.organization_name == "Test Org"
        assert config.thresholds.lying == 6.0

