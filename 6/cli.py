import argparse
from datetime import datetime
from typing import List

# 임시 카테고리 목록 (추후 repository.read_categories() 등으로 대체 가능)
EXISTING_CATEGORIES = ["food", "transport", "rent", "salary", "etc"]


# ==========================================
# 1. 대화형 입력 및 데이터 검증(Validation) 함수군
# ==========================================

def get_valid_date() -> str:
    while True:
        date_str = input("날짜(YYYY-MM-DD): ").strip()
        try:
            # 날짜 형식 및 유효성 검사 (예: 2월 30일 등 차단)
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("[오류] 날짜 형식이 올바르지 않거나 존재하지 않는 날짜입니다.")
            print("[힌트] YYYY-MM-DD 형식으로 입력해주세요. (예: 2026-05-25)")
            print("-" * 40)


def get_valid_type() -> str:
    while True:
        type_str = input("타입(income/expense): ").strip().lower()
        if type_str in ["income", "expense"]:
            return type_str
        print("[오류] 허용되지 않은 타입입니다.")
        print("[힌트] 'income' 또는 'expense'만 입력 가능합니다.")
        print("-" * 40)


def get_valid_category(registered_categories: List[str]) -> str:
    while True:
        category_str = input("카테고리: ").strip()
        if category_str in registered_categories:
            return category_str
        print(f"[오류] 존재하지 않는 카테고리입니다: '{category_str}'")
        print(f"[힌트] 현재 등록된 카테고리: {', '.join(registered_categories)}")
        print("-" * 40)


def get_valid_amount() -> int:
    while True:
        amount_str = input("금액(양수): ").strip()
        try:
            amount = int(amount_str)
            if amount > 0:
                return amount
            print("[오류] 금액은 0보다 커야 합니다.")
        except ValueError:
            print("[오류] 숫자가 아닌 값이 입력되었습니다.")
        print("[힌트] 양의 정수만 입력해주세요. (예: 15000)")
        print("-" * 40)


def get_tags() -> List[str]:
    tags_str = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
    if not tags_str:
        return []
    # 쉼표 분리 후 양끝 공백 제거, 빈 문자열 필터링
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]


# ==========================================
# 2. 메인 CLI 파싱 및 분기 실행 함수
# ==========================================

