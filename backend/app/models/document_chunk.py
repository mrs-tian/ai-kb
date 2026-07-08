from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunk"
    __table_args__ = (
        Index("idx_chunk_kb_id", "kb_id"),
        Index("idx_chunk_doc_id", "doc_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kb_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        nullable=False,
    )
    doc_id: Mapped[int] = mapped_column(
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    document = relationship("Document", back_populates="chunks")
