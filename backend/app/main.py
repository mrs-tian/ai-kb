from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import ApiLoggingMiddleware
from app.db.init_db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="智问 AI 知识库",
    description="AI 知识库问答后端 API",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ApiLoggingMiddleware)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "智问 AI 知识库 API", "version": settings.app_version}
