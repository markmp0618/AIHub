# AIHub Homepage

## 프로젝트 개요

AIHub 홈페이지는 "AI를 정보가 아니라 '실행'으로 바꾼다"는 비전을 담은 현대적인 웹 인터페이스입니다. Raycast에서 영감을 받은 중앙 집중식 레이아웃과 부드러운 그라디언트 애니메이션 배경을 특징으로 합니다.

## 기술 스택

- **프레임워크**: Next.js 15 (App Router)
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **폰트**:
  - Display: Outfit (bold, 기하학적, 현대적)
  - Body: Montserrat (깔끔하고 전문적)

## 디자인 특징

### 타이포그래피
- **AIHub 타이틀**: Outfit 폰트 사용, 8xl-9xl 크기로 대담하고 전문적
- Inter와 Roboto 같은 흔한 폰트 대신 독특한 선택
- 세련되고 읽기 쉬운 계층 구조

### 색상 테마
- **배경**: 밝은 테마 (흰색/밝은 회색)
- **텍스트**: 어두운 회색 (#1a1a1a)
- **악센트**: 그라디언트 색상 (7가지 생동감 있는 색상)
- **포커스**: 인디고-퍼플 그라디언트

### 애니메이션 배경
- **영감**: lightswind.com의 그라디언트 애니메이션
- **색상**: #ff6d1b, #ffee55, #5bff89, #4d8aff, #6b5fff, #ff64f9, #ff6565
- **효과**:
  - 8초 무한 루프 애니메이션
  - 120px 블러 효과로 부드러운 분위기 연출
  - 25% 투명도로 밝은 테마와 조화
- **배치**: 고정 위치, 콘텐츠 뒤에 배치 (z-index: -1)

### 챗봇 인터페이스
- **스타일**: 단일 라인 입력창
- **기능**:
  - 실시간 입력 상태 관리
  - 전송 버튼 (입력이 있을 때만 활성화)
  - 포커스 시 인디고 링 효과
- **디자인**:
  - 반투명 흰색 배경 (backdrop-blur)
  - 부드러운 그림자
  - 16px 보더 반경

## 프로젝트 구조

```
홈페이지 UI 제작 도우미/
├── app/
│   ├── page.tsx          # 메인 홈페이지
│   ├── layout.tsx        # 루트 레이아웃 (폰트 및 메타데이터)
│   └── globals.css       # 전역 스타일 및 애니메이션
├── components/
│   ├── HeroSection.tsx   # 메인 히어로 섹션 (타이틀, 서브타이틀)
│   ├── ChatbotInput.tsx  # 단일 라인 챗봇 입력 인터페이스
│   └── GradientBackground.tsx  # 애니메이션 그라디언트 배경
├── public/               # 정적 파일
├── package.json          # 프로젝트 의존성
├── tailwind.config.ts    # Tailwind 설정
├── tsconfig.json         # TypeScript 설정
└── Claude.md            # 이 문서
```

## 설치 및 실행

### 1. 의존성 설치
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

개발 서버가 [http://localhost:3000](http://localhost:3000)에서 실행됩니다.

### 3. 프로덕션 빌드
```bash
npm run build
npm start
```

## 컴포넌트 설명

### GradientBackground
고정 위치의 애니메이션 그라디언트 배경을 렌더링합니다.
- 7가지 색상의 선형 그라디언트
- 8초 부드러운 애니메이션
- 높은 블러 효과 (120px)
- 콘텐츠 뒤에 배치

### HeroSection
메인 콘텐츠 영역을 담당합니다:
- AIHub 타이틀 (대형 디스플레이 폰트)
- 서브타이틀 ("AI를 정보가 아니라 '실행'으로 바꿉니다")
- ChatbotInput 컴포넌트
- 헬퍼 텍스트
- 중앙 정렬 레이아웃

### ChatbotInput
사용자 입력을 받는 인터랙티브 컴포넌트:
- React 상태로 입력 관리
- 폼 제출 처리
- 반응형 디자인
- 접근성 고려 (aria-label)

## 반응형 디자인

### 데스크톱 (1024px+)
- 전체 레이아웃 적용
- 매우 큰 타이틀 (9xl)
- 최대 너비 제약

### 태블릿 (768-1023px)
- 약간 작은 타이포그래피 (8xl)
- 중앙 레이아웃 유지

### 모바일 (<768px)
- 세로로 스택된 요소
- 축소된 타이틀 크기 (7xl)
- 여백이 있는 전체 너비 입력창

## 성능 최적화

- **CSS 애니메이션**: GPU 가속으로 부드러운 60fps 애니메이션
- **폰트 최적화**: `next/font`로 자동 최적화 및 프리로드
- **이미지 최적화**: Next.js Image 컴포넌트 사용 (필요 시)
- **코드 스플리팅**: Next.js의 자동 코드 스플리팅

## 접근성

- 시맨틱 HTML 사용
- ARIA 라벨 제공
- 키보드 네비게이션 지원
- 충분한 색상 대비
- 포커스 인디케이터

## 향후 개선 사항

1. **챗봇 기능 완성**
   - 백엔드 API 연결
   - 실제 AI 응답 처리
   - 대화 히스토리 표시

2. **추가 페이지**
   - About 페이지
   - 서비스 소개
   - 가격 정책

3. **애니메이션 강화**
   - 페이지 로드 시 스태거 애니메이션
   - 스크롤 트리거 효과
   - 마이크로 인터랙션

4. **다크 모드**
   - 테마 토글 추가
   - 다크 모드용 색상 팔레트

## 배포

### Vercel (권장)
```bash
npm run build
vercel deploy
```

### 기타 플랫폼
정적 export가 가능하도록 설정되어 있습니다:
```bash
npm run build
npm start
```

## 라이선스

이 프로젝트는 AIHub의 소유입니다.

## 크레딧

- 디자인 영감: Raycast
- 애니메이션: lightswind.com
- 개발: Claude (Anthropic) with frontend-design skill

---

**Made with Claude Code** 🤖
