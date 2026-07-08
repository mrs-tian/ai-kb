import json
import time
from collections.abc import Iterator

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.rate_limit import check_public_rate_limit
from app.schemas.chat import (
    ChatAskRequest,
    ChatAskResponse,
    ChatMessageItem,
    ChatSessionMessagesResponse,
    ReferenceItem,
)
from app.schemas.common import ApiResponse
from app.services.chat_service import (
    ask_question,
    get_session_messages,
    save_stream_answer,
    stream_question,
)

router = APIRouter(prefix="/public/chat", tags=["public-chat"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


@router.post("", response_model=ApiResponse[ChatAskResponse])
def public_chat(
    body: ChatAskRequest,
    request: Request,
    db: Session = Depends(get_db),
    x_client_type: str | None = Header(None, alias="X-Client-Type"),
) -> ApiResponse[ChatAskResponse]:
    check_public_rate_limit(_client_ip(request))
    data = ask_question(
        db,
        kb_id=body.kb_id,
        question=body.question,
        session_id=body.session_id,
        client_type=x_client_type,
        client_ip=_client_ip(request),
    )
    return ApiResponse(data=data)


@router.post("/stream")
def public_chat_stream(
    body: ChatAskRequest,
    request: Request,
    db: Session = Depends(get_db),
    x_client_type: str | None = Header(None, alias="X-Client-Type"),
) -> StreamingResponse:
    check_public_rate_limit(_client_ip(request))

    session, references, stream, started, model = stream_question(
        db,
        kb_id=body.kb_id,
        question=body.question,
        session_id=body.session_id,
        client_type=x_client_type,
        client_ip=_client_ip(request),
    )

    def event_stream() -> Iterator[str]:
        yield _format_sse("session", {"session_id": session.id})
        answer_parts: list[str] = []
        try:
            for delta in stream:
                answer_parts.append(delta)
                yield _format_sse("delta", {"content": delta})
        except Exception as exc:
            yield _format_sse("error", {"message": str(exc)})
            return

        answer = "".join(answer_parts)
        latency_ms = int((time.perf_counter() - started) * 1000)
        save_stream_answer(
            db,
            session_id=session.id,
            answer=answer,
            references=references,
            model=model,
            latency_ms=latency_ms,
        )
        yield _format_sse("references", {"references": references})
        yield _format_sse("done", {"latency_ms": latency_ms})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ApiResponse[ChatSessionMessagesResponse],
)
def public_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[ChatSessionMessagesResponse]:
    session, messages = get_session_messages(db, session_id)
    data = ChatSessionMessagesResponse(
        session_id=session.id,
        kb_id=session.kb_id,
        messages=[
            ChatMessageItem(
                role=message.role,
                content=message.content,
                references=[
                    ReferenceItem(**ref)
                    for ref in (message.references_json or [])
                ]
                if message.references_json
                else None,
                created_at=message.created_at.isoformat(),
            )
            for message in messages
        ],
    )
    return ApiResponse(data=data)


def _format_sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
