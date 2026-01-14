# pyrems

A simple Python CLI tool for remembering and managing your bash commands.

## What it does

`pyrems` (Python Remember) helps you save, organize, and quickly access important commands you don't want to lose. Instead of digging through your bash history or losing commands when switching computers, `pyrems` stores your commands with optional notes and tracks how often you use them.

## Key Features

- **Save commands** with notes for future reference
- **Smart storage** - automatically increments hit counter for repeated commands
- **Interactive search** - browse and fuzzy-search your saved commands
- **Persistent across machines** - sync your commands via dotfiles
- **Usage tracking** - see which commands you use most often

## Quick Start

```bash
# Install pyrems
pip install pyrems

# Initialize the tool
pyrems install

# Save a command (add to your .bashrc)
tar -xzvf archive.tar.gz
rem "Extract gzipped tar archive"

# Browse and search saved commands
pyrems

# List all saved commands
pyrems list
```

## Commands

- `pyrems` - Interactive command browser with fuzzy search
- `pyrems store` - Store a command (usually called by the `rem` bash function)
- `pyrems list` - Display all saved commands in a table
- `pyrems install` - Set up configuration and files

