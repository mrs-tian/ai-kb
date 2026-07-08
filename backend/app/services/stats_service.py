from datetime import datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.api_request_log import ApiRequestLog
from app.models.chat_message import ChatMessage
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_base import KnowledgeBase
from app.schemas.stats import (
    AiUsageTrendData,
    AiUsageTrendItem,
    ApiTrendData,
    ApiTrendItem,
    ChatTrendData,
    ChatTrendItem,
    SettingsData,
    StatsOverview,
)

# Demo 估算单价（元 / 1K tokens）
_LLM_COST_PER_1K = 0.002
_EMBED_COST_PER_1K = 0.0002

_EXCLUDED_LOG_PATHS = ("/health", "/")


def _estimate_tokens_from_chars(char_count: int) -> int:
    return max(0, char_count // 4)


def _estimate_cost(llm_tokens: int, embedding_tokens: int) -> float:
    cost = (llm_tokens / 1000) * _LLM_COST_PER_1K + (embedding_tokens / 1000) * _EMBED_COST_PER_1K
    return round(cost, 4)


def _log_base_filter():
    return ApiRequestLog.path.notin_(_EXCLUDED_LOG_PATHS)


def _get_ai_usage(db: Session, *, since: datetime | None = None) -> dict[str, int]:
    chunk_query = select(func.coalesce(func.sum(DocumentChunk.token_count), 0))
    if since:
        chunk_query = chunk_query.where(DocumentChunk.created_at >= since)

    embedding_doc_tokens = int(db.scalar(chunk_query) or 0)

    user_msg_query = select(func.coalesce(func.sum(func.length(ChatMessage.content)), 0)).where(
        ChatMessage.role == "user"
    )
    if since:
        user_msg_query = user_msg_query.where(ChatMessage.created_at >= since)
    rag_query_tokens = _estimate_tokens_from_chars(int(db.scalar(user_msg_query) or 0))

    chat_query = select(func.coalesce(func.sum(func.length(ChatMessage.content)), 0))
    if since:
        chat_query = chat_query.where(ChatMessage.created_at >= since)
    llm_tokens = _estimate_tokens_from_chars(int(db.scalar(chat_query) or 0))

    llm_calls_query = select(func.count()).select_from(ChatMessage).where(
        ChatMessage.role == "assistant"
    )
    if since:
        llm_calls_query = llm_calls_query.where(ChatMessage.created_at >= since)
    llm_calls = int(db.scalar(llm_calls_query) or 0)

    embedding_tokens = embedding_doc_tokens + rag_query_tokens
    total_tokens = embedding_tokens + llm_tokens
    return {
        "embedding_tokens": embedding_tokens,
        "llm_tokens": llm_tokens,
        "total_tokens": total_tokens,
        "llm_calls": llm_calls,
        "estimated_cost": _estimate_cost(llm_tokens, embedding_tokens),
    }


def _get_api_health(db: Session, *, since: datetime | None = None) -> dict[str, float | int]:
    total_query = select(func.count()).select_from(ApiRequestLog).where(_log_base_filter())
    success_query = (
        select(func.count())
        .select_from(ApiRequestLog)
        .where(_log_base_filter(), ApiRequestLog.status_code < 400)
    )
    if since:
        total_query = total_query.where(ApiRequestLog.created_at >= since)
        success_query = success_query.where(ApiRequestLog.created_at >= since)

    total = int(db.scalar(total_query) or 0)
    success = int(db.scalar(success_query) or 0)
    failed = total - success
    rate = round(success / total * 100, 2) if total else 100.0
    return {
        "total": total,
        "failed": failed,
        "success_rate": rate,
    }


def get_stats_overview(db: Session) -> StatsOverview:
    kb_count = db.scalar(select(func.count()).select_from(KnowledgeBase)) or 0
    document_count = db.scalar(select(func.count()).select_from(Document)) or 0
    chunk_count = db.scalar(select(func.count()).select_from(DocumentChunk)) or 0
    chat_count = db.scalar(
        select(func.count()).select_from(ChatMessage).where(ChatMessage.role == "user")
    ) or 0

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_chat_count = db.scalar(
        select(func.count())
        .select_from(ChatMessage)
        .where(ChatMessage.role == "user", ChatMessage.created_at >= today_start)
    ) or 0

    ai_all = _get_ai_usage(db)
    ai_today = _get_ai_usage(db, since=today_start)
    api_all = _get_api_health(db)
    api_today = _get_api_health(db, since=today_start)

    return StatsOverview(
        kb_count=kb_count,
        document_count=document_count,
        chunk_count=chunk_count,
        chat_count=chat_count,
        today_chat_count=today_chat_count,
        ai_estimated_tokens=ai_all["total_tokens"],
        ai_estimated_cost=ai_all["estimated_cost"],
        ai_llm_calls=ai_all["llm_calls"],
        ai_embedding_tokens=ai_all["embedding_tokens"],
        ai_llm_tokens=ai_all["llm_tokens"],
        ai_today_cost=ai_today["estimated_cost"],
        api_success_rate=float(api_all["success_rate"]),
        api_total_requests=int(api_all["total"]),
        api_failed_requests=int(api_all["failed"]),
        api_today_success_rate=float(api_today["success_rate"]),
        api_today_requests=int(api_today["total"]),
    )


def get_chat_trend(db: Session, days: int = 7) -> ChatTrendData:
    days = max(1, min(days, 30))
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=days - 1
    )

    rows = db.execute(
        select(
            func.date(ChatMessage.created_at).label("day"),
            func.count().label("count"),
        )
        .where(ChatMessage.role == "user", ChatMessage.created_at >= start_date)
        .group_by(func.date(ChatMessage.created_at))
        .order_by(func.date(ChatMessage.created_at))
    ).all()

    count_map = {str(row.day): row.count for row in rows}
    items: list[ChatTrendItem] = []
    for offset in range(days):
        day = (start_date + timedelta(days=offset)).strftime("%Y-%m-%d")
        items.append(ChatTrendItem(date=day, count=count_map.get(day, 0)))

    return ChatTrendData(items=items)


