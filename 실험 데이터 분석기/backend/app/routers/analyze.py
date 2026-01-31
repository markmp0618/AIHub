"""
LabReportAI Analyze Router
/api/analyze/* 엔드포인트 정의
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
import json

from app.models.schemas import (
    AnalysisResponse,
    AnalysisData,
    AnalysisErrorResponse,
    ErrorDetail,
    ErrorCode,
    ColumnInfo,
    ColumnDetectionResponse,
    MultiSheetDetectionResponse,
    ExperimentConfig,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    BatchAnalysisData,
    SingleExperimentResult,
    ExperimentManualInfo
)
from app.services.analysis_engine import analysis_service, AnalysisError
from app.services.graph_generator import graph_generator
from app.utils.file_parser import (
    parse_uploaded_file,
    validate_columns,
    get_numeric_columns,
    FileParserError,
    parse_excel_all_sheets,
    detect_multi_sheets
)


router = APIRouter(prefix="/api/analyze", tags=["Analysis"])


@router.post("/data", response_model=AnalysisResponse)
async def analyze_data(
    file: UploadFile = File(..., description="CSV 또는 Excel 파일"),
    title: str = Form(..., description="실험 제목"),
    x_column: str = Form(..., description="X축 열 이름"),
    y_column: str = Form(..., description="Y축 열 이름"),
    theoretical_slope: Optional[float] = Form(None, description="이론적 기울기 (오차율 계산용)")
):
    """
    실험 데이터 파일을 업로드하고 통계 분석을 수행합니다.
    
    - **file**: CSV(.csv) 또는 Excel(.xlsx, .xls) 파일
    - **title**: 실험 제목 (예: "RC 회로 시정수 측정 실험")
    - **x_column**: X축으로 사용할 열 이름
    - **y_column**: Y축으로 사용할 열 이름
    - **theoretical_slope**: (선택) 이론적 기울기값 - 오차율 계산에 사용
    
    Returns:
        통계 분석 결과 및 그래프 이미지
    """
    try:
        # 1. 파일 파싱
        df = await parse_uploaded_file(file)
        
        # 2. 열 유효성 검사
        validate_columns(df, x_column, y_column)
        
        # 3. 통계 분석 수행
        statistics, data_summary, cleaned_df = analysis_service.analyze_dataframe(
            df=df,
            x_column=x_column,
            y_column=y_column,
            theoretical_slope=theoretical_slope
        )
        
        # 4. 그래프 생성
        graph_result = graph_generator.generate_scatter_with_trendline(
            df=cleaned_df,
            x_column=x_column,
            y_column=y_column,
            statistics=statistics,
            title=title
        )
        
        # 5. 분석 ID 생성
        analysis_id = analysis_service.generate_analysis_id()
        
        # 6. 응답 반환
        return AnalysisResponse(
            success=True,
            message="분석이 완료되었습니다.",
            data=AnalysisData(
                analysis_id=analysis_id,
                statistics=statistics,
                graph=graph_result,
                data_summary=data_summary
            )
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
        
    except AnalysisError as e:
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
                "success": False,
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": f"서버 내부 오류가 발생했습니다: {str(e)}"
                }
            }
        )


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    file: UploadFile = File(..., description="CSV 또는 Excel 파일")
):
    """
    업로드된 파일의 열 정보를 감지합니다.
    
    프론트엔드에서 X/Y축 선택 드롭다운을 채우기 위해 사용합니다.
    """
    try:
        # 파일 파싱
        df = await parse_uploaded_file(file)
        
        # 숫자형 열만 필터링
        numeric_cols = get_numeric_columns(df)
        
        # 열 정보 생성
        columns = []
        for col in df.columns:
            sample_values = df[col].head(3).astype(str).tolist()
            columns.append(ColumnInfo(
                name=col,
                dtype=str(df[col].dtype),
                sample_values=sample_values
            ))
        
        return ColumnDetectionResponse(
            success=True,
            message=f"총 {len(columns)}개의 열이 감지되었습니다. (숫자형: {len(numeric_cols)}개)",
            columns=columns
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


# ============================================================
# Multi-Sheet Endpoints (멀티시트 지원)
# ============================================================

@router.post("/detect-sheets", response_model=MultiSheetDetectionResponse)
async def detect_sheets(
    file: UploadFile = File(..., description="Excel 파일 (.xlsx, .xls)")
):
    """
    Excel 파일의 시트 정보를 감지합니다.

    멀티시트 배치 분석 전에 시트 목록과 열 정보를 확인하기 위해 사용합니다.

    Returns:
        각 시트의 이름, 열 목록, 행 수, 샘플 데이터
    """
    try:
        sheet_info_list = await detect_multi_sheets(file)

        return MultiSheetDetectionResponse(
            success=True,
            message=f"총 {len(sheet_info_list)}개의 시트가 감지되었습니다.",
            sheets=sheet_info_list,
            total_sheets=len(sheet_info_list)
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
                "success": False,
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": f"시트 감지 중 오류가 발생했습니다: {str(e)}"
                }
            }
        )


@router.post("/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(
    file: UploadFile = File(..., description="Excel 파일 (.xlsx, .xls)"),
    experiments_json: str = Form(..., description="실험 설정 JSON (List[ExperimentConfig])"),
    report_title: str = Form(..., description="리포트 제목"),
    manual_info_json: Optional[str] = Form(None, description="매뉴얼 정보 JSON (ExperimentManualInfo)")
):
    """
    여러 시트의 데이터를 배치로 분석합니다.

    - **file**: Excel 파일 (멀티시트)
    - **experiments_json**: 각 실험 설정 (JSON 문자열)
    - **report_title**: 리포트 제목
    - **manual_info_json**: (선택) PDF에서 추출한 매뉴얼 정보

    Returns:
        각 실험의 통계 분석 결과, 그래프, 데이터 테이블
    """
    try:
        # 1. JSON 파싱
        experiments_data = json.loads(experiments_json)
        experiments = [ExperimentConfig(**exp) for exp in experiments_data]

        manual_info = None
        if manual_info_json:
            manual_data = json.loads(manual_info_json)
            manual_info = ExperimentManualInfo(**manual_data)

        # 2. 모든 시트 파싱
        sheets_data = await parse_excel_all_sheets(file)

        # 3. 배치 분석 수행
        analysis_results = analysis_service.analyze_batch(
            sheets_data=sheets_data,
            experiments=experiments
        )

        # 4. 그래프 배치 생성을 위한 데이터 준비
        graph_input_data = []
        for i, (stats, data_summary, cleaned_df, data_table) in enumerate(analysis_results):
            exp_config = experiments[i]
            graph_input_data.append((
                cleaned_df,
                exp_config.x_column,
                exp_config.y_column,
                stats,
                exp_config.experiment_name
            ))

        # 5. 그래프 배치 생성
        graph_results = graph_generator.generate_batch_graphs(graph_input_data)

        # 6. 결과 조립
        experiment_results: List[SingleExperimentResult] = []
        for i, (stats, data_summary, cleaned_df, data_table) in enumerate(analysis_results):
            exp_config = experiments[i]
            graph_result = graph_results[i]

            experiment_results.append(SingleExperimentResult(
                experiment_name=exp_config.experiment_name,
                sheet_name=exp_config.sheet_name,
                statistics=stats,
                graph=graph_result,
                data_summary=data_summary,
                data_table=data_table
            ))

        # 7. 배치 ID 생성
        batch_id = analysis_service.generate_analysis_id()

        return BatchAnalysisResponse(
            success=True,
            message=f"{len(experiments)}개 실험의 배치 분석이 완료되었습니다.",
            data=BatchAnalysisData(
                batch_id=batch_id,
                report_title=report_title,
                experiments=experiment_results,
                total_experiments=len(experiments),
                manual_info=manual_info
            )
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "JSON_PARSE_ERROR",
                    "message": f"JSON 파싱 오류: {str(e)}"
                }
            }
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

    except AnalysisError as e:
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
                "success": False,
                "error": {
                    "code": ErrorCode.INTERNAL_ERROR.value,
                    "message": f"배치 분석 중 오류가 발생했습니다: {str(e)}"
                }
            }
        )
