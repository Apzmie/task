```bash
# 1. 전체 도움말 보기 (요구사항: 모든 명령은 --help가 되어야 함)
python -m budget_app --help

# 2. 특정 명령어(search) 도움말 보기
python -m budget_app search --help

# ① 새로운 거래 추가 (날짜, 타입, 카테고리 등을 차례로 묻는 대화형)
python -m budget_app add

# ② 거래 목록 최신순 조회 (메모리에 대용량 로드 없이 뒤에서부터 지정한 개수만 스트리밍)
python -m budget_app list --limit 5

# ③ 기존 거래 수정 (ID를 입력하면 기존 값을 보여주고 엔터/재입력으로 수정하는 대화형)
python -m budget_app update

# ④ 특정 거래 삭제 (지정한 ID를 임시 파일을 활용해 원자적으로 안전하게 삭제)
python -m budget_app delete --id TX-A1B2C3

# 3. 검색 옵션 테스트 (인자들이 잘 받아지는지 확인)
python -m budget_app search --from 2026-01-01 --to 2026-01-31 --type expense

# ① 기간 및 타입으로 검색 (2026년 1월 한 달간의 지출만 조회)
python -m budget_app search --from 2026-01-01 --to 2026-01-31 --type expense

# ① 월별 예산 설정 (2026년 5월 예산을 500,000원으로 영구 저장)
python -m budget_app budget set --month 2026-05 --amount 500000

# ② 월별 요약 보고서 조회 (총수입/지출/잔액 계산 및 지출 상위 카테고리 TOP 3 정렬)
# (※ 예산이 설정되어 있으면 '사용률%'과 '🚨 초과 경고'가 자동으로 함께 출력됩니다)
python -m budget_app summary --month 2026-05 --top 3

# ① 등록된 모든 카테고리 종류 확인
python -m budget_app category list

# ② 새로운 카테고리 추가
python -m budget_app category add

# ③ 카테고리 삭제 (※ 해당 카테고리를 가계부에서 사용 중이면 삭제가 자동 차단됨!)
python -m budget_app category remove

# ① 조건에 맞는 가계부 데이터를 CSV 파일로 내보내기 (지정 월 조건 필수)
python -m budget_app export --out backup_2026_05.csv --month 2026-05

# ② 외부 CSV 파일을 읽어와 유효성 검증 후 고유 ID를 부여해 가계부에 일괄 등록하기
python -m budget_app import --from import.csv
```
