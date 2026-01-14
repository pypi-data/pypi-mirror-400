"""Tests for sp upgrade command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from sp.main import app

runner = CliRunner()


class TestUpgrade:
    """Test suite for sp upgrade command."""

    def test_get_library_from_config(self, tmp_path: Path) -> None:
        """Test reading library name from config."""
        from sp.commands.upgrade import get_signalpilot_library

        # Mock config file
        config_file = tmp_path / "user-cli.toml"
        config_file.write_text('library = "signalpilot-ai-internal"\n')

        with patch("sp.config.SP_USER_CLI_CONFIG", config_file):
            lib = get_signalpilot_library()
            assert lib == "signalpilot-ai-internal"

    def test_get_library_default(self) -> None:
        """Test default library when config doesn't exist."""
        from sp.commands.upgrade import get_signalpilot_library

        with patch("sp.config.SP_USER_CLI_CONFIG", Path("/nonexistent/config.toml")):
            lib = get_signalpilot_library()
            assert lib == "signalpilot-ai"

    @patch("sp.commands.upgrade.upgrade_library")
    @patch("sp.commands.upgrade.upgrade_cli")
    def test_upgrade_both_success(
        self, mock_cli: MagicMock, mock_lib: MagicMock
    ) -> None:
        """Test successful upgrade of both CLI and library."""
        mock_cli.return_value = True
        mock_lib.return_value = True

        result = runner.invoke(app, ["upgrade"])

        assert result.exit_code == 0
        assert "Upgrade complete!" in result.stdout
        mock_cli.assert_called_once()
        mock_lib.assert_called_once()

    @patch("sp.commands.upgrade.upgrade_library")
    @patch("sp.commands.upgrade.upgrade_cli")
    def test_upgrade_cli_fails(
        self, mock_cli: MagicMock, mock_lib: MagicMock
    ) -> None:
        """Test when CLI upgrade fails."""
        mock_cli.return_value = False
        mock_lib.return_value = True

        result = runner.invoke(app, ["upgrade"])

        # Exit code is still 1 when one component fails
        assert result.exit_code == 1
        # Check output contains info about partial upgrade
        output = result.stdout
        assert "library upgrade" in output.lower() or "cli upgrade" in output.lower()

    @patch("sp.commands.upgrade.upgrade_library")
    @patch("sp.commands.upgrade.upgrade_cli")
    def test_upgrade_library_fails(
        self, mock_cli: MagicMock, mock_lib: MagicMock
    ) -> None:
        """Test when library upgrade fails."""
        mock_cli.return_value = True
        mock_lib.return_value = False

        result = runner.invoke(app, ["upgrade"])

        # Exit code is still 1 when one component fails
        assert result.exit_code == 1
        # Check output contains info about partial upgrade
        output = result.stdout
        assert "library upgrade" in output.lower() or "cli upgrade" in output.lower()

    @patch("sp.commands.upgrade.upgrade_library")
    @patch("sp.commands.upgrade.upgrade_cli")
    def test_upgrade_both_fail(
        self, mock_cli: MagicMock, mock_lib: MagicMock
    ) -> None:
        """Test when both upgrades fail."""
        mock_cli.return_value = False
        mock_lib.return_value = False

        result = runner.invoke(app, ["upgrade"])

        assert result.exit_code == 1
        assert "Upgrade failed" in result.stdout

    @patch("sp.commands.upgrade.get_latest_pypi_version")
    @patch("sp.config.is_initialized")
    def test_upgrade_library_not_initialized(
        self, mock_init: MagicMock, mock_pypi: MagicMock
    ) -> None:
        """Test library upgrade when not initialized."""
        from sp.commands.upgrade import upgrade_library

        mock_init.return_value = False

        result = upgrade_library()

        assert result is False
        mock_pypi.assert_not_called()

    @patch("subprocess.run")
    @patch("sp.commands.upgrade.get_latest_pypi_version")
    @patch("sp.commands.upgrade.get_signalpilot_library")
    @patch("sp.config.is_initialized")
    def test_upgrade_library_success(
        self,
        mock_init: MagicMock,
        mock_get_lib: MagicMock,
        mock_pypi: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test successful library upgrade."""
        from sp.commands.upgrade import upgrade_library

        mock_init.return_value = True
        mock_get_lib.return_value = "signalpilot-ai"
        mock_pypi.return_value = "1.0.0"
        mock_run.return_value = MagicMock(returncode=0)

        result = upgrade_library()

        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    @patch("sp.commands.upgrade.get_latest_pypi_version")
    @patch("sp.commands.upgrade.get_current_cli_version")
    def test_upgrade_cli_already_latest(
        self,
        mock_current: MagicMock,
        mock_latest: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test CLI upgrade when already on latest version."""
        from sp.commands.upgrade import upgrade_cli

        mock_current.return_value = "1.0.0"
        mock_latest.return_value = "1.0.0"

        result = upgrade_cli()

        assert result is True
        mock_run.assert_not_called()  # Should not upgrade
