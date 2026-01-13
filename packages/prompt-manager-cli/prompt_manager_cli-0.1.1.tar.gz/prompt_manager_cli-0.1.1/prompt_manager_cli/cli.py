"""CLI for prompt-manager-cli."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from prompt_manager_cli.utils import (
    DEFAULT_TEMPLATE,
    format_iso_timestamp,
    generate_filename,
    get_git_short_hash,
    get_local_timestamp,
    load_template,
    render_template,
    resolve_unique_filepath,
)

app = typer.Typer(
    name="pm",
    help="A CLI tool to create and organize prompt files for code agents.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()

DEFAULT_DIR = ".pm/prompts"


def get_editor() -> Optional[str]:
    """Get the configured editor.

    Priority:
    1. .pm/editor (local/repo config)
    2. $PM_EDITOR environment variable
    """
    # Check local config
    local_editor = Path.cwd() / ".pm" / "editor"
    if local_editor.is_file():
        editor = local_editor.read_text().strip()
        if editor:
            return editor

    # Fall back to environment variable
    return os.environ.get("PM_EDITOR")


@app.callback()
def callback() -> None:
    """A CLI tool to create and organize prompt files for code agents."""
    pass


@app.command("init")
def init() -> None:
    """Initialize .pm directory with default template."""
    try:
        pm_dir = Path.cwd() / ".pm"
        template_file = pm_dir / "template.md"

        if template_file.exists():
            console.print(f"[yellow]Already exists:[/yellow] {template_file}")
            raise typer.Exit(code=0)

        pm_dir.mkdir(parents=True, exist_ok=True)
        template_file.write_text(DEFAULT_TEMPLATE)
        console.print(f"[green]Created:[/green] {template_file}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


@app.command("new")
def new(
    editor: Optional[str] = typer.Argument(
        None,
        help="Editor to open the file with. Overrides config and environment.",
    ),
    dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help=f"Output directory for the prompt file. Default: {DEFAULT_DIR}",
    ),
) -> None:
    """Create a new prompt file and open it in your editor."""
    try:
        # Determine output directory
        output_dir = Path(dir) if dir else Path.cwd() / DEFAULT_DIR

        # Ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get timestamp and git hash
        now = get_local_timestamp()
        git_hash = get_git_short_hash()

        # Generate filename and resolve collisions
        base_filename = generate_filename(now, git_hash)
        filepath = resolve_unique_filepath(output_dir, base_filename)

        # Load template and render content
        template = load_template()
        content = render_template(
            template=template,
            created_at=format_iso_timestamp(now),
            git_hash=git_hash,
            cwd=str(Path.cwd().absolute()),
        )
        filepath.write_text(content)

        # Print success message
        console.print(f"[green]Created:[/green] {filepath}")

        # Determine editor: argument > config > environment
        resolved_editor = editor or get_editor()

        # Open in editor
        if resolved_editor:
            subprocess.run([resolved_editor, str(filepath)])
        else:
            console.print(
                "[dim]Tip: Set your editor in .pm/editor or $PM_EDITOR[/dim]"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold red")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
