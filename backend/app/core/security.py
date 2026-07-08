from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_access_token(subject: str, expires_minutes: int, secret: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode({"sub": subject, "exp": expire}, secret, algorithm=ALGORITHM)


def decode_access_token(token: str, secret: str) -> str | None:
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
    except JWTError:
        return None
