from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.admin_user import AdminUser


def seed_admin_user(db: Session) -> None:
    settings = get_settings()
    existing = db.scalar(
        select(AdminUser).where(AdminUser.username == settings.admin_username)
    )
    if existing:
        return

    admin = AdminUser(
        username=settings.admin_username,
        password_hash=hash_password(settings.admin_password),
        nickname="管理员",
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()


def init_db() -> None:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()
