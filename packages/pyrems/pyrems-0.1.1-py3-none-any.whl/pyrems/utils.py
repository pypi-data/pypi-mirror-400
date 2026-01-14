from pathlib import Path
from typing import Callable
from functools import partial


def get_commands_file_path() -> Path:
    data_dir = Path.home() / '.local' / 'share' / 'rems'
    return data_dir / 'commands.csv'


def _on_errors_impl(command_hint: str, sh: Callable[[str], None], errors: list[BaseException]) -> None:
    messages: list[str] = []
    for err in errors:
        text = str(err).strip()
        if not text:
            continue
        for line in text.splitlines():
            line = line.strip()
            if line:
                messages.append(line)

    count = len(messages) if messages else len(errors)
    sh(f'{count} Validation errors in {command_hint} command:')
    for msg in messages if messages else (str(e) for e in errors):
        sh(f'- {msg}')


def build_validation_on_errors(command_hint: str, sh: Callable[[str], None]) -> Callable[[list[BaseException]], None]:
    return partial(_on_errors_impl, command_hint, sh)
