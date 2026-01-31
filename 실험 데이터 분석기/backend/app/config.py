"""
LabReportAI Backend Configuration
환경 변수 관리를 위한 Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Gemini API (Step 3)
    gemini_api_key: str = ""
    
    # Supabase (Step 4에서 사용)
    supabase_url: str = ""
    supabase_key: str = ""
    
    # File Upload
    max_file_size_mb: int = 10
    allowed_extensions: List[str] = [".csv", ".xlsx", ".xls"]

    # PDF Settings
    max_pdf_size_mb: int = 20
    allowed_pdf_extensions: List[str] = [".pdf"]

    # Graph Settings
    graph_dpi: int = 300
    graph_figsize: tuple = (10, 6)

    # Batch Analysis Settings
    max_sheets_per_batch: int = 10
    max_data_points_per_sheet: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 싱글톤 인스턴스
settings = Settings()
