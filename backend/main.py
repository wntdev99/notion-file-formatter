from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router

app = FastAPI(
    title="Notion File Formatter",
    description="Notion 5MB 제한을 위한 파일 변환 서비스",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# 프론트엔드 정적 파일 서빙
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
