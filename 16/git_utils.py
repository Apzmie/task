# git_utils.py
import subprocess


def run_git_command(command):
    """
    Git 명령어를 실행하고 결과를 반환한다.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"[ERROR] Git 명령 실행 실패\n{e.stderr.strip()}"
        )


def get_git_status():
    """
    변경된 파일 목록을 반환한다.
    """
    return run_git_command(["git", "status", "--short"])


def get_git_diff():
    """
    Git diff 내용을 반환한다.
    """
    return run_git_command(["git", "diff"])


def get_current_branch():
    """
    현재 브랜치 이름을 반환한다.
    """
    return run_git_command(
        ["git", "branch", "--show-current"]
    )


def has_changes():
    """
    변경 사항 존재 여부를 확인한다.
    """
    return bool(get_git_status())


def get_changed_file_count():
    """
    변경된 파일 개수를 반환한다.
    """
    status = get_git_status()

    if not status:
        return 0

    return len(status.splitlines())


def get_diff_line_count():
    """
    diff 줄 수를 반환한다.
    """
    diff = get_git_diff()

    if not diff:
        return 0

    return len(diff.splitlines())