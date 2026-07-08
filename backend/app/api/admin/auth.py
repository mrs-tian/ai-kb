from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.ai_providers import AI_PROVIDERS
from app.core.deps import get_current_admin, get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import (
    AdminUserResponse,
    AiConfigResponse,
    AiConfigUpdateRequest,
    AiProviderOption,
    LoginRequest,
    LoginResponse,
)
from app.schemas.common import ApiResponse
from app.services.ai_config_service import build_ai_config_response, update_user_ai_config
from app.services.auth_service import login_admin

router = APIRouter()


@router.post("/login", response_model=ApiResponse[LoginResponse])
def login(body: LoginRequest, db: Session = Depends(get_db)) -> ApiResponse[LoginResponse]:
    data = login_admin(db, body.username, body.password)
    return ApiResponse(data=data)


@router.get("/me", response_model=ApiResponse[AdminUserResponse])
def get_me(current_admin: AdminUser = Depends(get_current_admin)) -> ApiResponse[AdminUserResponse]:
    return ApiResponse(data=AdminUserResponse.model_validate(current_admin))


@router.get("/ai-config", response_model=ApiResponse[AiConfigResponse])
def get_ai_config(
    current_admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[AiConfigResponse]:
    return ApiResponse(data=AiConfigResponse(**build_ai_config_response(current_admin)))


@router.put("/ai-config", response_model=ApiResponse[AiConfigResponse])
def put_ai_config(
    body: AiConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[AiConfigResponse]:
    update_user_ai_config(current_admin, provider=body.ai_provider, api_key=body.api_key)
    db.commit()
    db.refresh(current_admin)
    return ApiResponse(data=AiConfigResponse(**build_ai_config_response(current_admin)))


@router.get("/ai-providers", response_model=ApiResponse[list[AiProviderOption]])
def get_ai_providers(
    _current_admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[list[AiProviderOption]]:
    items = [
        AiProviderOption(value=key, label=value["label"]) for key, value in AI_PROVIDERS.items()
    ]
    return ApiResponse(data=items)
