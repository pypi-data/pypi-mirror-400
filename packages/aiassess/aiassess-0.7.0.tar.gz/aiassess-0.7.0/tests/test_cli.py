"""
Tests for AI Assess Tech SDK CLI.
"""

import pytest
from aiassess.cli import main


class TestCLI:
    """Tests for CLI commands."""

    def test_no_command_shows_help(self, capsys):
        """Test that no command shows help."""
        result = main([])
        assert result == 0

    def test_version(self, capsys):
        """Test version flag."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        # argparse exits with 0 for version
        assert exc_info.value.code == 0

    def test_assess_without_key(self, capsys):
        """Test assess command without key."""
        result = main(["assess"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No Health Check Key" in captured.err

    def test_verify_without_key(self, capsys):
        """Test verify command without key."""
        result = main(["verify", "test_run_123"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No Health Check Key" in captured.err

    def test_config_without_key(self, capsys):
        """Test config command without key."""
        result = main(["config"])
        assert result == 1
        captured = capsys.readouterr()
        assert "No Health Check Key" in captured.err


class TestCLIWithMocks:
    """Tests for CLI with mocked HTTP."""

    def test_assess_with_key(
        self, httpx_mock, valid_health_check_key, mock_config_response, capsys
    ):
        """Test assess command with valid key."""
        from pytest_httpx import HTTPXMock

        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        result = main(["assess", "--key", valid_health_check_key, "--dry-run"])

        assert result == 0
        captured = capsys.readouterr()
        assert "AI ASSESS TECH" in captured.out

    def test_assess_json_output(
        self, httpx_mock, valid_health_check_key, mock_config_response, capsys
    ):
        """Test assess command with JSON output."""
        httpx_mock.add_response(
            method="GET",
            url="https://www.aiassesstech.com/api/sdk/config",
            json=mock_config_response,
        )

        result = main(
            ["assess", "--key", valid_health_check_key, "--dry-run", "--json"]
        )

        assert result == 0
        captured = capsys.readouterr()
        # JSON output should contain result fields
        assert "run_id" in captured.out or "dryrun_" in captured.out

