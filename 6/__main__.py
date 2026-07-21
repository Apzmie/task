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
def time_and_log(func): # 1. 감쌀 함수를 받아옵니다.
    @wraps(func)        # 2. 원래 함수의 정보를 그대로 유지합니다.
    def wrapper(*args, **kwargs): # 3. 함수 실행 전후에 끼워 넣을 작업을 정의합니다.
        
        # [함수 실행 전 할 일]
        start_time = time.time()
        print(f"\n🚀 [LOG] '{func.__name__}' 명령어가 실행됩니다.")
        
        # [원래 함수 실행]
        result = func(*args, **kwargs) 
        
        # [함수 실행 후 할 일]
        end_time = time.time()
        print(f"⏱️ [LOG] '{func.__name__}' 실행 완료 (소요시간: {end_time - start_time:.4f}초)")
        
        return result # 4. 원래 함수가 내뱉어야 할 결과를 대신 전달합니다.
    return wrapper    # 5. 이제 기능이 추가된 새로운 함수를 돌려줍니다.

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
    # 1. 목록 조회 화면의 제목과 표의 머리글을 출력
    print(f"\n--- 거래 목록 조회 (list) ---")
    print(f"[안내] 최신순으로 최대 {args.limit}개의 데이터를 출력합니다.\n")
    print("-" * 70)
    print(f"{'거래 ID':<10} | {'날짜':<10} | {'타입':<8} | {'카테고리':<10} | {'금액':<10} | {'메모'}")
    print("-" * 70)

    # 2. 저장소에서 최신 거래 내역부터 역순으로 하나씩 가져오는 제너레이터(데이터 통로) 준비
    tx_stream = repo.load_transactions_backward()
    
    count = 0  # 출력한 데이터 개수를 세기 위한 변수
    for tx in tx_stream:
        # 3. 사용자가 요청한 개수(args.limit)만큼 출력했다면 반복문을 즉시 종료
        if count >= args.limit:
            break
            
        # 4. 딕셔너리 데이터에서 각 항목을 추출 (값이 없을 경우 빈 문자열이나 0을 기본값으로 사용)
        tx_id = tx.get("id", "")
        date = tx.get("date", "")
        tx_type = tx.get("type", "")
        category = tx.get("category", "")
        amount = tx.get("amount", 0)
        memo = tx.get("memo", "")
        
        # 5. 형식에 맞춰 출력 (숫자는 1,000 단위 콤마 포함, 각 항목은 지정된 간격으로 정렬)
        print(f"{tx_id:<10} | {date:<10} | {tx_type:<8} | {category:<10} | {amount:<10,} | {memo}")
        count += 1 # 출력한 데이터 개수 1 증가

    # 6. 루프가 끝난 뒤 출력된 데이터가 하나도 없다면 안내 메시지 출력
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
    # 사용자가 보고 싶은 '달(month)'과 '상위 몇 개까지 볼지(top_n)'를 가져옵니다.
    target_month = args.month.strip()
    top_n = args.top

    print(f"\n--- 월별 요약 및 보고서 (summary) ---")
    print(f"[조회 월]: {target_month} | [지출 상위 카테고리]: TOP {top_n}\n")

    # 통계용 변수들을 초기화합니다.
    total_income = 0        # 총 수입
    total_expense = 0       # 총 지출
    category_expenses = {}  # 카테고리별 지출 금액을 담을 사전(dict)

    # 전체 데이터를 최근순으로 하나씩 불러옵니다.
    tx_stream = repo.load_transactions_backward()
    has_data = False        # 데이터가 있는지 확인하는 표시

    for tx in tx_stream:
        date = tx.get("date", "")
        # 조회하려는 달이 아니면 넘어갑니다.
        if date[:7] != target_month:
            continue

        has_data = True
        tx_type = tx.get("type", "")
        amount = tx.get("amount", 0)
        category = tx.get("category", "")

        # 수입인지 지출인지 구분하여 더합니다.
        if tx_type == "income":
            total_income += amount
        elif tx_type == "expense":
            total_expense += amount
            # 카테고리별로 지출 합계를 계산합니다.
            if category in category_expenses:
                category_expenses[category] += amount
            else:
                category_expenses[category] = amount

    # 데이터가 아예 없으면 여기서 종료합니다.
    if not has_data:
        print(f"[안내] {target_month} 월은 등록된 가계부 데이터가 없습니다.")
        return

    # 수입에서 지출을 뺀 잔액을 계산합니다.
    balance = total_income - total_expense

    # [예산 연동] 저장소에서 해당 월의 예산 설정을 불러옵니다.
    budget_amount = repo.get_budget_by_month(target_month)

    print("=" * 45)
    print(f"총 수입 : {total_income:,}원")
    print(f"총 지출 : {total_expense:,}원")
    print(f"잔   액 : {balance:,}원")
    
    # 예산이 설정되어 있을 경우에만 비교 결과를 출력합니다.
    if budget_amount is not None:
        # 예산 대비 몇 퍼센트나 썼는지 계산합니다.
        if budget_amount > 0:
            usage_rate = (total_expense / budget_amount) * 100
        else:
            usage_rate = 0.0
            
        print(f"예   산 : {budget_amount:,}원 (사용률 {usage_rate:.1f}%)")
        
        # 지출이 예산을 넘었는지 확인하고 경고를 줍니다.
        if total_expense > budget_amount:
            over_amount = total_expense - budget_amount
            print(f"🚨 [경고] 설정한 예산을 {over_amount:,}원 초과했습니다!")
    else:
        print("예   산 : 설정된 예산이 없습니다.")
    print("=" * 45)

    # [지출 TOP N 출력] 지출이 많은 순서대로 정리해서 보여줍니다.
    print(f"\n[지출 TOP {top_n} 카테고리]")
    if not category_expenses:
        print("지출 내역이 없습니다.")
    else:
        # 지출 금액(x[1])을 기준으로 내림차순 정렬합니다.
        sorted_categories = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
        # 상위 N개만 뽑아서 출력합니다.
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
    # 가져올 CSV 파일의 경로를 확인합니다.
    from_file = args.from_file.strip()
    print(f"\n--- CSV 가져오기 (import) ---")
    
    # [파일 확인] 경로에 실제 파일이 있는지 먼저 체크합니다. 없으면 프로그램을 종료합니다.
    if not os.path.exists(from_file):
        print(f"[오류] 가져올 CSV 파일이 해당 경로에 존재하지 않습니다: {from_file}")
        sys.exit(1)

    # 미리 카테고리 목록을 불러오고, 통계용 변수를 초기화합니다.
    existing_categories = repo.load_categories()
    valid_transactions = [] # 올바른 데이터만 모아둘 리스트
    skipped_count = 0       # 형식이 맞지 않아 건너뛴 데이터 수
    imported_count = 0      # 성공적으로 가져온 데이터 수

    # CSV 파일을 읽기 모드로 엽니다.
    with open(from_file, "r", encoding="utf-8") as f:
        # csv.DictReader: CSV 파일의 각 줄을 이름표(헤더)가 붙은 딕셔너리로 바꿔줍니다.
        reader = csv.DictReader(f)
        
        # 각 줄을 하나씩 확인합니다. (데이터는 2번째 줄부터 시작한다고 가정)
        for index, row in enumerate(reader, start=2):
            # 파일에서 각 항목의 값을 가져와 정리합니다.
            date = row.get("date", "").strip()
            tx_type = row.get("type", "").strip()
            category = row.get("category", "").strip()
            amount_raw = row.get("amount", "").strip()
            memo = row.get("memo", "").strip()
            tags = row.get("tags", "").strip()

            # [안전망 1] 날짜, 타입, 카테고리가 규칙에 맞는지 검사합니다.
            # 하나라도 틀리면 이 줄은 무시(skip)합니다.
            if not validate_date(date) or not validate_type(tx_type) or not validate_category(category, existing_categories):
                skipped_count += 1
                continue
                
            # [안전망 2] 금액이 숫자로 올바르게 변환되는지 검사합니다.
            amount = validate_amount(amount_raw)
            if amount is None:
                skipped_count += 1
                continue

            # [데이터 정리] 모든 검사를 통과했다면, 시스템에서 쓸 고유한 ID를 부여합니다.
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
            # 검증 완료된 데이터를 리스트에 추가합니다.
            valid_transactions.append(new_tx)
            imported_count += 1

    # [저장] 리스트에 모아둔 정상 데이터들을 한꺼번에 저장소에 저장합니다.
    if valid_transactions:
        repo.save_transactions_bulk(valid_transactions)

    # 최종 결과(성공 수, 실패 수)를 사용자에게 보여줍니다.
    print(f"[완료] imported={imported_count}, skipped={skipped_count}")

