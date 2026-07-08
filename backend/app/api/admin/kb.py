from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.kb import KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseUpdate
from app.services.kb_service import (
    create_knowledge_base,
    delete_knowledge_base,
    get_kb_or_404,
    list_knowledge_bases,
    update_knowledge_base,
)

router = APIRouter(prefix="/admin/kb", dependencies=[Depends(get_current_admin)])


@router.get("", response_model=ApiResponse[PaginatedData[KnowledgeBaseResponse]])
def get_kb_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[PaginatedData[KnowledgeBaseResponse]]:
    items, total = list_knowledge_bases(db, page=page, page_size=page_size, keyword=keyword)
    data = PaginatedData[KnowledgeBaseResponse](
        items=[KnowledgeBaseResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)


@router.post("", response_model=ApiResponse[KnowledgeBaseResponse])
def create_kb(
    body: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[KnowledgeBaseResponse]:
    kb = create_knowledge_base(db, body)
    return ApiResponse(data=KnowledgeBaseResponse.model_validate(kb))


@router.get("/{kb_id}", response_model=ApiResponse[KnowledgeBaseResponse])
def get_kb_detail(
    kb_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[KnowledgeBaseResponse]:
    kb = get_kb_or_404(db, kb_id)
    return ApiResponse(data=KnowledgeBaseResponse.model_validate(kb))


@router.put("/{kb_id}", response_model=ApiResponse[KnowledgeBaseResponse])
def update_kb(
    kb_id: int,
    body: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[KnowledgeBaseResponse]:
    kb = update_knowledge_base(db, kb_id, body)
    return ApiResponse(data=KnowledgeBaseResponse.model_validate(kb))


@router.delete("/{kb_id}", response_model=ApiResponse[None])
def delete_kb(
    kb_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[None]:
    delete_knowledge_base(db, kb_id)
    return ApiResponse(message="删除成功")
