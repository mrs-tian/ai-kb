from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.chat import (
    PublicKnowledgeBaseDetail,
    PublicKnowledgeBaseItem,
    PublicKnowledgeBaseList,
)
from app.schemas.common import ApiResponse
from app.services.chat_service import get_public_kb_or_404, list_public_knowledge_bases

router = APIRouter(prefix="/public/kb", tags=["public-kb"])


@router.get("", response_model=ApiResponse[PublicKnowledgeBaseList])
def get_public_kb_list(db: Session = Depends(get_db)) -> ApiResponse[PublicKnowledgeBaseList]:
    items = list_public_knowledge_bases(db)
    data = PublicKnowledgeBaseList(
        items=[PublicKnowledgeBaseItem.model_validate(item) for item in items]
    )
    return ApiResponse(data=data)


@router.get("/{kb_id}", response_model=ApiResponse[PublicKnowledgeBaseDetail])
def get_public_kb_detail(
    kb_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[PublicKnowledgeBaseDetail]:
    kb = get_public_kb_or_404(db, kb_id)
    return ApiResponse(
        data=PublicKnowledgeBaseDetail(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            doc_count=kb.doc_count,
        )
    )
