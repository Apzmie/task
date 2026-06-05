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
```bash
제너레이터를 사용해 스트리밍으로 처리하면 무엇이 좋은가요?
데이터를 한 번에 메모리에 올리지 않고 하나씩 처리하여 메모리 효율성을 극대화하고 처리 속도를 높일 수 있습니다.

로직을 데코레이터로 분리하는 이유는 무엇인가요?
반복되는 공통 기능(로깅, 인증 등)을 따로 관리함으로써 핵심 코드의 가독성을 높이고 유지보수를 용이하게 하기 위해서입니다.

타입 힌트를 적용하면 어떤 이점이 있나요?
데이터 타입을 명확히 정의해 실행 전 오류를 방지

왜 다른 포맷 대신 JSONL을 선택했나요?
줄 단위로 데이터를 읽고 쓸 수 있어 대용량 데이터 스트리밍 시 메모리 부하가 적고 안정적이기 때문입니다.

데이터가 10만 건으로 늘어날 때 병목은 어디이며 어떻게 개선하나요?
데이터를 하나씩 DB에 저장하는 I/O 병목이 발생하므로, 데이터를 묶어서 처리하는 배치(Batch) 삽입과 CPU 자원을 효율적으로 쓰는 병렬 처리를 도입해 해결합니다.

CSV에 깨진 행이 섞여 있을 때 어떻게 사용자 신뢰를 지킬 수 있나요?
정상 데이터는 저장하고 에러가 난 행만 따로 로그 파일로 리포트하여 사용자에게 친절한 피드백을 제공합니다.
```
