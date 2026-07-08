from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.log import ApiLogItem, ClearLogsData
from app.services.log_service import clear_api_logs, list_api_logs

router = APIRouter(prefix="/admin/logs", dependencies=[Depends(require_admin)])


def _serialize_log(log) -> ApiLogItem:
    return ApiLogItem(
        id=log.id,
        method=log.method,
        path=log.path,
        query_string=log.query_string,
        status_code=log.status_code,
        response_body=log.response_body,
        user_id=log.user_id,
        username=log.username,
        client_ip=log.client_ip,
        duration_ms=log.duration_ms,
        is_authenticated=log.is_authenticated,
        created_at=log.created_at.isoformat(),
    )


@router.get("", response_model=ApiResponse[PaginatedData[ApiLogItem]])
def get_api_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: str | None = Query(None),
    path_keyword: str | None = Query(None),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> ApiResponse[PaginatedData[ApiLogItem]]:
    items, total = list_api_logs(
        db,
        page=page,
        page_size=page_size,
        username=username,
        path_keyword=path_keyword,
        start_time=start_time,
        end_time=end_time,
    )
    data = PaginatedData[ApiLogItem](
        items=[_serialize_log(log) for log in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)


@router.delete("", response_model=ApiResponse[ClearLogsData])
def delete_api_logs(
    username: str | None = Query(None),
    path_keyword: str | None = Query(None),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> ApiResponse[ClearLogsData]:
    deleted_count = clear_api_logs(
        db,
        username=username,
        path_keyword=path_keyword,
        start_time=start_time,
        end_time=end_time,
    )
    return ApiResponse(data=ClearLogsData(deleted_count=deleted_count), message="日志已清除")
