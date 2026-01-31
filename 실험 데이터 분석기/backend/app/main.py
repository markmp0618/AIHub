"""
LabReportAI Backend - FastAPI Application
실험 데이터 분석 및 리포트 생성 API 서버
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.analyze import router as analyze_router
from app.routers.generate import router as generate_router


# FastAPI 앱 생성
app = FastAPI(
    title="LabReportAI API",
    description="이공계 대학생을 위한 실험 데이터 분석 및 리포트 초안 생성 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(analyze_router)
app.include_router(generate_router)


@app.get("/", tags=["Health"])
async def root():
    """API 루트 엔드포인트"""
    return {
        "name": "LabReportAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "labreportai-backend"
    }


# 개발 서버 실행 (직접 실행 시)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
