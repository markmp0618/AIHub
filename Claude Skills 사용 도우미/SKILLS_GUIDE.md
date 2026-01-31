# Claude Code Skills 공식 가이드

> 출처: [Claude Code 공식 문서](https://code.claude.com/docs/en/skills)

---

## Skills란?

Skills는 Claude의 기능을 확장하는 모듈입니다. `SKILL.md` 파일에 지침을 작성하면 Claude가 자동으로 로드하여 사용합니다.

- **자동 호출**: Claude가 관련 상황에서 자동으로 skill을 적용
- **수동 호출**: `/skill-name`으로 직접 호출 가능

---

## 빠른 시작

### 첫 번째 Skill 만들기

```bash
# 1. skill 폴더 생성 (개인용 - 모든 프로젝트에서 사용)
mkdir -p ~/.claude/skills/explain-code

# 또는 프로젝트용
mkdir -p .claude/skills/explain-code
```

### SKILL.md 작성

```yaml
---
name: explain-code
description: 코드를 시각적 다이어그램과 비유로 설명합니다. "이거 어떻게 동작해?" 같은 질문에 사용.
---

코드를 설명할 때 항상 포함할 것:

1. **비유로 시작**: 일상생활에 비유해서 설명
2. **다이어그램 그리기**: ASCII 아트로 흐름이나 구조 표현
3. **단계별 설명**: 무슨 일이 일어나는지 순서대로 설명
4. **주의점**: 흔한 실수나 오해 짚어주기
```

### 테스트

```
# 자동 호출 (관련 질문하면 Claude가 알아서 적용)
"이 코드 어떻게 동작해?"

# 수동 호출
/explain-code src/auth/login.ts
```

---

## Skill 저장 위치

| 위치 | 경로 | 적용 범위 |
|------|------|----------|
| **개인용** | `~/.claude/skills/<skill-name>/SKILL.md` | 모든 프로젝트 |
| **프로젝트용** | `.claude/skills/<skill-name>/SKILL.md` | 해당 프로젝트만 |
| **플러그인** | `<plugin>/skills/<skill-name>/SKILL.md` | 플러그인 활성화된 곳 |
| **기업용** | managed settings 참조 | 조직 전체 |

**우선순위**: 기업 > 개인 > 프로젝트

---

## Skill 폴더 구조

```
my-skill/
├── SKILL.md           # 메인 지침 (필수)
├── template.md        # 템플릿 (선택)
├── examples/
│   └── sample.md      # 예시 (선택)
└── scripts/
    └── validate.sh    # 실행 스크립트 (선택)
```

---

## Frontmatter 설정

```yaml
---
name: my-skill                      # skill 이름 (폴더명 사용 가능)
description: 이 skill이 하는 일      # Claude가 언제 사용할지 판단 (권장)
argument-hint: [filename] [format]  # 자동완성 힌트
disable-model-invocation: true      # Claude 자동 호출 방지 (수동만)
user-invocable: false               # /메뉴에서 숨김 (Claude만 호출)
allowed-tools: Read, Grep, Glob     # 허용 도구 제한
context: fork                       # subagent에서 실행
agent: Explore                      # subagent 유형
---
```

### 주요 설정 설명

| 필드 | 설명 |
|------|------|
| `name` | skill 이름. 소문자, 숫자, 하이픈만 (최대 64자) |
| `description` | skill 설명. Claude가 언제 사용할지 판단하는 기준 |
| `disable-model-invocation` | `true`면 사용자만 호출 가능 (deploy, commit 등에 적합) |
| `user-invocable` | `false`면 /메뉴에 안 보임 (배경 지식용) |
| `allowed-tools` | skill 활성화 시 허용할 도구 목록 |
| `context` | `fork`로 설정하면 별도 subagent에서 실행 |

---

## 변수 치환

| 변수 | 설명 |
|------|------|
| `$ARGUMENTS` | 호출 시 전달된 모든 인자 |
| `$ARGUMENTS[0]`, `$0` | 첫 번째 인자 |
| `$ARGUMENTS[1]`, `$1` | 두 번째 인자 |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |

### 예시

```yaml
---
name: fix-issue
description: GitHub 이슈 수정
disable-model-invocation: true
---

GitHub 이슈 #$ARGUMENTS 수정하기:

1. 이슈 내용 읽기
2. 요구사항 파악
3. 수정 구현
4. 테스트 작성
5. 커밋 생성
```

사용: `/fix-issue 123` → "GitHub 이슈 #123 수정하기..."

---

## 호출 제어

### 누가 호출할 수 있는가?

| 설정 | 사용자 호출 | Claude 호출 | 용도 |
|------|------------|------------|------|
| (기본값) | O | O | 일반 skill |
| `disable-model-invocation: true` | O | X | deploy, commit 등 |
| `user-invocable: false` | X | O | 배경 지식 |

### 예시: 배포 skill (사용자만 호출)

```yaml
---
name: deploy
description: 프로덕션 배포
disable-model-invocation: true
---

$ARGUMENTS를 프로덕션에 배포:

1. 테스트 실행
2. 앱 빌드
3. 배포
4. 배포 확인
```

---

## 동적 컨텍스트 주입

`` !`command` `` 문법으로 쉘 명령어 실행 결과를 skill에 삽입:

```yaml
---
name: pr-summary
description: PR 요약
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR 정보
- PR diff: !`gh pr diff`
- PR 댓글: !`gh pr view --comments`
- 변경 파일: !`gh pr diff --name-only`

## 할 일
이 PR을 요약해주세요...
```

---

## Subagent에서 실행

`context: fork`를 추가하면 skill이 별도 subagent에서 실행됩니다:

```yaml
---
name: deep-research
description: 주제 심층 조사
context: fork
agent: Explore
---

$ARGUMENTS에 대해 철저히 조사:

1. Glob과 Grep으로 관련 파일 찾기
2. 코드 읽고 분석
3. 파일 참조와 함께 결과 요약
```

### 사용 가능한 Agent 유형

- `Explore`: 읽기 전용, 코드베이스 탐색
- `Plan`: 구현 계획 수립
- `general-purpose`: 범용 (기본값)
- 커스텀 subagent (`.claude/agents/`에 정의)

---

## 도구 제한

```yaml
---
name: safe-reader
description: 파일 읽기만 (수정 불가)
allowed-tools: Read, Grep, Glob
---
```

---

## 지원 파일 추가

큰 참조 문서는 별도 파일로 분리:

```
my-skill/
├── SKILL.md (개요 및 네비게이션)
├── reference.md (상세 API 문서)
├── examples.md (사용 예시)
└── scripts/
    └── helper.py (유틸리티 스크립트)
```

SKILL.md에서 참조:

```markdown
## 추가 리소스

- API 상세 내용: [reference.md](reference.md) 참조
- 사용 예시: [examples.md](examples.md) 참조
```

**팁**: SKILL.md는 500줄 이하로 유지. 상세 내용은 별도 파일로.

---

## 문제 해결

### Skill이 작동하지 않을 때

1. description에 사용자가 쓸 만한 키워드가 있는지 확인
2. `What skills are available?`로 skill 목록 확인
3. 요청 문구를 description에 맞게 수정
4. `/skill-name`으로 직접 호출 시도

### Skill이 너무 자주 작동할 때

1. description을 더 구체적으로 수정
2. 수동 호출만 원하면 `disable-model-invocation: true` 추가

### Claude가 모든 skill을 못 볼 때

Skill description이 너무 많으면 context 제한(기본 15,000자)에 걸릴 수 있음.
`/context`로 확인하고, 필요시 `SLASH_COMMAND_TOOL_CHAR_BUDGET` 환경변수로 늘리기.

---

## 관련 문서

- [Subagents](https://code.claude.com/docs/en/sub-agents): 전문 에이전트에 작업 위임
- [Plugins](https://code.claude.com/docs/en/plugins): skill을 패키지로 배포
- [Hooks](https://code.claude.com/docs/en/hooks): 도구 이벤트 자동화
- [Memory](https://code.claude.com/docs/en/memory): CLAUDE.md로 지속적 컨텍스트 관리
- [Permissions](https://code.claude.com/docs/en/iam): 도구 및 skill 접근 제어

---

## 예시 모음

### 1. 코드 리뷰 Skill

```yaml
---
name: review
description: 코드 리뷰. 버그, 보안 이슈, 개선점 확인.
---

코드 리뷰 시 확인 사항:
- 버그 및 로직 오류
- 보안 취약점
- 성능 이슈
- 코드 스타일
```

### 2. Git 커밋 Skill

```yaml
---
name: commit
description: 변경사항 커밋
disable-model-invocation: true
---

변경사항을 커밋:
1. git status 확인
2. git diff로 변경 내용 파악
3. 의미있는 커밋 메시지 작성
4. git commit 실행
```

### 3. 문서화 Skill

```yaml
---
name: document
description: 코드 문서화. JSDoc, 타입 정의, README 작성.
allowed-tools: Read, Write, Grep
---

문서화 작업:
1. 함수/클래스에 JSDoc 주석 추가
2. 타입 정의 보완
3. 필요시 README 업데이트
```

---

*이 문서는 Claude Code 공식 문서를 기반으로 작성되었습니다.*
*최종 업데이트: 2026년 1월*
