from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_base import KnowledgeBase
from app.schemas.kb import KnowledgeBaseCreate, KnowledgeBaseUpdate


def get_kb_or_404(db: Session, kb_id: int) -> KnowledgeBase:
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise AppException(40401, "知识库不存在", 404)
    return kb


def refresh_kb_stats(db: Session, kb_id: int) -> None:
    kb = get_kb_or_404(db, kb_id)
    doc_count = db.scalar(
        select(func.count()).select_from(Document).where(Document.kb_id == kb_id)
    )
    chunk_count = db.scalar(
        select(func.count()).select_from(DocumentChunk).where(DocumentChunk.kb_id == kb_id)
    )
    kb.doc_count = doc_count or 0
    kb.chunk_count = chunk_count or 0
    db.commit()


def list_knowledge_bases(
    db: Session,
    *,
    page: int,
    page_size: int,
    keyword: str | None = None,
) -> tuple[list[KnowledgeBase], int]:
    query = select(KnowledgeBase)
    if keyword:
        pattern = f"%{keyword.strip()}%"
        query = query.where(
            or_(
                KnowledgeBase.name.ilike(pattern),
                KnowledgeBase.description.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(KnowledgeBase.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(items), total


def create_knowledge_base(db: Session, payload: KnowledgeBaseCreate) -> KnowledgeBase:
    kb = KnowledgeBase(
        name=payload.name,
        description=payload.description,
        status="active",
        is_public=payload.is_public,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


def update_knowledge_base(
    db: Session, kb_id: int, payload: KnowledgeBaseUpdate
) -> KnowledgeBase:
    kb = get_kb_or_404(db, kb_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(kb, field, value)
    db.commit()
    db.refresh(kb)
    return kb


def delete_knowledge_base(db: Session, kb_id: int) -> None:
    kb = get_kb_or_404(db, kb_id)
    storage = get_storage_backend()
    for document in list(kb.documents):
        path = storage.absolute_path(document.storage_path)
        if path.exists():
            path.unlink()
    db.delete(kb)
    db.commit()
