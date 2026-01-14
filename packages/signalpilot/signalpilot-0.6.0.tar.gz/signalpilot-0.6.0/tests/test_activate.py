"""Tests for sp activate command."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from sp.main import app

runner = CliRunner()


class TestActivate:
    """Test suite for sp activate command."""

    @patch("sp.commands.activate.is_running_in_uvx")
    def test_activate_not_in_uvx(self, mock_uvx: MagicMock) -> None:
        """Test that activate fails when not running in uvx."""
        mock_uvx.return_value = False

        result = runner.invoke(app, ["activate"])

        assert result.exit_code == 1
        assert "uvx sp-cli activate" in result.stdout

    @patch("sp.commands.activate.is_running_in_uvx")
    @patch("sp.commands.activate.Path.home")
    def test_activate_creates_wrapper(
        self, mock_home: MagicMock, mock_uvx: MagicMock, tmp_path: Path
    ) -> None:
        """Test that activate creates wrapper script."""
        mock_uvx.return_value = True
        mock_home.return_value = tmp_path

        # Mock shell rc files to prevent actual modification
        bashrc = tmp_path / ".bashrc"
        bashrc.write_text("# existing bashrc\n")

        result = runner.invoke(app, ["activate"])

        assert result.exit_code == 0

        # Check wrapper script was created
        sp_wrapper = tmp_path / ".local" / "bin" / "sp"
        assert sp_wrapper.exists()
        assert sp_wrapper.stat().st_mode & 0o111  # Executable

        # Check wrapper content
        content = sp_wrapper.read_text()
        assert "#!/bin/sh" in content
        assert "uvx sp-cli" in content

    @patch("sp.commands.activate.is_running_in_uvx")
    @patch("sp.commands.activate.Path.home")
    def test_activate_updates_shell_rc(
        self, mock_home: MagicMock, mock_uvx: MagicMock, tmp_path: Path
    ) -> None:
        """Test that activate updates shell rc files."""
        mock_uvx.return_value = True
        mock_home.return_value = tmp_path

        # Create shell rc files
        bashrc = tmp_path / ".bashrc"
        bashrc.write_text("# bashrc\n")

        zshrc = tmp_path / ".zshrc"
        zshrc.write_text("# zshrc\n")

        result = runner.invoke(app, ["activate"])

        assert result.exit_code == 0

        # Check PATH was added to both files
        assert ".local/bin" in bashrc.read_text()
        assert ".local/bin" in zshrc.read_text()

    @patch("sp.commands.activate.is_running_in_uvx")
    @patch("sp.commands.activate.Path.home")
    def test_activate_idempotent_path(
        self, mock_home: MagicMock, mock_uvx: MagicMock, tmp_path: Path
    ) -> None:
        """Test that activate doesn't duplicate PATH entries."""
        mock_uvx.return_value = True
        mock_home.return_value = tmp_path

        # Create shell rc with PATH already set
        bashrc = tmp_path / ".bashrc"
        bashrc.write_text('export PATH="$HOME/.local/bin:$PATH"\n')

        result = runner.invoke(app, ["activate"])

        assert result.exit_code == 0

        # Verify PATH wasn't duplicated
        content = bashrc.read_text()
        assert content.count(".local/bin") == 1

    @patch("sp.commands.activate.is_running_in_uvx")
    @patch("sp.commands.activate.Path.home")
    def test_activate_success_message(
        self, mock_home: MagicMock, mock_uvx: MagicMock, tmp_path: Path
    ) -> None:
        """Test that activate shows success message with next steps."""
        mock_uvx.return_value = True
        mock_home.return_value = tmp_path

        # Create minimal shell rc
        (tmp_path / ".bashrc").write_text("")

        result = runner.invoke(app, ["activate"])

        assert result.exit_code == 0
        assert "SignalPilot CLI installed!" in result.stdout
        assert "sp init" in result.stdout
        assert "source" in result.stdout
