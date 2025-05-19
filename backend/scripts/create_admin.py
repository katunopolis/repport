"""
Script to create an admin user for the helpdesk system.
Usage: python -m scripts.create_admin email password
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import UserCreate, User
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import get_session, engine
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

async def create_admin_user(email: str, password: str):
    """Create a new admin user with the given email and password."""
    # Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Get async session
    async for session in get_session():
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            if user.is_superuser:
                print(f"Admin user {email} already exists.")
                return
            else:
                # Update existing user to admin
                user.is_superuser = True
                session.add(user)
                await session.commit()
                print(f"User {email} updated to admin.")
                return
        
        # Create new admin user
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
            is_verified=True
        )
        
        session.add(new_user)
        await session.commit()
        print(f"Admin user {email} created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.create_admin email password")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    asyncio.run(create_admin_user(email, password)) 