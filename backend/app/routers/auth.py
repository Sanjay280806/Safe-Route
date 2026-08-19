from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_user_by_username, verify_password
from app.config import settings
from app.database import get_db
from app.dependencies import login_is_rate_limited, record_failed_login
from app.schemas import LoginRequest, LoginResponse, AuthUser
from app.utils.errors import APIError


router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> LoginResponse:
    ip = request.client.host if request.client else "unknown"
    if login_is_rate_limited(ip):
        raise APIError(429, "RATE_LIMITED", "Too many failed login attempts. Try again later.")

    user = get_user_by_username(db, payload.username)
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        record_failed_login(ip)
        raise APIError(401, "INVALID_CREDENTIALS", "Invalid username or password.")

    token = create_access_token(user)
    return LoginResponse(
        access_token=token,
        token_type="Bearer",
        expires_in=settings.jwt_expire_seconds,
        user=AuthUser(id=user.id, username=user.username, role=user.role),
    )