def get_api_success_trend(db: Session, days: int = 7) -> ApiTrendData:
    days = max(1, min(days, 30))
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=days - 1
    )

    rows = db.execute(
        select(
            func.date(ApiRequestLog.created_at).label("day"),
            func.count().label("total"),
            func.sum(case((ApiRequestLog.status_code < 400, 1), else_=0)).label("success"),
        )
        .where(_log_base_filter(), ApiRequestLog.created_at >= start_date)
        .group_by(func.date(ApiRequestLog.created_at))
        .order_by(func.date(ApiRequestLog.created_at))
    ).all()

    stats_map = {
        str(row.day): {
            "total": int(row.total or 0),
            "success": int(row.success or 0),
        }
        for row in rows
    }

    items: list[ApiTrendItem] = []
    for offset in range(days):
        day = (start_date + timedelta(days=offset)).strftime("%Y-%m-%d")
        stat = stats_map.get(day, {"total": 0, "success": 0})
        total = stat["total"]
        rate = round(stat["success"] / total * 100, 2) if total else 100.0
        items.append(ApiTrendItem(date=day, success_rate=rate, total=total))

    return ApiTrendData(items=items)


def get_ai_usage_trend(db: Session, days: int = 7) -> AiUsageTrendData:
    days = max(1, min(days, 30))
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
        days=days - 1
    )

    items: list[AiUsageTrendItem] = []
    for offset in range(days):
        day_start = start_date + timedelta(days=offset)
        day_end = day_start + timedelta(days=1)
        usage = _get_ai_usage_for_range(db, day_start, day_end)
        items.append(
            AiUsageTrendItem(
                date=day_start.strftime("%Y-%m-%d"),
                estimated_tokens=usage["total_tokens"],
                estimated_cost=usage["estimated_cost"],
            )
        )

    return AiUsageTrendData(items=items)


def _get_ai_usage_for_range(db: Session, start: datetime, end: datetime) -> dict[str, int | float]:
    chunk_tokens = int(
        db.scalar(
            select(func.coalesce(func.sum(DocumentChunk.token_count), 0)).where(
                DocumentChunk.created_at >= start,
                DocumentChunk.created_at < end,
            )
        )
        or 0
    )

    user_chars = int(
        db.scalar(
            select(func.coalesce(func.sum(func.length(ChatMessage.content)), 0)).where(
                ChatMessage.role == "user",
                ChatMessage.created_at >= start,
                ChatMessage.created_at < end,
            )
        )
        or 0
    )
    rag_tokens = _estimate_tokens_from_chars(user_chars)

    chat_chars = int(
        db.scalar(
            select(func.coalesce(func.sum(func.length(ChatMessage.content)), 0)).where(
                ChatMessage.created_at >= start,
                ChatMessage.created_at < end,
            )
        )
        or 0
    )
    llm_tokens = _estimate_tokens_from_chars(chat_chars)
    embedding_tokens = chunk_tokens + rag_tokens
    total_tokens = embedding_tokens + llm_tokens

    return {
        "total_tokens": total_tokens,
        "estimated_cost": _estimate_cost(llm_tokens, embedding_tokens),
    }


def get_settings_data() -> SettingsData:
    settings = get_settings()
    return SettingsData(
        rag_top_k=settings.rag_top_k,
        storage_type=settings.storage_type,
    )
