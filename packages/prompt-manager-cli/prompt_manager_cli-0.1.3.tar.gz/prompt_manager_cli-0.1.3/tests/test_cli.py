"""Tests for CLI commands."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from prompt_manager_cli.cli import app
from prompt_manager_cli.utils import DEFAULT_TEMPLATE

runner = CliRunner()


class TestNewCommand:
    """Tests for the 'new' command."""

    def test_creates_directory_if_missing(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "prompts"
        assert not output_dir.exists()

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        assert output_dir.exists()

    def test_creates_file_with_correct_name_format(self, tmp_path):
        """Test that created file has correct naming format."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc1234"):
                result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        files = list(output_dir.glob("prompt-*.md"))
        assert len(files) == 1
        filename = files[0].name
        assert filename.startswith("prompt-")
        assert "-abc1234.md" in filename

    def test_creates_file_with_correct_content(self, tmp_path):
        """Test that created file has correct template content."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        files = list(output_dir.glob("prompt-*.md"))
        content = files[0].read_text()

        assert "---" in content
        assert "created_at:" in content
        assert "git_hash:" in content
        assert "cwd:" in content
        assert "# Goal" in content
        assert "# Context" in content
        assert "# Constraints" in content
        assert "# Acceptance criteria" in content

    def test_uses_default_directory(self, tmp_path):
        """Test that default directory is .pm/prompts/."""
        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new"])

        assert result.exit_code == 0
        expected_dir = tmp_path / ".pm" / "prompts"
        assert expected_dir.exists()
        files = list(expected_dir.glob("prompt-*.md"))
        assert len(files) == 1

    def test_handles_filename_collision(self, tmp_path):
        """Test that collision handling works correctly."""
        output_dir = tmp_path / "prompts"
        output_dir.mkdir(parents=True)

        # Create files with same timestamp pattern
        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                # First file
                result1 = runner.invoke(app, ["new", "--dir", str(output_dir)])
                assert result1.exit_code == 0

                # Second file (should get -2 suffix since same minute)
                result2 = runner.invoke(app, ["new", "--dir", str(output_dir)])
                assert result2.exit_code == 0

        all_files = list(output_dir.glob("prompt-*.md"))
        assert len(all_files) == 2
        filenames = [f.name for f in all_files]
        assert any("-2.md" in name for name in filenames)

    def test_prints_success_message(self, tmp_path):
        """Test that success message is printed."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        assert "Created:" in result.output

    def test_opens_editor_from_argument(self, tmp_path):
        """Test that editor argument opens the specified editor."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                    result = runner.invoke(app, ["new", "micro", "--dir", str(output_dir)])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "micro"
        assert call_args[1].endswith(".md")

    def test_opens_editor_from_local_config(self, tmp_path):
        """Test that editor is read from .pm/editor."""
        output_dir = tmp_path / "prompts"
        pm_dir = tmp_path / ".pm"
        pm_dir.mkdir()
        (pm_dir / "editor").write_text("code")

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                    result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "code"

    def test_local_config_takes_precedence_over_env(self, tmp_path):
        """Test that .pm/editor takes precedence over $PM_EDITOR."""
        output_dir = tmp_path / "prompts"
        pm_dir = tmp_path / ".pm"
        pm_dir.mkdir()
        (pm_dir / "editor").write_text("micro")

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                with patch.dict(os.environ, {"PM_EDITOR": "vim"}):
                    with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                        result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "micro"

    def test_editor_argument_takes_precedence(self, tmp_path):
        """Test that editor argument takes precedence over config."""
        output_dir = tmp_path / "prompts"
        pm_dir = tmp_path / ".pm"
        pm_dir.mkdir()
        (pm_dir / "editor").write_text("vim")

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                    result = runner.invoke(app, ["new", "nano", "--dir", str(output_dir)])

        assert result.exit_code == 0
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "nano"

    def test_falls_back_to_environment_variable(self, tmp_path):
        """Test that PM_EDITOR is used if no config exists."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                with patch.dict(os.environ, {"PM_EDITOR": "micro"}):
                    with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                        result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "micro"

    def test_shows_tip_when_no_editor_configured(self, tmp_path):
        """Test that a tip is shown when no editor is configured."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                # Clear PM_EDITOR environment variable
                env = {k: v for k, v in os.environ.items() if k != "PM_EDITOR"}
                with patch.dict(os.environ, env, clear=True):
                    with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                        result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        mock_run.assert_not_called()
        assert "Tip:" in result.output

    def test_nogit_hash_when_not_in_repo(self, tmp_path):
        """Test that 'nogit' is used when not in a git repository."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="nogit"):
                result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        files = list(output_dir.glob("prompt-*-nogit.md"))
        assert len(files) == 1

        content = files[0].read_text()
        assert 'git_hash: "nogit"' in content


class TestInitCommand:
    """Tests for the 'init' command."""

    def test_creates_template_file(self, tmp_path):
        """Test that pm init creates .pm/template.md."""
        template_file = tmp_path / ".pm" / "template.md"
        assert not template_file.exists()

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert template_file.exists()
        assert template_file.read_text() == DEFAULT_TEMPLATE
        assert "Created:" in result.output

    def test_does_not_overwrite_existing_template(self, tmp_path):
        """Test that pm init does not overwrite existing template."""
        pm_dir = tmp_path / ".pm"
        pm_dir.mkdir()
        template_file = pm_dir / "template.md"
        custom_content = "# My Custom Template"
        template_file.write_text(custom_content)

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert template_file.read_text() == custom_content
        assert "Already exists:" in result.output

    def test_creates_pm_directory_if_missing(self, tmp_path):
        """Test that pm init creates .pm directory if it doesn't exist."""
        pm_dir = tmp_path / ".pm"
        assert not pm_dir.exists()

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["init"])

        assert result.exit_code == 0
        assert pm_dir.exists()
