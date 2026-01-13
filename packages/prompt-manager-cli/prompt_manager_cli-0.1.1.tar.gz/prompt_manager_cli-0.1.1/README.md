# prompt-manager-cli

A CLI tool to create and organize prompt files for code agents (Claude Code, Codex, Gemini CLI, etc.).

## Installation

```bash
pip install prompt-manager-cli
```

Or install in editable mode for development:

```bash
pip install -e ".[dev]"
```

## Usage

### Initialize a project

```bash
pm init
```

This creates `.pm/template.md` with the default template. Edit this file to customize your prompts.

### Create a new prompt file

```bash
pm new
```

This creates a new Markdown file in `.pm/prompts/` and opens it in your editor.

```
prompt-2026-01-05-14-37-a1b2c3d.md
```

You can specify the editor directly:

```bash
pm new micro
pm new code
pm new vim
```

### Options

```bash
# Specify a custom output directory
pm new --dir ./my-prompts

# Combine editor and directory
pm new micro --dir ./my-prompts
```

## Editor Configuration

The editor is resolved in this order:

1. **Command argument**: `pm new micro`
2. **Local config**: `.pm/editor` (per-repo)
3. **Environment**: `$PM_EDITOR` (global)

To set your default editor, add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export PM_EDITOR="micro"
```

To override per-project:

```bash
echo "code" > .pm/editor
```

## Custom Templates

Run `pm init` to create `.pm/template.md` with the default template, then edit it to customize your prompts.

You can also create a global template at `~/.pm/template.md` for use across all projects. Local templates take precedence over global templates.

### Template Variables

Templates use Python's string formatting. Available variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{created_at}` | ISO 8601 timestamp with timezone | `2026-01-05T14:37:00+01:00` |
| `{git_hash}` | Short git hash or "nogit" | `a1b2c3d` |
| `{cwd}` | Absolute path to current directory | `/home/user/project` |

### Example Custom Template

```markdown
---
date: "{created_at}"
commit: "{git_hash}"
project: "{cwd}"
---

## What I Want

## Background

## Requirements

## Done When
```

## Local Development

Run directly without installing:

```bash
python -m prompt_manager_cli new
```

Run tests:

```bash
pytest
```

## License

MIT
