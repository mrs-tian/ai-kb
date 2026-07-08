from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db, require_admin
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.user import UserCreateRequest, UserResetPasswordRequest, UserResponse
from app.services.user_service import create_user, list_users, reset_user_password

router = APIRouter(prefix="/admin/users", dependencies=[Depends(require_admin)])


@router.get("", response_model=ApiResponse[PaginatedData[UserResponse]])
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> ApiResponse[PaginatedData[UserResponse]]:
    items, total = list_users(db, page=page, page_size=page_size, keyword=keyword)
    data = PaginatedData[UserResponse](
        items=[
            UserResponse(
                id=user.id,
                username=user.username,
                nickname=user.nickname,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
            )
            for user in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)


@router.post("", response_model=ApiResponse[UserResponse])
def post_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> ApiResponse[UserResponse]:
    user = create_user(
        db,
        username=body.username,
        password=body.password,
        nickname=body.nickname,
        role=body.role,
    )
    return ApiResponse(
        data=UserResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )
    )


@router.put("/{user_id}/password", response_model=ApiResponse[None])
def put_user_password(
    user_id: int,
    body: UserResetPasswordRequest,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(require_admin),
) -> ApiResponse[None]:
    reset_user_password(db, user_id, body.password)
    return ApiResponse(message="密码已重置")
