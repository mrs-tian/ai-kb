from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    kb_id: int
    filename: str
    file_ext: str
    file_size: int
    char_count: int
    status: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
