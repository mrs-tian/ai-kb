from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    is_public: bool = True


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    status: str | None = Field(default=None, pattern="^(active|disabled)$")
    is_public: bool | None = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: str | None
    status: str
    is_public: bool
    doc_count: int
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
