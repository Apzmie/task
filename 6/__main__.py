import argparse
import sys

# ==========================================
# 1. 명령어별 실행 함수 (프린트문으로 정상 작동 체크)
# ==========================================

def handle_add():
    print("\n--- [대화형] 거래 추가 (add) ---")
    date = input("날짜(YYYY-MM-DD): ").strip()
    tx_type = input("타입(income/expense): ").strip()
    category = input("카테고리: ").strip()
    amount = input("금액(양수): ").strip()
    memo = input("메모(선택): ").strip()
    tags = input("태그(쉼표 구분, 선택): ").strip()
    print(f"[체크] 입력받은 값: {date}, {tx_type}, {category}, {amount}원")

def handle_list(args):
    print(f"\n--- 거래 목록 조회 (list) ---")
    print(f"[옵션 확인] 조회 제한 개수(--limit): {args.limit}")

def handle_search(args):
    print("\n--- 거래 검색 (search) ---")
    print(f"[옵션 확인] 시작일(--from): {args.from_date}")
    print(f"[옵션 확인] 종료일(--to): {args.to_date}")
    print(f"[옵션 확인] 카테고리(--category): {args.category}")
    print(f"[옵션 확인] 타입(--type): {args.type}")
    print(f"[옵션 확인] 메모 검색어(--q): {args.q}")
    print(f"[옵션 확인] 태그(--tag): {args.tag}")

def handle_summary(args):
    print("\n--- 월별 요약 및 보고서 (summary) ---")
    print(f"[옵션 확인] 조회 월(--month): {args.month}")
    print(f"[옵션 확인] 상위 N개(--top): {args.top}")

def handle_budget(args):
    print("\n--- 예산 설정 (budget set) ---")
    print(f"[옵션 확인] 설정 월(--month): {args.month}")
    print(f"[옵션 확인] 예산 금액(--amount): {args.amount}")

def handle_category(args):
    print(f"\n--- 카테고리 관리 (category {args.action}) ---")
    if args.action in ["add", "remove"]:
        name = input("카테고리명 입력: ").strip()
        print(f"[대화형 확인] 입력한 카테고리명: {name}")

def handle_update():
    print("\n--- [대화형] 거래 수정 (update) ---")
    tx_id = input("수정할 거래 ID 입력: ").strip()
    print(f"[대화형 확인] 입력한 ID: {tx_id} (이후 수정 필드를 대화형으로 진행)")

def handle_delete(args):
    print("\n--- 거래 삭제 (delete) ---")
    print(f"[옵션 확인] 삭제할 거래 ID(--id): {args.id}")

def handle_import(args):
    print("\n--- CSV 가져오기 (import) ---")
    print(f"[옵션 확인] 파일 경로(--from): {args.from_file}")

def handle_export(args):
    print("\n--- CSV 내보내기 (export) ---")
    print(f"[옵션 확인] 저장할 파일명(--out): {args.out}")
    print(f"[옵션 확인] 조회 월(--month): {args.month}")
    print(f"[옵션 확인] 시작일(--from): {args.from_date}")
    print(f"[옵션 확인] 종료일(--to): {args.to_date}")


# ==========================================
# 2. CLI 메인 제어부 (argparse 완벽 설정)
# ==========================================

def main():
    parser = argparse.ArgumentParser(
        description="파일 기반 가계부 콘솔 프로그램",
        prog="python -m budget_app"
    )
    # 공통 옵션: 데이터 저장 디렉토리 지정 (-data-dir은 요구사항 반영하되 리눅스 표준인 --data-dir로 세팅)
    parser.add_argument("--data-dir", default="./data", help="데이터 저장 폴더 경로 (기본값: ./data)")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="실행할 명령어를 선택하세요.")

    # (1) add
    subparsers.add_parser("add", help="새로운 거래를 추가합니다. (대화형)")

    # (2) list
    list_p = subparsers.add_parser("list", help="거래 목록을 조회합니다.")
    list_p.add_argument("--limit", type=int, default=10, help="조회할 최신 거래 개수 (기본값: 10)")

    # (3) search
    search_p = subparsers.add_parser("search", help="조건에 맞는 거래를 검색합니다.")
    search_p.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    search_p.add_argument("--to", dest="to_date", help="종료 날짜 (YYYY-MM-DD)")
    search_p.add_argument("--category", help="카테고리 지정")
    search_p.add_argument("--type", choices=["income", "expense"], help="타입 지정 (income/expense)")
    search_p.add_argument("--q", help="메모 키워드 검색")
    search_p.add_argument("--tag", help="태그 검색")

    # (4) summary
    summary_p = subparsers.add_parser("summary", help="월별 요약 및 카테고리 리포트를 출력합니다.")
    summary_p.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
    summary_p.add_argument("--top", type=int, default=3, help="지출 상위 N개 카테고리 (기본값: 3)")

    # (5) budget
    budget_p = subparsers.add_parser("budget", help="예산을 설정합니다.")
    budget_sub = budget_p.add_subparsers(dest="subcommand", required=True)
    b_set_p = budget_sub.add_parser("set", help="월 예산을 저장합니다.")
    b_set_p.add_argument("--month", required=True, help="예산 월 (YYYY-MM)")
    b_set_p.add_argument("--amount", type=int, required=True, help="예산 금액 (양수 정수)")

    # (6) category
    cat_p = subparsers.add_parser("category", help="카테고리를 관리합니다.")
    cat_p.add_argument("action", choices=["add", "list", "remove"], help="수행할 작업 (add/list/remove)")

    # (7) update
    subparsers.add_parser("update", help="기존 거래를 수정합니다. (대화형)")

    # (8) delete
    delete_p = subparsers.add_parser("delete", help="특정 거래를 삭제합니다.")
    delete_p.add_argument("--id", required=True, help="삭제할 거래 ID")

    # (9) import
    import_p = subparsers.add_parser("import", help="CSV 파일에서 거래를 일괄 등록합니다.")
    import_p.add_argument("--from", dest="from_file", required=True, help="가져올 CSV 파일 경로")

    # (10) export
    export_p = subparsers.add_parser("export", help="조건에 맞는 거래를 CSV로 저장합니다.")
    export_p.add_argument("--out", required=True, help="내보낼 CSV 파일 경로")
    export_p.add_argument("--month", help="지정 월 (YYYY-MM)")
    export_p.add_argument("--from", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    export_p.add_argument("--to", dest="to_date", help="종료 날짜 (YYYY-MM-DD)")

    # 인자 분석
    args = parser.parse_args()

    # 명령어 분기 처리
    if args.command == "add":
        handle_add()
    elif args.command == "list":
        handle_list(args)
    elif args.command == "search":
        handle_search(args)
    elif args.command == "summary":
        handle_summary(args)
    elif args.command == "budget":
        handle_budget(args)
    elif args.command == "category":
        handle_category(args)
    elif args.command == "update":
        handle_update()
    elif args.command == "delete":
        handle_delete(args)
    elif args.command == "import":
        handle_import(args)
    elif args.command == "export":
        # export의 필수 조건 검증 (month 혹은 from/to 중 하나는 있어야 함)
        if not args.month and not (args.from_date and args.to_date):
            print("[오류] export는 --month 또는 --from과 --to 조건이 필수로 필요합니다.", file=sys.stderr)
            sys.exit(1)
        handle_export(args)

if __name__ == "__main__":
    main()
