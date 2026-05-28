#__main__.py
import argparse
import sys
import uuid  # 유일한 ID 생성을 위한 파이썬 표준 라이브러리
import csv
import os
import time
from functools import wraps

# 우리가 방금 만든 모델과 검증 함수 가져오기
from budget_app.models import Transaction, validate_date, validate_type, validate_amount, validate_category
from budget_app.repository import DataRepository

# 임시 카테고리 목록 (다음 단계에서 파일 저장으로 바뀔 예정입니다)
EXISTING_CATEGORIES = ["food", "transport", "rent", "salary", "etc"]

# 1. 데코레이터 정의
def time_and_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"\n🚀 [LOG] '{func.__name__}' 명령어가 실행됩니다.")
        
        result = func(*args, **kwargs)  # 실제 함수 실행
        
        end_time = time.time()
        print(f"⏱️ [LOG] '{func.__name__}' 실행 완료 (소요시간: {end_time - start_time:.4f}초)")
        return result
    return wrapper

# ==========================================
# 1. 명령어별 실행 함수 (프린트문으로 정상 작동 체크)
# ==========================================
# 📌 repo 인자를 받도록 변경하여 파일 데이터를 직접 다룹니다.
def handle_add(repo: DataRepository):
    print("\n--- [대화형] 새로운 거래 추가 ---")
    
    # 📌 실시간으로 파일에서 등록된 카테고리 목록 가져오기
    existing_categories = repo.load_categories()
    
    # 1. 날짜 입력 및 검증
    while True:
        date = input("날짜(YYYY-MM-DD): ").strip()
        if validate_date(date):
            break
        print("[오류] 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).")
        print("[힌트] 예: 2026-05-27 처럼 대시(-)를 포함해 정확한 날짜를 입력하세요.\n")

    # 2. 타입 입력 및 검증
    while True:
        tx_type = input("타입(income/expense): ").strip()
        if validate_type(tx_type):
            break
        print("[오류] 타입은 'income' 또는 'expense'만 가능합니다.")
        print("[힌트] 수입은 income, 지출은 expense를 입력하세요.\n")

    # 3. 카테고리 입력 및 검증
    while True:
        category = input(f"카테고리 ({', '.join(existing_categories)}): ").strip()
        if validate_category(category, existing_categories):
            break
        print(f"[오류] 존재하지 않는 카테고리입니다: '{category}'")
        print(f"[힌트] 현재 등록된 카테고리 중에서 입력하세요.\n")

    # 4. 금액 입력 및 검증
    while True:
        amount_raw = input("금액(양수 정수): ").strip()
        amount = validate_amount(amount_raw)
        if amount is not None:
            break
        print("[오류] 금액은 0보다 큰 양수 정수여야 합니다.")
        print("[힌트] 콤마(,) 없이 숫자만 입력하세요. 예: 15000\n")

    # 5. 선택 사항 입력
    memo = input("메모(선택, 없으면 엔터): ").strip()
    tags = input("태그(쉼표로 구분, 없으면 엔터): ").strip()

    # 6. ID 생성 및 모델 생성
    tx_id = f"TX-{uuid.uuid4().hex[:6].upper()}"
    new_tx = Transaction(
        id=tx_id, type=tx_type, date=date, amount=amount,
        category=category, memo=memo, tags=tags
    )

    # 📌 7. [핵심] 파일에 실제 데이터 영구 저장하기
    # dataclass를 딕셔너리로 쉽게 바꾸기 위해 __dict__를 사용합니다.
    repo.save_transaction(new_tx.__dict__)

    print(f"\n[저장 완료] id={new_tx.id}")
    print(f"상세 정보: {new_tx.date} | {new_tx.type} | {new_tx.category} | {new_tx.amount}원 | {new_tx.memo}")

