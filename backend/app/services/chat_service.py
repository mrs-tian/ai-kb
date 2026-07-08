import time
import uuid
from collections.abc import Iterator

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.admin_user import AdminUser
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.knowledge_base import KnowledgeBase
from app.schemas.chat import ChatAskResponse, ReferenceItem
from app.services.ai_config_service import resolve_effective_ai_credentials
from app.services.llm_service import chat_completion, stream_chat_completion
from app.services.rag_service import build_context, build_references, retrieve_chunks


def get_public_kb_or_404(db: Session, kb_id: int) -> KnowledgeBase:
    kb = db.scalar(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.is_public.is_(True),
            KnowledgeBase.status == "active",
        )
    )
    if not kb:
        raise AppException(40401, "知识库不存在或未公开", 404)
    return kb


def list_public_knowledge_bases(db: Session) -> list[KnowledgeBase]:
    return list(
        db.scalars(
            select(KnowledgeBase)
            .where(
                KnowledgeBase.is_public.is_(True),
                KnowledgeBase.status == "active",
            )
            .order_by(KnowledgeBase.id.desc())
        ).all()
    )


def _normalize_title(question: str) -> str:
    title = question.strip()
    return title[:128] if len(title) > 128 else title


def _get_or_create_session(
    db: Session,
    *,
    kb_id: int,
    session_id: str | None,
    question: str,
    client_type: str | None,
    client_ip: str | None,
) -> ChatSession:
    if session_id:
        session = db.scalar(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.kb_id == kb_id,
            )
        )
        if session:
            return session
        raise AppException(40401, "会话不存在", 404)

    session = ChatSession(
        id=str(uuid.uuid4()),
        kb_id=kb_id,
        title=_normalize_title(question),
        client_type=client_type,
        client_ip=client_ip,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def ask_question(
    db: Session,
    *,
    kb_id: int,
    question: str,
    session_id: str | None = None,
    client_type: str | None = None,
    client_ip: str | None = None,
    require_public: bool = True,
    user: AdminUser | None = None,
) -> ChatAskResponse:
    if require_public:
        get_public_kb_or_404(db, kb_id)
    else:
        from app.services.kb_service import get_kb_or_404

        get_kb_or_404(db, kb_id)
    started = time.perf_counter()
    credentials = resolve_effective_ai_credentials(db, user)

    session = _get_or_create_session(
        db,
        kb_id=kb_id,
        session_id=session_id,
        question=question,
        client_type=client_type,
        client_ip=client_ip,
    )

    retrieved = retrieve_chunks(db, kb_id, question, credentials=credentials)
    context = build_context(retrieved)
    references = build_references(retrieved)
    answer, model = chat_completion(question, context, credentials=credentials)
    latency_ms = int((time.perf_counter() - started) * 1000)

    db.add(
        ChatMessage(
            session_id=session.id,
            role="user",
            content=question,
        )
    )
    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            references_json=references,
            model=model,
            latency_ms=latency_ms,
        )
    )
    db.commit()

    return ChatAskResponse(
        session_id=session.id,
        answer=answer,
        references=[ReferenceItem(**item) for item in references],
        latency_ms=latency_ms,
    )


def stream_question(
    db: Session,
    *,
    kb_id: int,
    question: str,
    session_id: str | None = None,
    client_type: str | None = None,
    client_ip: str | None = None,
    require_public: bool = True,
    user: AdminUser | None = None,
) -> tuple[ChatSession, list[dict], Iterator[str], float, str | None]:
    if require_public:
        get_public_kb_or_404(db, kb_id)
    else:
        from app.services.kb_service import get_kb_or_404

        get_kb_or_404(db, kb_id)
    started = time.perf_counter()
    credentials = resolve_effective_ai_credentials(db, user)

    session = _get_or_create_session(
        db,
        kb_id=kb_id,
        session_id=session_id,
        question=question,
        client_type=client_type,
        client_ip=client_ip,
    )

    retrieved = retrieve_chunks(db, kb_id, question, credentials=credentials)
    context = build_context(retrieved)
    references = build_references(retrieved)

    db.add(ChatMessage(session_id=session.id, role="user", content=question))
    db.commit()

    stream = stream_chat_completion(question, context, credentials=credentials)
    model = credentials.llm_model if credentials else None
    return session, references, stream, started, model


def save_stream_answer(
    db: Session,
    *,
    session_id: str,
    answer: str,
    references: list[dict],
    model: str | None,
    latency_ms: int,
) -> None:
    db.add(
        ChatMessage(
            session_id=session_id,
            role="assistant",
            content=answer,
            references_json=references,
            model=model,
            latency_ms=latency_ms,
        )
    )
    db.commit()


def get_session_messages(db: Session, session_id: str) -> tuple[ChatSession, list[ChatMessage]]:
    session = db.get(ChatSession, session_id)
    if not session:
        raise AppException(40401, "会话不存在", 404)

    messages = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.id.asc())
        ).all()
    )
    return session, messages


def list_admin_chat_sessions(
    db: Session,
    *,
    page: int,
    page_size: int,
    kb_id: int | None = None,
    keyword: str | None = None,
) -> tuple[list[dict], int]:
    query = select(ChatSession)
    if kb_id is not None:
        query = query.where(ChatSession.kb_id == kb_id)
    if keyword:
        pattern = f"%{keyword.strip()}%"
        message_session_ids = select(ChatMessage.session_id).where(
            ChatMessage.content.ilike(pattern)
        )
        query = query.where(
            or_(
                ChatSession.title.ilike(pattern),
                ChatSession.id.in_(message_session_ids),
            )
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sessions = list(
        db.scalars(
            query.order_by(ChatSession.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )

    items: list[dict] = []
    for session in sessions:
        kb = db.get(KnowledgeBase, session.kb_id)
        message_count = db.scalar(
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session.id)
        )
        items.append(
            {
                "id": session.id,
                "kb_id": session.kb_id,
                "kb_name": kb.name if kb else "",
                "title": session.title,
                "client_type": session.client_type,
                "message_count": message_count or 0,
                "created_at": session.created_at.isoformat(),
            }
        )
    return items, total


def get_admin_session_messages(db: Session, session_id: str) -> tuple[ChatSession, list[ChatMessage]]:
    session = db.get(ChatSession, session_id)
    if not session:
        raise AppException(40401, "会话不存在", 404)

    messages = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.id.asc())
        ).all()
    )
    return session, messages
