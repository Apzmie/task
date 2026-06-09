```
1. 메모리 및 데이터 저장 테스트
CONFIG SET maxmemory 30
SET user:1 "Alice"
SET user:2 "Bob"
SET user:3 "Charlie"

2. LRU 및 메모리 상태 확인
GET user:1
INFO memory
KEYS

3. TTL (만료 시간) 테스트
SET user:4 "David"
EXPIRE user:4 5
TTL user:4

4. 만료 후 조회
# (5초 정도 기다린 후)
GET user:4
TTL user:4
```
