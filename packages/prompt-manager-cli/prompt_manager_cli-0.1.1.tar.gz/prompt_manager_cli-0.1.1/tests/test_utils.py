"""Tests for utility functions."""

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from prompt_manager_cli.utils import (
    DEFAULT_TEMPLATE,
    find_template,
    format_iso_timestamp,
    generate_filename,
    get_git_short_hash,
    load_template,
    render_template,
    resolve_unique_filepath,
)


class TestGetGitShortHash:
    """Tests for get_git_short_hash function."""

    def test_returns_hash_in_git_repo(self):
        """Test that we get a hash when in a git repo."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "a1b2c3d\n"
            mock_run.return_value.returncode = 0
            result = get_git_short_hash()
            assert result == "a1b2c3d"
            mock_run.assert_called_once_with(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )

    def test_returns_nogit_when_not_in_repo(self):
        """Test that we get 'nogit' when not in a git repository."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(128, "git")
            result = get_git_short_hash()
            assert result == "nogit"

    def test_returns_nogit_when_git_not_installed(self):
        """Test that we get 'nogit' when git is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = get_git_short_hash()
            assert result == "nogit"


class TestGenerateFilename:
    """Tests for generate_filename function."""

    def test_generates_correct_format(self):
        """Test filename format is correct."""
        dt = datetime(2026, 1, 5, 14, 37, 0)
        result = generate_filename(dt, "a1b2c3d")
        assert result == "prompt-2026-01-05-14-37-a1b2c3d.md"

    def test_with_nogit_hash(self):
        """Test filename with nogit hash."""
        dt = datetime(2026, 1, 5, 14, 37, 0)
        result = generate_filename(dt, "nogit")
        assert result == "prompt-2026-01-05-14-37-nogit.md"

    def test_pads_single_digit_values(self):
        """Test that single digit month/day/hour/minute are zero-padded."""
        dt = datetime(2026, 1, 5, 9, 5, 0)
        result = generate_filename(dt, "abc123")
        assert result == "prompt-2026-01-05-09-05-abc123.md"


class TestResolveUniqueFilepath:
    """Tests for resolve_unique_filepath function."""

    def test_returns_base_path_when_no_collision(self, tmp_path):
        """Test that we get the base path when there's no collision."""
        result = resolve_unique_filepath(tmp_path, "prompt-2026-01-05-14-37-abc.md")
        assert result == tmp_path / "prompt-2026-01-05-14-37-abc.md"

    def test_appends_suffix_on_collision(self, tmp_path):
        """Test that we get -2 suffix when file exists."""
        # Create existing file
        (tmp_path / "prompt-2026-01-05-14-37-abc.md").touch()

        result = resolve_unique_filepath(tmp_path, "prompt-2026-01-05-14-37-abc.md")
        assert result == tmp_path / "prompt-2026-01-05-14-37-abc-2.md"

    def test_increments_suffix_for_multiple_collisions(self, tmp_path):
        """Test that suffix increments for multiple collisions."""
        # Create existing files
        (tmp_path / "prompt-2026-01-05-14-37-abc.md").touch()
        (tmp_path / "prompt-2026-01-05-14-37-abc-2.md").touch()
        (tmp_path / "prompt-2026-01-05-14-37-abc-3.md").touch()

        result = resolve_unique_filepath(tmp_path, "prompt-2026-01-05-14-37-abc.md")
        assert result == tmp_path / "prompt-2026-01-05-14-37-abc-4.md"


class TestFormatIsoTimestamp:
    """Tests for format_iso_timestamp function."""

    def test_formats_with_timezone(self):
        """Test that ISO timestamp includes timezone offset."""
        tz = timezone.utc
        dt = datetime(2026, 1, 5, 14, 37, 0, tzinfo=tz)
        result = format_iso_timestamp(dt)
        assert result == "2026-01-05T14:37:00+00:00"

    def test_excludes_microseconds(self):
        """Test that microseconds are not included."""
        tz = timezone.utc
        dt = datetime(2026, 1, 5, 14, 37, 0, 123456, tzinfo=tz)
        result = format_iso_timestamp(dt)
        assert "123456" not in result
        assert result == "2026-01-05T14:37:00+00:00"


