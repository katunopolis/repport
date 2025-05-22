"""
Script to fix the admin password for the helpdesk system.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.core.security import get_password_hash
from app.core.database import engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def fix_admin_password(email: str, new_password: str):
    """Fix the admin password to ensure it works correctly."""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"Error: User {email} not found.")
            return
        
        # Update password with bcrypt hash to ensure compatibility
        user.hashed_password = get_password_hash(new_password)
        session.add(user)
        await session.commit()
        print(f"Password for {email} has been updated.")
        
        # Verify the user details
        await session.refresh(user)
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Is Admin: {user.is_superuser}")
        print(f"Is Active: {user.is_active}")
        print(f"New Hash: {user.hashed_password[:20]}...")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.fix_admin email password")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    asyncio.run(fix_admin_password(email, password)) 