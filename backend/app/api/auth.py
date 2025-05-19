from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.manager import UserManagerDependency
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_session
from app.models.user import User, UserCreate, UserUpdate, UserDB
from app.core.config import settings
from sqlmodel import select
import secrets
from app.core.security import get_password_hash
from app.core.email import send_email

router = APIRouter()

# JWT Configuration
SECRET = settings.SECRET_KEY
LIFETIME = 3600  # 1 hour

# Bearer transport for JWT
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=LIFETIME)

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# User database
async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, UserDB)

# User manager
async def get_user_manager():
    user_db = SQLAlchemyUserDatabase(AsyncSession(), UserDB)
    yield user_db

# FastAPI Users instance with simplified initialization
fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
)

# Current user dependency
current_active_user = fastapi_users.current_user(active=True)

# Include FastAPI Users routers
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_register_router(UserCreate, UserDB),
    prefix="/auth",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_users_router(UserCreate, UserDB),
    prefix="/users",
    tags=["users"]
)

# Password reset endpoints
@router.post("/auth/forgot-password")
async def forgot_password(email: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        session.add(user)
        await session.commit()
        # Send reset email using Resend
        await send_email(
            email_to=user.email,
            subject="Password Reset Request",
            body=f"Click the link to reset your password: http://yourdomain.com/reset-password?token={reset_token}"
        )
    return {"message": "If an account exists with this email, you will receive a password reset link"}

@router.post("/auth/reset-password")
async def reset_password(token: str, new_password: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    session.add(user)
    await session.commit()
    return {"message": "Password has been reset successfully"}

# User profile endpoint
@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(current_active_user)):
    return current_user

# Update user profile
@router.patch("/users/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session)
):
    # Update user profile
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user

@router.post("/verify/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.verification_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    user.is_verified = True
    user.verification_token = None
    session.add(user)
    await session.commit()
    return {"message": "Email verified successfully."}
