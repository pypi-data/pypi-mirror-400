from pathlib import Path

import click

from pyrems.utils import build_validation_on_errors, get_commands_file_path
from pyrems.validation import RemsValidator


def needs_csv_path(*, check_exists: bool = False, check_file: bool = False):
    def callback(ctx, _param, value):
        csv_path = Path(value) if value else get_commands_file_path()
        if check_exists or check_file:
            on_errors = build_validation_on_errors('list', click.echo)
            (
                RemsValidator(raises=click.BadParameter, on_errors=on_errors)
                .csv_file_exists(csv_path)
                .csv_file_is_file(csv_path if check_file else csv_path)
                .execute()
            )
        ctx.params['csv_path'] = csv_path
        return csv_path

    return click.option(
        '--csv-path',
        type=click.Path(path_type=Path),
        default=None,
        help='Path to the CSV file (defaults to XDG: ~/.local/share/rems/commands.csv)',
        callback=callback,
    )
