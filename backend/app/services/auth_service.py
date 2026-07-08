from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.security import create_access_token, verify_password
from app.models.admin_user import AdminUser
from app.schemas.auth import LoginResponse


def authenticate_admin(db: Session, username: str, password: str) -> AdminUser | None:
    user = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login_admin(db: Session, username: str, password: str) -> LoginResponse:
    user = authenticate_admin(db, username, password)
    if not user:
        raise AppException(40001, "用户名或密码错误", 401)

    settings = get_settings()
    expires_in = settings.jwt_expire_minutes * 60
    token = create_access_token(
        subject=user.username,
        expires_minutes=settings.jwt_expire_minutes,
        secret=settings.jwt_secret,
    )
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
    )
