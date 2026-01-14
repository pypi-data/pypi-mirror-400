from pathlib import Path

import click

from pyrems.cli.decorators import needs_csv_path
from pyrems.handlers import handle_install, handle_list, handle_store, handle_select
from pyrems.utils import build_validation_on_errors
from pyrems.validation import RemsValidator


@click.group()
def cli():
    """
    pyrems - Remember and search your bash commands.
    
    Use the 'rems' bash function (installed via 'pyrems install') to search
    and select commands interactively with automatic bash history integration.
    """
    pass


@cli.command()
@needs_csv_path(check_exists=True, check_file=True)
@click.option('-c', '--clipboard', is_flag=True, help='Copy selected command to clipboard using xclip')
@click.option('-s', '--silent', is_flag=True, help='Silent mode - skip displaying command details after selection')
@click.option('-n', '--limit', default=20, help='Number of recent commands to display (default: 20)')
def select(csv_path: Path, clipboard: bool, silent: bool, limit: int):
    """
    Search and select a saved command using fzf.
    
    This command is called by the 'rems' bash function. The selected command
    will be printed to stdout as the first line, followed by usage information.
    
    The bash wrapper function automatically adds the selected command to your
    bash history using 'history -s', making it accessible via UP arrow or !!.
    
    Examples:
    
      pyrems select              Search and select a command
      
      pyrems select -c           Copy selected command to clipboard
      
      pyrems select -s           Silent mode (no info message)
      
      pyrems select -n 50        Search through last 50 commands
    """
    on_errors = build_validation_on_errors('select', click.echo)
    validator = RemsValidator(raises=click.BadParameter, on_errors=on_errors).limit_positive(limit).csv_file_exists(csv_path).csv_file_is_file(csv_path).fzf_installed()
    
    if clipboard:
        validator.xclip_installed()
    
    validator.execute()
    
    handle_select(csv_path, limit, clipboard, silent, click.echo)


@cli.command()
@needs_csv_path()
@click.argument('command')
@click.option('--note', default='', help='Optional note describing what the command does')
def store(csv_path: Path, command: str, note: str) -> None:
    """
    Store a bash command with an optional note.
    
    If the command already exists, it updates the hit counter and note.
    Otherwise, it creates a new entry with hit counter set to 1.
    
    This command is typically called by the 'rem' bash function rather than
    directly. To use it interactively:
    
      1. Run any bash command
      2. Type: rem
      3. Or with a note: rem "your note here"
    
    Examples:
    
      pyrems store "tar -xvf file.tar.gz" --note "Extract tar archive"
      
      pyrems store "npm run dev"
    """
    on_errors = build_validation_on_errors('store', click.echo)
    RemsValidator(raises=click.BadParameter, on_errors=on_errors).command_not_empty(command).parent_directory_writable(csv_path).execute()
    
    handle_store(csv_path, command, note)
    click.echo(f'Command stored: {command}')


@cli.command()
@needs_csv_path(check_exists=True, check_file=True)
@click.option('--limit', default=20, help='Number of commands to display (default: 20)')
def list(csv_path: Path, limit: int) -> None:
    """
    Display all saved commands in a formatted table.
    
    Commands are ordered by usage (hit count) and date, showing the most
    frequently and recently used commands first.
    
    The table displays:
      - Command: The bash command
      - Note: Your description of what it does
      - Date: Last used date
      - Hits: Number of times you've selected this command
    
    Examples:
    
      pyrems list                List last 20 commands (default)
      
      pyrems list --limit 50     List last 50 commands
    """
    on_errors = build_validation_on_errors('list', click.echo)
    RemsValidator(raises=click.BadParameter, on_errors=on_errors).limit_positive(limit).execute()
    
    handle_list(csv_path, limit, click.echo)


@cli.command()
@needs_csv_path()
def install(csv_path: Path) -> None:
    """
    Initialize rems and create the 'rem' bash function.
    
    This command:
      1. Creates the commands storage file
      2. Provides instructions to add the 'rem' bash function to your ~/.bashrc
    
    After installation, you'll be able to use:
      - 'rem' to save the last command you ran
      - 'rem "note"' to save the last command with a description
      - 'rems' to search and recall saved commands
    
    Run this command once to set up rems on your system.
    
    Example:
    
      pyrems install
      
    Then follow the displayed instructions to complete the setup.
    """
    on_errors = build_validation_on_errors('install', click.echo)
    RemsValidator(raises=click.BadParameter, on_errors=on_errors).csv_file_not_exists(csv_path).rem_function_not_exists().parent_directory_writable(csv_path).execute()
    
    handle_install(csv_path, click.echo)
