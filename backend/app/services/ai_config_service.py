from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.ai_providers import AI_PROVIDERS, AiCredentials, get_provider_config
from app.core.config import get_settings
from app.core.crypto import decrypt_secret, encrypt_secret, mask_secret
from app.core.exceptions import AppException
from app.models.admin_user import AdminUser


def resolve_ai_credentials(user: AdminUser | None) -> AiCredentials | None:
    if not user or not user.api_key_encrypted or not user.ai_provider:
        return None
    provider = user.ai_provider
    config = get_provider_config(provider)
    api_key = decrypt_secret(user.api_key_encrypted)
    return AiCredentials(
        provider=provider,
        api_key=api_key,
        base_url=config["base_url"],
        llm_model=config["llm_model"],
        embedding_model=config["embedding_model"],
    )


def resolve_public_ai_credentials(db: Session) -> AiCredentials | None:
    """C 端无登录用户，使用指定管理员账号（默认 admin）已配置的 AI Key。"""
    settings = get_settings()
    user = db.scalar(
        select(AdminUser).where(
            AdminUser.username == settings.public_ai_username,
            AdminUser.is_active.is_(True),
        )
    )
    return resolve_ai_credentials(user)


def resolve_effective_ai_credentials(
    db: Session,
    user: AdminUser | None,
) -> AiCredentials | None:
    if user:
        return resolve_ai_credentials(user)
    return resolve_public_ai_credentials(db)


def build_ai_config_response(user: AdminUser) -> dict:
    masked_key = None
    if user.api_key_encrypted:
        try:
            masked_key = mask_secret(decrypt_secret(user.api_key_encrypted))
        except ValueError:
            masked_key = "****"
    provider_label = None
    if user.ai_provider and user.ai_provider in AI_PROVIDERS:
        provider_label = AI_PROVIDERS[user.ai_provider]["label"]
    return {
        "ai_provider": user.ai_provider,
        "ai_provider_label": provider_label,
        "api_key_masked": masked_key,
        "api_key_configured": bool(user.api_key_encrypted),
    }


def update_user_ai_config(user: AdminUser, *, provider: str, api_key: str) -> AdminUser:
    if provider not in AI_PROVIDERS:
        raise AppException(40001, "不支持的 AI 提供商", 400)
    api_key = api_key.strip()
    if not api_key:
        raise AppException(40001, "API Key 不能为空", 400)
    user.ai_provider = provider
    user.api_key_encrypted = encrypt_secret(api_key)
    return user
