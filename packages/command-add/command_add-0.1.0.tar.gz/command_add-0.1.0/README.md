# command-add

Add Claude Code slash commands from GitHub to your project.

This is a convenience wrapper for [skill-add](https://pypi.org/project/skill-add/) that provides a cleaner CLI experience.

## Installation

```bash
uvx command-add <username>/<command-name>
```

Or install globally:

```bash
uv tool install command-add
```

## Usage

```bash
# Add a command to current project
command-add <username>/<command-name>

# Overwrite existing command
command-add <username>/<command-name> --overwrite

# Install globally (~/.claude/commands/)
command-add <username>/<command-name> --global
```

The tool fetches slash commands from the user's `agent-skills` repository on GitHub and installs them to `.claude/commands/` in your project.
# command-add
