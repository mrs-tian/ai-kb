from pydantic import BaseModel


class StatsOverview(BaseModel):
    kb_count: int
    document_count: int
    chunk_count: int
    chat_count: int
    today_chat_count: int
    ai_estimated_tokens: int
    ai_estimated_cost: float
    ai_llm_calls: int
    ai_embedding_tokens: int
    ai_llm_tokens: int
    ai_today_cost: float
    api_success_rate: float
    api_total_requests: int
    api_failed_requests: int
    api_today_success_rate: float
    api_today_requests: int


class ApiTrendItem(BaseModel):
    date: str
    success_rate: float
    total: int


class ApiTrendData(BaseModel):
    items: list[ApiTrendItem]


class AiUsageTrendItem(BaseModel):
    date: str
    estimated_tokens: int
    estimated_cost: float


class AiUsageTrendData(BaseModel):
    items: list[AiUsageTrendItem]


class ChatTrendItem(BaseModel):
    date: str
    count: int


class ChatTrendData(BaseModel):
    items: list[ChatTrendItem]


class SettingsData(BaseModel):
    rag_top_k: int
    storage_type: str
