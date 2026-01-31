# Claude Skills 테스트 프로젝트

이 프로젝트는 다양한 Claude Skills를 테스트하고 실험하는 공간입니다.

## Skills 저장 위치

### 개인 전역 Skills (모든 프로젝트에서 사용 가능)
- **위치**: `~/.claude/skills/` (Windows: `C:\Users\PC\.claude\skills\`)
- 여기에 저장된 skills는 어떤 프로젝트에서든 자동으로 인식됩니다.

### 프로젝트 Skills (이 프로젝트에서만 사용)
- **위치**: `.claude/skills/`

## 설치된 Skills

### 1. 코드/개발
- **code-review**: 코드 리뷰 및 품질 분석

### 2. 콘텐츠 생성
- **youtube-script**: 유튜브 영상 스크립트 작성
- **blog-writer**: SEO 최적화 블로그 포스트 작성
- **summarizer**: 텍스트/문서/영상 요약

### 3. 데이터/분석
- **stock-analysis**: 주식 및 투자 분석
- **data-analyst**: 데이터 분석 및 인사이트 도출

### 4. 주식/투자 (개인 전역 Skills)
- **technical-analyst**: 주식/암호화폐 차트 기술적 분석
- **us-stock-analysis**: 미국 주식 종합 분석 (펀더멘털 + 기술적)
- **canslim-screener**: CANSLIM 방법론 기반 고성장주 스크리닝
- **institutional-flow-tracker**: 기관투자자 매매 추적 (13F 보고서)
- **portfolio-manager**: 포트폴리오 분석 및 리밸런싱

## 사용 방법

각 skill은 관련 요청을 하면 자동으로 활성화됩니다:

- "이 코드 리뷰해줘" → code-review skill
- "유튜브 스크립트 써줘" → youtube-script skill
- "블로그 글 써줘" → blog-writer skill
- "이 내용 요약해줘" → summarizer skill
- "삼성전자 주식 분석해줘" → stock-analysis skill
- "이 CSV 데이터 분석해줘" → data-analyst skill

## 폴더 구조

```
Claude Skills 사용 도우미/
├── CLAUDE.md                  # 프로젝트 설정 파일
├── SKILLS_GUIDE.md            # Skills 공식 가이드 (한국어)
├── SKILLS_CREATION_GUIDE.md   # Skills 제작 가이드
└── .claude/
    └── skills/                # 프로젝트 Skills 폴더
        ├── code-review/
        ├── youtube-script/
        ├── blog-writer/
        ├── summarizer/
        ├── stock-analysis/
        └── data-analyst/

~/.claude/skills/              # 개인 전역 Skills 폴더
├── technical-analyst/
├── us-stock-analysis/
├── canslim-screener/
├── institutional-flow-tracker/
└── portfolio-manager/
```

## 참고 문서

- [SKILLS_GUIDE.md](SKILLS_GUIDE.md) - Claude Code Skills 공식 가이드 (한국어 번역)
- [SKILLS_CREATION_GUIDE.md](SKILLS_CREATION_GUIDE.md) - Skills 직접 제작 가이드
- [공식 문서](https://code.claude.com/docs/en/skills) - Anthropic 공식 Skills 문서

## Skills 만들기

새로운 skill을 만들고 싶다면:
1. [SKILLS_CREATION_GUIDE.md](SKILLS_CREATION_GUIDE.md) 참고
2. "~하는 skill 만들어줘" 라고 요청하면 Claude가 바로 생성
