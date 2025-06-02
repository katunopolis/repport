from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.database import get_session
from app.models.user import User, UserCreate, UserUpdate, UserDB, UserResponse
from app.core.config import settings
from sqlmodel import select
import secrets
from app.core.security import get_password_hash, verify_password
from app.core.email import send_email
import logging
import os

router = APIRouter()

# JWT Configuration
SECRET = settings.SECRET_KEY
LIFETIME = 3600  # 1 hour

# Bearer transport for JWT
bearer_transport = BearerTransport(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=LIFETIME)

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# Define a proper user manager class
class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(self, user: User, request=None):
        print(f"User {user.id} has reset their password.")
        
    def parse_id(self, value: str) -> int:
        return int(value)
        
    # Override validate_password method to fix the password validation issue
    async def validate_password(self, password: str, user_create: Any) -> None:
        # Simple password validation
        if len(password) < 8:
            raise ValueError("Password should be at least 8 characters")
        return None
        
    # Override create method to completely handle password validation properly
    async def create(self, user_create: Any, safe: bool = False, request=None) -> User:
        """
        Create a user in database.
        Triggers password validation and user_create validation.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser will be ignored
            during the creation, defaults to False.
        :param request: Optional request object associated with this operation
        :return: A new user.
        """
        logger = logging.getLogger(__name__)
        
        # Debug log to inspect what we're receiving
        logger.info(f"Received user_create object: {type(user_create).__name__}")
        logger.info(f"user_create attributes: {dir(user_create)}")
        
        # Try to extract password in various ways since fastapi_users may pass it differently
        password = None
        
        # Method 1: Get from attribute directly if it exists
        if hasattr(user_create, "password"):
            password = user_create.password
            logger.info("Got password from direct attribute access")
            
        # Method 2: Try to get from dict method if available
        elif hasattr(user_create, "dict") and callable(getattr(user_create, "dict")):
            user_dict = user_create.dict()
            if "password" in user_dict:
                password = user_dict["password"]
                logger.info("Got password from dict() method")
                
        # Method 3: Try to get from __dict__ attribute
        elif hasattr(user_create, "__dict__"):
            if "password" in user_create.__dict__:
                password = user_create.__dict__["password"]
                logger.info("Got password from __dict__ attribute")
        
        # Method 4: Check if user_create is itself a dict
        elif isinstance(user_create, dict) and "password" in user_create:
            password = user_create["password"]
            logger.info("Got password from dict object")
            
        # When the register endpoint is called via FastAPI Users, "password" might be encapsulated
        # Let's try to extract it from the request object if available
        if not password and request and hasattr(request, "json"):
            try:
                json_data = await request.json()
                if "password" in json_data:
                    password = json_data["password"]
                    logger.info("Got password from request JSON data")
            except Exception as e:
                logger.warning(f"Error extracting JSON from request: {str(e)}")
                
        # Log the password presence (not the actual value, for security)
        logger.info(f"Password found: {password is not None}")
        
        # Ensure we have a password
        if not password:
            # Handle missing password more gracefully - this is debug code
            # Since we're in development, let's use a default password for testing
            logger.warning("Password missing - no default password will be set in production mode")
            if settings.ENVIRONMENT == "development":
                logger.warning("DEVELOPMENT MODE: Using placeholder password")
                password = os.getenv("DEFAULT_DEV_PASSWORD", "")  # Use environment variable instead of hardcoded value
            else:
                raise ValueError("Password is required")
        
        # Always validate the password
        try:
            await self.validate_password(password, user_create)
            logger.info(f"Password validated successfully for: {getattr(user_create, 'email', 'unknown')}")
        except Exception as e:
            logger.error(f"Password validation failed: {str(e)}")
            raise e
        
        # Get user_create data
        user_dict = {}
        
        # Try to extract data in various ways
        if hasattr(user_create, "dict") and callable(getattr(user_create, "dict")):
            # If user_create has a dict method (like Pydantic models)
            temp_dict = user_create.dict()
            for key, value in temp_dict.items():
                if key != "password":  # Skip password as we handle it separately
                    user_dict[key] = value
            logger.info("Extracted user data using dict() method")
        elif hasattr(user_create, "__dict__"):
            # If user_create has a __dict__ attribute
            for key, value in user_create.__dict__.items():
                if key != "password" and not key.startswith("_"):
                    user_dict[key] = value
            logger.info("Extracted user data using __dict__ attribute")
        elif isinstance(user_create, dict):
            # If user_create is a dict
            for key, value in user_create.items():
                if key != "password":
                    user_dict[key] = value
            logger.info("Extracted user data from dict object")
        
        # Extract email if not in user_dict yet
        if "email" not in user_dict and hasattr(user_create, "email"):
            user_dict["email"] = user_create.email
            
        # Set defaults for required fields if missing
        user_dict.setdefault("is_active", True)
        user_dict.setdefault("is_superuser", False)
        user_dict.setdefault("is_verified", False)
        
        # Handle safe parameter to restrict fields
        if safe:
            user_dict.pop("is_superuser", None)
            user_dict.pop("is_verified", None)
        
        # Always hash the password and ensure hashed_password is set
        hashed_password = get_password_hash(password)
        user_dict["hashed_password"] = hashed_password
        
        logger.info(f"Creating user with email: {user_dict.get('email')}, hashed_password length: {len(hashed_password)}")
        
        # Create user model and save to DB
        user = User(**user_dict)
        
        self.user_db.session.add(user)
        await self.user_db.session.commit()
        await self.user_db.session.refresh(user)
        
        # Trigger after register event
        await self.on_after_register(user, request)
        
        return user

