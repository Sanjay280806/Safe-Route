from collections import defaultdict
from time import time

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.auth import decode_access_token, get_user_by_id
from app.database import get_db
from app.models import User
from app.utils.errors import APIError
from jose import JWTError


_failed_logins: dict[str, list[float]] = defaultdict(list)


def record_failed_login(ip: str) -> None:
    now = time()
    attempts = [stamp for stamp in _failed_logins[ip] if now - stamp < 60]
    attempts.append(now)
    _failed_logins[ip] = attempts


def login_is_rate_limited(ip: str) -> bool:
    now = time()
    attempts = [stamp for stamp in _failed_logins.get(ip, []) if now - stamp < 60]
    _failed_logins[ip] = attempts
    return len(attempts) >= 5


def get_optional_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise APIError(401, "UNAUTHORIZED", "Invalid authorization header.")
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise APIError(401, "UNAUTHORIZED", "Invalid or expired token.")
    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise APIError(401, "UNAUTHORIZED", "Invalid or expired token.")
    return user


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    if user is None:
        raise APIError(401, "UNAUTHORIZED", "Authentication required.")
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise APIError(403, "FORBIDDEN", "You do not have permission to perform this action.")
        return user

    return dependency
