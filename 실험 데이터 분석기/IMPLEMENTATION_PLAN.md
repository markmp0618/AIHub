# LabReportAI 멀티 실험 리포트 확장 - 인수인계 보고서 (Handover Report)

> **작성일**: 2026-01-30
> **상태**: ✅ Phase 6 테스트 완료 - Step 4 (Supabase 통합) 대기 중

---

## 🎉 현재 진행 상황 (Current Status)

### ✅ 완료된 작업 (Phase 1-6 완료)
1. **API 엔드포인트 수정**:
   - `app/main.py`와 `app/routers/__init__.py` 수정하여 모든 엔드포인트 정상 작동.
   - `analyze_router`와 `generate_router`를 명시적으로 import하여 등록 완료.
2. **패키지 의존성 업데이트**:
   - `backend/requirements.txt`에 `google-genai==0.8.3` 추가 및 설치 완료.
3. **PDF 매뉴얼 추출 기능** ✅:
   - Gemini API `response_mime_type="application/json"` 설정으로 JSON 응답 강제.
   - 테스트 결과: 정상 작동 (200 OK, JSON 파싱 성공).
4. **멀티시트 Excel 분석 기능** ✅:
   - `/api/analyze/detect-sheets`: 3개 시트 감지 성공.
   - `/api/analyze/batch`: 배치 분석 성공 (R² > 0.96 모든 실험).
5. **전체 리포트 생성 기능** ✅:
   - `/api/generate/full-report`: 588KB 마크다운 리포트 생성 성공.
   - 데이터 테이블 + 그래프(Base64) + AI 분석 텍스트 포함.

### 📊 E2E 테스트 결과 (2026-01-30)
| API 엔드포인트 | 상태 | 비고 |
|---------------|------|------|
| `POST /api/generate/extract-manual` | ✅ 200 OK | PDF → JSON 추출 성공 |
| `POST /api/analyze/detect-sheets` | ✅ 200 OK | 3개 시트 감지 |
| `POST /api/analyze/batch` | ✅ 200 OK | 3개 실험 분석, 그래프 생성 |
| `POST /api/generate/full-report` | ✅ 200 OK | 마크다운 리포트 생성 |

### 📝 다음에 해야 할 일 (Next Steps)
1. **Supabase 통합 (Step 4)** - 미구현:
   - 리포트 저장 및 히스토리 관리
   - 사용자 인증 (선택)
2. **Frontend 연동 테스트**:
   - 새 컴포넌트 4개 동작 확인
   - `page.tsx` 멀티스텝 플로우 검증
3. **배포**:
   - Backend: Railway / Render
   - Frontend: Vercel

---

## 📂 파일 수정 이력

### `backend/app/main.py`
- 라우터 임포트 방식 변경 (`from app.routers import ...` → `from app.routers.module import router ...`)

### `backend/app/routers/__init__.py`
- `generate_router` export 추가

### `backend/app/services/gemini_service.py`
- `extract_manual_from_pdf` 메서드: JSON 모드 활성화, 로그 추가.

### `backend/requirements.txt`
- `google-genai` 패키지 추가

---

# LabReportAI 멀티 실험 리포트 확장 계획

> **작성일**: 2026-01-30
> **이전 대화**: 2026-01-30 세션
> **목적**: 새 대화창에서도 이 계획을 참조하여 구현 진행

---

## 1. 프로젝트 개요

### 현재 상태
- 단일 CSV/Excel 파일 업로드 → 하나의 그래프 + 통계 분석
- Gemini AI로 고찰(Discussion) 생성
- MVP 75% 완료 (Step 1-3 완료, Step 4 미구현)

### 새로운 요구사항
- **PDF 매뉴얼 업로드** → Gemini가 실험 목적, 이론, 오차 가이드 자동 추출
- **Excel 멀티시트 지원** → 각 시트가 하나의 실험, 여러 실험 동시 분석
- **전체 리포트 생성** → 마크다운 + Base64 이미지 임베딩
- **리포트 구조**: 실험결과 (데이터 테이블 + 그래프) + 결과분석 + 토의

### 새로운 플로우
```
PDF 매뉴얼 (선택) → Excel (여러 시트) → 배치 분석 → 마크다운 리포트 다운로드
```

---