# User database
async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)

# User manager dependency
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# FastAPI Users instance with proper initialization
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Current user dependency
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# Include FastAPI Users routers with updated schemas
router.include_router(
    fastapi_users.get_register_router(UserCreate, UserResponse),
    prefix="/auth",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_users_router(UserUpdate, UserResponse),
    prefix="/users",
    tags=["users"]
)

# Custom logout endpoint - placed OUTSIDE the auth prefix to avoid auth requirements
@router.post("/logout")
async def logout():
    # Since we're using JWTs, server-side logout isn't needed
    # The client just removes the token from local storage
    return {"status": "success", "message": "Logged out successfully"}

# Duplicate logout endpoint with /auth prefix to match what frontend is calling
@router.post("/auth/logout")
async def logout_with_auth_prefix():
    # Same implementation as the original logout endpoint
    return {"status": "success", "message": "Logged out successfully"}

# Password reset endpoints
@router.post("/auth/forgot-password")
async def forgot_password(
    email: str = Body(..., embed=True), 
    session: AsyncSession = Depends(get_session)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Password reset request for email: {email}")
    
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        # Generate a secure token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        session.add(user)
        await session.commit()
        logger.info(f"Generated reset token for user {email}")
        
        # In a real production app, we would send an email
        try:
            # Send reset email using Resend or your preferred email service
            await send_email(
                email_to=user.email,
                subject="Password Reset Request",
                body=f"Your password reset token is: {reset_token}\n\nUse this token to reset your password."
            )
            logger.info(f"Sent password reset email to {email}")
        except Exception as e:
            logger.error(f"Failed to send reset email: {str(e)}")
            # For development, we'll still return the token directly
            if settings.ENVIRONMENT != "production":
                logger.info(f"Development mode: Returning token directly in response")
                return {
                    "message": "Password reset token generated. In production, this would be emailed.",
                    "token": reset_token,  # Only included in development mode!
                    "_dev_note": "This token is only returned in development mode"
                }
    else:
        logger.warning(f"Password reset requested for non-existent email: {email}")
    
    # Always return the same message whether the user exists or not
    # to prevent email enumeration attacks
    return {"message": "If an account exists with this email, you will receive a password reset link"}

@router.post("/auth/reset-password")
async def reset_password(
    token: str = Body(..., embed=True), 
    new_password: str = Body(..., embed=True), 
    session: AsyncSession = Depends(get_session)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Password reset attempt with token: {token[:10]}...")
    
    # Check for minimum password length
    if len(new_password) < 8:
        logger.warning("Password reset failed: Password too short")
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    result = await session.execute(select(User).where(User.reset_token == token))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning("Password reset failed: Invalid or expired token")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    # Update password and clear the reset token
    logger.info(f"Resetting password for user: {user.email}")
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    session.add(user)
    await session.commit()
    
    logger.info(f"Password reset successful for user: {user.email}")
    return {"message": "Password has been reset successfully"}

# User profile endpoint - moved to top level to be accessible at /api/v1/users/me
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

# Custom user creation endpoint for admin dashboard
@router.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)
):
    # Log authentication info for debugging
    logger = logging.getLogger(__name__)
    logger.info(f"Create user request received. Auth user: {current_user.email}, is_superuser: {current_user.is_superuser}")
    
    # Only admins can create users
    if not current_user.is_superuser:
        logger.warning(f"User {current_user.email} attempted to create a user but lacks admin privileges")
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    # Check if user exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"Attempted to create duplicate user with email {user_data.email}")
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create new user
    logger.info(f"Creating new user with email: {user_data.email}, is_superuser: {getattr(user_data, 'is_superuser', False)}")
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_superuser=getattr(user_data, "is_superuser", False),
        is_verified=True
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    logger.info(f"Successfully created user with ID: {new_user.id}")
    
    return new_user

