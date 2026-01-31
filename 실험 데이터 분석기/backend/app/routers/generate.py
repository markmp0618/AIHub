"""
Generate Router
AI 고찰 생성 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import (
    DiscussionRequest,
    DiscussionResponse,
    PDFExtractionResponse,
    FullReportRequest,
    FullReportResponse,
    ReportOptions
)
from app.services.gemini_service import get_gemini_service
from app.services.report_generator import report_generator
from app.utils.file_parser import parse_pdf_file, FileParserError
from app.config import settings

router = APIRouter(prefix="/api/generate", tags=["Generate"])


@router.post("/discussion", response_model=DiscussionResponse)
async def generate_discussion(request: DiscussionRequest) -> DiscussionResponse:
    """
    실험 결과에 대한 AI 고찰 생성
    
    - Gemini 2.5 Flash를 사용하여 실험 보고서의 고찰 섹션을 자동 생성합니다.
    - 통계 분석 결과를 바탕으로 결과 분석, R² 해석, 오차 분석, 결론을 포함합니다.
    """
    
    # Gemini API 키 확인
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GEMINI_API_NOT_CONFIGURED",
                "message": "Gemini API 키가 설정되지 않았습니다. .env 파일에 GEMINI_API_KEY를 설정해주세요."
            }
        )
    
    try:
        gemini_service = get_gemini_service()
        
        response = gemini_service.generate_discussion(
            experiment_title=request.experiment_title,
            statistics=request.statistics,
            context=request.context
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GEMINI_INIT_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "GENERATION_FAILED",
                "message": f"고찰 생성 중 오류가 발생했습니다: {str(e)}"
            }
        )


@router.get("/status")
async def generation_status():
    """AI 생성 서비스 상태 확인"""
    return {
        "service": "gemini",
        "model": "gemini-2.5-flash-preview-05-20",
        "configured": bool(settings.gemini_api_key),
        "status": "ready" if settings.gemini_api_key else "not_configured"
    }


# ============================================================
# PDF Manual Extraction (매뉴얼 정보 추출)
# ============================================================

@router.post("/extract-manual", response_model=PDFExtractionResponse)
async def extract_manual(
    file: UploadFile = File(..., description="PDF 매뉴얼 파일")
):
    """
    PDF 매뉴얼에서 실험 정보를 추출합니다.

    Gemini AI를 사용하여 PDF에서 다음 정보를 추출합니다:
    - 실험 목적
    - 이론 및 원리
    - 오차 원인 가이드
    - 예상 결과
    - 실험 기구 목록

    Returns:
        추출된 매뉴얼 정보 (ExperimentManualInfo)
    """
    # API 키 확인
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GEMINI_API_NOT_CONFIGURED",
                "message": "Gemini API 키가 설정되지 않았습니다."
            }
        )

    try:
        # 1. PDF 파일 읽기
        pdf_bytes = await parse_pdf_file(file)
        filename = file.filename or "unknown.pdf"

        # 2. Gemini로 매뉴얼 정보 추출
        gemini_service = get_gemini_service()
        manual_info = gemini_service.extract_manual_from_pdf(pdf_bytes, filename)

        return PDFExtractionResponse(
            success=True,
            message="PDF 매뉴얼에서 정보를 성공적으로 추출했습니다.",
            data=manual_info
        )

    except FileParserError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": e.code.value,
                    "message": e.message
                }
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXTRACTION_FAILED",
                "message": f"PDF 추출 중 오류가 발생했습니다: {str(e)}"
            }
        )


# ============================================================
# Full Report Generation (전체 리포트 생성)
# ============================================================

@router.post("/full-report", response_model=FullReportResponse)
async def generate_full_report(request: FullReportRequest):
    """
    배치 분석 결과를 바탕으로 전체 마크다운 리포트를 생성합니다.

    Gemini AI를 사용하여 다음 섹션을 생성합니다:
    - 실험 결과 해석
    - 결과 분석
    - 토의 (오차 분석 포함)

    그리고 데이터 테이블, 그래프 이미지를 포함한 완전한 마크다운 리포트를 조립합니다.

    Returns:
        완전한 마크다운 리포트 및 섹션별 텍스트
    """
    # API 키 확인
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GEMINI_API_NOT_CONFIGURED",
                "message": "Gemini API 키가 설정되지 않았습니다."
            }
        )

    try:
        gemini_service = get_gemini_service()

        # 1. AI로 리포트 섹션 생성
        ai_response = gemini_service.generate_full_report(
            report_title=request.report_title,
            experiments=request.experiments,
            manual_info=request.manual_info,
            options=request.options
        )

        # 2. 마크다운 리포트 조립 (데이터 테이블 + 그래프 이미지 포함)
        markdown_content = report_generator.generate_markdown_report(
            report_title=request.report_title,
            experiments=request.experiments,
            generated_sections=ai_response.sections,
            manual_info=request.manual_info
        )

        return FullReportResponse(
            success=True,
            message="전체 리포트가 성공적으로 생성되었습니다.",
            markdown_content=markdown_content,
            sections=ai_response.sections
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "REPORT_GENERATION_FAILED",
                "message": f"리포트 생성 중 오류가 발생했습니다: {str(e)}"
            }
        )