@time_and_log
def handle_list(args, repo: DataRepository):
    print(f"\n--- 거래 목록 조회 (list) ---")
    print(f"[안내] 최신순으로 최대 {args.limit}개의 데이터를 출력합니다.\n")
    print("-" * 70)
    print(f"{'거래 ID':<10} | {'날짜':<10} | {'타입':<8} | {'카테고리':<10} | {'금액':<10} | {'메모'}")
    print("-" * 70)

    # 레포지토리의 제너레이터 가져오기
    tx_stream = repo.load_transactions_backward()
    
    count = 0
    for tx in tx_stream:
        # 사용자가 요청한 limit 개수만큼만 출력하고 멈춥니다.
        if count >= args.limit:
            break
            
        # 데이터 출력 포맷 맞추기
        tx_id = tx.get("id", "")
        date = tx.get("date", "")
        tx_type = tx.get("type", "")
        category = tx.get("category", "")
        amount = tx.get("amount", 0)
        memo = tx.get("memo", "")
        
        print(f"{tx_id:<10} | {date:<10} | {tx_type:<8} | {category:<10} | {amount:<10,} | {memo}")
        count += 1

    if count == 0:
        print("[안내] 등록된 거래 내역이 없습니다.")
    print("-" * 70)

def handle_search(args, repo: DataRepository):
    print("\n--- 거래 검색 (search) ---")
    print("[안내] 조건에 맞는 최신 거래 내역을 검색합니다.\n")

    # 레포지토리에서 파일 뒤에서부터 한 줄씩 읽어오는 제너레이터 가져오기
    tx_stream = repo.load_transactions_backward()
    
    print("-" * 75)
    print(f"{'거래 ID':<10} | {'날짜':<10} | {'타입':<8} | {'카테고리':<10} | {'금액':<10} | {'메모'}")
    print("-" * 75)

    count = 0

    # 파일 끝에서부터 한 줄씩 꺼내서 조건 검사 시작!
    for tx in tx_stream:
        # 1. 기간 필터링 (--from, --to)
        # 내역의 날짜가 사용자가 지정한 시작일보다 전이거나, 종료일보다 후라면 탈락!
        if args.from_date and tx.get("date") < args.from_date:
            continue
        if args.to_date and tx.get("date") > args.to_date:
            continue

        # 2. 타입 필터링 (--type: income/expense)
        if args.type and tx.get("type") != args.type:
            continue

        # 3. 카테고리 필터링 (--category)
        if args.category and tx.get("category") != args.category:
            continue

        # 4. 메모 키워드 검색 (--q)
        # 사용자가 입력한 검색어가 메모에 포함되어 있지 않으면 탈락!
        if args.q and args.q not in tx.get("memo", ""):
            continue

        # 5. 태그 검색 (--tag)
        # 내역에 적힌 태그 문자열에 사용자가 찾는 태그가 없으면 탈락!
        if args.tag and args.tag not in tx.get("tags", ""):
            continue

        # --- 모든 까다로운 조건을 통과한 데이터만 아래에서 출력됩니다! ---
        tx_id = tx.get("id", "")
        date = tx.get("date", "")
        tx_type = tx.get("type", "")
        category = tx.get("category", "")
        amount = tx.get("amount", 0)
        memo = tx.get("memo", "")
        
        print(f"{tx_id:<10} | {date:<10} | {tx_type:<8} | {category:<10} | {amount:<10,} | {memo}")
        count += 1

    if count == 0:
        print("[안내] 조건에 일치하는 거래 내역이 없습니다.")
    else:
        print(f"\n[검색 완료] 총 {count}건의 내역을 찾았습니다.")
    print("-" * 75)

