"""
LabReportAI Analysis Engine (핵심)
Pandas + Scipy를 활용한 데이터 분석 로직
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Tuple, Dict, List
import uuid

from app.models.schemas import (
    StatisticsResult,
    DataSummary,
    ErrorCode,
    ExperimentConfig,
    SingleExperimentResult,
    GraphResult
)
from app.utils.file_parser import FileParserError


class AnalysisError(Exception):
    """분석 관련 커스텀 예외"""
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class AnalysisService:
    """
    데이터 분석 서비스 클래스
    
    Pandas DataFrame을 받아 선형 회귀 분석을 수행하고
    통계 결과를 반환합니다.
    """
    
    MIN_DATA_POINTS = 5  # 최소 데이터 포인트 수
    
    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        theoretical_slope: Optional[float] = None
    ) -> Tuple[StatisticsResult, DataSummary, pd.DataFrame]:
        """
        DataFrame을 분석하여 통계 결과를 반환
        
        Args:
            df: pandas DataFrame
            x_column: X축 열 이름
            y_column: Y축 열 이름
            theoretical_slope: 이론적 기울기 (오차율 계산용, 옵션)
            
        Returns:
            Tuple[StatisticsResult, DataSummary, pd.DataFrame]: 
                통계 결과, 데이터 요약, 전처리된 DataFrame
                
        Raises:
            AnalysisError: 분석 실패 시
        """
        # 1. 데이터 전처리
        cleaned_df, null_removed = self._preprocess_data(df, x_column, y_column)
        
        # 2. 데이터 포인트 수 확인
        if len(cleaned_df) < self.MIN_DATA_POINTS:
            raise AnalysisError(
                code=ErrorCode.INSUFFICIENT_DATA,
                message=f"최소 {self.MIN_DATA_POINTS}개 이상의 데이터 포인트가 필요합니다. 현재: {len(cleaned_df)}개"
            )
        
        # 3. 통계 분석 수행
        statistics = self._perform_regression(
            cleaned_df[x_column].values,
            cleaned_df[y_column].values,
            theoretical_slope
        )
        
        # 4. 데이터 요약 생성
        data_summary = DataSummary(
            columns=df.columns.tolist(),
            row_count=len(cleaned_df),
            null_values_removed=null_removed
        )
        
        return statistics, data_summary, cleaned_df
    
    def _preprocess_data(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str
    ) -> Tuple[pd.DataFrame, int]:
        """
        데이터 전처리: 결측치 제거, 숫자형 변환
        
        Args:
            df: 원본 DataFrame
            x_column: X축 열 이름
            y_column: Y축 열 이름
            
        Returns:
            Tuple[pd.DataFrame, int]: 전처리된 DataFrame, 제거된 결측치 수
        """
        # 복사본 생성
        df_copy = df[[x_column, y_column]].copy()
        
        # 숫자형 변환
        df_copy[x_column] = pd.to_numeric(df_copy[x_column], errors='coerce')
        df_copy[y_column] = pd.to_numeric(df_copy[y_column], errors='coerce')
        
        # 원본 행 수
        original_count = len(df_copy)
        
        # 결측치 제거
        df_copy = df_copy.dropna()
        
        # 제거된 행 수
        null_removed = original_count - len(df_copy)
        
        return df_copy, null_removed
    
    def _perform_regression(
        self,
        x: np.ndarray,
        y: np.ndarray,
        theoretical_slope: Optional[float] = None
    ) -> StatisticsResult:
        """
        선형 회귀 분석 수행
        
        Args:
            x: X 데이터 배열
            y: Y 데이터 배열
            theoretical_slope: 이론적 기울기 (옵션)
            
        Returns:
            StatisticsResult: 통계 분석 결과
        """
        try:
            # scipy.stats.linregress 사용
            result = stats.linregress(x, y)
            
            slope = result.slope
            intercept = result.intercept
            r_value = result.rvalue
            std_error = result.stderr
            
            # R² (결정계수) 계산
            r_squared = r_value ** 2
            
            # 오차율 계산 (이론값이 주어진 경우)
            error_rate_percent = None
            if theoretical_slope is not None and theoretical_slope != 0:
                error_rate_percent = abs((slope - theoretical_slope) / theoretical_slope) * 100
            
            return StatisticsResult(
                slope=round(slope, 6),
                intercept=round(intercept, 6),
                r_squared=round(r_squared, 6),
                std_error=round(std_error, 6),
                error_rate_percent=round(error_rate_percent, 2) if error_rate_percent else None,
                data_points=len(x),
                x_range=(round(float(x.min()), 4), round(float(x.max()), 4)),
                y_range=(round(float(y.min()), 4), round(float(y.max()), 4))
            )
            
        except Exception as e:
            raise AnalysisError(
                code=ErrorCode.ANALYSIS_FAILED,
                message=f"회귀 분석 중 오류가 발생했습니다: {str(e)}"
            )
    
    @staticmethod
    def generate_analysis_id() -> str:
        """고유 분석 ID 생성"""
        return str(uuid.uuid4())

    def analyze_batch(
        self,
        sheets_data: Dict[str, pd.DataFrame],
        experiments: List[ExperimentConfig]
    ) -> List[Tuple[StatisticsResult, DataSummary, pd.DataFrame, List[dict]]]:
        """
        여러 시트의 데이터를 배치로 분석

        Args:
            sheets_data: {시트이름: DataFrame} 형태의 딕셔너리
            experiments: 실험 설정 목록

        Returns:
            List[Tuple[StatisticsResult, DataSummary, pd.DataFrame, List[dict]]]:
                각 실험에 대한 (통계결과, 데이터요약, 전처리된DataFrame, 데이터테이블) 튜플 리스트

        Raises:
            AnalysisError: 분석 실패 시
        """
        results = []

        for exp_config in experiments:
            sheet_name = exp_config.sheet_name

            # 시트 존재 확인
            if sheet_name not in sheets_data:
                raise AnalysisError(
                    code=ErrorCode.COLUMN_NOT_FOUND,
                    message=f"'{sheet_name}' 시트를 찾을 수 없습니다. 사용 가능한 시트: {list(sheets_data.keys())}"
                )

            df = sheets_data[sheet_name]

            # 개별 분석 수행
            statistics, data_summary, cleaned_df = self.analyze_dataframe(
                df=df,
                x_column=exp_config.x_column,
                y_column=exp_config.y_column,
                theoretical_slope=exp_config.theoretical_slope
            )

            # 데이터 테이블 생성
            data_table = self.dataframe_to_table(
                cleaned_df,
                exp_config.x_column,
                exp_config.y_column
            )

            results.append((statistics, data_summary, cleaned_df, data_table))

        return results

    def dataframe_to_table(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        max_rows: int = 50
    ) -> List[dict]:
        """
        DataFrame을 마크다운 테이블용 딕셔너리 리스트로 변환

        Args:
            df: pandas DataFrame
            x_col: X축 열 이름
            y_col: Y축 열 이름
            max_rows: 최대 행 수 (기본 50)

        Returns:
            List[dict]: [{x_col: value, y_col: value}, ...] 형태
        """
        # 행 수 제한
        if len(df) > max_rows:
            df = df.head(max_rows)

        # 딕셔너리 리스트로 변환
        table_data = df[[x_col, y_col]].to_dict(orient='records')

        # NaN 값 처리 및 반올림
        cleaned_table = []
        for row in table_data:
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned_row[key] = None
                elif isinstance(value, float):
                    cleaned_row[key] = round(value, 6)
                else:
                    cleaned_row[key] = value
            cleaned_table.append(cleaned_row)

        return cleaned_table


# 서비스 인스턴스 (싱글톤)
analysis_service = AnalysisService()
