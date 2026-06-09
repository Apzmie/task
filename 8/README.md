```
# 1. 메모리 제한을 30바이트로 설정
mini-redis> CONFIG SET maxmemory 30
OK

# 2. 데이터 저장 (30바이트 안쪽)
mini-redis> SET user:1 Alice
OK
mini-redis> SET user:2 Bob
OK

# 3. 현재 메모리 사용량 확인 (evicted_keys가 0인지 확인)
mini-redis> INFO memory
used_memory:22
maxmemory:30
evicted_keys:0

# 4. 메모리를 초과하는 데이터를 넣어서 LRU(가장 오래된 데이터 제거) 테스트
mini-redis> SET user:3 Charlie
OK

# 5. 이제 user:1이 삭제되었는지 확인
mini-redis> GET user:1
(nil)
```