class TestFindTemplate:
    """Tests for find_template function."""

    def test_returns_none_when_no_template_exists(self, tmp_path):
        """Test that None is returned when no template exists."""
        with patch("prompt_manager_cli.utils.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.utils.Path.home", return_value=tmp_path / "home"):
                result = find_template()
        assert result is None

    def test_finds_local_template(self, tmp_path):
        """Test that local template is found."""
        local_pm_dir = tmp_path / ".pm"
        local_pm_dir.mkdir()
        local_template = local_pm_dir / "template.md"
        local_template.write_text("# Local Template")

        with patch("prompt_manager_cli.utils.Path.cwd", return_value=tmp_path):
            result = find_template()

        assert result == local_template

    def test_finds_global_template(self, tmp_path):
        """Test that global template is found when no local exists."""
        home_dir = tmp_path / "home"
        global_pm_dir = home_dir / ".pm"
        global_pm_dir.mkdir(parents=True)
        global_template = global_pm_dir / "template.md"
        global_template.write_text("# Global Template")

        with patch("prompt_manager_cli.utils.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.utils.Path.home", return_value=home_dir):
                result = find_template()

        assert result == global_template

    def test_local_template_takes_precedence(self, tmp_path):
        """Test that local template is preferred over global."""
        # Create local template
        local_pm_dir = tmp_path / ".pm"
        local_pm_dir.mkdir()
        local_template = local_pm_dir / "template.md"
        local_template.write_text("# Local Template")

        # Create global template
        home_dir = tmp_path / "home"
        global_pm_dir = home_dir / ".pm"
        global_pm_dir.mkdir(parents=True)
        global_template = global_pm_dir / "template.md"
        global_template.write_text("# Global Template")

        with patch("prompt_manager_cli.utils.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.utils.Path.home", return_value=home_dir):
                result = find_template()

        assert result == local_template


class TestLoadTemplate:
    """Tests for load_template function."""

    def test_returns_default_when_no_custom_template(self, tmp_path):
        """Test that default template is returned when no custom exists."""
        with patch("prompt_manager_cli.utils.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.utils.Path.home", return_value=tmp_path / "home"):
                result = load_template()

        assert result == DEFAULT_TEMPLATE

    def test_loads_custom_template(self, tmp_path):
        """Test that custom template content is loaded."""
        local_pm_dir = tmp_path / ".pm"
        local_pm_dir.mkdir()
        custom_content = "# Custom\n{created_at}\n{git_hash}\n{cwd}"
        (local_pm_dir / "template.md").write_text(custom_content)

        with patch("prompt_manager_cli.utils.Path.cwd", return_value=tmp_path):
            result = load_template()

        assert result == custom_content


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_renders_default_template(self):
        """Test that default template renders correctly."""
        result = render_template(
            template=DEFAULT_TEMPLATE,
            created_at="2026-01-05T14:37:00+01:00",
            git_hash="a1b2c3d",
            cwd="/home/user/project",
        )
        assert "---" in result
        assert 'created_at: "2026-01-05T14:37:00+01:00"' in result
        assert 'git_hash: "a1b2c3d"' in result
        assert 'cwd: "/home/user/project"' in result
        assert "# Goal" in result
        assert "# Context" in result
        assert "# Constraints" in result
        assert "# Acceptance criteria" in result

    def test_renders_custom_template(self):
        """Test that custom template renders correctly."""
        custom_template = "Date: {created_at}\nHash: {git_hash}\nDir: {cwd}"
        result = render_template(
            template=custom_template,
            created_at="2026-01-05T14:37:00+01:00",
            git_hash="abc123",
            cwd="/projects/myapp",
        )
        assert result == "Date: 2026-01-05T14:37:00+01:00\nHash: abc123\nDir: /projects/myapp"
