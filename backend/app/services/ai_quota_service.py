from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.models.admin_user import AdminUser
from app.models.ai_usage_log import AiUsageLog
from app.services.ai_cost import estimate_cost


def _today_start() -> datetime:
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def get_user_today_cost(db: Session, user_id: int) -> float:
    total = db.scalar(
        select(func.coalesce(func.sum(AiUsageLog.estimated_cost), 0.0)).where(
            AiUsageLog.user_id == user_id,
            AiUsageLog.created_at >= _today_start(),
        )
    )
    return float(total or 0.0)


def assert_user_within_daily_quota(
    db: Session,
    user: AdminUser | None,
    *,
    extra_cost: float = 0.0,
) -> None:
    if not user:
        return
    limit = get_settings().ai_daily_cost_limit_yuan
    today_cost = get_user_today_cost(db, user.id)
    if today_cost + extra_cost > limit + 1e-9:
        raise AppException(
            42901,
            f"今日 AI 消耗已达上限（{limit:g} 元/日），请明日再试",
            429,
        )


def record_ai_usage(
    db: Session,
    user: AdminUser | None,
    *,
    llm_tokens: int = 0,
    embedding_tokens: int = 0,
) -> None:
    if not user or (llm_tokens <= 0 and embedding_tokens <= 0):
        return
    cost = estimate_cost(llm_tokens, embedding_tokens)
    if cost <= 0:
        return
    db.add(
        AiUsageLog(
            user_id=user.id,
            llm_tokens=llm_tokens,
            embedding_tokens=embedding_tokens,
            estimated_cost=cost,
        )
    )
