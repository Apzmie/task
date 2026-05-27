```bash
# 1. 전체 도움말 보기 (요구사항: 모든 명령은 --help가 되어야 함)
python -m budget_app --help

# 2. 특정 명령어(search) 도움말 보기
python -m budget_app search --help

# 3. 검색 옵션 테스트 (인자들이 잘 받아지는지 확인)
python -m budget_app search --from 2026-01-01 --to 2026-01-31 --type expense

# 4. 예산 설정 테스트 (budget set)
python -m budget_app budget set --month 2026-01 --amount 500000
```
