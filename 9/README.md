```
# 1. 저장소 초기화
init "Alice"

# 2. 커밋 생성
commit "First commit"
commit "Second commit"

# 3. 브랜치 생성 및 전환
branch "feature-a"
switch "feature-a"
commit "Add login logic"

# 4. 로그 확인 (정렬 확인)
log
log --sort-by=date
log --sort-by=author

# 5. 경로 탐색 (앞서 생성한 해시 값을 확인 후 입력)
# 예: path <해시1> <해시2>
path <첫번째_커밋_해시> <세번째_커밋_해시>

# 6. 조상 커밋 확인
ancestors <세번째_커밋_해시>

# 7. 검색 기능
search "login"
search --author="Alice"

# 8. 종료
exit
```