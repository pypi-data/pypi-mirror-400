import os
from pathlib import Path
from typing import Callable

from pyrems.managers.system_manager import check_fzf_installed, check_xclip_installed, check_rem_function_exists


class ValidationError(Exception):
    pass


def validate_command_not_empty(command: str) -> None:
    if not command or command.strip() == '':
        raise ValidationError('Command cannot be empty')


def validate_limit_positive(limit: int) -> None:
    if limit <= 0:
        raise ValidationError('Limit must be a positive integer')


def validate_csv_file_exists(file_path: Path) -> None:
    if not file_path.exists():
        raise ValidationError(f'CSV file does not exist: {file_path}')


def validate_csv_file_is_file(file_path: Path) -> None:
    if not file_path.is_file():
        raise ValidationError(f'Path is not a file: {file_path}')


def validate_csv_file_not_exists(file_path: Path) -> None:
    if file_path.exists():
        raise ValidationError(f'Commands file already exists at: {file_path}')


def validate_fzf_installed() -> None:
    if not check_fzf_installed():
        raise ValidationError('fzf is not installed. Install it with: sudo apt install fzf (Ubuntu) or brew install fzf (macOS)')


def validate_xclip_installed() -> None:
    if not check_xclip_installed():
        raise ValidationError('xclip is not installed. Install it with: sudo apt install xclip')


def validate_rem_function_not_exists() -> None:
    if check_rem_function_exists():
        raise ValidationError('rem/rems bash functions are already installed')


def validate_parent_directory_writable(file_path: Path) -> None:
    parent_dir = file_path.parent

    if parent_dir.exists():
        if not parent_dir.is_dir():
            raise ValidationError(f'Parent path exists but is not a directory: {parent_dir}')
        if not os.access(parent_dir, os.W_OK):
            raise ValidationError(f'Parent directory is not writable: {parent_dir}')
    else:
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise ValidationError(f'Cannot create parent directory {parent_dir}: {e}')


class RemsValidator:
    def __init__(
        self,
        raises: type[Exception],
        on_errors: Callable[[list[BaseException]], None] | None,
    ):
        self._raises = raises
        self._on_errors = on_errors
        self._errors: list[BaseException] = []

    def command_not_empty(self, command: str):
        try:
            validate_command_not_empty(command)
        except ValidationError as e:
            self._errors.append(e)
        return self

    def limit_positive(self, limit: int):
        try:
            validate_limit_positive(limit)
        except ValidationError as e:
            self._errors.append(e)
        return self

    def csv_file_exists(self, file_path: Path):
        try:
            validate_csv_file_exists(file_path)
        except ValidationError as e:
            self._errors.append(e)
        return self

    def csv_file_is_file(self, file_path: Path):
        try:
            validate_csv_file_is_file(file_path)
        except ValidationError as e:
            self._errors.append(e)
        return self

    def csv_file_not_exists(self, file_path: Path):
        try:
            validate_csv_file_not_exists(file_path)
        except ValidationError as e:
            self._errors.append(e)
        return self

    def fzf_installed(self):
        try:
            validate_fzf_installed()
        except ValidationError as e:
            self._errors.append(e)
        return self

    def xclip_installed(self):
        try:
            validate_xclip_installed()
        except ValidationError as e:
            self._errors.append(e)
        return self

    def rem_function_not_exists(self):
        try:
            validate_rem_function_not_exists()
        except ValidationError as e:
            self._errors.append(e)
        return self

    def parent_directory_writable(self, file_path: Path):
        try:
            validate_parent_directory_writable(file_path)
        except ValidationError as e:
            self._errors.append(e)
        return self

    def execute(self) -> None:
        if not self._errors:
            return

        if self._on_errors:
            self._on_errors(self._errors)

        raise self._raises(ExceptionGroup('Validation failed', self._errors))
