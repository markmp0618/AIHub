/**
 * LabReportAI API Client
 * FastAPI 백엔드와 통신하는 함수들
 */

import {
    AnalysisResponse,
    ErrorResponse,
    MultiSheetDetectionResponse,
    BatchAnalysisResponse,
    ExperimentConfig,
    ExperimentManualInfo,
    PDFExtractionResponse,
    FullReportRequest,
    FullReportResponse,
    SingleExperimentResult
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * 파일을 분석하고 통계 결과를 반환
 */
export async function analyzeData(
    file: File,
    title: string,
    xColumn: string,
    yColumn: string,
    theoreticalSlope?: number
): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('x_column', xColumn);
    formData.append('y_column', yColumn);

    if (theoreticalSlope !== undefined) {
        formData.append('theoretical_slope', theoreticalSlope.toString());
    }

    const response = await fetch(`${API_BASE_URL}/api/analyze/data`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.error?.message || '분석 중 오류가 발생했습니다.');
    }

    return response.json();
}

/**
 * 파일의 열 정보를 감지
 */
export async function detectColumns(file: File): Promise<{
    success: boolean;
    message: string;
    columns: Array<{ name: string; dtype: string; sample_values: string[] }>;
}> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/analyze/detect-columns`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('열 정보를 감지할 수 없습니다.');
    }

    return response.json();
}

/**
 * 헬스체크
 */
export async function healthCheck(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

/**
 * AI 고찰 생성
 */
export async function generateDiscussion(
    experimentTitle: string,
    statistics: {
        slope: number;
        intercept: number;
        r_squared: number;
        std_error: number;
        error_rate_percent: number | null;
        data_points: number;
        x_range: [number, number];
        y_range: [number, number];
    },
    context?: string
): Promise<{
    success: boolean;
    message: string;
    discussion: string | null;
    model_used: string | null;
}> {
    const response = await fetch(`${API_BASE_URL}/api/generate/discussion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            experiment_title: experimentTitle,
            statistics,
            context,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || '고찰 생성 중 오류가 발생했습니다.');
    }

    return response.json();
}

// ============================================================
// Multi-Sheet API Functions (멀티시트 지원)
// ============================================================

/**
 * Excel 파일의 시트 정보를 감지
 */
export async function detectExcelSheets(file: File): Promise<MultiSheetDetectionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/analyze/detect-sheets`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.error?.message || '시트 감지 중 오류가 발생했습니다.');
    }

    return response.json();
}

/**
 * 여러 시트의 데이터를 배치로 분석
 */
export async function analyzeBatch(
    file: File,
    config: {
        experiments: ExperimentConfig[];
        report_title: string;
        manual_info?: ExperimentManualInfo;
    }
): Promise<BatchAnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('experiments_json', JSON.stringify(config.experiments));
    formData.append('report_title', config.report_title);

    if (config.manual_info) {
        formData.append('manual_info_json', JSON.stringify(config.manual_info));
    }

    const response = await fetch(`${API_BASE_URL}/api/analyze/batch`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error: ErrorResponse = await response.json();
        throw new Error(error.error?.message || '배치 분석 중 오류가 발생했습니다.');
    }

    return response.json();
}

// ============================================================
// PDF Manual Extraction (매뉴얼 정보 추출)
// ============================================================

/**
 * PDF 매뉴얼에서 실험 정보를 추출
 */
export async function extractManualFromPdf(file: File): Promise<PDFExtractionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/generate/extract-manual`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || 'PDF 추출 중 오류가 발생했습니다.');
    }

    return response.json();
}

// ============================================================
// Full Report Generation (전체 리포트 생성)
// ============================================================

/**
 * 배치 분석 결과를 바탕으로 전체 마크다운 리포트 생성
 */
export async function generateFullReport(
    request: FullReportRequest
): Promise<FullReportResponse> {
    const response = await fetch(`${API_BASE_URL}/api/generate/full-report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || '리포트 생성 중 오류가 발생했습니다.');
    }

    return response.json();
}

/**
 * 마크다운 파일 다운로드 유틸리티
 */
export function downloadMarkdownReport(
    markdownContent: string,
    filename: string = 'report.md'
): void {
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
