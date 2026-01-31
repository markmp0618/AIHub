"""
LabReportAI File Parser
CSV/Excel/PDF 파일 파싱 유틸리티
"""

import pandas as pd
from fastapi import UploadFile
from typing import List, Dict
import io

from app.config import settings
from app.models.schemas import ErrorCode, SheetInfo


class FileParserError(Exception):
    """파일 파싱 관련 커스텀 예외"""
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


async def parse_uploaded_file(file: UploadFile) -> pd.DataFrame:
    """
    업로드된 파일을 DataFrame으로 변환
    
    Args:
        file: FastAPI UploadFile 객체
        
    Returns:
        pd.DataFrame: 파싱된 데이터
        
    Raises:
        FileParserError: 파일 파싱 실패 시
    """
    # 파일 확장자 확인
    filename = file.filename or ""
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""
    
    if extension not in settings.allowed_extensions:
        raise FileParserError(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message=f"지원하지 않는 파일 형식입니다. 허용 형식: {', '.join(settings.allowed_extensions)}"
        )
    
    # 파일 크기 확인
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    if file_size_mb > settings.max_file_size_mb:
        raise FileParserError(
            code=ErrorCode.FILE_TOO_LARGE,
            message=f"파일 크기가 너무 큽니다. 최대 {settings.max_file_size_mb}MB까지 허용됩니다."
        )
    
    # 파일 파싱
    try:
        if extension == ".csv":
            # CSV 파일
            df = pd.read_csv(io.BytesIO(content))
        else:
            # Excel 파일 (.xlsx, .xls)
            df = pd.read_excel(io.BytesIO(content))
        
        return df
        
    except Exception as e:
        raise FileParserError(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message=f"파일을 읽을 수 없습니다: {str(e)}"
        )


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    DataFrame에서 숫자형 열 목록 반환
    
    Args:
        df: pandas DataFrame
        
    Returns:
        List[str]: 숫자형 열 이름 목록
    """
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()


def validate_columns(df: pd.DataFrame, x_column: str, y_column: str) -> None:
    """
    지정된 열이 DataFrame에 존재하고 숫자형인지 확인
    
    Args:
        df: pandas DataFrame
        x_column: X축 열 이름
        y_column: Y축 열 이름
        
    Raises:
        FileParserError: 열이 없거나 숫자형이 아닐 경우
    """
    available_columns = df.columns.tolist()
    
    if x_column not in available_columns:
        raise FileParserError(
            code=ErrorCode.COLUMN_NOT_FOUND,
            message=f"'{x_column}' 열을 찾을 수 없습니다. 사용 가능한 열: {available_columns}"
        )
    
    if y_column not in available_columns:
        raise FileParserError(
            code=ErrorCode.COLUMN_NOT_FOUND,
            message=f"'{y_column}' 열을 찾을 수 없습니다. 사용 가능한 열: {available_columns}"
        )
    
    # 숫자형 변환 시도
    try:
        df[x_column] = pd.to_numeric(df[x_column], errors='coerce')
        df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
    except Exception as e:
        raise FileParserError(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message=f"열 데이터를 숫자로 변환할 수 없습니다: {str(e)}"
        )


# ============================================================
# Multi-Sheet Excel Parsing (멀티시트 지원)
# ============================================================

async def parse_excel_all_sheets(file: UploadFile) -> Dict[str, pd.DataFrame]:
    """
    Excel 파일의 모든 시트를 파싱하여 Dict로 반환

    Args:
        file: FastAPI UploadFile 객체 (Excel 파일)

    Returns:
        Dict[str, pd.DataFrame]: {시트이름: DataFrame} 형태

    Raises:
        FileParserError: 파일 파싱 실패 시
    """
    filename = file.filename or ""
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in [".xlsx", ".xls"]:
        raise FileParserError(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message="멀티시트 파싱은 Excel 파일(.xlsx, .xls)만 지원합니다."
        )

    content = await file.read()
    await file.seek(0)  # 파일 포인터 초기화

    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise FileParserError(
            code=ErrorCode.FILE_TOO_LARGE,
            message=f"파일 크기가 너무 큽니다. 최대 {settings.max_file_size_mb}MB까지 허용됩니다."
        )

    try:
        # 모든 시트를 Dict로 읽기
        excel_file = pd.ExcelFile(io.BytesIO(content))
        sheets_data: Dict[str, pd.DataFrame] = {}

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # 빈 시트 제외
            if not df.empty:
                sheets_data[sheet_name] = df

        return sheets_data

    except Exception as e:
        raise FileParserError(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message=f"Excel 파일을 읽을 수 없습니다: {str(e)}"
        )


async def detect_multi_sheets(file: UploadFile) -> List[SheetInfo]:
    """
    Excel 파일의 시트 정보를 감지하여 반환

    Args:
        file: FastAPI UploadFile 객체 (Excel 파일)

    Returns:
        List[SheetInfo]: 시트 정보 목록

    Raises:
        FileParserError: 파일 파싱 실패 시
    """
    sheets_data = await parse_excel_all_sheets(file)

    sheet_info_list: List[SheetInfo] = []

    for sheet_name, df in sheets_data.items():
        # 샘플 데이터 (최대 5행)
        sample_rows = df.head(5).to_dict(orient='records')
        # NaN 값을 None으로 변환
        sample_data = [
            {k: (None if pd.isna(v) else v) for k, v in row.items()}
            for row in sample_rows
        ]

        sheet_info = SheetInfo(
            sheet_name=sheet_name,
            columns=df.columns.tolist(),
            row_count=len(df),
            sample_data=sample_data
        )
        sheet_info_list.append(sheet_info)

    return sheet_info_list


# ============================================================
# PDF Parsing (PDF 매뉴얼 지원)
# ============================================================

async def parse_pdf_file(file: UploadFile) -> bytes:
    """
    PDF 파일을 읽어서 바이트로 반환 (Gemini API에서 처리)

    Args:
        file: FastAPI UploadFile 객체 (PDF 파일)

    Returns:
        bytes: PDF 파일 바이트 데이터

    Raises:
        FileParserError: 파일 파싱 실패 시
    """
    filename = file.filename or ""
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if extension != ".pdf":
        raise FileParserError(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message="PDF 파일(.pdf)만 지원합니다."
        )

    content = await file.read()
    await file.seek(0)  # 파일 포인터 초기화

    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.max_pdf_size_mb:
        raise FileParserError(
            code=ErrorCode.FILE_TOO_LARGE,
            message=f"PDF 파일 크기가 너무 큽니다. 최대 {settings.max_pdf_size_mb}MB까지 허용됩니다."
        )

    return content


async def get_pdf_info(file: UploadFile) -> dict:
    """
    PDF 파일의 기본 정보 반환

    Args:
        file: FastAPI UploadFile 객체 (PDF 파일)

    Returns:
        dict: PDF 파일 정보 (filename, size_mb)
    """
    content = await file.read()
    await file.seek(0)

    return {
        "filename": file.filename,
        "size_mb": round(len(content) / (1024 * 1024), 2)
    }