# Same endpoint with trailing slash
@router.post("/users/", response_model=User)
async def create_user_with_slash(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Create user with trailing slash endpoint called. Forwarding to main endpoint. Auth user: {current_user.email}")
    return await create_user(user_data, session, current_user)

# Custom endpoint to list all users
@router.get("/users", response_model=List[User])
async def list_users(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)
):
    # Only admins can list all users
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Use SQLModel select instead of raw SQL
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

# Same endpoint with trailing slash
@router.get("/users/", response_model=List[User])
async def list_users_with_slash(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)
):
    return await list_users(session, current_user)

# Get a specific user
@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)
):
    # Only admins can view specific users
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Update a specific user
@router.patch("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,  # Changed from dict to UserUpdate
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)  # Changed to require superuser
):
    # Only admins can update users
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields using the UserUpdate model
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

# Delete a user
@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_superuser)
):
    # Only admins can delete users
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await session.delete(user)
    await session.commit()
    
    return None

# Password change endpoint for authenticated users
@router.post("/users/me/change-password", status_code=200)
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Password change request for user ID: {current_user.id}")
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        logger.warning(f"Password change failed: Invalid current password for user ID {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    
    # Validate new password
    if len(new_password) < 8:
        logger.warning(f"Password change failed: New password too short for user ID {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )
    
    # Prevent reusing the same password
    if verify_password(new_password, current_user.hashed_password):
        logger.warning(f"Password change failed: New password is same as current password for user ID {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as your current password",
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    session.add(current_user)
    await session.commit()
    
    logger.info(f"Password changed successfully for user ID: {current_user.id}")
    return {"message": "Password changed successfully"}

# Specific endpoint just for promoting/demoting a user to admin
@router.patch("/users/{user_id}/promote", response_model=User)
async def promote_user(
    user_id: int,
    is_superuser: bool = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_active_user)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Promote user request for user ID {user_id} to admin status: {is_superuser}")
    logger.info(f"Request by user: {current_user.email}, is_superuser: {current_user.is_superuser}")
    
    # Get the target user first
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"Failed to find user with ID {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if this is the first user trying to promote themselves
    result = await session.execute(select(User))
    all_users = result.scalars().all()
    is_first_user = len(all_users) == 1 and current_user.id == user_id
    
    # Allow promotion if:
    # 1. The current user is a superuser, or
    # 2. This is the first user in the system promoting themselves
    if not current_user.is_superuser and not is_first_user:
        logger.warning(f"Non-admin user {current_user.email} attempted to modify admin status")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Don't allow demoting yourself unless there's another admin
    if current_user.id == user_id and not is_superuser:
        # Count how many other admins exist
        result = await session.execute(
            select(User).where(
                User.is_superuser == True,
                User.id != current_user.id
            )
        )
        other_admins = result.scalars().all()
        if not other_admins:
            logger.warning(f"User {current_user.email} attempted to demote themselves when they are the only admin")
            raise HTTPException(status_code=400, detail="Cannot demote yourself when you are the only admin")
    
    # Update admin status
    logger.info(f"Changing admin status for user {user.email} from {user.is_superuser} to {is_superuser}")
    user.is_superuser = is_superuser
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    logger.info(f"Successfully updated admin status for user {user.email}")
    return user

# Custom signup endpoint that bypasses FastAPI Users
@router.post("/auth/signup")
async def custom_signup(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user_manager: UserManager = Depends(get_user_manager)
):
    # Extract user data from request
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email and password are required"
            )
        
        # Check if user already exists before attempting to create
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        
        # Create a proper UserCreate object with all required fields
        user_dict = {
            "email": email,
            "password": password,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        }
        
        user_create = UserCreate(**user_dict)
        
        # Create the user using our custom user manager
        try:
            user = await user_manager.create(user_create, safe=True, request=request)
        except ValueError as e:
            # Handle password validation errors with a clear message
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            # Check if it's a database integrity error
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists"
                )
            # Log the full error for debugging but return a simplified message to users
            logging.exception(f"Error during user creation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create user account"
            )
        
        # Handle authentication after registration
        try:
            # Generate JWT token by passing the user object directly
            strategy = auth_backend.get_strategy()
            access_token = await strategy.write_token(user)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser
                }
            }
        except Exception as e:
            # Log token generation errors
            logging.exception(f"Error generating token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but unable to generate login token. Please login manually."
            )
    except HTTPException as e:
        # Re-raise HTTP exceptions as they already have the correct format
        raise
    except Exception as e:
        # Log the full error for debugging
        logging.exception(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

# Custom login endpoint with proper password validation
@router.post("/auth/login")
async def custom_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    logger = logging.getLogger(__name__)
    logger.info(f"Login attempt for user: {form_data.username}")
    
    # Find user by email
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    # Check if user exists and is active
    if not user or not user.is_active:
        logger.warning(f"Login failed: User {form_data.username} not found or not active")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Generate token
    strategy = auth_backend.get_strategy()
    access_token = await strategy.write_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
