"""Utility functions for prompt-manager-cli."""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_TEMPLATE = '''---
created_at: "{created_at}"
git_hash: "{git_hash}"
cwd: "{cwd}"
---

# Goal

# Context

# Constraints

# Acceptance criteria
'''


def get_git_short_hash() -> str:
    """Get the short git hash of the current repo HEAD.

    Returns 'nogit' if not in a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "nogit"


def get_local_timestamp() -> datetime:
    """Get the current local timestamp with timezone info."""
    return datetime.now().astimezone()


def format_iso_timestamp(dt: datetime) -> str:
    """Format datetime as ISO 8601 with timezone offset."""
    return dt.isoformat(timespec="seconds")


def generate_filename(dt: datetime, git_hash: str) -> str:
    """Generate the base filename (without collision suffix).

    Format: prompt-YYYY-MM-DD-HH-MM-<git_hash>.md
    """
    time_part = dt.strftime("%Y-%m-%d-%H-%M")
    return f"prompt-{time_part}-{git_hash}.md"


def resolve_unique_filepath(directory: Path, base_filename: str) -> Path:
    """Find a unique filepath, adding -2, -3, etc. suffix if needed."""
    filepath = directory / base_filename
    if not filepath.exists():
        return filepath

    # Remove .md extension for suffix handling
    stem = base_filename[:-3]  # Remove ".md"
    counter = 2

    while True:
        new_filename = f"{stem}-{counter}.md"
        filepath = directory / new_filename
        if not filepath.exists():
            return filepath
        counter += 1


def find_template() -> Optional[Path]:
    """Find a custom template file.

    Search order:
    1. .pm/template.md in current directory (local/repo template)
    2. ~/.pm/template.md (global template)

    Returns None if no custom template is found.
    """
    # Check local template first
    local_template = Path.cwd() / ".pm" / "template.md"
    if local_template.is_file():
        return local_template

    # Check global template
    global_template = Path.home() / ".pm" / "template.md"
    if global_template.is_file():
        return global_template

    return None


def load_template() -> str:
    """Load the template content.

    Uses custom template if found, otherwise returns default.
    """
    template_path = find_template()
    if template_path:
        return template_path.read_text()
    return DEFAULT_TEMPLATE


def render_template(template: str, created_at: str, git_hash: str, cwd: str) -> str:
    """Render a template with the given variables."""
    return template.format(created_at=created_at, git_hash=git_hash, cwd=cwd)
