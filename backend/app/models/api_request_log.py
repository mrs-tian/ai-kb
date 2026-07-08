from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApiRequestLog(Base):
    __tablename__ = "api_request_log"
    __table_args__ = (
        Index("idx_api_log_created", "created_at"),
        Index("idx_api_log_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    query_string: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_authenticated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
