"""
LabReportAI Graph Generator
Matplotlib을 활용한 논문용 그래프 생성
"""

import matplotlib
matplotlib.use('Agg')  # GUI 없이 사용하기 위한 백엔드 설정

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import base64
import io
from typing import Optional, List, Tuple

from app.config import settings
from app.models.schemas import GraphResult, StatisticsResult, ExperimentConfig


class GraphGenerator:
    """
    고품질 그래프 생성기
    
    산점도 + 추세선 그래프를 생성하고
    Base64 인코딩된 PNG 이미지를 반환합니다.
    """
    
    # 그래프 스타일 설정
    SCATTER_COLOR = '#3B82F6'     # 산점도 색상 (파란색)
    LINE_COLOR = '#EF4444'        # 추세선 색상 (빨간색)
    SCATTER_SIZE = 60             # 산점도 점 크기
    LINE_WIDTH = 2                # 추세선 두께
    
    def __init__(self):
        """그래프 스타일 초기화"""
        # 스타일 설정
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # 한글 폰트 설정 시도
        self._setup_korean_font()
    
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        try:
            # Windows 기본 한글 폰트
            plt.rcParams['font.family'] = 'Malgun Gothic'
            plt.rcParams['axes.unicode_minus'] = False
        except:
            # 실패 시 기본 폰트 사용
            pass
    
    def generate_scatter_with_trendline(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        statistics: StatisticsResult,
        title: str = ""
    ) -> GraphResult:
        """
        산점도 + 추세선 그래프 생성
        
        Args:
            df: pandas DataFrame (전처리 완료된 데이터)
            x_column: X축 열 이름
            y_column: Y축 열 이름
            statistics: 통계 분석 결과
            title: 그래프 제목
            
        Returns:
            GraphResult: Base64 인코딩된 그래프 이미지
        """
        # Figure 생성
        fig, ax = plt.subplots(figsize=settings.graph_figsize, dpi=settings.graph_dpi)
        
        x = df[x_column].values
        y = df[y_column].values
        
        # 1. 산점도 그리기
        ax.scatter(
            x, y,
            c=self.SCATTER_COLOR,
            s=self.SCATTER_SIZE,
            alpha=0.7,
            edgecolors='white',
            linewidths=0.5,
            label='측정 데이터',
            zorder=2
        )
        
        # 2. 추세선 그리기
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = statistics.slope * x_line + statistics.intercept
        
        ax.plot(
            x_line, y_line,
            color=self.LINE_COLOR,
            linewidth=self.LINE_WIDTH,
            linestyle='--',
            label=f'추세선: y = {statistics.slope:.4f}x + {statistics.intercept:.4f}',
            zorder=1
        )
        
        # 3. 그래프 꾸미기
        ax.set_xlabel(x_column, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_column, fontsize=12, fontweight='bold')
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        # 4. R² 값 표시 (텍스트 박스)
        textstr = f'$R^2$ = {statistics.r_squared:.4f}'
        props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
        ax.text(
            0.05, 0.95, textstr,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment='top',
            bbox=props
        )
        
        # 5. 범례
        ax.legend(loc='lower right', fontsize=10)
        
        # 6. 그리드 스타일
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 레이아웃 조정
        plt.tight_layout()
        
        # 7. Base64 인코딩
        image_base64 = self._fig_to_base64(fig)
        
        # Figure 닫기 (메모리 해제)
        plt.close(fig)
        
        return GraphResult(
            image_base64=image_base64,
            image_url=None  # Storage 업로드는 나중에 구현
        )
    
    def _fig_to_base64(self, fig: plt.Figure) -> str:
        """
        Matplotlib Figure를 Base64 문자열로 변환

        Args:
            fig: Matplotlib Figure 객체

        Returns:
            str: data:image/png;base64,... 형식의 문자열
        """
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_batch_graphs(
        self,
        experiments_data: List[Tuple[pd.DataFrame, str, str, StatisticsResult, str]]
    ) -> List[GraphResult]:
        """
        여러 실험 데이터에 대한 그래프를 배치로 생성

        Args:
            experiments_data: 리스트 of (DataFrame, x_column, y_column, statistics, experiment_name) 튜플

        Returns:
            List[GraphResult]: 생성된 그래프 결과 리스트
        """
        results = []

        for df, x_column, y_column, statistics, experiment_name in experiments_data:
            graph_result = self.generate_scatter_with_trendline(
                df=df,
                x_column=x_column,
                y_column=y_column,
                statistics=statistics,
                title=experiment_name
            )
            results.append(graph_result)

        return results

    def get_base64_without_prefix(self, graph_result: GraphResult) -> str:
        """
        GraphResult에서 'data:image/png;base64,' 접두사를 제거한 Base64 문자열 반환

        Args:
            graph_result: 그래프 결과

        Returns:
            str: 순수 Base64 문자열
        """
        prefix = "data:image/png;base64,"
        if graph_result.image_base64.startswith(prefix):
            return graph_result.image_base64[len(prefix):]
        return graph_result.image_base64


# 서비스 인스턴스 (싱글톤)
graph_generator = GraphGenerator()
