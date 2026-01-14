"""Tests for sp install command."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from sp.main import app

runner = CliRunner()


class TestInstall:
    """Test suite for sp install command."""

    @patch("sp.config.is_initialized")
    def test_install_not_initialized(self, mock_initialized: MagicMock) -> None:
        """Test that install shows error when not initialized."""
        mock_initialized.return_value = False

        result = runner.invoke(app, ["install"])

        assert result.exit_code == 1
        assert "not installed" in result.stdout
        assert "sp init" in result.stdout

    @patch("sp.commands.install.get_version")
    @patch("sp.config.is_initialized")
    @patch("sp.config.SP_HOME", Path("/fake/home"))
    @patch("sp.config.SP_VENV", Path("/fake/home/.venv"))
    @patch("sp.config.get_venv_python")
    def test_install_status_healthy(
        self,
        mock_python: MagicMock,
        mock_initialized: MagicMock,
        mock_version: MagicMock,
    ) -> None:
        """Test status display when installation is healthy."""
        mock_initialized.return_value = True
        mock_version.return_value = "0.2.0"

        # Create a mock Path object with exists() method
        mock_python_path = MagicMock()
        mock_python_path.exists.return_value = True
        mock_python.return_value = mock_python_path

        result = runner.invoke(app, ["install"])

        assert result.exit_code == 0
        assert "installed (version: 0.2.0)" in result.stdout
        assert "sp lab" in result.stdout

    @patch("sp.commands.install.get_version")
    @patch("sp.config.is_initialized")
    @patch("sp.config.get_venv_python")
    def test_install_status_broken_venv(
        self,
        mock_python: MagicMock,
        mock_initialized: MagicMock,
        mock_version: MagicMock,
    ) -> None:
        """Test status display when venv is broken."""
        mock_initialized.return_value = True
        mock_version.return_value = "0.2.0"

        # Create a mock Path object with exists() returning False
        mock_python_path = MagicMock()
        mock_python_path.exists.return_value = False
        mock_python.return_value = mock_python_path

        result = runner.invoke(app, ["install"])

        assert result.exit_code == 0
        assert "Python environment is broken" in result.stdout
        assert "sp install --repair" in result.stdout

    @patch("sp.config.SP_HOME")
    def test_install_repair_not_initialized(self, mock_home: MagicMock) -> None:
        """Test that repair fails when not initialized."""
        mock_home.exists.return_value = False

        result = runner.invoke(app, ["install", "--repair"])

        assert result.exit_code == 1
        assert "not initialized" in result.stdout

    @patch("sp.core.environment.install_packages")
    @patch("sp.core.environment.create_venv")
    @patch("sp.core.environment.install_python")
    @patch("sp.core.environment.ensure_uv")
    @patch("sp.config.SP_VENV")
    @patch("sp.config.SP_HOME")
    def test_install_repair_success(
        self,
        mock_home: MagicMock,
        mock_venv: MagicMock,
        mock_uv: MagicMock,
        mock_install_python: MagicMock,
        mock_create_venv: MagicMock,
        mock_install_packages: MagicMock,
    ) -> None:
        """Test successful repair."""
        mock_home.exists.return_value = True
        mock_venv.exists.return_value = False
        mock_uv.return_value = True
        mock_install_python.return_value = True
        mock_create_venv.return_value = True
        mock_install_packages.return_value = True

        result = runner.invoke(app, ["install", "--repair"])

        assert result.exit_code == 0
        assert "Installation repaired" in result.stdout
        mock_install_python.assert_called_once()
        mock_create_venv.assert_called_once()
        mock_install_packages.assert_called_once()

    @patch("sp.config.SP_HOME")
    def test_install_force_not_initialized(self, mock_home: MagicMock) -> None:
        """Test force when not initialized."""
        mock_home.exists.return_value = False

        result = runner.invoke(app, ["install", "--force"])

        assert result.exit_code == 0
        assert "not installed" in result.stdout

    @patch("shutil.rmtree")
    @patch("sp.config.SP_SYSTEM")
    @patch("sp.config.SP_VENV")
    @patch("sp.config.SP_SIGNALPILOT")
    @patch("sp.config.SP_HOME")
    def test_install_force_cancelled(
        self,
        mock_home: MagicMock,
        mock_signalpilot: MagicMock,
        mock_venv: MagicMock,
        mock_system: MagicMock,
        mock_rmtree: MagicMock,
    ) -> None:
        """Test force installation cancelled by user."""
        mock_home.exists.return_value = True
        mock_signalpilot.exists.return_value = True
        mock_venv.exists.return_value = True
        mock_system.exists.return_value = True

        # Simulate user saying "no" to confirmation
        result = runner.invoke(app, ["install", "--force"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_rmtree.assert_not_called()

    @patch("shutil.rmtree")
    @patch("sp.config.SP_SYSTEM")
    @patch("sp.config.SP_VENV")
    @patch("sp.config.SP_SIGNALPILOT")
    @patch("sp.config.SP_HOME")
    def test_install_force_confirmed(
        self,
        mock_home: MagicMock,
        mock_signalpilot: MagicMock,
        mock_venv: MagicMock,
        mock_system: MagicMock,
        mock_rmtree: MagicMock,
    ) -> None:
        """Test force installation with user confirmation."""
        mock_home.exists.return_value = True

        # Mock the directory paths with .name attributes
        mock_signalpilot.exists.return_value = True
        mock_signalpilot.name = ".signalpilot"
        mock_venv.exists.return_value = True
        mock_venv.name = ".venv"
        mock_system.exists.return_value = True
        mock_system.name = "system"

        # Simulate user saying "yes" to confirmation
        result = runner.invoke(app, ["install", "--force"], input="y\n")

        assert result.exit_code == 0
        assert "Removed:" in result.stdout
        assert "sp init" in result.stdout

        # Verify all three directories were removed
        assert mock_rmtree.call_count == 3

    @patch("shutil.rmtree")
    @patch("sp.config.SP_SYSTEM")
    @patch("sp.config.SP_VENV")
    @patch("sp.config.SP_SIGNALPILOT")
    @patch("sp.config.SP_HOME")
    def test_install_force_preserves_user_data(
        self,
        mock_home: MagicMock,
        mock_signalpilot: MagicMock,
        mock_venv: MagicMock,
        mock_system: MagicMock,
        mock_rmtree: MagicMock,
    ) -> None:
        """Test that force only removes system directories."""
        mock_home.exists.return_value = True

        # Mock the directory paths with .name attributes
        mock_signalpilot.exists.return_value = True
        mock_signalpilot.name = ".signalpilot"
        mock_venv.exists.return_value = True
        mock_venv.name = ".venv"
        mock_system.exists.return_value = True
        mock_system.name = "system"

        result = runner.invoke(app, ["install", "--force"], input="y\n")

        assert result.exit_code == 0
        assert "User notebooks, skills, and rules will be preserved" in result.stdout

        # Verify we only removed system directories
        removed_paths = [call[0][0] for call in mock_rmtree.call_args_list]
        assert mock_signalpilot in removed_paths
        assert mock_venv in removed_paths
        assert mock_system in removed_paths
