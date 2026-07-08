from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6)
    nickname: str | None = None
    role: str = Field(default="user", pattern="^(admin|user)$")


class UserResetPasswordRequest(BaseModel):
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str | None
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}
