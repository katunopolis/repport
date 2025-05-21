import asyncio
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import User
from app.core.database import engine

async def check_users():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print("User Permissions:")
        print("-" * 50)
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Is Admin: {user.is_superuser}")
        
        print("\nTotal Users:", len(users))
        print("Admin Users:", sum(1 for user in users if user.is_superuser))

        # If no admin users found, create one
        if not any(user.is_superuser for user in users):
            print("\nNo admin users found. Adding admin privileges to first user...")
            if users:
                first_user = users[0]
                first_user.is_superuser = True
                session.add(first_user)
                await session.commit()
                print(f"User {first_user.email} has been promoted to admin.")

if __name__ == "__main__":
    asyncio.run(check_users()) 