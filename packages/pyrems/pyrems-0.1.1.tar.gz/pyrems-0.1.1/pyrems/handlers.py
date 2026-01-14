from pathlib import Path
import textwrap
from typing import Callable
from datetime import datetime

from rich.console import Console
from rich.table import Table

from pyrems.core import build_list_header, generate_rem_bash_function
from pyrems.managers.records_manager import (
    CommandRecord,
    build_fzf_input_from_records,
    create_empty_csv,
    extract_command_from_fzf_selection,
    get_command_record,
    increment_command_hits,
    list_commands_from_file,
    store_command_in_file,
)
from pyrems.managers.system_manager import (
    append_command_to_history,
    copy_to_clipboard,
    run_fzf_selection,
)

def handle_store(csv_path: Path, command: str, note: str) -> None:
    store_command_in_file(csv_path, command, note)


def format_commands_table(records: list[CommandRecord]) -> Table:
    table = Table(show_header=True)
    table.add_column('Command', no_wrap=False)
    table.add_column('Note')
    table.add_column('Date')
    table.add_column('Hits', justify='right')

    for record in records:
        table.add_row(
            record.command,
            record.note,
            record.date,
            str(record.hits)
        )

    return table


def get_file_last_modified(file_path: Path) -> str:
    timestamp = file_path.stat().st_mtime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%d.%m.%Y %H:%M')


def handle_list(csv_path: Path, limit: int, sh: Callable[[str], None]) -> None:
    records = list_commands_from_file(csv_path, limit)

    if not records:
        sh('No commands found.')
        return

    last_modified = get_file_last_modified(csv_path)
    header = build_list_header(csv_path, last_modified)
    sh(header)

    table = format_commands_table(records)
    console = Console()
    console.print(table)


def handle_select(csv_path: Path, limit: int, use_clipboard: bool, silent: bool, sh: Callable[[str], None]) -> None:
    records = list_commands_from_file(csv_path, limit)

    if not records:
        sh('No commands found.')
        return

    fzf_input = build_fzf_input_from_records(records)
    selection = run_fzf_selection(fzf_input, 'Search commands: ')

    if not selection:
        return

    command = extract_command_from_fzf_selection(selection)

    increment_command_hits(csv_path, command)

    if use_clipboard:
        copy_to_clipboard(command)
    
    append_command_to_history(command)

    if not silent:
        record = get_command_record(csv_path, command)
        sh('')
        if record.note:
            note_line = f'Note: {record.note}'
        else:
            note_line = ''
        message_parts = [
            note_line,
            f'Uses: {record.hits}',
            f'Last used: {record.date}',
            '',
            'Press UP arrow or use !! to access the command',
        ]
        sh('\n'.join(part for part in message_parts if part != ''))


def handle_install(csv_path: Path, sh: Callable[[str], None]) -> None:
    create_empty_csv(csv_path)
    sh(f'Commands file created at: {csv_path}')

    bash_function = generate_rem_bash_function()
    install_command = f"cat << 'EOF' >> ~/.bashrc\n{bash_function}\nEOF"
    message = textwrap.dedent(
        f"""
        
        {'=' * 60}
        Welcome to rems - Your Bash Command Memory!
        {'=' * 60}
        
        To complete the installation, add the bash functions:
        
        Run this command:
        
        {install_command}
        
        Then reload your bash configuration:
          source ~/.bashrc
        
        Usage:
          1. Run any command
          2. Type "rem" to save it
          3. Type "rem your note here" to save with a note
          4. Type "rems" to search and recall saved commands
        
        The selected command will be added to your bash history automatically.
        
        Note: To use CLI commands directly, use: pyrems <subcommand>
        Examples: pyrems list, pyrems store "echo test"
        
        Happy command remembering!
        """
    ).rstrip()
    sh(message)
