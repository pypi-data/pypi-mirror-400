import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class CommandRecord:
    command: str
    note: str
    date: str
    hits: int


def read_commands(file_path: Path) -> list[CommandRecord]:
    if not file_path.exists():
        return []

    records = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = CommandRecord(
                command=row['COMMAND'],
                note=row['NOTE'],
                date=row['DATE'],
                hits=int(row['NUMBER_OF_HITS'])
            )
            records.append(record)

    return records


def write_commands(file_path: Path, records: list[CommandRecord]) -> None:
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['COMMAND', 'NOTE', 'DATE', 'NUMBER_OF_HITS']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for record in records:
            writer.writerow({
                'COMMAND': record.command,
                'NOTE': record.note,
                'DATE': record.date,
                'NUMBER_OF_HITS': record.hits
            })


def create_empty_csv(file_path: Path) -> None:
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['COMMAND', 'NOTE', 'DATE', 'NUMBER_OF_HITS']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()


def get_today_date() -> str:
    return date.today().isoformat()


def find_command_index(records: list[CommandRecord], command: str) -> int:
    for index, record in enumerate(records):
        if record.command == command:
            return index
    return -1


def update_existing_command(record: CommandRecord, note: str) -> CommandRecord:
    updated_hits = record.hits + 1
    updated_note = note if note else record.note
    updated_date = get_today_date()

    return CommandRecord(
        command=record.command,
        note=updated_note,
        date=updated_date,
        hits=updated_hits
    )


def create_new_command(command: str, note: str) -> CommandRecord:
    return CommandRecord(
        command=command,
        note=note,
        date=get_today_date(),
        hits=1
    )


def store_command_in_file(file_path: Path, command: str, note: str) -> None:
    records = read_commands(file_path)
    command_index = find_command_index(records, command)

    if command_index >= 0:
        existing_record = records[command_index]
        updated_record = update_existing_command(existing_record, note)
        records[command_index] = updated_record
    else:
        new_record = create_new_command(command, note)
        records.append(new_record)

    write_commands(file_path, records)


def sort_commands_by_hits_and_date(records: list[CommandRecord]) -> list[CommandRecord]:
    return sorted(records, key=lambda r: (r.hits, r.date), reverse=True)


def get_top_n_commands(records: list[CommandRecord], limit: int) -> list[CommandRecord]:
    sorted_records = sort_commands_by_hits_and_date(records)
    return sorted_records[:limit]


def list_commands_from_file(file_path: Path, limit: int) -> list[CommandRecord]:
    records = read_commands(file_path)
    return get_top_n_commands(records, limit)


def format_record_for_fzf(record: CommandRecord) -> str:
    note_part = f' [{record.note}]' if record.note else ''
    return f'{record.command}{note_part}'


def build_fzf_input_from_records(records: list[CommandRecord]) -> str:
    lines = [format_record_for_fzf(record) for record in records]
    return '\n'.join(lines)


def extract_command_from_fzf_selection(selection: str) -> str:
    if '[' in selection:
        command_part = selection.split('[')[0].strip()
        return command_part
    return selection.strip()


def increment_command_hits(file_path: Path, command: str) -> None:
    records = read_commands(file_path)
    command_index = find_command_index(records, command)

    if command_index >= 0:
        existing_record = records[command_index]
        updated_record = update_existing_command(existing_record, '')
        records[command_index] = updated_record
        write_commands(file_path, records)


def get_command_record(file_path: Path, command: str) -> CommandRecord:
    records = read_commands(file_path)
    command_index = find_command_index(records, command)

    if command_index >= 0:
        return records[command_index]

    return CommandRecord(command=command, note='', date='', hits=0)


