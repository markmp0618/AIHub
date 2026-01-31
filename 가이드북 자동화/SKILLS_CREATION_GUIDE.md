# Claude Code Skills 제작 가이드

이 가이드는 Claude Code Skills를 직접 만들기 위한 실용적인 안내서입니다.

---

## 목차

1. [Skills 기본 개념](#1-skills-기본-개념)
2. [폴더 구조](#2-폴더-구조)
3. [SKILL.md 작성법](#3-skillmd-작성법)
4. [Frontmatter 옵션](#4-frontmatter-옵션)
5. [변수 치환](#5-변수-치환)
6. [복잡도별 템플릿](#6-복잡도별-템플릿)
7. [실제 예시](#7-실제-예시)
8. [Skills 저장 위치](#8-skills-저장-위치)
9. [다른 컴퓨터로 이전](#9-다른-컴퓨터로-이전)
10. [문제 해결](#10-문제-해결)

---

## 1. Skills 기본 개념

### Skills란?
- Claude가 **특정 작업을 더 잘 수행**하도록 가르치는 지침서
- 폴더 단위의 파일 모음 (SKILL.md + 지원 파일)
- 사용자가 `/skill-name`으로 직접 호출하거나, Claude가 자동으로 사용

### Skills의 장점
- **재사용성**: 한 번 만들면 계속 사용
- **일관성**: 동일한 형식과 품질 유지
- **공유 가능**: 팀원이나 커뮤니티와 공유

---

## 2. 폴더 구조

### 최소 구조 (필수)
```
skill-name/
└── SKILL.md           # 필수 - 메인 지침 파일
```

### 권장 구조
```
skill-name/
├── SKILL.md           # 필수 - 메인 지침
├── README.md          # 선택 - 개요 및 사용법
└── references/        # 선택 - 상세 참조 문서
    ├── guide1.md
    └── guide2.md
```

### 복잡한 구조 (고급)
```
skill-name/
├── SKILL.md                    # 메인 지침 (네비게이션 역할)
├── README.md                   # 개요 및 설치 방법
├── references/                 # 상세 문서
│   ├── methodology.md         # 방법론
│   ├── api_guide.md           # API 가이드
│   └── examples.md            # 사용 예시
├── scripts/                    # 실행 스크립트
│   ├── main.py
│   └── utils.py
└── assets/                     # 템플릿, 이미지 등
    └── template.md
```

### 폴더명 규칙
- **소문자**만 사용
- 단어 구분은 **하이픈(-)** 사용
- 예: `code-review`, `stock-analysis`, `pr-summarizer`

---

## 3. SKILL.md 작성법

### 기본 구조

```markdown
---
name: skill-name
description: 이 skill이 무엇을 하는지 설명
---

# Skill 제목

## 역할 정의
당신은 [역할]입니다.

## 수행 작업
1. 첫 번째 단계
2. 두 번째 단계
3. 세 번째 단계

## 출력 형식
[마크다운 템플릿]

## 사용 예시
사용자가 "~해줘"라고 하면 이 skill을 적용하세요.
```

### 핵심 섹션 설명

| 섹션 | 설명 | 필수 여부 |
|------|------|----------|
| Frontmatter | YAML 메타데이터 (name, description) | 권장 |
| 역할 정의 | Claude가 어떤 역할을 수행할지 | 권장 |
| 수행 작업 | 단계별 지침 | 권장 |
| 출력 형식 | 결과물 템플릿 | 권장 |
| 사용 예시 | 언제 사용할지 예시 | 선택 |

---

## 4. Frontmatter 옵션

### 전체 옵션 목록

```yaml
---
name: my-skill                      # skill 이름 (소문자, 숫자, 하이픈)
description: 이 skill의 설명         # Claude 자동 호출 판단에 사용
argument-hint: [filename] [format]  # 인자 힌트 (자동완성 시 표시)
disable-model-invocation: true      # true: 사용자만 호출 가능
user-invocable: false               # false: / 메뉴에서 숨김
allowed-tools: Read, Grep, Glob     # 허용 도구 제한
context: fork                       # fork: subagent에서 실행
agent: Explore                      # subagent 유형
model: opus                         # 사용할 모델
---
```

### 옵션 상세 설명

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `name` | 폴더명 | skill 이름. 64자 이하, 소문자/숫자/하이픈만 |
| `description` | 본문 첫 문단 | Claude가 언제 사용할지 판단하는 키워드 포함 |
| `argument-hint` | 없음 | `/skill-name` 자동완성 시 힌트 표시 |
| `disable-model-invocation` | `false` | `true`면 Claude 자동 호출 차단 |
| `user-invocable` | `true` | `false`면 `/` 메뉴에서 숨김 |
| `allowed-tools` | 전체 | 사용 가능한 도구 제한 |
| `context` | inline | `fork`면 별도 subagent에서 실행 |
| `agent` | general-purpose | subagent 유형 (Explore, Plan 등) |

### 호출 제어 조합

| 설정 | 사용자 호출 | Claude 호출 | 사용 사례 |
|------|------------|------------|----------|
| 기본값 | O | O | 일반 skill |
| `disable-model-invocation: true` | O | X | deploy, commit 등 |
| `user-invocable: false` | X | O | 배경 지식 skill |

---

## 5. 변수 치환

### 사용 가능한 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `$ARGUMENTS` | 전체 인자 | `/skill arg1 arg2` → `arg1 arg2` |
| `$0` | 첫 번째 인자 | `/skill arg1 arg2` → `arg1` |
| `$1` | 두 번째 인자 | `/skill arg1 arg2` → `arg2` |
| `$ARGUMENTS[N]` | N번째 인자 (0부터) | `$ARGUMENTS[0]` = `$0` |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID | 로깅, 파일명에 활용 |

### 사용 예시

```yaml
---
name: fix-issue
description: GitHub 이슈 수정
---

GitHub 이슈 #$ARGUMENTS 를 수정합니다.

1. 이슈 내용 확인
2. 코드 수정
3. 테스트 작성
4. 커밋 생성
```

사용: `/fix-issue 123` → "GitHub 이슈 #123 를 수정합니다."

### 동적 컨텍스트 주입 (!`command`)

```yaml
---
name: pr-summary
description: PR 요약
---

## PR 정보
- 변경된 파일: !`gh pr diff --name-only`
- PR 댓글: !`gh pr view --comments`

이 PR을 요약하세요.
```

`!`command`` 안의 명령이 **먼저 실행**되고, 결과가 skill에 삽입됩니다.

---

## 6. 복잡도별 템플릿

### 간단 (50-100줄) - SKILL.md만

```yaml
---
name: code-review
description: 코드 리뷰 및 품질 분석을 수행합니다. 버그, 보안, 성능을 검토합니다.
---

# Code Review Skill

당신은 시니어 소프트웨어 엔지니어입니다.

## 리뷰 항목

### 1. 버그 및 로직 오류
- 널 포인터, 범위 초과 등 확인

### 2. 보안 취약점
- SQL 인젝션, XSS 등 OWASP Top 10 확인

### 3. 성능
- 불필요한 루프, N+1 쿼리 등 확인

### 4. 코드 품질
- 명명 규칙, 중복 코드 확인

## 출력 형식

### 리뷰 결과

#### 심각도: [높음/중간/낮음]

**발견된 이슈:**
1. [파일명:라인] - [이슈 설명]

**권장 수정사항:**
- [수정 제안]
```

### 중간 (100-300줄) - SKILL.md + references

```yaml
---
name: api-designer
description: RESTful API 설계 및 문서화
---

# API Designer Skill

당신은 API 설계 전문가입니다.

## 설계 원칙
[간략한 원칙 설명]

## 상세 가이드
상세한 API 설계 가이드는 [references/api-conventions.md](references/api-conventions.md)를 참조하세요.

## 출력 형식
[API 문서 템플릿]
```

### 복잡 (300줄+) - 전체 구조

```yaml
---
name: stock-screener
description: 주식 스크리닝 및 분석
context: fork
agent: general-purpose
---

# Stock Screener

## 개요
[간략한 설명]

## 사용 조건
- API 키 필요: FMP_API_KEY

## 워크플로우

### Step 1: 데이터 수집
[references/data-collection.md](references/data-collection.md) 참조

### Step 2: 분석 실행
[references/analysis-framework.md](references/analysis-framework.md) 참조

### Step 3: 리포트 생성
[references/report-template.md](references/report-template.md) 참조

## 문제 해결
[references/troubleshooting.md](references/troubleshooting.md) 참조
```

---

## 7. 실제 예시

### 예시 1: 커밋 메시지 생성기

```yaml
---
name: commit-message
description: 변경사항을 분석하여 conventional commit 형식의 메시지 생성
disable-model-invocation: true
---

# Commit Message Generator

staged된 변경사항을 분석하여 commit 메시지를 생성합니다.

## 형식
```
<type>(<scope>): <subject>

<body>

<footer>
```

## Type 종류
- feat: 새 기능
- fix: 버그 수정
- docs: 문서 변경
- style: 코드 포맷팅
- refactor: 리팩토링
- test: 테스트
- chore: 빌드, 설정 등

## 실행 방법
1. `git diff --staged` 실행
2. 변경사항 분석
3. 적절한 type 선택
4. 메시지 생성
```

### 예시 2: 문서 요약기

```yaml
---
name: summarizer
description: 긴 텍스트, 문서, 코드를 요약합니다. 핵심만 빠르게 파악할 때 사용합니다.
---

# Summarizer Skill

당신은 전문 요약가입니다.

## 요약 원칙
1. 핵심 포인트 추출
2. 불필요한 내용 제거
3. 원문의 의도 유지

## 출력 형식

### 요약 결과

**핵심 요약** (3줄 이내)
[요약 내용]

**주요 포인트**
- 포인트 1
- 포인트 2
- 포인트 3

**원문 길이**: [X]줄 → **요약 길이**: [Y]줄 ([Z]% 축소)
```

---

## 8. Skills 저장 위치

### 위치별 적용 범위

| 위치 | 경로 | 적용 범위 |
|------|------|----------|
| **개인** | `~/.claude/skills/` | 모든 프로젝트 |
| **프로젝트** | `.claude/skills/` | 해당 프로젝트만 |
| **플러그인** | `<plugin>/skills/` | 플러그인 활성화 시 |
| **기업** | 관리 설정 | 조직 전체 |

### Windows 경로
- 개인: `C:\Users\사용자명\.claude\skills\`
- 프로젝트: `프로젝트폴더\.claude\skills\`

### 우선순위
같은 이름의 skill이 있을 경우: **기업 > 개인 > 프로젝트**

### 권장 사용법
- **자주 쓰는 skill** → 개인 폴더 (`~/.claude/skills/`)
- **프로젝트 전용 skill** → 프로젝트 폴더 (`.claude/skills/`)
- **팀 공유 skill** → 프로젝트 폴더 + Git 커밋

---

## 9. 다른 컴퓨터로 이전

### 이전 방법

Skills는 **폴더 복사만으로 100% 이식** 가능합니다.

```
# 복사할 폴더
~/.claude/skills/
또는
.claude/skills/

# 새 컴퓨터의 같은 위치에 붙여넣기
```

### 주의사항

1. **Claude Code 설치 필요**
   - 새 컴퓨터에도 Claude Code가 설치되어 있어야 함

2. **외부 의존성 설정 필요**
   | 의존성 | 설정 방법 |
   |--------|----------|
   | API 키 | 환경변수 설정 (예: `FMP_API_KEY`) |
   | MCP 서버 | `.claude/settings.json`에서 설정 |
   | Python 패키지 | `pip install` 실행 |

3. **환경변수 예시**
   ```bash
   # Windows
   setx FMP_API_KEY "your-api-key"

   # Mac/Linux
   export FMP_API_KEY="your-api-key"
   ```

---

## 10. 문제 해결

### Skill이 호출되지 않을 때

1. **description 확인**: 사용자 요청과 매칭되는 키워드 포함?
2. **위치 확인**: 올바른 폴더에 있는지?
3. **직접 호출 테스트**: `/skill-name`으로 직접 호출
4. **skills 목록 확인**: "What skills are available?" 질문

### Skill이 너무 자주 호출될 때

1. **description 구체화**: 더 특정한 조건 명시
2. **disable-model-invocation 추가**: 수동 호출만 허용

### 모든 skills가 표시되지 않을 때

- skill description의 총 문자 수가 15,000자를 초과하면 일부 제외됨
- `/context` 명령으로 경고 메시지 확인
- 환경변수로 제한 증가: `SLASH_COMMAND_TOOL_CHAR_BUDGET`

### SKILL.md 권장 라인 수

| 복잡도 | 라인 수 | 권장 구조 |
|--------|---------|----------|
| 간단 | 50-100줄 | SKILL.md만 |
| 중간 | 100-300줄 | SKILL.md + references |
| 복잡 | 300줄+ | 500줄 넘으면 references로 분리 |

---

## 참고 자료

- [Claude Code Skills 공식 문서](https://code.claude.com/docs/en/skills)
- [Agent Skills 오픈 스탠다드](https://agentskills.io)
- [Anthropic Skills GitHub](https://github.com/anthropics/skills)
- [SkillsMP - Skills 마켓플레이스](https://skillsmp.com/)

---

## 빠른 시작 체크리스트

- [ ] skill 폴더 생성 (`skill-name/`)
- [ ] SKILL.md 작성
- [ ] Frontmatter에 name, description 추가
- [ ] 역할 정의 작성
- [ ] 수행 작업 단계 작성
- [ ] 출력 형식 템플릿 작성
- [ ] 테스트: `/skill-name` 호출
- [ ] 필요시 개인 폴더로 이동 (`~/.claude/skills/`)