def handle_summary(args, repo: DataRepository):
    target_month = args.month.strip()
    top_n = args.top

    print(f"\n--- 월별 요약 및 보고서 (summary) ---")
    print(f"[조회 월]: {target_month} | [지출 상위 카테고리]: TOP {top_n}\n")

    total_income = 0
    total_expense = 0
    category_expenses = {}

    tx_stream = repo.load_transactions_backward()
    has_data = False

    for tx in tx_stream:
        date = tx.get("date", "")
        if date[:7] != target_month:
            continue

        has_data = True
        tx_type = tx.get("type", "")
        amount = tx.get("amount", 0)
        category = tx.get("category", "")

        if tx_type == "income":
            total_income += amount
        elif tx_type == "expense":
            total_expense += amount
            if category in category_expenses:
                category_expenses[category] += amount
            else:
                category_expenses[category] = amount

    if not has_data:
        print(f"[안내] {target_month} 월은 등록된 가계부 데이터가 없습니다.")
        return

    balance = total_income - total_expense

    # 📌 [여기서부터 수정/추가되는 핵심 예산 연동 로직]
    # 해당 월에 설정된 예산이 있는지 레포지토리에서 불러옵니다.
    budget_amount = repo.get_budget_by_month(target_month)

    print("=" * 45)
    print(f"총 수입 : {total_income:,}원")
    print(f"총 지출 : {total_expense:,}원")
    print(f"잔   액 : {balance:,}원")
    
    # 예산 데이터가 존재하는 경우에만 사용률과 경고를 출력합니다.
    if budget_amount is not None:
        # 사용률 계산 (지출 / 예산 * 100)
        if budget_amount > 0:
            usage_rate = (total_expense / budget_amount) * 100
        else:
            usage_rate = 0.0
            
        print(f"예   산 : {budget_amount:,}원 (사용률 {usage_rate:.1f}%)")
        
        # 만약 지출이 예산을 초과했다면 경고 메시지를 띄웁니다!
        if total_expense > budget_amount:
            over_amount = total_expense - budget_amount
            print(f"🚨 [경고] 설정한 예산을 {over_amount:,}원 초과했습니다!")
    else:
        print("예   산 : 설정된 예산이 없습니다.")
    print("=" * 45)

    # (이하 지출 TOP N 출력 코드는 이전과 동일)
    print(f"\n[지출 TOP {top_n} 카테고리]")
    if not category_expenses:
        print("지출 내역이 없습니다.")
    else:
        sorted_categories = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
        for index, (cat_name, cat_amount) in enumerate(sorted_categories[:top_n], start=1):
            print(f"{index}) {cat_name:<10} {cat_amount:,}원")
    print("=" * 45)

def handle_budget(args, repo: DataRepository):
    # budget set 명령어 처리
    if args.subcommand == "set":
        month = args.month.strip()
        amount = args.amount

        # 금액 음수 검증
        if amount <= 0:
            print("[오류] 예산 금액은 0보다 큰 양수 정수여야 합니다.")
            sys.exit(1)

        # 레포지토리에 예산 저장 요청
        repo.save_budget(month, amount)
        print(f"\n[저장 완료] {month} 예산 {amount:,}원")

def handle_category(args, repo: DataRepository):
    action = args.action  # "add", "list", "remove" 중 하나
    
    # 현재 파일에 등록된 카테고리 목록 불러오기
    categories = repo.load_categories()

    # ---- (1) 카테고리 목록 조회 (list) ----
    if action == "list":
        print("\n--- 등록된 카테고리 목록 ---")
        if not categories:
            print("[안내] 등록된 카테고리가 없습니다.")
        else:
            for cat in categories:
                print(f"- {cat}")
        print("-" * 30)

    # ---- (2) 카테고리 추가 (add) ----
    elif action == "add":
        print("\n--- 카테고리 추가 ---")
        name = input("추가할 카테고리명 입력: ").strip()
        
        if not name:
            print("[오류] 카테고리명은 빈칸으로 둘 수 없습니다.")
            sys.exit(1)
            
        if name in categories:
            print(f"[오류] '{name}'은 이미 존재하는 카테고리입니다.")
            sys.exit(1)
            
        # 기존 목록에 새 카테고리 추가 후 저장
        categories.append(name)
        repo.save_categories(categories)
        print(f"\n[저장 완료] category={name}")

    # ---- (3) 카테고리 삭제 (remove) ----
    elif action == "remove":
        print("\n--- 카테고리 삭제 ---")
        name = input("삭제할 카테고리명 입력: ").strip()
        
        if name not in categories:
            print(f"[오류] 존재하지 않는 카테고리입니다: '{name}'")
            print("[힌트] 'python -m budget_app category list'로 정확한 이름을 확인하세요.")
            sys.exit(1)
            
        # 📌 [핵심 안전장치] 가계부 내역 파일에서 이 카테고리를 쓰고 있는지 검사!
        if repo.is_category_used(name):
            print(f"[삭제 불가] '{name}' 카테고리를 사용하는 가계부 거래 내역이 존재합니다.")
            print("[힌트] 해당 카테고리가 지정된 거래들을 먼저 수정(update)하거나 삭제(delete)한 뒤 시도하세요.")
            sys.exit(1)
            
        # 사용 중이 아니라면 안전하게 삭제 진행
        categories.remove(name)
        repo.save_categories(categories)
        print(f"\n[삭제 완료] category={name} 가 정상적으로 제거되었습니다.")

