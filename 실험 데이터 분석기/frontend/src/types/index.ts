/**
 * LabReportAI TypeScript Types
 * API 통신에 사용되는 타입 정의
 */

// ============================================================
// Statistics Types
// ============================================================

export interface StatisticsResult {
  slope: number;
  intercept: number;
  r_squared: number;
  std_error: number;
  error_rate_percent: number | null;
  data_points: number;
  x_range: [number, number];
  y_range: [number, number];
}

export interface GraphResult {
  image_base64: string;
  image_url: string | null;
}

export interface DataSummary {
  columns: string[];
  row_count: number;
  null_values_removed: number;
}

// ============================================================
// API Response Types
// ============================================================

export interface AnalysisData {
  analysis_id: string;
  statistics: StatisticsResult;
  graph: GraphResult;
  data_summary: DataSummary;
}

export interface AnalysisResponse {
  success: boolean;
  message: string;
  data: AnalysisData | null;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
  };
}

// ============================================================
// Component Props Types
// ============================================================

export interface FileUploaderProps {
  onAnalysisComplete: (result: AnalysisData) => void;
  onError: (message: string) => void;
}

export interface StatisticsCardProps {
  statistics: StatisticsResult;
}

export interface AnalysisState {
  isLoading: boolean;
  result: AnalysisData | null;
  error: string | null;
}

// ============================================================
// PDF Extraction Types (매뉴얼 정보 추출)
// ============================================================

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

export interface PDFExtractionResponse {
  success: boolean;
  message: string;
  data: ExperimentManualInfo | null;
}

// ============================================================
// Multi-Sheet Types (멀티시트 지원)
// ============================================================

export interface SheetInfo {
  sheet_name: string;
  columns: string[];
  row_count: number;
  sample_data: Record<string, unknown>[];
}

export interface MultiSheetDetectionResponse {
  success: boolean;
  message: string;
  sheets: SheetInfo[];
  total_sheets: number;
}

export interface ExperimentConfig {
  sheet_name: string;
  experiment_name: string;
  x_column: string;
  y_column: string;
  theoretical_slope?: number;
}

// ============================================================
// Batch Analysis Types (배치 분석)
// ============================================================

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

export interface BatchAnalysisResponse {
  success: boolean;
  message: string;
  data: BatchAnalysisData | null;
}

// ============================================================
// Report Generation Types (리포트 생성)
// ============================================================

export interface ReportOptions {
  language: string;
  include_data_tables: boolean;
  include_individual_analysis: boolean;
  tone: string;
}

export interface ReportSections {
  experiment_results: string;
  result_analysis: string;
  discussion: string;
}

export interface FullReportRequest {
  batch_id: string;
  report_title: string;
  experiments: SingleExperimentResult[];
  manual_info?: ExperimentManualInfo;
  options?: ReportOptions;
}

export interface FullReportResponse {
  success: boolean;
  message: string;
  markdown_content: string;
  sections: ReportSections;
}

// ============================================================
// UI State Types (멀티스텝 플로우 상태)
// ============================================================

export type AnalysisStep =
  | 'upload'        // 1단계: 파일 업로드
  | 'configure'     // 2단계: 시트별 설정
  | 'analyzing'     // 3단계: 분석 중
  | 'results'       // 4단계: 결과 확인
  | 'report';       // 5단계: 리포트 생성

export interface MultiStepState {
  currentStep: AnalysisStep;
  excelFile: File | null;
  pdfFile: File | null;
  sheets: SheetInfo[];
  experimentConfigs: ExperimentConfig[];
  manualInfo: ExperimentManualInfo | null;
  batchResults: BatchAnalysisData | null;
  reportTitle: string;
  markdownReport: string | null;
  isLoading: boolean;
  error: string | null;
}
