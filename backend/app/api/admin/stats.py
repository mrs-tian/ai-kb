from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse
from app.schemas.stats import (
    AiUsageTrendData,
    ApiTrendData,
    ChatTrendData,
    SettingsData,
    StatsOverview,
)
from app.services.stats_service import (
    get_ai_usage_trend,
    get_api_success_trend,
    get_chat_trend,
    get_settings_data,
    get_stats_overview,
)

router = APIRouter(prefix="/admin", dependencies=[Depends(get_current_admin)])


@router.get("/stats/overview", response_model=ApiResponse[StatsOverview])
def stats_overview(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[StatsOverview]:
    return ApiResponse(data=get_stats_overview(db))


@router.get("/stats/chat-trend", response_model=ApiResponse[ChatTrendData])
def stats_chat_trend(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[ChatTrendData]:
    return ApiResponse(data=get_chat_trend(db, days=days))


@router.get("/stats/api-trend", response_model=ApiResponse[ApiTrendData])
def stats_api_trend(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[ApiTrendData]:
    return ApiResponse(data=get_api_success_trend(db, days=days))


@router.get("/stats/ai-trend", response_model=ApiResponse[AiUsageTrendData])
def stats_ai_trend(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[AiUsageTrendData]:
    return ApiResponse(data=get_ai_usage_trend(db, days=days))


@router.get("/settings", response_model=ApiResponse[SettingsData])
def get_settings(
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[SettingsData]:
    return ApiResponse(data=get_settings_data())