def handle_update(repo: DataRepository):
    print("\n--- [대화형] 거래 수정 (update) ---")
    tx_id = input("수정할 거래 ID 입력: ").strip()
    
    # 1. 존재하는 ID인지 먼저 조회
    tx = repo.find_transaction_by_id(tx_id)
    if not tx:
        print(f"[오류] 입력하신 ID '{tx_id}'는 존재하지 않는 데이터입니다.")
        print("[힌트] 정확한 ID를 다시 입력하거나 목록(list)을 먼저 확인하세요.\n")
        sys.exit(1)
        
    print(f"\n[기존 데이터 발견] 수정하지 않고 넘어가려면 그냥 [엔터]를 누르세요.")
    print(f"기존 정보: {tx['date']} | {tx['type']} | {tx['category']} | {tx['amount']}원 | {tx['memo']}")
    print("-" * 50)

    # 2. 날짜 수정 입력 및 검증
    while True:
        date_input = input(f"날짜 ({tx['date']}): ").strip()
        if not date_input:  # 엔터만 치면 기존 값 유지
            break
        if validate_date(date_input):
            tx['date'] = date_input
            break
        print("[오류] 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).")

    # 3. 타입 수정 입력 및 검증
    while True:
        type_input = input(f"타입 (income/expense) ({tx['type']}): ").strip()
        if not type_input:
            break
        if validate_type(type_input):
            tx['type'] = type_input
            break
        print("[오류] 타입은 'income' 또는 'expense'만 가능합니다.")

    # 4. 카테고리 수정 입력 및 검증
    existing_categories = repo.load_categories()
    while True:
        cat_input = input(f"카테고리 ({tx['category']}): ").strip()
        if not cat_input:
            break
        if validate_category(cat_input, existing_categories):
            tx['category'] = cat_input
            break
        print(f"[오류] 존재하지 않는 카테고리입니다. 등록된 카테고리: {', '.join(existing_categories)}")

    # 5. 금액 수정 입력 및 검증
    while True:
        amount_input = input(f"금액 ({tx['amount']}): ").strip()
        if not amount_input:
            break
        amount_valid = validate_amount(amount_input)
        if amount_valid is not None:
            tx['amount'] = amount_valid
            break
        print("[오류] 금액은 0보다 큰 양수 정수여야 합니다.")

    # 6. 메모 및 태그 수정
    memo_input = input(f"메모 ({tx['memo']}): ").strip()
    if memo_input:
        tx['memo'] = memo_input
        
    tags_input = input(f"태그 ({tx['tags']}): ").strip()
    if tags_input:
        tx['tags'] = tags_input

    # 7. 실제 파일에 업데이트 반영
    repo.update_transaction(tx)
    print(f"\n[수정 완료] id={tx_id} 데이터가 안전하게 변경되었습니다.")

def handle_delete(args, repo: DataRepository):
    print("\n--- 거래 삭제 (delete) ---")
    tx_id = args.id.strip()
    
    # 레포지토리에 삭제 요청
    success = repo.delete_transaction(tx_id)
    
    if success:
        print(f"[삭제 완료] ID가 '{tx_id}'인 거래 내역이 안전하게 삭제되었습니다.")
    else:
        print(f"[오류] 입력하신 ID '{tx_id}'는 존재하지 않는 데이터입니다.")
        print("[힌트] 'python -m budget_app list' 명령어로 정확한 ID를 확인해 보세요.\n")
        sys.exit(1)

