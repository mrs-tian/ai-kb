from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.models.admin_user import AdminUser
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.ai_config_service import resolve_effective_ai_credentials
from app.services.chunk_service import estimate_token_count, split_text
from app.services.embedding_service import create_embeddings
from app.services.kb_service import get_kb_or_404, refresh_kb_stats
from app.services.parser_service import ALLOWED_EXTENSIONS, parse_bytes_content
from app.services.storage_service import build_storage_key, get_storage_backend


def _validate_upload(file: UploadFile, content: bytes) -> tuple[str, str]:
    if not file.filename:
        raise AppException(40001, "文件名不能为空", 400)

    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in ALLOWED_EXTENSIONS:
        raise AppException(40002, "文件格式不支持，仅支持 txt / md / pdf", 400)

    settings = get_settings()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise AppException(40003, f"文件过大，最大 {settings.max_upload_size_mb}MB", 400)

    return Path(file.filename).name, ext


def get_document_or_404(db: Session, document_id: int) -> Document:
    document = db.get(Document, document_id)
    if not document:
        raise AppException(40401, "文档不存在", 404)
    return document


def list_documents(
    db: Session,
    kb_id: int,
    *,
    page: int,
    page_size: int,
) -> tuple[list[Document], int]:
    get_kb_or_404(db, kb_id)
    query = select(Document).where(Document.kb_id == kb_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = db.scalars(
        query.order_by(Document.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(items), total


async def upload_document(db: Session, kb_id: int, file: UploadFile, user: AdminUser) -> Document:
    get_kb_or_404(db, kb_id)
    content = await file.read()
    filename, ext = _validate_upload(file, content)

    settings = get_settings()
    storage = get_storage_backend(settings)
    storage_key = build_storage_key(kb_id, filename)
    path = storage.absolute_path(storage_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

    document = Document(
        kb_id=kb_id,
        filename=filename,
        file_ext=ext,
        file_size=len(content),
        storage_type=settings.storage_type,
        storage_path=storage_key,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document(db, document, content=content, user=user)
    refresh_kb_stats(db, kb_id)
    db.refresh(document)
    return document


def process_document(
    db: Session,
    document: Document,
    *,
    content: bytes | None = None,
    user: AdminUser | None = None,
) -> Document:
    settings = get_settings()
    storage = get_storage_backend(settings)

    try:
        document.status = "parsing"
        document.error_message = None
        db.commit()

        if content is None:
            content = storage.read_bytes(document.storage_path)

        text, char_count = parse_bytes_content(content, document.file_ext)

        document.status = "embedding"
        db.commit()

        db.query(DocumentChunk).filter(DocumentChunk.doc_id == document.id).delete()

        chunks = split_text(
            text,
            chunk_size=settings.rag_chunk_size,
            overlap=settings.rag_chunk_overlap,
        )
        chunk_models: list[DocumentChunk] = []
        for index, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                kb_id=document.kb_id,
                doc_id=document.id,
                chunk_index=index,
                content=chunk_text,
                token_count=estimate_token_count(chunk_text),
            )
            db.add(chunk)
            chunk_models.append(chunk)
        db.flush()

        credentials = resolve_effective_ai_credentials(db, user)
        embeddings = create_embeddings(
            [chunk.content for chunk in chunk_models],
            credentials=credentials,
        )
        if embeddings:
            for chunk, embedding in zip(chunk_models, embeddings, strict=True):
                chunk.embedding = embedding

        document.char_count = char_count
        document.status = "ready"
        document.error_message = None
        db.commit()
        db.refresh(document)
        refresh_kb_stats(db, document.kb_id)
        return document
    except Exception as exc:
        document.status = "failed"
        document.error_message = str(exc)
        db.commit()
        db.refresh(document)
        return document


def reparse_document(db: Session, document_id: int, user: AdminUser) -> Document:
    document = get_document_or_404(db, document_id)
    return process_document(db, document, user=user)


async def delete_document(db: Session, document_id: int) -> None:
    document = get_document_or_404(db, document_id)
    kb_id = document.kb_id
    storage = get_storage_backend()
    await storage.delete(document.storage_path)
    db.delete(document)
    db.commit()
    refresh_kb_stats(db, kb_id)
