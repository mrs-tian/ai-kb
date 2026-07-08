from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    role: str

    model_config = {"from_attributes": True}


class AiConfigResponse(BaseModel):
    ai_provider: str | None = None
    ai_provider_label: str | None = None
    api_key_masked: str | None = None
    api_key_configured: bool = False


class AiConfigUpdateRequest(BaseModel):
    ai_provider: str = Field(pattern="^(deepseek|qwen)$")
    api_key: str = Field(min_length=1)


class AiProviderOption(BaseModel):
    value: str
    label: str
