"""
Gemini AI Service
Google Gemini 2.5 Flash를 사용한 AI 고찰 생성 서비스
"""

from typing import Optional, List
import json
from google import genai
from google.genai import types

from app.config import settings
from app.models.schemas import (
    StatisticsResult,
    DiscussionRequest,
    DiscussionResponse,
    ExperimentManualInfo,
    ErrorGuideItem,
    SingleExperimentResult,
    ReportOptions,
    ReportSections,
    FullReportResponse
)


class GeminiService:
    """Gemini AI 서비스"""
    
    MODEL_NAME = "gemini-2.5-flash"
    
    def __init__(self):
        """Gemini 클라이언트 초기화"""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        self.client = genai.Client(api_key=settings.gemini_api_key)
    
    def generate_discussion(
        self,
        experiment_title: str,
        statistics: StatisticsResult,
        context: Optional[str] = None
    ) -> DiscussionResponse:
        """
        실험 결과에 대한 AI 고찰 생성
        
        Args:
            experiment_title: 실험 제목
            statistics: 통계 분석 결과
            context: 추가 맥락 정보 (선택)
            
        Returns:
            DiscussionResponse: 생성된 고찰 텍스트
        """
        
        prompt = self._build_prompt(experiment_title, statistics, context)
        
        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4000,  # 더 긴 출력을 위해 증가
            )
        )
        
        generated_text = response.text
        
        return DiscussionResponse(
            success=True,
            message="고찰이 성공적으로 생성되었습니다.",
            discussion=generated_text,
            model_used=self.MODEL_NAME
        )
    
    def _build_prompt(
        self, 
        experiment_title: str, 
        statistics: StatisticsResult,
        context: Optional[str] = None
    ) -> str:
        """프롬프트 생성"""
        
        # R² 값에 따른 해석 가이드
        r_squared = statistics.r_squared
        if r_squared >= 0.99:
            r_squared_interpretation = "매우 강한 선형 상관관계 (거의 완벽한 선형성)"
        elif r_squared >= 0.95:
            r_squared_interpretation = "강한 선형 상관관계 (우수한 선형성)"
        elif r_squared >= 0.9:
            r_squared_interpretation = "양호한 선형 상관관계"
        elif r_squared >= 0.7:
            r_squared_interpretation = "중간 정도의 선형 상관관계"
        else:
            r_squared_interpretation = "약한 선형 상관관계 (비선형적 특성 가능)"
        
        error_analysis = ""
        if statistics.error_rate_percent is not None:
            error_rate = statistics.error_rate_percent
            if error_rate < 1:
                error_level = "매우 우수 (1% 미만)"
            elif error_rate < 5:
                error_level = "양호 (5% 미만)"
            elif error_rate < 10:
                error_level = "허용 가능 (10% 미만)"
            else:
                error_level = "개선 필요 (10% 이상)"
            
            error_analysis = f"""
- 오차율: {error_rate:.2f}% ({error_level})"""

        prompt = f"""당신은 이공계 대학 실험 보고서 작성을 전문으로 하는 물리학/공학 박사급 조교입니다.
다음 실험 결과 데이터를 바탕으로 **상세하고 학술적인** 실험 보고서의 '결과 및 고찰' 섹션을 작성해주세요.

반드시 **최소 800자 이상**, 충분히 길고 상세하게 작성해야 합니다.

---

## 📋 실험 정보
- **실험 제목**: {experiment_title}

## 📊 통계 분석 결과
| 항목 | 값 | 의미 |
|------|-----|------|
| 기울기 (Slope) | {statistics.slope:.6f} | 독립 변수 1단위 증가 시 종속 변수 변화량 |
| y절편 (Intercept) | {statistics.intercept:.6f} | X=0일 때의 Y 예측값 |
| 결정계수 (R²) | {statistics.r_squared:.6f} | {r_squared_interpretation} |
| 표준 오차 | {statistics.std_error:.6f} | 기울기 추정의 불확실성 |
| 데이터 포인트 수 | {statistics.data_points}개 | 분석에 사용된 측정값 개수 |
| X 범위 | {statistics.x_range[0]:.4f} ~ {statistics.x_range[1]:.4f} | 독립 변수 측정 범위 |
| Y 범위 | {statistics.y_range[0]:.4f} ~ {statistics.y_range[1]:.4f} | 종속 변수 측정 범위 |
{error_analysis}

{f"## 📝 추가 맥락 정보{chr(10)}{context}" if context else ""}

---

## ✍️ 작성 지침 (반드시 준수)

다음 **5개 섹션**을 모두 포함하여 작성하세요. 각 섹션은 최소 2-3개의 문단으로 구성되어야 합니다.

### 1. 결과 분석 (Results Analysis)
- 회귀 방정식 Y = {statistics.slope:.4f}X + {statistics.intercept:.4f}의 물리적/과학적 의미를 상세히 해석
- 기울기가 의미하는 물리량 또는 관계성 설명
- y절편의 물리적 의미와 0에서 벗어난 경우의 원인 분석
- 데이터 범위 내에서의 선형성 평가

### 2. 결정계수(R²) 분석 (Coefficient of Determination)
- R² = {statistics.r_squared:.4f}가 의미하는 바를 통계학적으로 해석
- 이 값이 실험의 신뢰도에 미치는 영향
- 선형 모델의 적합도 평가
- 잔차(residual) 분석 관점에서의 해석

### 3. 오차 원인 분석 (Error Analysis)
최소 3가지 이상의 가능한 오차 원인을 구체적으로 제시:
- **계통 오차 (Systematic Error)**: 측정 장비의 영점 오차, 보정 문제, 환경 조건 등
- **우연 오차 (Random Error)**: 측정자의 판독 오차, 환경 변동, 샘플링 오차 등
- **방법 오차 (Procedural Error)**: 실험 방법론의 한계, 가정의 적절성 등
- 각 오차 원인이 기울기, 절편, R² 값에 미치는 영향 분석

### 4. 개선 방안 (Improvements)
- 오차를 줄이기 위한 구체적인 개선 방안 제시
- 측정 정밀도 향상 방법
- 데이터 수집 절차 개선안
- 추가 실험 또는 검증 방법 제안

### 5. 결론 (Conclusion)
- 실험 목적 달성 여부 평가
- 주요 발견 사항 요약
- 실험 결과의 의의와 응용 가능성
- 향후 연구 방향 제안

---

## 📝 형식 요구사항
- 마크다운 형식으로 작성
- 각 섹션에 ## 또는 ### 제목 사용
- 학술 논문 스타일의 객관적이고 전문적인 어조 유지
- 수치는 적절한 유효숫자로 표기
- 필요시 수식 사용 (예: $Y = aX + b$ 형태)

**중요: 반드시 모든 섹션을 포함하여 상세하게 작성하세요. 간략하게 작성하지 마세요!**"""

        return prompt

    # ============================================================
    # PDF Manual Extraction (매뉴얼 정보 추출)
    # ============================================================

    def extract_manual_from_pdf(
        self,
        pdf_bytes: bytes,
        filename: str
    ) -> ExperimentManualInfo:
        """
        PDF 파일에서 실험 매뉴얼 정보를 추출

        Args:
            pdf_bytes: PDF 파일 바이트 데이터
            filename: 원본 파일명

        Returns:
            ExperimentManualInfo: 추출된 매뉴얼 정보
        """
        prompt = self._build_pdf_extraction_prompt(filename)

        # PDF를 Gemini에 전송 (inline_data 사용)
        try:
            print(f"DEBUG: Processing PDF with {self.MODEL_NAME}")
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type="application/pdf",
                                    data=pdf_bytes
                                )
                            ),
                            types.Part(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,  # 더 낮춤
                    max_output_tokens=4000,
                    response_mime_type="application/json"
                )
            )

            # JSON 파싱
            raw_text = response.text.strip()
            print(f"DEBUG: Gemini Response: {raw_text[:200]}...")

            data = json.loads(raw_text)
            
        except Exception as e:
            print(f"ERROR in PDF extraction: {str(e)}")
            if 'response' in locals():
                print(f"Response text was: {response.text}")
            
            # 실패 시 기본값 반환
            return ExperimentManualInfo(
                experiment_purpose=f"PDF 분석 실패: {str(e)}",
                theory="PDF에서 내용을 추출하지 못했습니다.",
                error_guides=[]
            )

        # ErrorGuideItem 리스트 변환
        error_guides = []
        for item in data.get("error_guides", []):
            error_guides.append(ErrorGuideItem(
                cause=item.get("cause", ""),
                description=item.get("description", ""),
                mitigation=item.get("mitigation")
            ))

        return ExperimentManualInfo(
            experiment_purpose=data.get("experiment_purpose", ""),
            theory=data.get("theory", ""),
            error_guides=error_guides,
            expected_results=data.get("expected_results"),
            equipment_list=data.get("equipment_list")
        )

    def _build_pdf_extraction_prompt(self, filename: str) -> str:
        """PDF 매뉴얼 추출 프롬프트 생성"""
        return f"""당신은 이공계 실험 매뉴얼 분석 전문가입니다.

첨부된 PDF 파일 "{filename}"에서 다음 정보를 추출하여 **JSON 형식**으로 반환해주세요.

## 추출 항목:
1. **experiment_purpose**: 실험 목적 (1-3문장으로 요약)
2. **theory**: 실험 이론 및 원리 (주요 수식 포함, 500자 이내)
3. **error_guides**: 오차 원인 목록 (각 항목은 cause, description, mitigation 포함)
4. **expected_results**: 예상 결과 (있을 경우)
5. **equipment_list**: 실험 기구 목록 (있을 경우)

## 출력 형식 (JSON만 반환):
```json
{{
    "experiment_purpose": "실험 목적 설명...",
    "theory": "이론 및 원리 설명... 수식: τ = RC",
    "error_guides": [
        {{
            "cause": "접촉 저항",
            "description": "회로 연결부의 접촉 불량으로 인한 저항 증가",
            "mitigation": "연결부 재확인 및 접점 청소"
        }},
        {{
            "cause": "측정 기기 오차",
            "description": "멀티미터의 내부 저항으로 인한 측정값 왜곡",
            "mitigation": "고입력 임피던스 측정기 사용"
        }}
    ],
    "expected_results": "예상 결과 설명...",
    "equipment_list": ["오실로스코프", "함수 발생기", "저항", "커패시터"]
}}
```

**중요**: JSON만 반환하세요. 다른 설명은 필요 없습니다."""

    # ============================================================
    # Full Report Generation (전체 리포트 생성)
    # ============================================================

    def generate_full_report(
        self,
        report_title: str,
        experiments: List[SingleExperimentResult],
        manual_info: Optional[ExperimentManualInfo] = None,
        options: Optional[ReportOptions] = None
    ) -> FullReportResponse:
        """
        전체 실험 리포트의 텍스트 섹션 생성

        Args:
            report_title: 리포트 제목
            experiments: 실험 결과 목록
            manual_info: 매뉴얼 정보 (PDF에서 추출, 선택)
            options: 리포트 옵션

        Returns:
            FullReportResponse: 생성된 리포트 섹션들
        """
        if options is None:
            options = ReportOptions()

        prompt = self._build_full_report_prompt(
            report_title=report_title,
            experiments=experiments,
            manual_info=manual_info,
            options=options
        )

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8000,  # 긴 리포트를 위해 증가
            )
        )

        generated_text = response.text

        # 섹션 분리 (마커 기반)
        sections = self._parse_report_sections(generated_text)

        return FullReportResponse(
            success=True,
            message="전체 리포트가 성공적으로 생성되었습니다.",
            markdown_content=generated_text,
            sections=sections
        )

    def _build_full_report_prompt(
        self,
        report_title: str,
        experiments: List[SingleExperimentResult],
        manual_info: Optional[ExperimentManualInfo],
        options: ReportOptions
    ) -> str:
        """전체 리포트 생성 프롬프트"""

        # 실험 데이터 요약 생성
        experiments_summary = ""
        for i, exp in enumerate(experiments, 1):
            stats = exp.statistics
            experiments_summary += f"""
### 실험 {i}: {exp.experiment_name}
- **시트명**: {exp.sheet_name}
- **데이터 포인트**: {stats.data_points}개
- **기울기**: {stats.slope:.6f}
- **y절편**: {stats.intercept:.6f}
- **R²**: {stats.r_squared:.6f}
- **표준 오차**: {stats.std_error:.6f}
- **X 범위**: {stats.x_range[0]:.4f} ~ {stats.x_range[1]:.4f}
- **Y 범위**: {stats.y_range[0]:.4f} ~ {stats.y_range[1]:.4f}
{f"- **오차율**: {stats.error_rate_percent:.2f}%" if stats.error_rate_percent else ""}
"""

        # 매뉴얼 정보 섹션
        manual_section = ""
        if manual_info:
            error_guide_text = ""
            if manual_info.error_guides:
                for eg in manual_info.error_guides:
                    error_guide_text += f"  - {eg.cause}: {eg.description}\n"

            manual_section = f"""
## 📖 실험 매뉴얼 정보 (PDF에서 추출)

### 실험 목적
{manual_info.experiment_purpose}

### 이론 및 원리
{manual_info.theory}

### 오차 원인 가이드
{error_guide_text if error_guide_text else "N/A"}

{f"### 예상 결과{chr(10)}{manual_info.expected_results}" if manual_info.expected_results else ""}
"""

        language_instruction = "한국어로" if options.language == "ko" else "in English"
        tone_instruction = "학술 논문 스타일의 객관적이고 전문적인 어조" if options.tone == "academic" else "이해하기 쉬운 일반적인 어조"

        return f"""당신은 이공계 실험 보고서 작성 전문가입니다.

다음 실험 데이터와 매뉴얼 정보를 바탕으로 **완전한 실험 보고서**를 작성해주세요.

---

# 📋 리포트 정보
- **제목**: {report_title}
- **총 실험 수**: {len(experiments)}개

{manual_section}

## 📊 실험 결과 데이터
{experiments_summary}

---

## ✍️ 작성 지침

{language_instruction} 작성하되, {tone_instruction}를 유지하세요.

다음 **3개 섹션**을 작성해주세요:

### 섹션 1: 실험 결과 (<!-- SECTION: experiment_results -->)
- 각 실험의 데이터와 그래프 분석
- 측정된 값들의 특징과 경향
- 데이터의 품질 평가

### 섹션 2: 결과 분석 (<!-- SECTION: result_analysis -->)
- 각 실험의 R² 값 해석
- 기울기와 절편의 물리적 의미
- 실험 간 비교 분석 (여러 실험인 경우)
- 이론값과의 비교 (매뉴얼 정보 있을 경우)

### 섹션 3: 토의 (<!-- SECTION: discussion -->)
- 종합적인 고찰
- 오차 원인 분석 (매뉴얼의 오차 가이드 참고)
- 개선 방안 제시
- 결론 및 향후 연구 방향

---

## 📝 형식 요구사항
- 각 섹션 시작 전에 마커 주석 포함: `<!-- SECTION: section_name -->`
- 마크다운 형식 사용
- 각 섹션은 최소 300자 이상 상세하게 작성
- 수치는 적절한 유효숫자로 표기
- 필요시 수식 사용

**모든 섹션을 빠짐없이 상세하게 작성해주세요.**"""

    def _parse_report_sections(self, text: str) -> ReportSections:
        """리포트 텍스트에서 섹션 분리"""

        def extract_section(marker: str, next_marker: Optional[str] = None) -> str:
            start_marker = f"<!-- SECTION: {marker} -->"
            if start_marker not in text:
                return ""

            start_idx = text.find(start_marker) + len(start_marker)

            if next_marker:
                end_marker = f"<!-- SECTION: {next_marker} -->"
                end_idx = text.find(end_marker) if end_marker in text else len(text)
            else:
                end_idx = len(text)

            return text[start_idx:end_idx].strip()

        return ReportSections(
            experiment_results=extract_section("experiment_results", "result_analysis"),
            result_analysis=extract_section("result_analysis", "discussion"),
            discussion=extract_section("discussion")
        )


# 싱글톤 인스턴스 (지연 초기화)
_gemini_service: Optional[GeminiService] = None

def get_gemini_service() -> GeminiService:
    """Gemini 서비스 싱글톤 반환"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
