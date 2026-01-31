"""
LabReportAI Report Generator
마크다운 리포트 조립 서비스
"""

from typing import Optional, List

from app.models.schemas import (
    SingleExperimentResult,
    ExperimentManualInfo,
    ReportSections
)


class ReportGenerator:
    """
    마크다운 리포트 생성기

    실험 결과와 AI 생성 텍스트를 조합하여
    완전한 마크다운 리포트를 생성합니다.
    """

    def generate_markdown_report(
        self,
        report_title: str,
        experiments: List[SingleExperimentResult],
        generated_sections: ReportSections,
        manual_info: Optional[ExperimentManualInfo] = None
    ) -> str:
        """
        완전한 마크다운 리포트 생성

        Args:
            report_title: 리포트 제목
            experiments: 실험 결과 목록
            generated_sections: AI 생성 섹션들
            manual_info: 매뉴얼 정보 (선택)

        Returns:
            str: 완전한 마크다운 리포트 문자열
        """
        sections = []

        # 1. 제목
        sections.append(f"# {report_title}\n")

        # 2. 매뉴얼 정보 (있을 경우)
        if manual_info:
            sections.append(self._generate_manual_section(manual_info))

        # 3. 실험 결과 섹션 (데이터 테이블 + 그래프)
        sections.append("## 1. 실험 결과\n")
        for i, exp in enumerate(experiments, 1):
            sections.append(self._generate_experiment_section(exp, i))

        # 4. AI 생성 실험 결과 해석
        if generated_sections.experiment_results:
            sections.append("### 실험 결과 해석\n")
            sections.append(generated_sections.experiment_results + "\n")

        # 5. 결과 분석 섹션
        sections.append("## 2. 결과 분석\n")
        sections.append(generated_sections.result_analysis + "\n")

        # 6. 토의 섹션
        sections.append("## 3. 토의\n")
        sections.append(generated_sections.discussion + "\n")

        # 7. 푸터
        sections.append("\n---\n")
        sections.append("*이 리포트는 LabReportAI에 의해 자동 생성되었습니다.*\n")

        return "\n".join(sections)

    def _generate_manual_section(self, manual_info: ExperimentManualInfo) -> str:
        """매뉴얼 정보 섹션 생성"""
        lines = ["## 실험 개요\n"]

        # 실험 목적
        lines.append("### 실험 목적\n")
        lines.append(manual_info.experiment_purpose + "\n")

        # 이론 및 원리
        lines.append("### 이론 및 원리\n")
        lines.append(manual_info.theory + "\n")

        # 실험 기구 (있을 경우)
        if manual_info.equipment_list:
            lines.append("### 실험 기구\n")
            for equip in manual_info.equipment_list:
                lines.append(f"- {equip}")
            lines.append("")

        return "\n".join(lines) + "\n"

    def _generate_experiment_section(
        self,
        exp: SingleExperimentResult,
        index: int
    ) -> str:
        """개별 실험 섹션 생성 (데이터 테이블 + 그래프 + 통계)"""
        lines = []

        # 실험 제목
        lines.append(f"### 실험 {index}: {exp.experiment_name}\n")

        # 데이터 테이블
        if exp.data_table:
            lines.append("#### 측정 데이터\n")
            lines.append(self._generate_data_table_markdown(exp.data_table))

        # 통계 요약 테이블
        lines.append("#### 통계 분석 결과\n")
        lines.append(self._generate_statistics_table(exp))

        # 그래프 이미지 (Base64 임베딩)
        lines.append("#### 그래프\n")
        lines.append(self._embed_base64_image(
            exp.graph.image_base64,
            f"그림 {index}: {exp.experiment_name} - 산점도 및 추세선"
        ))

        return "\n".join(lines) + "\n"

    def _generate_data_table_markdown(self, data_table: List[dict]) -> str:
        """데이터 테이블을 마크다운 형식으로 변환"""
        if not data_table:
            return "*데이터 없음*\n"

        # 열 이름 추출
        columns = list(data_table[0].keys())

        # 헤더
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"

        # 데이터 행 (최대 20행만 표시)
        rows = []
        display_data = data_table[:20]
        for row in display_data:
            values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    values.append("-")
                elif isinstance(val, float):
                    values.append(f"{val:.4f}")
                else:
                    values.append(str(val))
            rows.append("| " + " | ".join(values) + " |")

        # 생략 표시
        if len(data_table) > 20:
            rows.append(f"| ... | ... |")
            rows.append(f"*({len(data_table)}개 데이터 중 20개 표시)*")

        return header + "\n" + separator + "\n" + "\n".join(rows) + "\n"

    def _generate_statistics_table(self, exp: SingleExperimentResult) -> str:
        """통계 요약 테이블 생성"""
        stats = exp.statistics

        lines = [
            "| 항목 | 값 |",
            "| --- | --- |",
            f"| 기울기 (Slope) | {stats.slope:.6f} |",
            f"| y절편 (Intercept) | {stats.intercept:.6f} |",
            f"| 결정계수 (R²) | {stats.r_squared:.6f} |",
            f"| 표준 오차 | {stats.std_error:.6f} |",
            f"| 데이터 포인트 | {stats.data_points}개 |",
            f"| X 범위 | {stats.x_range[0]:.4f} ~ {stats.x_range[1]:.4f} |",
            f"| Y 범위 | {stats.y_range[0]:.4f} ~ {stats.y_range[1]:.4f} |",
        ]

        if stats.error_rate_percent is not None:
            lines.append(f"| 오차율 | {stats.error_rate_percent:.2f}% |")

        return "\n".join(lines) + "\n"

    def _embed_base64_image(self, image_base64: str, caption: str) -> str:
        """Base64 이미지를 마크다운에 임베딩"""
        # 이미 data:image/png;base64, 접두사가 있으면 그대로 사용
        if not image_base64.startswith("data:"):
            image_base64 = f"data:image/png;base64,{image_base64}"

        return f"![{caption}]({image_base64})\n\n*{caption}*\n"


# 서비스 인스턴스 (싱글톤)
report_generator = ReportGenerator()
