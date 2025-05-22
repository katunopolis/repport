"""
Script to check if all users have consistent bcrypt password hashes.
"""
import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.core.database import engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

# Create a test password context to identify hash types
pwd_context = CryptContext(schemes=["bcrypt", "argon2", "pbkdf2_sha256", "des_crypt"], deprecated="auto")

async def check_password_hashes():
    """Check if all users have consistent bcrypt password hashes."""
    logger.info("Starting password hash check")
    
    async with AsyncSession(engine) as session:
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        logger.info(f"Found {len(users)} users in the database")
        
        # Track stats
        stats = {
            "total": len(users),
            "bcrypt": 0,
            "argon2": 0,
            "other": 0,
            "unknown": 0
        }
        
        # Check each user's password hash
        non_bcrypt_users = []
        
        for user in users:
            hash_prefix = user.hashed_password[:4] if len(user.hashed_password) >= 4 else ""
            
            if user.hashed_password.startswith('$2b$'):
                stats["bcrypt"] += 1
            elif user.hashed_password.startswith('$argon2id$'):
                stats["argon2"] += 1
                non_bcrypt_users.append((user.id, user.email, "argon2id"))
            else:
                # Try to identify the hash type
                try:
                    hash_type = pwd_context.identify(user.hashed_password)
                    if hash_type:
                        if hash_type == "bcrypt":
                            stats["bcrypt"] += 1
                        else:
                            stats["other"] += 1
                            non_bcrypt_users.append((user.id, user.email, hash_type))
                    else:
                        stats["unknown"] += 1
                        non_bcrypt_users.append((user.id, user.email, "unknown"))
                except Exception as e:
                    logger.error(f"Error identifying hash for user {user.email}: {str(e)}")
                    stats["unknown"] += 1
                    non_bcrypt_users.append((user.id, user.email, f"error: {str(e)}"))
        
        # Report results
        logger.info("=" * 50)
        logger.info("Password Hash Check Complete")
        logger.info("=" * 50)
        logger.info(f"Total users: {stats['total']}")
        logger.info(f"bcrypt hashes: {stats['bcrypt']}")
        logger.info(f"argon2 hashes: {stats['argon2']}")
        logger.info(f"other hashes: {stats['other']}")
        logger.info(f"unknown hashes: {stats['unknown']}")
        
        if stats['bcrypt'] == stats['total']:
            logger.info("SUCCESS: All users have bcrypt password hashes")
        else:
            logger.warning(f"WARNING: {stats['total'] - stats['bcrypt']} users do not have bcrypt password hashes")
            logger.info("Non-bcrypt users:")
            for user_id, email, hash_type in non_bcrypt_users:
                logger.info(f"User {user_id} ({email}): {hash_type}")

if __name__ == "__main__":
    logger.info("Running password hash check")
    asyncio.run(check_password_hashes()) 