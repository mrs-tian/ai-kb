from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_db
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    delete_document,
    get_document_or_404,
    list_documents,
    reparse_document,
    upload_document,
)

router = APIRouter(prefix="/admin", dependencies=[Depends(get_current_admin)])


@router.get("/kb/{kb_id}/documents", response_model=ApiResponse[PaginatedData[DocumentResponse]])
def get_documents(
    kb_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[PaginatedData[DocumentResponse]]:
    items, total = list_documents(db, kb_id, page=page, page_size=page_size)
    data = PaginatedData[DocumentResponse](
        items=[DocumentResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=data)


@router.post("/kb/{kb_id}/documents", response_model=ApiResponse[DocumentResponse])
async def post_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[DocumentResponse]:
    document = await upload_document(db, kb_id, file, _admin)
    return ApiResponse(data=DocumentResponse.model_validate(document))


@router.get("/documents/{document_id}", response_model=ApiResponse[DocumentResponse])
def get_document_detail(
    document_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[DocumentResponse]:
    document = get_document_or_404(db, document_id)
    return ApiResponse(data=DocumentResponse.model_validate(document))


@router.delete("/documents/{document_id}", response_model=ApiResponse[None])
async def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[None]:
    await delete_document(db, document_id)
    return ApiResponse(message="删除成功")


@router.post("/documents/{document_id}/reparse", response_model=ApiResponse[DocumentResponse])
def post_reparse_document(
    document_id: int,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> ApiResponse[DocumentResponse]:
    document = reparse_document(db, document_id, _admin)
    return ApiResponse(data=DocumentResponse.model_validate(document))
