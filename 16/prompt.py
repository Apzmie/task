# prompt.py
def build_commit_prompt(status, diff):
    """
    Git 변경사항 기반 커밋 메시지 생성 프롬프트
    """

    prompt = f"""
너는 숙련된 소프트웨어 개발자이다.
아래 Git 변경사항을 분석해서 Conventional Commit 형식의 커밋 메시지를 작성하라.

작성 규칙:
- 첫 줄은 반드시 커밋 제목이어야 한다.
- 제목은 72자 이내로 작성한다.
- 형식 예시:
  feat: 새로운 기능 추가
  fix: 오류 수정
  docs: 문서 수정
  refactor: 코드 개선
- 필요하면 본문을 추가한다.
- 본문을 작성할 경우:
  - 변경된 파일 또는 모듈을 1~3개 언급
  - 핵심 변경사항을 불릿으로 작성
- 설명, 인사말, 마크다운 코드블록은 작성하지 않는다.

[Git Status]
{status}

[Git Diff]
{diff}

결과만 출력하라.
"""

    return prompt.strip()


def build_pr_prompt(status, diff, branch):
    """
    Git 변경사항 기반 PR 생성 프롬프트
    """

    prompt = f"""
너는 소프트웨어 프로젝트의 Pull Request 작성자이다.

아래 Git 변경사항을 분석하여 PR 제목과 본문 초안을 작성하라.

현재 브랜치:
{branch}

반드시 아래 형식을 지켜라.

PR Title:
한 줄 제목

## Why
- 변경 배경 또는 문제 상황

## What
- 핵심 변경사항
- 구현한 기능 또는 수정 내용

## How to Test
- 실행 방법
- 확인 방법

작성 규칙:
- PR Title은 80자 이내
- Why, What, How to Test 헤더는 반드시 포함
- 각 섹션마다 최소 1개 이상의 불릿 작성
- 실제 변경 내용 기반으로 작성
- 추측하거나 존재하지 않는 기능을 만들지 않는다.
- 불필요한 설명은 작성하지 않는다.

[Git Status]
{status}

[Git Diff]
{diff}

결과만 출력하라.
"""

    return prompt.strip()