## 2. 수정/생성 파일 목록

### Backend (수정)

| 파일 | 경로 | 변경 내용 |
|------|------|----------|
| schemas.py | `backend/app/models/schemas.py` | 새 Pydantic 모델 추가 |
| file_parser.py | `backend/app/utils/file_parser.py` | 멀티시트 Excel + PDF 파싱 |
| analysis_engine.py | `backend/app/services/analysis_engine.py` | 배치 분석 메서드 |
| graph_generator.py | `backend/app/services/graph_generator.py` | 멀티 그래프 생성 |
| gemini_service.py | `backend/app/services/gemini_service.py` | PDF 추출 + 전체 리포트 생성 |
| analyze.py | `backend/app/routers/analyze.py` | 새 엔드포인트 추가 |
| generate.py | `backend/app/routers/generate.py` | 새 엔드포인트 추가 |
| config.py | `backend/app/config.py` | PDF 설정 추가 |

### Backend (신규)

| 파일 | 경로 | 역할 |
|------|------|------|
| report_generator.py | `backend/app/services/report_generator.py` | 마크다운 리포트 조립 |

### Frontend (수정)

| 파일 | 경로 | 변경 내용 |
|------|------|----------|
| index.ts | `frontend/src/types/index.ts` | 새 TypeScript 인터페이스 |
| api.ts | `frontend/src/lib/api.ts` | 새 API 함수 |
| page.tsx | `frontend/src/app/page.tsx` | 멀티스텝 UI 플로우 |

### Frontend (신규)

| 파일 | 경로 | 역할 |
|------|------|------|
| MultiFileUploader.tsx | `frontend/src/components/MultiFileUploader.tsx` | PDF + Excel 업로드 UI |
| SheetConfigEditor.tsx | `frontend/src/components/SheetConfigEditor.tsx` | 시트별 설정 편집기 |
| BatchResultsView.tsx | `frontend/src/components/BatchResultsView.tsx` | 배치 결과 뷰어 |
| MarkdownReportViewer.tsx | `frontend/src/components/MarkdownReportViewer.tsx` | 리포트 미리보기 + 다운로드 |

---

## 3. 새 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/analyze/detect-sheets` | Excel 파일의 시트 정보 감지 |
| POST | `/api/analyze/batch` | 여러 시트 배치 분석 |
| POST | `/api/generate/extract-manual` | PDF에서 매뉴얼 정보 추출 |
| POST | `/api/generate/full-report` | 전체 마크다운 리포트 생성 |

---

## 4. 새 Pydantic 모델 (schemas.py에 추가)

```python
# PDF 추출 관련
class ErrorGuideItem(BaseModel):
    cause: str
    description: str
    mitigation: Optional[str] = None

class ExperimentManualInfo(BaseModel):
    experiment_purpose: str
    theory: str
    error_guides: List[ErrorGuideItem] = []
    expected_results: Optional[str] = None
    equipment_list: Optional[List[str]] = None

class PDFExtractionResponse(ApiResponse):
    data: Optional[ExperimentManualInfo] = None

# 멀티시트 관련
class SheetInfo(BaseModel):
    sheet_name: str
    columns: List[str]
    row_count: int
    sample_data: List[dict] = []

class MultiSheetDetectionResponse(ApiResponse):
    sheets: List[SheetInfo] = []
    total_sheets: int = 0

class ExperimentConfig(BaseModel):
    sheet_name: str
    experiment_name: str
    x_column: str
    y_column: str
    theoretical_slope: Optional[float] = None

class BatchAnalysisRequest(BaseModel):
    experiments: List[ExperimentConfig]
    report_title: str
    manual_info: Optional[ExperimentManualInfo] = None

# 배치 분석 결과
class SingleExperimentResult(BaseModel):
    experiment_name: str
    sheet_name: str
    statistics: StatisticsResult
    graph: GraphResult
    data_summary: DataSummary
    data_table: List[dict]

class BatchAnalysisData(BaseModel):
    batch_id: str
    report_title: str
    experiments: List[SingleExperimentResult] = []
    total_experiments: int
    manual_info: Optional[ExperimentManualInfo] = None

class BatchAnalysisResponse(ApiResponse):
    data: Optional[BatchAnalysisData] = None

# 리포트 생성
class ReportOptions(BaseModel):
    language: str = "ko"
    include_data_tables: bool = True
    include_individual_analysis: bool = True
    tone: str = "academic"

class ReportSections(BaseModel):
    experiment_results: str
    result_analysis: str
    discussion: str

class FullReportRequest(BaseModel):
    batch_id: str
    report_title: str
    experiments: List[SingleExperimentResult]
    manual_info: Optional[ExperimentManualInfo] = None
    options: Optional[ReportOptions] = None

class FullReportResponse(ApiResponse):
    markdown_content: str
    sections: ReportSections
```

