import json
import re
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.models.api_request_log import ApiRequestLog


def _log_filter_conditions(
    *,
    username: str | None = None,
    path_keyword: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[ColumnElement[bool]]:
    conditions: list[ColumnElement[bool]] = []
    if username:
        conditions.append(ApiRequestLog.username.ilike(f"%{username.strip()}%"))
    if path_keyword:
        conditions.append(ApiRequestLog.path.ilike(f"%{path_keyword.strip()}%"))
    if start_time:
        conditions.append(ApiRequestLog.created_at >= start_time)
    if end_time:
        conditions.append(ApiRequestLog.created_at <= end_time)
    return conditions


def list_api_logs(
    db: Session,
    *,
    page: int,
    page_size: int,
    username: str | None = None,
    path_keyword: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> tuple[list[ApiRequestLog], int]:
    query = select(ApiRequestLog)
    conditions = _log_filter_conditions(
        username=username,
        path_keyword=path_keyword,
        start_time=start_time,
        end_time=end_time,
    )
    if conditions:
        query = query.where(*conditions)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(
        db.scalars(
            query.order_by(ApiRequestLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return items, total


def clear_api_logs(
    db: Session,
    *,
    username: str | None = None,
    path_keyword: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> int:
    stmt = delete(ApiRequestLog)
    conditions = _log_filter_conditions(
        username=username,
        path_keyword=path_keyword,
        start_time=start_time,
        end_time=end_time,
    )
    if conditions:
        stmt = stmt.where(*conditions)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount or 0


def sanitize_request_body(path: str, body: bytes) -> str | None:
    if not body:
        return None
    text = body.decode("utf-8", errors="replace")
    if len(text) > 2000:
        text = text[:2000] + "...(truncated)"
    if "/auth/login" in path:
        try:
            payload = json.loads(text)
            if "password" in payload:
                payload["password"] = "***"
            return json.dumps(payload, ensure_ascii=False)
        except json.JSONDecodeError:
            return re.sub(r'"password"\s*:\s*"[^"]*"', '"password":"***"', text)
    return text


def write_api_log(db: Session, **kwargs) -> None:
    log = ApiRequestLog(**kwargs)
    db.add(log)
    db.commit()
