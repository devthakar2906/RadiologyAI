from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut
from app.services.logging_service import create_log
from app.services.redis_client import check_rate_limit
from app.services.security import create_access_token, get_password_hash, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/signup", response_model=Token)
def signup(payload: UserCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    rate_key = f"rate:auth:signup:{request.client.host if request.client else 'unknown'}"
    if not check_rate_limit(
        key=rate_key,
        limit=settings.auth_rate_limit_count,
        window_seconds=settings.auth_rate_limit_window_seconds,
    ):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many signup attempts")

    normalized_email = payload.email.strip().lower()
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if payload.role not in {"doctor", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user = User(
        name=payload.name,
        email=normalized_email,
        password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    create_log(db, user.id, "signup", "success")
    token = create_access_token(str(user.id), user.role)
    _set_auth_cookie(response, token)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, response: Response, request: Request, db: Session = Depends(get_db)):
    rate_key = f"rate:auth:login:{request.client.host if request.client else 'unknown'}"
    if not check_rate_limit(
        key=rate_key,
        limit=settings.auth_rate_limit_count,
        window_seconds=settings.auth_rate_limit_window_seconds,
    ):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts")

    normalized_email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == normalized_email))
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    create_log(db, user.id, "login", "success")
    token = create_access_token(str(user.id), user.role)
    _set_auth_cookie(response, token)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(key=settings.auth_cookie_name, path="/")


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