---

## 5. 서비스 메서드 시그니처

### file_parser.py (추가)
```python
async def parse_excel_all_sheets(file: UploadFile) -> Dict[str, pd.DataFrame]
async def detect_multi_sheets(file: UploadFile) -> List[SheetInfo]
async def parse_pdf_file(file: UploadFile) -> bytes
```

### analysis_engine.py (추가)
```python
def analyze_batch(
    self,
    sheets_data: Dict[str, pd.DataFrame],
    experiments: List[ExperimentConfig]
) -> List[Tuple[StatisticsResult, DataSummary, pd.DataFrame, List[dict]]]

def dataframe_to_table(self, df, x_col, y_col, max_rows=50) -> List[dict]
```

### graph_generator.py (추가)
```python
def generate_batch_graphs(
    self,
    experiments_data: List[Tuple[pd.DataFrame, str, str, StatisticsResult, str]]
) -> List[GraphResult]
```

### gemini_service.py (추가)
```python
def extract_manual_from_pdf(self, pdf_bytes: bytes, filename: str) -> ExperimentManualInfo
def generate_full_report(
    self,
    report_title: str,
    experiments: List[SingleExperimentResult],
    manual_info: Optional[ExperimentManualInfo] = None,
    options: Optional[ReportOptions] = None
) -> FullReportResponse
```

### report_generator.py (신규)
```python
class ReportGenerator:
    def generate_markdown_report(
        self,
        report_title: str,
        experiments: List[SingleExperimentResult],
        generated_sections: ReportSections,
        manual_info: Optional[ExperimentManualInfo] = None
    ) -> str

    def _generate_data_table_markdown(self, data_table: List[dict], experiment_name: str) -> str
    def _embed_base64_image(self, image_base64: str, caption: str) -> str
```

---

## 6. Frontend TypeScript 인터페이스 (types/index.ts에 추가)

```typescript
// PDF 추출
export interface ErrorGuideItem {
  cause: string;
  description: string;
  mitigation?: string;
}

export interface ExperimentManualInfo {
  experiment_purpose: string;
  theory: string;
  error_guides: ErrorGuideItem[];
  expected_results?: string;
  equipment_list?: string[];
}

// 멀티시트
export interface SheetInfo {
  sheet_name: string;
  columns: string[];
  row_count: number;
  sample_data: Record<string, unknown>[];
}

export interface ExperimentConfig {
  sheet_name: string;
  experiment_name: string;
  x_column: string;
  y_column: string;
  theoretical_slope?: number;
}

// 배치 분석
export interface SingleExperimentResult {
  experiment_name: string;
  sheet_name: string;
  statistics: StatisticsResult;
  graph: GraphResult;
  data_summary: DataSummary;
  data_table: Record<string, unknown>[];
}

export interface BatchAnalysisData {
  batch_id: string;
  report_title: string;
  experiments: SingleExperimentResult[];
  total_experiments: number;
  manual_info?: ExperimentManualInfo;
}

// 리포트
export interface ReportSections {
  experiment_results: string;
  result_analysis: string;
  discussion: string;
}

export interface FullReportData {
  markdown_content: string;
  sections: ReportSections;
}
```

---

## 7. Frontend API 함수 (api.ts에 추가)

```typescript
export async function extractManualFromPdf(file: File): Promise<ApiResponse<ExperimentManualInfo>>

export async function detectExcelSheets(file: File): Promise<{
  success: boolean;
  sheets: SheetInfo[];
  total_sheets: number;
}>

export async function analyzeBatch(
  file: File,
  config: {
    experiments: ExperimentConfig[];
    report_title: string;
    manual_info?: ExperimentManualInfo;
  }
): Promise<ApiResponse<BatchAnalysisData>>

export async function generateFullReport(
  request: FullReportRequest
): Promise<{
  success: boolean;
  markdown_content: string;
  sections: ReportSections;
}>
```

