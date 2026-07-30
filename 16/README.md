```
docker run -it python:3.11-slim bash
export AI_API_KEY=""

apt update
apt install -y git

git init
git config user.name "Your Name"
git config user.email "your@email.com"

git add .
git commit -m "initial project"

echo "# test" >> test.txt
git add test.txt
git commit -m "add test file"

echo "hello" >> test.txt
git status
git diff

python main.py commit
python main.py pr

## 주의사항
- git diff에 민감정보가 포함되지 않도록 확인 후 사용합니다.
- AI가 생성한 커밋 메시지와 PR 내용은 검토 후 적용합니다.
- commit/pr 실행마다 AI API 요청이 발생하므로 불필요한 반복 실행을 줄입니다
```
```
[INFO] Git status 수집 완료: 1개 파일 변경 감지
[INFO] Git diff 수집 완료: 7줄
[INFO] Gemini API 요청 중...

==================================================
Commit Message
==================================================
docs: test.txt 파일에 인사말 추가

- test.txt 파일 내용 수정
- hello 문자열 추가
==================================================
```
```
[INFO] 현재 브랜치: master
[INFO] Git diff 수집 완료: 30줄
[INFO] Gemini API 요청 중...

==================================================
Pull Request Draft
==================================================
PR Title:
docs: README 예시 추가 및 test.txt 인사말 수정

## Why
- 문서에 Git 상태 수집 및 Gemini API 요청 관련 로그 예시를 추가할 필요가 있음
- 테스트 파일에 새로운 내용을 추가하여 변경 사항을 반영함

## What
- README.md 파일에 Gemini API 커밋 메시지 생성 로그 예시 추가
- test.txt 파일에 `hello` 문자열 추가

## How to Test
- README.md 파일의 내용이 올바르게 추가되었는지 확인
- test.txt 파일에 `hello`가 정상적으로 추가되었는지 확인
==================================================
```
