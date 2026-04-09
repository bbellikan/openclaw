"""Tests for OpenClaw integration."""

from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import AmazonRegion, Settings
from src.openclaw import RunMode, build_task_message, check_openclaw_installed


class TestBuildTaskMessage:
    """Tests for task message generation."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Create mock settings for testing."""
        return Settings(
            amazon_nl_username="test@example.com",
            amazon_nl_password="testpass123",
            google_api_key="test-key",
            max_price_eur=Decimal("10.00"),
            region=AmazonRegion.NL,
        )

    def test_dry_run_message_contains_stop_instruction(
        self, mock_settings: Settings
    ) -> None:
        """Test that dry run message contains instruction not to purchase."""
        message = build_task_message(mock_settings, RunMode.DRY_RUN)
        assert "DRY RUN MODE" in message
        assert "DO NOT COMPLETE THE PURCHASE" in message
        assert "DO NOT click" in message

    def test_live_message_allows_purchase(self, mock_settings: Settings) -> None:
        """Test that live message allows completing purchase."""
        message = build_task_message(mock_settings, RunMode.LIVE)
        assert "DRY RUN MODE" not in message
        assert "place the order" in message

    def test_message_includes_budget(self, mock_settings: Settings) -> None:
        """Test that message includes budget constraint."""
        message = build_task_message(mock_settings, RunMode.DRY_RUN)
        assert "€10.00" in message

    def test_message_includes_credentials(self, mock_settings: Settings) -> None:
        """Test that message includes login credentials."""
        message = build_task_message(mock_settings, RunMode.DRY_RUN)
        assert "test@example.com" in message
        assert "testpass123" in message

    def test_message_includes_region_url(self, mock_settings: Settings) -> None:
        """Test that message includes correct Amazon URL."""
        message = build_task_message(mock_settings, RunMode.DRY_RUN)
        assert "amazon.nl" in message


class TestCheckOpenClawInstalled:
    """Tests for OpenClaw installation check."""

    def test_returns_path_when_installed(self) -> None:
        """Test that function returns path when OpenClaw is found."""
        with patch("shutil.which", return_value="/usr/local/bin/openclaw"):
            result = check_openclaw_installed()
            assert result == Path("/usr/local/bin/openclaw")

    def test_raises_when_not_installed(self) -> None:
        """Test that function raises when OpenClaw is not found."""
        from src.openclaw import OpenClawNotInstalledError

        with patch("shutil.which", return_value=None):
            with pytest.raises(OpenClawNotInstalledError):
                check_openclaw_installed()
