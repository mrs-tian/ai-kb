from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "document"
    __table_args__ = (
        Index("idx_doc_kb_id", "kb_id"),
        Index("idx_doc_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kb_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_ext: Mapped[str] = mapped_column(String(16), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_type: Mapped[str] = mapped_column(String(16), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
