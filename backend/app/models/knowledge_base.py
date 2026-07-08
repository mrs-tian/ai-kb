from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class KnowledgeBase(Base, TimestampMixin):
    __tablename__ = "knowledge_base"
    __table_args__ = (
        Index("idx_kb_status", "status"),
        Index("idx_kb_public", "is_public", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    doc_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    documents = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    chat_sessions = relationship(
        "ChatSession",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