def handle_export(args, repo: DataRepository):
    # 사용자가 저장하고 싶은 파일 이름을 가져옵니다.
    out_file = args.out.strip()
    print(f"\n--- CSV 내보내기 (export) ---")
    print(f"[안내] 지정된 조건의 가계부 데이터를 {out_file} 파일로 저장합니다.")

    # 1. CSV 파일의 맨 윗줄에 들어갈 제목(항목 이름)을 정합니다.
    headers = ["date", "type", "category", "amount", "memo", "tags"]
    
    # 2. 저장소에서 가계부 데이터를 최근순(뒤에서부터)으로 한 줄씩 가져올 준비를 합니다.
    tx_stream = repo.load_transactions_backward()
    
    count = 0              # 내보낸 데이터 개수를 셀 변수입니다.
    is_first_row = True    # 파일의 첫 줄(헤더)을 쓸지 말지 결정하기 위한 표시입니다.

    # 가계부 데이터를 하나씩 꺼내서 확인합니다.
    for tx in tx_stream:
        date = tx.get("date", "")
        
        # [조건 검증 1] 특정 '월'만 골라내기
        # 사용자가 입력한 달과 데이터의 날짜가 다르면 이 데이터는 건너뜁니다.
        if args.month and date[:7] != args.month.strip():
            continue
            
        # [조건 검증 2] 특정 '기간' 내의 데이터만 골라내기
        # 시작 날짜보다 빠르거나, 종료 날짜보다 늦으면 건너뜁니다.
        if args.from_date and date < args.from_date.strip():
            continue
        if args.to_date and date > args.to_date.strip():
            continue

        # [데이터 준비] 모든 조건을 통과했다면 CSV에 저장할 형식으로 정리합니다.
        row = [
            tx.get("date"),
            tx.get("type"),
            tx.get("category"),
            tx.get("amount"),
            tx.get("memo", ""),
            tx.get("tags", "")
        ]
        
        # [파일 쓰기] 만약 이게 첫 번째로 저장하는 데이터라면, 먼저 제목(헤더)부터 씁니다.
        if is_first_row:
            repo.append_to_csv(out_file, headers, is_first=True)
            is_first_row = False
            
        # 데이터를 파일에 한 줄 추가합니다.
        repo.append_to_csv(out_file, row, is_first=False)
        count += 1 # 데이터가 하나 저장될 때마다 숫자를 1 올립니다.

    # 내보내기가 완료된 후 결과를 알려줍니다.
    if count == 0:
        print(f"[안내] 해당 조건에 맞는 데이터가 없어 CSV 파일이 생성되지 않았습니다.")
    else:
        print(f"[완료] {out_file} ({count} records)")


# ==========================================
# 2. CLI 메인 제어부 (argparse 완벽 설정)
# ==========================================

def main():
    # 1. 프로그램 기본 정보 설정 (도움말 및 실행 명령어 정의)
    parser = argparse.ArgumentParser(
        description="파일 기반 가계부 콘솔 프로그램",
        prog="python -m budget_app"
    )

    # 2. 공통 옵션 설정 (모든 명령어에서 공통으로 사용할 데이터 경로 지정)
    # --data-dir 인자를 통해 데이터를 저장할 폴더를 지정하며, 없으면 기본값인 './data'를 사용합니다.
    parser.add_argument("--data-dir", default="./data", help="데이터 저장 폴더 경로 (기본값: ./data)")

    # 3. 하위 명령어(sub-command) 기능 활성화
    # 'add', 'list', 'delete' 등과 같이 기능을 나눌 수 있도록 서브 파서를 생성합니다.
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

    try:
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
    except (KeyboardInterrupt, EOFError):
        print("\n[안내] 사용자에 의해 프로그램이 종료되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[시스템 예외 발생] 예상치 못한 오류입니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