def parse_args_and_run():
    # 1. 최상위 파서 생성 (--help 자동 지원)
    parser = argparse.ArgumentParser(description="파일 기반 가계부 프로그램 (budget_app)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 2. 대화형 명령어 등록 (add)
    subparsers.add_parser("add", help="거래 내역 추가 (대화형)")

    # 3. 옵션형 명령어 등록 (list)
    list_parser = subparsers.add_parser("list", help="거래 목록 조회")
    list_parser.add_argument("--limit", type=int, default=10, help="조회할 개수 (기본값: 10)")

    # 4. 거래 검색 명령어 등록 (search)
    search_parser = subparsers.add_parser("search", help="조건 기반 거래 검색")
    # --from은 파이썬 예약어(from) 문제 방지를 위해 내부에선 from_date로 매핑
    search_parser.add_argument("--from-date", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    search_parser.add_argument("--to", help="종료 날짜 (YYYY-MM-DD)")
    search_parser.add_argument("--category", help="카테고리 필터")
    search_parser.add_argument("--type", choices=["income", "expense"], help="타입 필터 (income/expense)")
    search_parser.add_argument("--q", help="메모 키워드 검색")
    search_parser.add_argument("--tag", help="태그 필터")

    # 5. 월별 요약 명령어 등록 (summary)
    summary_parser = subparsers.add_parser("summary", help="월별 요약 및 카테고리 리포트")
    summary_parser.add_argument("--month", required=True, help="조회할 월 (YYYY-MM)")
    summary_parser.add_argument("--top", type=int, default=3, help="지출 상위 카테고리 개수 (기본값: 3)")

    # 6. 예산 설정/조회 명령어 등록 (budget)
    budget_parser = subparsers.add_parser("budget", help="월별 예산 설정 및 조회")
    budget_subparsers = budget_parser.add_subparsers(dest="action", required=True)
    
    budget_set_parser = budget_subparsers.add_parser("set", help="예산 설정")
    budget_set_parser.add_argument("--month", required=True, help="설정할 월 (YYYY-MM)")
    budget_set_parser.add_argument("--amount", type=int, required=True, help="예산 금액 (양수 정수)")

    # 7. 카테고리 관리 명령어 등록 (category)
    category_parser = subparsers.add_parser("category", help="카테고리 관리 (add/list/remove)")
    category_subparsers = category_parser.add_subparsers(dest="action", required=True)
    category_subparsers.add_parser("add", help="새로운 카테고리 추가 (대화형)")
    category_subparsers.add_parser("list", help="카테고리 목록 조회")
    category_subparsers.add_parser("remove", help="카테고리 삭제 (대화형)")

    # 8. 거래 수정 명령어 등록 (update) - [안 A: 옵션 기반 방식으로 고정]
    update_parser = subparsers.add_parser("update", help="기존 거래 수정 (옵션 기반)")
    update_parser.add_argument("--id", required=True, help="수정할 거래 ID")
    update_parser.add_argument("--date", help="변경할 날짜 (YYYY-MM-DD)")
    update_parser.add_argument("--type", choices=["income", "expense"], help="변경할 타입 (income/expense)")
    update_parser.add_argument("--category", help="변경할 카테고리")
    update_parser.add_argument("--amount", type=int, help="변경할 금액 (양수 정수)")
    update_parser.add_argument("--memo", help="변경할 메모")
    update_parser.add_argument("--tags", help="변경할 태그 (쉼표 구분)")

    # 9. 거래 삭제 명령어 등록 (delete)
    delete_parser = subparsers.add_parser("delete", help="거래 내역 삭제")
    delete_parser.add_argument("--id", required=True, help="삭제할 거래 ID")

    # 10. 가져오기/내보내기 명령어 등록 (import / export)
    import_parser = subparsers.add_parser("import", help="CSV 파일로부터 거래 가져오기")
    import_parser.add_argument("--from", dest="import_from", required=True, help="가져올 CSV 파일 경로")

    export_parser = subparsers.add_parser("export", help="조건에 맞는 거래를 CSV로 내보내기")
    export_parser.add_argument("--out", required=True, help="내보낼 CSV 파일 경로")
    export_parser.add_argument("--month", help="내보낼 월 (YYYY-MM)")
    export_parser.add_argument("--from-date", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    export_parser.add_argument("--to", help="종료 날짜 (YYYY-MM-DD)")

    # 인자 파싱
    args = parser.parse_args()

    # ------------------------------------------
    # 명령어 분기 및 핵심 비즈니스 로직 연동부
    # ------------------------------------------
    if args.command == "add":
        print("[안내] 대화형 입력을 시작합니다.")
        print("=" * 40)
        
        # 반복 입력 검증기 가동
        date = get_valid_date()
        type_ = get_valid_type()
        category = get_valid_category(EXISTING_CATEGORIES)
        amount = get_valid_amount()
        memo = input("메모(선택): ").strip()
        tags = get_tags()
        
        print("=" * 40)
        # 가상의 생성 ID 결과 (추후 서비스 레이어에서 반환받는 구조로 대체)
        mock_id = "TX-000012" 
        print(f"[저장 완료] id={mock_id}")

    elif args.command == "list":
        print(f"[조회] 최신순으로 {args.limit}개의 목록을 출력합니다 (스트리밍).")

    elif args.command == "search":
        print(f"[검색] 조건에 맞는 데이터를 최신순으로 검색합니다. (from={args.from_date}, to={args.to}, category={args.category}, type={args.type}, q={args.q}, tag={args.tag})")

    elif args.command == "summary":
        print(f"[요약] {args.month} 달의 요약 정보를 출력합니다. (상위 지출 {args.top}개 표시)")

    elif args.command == "budget":
        if args.action == "set":
            print(f"[예산] {args.month} 예산을 {args.amount}원으로 설정합니다.")

    elif args.command == "category":
        if args.action == "add":
            print("[카테고리 추가] 대화형 입력을 시작합니다.")
            cat_name = input("카테고리명: ")
            print(f"[저장 완료] category={cat_name}")
        elif args.action == "list":
            print("[카테고리 목록 출력]")
        elif args.action == "remove":
            print("[카테고리 삭제] 대화형 입력을 시작합니다.")
            cat_name = input("삭제할 카테고리명: ")
            print(f"[삭제 처리] category={cat_name}")

    elif args.command == "update":
        print(f"[수정] ID {args.id}의 항목을 옵션값 기반으로 수정을 시도합니다.")

    elif args.command == "delete":
        print(f"[삭제] ID {args.id}의 항목 수정을 시도합니다.")

    elif args.command == "import":
        print(f"[가져오기] {args.import_from} 파일에서 데이터를 읽어옵니다.")

    elif args.command == "export":
        print(f"[내보내기] 조건에 맞는 데이터를 {args.out} 파일로 저장합니다.")
