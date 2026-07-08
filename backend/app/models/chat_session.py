from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_session"
    __table_args__ = (
        Index("idx_session_kb_id", "kb_id"),
        Index("idx_session_created", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kb_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    client_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)

    knowledge_base = relationship("KnowledgeBase", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
