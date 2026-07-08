import json
import time
from typing import Callable

from fastapi import Request, Response
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser
from app.services.log_service import sanitize_request_body, write_api_log


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _resolve_user(request: Request) -> tuple[int | None, str | None, bool]:
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        return None, None, False

    token = auth.split(" ", 1)[1].strip()
    settings = get_settings()
    username = decode_access_token(token, settings.jwt_secret)
    if not username:
        return None, None, False

    db = SessionLocal()
    try:
        user = db.scalar(select(AdminUser).where(AdminUser.username == username))
        if user and user.is_active:
            return user.id, user.username, True
        return None, username, False
    finally:
        db.close()


class ApiLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in {"/health", "/"}:
            return await call_next(request)

        started = time.perf_counter()
        user_id, username, is_authenticated = _resolve_user(request)
        request_body = await request.body()

        async def receive():
            return {"type": "http.request", "body": request_body, "more_body": False}

        request._receive = receive

        response = await call_next(request)
        duration_ms = int((time.perf_counter() - started) * 1000)

        response_body = ""
        if isinstance(response, StreamingResponse):
            chunks: list[bytes] = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            raw = b"".join(chunks)
            response_body = raw.decode("utf-8", errors="replace")[:2000]
            response = Response(
                content=raw,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        elif hasattr(response, "body") and response.body:
            response_body = response.body.decode("utf-8", errors="replace")[:2000]

        try:
            parsed = json.loads(response_body) if response_body else None
            if isinstance(parsed, dict) and "data" in parsed:
                if isinstance(parsed["data"], dict) and "access_token" in parsed["data"]:
                    parsed["data"]["access_token"] = "***"
                    response_body = json.dumps(parsed, ensure_ascii=False)[:2000]
        except json.JSONDecodeError:
            pass

        db = SessionLocal()
        try:
            write_api_log(
                db,
                method=request.method,
                path=request.url.path,
                query_string=str(request.url.query) or None,
                status_code=response.status_code,
                response_body=response_body or None,
                user_id=user_id,
                username=username,
                client_ip=_client_ip(request),
                duration_ms=duration_ms,
                is_authenticated=is_authenticated,
            )
        finally:
            db.close()

        return response
