import subprocess
import sys


def check_fzf_installed() -> bool:
    try:
        subprocess.run(
            ['fzf', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_fzf_selection(input_text: str, prompt: str) -> str:
    result = subprocess.run(
        [
            'fzf',
            f'--prompt={prompt}',
            '--height=40%',
            '--reverse',
            '--border',
        ],
        input=input_text,
        text=True,
        capture_output=True,
    )

    if result.returncode == 0:
        return result.stdout.strip()

    return ''


def check_xclip_installed() -> bool:
    try:
        subprocess.run(
            ['xclip', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def copy_to_clipboard(text: str) -> None:
    subprocess.run(
        ['xclip', '-selection', 'clipboard'],
        input=text,
        text=True,
        check=True,
    )


def append_command_to_history(command: str) -> None:
    print(command)
    sys.stdout.flush()


def check_rem_function_exists() -> bool:
    rem_result = subprocess.run(
        ['bash', '-c', 'declare -F rem'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    rems_result = subprocess.run(
        ['bash', '-c', 'declare -F rems'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return rem_result.returncode == 0 or rems_result.returncode == 0


