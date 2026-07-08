from datetime import datetime

from pydantic import BaseModel


class ApiLogItem(BaseModel):
    id: int
    method: str
    path: str
    query_string: str | None
    status_code: int
    response_body: str | None
    user_id: int | None
    username: str | None
    client_ip: str | None
    duration_ms: int
    is_authenticated: bool
    created_at: str

    model_config = {"from_attributes": True}


class ClearLogsData(BaseModel):
    deleted_count: int
