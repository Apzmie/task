# 1. 빈 데이터베이스 파일 생성
sqlite3 school.db

# 2. 구조(설계도) 적용
sqlite> .read schema.sql

# 3. 데이터 입력
sqlite> .read data.sql

# 4. 쿼리 실행 (한꺼번에 실행)
sqlite> .headers on
sqlite> .mode column
sqlite> .read queries.sql