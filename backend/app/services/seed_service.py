from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth import get_user_by_username, hash_password
from app.config import settings
from app.models import User


def seed_users(db: Session) -> list[str]:
    created: list[str] = []
    admin_username = (settings.auth_admin_username or "admin").lower()
    admin_password = settings.auth_admin_password or "admin123"
    reporter_username = (settings.auth_reporter_username or settings.auth_responder_username or "reporter").lower()
    reporter_password = settings.auth_reporter_password or settings.auth_responder_password or "reporter123"

    if settings.app_env == "production":
        if not settings.auth_admin_username or not settings.auth_admin_password:
            raise RuntimeError("AUTH_ADMIN_USERNAME and AUTH_ADMIN_PASSWORD are required in production.")
        if admin_password in {"admin123", "password", "password123"}:
            raise RuntimeError("Default admin passwords are not allowed in production.")

    created.extend(_upsert_user(db, admin_username, admin_password, "admin"))
    created.extend(_upsert_user(db, reporter_username, reporter_password, "reporter"))
    db.commit()
    return created


def _upsert_user(db: Session, username: str, password: str, role: str) -> list[str]:
    user = get_user_by_username(db, username)
    if user is None:
        user = User(username=username, password_hash=hash_password(password), role=role, is_active=True)
        db.add(user)
        db.flush()
        return [username]
    user.role = role
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    return []
