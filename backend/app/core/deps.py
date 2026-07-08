from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.db.session import get_db as _get_db
from app.models.admin_user import AdminUser

security_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException(40101, "未登录或 token 无效", 401)

    settings = get_settings()
    username = decode_access_token(credentials.credentials, settings.jwt_secret)
    if not username:
        raise AppException(40101, "未登录或 token 无效", 401)

    user = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if not user or not user.is_active:
        raise AppException(40101, "未登录或 token 无效", 401)

    return user


def require_admin(current: AdminUser = Depends(get_current_admin)) -> AdminUser:
    if current.role != "admin":
        raise AppException(40301, "无权限访问", 403)
    return current
