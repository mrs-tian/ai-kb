from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Storage
    storage_type: str = "local"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 20

    # RAG
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50
    rag_top_k: int = 5
    rag_max_context_chars: int = 4000

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 1440
    admin_username: str = "admin"
    admin_password: str = "demo123456"
    public_rate_limit: int = 30
    public_ai_username: str = "admin"
    ai_daily_cost_limit_yuan: float = 1.0
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
