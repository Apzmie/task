import argparse

# ⚠️ 여기 함수 이름을 main()에서 parse_args_and_run()으로 변경했습니다!
def parse_args_and_run():
    # 1. 최상위 파서 생성 (--help 자동 지원)
    parser = argparse.ArgumentParser(description="파일 기반 가계부 프로그램")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 2. 대화형 명령어 등록 (add)
    subparsers.add_parser("add", help="거래 내역 추가 (대화형)")

    # 3. 옵션형 명령어 등록 (list) -> 뒤에 --limit 옵션을 붙일 수 있음
    list_parser = subparsers.add_parser("list", help="거래 목록 조회")
    list_parser.add_argument("--limit", type=int, default=10, help="조회할 개수")

    # 인자 파싱
    args = parser.parse_args()

    # 4. 명령어 분기 처리
    if args.command == "add":
        print("[안내] 대화형 입력을 시작합니다.")
        date = input("날짜(YYYY-MM-DD): ")
        amount = input("금액(양수): ")
        print(f"[저장 완료] 입력된 값: {date}, {amount}")

    elif args.command == "list":
        print(f"[조회] 최신순으로 {args.limit}개의 목록을 출력합니다 (스트리밍).")

