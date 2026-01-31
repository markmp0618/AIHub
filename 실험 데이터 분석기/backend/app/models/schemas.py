"""
LabReportAI Pydantic Schemas
Request/Response 모델 정의
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Tuple
from enum import Enum


# ============================================================
# Common Models
# ============================================================

class ErrorCode(str, Enum):
    """에러 코드 열거형"""
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    COLUMN_NOT_FOUND = "COLUMN_NOT_FOUND"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    code: ErrorCode
    message: str


class ApiResponse(BaseModel):
    """기본 API 응답 형식"""
    success: bool
    message: str


# ============================================================
# Analysis Models
# ============================================================

class StatisticsResult(BaseModel):
    """통계 분석 결과"""
    slope: float = Field(..., description="기울기")
    intercept: float = Field(..., description="y절편")
    r_squared: float = Field(..., description="결정계수 (R²)")
    std_error: float = Field(..., description="표준 오차")
    error_rate_percent: Optional[float] = Field(None, description="오차율 (%)")
    data_points: int = Field(..., description="데이터 포인트 수")
    x_range: Tuple[float, float] = Field(..., description="X축 범위 (min, max)")
    y_range: Tuple[float, float] = Field(..., description="Y축 범위 (min, max)")


class GraphResult(BaseModel):
    """그래프 생성 결과"""
    image_base64: str = Field(..., description="Base64 인코딩된 PNG 이미지")
    image_url: Optional[str] = Field(None, description="저장된 이미지 URL (옵션)")


class DataSummary(BaseModel):
    """데이터 요약 정보"""
    columns: List[str] = Field(..., description="열 이름 목록")
    row_count: int = Field(..., description="총 행 수")
    null_values_removed: int = Field(0, description="제거된 결측치 수")


class AnalysisData(BaseModel):
    """분석 결과 데이터"""
    analysis_id: str = Field(..., description="분석 ID")
    statistics: StatisticsResult
    graph: GraphResult
    data_summary: DataSummary


class AnalysisResponse(ApiResponse):
    """분석 API 성공 응답"""
    data: Optional[AnalysisData] = None


class AnalysisErrorResponse(BaseModel):
    """분석 API 에러 응답"""
    success: bool = False
    error: ErrorDetail


# ============================================================
# Request Models (Form Data - 파일 업로드용)
# ============================================================

class AnalysisRequest(BaseModel):
    """분석 요청 (참고용 - 실제로는 Form으로 받음)"""
    title: str = Field(..., description="실험 제목", examples=["RC 회로 시정수 측정 실험"])
    x_column: str = Field(..., description="X축 열 이름", examples=["time"])
    y_column: str = Field(..., description="Y축 열 이름", examples=["voltage"])
    preset_id: Optional[str] = Field(None, description="실험 프리셋 ID")
    theoretical_slope: Optional[float] = Field(None, description="이론적 기울기 (오차율 계산용)")


# ============================================================
# Column Detection Models
# ============================================================

class ColumnInfo(BaseModel):
    """열 정보"""
    name: str
    dtype: str
    sample_values: List[str]


class ColumnDetectionResponse(ApiResponse):
    """열 감지 응답"""
    columns: List[ColumnInfo] = []


# ============================================================
# Discussion Generation Models (Step 3 - Gemini AI)
# ============================================================

class DiscussionRequest(BaseModel):
    """고찰 생성 요청"""
    experiment_title: str = Field(..., description="실험 제목")
    statistics: StatisticsResult = Field(..., description="통계 분석 결과")
    context: Optional[str] = Field(None, description="추가 맥락 정보")


class DiscussionResponse(ApiResponse):
    """고찰 생성 응답"""
    discussion: Optional[str] = Field(None, description="생성된 고찰 텍스트 (Markdown)")
    model_used: Optional[str] = Field(None, description="사용된 AI 모델명")


# ============================================================
# PDF Manual Extraction Models (멀티 리포트 확장)
# ============================================================

class ErrorGuideItem(BaseModel):
    """오차 원인 항목"""
    cause: str = Field(..., description="오차 원인")
    description: str = Field(..., description="오차 설명")
    mitigation: Optional[str] = Field(None, description="개선 방안")


class ExperimentManualInfo(BaseModel):
    """PDF 매뉴얼에서 추출된 실험 정보"""
    experiment_purpose: str = Field(..., description="실험 목적")
    theory: str = Field(..., description="실험 이론 및 원리")
    error_guides: List[ErrorGuideItem] = Field(default_factory=list, description="오차 원인 목록")
    expected_results: Optional[str] = Field(None, description="예상 결과")
    equipment_list: Optional[List[str]] = Field(None, description="실험 기구 목록")


class PDFExtractionResponse(ApiResponse):
    """PDF 추출 응답"""
    data: Optional[ExperimentManualInfo] = None


# ============================================================
# Multi-Sheet Detection Models (멀티시트 Excel 지원)
# ============================================================

class SheetInfo(BaseModel):
    """Excel 시트 정보"""
    sheet_name: str = Field(..., description="시트 이름")
    columns: List[str] = Field(..., description="열 이름 목록")
    row_count: int = Field(..., description="데이터 행 수")
    sample_data: List[dict] = Field(default_factory=list, description="샘플 데이터 (최대 5행)")


class MultiSheetDetectionResponse(ApiResponse):
    """멀티시트 감지 응답"""
    sheets: List[SheetInfo] = Field(default_factory=list, description="시트 정보 목록")
    total_sheets: int = Field(0, description="총 시트 수")


class ExperimentConfig(BaseModel):
    """개별 실험 설정"""
    sheet_name: str = Field(..., description="시트 이름")
    experiment_name: str = Field(..., description="실험 이름")
    x_column: str = Field(..., description="X축 열 이름")
    y_column: str = Field(..., description="Y축 열 이름")
    theoretical_slope: Optional[float] = Field(None, description="이론적 기울기 (오차율 계산용)")


# ============================================================
# Batch Analysis Models (배치 분석)
# ============================================================

class BatchAnalysisRequest(BaseModel):
    """배치 분석 요청"""
    experiments: List[ExperimentConfig] = Field(..., description="실험 설정 목록")
    report_title: str = Field(..., description="리포트 제목")
    manual_info: Optional[ExperimentManualInfo] = Field(None, description="매뉴얼 정보 (PDF에서 추출)")


class SingleExperimentResult(BaseModel):
    """단일 실험 분석 결과"""
    experiment_name: str = Field(..., description="실험 이름")
    sheet_name: str = Field(..., description="시트 이름")
    statistics: StatisticsResult = Field(..., description="통계 분석 결과")
    graph: GraphResult = Field(..., description="그래프 결과")
    data_summary: DataSummary = Field(..., description="데이터 요약")
    data_table: List[dict] = Field(default_factory=list, description="데이터 테이블 (Markdown용)")


class BatchAnalysisData(BaseModel):
    """배치 분석 결과 데이터"""
    batch_id: str = Field(..., description="배치 분석 ID")
    report_title: str = Field(..., description="리포트 제목")
    experiments: List[SingleExperimentResult] = Field(default_factory=list, description="실험 결과 목록")
    total_experiments: int = Field(..., description="총 실험 수")
    manual_info: Optional[ExperimentManualInfo] = Field(None, description="매뉴얼 정보")


class BatchAnalysisResponse(ApiResponse):
    """배치 분석 응답"""
    data: Optional[BatchAnalysisData] = None


# ============================================================
# Full Report Generation Models (전체 리포트 생성)
# ============================================================

class ReportOptions(BaseModel):
    """리포트 생성 옵션"""
    language: str = Field("ko", description="언어 (ko, en)")
    include_data_tables: bool = Field(True, description="데이터 테이블 포함 여부")
    include_individual_analysis: bool = Field(True, description="개별 실험 분석 포함 여부")
    tone: str = Field("academic", description="문체 (academic, casual)")


class ReportSections(BaseModel):
    """리포트 섹션"""
    experiment_results: str = Field(..., description="실험 결과 섹션")
    result_analysis: str = Field(..., description="결과 분석 섹션")
    discussion: str = Field(..., description="토의 섹션")


class FullReportRequest(BaseModel):
    """전체 리포트 생성 요청"""
    batch_id: str = Field(..., description="배치 분석 ID")
    report_title: str = Field(..., description="리포트 제목")
    experiments: List[SingleExperimentResult] = Field(..., description="실험 결과 목록")
    manual_info: Optional[ExperimentManualInfo] = Field(None, description="매뉴얼 정보")
    options: Optional[ReportOptions] = Field(None, description="리포트 옵션")


class FullReportResponse(ApiResponse):
    """전체 리포트 생성 응답"""
    markdown_content: Optional[str] = Field(None, description="마크다운 리포트 전체 내용")
    sections: Optional[ReportSections] = Field(None, description="섹션별 내용")
