import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.core.database import engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def list_users():
    """List all users in the database."""
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print("\nUSERS IN DATABASE:")
        print("=" * 50)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Is Admin: {user.is_superuser}")
            print(f"Is Active: {user.is_active}")
            print(f"Password Hash: {user.hashed_password[:20]}...")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(list_users()) 