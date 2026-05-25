import argparse

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
    search_parser.add_argument("--from-date", dest="from_date", help="시작 날짜 (YYYY-MM-DD)") # --from은 파썬 예약어 문제 방지를 위해 내부에선 from_date로 매핑
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
    # 아래 옵션 중 하나 이상 필수 체크는 서비스 레이어 혹은 파싱 후 로직에서 처리
    export_parser.add_argument("--month", help="내보낼 월 (YYYY-MM)")
    export_parser.add_argument("--from-date", dest="from_date", help="시작 날짜 (YYYY-MM-DD)")
    export_parser.add_argument("--to", help="종료 날짜 (YYYY-MM-DD)")

    # 인자 파싱
    args = parser.parse_args()

    # 4. 명령어 분기 처리
    if args.command == "add":
        print("[안내] 대화형 입력을 시작합니다.")
        date = input("날짜(YYYY-MM-DD): ")
        type_ = input("타입(income/expense): ")
        category = input("카테고리: ")
        amount = input("금액(양수): ")
        memo = input("메모(선택): ")
        tags = input("태그(쉼표로 구분, 없으면 엔터): ")
        print(f"[저장 완료] 입력된 값: {date}, {type_}, {category}, {amount}, {memo}, {tags}")

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
