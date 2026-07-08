from pydantic import BaseModel, Field


class ChatAskRequest(BaseModel):
    kb_id: int
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


class ReferenceItem(BaseModel):
    doc_id: int
    doc_name: str
    chunk_id: int
    snippet: str
    score: float


class ChatAskResponse(BaseModel):
    session_id: str
    answer: str
    references: list[ReferenceItem]
    latency_ms: int


class PublicKnowledgeBaseItem(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class PublicKnowledgeBaseDetail(PublicKnowledgeBaseItem):
    doc_count: int


class PublicKnowledgeBaseList(BaseModel):
    items: list[PublicKnowledgeBaseItem]


class ChatMessageItem(BaseModel):
    role: str
    content: str
    references: list[ReferenceItem] | None = None
    created_at: str


class ChatSessionMessagesResponse(BaseModel):
    session_id: str
    kb_id: int
    messages: list[ChatMessageItem]


class AdminChatSessionItem(BaseModel):
    id: str
    kb_id: int
    kb_name: str
    title: str | None
    client_type: str | None
    message_count: int
    created_at: str


class AdminChatSessionDetail(BaseModel):
    id: str
    kb_id: int
    title: str | None


class AdminChatMessageItem(BaseModel):
    id: int
    role: str
    content: str
    references_json: list | None
    latency_ms: int | None
    created_at: str


class AdminChatMessagesResponse(BaseModel):
    session: AdminChatSessionDetail
    messages: list[AdminChatMessageItem]
