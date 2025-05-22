"""
Script to list all users in the database with their details.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.core.database import engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import json

async def list_all_users():
    """List all users in the database with their details."""
    
    print("\n===== USER ACCOUNTS =====")
    print(f"{'ID':<5} {'Email':<30} {'Is Admin':<10} {'Is Active':<10}")
    print("-" * 60)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        users_data = []
        
        for user in users:
            print(f"{user.id:<5} {user.email:<30} {'Yes' if user.is_superuser else 'No':<10} {'Yes' if user.is_active else 'No':<10}")
            
            users_data.append({
                "id": user.id,
                "email": user.email,
                "is_admin": user.is_superuser,
                "is_active": user.is_active,
                "hash_type": "bcrypt" if user.hashed_password.startswith("$2b$") else "unknown"
            })
            
        # Save detailed data to file for reference
        with open("all_users.json", "w") as f:
            json.dump(users_data, f, indent=2)
            
        print("-" * 60)
        print(f"Total users: {len(users)}")
        print(f"Admin users: {sum(1 for u in users if u.is_superuser)}")
        print(f"Regular users: {sum(1 for u in users if not u.is_superuser)}")
        print(f"Active users: {sum(1 for u in users if u.is_active)}")
        print("\nDetailed data saved to all_users.json")
        
        # Check if reset passwords file exists
        try:
            with open("reset_passwords.txt", "r") as f:
                reset_data = f.read()
                print("\n===== RESET PASSWORDS =====")
                print(reset_data)
        except FileNotFoundError:
            print("\nNo reset passwords file found.")

if __name__ == "__main__":
    asyncio.run(list_all_users()) 