---

## 8. 단계별 구현 순서

### Phase 1: Backend 스키마 및 파일 파서
1. `schemas.py`에 새 모델 추가
2. `file_parser.py`에 멀티시트/PDF 파싱 함수 추가
3. `config.py`에 PDF 설정 추가

### Phase 2: Backend 분석 및 그래프 서비스
1. `analysis_engine.py`에 배치 분석 메서드 추가
2. `graph_generator.py`에 멀티 그래프 생성 메서드 추가

### Phase 3: Gemini 서비스 확장
1. `gemini_service.py`에 PDF 추출 메서드 추가
2. `gemini_service.py`에 전체 리포트 생성 메서드 추가

### Phase 4: 리포트 생성기 및 API
1. `report_generator.py` 신규 생성
2. `analyze.py`에 새 엔드포인트 추가
3. `generate.py`에 새 엔드포인트 추가

### Phase 5: Frontend 구현
1. `types/index.ts`에 인터페이스 추가
2. `api.ts`에 API 함수 추가
3. 새 컴포넌트 4개 생성
4. `page.tsx` 멀티스텝 플로우로 수정

### Phase 6: 테스트 및 검증
1. Backend 단위 테스트
2. E2E 플로우 테스트

---

## 9. Gemini 프롬프트

### PDF 매뉴얼 추출 프롬프트
```
당신은 이공계 실험 매뉴얼 분석 전문가입니다.
첨부된 PDF 파일에서 다음 정보를 추출하여 JSON 형식으로 반환해주세요.

추출 항목:
1. experiment_purpose: 실험 목적 (1-3문장)
2. theory: 실험 이론 및 원리 (주요 수식 포함)
3. error_guides: 오차 원인 목록 [{cause, description, mitigation}]
4. expected_results: 예상 결과
5. equipment_list: 실험 기구 목록

JSON만 반환하세요.
```

### 전체 리포트 생성 프롬프트
```
당신은 이공계 실험 보고서 작성 전문가입니다.

입력:
- 리포트 제목
- 매뉴얼 정보 (목적, 이론, 오차 가이드)
- 실험 데이터 (통계, 그래프 정보)

출력 섹션:
1. 실험결과: 데이터 해석, 그래프 설명
2. 결과분석: R² 분석, 이론값 비교
3. 토의: 종합 고찰, 오차 분석, 개선방안

학술적 어조로 작성하세요.
```

---

## 10. 검증 방법

### Backend 테스트
```bash
cd backend
uvicorn app.main:app --reload --port 8000
# API 테스트: http://localhost:8000/docs
```

### Frontend 테스트
```bash
cd frontend
npm run dev
# 브라우저: http://localhost:3000
```

### E2E 시나리오
1. PDF 매뉴얼 업로드 → 추출 정보 확인
2. 멀티시트 Excel 업로드 → 시트 감지 확인
3. 시트별 설정 → 배치 분석 실행
4. 결과 확인 → 각 실험 그래프/통계 표시
5. 전체 리포트 생성 → 마크다운 다운로드
6. .md 파일 열어서 이미지 임베딩 확인

---

## 11. 하위 호환성

- 기존 `/api/analyze/data` 엔드포인트 유지
- 기존 단일 파일 분석 플로우 계속 작동
- 기존 `FileUploader.tsx` 컴포넌트 유지

---

## 12. 참고: 현재 프로젝트 구조

```
실험 데이터 분석기/
├── CLAUDE.md                    # 프로젝트 설계 문서
├── IMPLEMENTATION_PLAN.md       # 이 파일 (구현 계획)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/schemas.py
│   │   ├── routers/
│   │   │   ├── analyze.py
│   │   │   └── generate.py
│   │   ├── services/
│   │   │   ├── analysis_engine.py
│   │   │   ├── gemini_service.py
│   │   │   └── graph_generator.py
│   │   └── utils/file_parser.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── app/page.tsx
        ├── components/
        │   ├── FileUploader.tsx
        │   └── StatisticsCard.tsx
        ├── lib/api.ts
        └── types/index.ts
```
