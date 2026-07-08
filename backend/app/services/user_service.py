from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import hash_password
from app.models.admin_user import AdminUser


def list_users(
    db: Session,
    *,
    page: int,
    page_size: int,
    keyword: str | None = None,
) -> tuple[list[AdminUser], int]:
    query = select(AdminUser)
    if keyword:
        pattern = f"%{keyword.strip()}%"
        query = query.where(
            AdminUser.username.ilike(pattern) | AdminUser.nickname.ilike(pattern)
        )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(
        db.scalars(
            query.order_by(AdminUser.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return items, total


def create_user(
    db: Session,
    *,
    username: str,
    password: str,
    nickname: str | None = None,
    role: str = "user",
) -> AdminUser:
    username = username.strip()
    if not username:
        raise AppException(40001, "用户名不能为空", 400)
    if role not in {"admin", "user"}:
        raise AppException(40001, "角色无效", 400)
    existing = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if existing:
        raise AppException(40001, "用户名已存在", 400)

    user = AdminUser(
        username=username,
        password_hash=hash_password(password),
        nickname=nickname or username,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user_id: int, password: str) -> AdminUser:
    user = db.get(AdminUser, user_id)
    if not user:
        raise AppException(40401, "用户不存在", 404)
    if not password.strip():
        raise AppException(40001, "密码不能为空", 400)
    user.password_hash = hash_password(password)
    db.commit()
    db.refresh(user)
    return user