def handle_import(args, repo: DataRepository):
    from_file = args.from_file.strip()
    print(f"\n--- CSV 가져오기 (import) ---")
    
    if not os.path.exists(from_file):
        print(f"[오류] 가져올 CSV 파일이 해당 경로에 존재하지 않습니다: {from_file}")
        sys.exit(1)

    existing_categories = repo.load_categories()
    valid_transactions = []
    skipped_count = 0
    imported_count = 0

    with open(from_file, "r", encoding="utf-8") as f:
        # csv.DictReader는 첫 줄의 헤더를 기준으로 데이터를 딕셔너리로 예쁘게 파싱해 줍니다.
        reader = csv.DictReader(f)
        
        for index, row in enumerate(reader, start=2):  # 헤더가 1번 줄이므로 데이터는 2번 줄부터 시작
            # 필수값 양식 받아오기
            date = row.get("date", "").strip()
            tx_type = row.get("type", "").strip()
            category = row.get("category", "").strip()
            amount_raw = row.get("amount", "").strip()
            memo = row.get("memo", "").strip()
            tags = row.get("tags", "").strip()

            # 📌 [안전망] 필수 데이터 유효성 일괄 검증
            if not validate_date(date) or not validate_type(tx_type) or not validate_category(category, existing_categories):
                skipped_count += 1
                continue
                
            amount = validate_amount(amount_raw)
            if amount is None:
                skipped_count += 1
                continue

            # 검증을 통과한 데이터는 시스템용 고유 ID를 새로 부여하여 담습니다.
            tx_id = f"TX-IMP{uuid.uuid4().hex[:4].upper()}"
            new_tx = {
                "id": tx_id,
                "type": tx_type,
                "date": date,
                "amount": amount,
                "category": category,
                "memo": memo,
                "tags": tags
            }
            valid_transactions.append(new_tx)
            imported_count += 1

    # 검증이 끝난 정상 데이터들을 파일에 일괄 누적 저장
    if valid_transactions:
        repo.save_transactions_bulk(valid_transactions)

    print(f"[완료] imported={imported_count}, skipped={skipped_count}")

def handle_export(args, repo: DataRepository):
    out_file = args.out.strip()
    print(f"\n--- CSV 내보내기 (export) ---")
    print(f"[안내] 지정된 조건의 가계부 데이터를 {out_file} 파일로 저장합니다.")

    # 1. CSV 헤더(컬럼명) 규칙 고정
    headers = ["date", "type", "category", "amount", "memo", "tags"]
    
    # 2. 파일 뒤에서부터 한 줄씩 읽는 제너레이터 연결
    tx_stream = repo.load_transactions_backward()
    
    count = 0
    is_first_row = True

    for tx in tx_stream:
        date = tx.get("date", "")
        
        # [조건 검증 1] --month 조건이 있을 때 맞지 않으면 탈락!
        if args.month and date[:7] != args.month.strip():
            continue
            
        # [조건 검증 2] --from, --to 기간 조건이 있을 때 범위를 벗어나면 탈락!
        if args.from_date and date < args.from_date.strip():
            continue
        if args.to_date and date > args.to_date.strip():
            continue

        # 모든 조건을 통과했다면 CSV에 담을 데이터 순서 정렬
        row = [
            tx.get("date"),
            tx.get("type"),
            tx.get("category"),
            tx.get("amount"),
            tx.get("memo", ""),
            tx.get("tags", "")
        ]
        
        # 처음 쓸 때는 헤더를 먼저 포함하여 내보냅니다.
        if is_first_row:
            repo.append_to_csv(out_file, headers, is_first=True)
            is_first_row = False
            
        # 데이터 행 쓰기 (스트리밍 유지)
        repo.append_to_csv(out_file, row, is_first=False)
        count += 1

    if count == 0:
        print(f"[안내] 해당 조건에 맞는 데이터가 없어 CSV 파일이 생성되지 않았습니다.")
    else:
        print(f"[완료] {out_file} ({count} records)")


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

    # 📌 사용자가 지정한 폴더(--data-dir)를 기반으로 저장소 실행 및 초기화 진행
    repo = DataRepository(args.data_dir)

    # 명령어 분기 처리
    if args.command == "add":
        handle_add(repo)
    elif args.command == "list":
        handle_list(args, repo)
    elif args.command == "search":
        handle_search(args, repo)
    elif args.command == "summary":
        handle_summary(args, repo)
    elif args.command == "budget":
        handle_budget(args, repo)
    elif args.command == "category":
        handle_category(args, repo)  # 📌 여기에 repo를 추가로 전달해 줍니다.
    elif args.command == "update":
        handle_update(repo)      # 📌 repo를 넘겨주도록 수정
    elif args.command == "delete":
        handle_delete(args, repo)  # 📌 args와 repo를 둘 다 넘겨주도록 수정
    elif args.command == "import":
        handle_import(args, repo)  # 📌 repo 추가
    elif args.command == "export":
        if not args.month and not (args.from_date and args.to_date):
            print("[오류] export는 --month 또는 --from과 --to 조건이 필수로 필요합니다.", file=sys.stderr)
            sys.exit(1)
        handle_export(args, repo)  # 📌 repo 추가

if __name__ == "__main__":
    main()
