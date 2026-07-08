from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.admin_user import AdminUser
from app.schemas.chat import (
    AdminChatMessageItem,
    AdminChatMessagesResponse,
    AdminChatSessionDetail,
    AdminChatSessionItem,
    ChatAskRequest,
    ChatAskResponse,
)
from app.schemas.common import ApiResponse, PaginatedData
from app.services.chat_service import ask_question, get_admin_session_messages, list_admin_chat_sessions

router = APIRouter(prefix="/admin/chats", dependencies=[Depends(get_current_admin)])


@router.get("/sessions", response_model=ApiResponse[PaginatedData[AdminChatSessionItem]])
def get_chat_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    kb_id: int | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[PaginatedData[AdminChatSessionItem]]:
    items, total = list_admin_chat_sessions(
        db, page=page, page_size=page_size, kb_id=kb_id, keyword=keyword
    )
    data = PaginatedData[AdminChatSessionItem](
        items=[AdminChatSessionItem(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ApiResponse[AdminChatMessagesResponse],
)
def get_chat_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[AdminChatMessagesResponse]:
    session, messages = get_admin_session_messages(db, session_id)
    data = AdminChatMessagesResponse(
        session=AdminChatSessionDetail(
            id=session.id,
            kb_id=session.kb_id,
            title=session.title,
        ),
        messages=[
            AdminChatMessageItem(
                id=message.id,
                role=message.role,
                content=message.content,
                references_json=message.references_json,
                latency_ms=message.latency_ms,
                created_at=message.created_at.isoformat(),
            )
            for message in messages
        ],
    )
    return ApiResponse(data=data)


@router.post("/ask", response_model=ApiResponse[ChatAskResponse])
def admin_ask(
    body: ChatAskRequest,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[ChatAskResponse]:
    data = ask_question(
        db,
        kb_id=body.kb_id,
        question=body.question,
        session_id=body.session_id,
        client_type="admin",
        require_public=False,
        user=_admin,
    )
    return ApiResponse(data=data)
