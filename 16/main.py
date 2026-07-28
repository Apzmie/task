# main.py
import argparse

from config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
)

from git_utils import (
    get_git_status,
    get_git_diff,
    get_current_branch,
    get_changed_file_count,
    get_diff_line_count,
)

from prompt import (
    build_commit_prompt,
    build_pr_prompt,
)

from ai_client import (
    generate_commit,
    generate_pr,
)


def print_header(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def check_changes():
    """
    Git 변경사항 확인
    """
    status = get_git_status()

    if not status:
        print("[INFO] 변경 사항이 없습니다.")
        return None

    return status


def run_commit(args):
    """
    커밋 메시지 생성 실행
    """

    status = check_changes()

    if status is None:
        return

    diff = get_git_diff()

    print(
        f"[INFO] Git status 수집 완료: "
        f"{get_changed_file_count()}개 파일 변경 감지"
    )

    print(
        f"[INFO] Git diff 수집 완료: "
        f"{get_diff_line_count()}줄"
    )

    print("[INFO] Gemini API 요청 중...")

    prompt = build_commit_prompt(
        status,
        diff
    )

    result = generate_commit(
        prompt,
        model=args.model,
        temperature=args.temperature,
        max_output_tokens=args.max_tokens
    )

    print_header("Commit Message")

    print(result)

    print("=" * 50)


def run_pr(args):
    """
    PR 초안 생성 실행
    """

    status = check_changes()

    if status is None:
        return

    diff = get_git_diff()
    branch = get_current_branch()

    print(f"[INFO] 현재 브랜치: {branch}")

    print(
        f"[INFO] Git diff 수집 완료: "
        f"{get_diff_line_count()}줄"
    )

    print("[INFO] Gemini API 요청 중...")

    prompt = build_pr_prompt(
        status,
        diff,
        branch
    )

    result = generate_pr(
        prompt,
        model=args.model,
        temperature=args.temperature,
        max_output_tokens=args.max_tokens
    )

    print_header("Pull Request Draft")

    print(result)

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="AI Git Commit / PR Generator"
    )

    parser.add_argument(
        "command",
        choices=["commit", "pr"],
        help="생성할 결과 선택"
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Gemini 모델"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help="AI 생성 다양성"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        dest="max_tokens",
        help="최대 출력 토큰"
    )

    args = parser.parse_args()

    try:
        if args.command == "commit":
            run_commit(args)

        elif args.command == "pr":
            run_pr(args)

    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()