"""
LabReportAI Analysis Engine Tests
분석 엔진 단위 테스트
"""

import pytest
import pandas as pd
import numpy as np
from io import BytesIO

from app.services.analysis_engine import AnalysisService, AnalysisError
from app.services.graph_generator import GraphGenerator
from app.models.schemas import ErrorCode


class TestAnalysisService:
    """AnalysisService 테스트"""
    
    @pytest.fixture
    def service(self):
        """분석 서비스 인스턴스"""
        return AnalysisService()
    
    @pytest.fixture
    def sample_dataframe(self):
        """테스트용 샘플 데이터"""
        # y = 10x (완벽한 선형 관계)
        return pd.DataFrame({
            'time': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            'voltage': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        })
    
    @pytest.fixture
    def noisy_dataframe(self):
        """노이즈가 있는 테스트 데이터"""
        return pd.DataFrame({
            'time': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            'voltage': [1.1, 1.9, 3.1, 3.9, 5.2, 5.8, 7.1, 8.0, 9.2, 9.9]
        })
    
    def test_analyze_perfect_linear_data(self, service, sample_dataframe):
        """완벽한 선형 데이터 분석 테스트"""
        stats, summary, df = service.analyze_dataframe(
            df=sample_dataframe,
            x_column='time',
            y_column='voltage'
        )
        
        # 기울기 확인 (약 10)
        assert abs(stats.slope - 10.0) < 0.01, f"Expected slope ~10, got {stats.slope}"
        
        # R² 확인 (1에 가까워야 함)
        assert stats.r_squared > 0.999, f"Expected R² > 0.999, got {stats.r_squared}"
        
        # 데이터 포인트 수 확인
        assert stats.data_points == 10
        
    def test_analyze_noisy_data(self, service, noisy_dataframe):
        """노이즈가 있는 데이터 분석 테스트"""
        stats, summary, df = service.analyze_dataframe(
            df=noisy_dataframe,
            x_column='time',
            y_column='voltage'
        )
        
        # R² 확인 (0.95 이상이어야 함)
        assert stats.r_squared > 0.95, f"Expected R² > 0.95, got {stats.r_squared}"
        
    def test_insufficient_data_error(self, service):
        """데이터 부족 시 에러 테스트"""
        small_df = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [1, 2, 3]
        })
        
        with pytest.raises(AnalysisError) as exc_info:
            service.analyze_dataframe(small_df, 'x', 'y')
        
        assert exc_info.value.code == ErrorCode.INSUFFICIENT_DATA
        
    def test_error_rate_calculation(self, service, sample_dataframe):
        """오차율 계산 테스트"""
        # 이론적 기울기 10일 때
        stats, _, _ = service.analyze_dataframe(
            df=sample_dataframe,
            x_column='time',
            y_column='voltage',
            theoretical_slope=10.0
        )
        
        # 오차율이 0에 가까워야 함
        assert stats.error_rate_percent is not None
        assert stats.error_rate_percent < 1.0
        
    def test_missing_values_handling(self, service):
        """결측치 처리 테스트"""
        df_with_nan = pd.DataFrame({
            'x': [1, 2, 3, 4, 5, 6, 7, np.nan, 9, 10],
            'y': [1, 2, 3, 4, 5, np.nan, 7, 8, 9, 10]
        })
        
        stats, summary, _ = service.analyze_dataframe(
            df=df_with_nan,
            x_column='x',
            y_column='y'
        )
        
        # 결측치 제거 확인
        assert summary.null_values_removed > 0
        assert stats.data_points < 10


class TestGraphGenerator:
    """GraphGenerator 테스트"""
    
    @pytest.fixture
    def generator(self):
        """그래프 생성기 인스턴스"""
        return GraphGenerator()
    
    @pytest.fixture
    def sample_data(self):
        """테스트용 데이터와 통계"""
        from app.models.schemas import StatisticsResult
        
        df = pd.DataFrame({
            'time': [0.1, 0.2, 0.3, 0.4, 0.5],
            'voltage': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        stats = StatisticsResult(
            slope=10.0,
            intercept=0.0,
            r_squared=1.0,
            std_error=0.0,
            error_rate_percent=0.0,
            data_points=5,
            x_range=(0.1, 0.5),
            y_range=(1.0, 5.0)
        )
        
        return df, stats
    
    def test_generate_graph_returns_base64(self, generator, sample_data):
        """그래프 생성 및 Base64 반환 테스트"""
        df, stats = sample_data
        
        result = generator.generate_scatter_with_trendline(
            df=df,
            x_column='time',
            y_column='voltage',
            statistics=stats,
            title='Test Graph'
        )
        
        # Base64 이미지 확인
        assert result.image_base64 is not None
        assert result.image_base64.startswith('data:image/png;base64,')
        
        # Base64 디코딩 가능 확인
        import base64
        image_data = result.image_base64.split(',')[1]
        decoded = base64.b64decode(image_data)
        assert len(decoded) > 0


# pytest 실행
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
